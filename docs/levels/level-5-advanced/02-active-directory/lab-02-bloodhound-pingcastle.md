---
title: "LAB-502-02 · Enumerate, Map and Audit"
description: "Collect directory data with SharpHound, analyse privilege paths in BloodHound CE, cross-check with PingCastle, and write findings with preconditions."
module_code: CYB-502
level: 5
kind: lab
prerequisites: [CYB-502]
estimated_minutes: 240
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-502-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [bloodhound, sharphound, pingcastle, acl, kerberoasting, findings]
---

# LAB-502-02 · Enumerate, Map and Audit

!!! note "How this walkthrough was produced"
    The BloodHound and PingCastle commands and expected output below were written against current vendor documentation and the
    pinned versions in the tool table. They were **not** captured from a verified run in the author's lab.
    Treat the output as a **shape**, not a transcript: field order, wording and version banners differ between
    releases. Record what you actually see, and report a deviation rather than adjusting your output to match
    this page.

## Scenario and background

Your `lab.local` domain has a helpdesk group, a server-admin group and a service account with an SPN. On paper that is
ordinary. In a graph, it may be two hops from Domain Admin.

You will collect the directory data, look for paths, cross-check with a configuration auditor, and write findings that
state the **precondition** for each path. A path without a precondition is a screenshot, not a finding.

## Learning objectives

1. Deploy BloodHound CE 9.9.0 and collect with the matching SharpHound.
2. Query for Kerberoastable, AS-REP-roastable and delegation-enabled objects.
3. Trace a shortest path from a low-privilege user to a privileged group.
4. Run PingCastle and reconcile its findings with BloodHound's.
5. Write findings with evidence, preconditions, controls and ATT&CK mapping.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| BloodHound CE | 9.9.0 | Docker + `bloodhound-cli`; 8 GB RAM |
| SharpHound | 2.17.1 | Download from **your** instance's Settings → Download Collectors |
| PingCastle | 4.0.0.31 | Community edition, free for your own environment |
| Domain | `lab.local` | From LAB-502-01, snapshotted |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab.local` only, on the internal network. Both tools generate directory reads and
    authentication events; that is expected here because you own the domain.

    **Never run SharpHound or PingCastle against a domain you do not administer**, including an employer's domain
    "to see what it finds". It is noisy, it is not read-only in effect, and without written authorization it is an
    incident.

    PingCastle's free edition is for auditing your own environment; using it for paid client assessments requires a
    commercial licence.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The assumed attacker has a valid low-privilege domain account — `a.khan` — and a workstation on the internal network.
The question is what that account can reach through group membership, ACLs, SPNs and delegation, and which single
control would break the shortest path.

## Procedure

### 1. Deploy BloodHound CE

On the analyst host (Docker installed, 8 GB free):

```bash
# Download the CLI for your platform from the BloodHound CE v9.9.0 release, verify the checksum, then:
unzip bloodhound-cli-*.zip -d bloodhound-cli
cd bloodhound-cli
./bloodhound-cli install
./bloodhound-cli info
```

**Expected:** containers start and `info` prints the URL and the initial admin password. Open
`http://localhost:8080`, change the password, and confirm the version is 9.9.0.

**If Docker is unavailable:** install Docker Engine or Docker Desktop, or run BloodHound on a separate 8 GB VM. Do not
reduce the memory and then blame the ingest.

### 2. Collect with SharpHound

In the BloodHound UI: **Settings → Download Collectors**, download the SharpHound build offered by *your* instance.
Copy it to `WS01`, then run as `LAB\a.khan`:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\SharpHound.exe -c All --zipfilename lab502-a-khan.zip --outputdirectory C:\lab502
Get-Item C:\lab502\lab502-a-khan.zip | Select-Object Name, Length
Get-FileHash C:\lab502\lab502-a-khan.zip -Algorithm SHA256
```

**Expected:** a zip of JSON files and a SHA-256 you record. Collection may take a few minutes.

**Why collect as a normal user:** it shows what an ordinary account can see, which is the attacker's starting point.
Collecting as Domain Admin produces a graph that overstates visibility and hides the paths that matter.

**Collection scope is a finding in itself.** `-c All` includes sessions and local admin rights, which is noisy;
`-c DCOnly` is quieter but misses local admin edges. Record which you used and why.

### 3. Ingest and query

Upload the zip in the UI (**Administration → File Ingest**), wait for completion, then run these queries from the
search bar (Cypher):

```cypher
// Kerberoastable accounts
MATCH (u:User {hasspn:true}) RETURN u.name, u.serviceprincipalnames

// AS-REP roastable
MATCH (u:User {dontreqpreauth:true}) RETURN u.name

// Unconstrained delegation
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name

// Path from the low-privilege user to Domain Admins
MATCH p=shortestPath((u:User {name:'A.KHAN@LAB.LOCAL'})-[*1..]->(g:Group {name:'DOMAIN ADMINS@LAB.LOCAL'}))
RETURN p
```

**Expected:** `SVC-SQL@LAB.LOCAL` appears in the Kerberoastable list. The shortest-path query either returns a path
through `HELPDESK`/`SERVER ADMINS` or returns nothing — both are results. If nothing, add an ACL in the next step to
create one deliberately, so you have a path to analyse.

**To create a realistic path safely**, grant `Helpdesk` the right to add members to `Server Admins` on the DC:

```powershell
# On DC01, as Administrator
$group = Get-ADGroup "Server Admins"
$acl = Get-Acl "AD:\$($group.DistinguishedName)"
$sid = (Get-ADGroup "Helpdesk").SID
$rule = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
  $sid, "WriteProperty", "Allow", [Guid]"bf9679c0-0de6-11d0-a285-00aa003049e2")
$acl.AddAccessRule($rule)
Set-Acl "AD:\$($group.DistinguishedName)" $acl
```

Re-collect and re-query. **Expected:** a two-hop path: `a.khan → Helpdesk → Server Admins → Domain Admins` (depending
on nesting). This is a *deliberate training weakness*; record it as such.

### 4. Run PingCastle

On `DC01` as a domain administrator:

```powershell
.\PingCastle.exe --healthcheck --server DC01 --protocol AD
```

**Expected:** an HTML report and a score (0–100, higher is better). Read the **top rules** and the **stale objects**
sections, not just the score.

Record at least three rules that overlap with a BloodHound finding and one that BloodHound would not show (for example,
password policy, stale accounts, or privileged group hygiene).

### 5. Reconcile and write findings

`findings.md` — one row per finding:

| Field | Requirement |
| --- | --- |
| Finding | Concrete: "Helpdesk can add members to Server Admins" |
| Evidence | BloodHound path screenshot/export + `Get-Acl` output + PingCastle rule ID |
| Precondition | What the attacker needs first: a valid account, a workstation, network access |
| Impact | What the path reaches, and what that grants |
| Control | The specific change that breaks it |
| ATT&CK | Technique ID and why |
| Confidence | High/medium, with the reason |

Include a section **"What the tools cannot tell you"**: exploitability, whether the ACL is intentional, detection
coverage, and how quickly the graph ages after a change.

## Evidence to collect

- `bloodhound-version.txt`, collection command and zip hash.
- Cypher queries and their outputs (`paths.txt`, `kerberoastable.txt`, `delegation.txt`).
- PingCastle HTML report and the extracted top rules (`pingcastle-top.txt`).
- `findings.md` with preconditions, controls and ATT&CK.
- `limits.md`.

## Verification

- [ ] BloodHound 9.9.0 running; collector version matches the instance.
- [ ] Collection performed as a low-privilege user, with scope recorded.
- [ ] Kerberoastable account identified with its SPN.
- [ ] A shortest path is shown with each hop and the edge type.
- [ ] PingCastle run on the DC, score and top rules recorded.
- [ ] At least one finding exists in both tools and one only in PingCastle.
- [ ] Every finding names a precondition and a control.
- [ ] Limits section states that the graph is a snapshot and does not prove exploitability.

## Teardown and reset

Remove the deliberate ACL if you added it, or revert both VMs to `ad-clean`. Stop the BloodHound containers with
`bloodhound-cli stop` when not in use; they consume 8 GB.

## Reflection

1. Your path runs through a helpdesk group. Why is that more realistic than a direct Domain Admin membership?
2. PingCastle assigns a score; BloodHound shows a graph. What decision does each support, and which would you show a
   manager?
3. The collection was run as `a.khan`. What would change if you had run it as Domain Admin, and why does that matter?
4. What would make this finding disappear without anyone fixing it, and how would you detect that?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Collection | Tool run as admin | Low-privilege collection | Scope and version recorded, hash retained |
| Analysis | Queries run | Path identified | Path with edge types and preconditions |
| Cross-check | One tool | Both tools | Overlap and divergence explained |
| Reporting | List of issues | Findings with controls | Controls plus ATT&CK and explicit limits |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| BloodHound ingest stuck | Insufficient RAM or disk | 8 GB minimum; check container logs |
| Collector mismatch | SharpHound downloaded elsewhere | Use Settings → Download Collectors in your instance |
| Shortest path returns nothing | No ACL edge exists | Add the deliberate ACL in step 3, re-collect |
| `Get-Acl` on AD path fails | AD provider not loaded | `Import-Module ActiveDirectory`; use `AD:\` drive |
| PingCastle score very low | Default lab configuration | Expected; record the top rules, not just the number |
| Collection file huge | `-c All` with session data | Use `-c DCOnly` for a smaller graph, and say so |

## References

1. SpecterOps — BloodHound CE 9.9.0 quickstart and Cypher queries.
   <https://bloodhound.specterops.io/> Accessed 2026-10-29.
2. SharpHound collection methods. <https://bloodhound.specterops.io/collect-data/ce-collection/sharphound> Accessed
   2026-10-29.
3. PingCastle 4.0.0.31 — healthcheck and rules. <https://www.pingcastle.com/documentation/> Accessed 2026-10-29.
4. MITRE ATT&CK — T1558.003 Kerberoasting, T1558.004 AS-REP Roasting, T1098 Account Manipulation, T1484 Domain Policy
   Modification. Accessed 2026-10-29.

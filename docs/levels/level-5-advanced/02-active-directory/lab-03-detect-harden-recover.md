---
title: "LAB-502-03 · Final Challenge: Detect, Harden, Recover"
description: "Detect a credential-theft and privilege-escalation chain in domain controller events, break the path with verified hardening, and write the recovery runbook."
module_code: CYB-502
level: 5
kind: lab
prerequisites: [CYB-502]
estimated_minutes: 240
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-502-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [detection, kerberoasting, krbtgt, hardening, laps, gmsa, final-challenge]
---

# LAB-502-03 · Final Challenge: Detect, Harden, Recover

## Scenario and background

The domain from LAB-502-01 is compromised in the way domains usually are: a normal account, a service ticket
requested with RC4, a logon burst, a new account added to a privileged group, and a directory replication request from
a workstation.

You get the domain controller's event extract, not a live intrusion. Your job is to reconstruct the chain, write
detections that would have caught it, break the path, verify the break, and write the recovery runbook you hope never
to use.

## Learning objectives

1. Reconstruct an attack chain from domain controller events, with UTC timestamps and no speculation.
2. Write detection logic for ticket anomalies, logon bursts and privilege changes, with false-positive analysis.
3. Break a privilege path with gMSA, Protected Users, delegation hygiene and audit policy.
4. Verify each hardening change by query, and re-run the assessment to show the path is gone.
5. Write an ordered recovery runbook for a domain compromise.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Domain | `lab.local` | From LAB-502-01, snapshot before changes |
| PowerShell + AD module | — | On DC01 |
| Python | 3.10+ | Event analysis (or `jq`/`Import-Csv`) |
| PingCastle | 4.0.0.31 | Before/after comparison |

!!! warning "Authorized scope — read before you begin"
    **Everything is `lab.local`.** The event extract is synthetic, the hardening is applied to your own DC, and the
    recovery runbook is **not executed** unless you snapshot first and accept that it invalidates every ticket in the
    lab.

    **Do not reset `krbtgt` on any domain you do not own.** It invalidates authentication domain-wide and is a
    legitimate emergency action, not an exercise.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

An attacker with `a.khan`'s credentials: requests service tickets for accounts with SPNs (Kerberoasting), cracks one
offline, uses it, creates a new account, adds it to a privileged group, and attempts directory replication. The last
step is the one that turns a foothold into a domain compromise.

## The event extract

`dc-events.csv`:

```csv
time_utc,event_id,user,src_ip,computer,detail,encryption,preauth,group
2026-10-29T08:01:12Z,4769,a.khan,192.0.2.61,DC01,MSSQLSvc/sql01.lab.local:1433,0x17,,
2026-10-29T08:01:19Z,4769,a.khan,192.0.2.61,DC01,HTTP/ws01.lab.local,0x17,,
2026-10-29T08:01:27Z,4769,a.khan,192.0.2.61,DC01,MSSQLSvc/sql01.lab.local:1433,0x17,,
2026-10-29T08:01:35Z,4769,a.khan,192.0.2.61,DC01,LDAP/DC01.lab.local,0x17,,
2026-10-29T08:01:44Z,4769,a.khan,192.0.2.61,DC01,CIFS/fs01.lab.local,0x17,,
2026-10-29T08:01:52Z,4769,a.khan,192.0.2.61,DC01,RestrictedKrbHost/DC01.lab.local,0x17,,
2026-10-29T08:05:02Z,4768,svc-legacy,192.0.2.61,DC01,TGT requested,0x17,false,
2026-10-29T08:20:11Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:20:19Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:20:27Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:20:35Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:20:43Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:20:51Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:20:59Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:21:07Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:21:15Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:21:23Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:21:31Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:21:39Z,4625,a.khan,192.0.2.61,DC01,Failed logon type 3,,,
2026-10-29T08:22:04Z,4624,a.khan,192.0.2.61,DC01,Logon type 3,,,
2026-10-29T08:22:06Z,4672,a.khan,192.0.2.61,DC01,Special privileges assigned,,,
2026-10-29T08:30:15Z,4720,helpdesk1,192.0.2.61,DC01,New user svc-backup2,,,
2026-10-29T08:31:02Z,4732,helpdesk1,192.0.2.61,DC01,Member added to Server Admins,,,Server Admins
2026-10-29T08:40:44Z,4662,a.khan,192.0.2.61,WS01,Replication rights on domain object,,,
2026-10-29T08:52:01Z,4769,r.hassan,192.0.2.62,DC01,HTTP/ws01.lab.local,0x12,,
2026-10-29T08:59:12Z,4624,r.hassan,192.0.2.62,DC01,Logon type 2,,,
2026-10-29T09:02:30Z,1102,a.khan,192.0.2.61,DC01,Audit log cleared,,,
```

**Note the noise:** two events at the end are benign (`r.hassan` using AES and an interactive logon). A detection that
flags those is not ready.

## Procedure

### 1. Reconstruct the chain

```bash
python3 - <<'PY'
import csv, collections
rows = list(csv.DictReader(open("dc-events.csv", encoding="utf-8")))
print("events:", len(rows))
for r in sorted(rows, key=lambda x: x["time_utc"]):
    print(r["time_utc"], r["event_id"], r["user"], r["src_ip"], r["detail"][:48], r["encryption"], r["preauth"])
PY
```

**Expected:** the RC4 ticket burst at 08:01, a TGT without pre-auth at 08:05, a failed-logon burst at 08:20 followed by
success and special privileges at 08:22, account creation and group addition at 08:30–08:31, replication access at
08:40, log cleared at 09:02.

Write `chain.md` with one line per phase, each citing a timestamp and event ID, and map to ATT&CK:

| Phase | Evidence | ATT&CK |
| --- | --- | --- |
| Service ticket requests with RC4 | six 4769, 0x17, one source | T1558.003 |
| TGT without pre-auth | 4768, preauth=false | T1558.004 |
| Failed logons then success with special privileges | 4625 ×12 → 4624 type 3 → 4672 | T1110, T1078 |
| Account creation and privileged group addition | 4720, 4732 | T1136.001, T1098 |
| Directory replication attempt | 4662 on domain object from a workstation | T1003.006 |
| Log cleared | 1102 | T1070.001 |

### 2. Write the detections

`detections.md` — three rules minimum, each with logic, threshold, data source, false positives and tuning:

**D1: RC4 service-ticket burst**

```yaml
title: Multiple RC4 Service Tickets Requested by One Account
logsource: { product: windows, service: security }
detection:
  selection:
    EventID: 4769
    TicketEncryptionType: '0x17'
  timeframe: 10m
  condition: selection | count(ServiceName) by TargetUserName > 3
falsepositives:
  - Legacy applications that still require RC4 (fix those, do not tune this away)
  - Vulnerability scanners performing authenticated checks
level: high
```

**D2: TGT without pre-authentication**

```yaml
title: AS-REP Roastable Account Used
logsource: { product: windows, service: security }
detection:
  selection:
    EventID: 4768
    PreAuthType: '0'
  condition: selection
falsepositives:
  - Accounts intentionally configured without pre-auth (these are the finding)
level: high
```

**D3: Privileged group change outside a change window**

```yaml
title: Member Added to Privileged Group
logsource: { product: windows, service: security }
detection:
  selection:
    EventID: [4728, 4732, 4756]
    TargetUserName|endswith:
      - 'Domain Admins'
      - 'Enterprise Admins'
      - 'Server Admins'
  condition: selection
falsepositives:
  - Approved joiner/mover changes
level: medium
```

Add the false-positive analysis: which benign event in the extract would D1 wrongly flag? (None, because `r.hassan` uses
AES.) Which would D3 flag if the change were approved? (The 4732, if it were in a window — hence the change-ticket
correlation.)

### 3. Harden the path

Snapshot first. Then, on `DC01`:

```powershell
Import-Module ActiveDirectory

# A. Replace the roastable service account with a gMSA
Add-KdsRootKey -EffectiveTime ((Get-Date).AddHours(-10))
New-ADServiceAccount -Name "gmsa-sql" -DNSHostName "sql01.lab.local" `
  -PrincipalsAllowedToRetrieveManagedPassword "WS01$"
# On WS01:
# Install-WindowsFeature RSAT-AD-PowerShell; Install-ADServiceAccount gmsa-sql; Test-ADServiceAccount gmsa-sql

# Disable the old account and clear its SPN
Set-ADUser svc-sql -ServicePrincipalNames @{Clear="MSSQLSvc/sql01.lab.local:1433"} -Enabled $false

# B. Protect privileged accounts from credential exposure
Add-ADGroupMember -Identity "Protected Users" -Members "r.hassan"

# C. Remove unconstrained delegation
Get-ADComputer -Filter {TrustedForDelegation -eq $true} | ForEach-Object {
  Set-ADComputer -Identity $_ -TrustedForDelegation $false
}

# D. Disable the print spooler on the DC
Stop-Service Spooler -Force
Set-Service Spooler -StartupType Disabled

# E. Require SMB signing
Set-SmbServerConfiguration -RequireSecuritySignature $true -Force

# F. Audit the events the detections depend on
auditpol /set /subcategory:"Kerberos Service Ticket Operations" /success:enable /failure:enable
auditpol /set /subcategory:"Kerberos Authentication Service" /success:enable /failure:enable
auditpol /set /subcategory:"User Account Management" /success:enable /failure:enable
auditpol /set /subcategory:"Directory Service Access" /success:enable /failure:enable
```

**Expected:** the gMSA is created, `svc-sql` is disabled, `r.hassan` is in Protected Users, no computer has
unconstrained delegation, the spooler is stopped, SMB signing is required and the audit subcategories show success.

**Note on Protected Users:** it blocks NTLM and weak encryption for those accounts. If a legacy application needs
NTLM for that user, you will break it — which is why the change is tested, not assumed.

### 4. Verify, then re-assess

```powershell
Get-ADServiceAccount gmsa-sql | Select-Object Name, Enabled
Get-ADUser svc-sql -Properties ServicePrincipalNames, Enabled | Select-Object SamAccountName, Enabled, ServicePrincipalNames
Get-ADGroupMember "Protected Users" | Select-Object Name
Get-ADComputer -Filter {TrustedForDelegation -eq $true} | Measure-Object
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature
auditpol /get /subcategory:"Kerberos Service Ticket Operations"
```

**Expected:** gMSA enabled; `svc-sql` disabled with no SPNs; the protected user listed; zero delegation-enabled
computers; signing required; audit success enabled.

Then re-run the BloodHound collection and the PingCastle healthcheck. Record:

| Check | Before | After | Evidence |
| --- | --- | --- | --- |
| Kerberoastable accounts | | | Cypher result |
| Unconstrained delegation | | | `Get-ADComputer` count |
| Helpdesk path to Server Admins | | | Shortest-path query |
| PingCastle score / top rules | | | HTML report |
| RC4 ticket volume | | | Event query |

**The path may persist** if you did not remove the deliberate ACL from LAB-502-02. Remove it and re-query. A hardening
report that shows the same path afterwards is a finding about the hardening, not the tool.

### 5. Recovery runbook

`recovery.md` — ordered, with commands and decision points. **Do not execute** unless you snapshot and accept the
consequences:

1. Isolate DCs and Tier 0 hosts; preserve logs and directory evidence (CYB-407).
2. Reset `krbtgt` **twice**, with replication between:

```powershell
# Illustrative — invalidates all Kerberos tickets in the domain
Set-ADAccountPassword -Identity krbtgt -Reset -NewPassword (Read-Host -AsSecureString)
repadmin /syncall /AdeP
Start-Sleep -Seconds 600
Set-ADAccountPassword -Identity krbtgt -Reset -NewPassword (Read-Host -AsSecureString)
repadmin /syncall /AdeP
```

3. Reset privileged credentials twice, including service accounts and LAPS passwords.
4. Rebuild Tier 0 from known-good media; do not clean a compromised DC.
5. Check persistence: SIDHistory, AdminSDHolder ACL, new SPNs, shadow credentials, certificate templates.
6. Restore trust only after 1–5; re-establish tiering before normal operations.

Add a decision table: who authorises the krbtgt reset, what breaks (all sessions), and how users are told.

## Evidence to collect

- `chain.md` with timestamps, event IDs and ATT&CK mapping.
- `detections.md` with three rules and false-positive analysis.
- Hardening transcript and verification outputs.
- `before-after.md` comparison table.
- `recovery.md` runbook with decision points.
- `limits.md` — what the event extract cannot show.

## Verification

- [ ] Chain uses only events present in the extract; no invented activity.
- [ ] Benign events are explicitly excluded from the detections.
- [ ] Three detections, each with data source, threshold and false positives.
- [ ] Hardening covers service account, protected users, delegation, spooler, signing and audit.
- [ ] Every change verified by a query, not by the absence of an error.
- [ ] Re-assessment shows the path broken, or the persistence is explained.
- [ ] Recovery runbook is ordered, with the krbtgt double reset and a decision owner.
- [ ] Limits state that the extract is synthetic and partial.

## Teardown and reset

Revert both VMs to `ad-clean` (or the snapshot taken before hardening). Stop BloodHound containers. Nothing in this
lab touched a system outside the lab.

## Reflection

1. Which detection would you deploy first in a real domain, and what would it cost in false positives?
2. The RC4 burst and the pre-auth-less TGT are both "kerberos is working normally" from the protocol's point of view.
   What makes them detectable, and what makes them easy to miss?
3. You disabled `svc-sql` and moved to a gMSA. What application testing would you require before doing that in
   production?
4. The krbtgt reset invalidates every session. Why is that acceptable after a domain compromise, and what would make
   you hesitate?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Reconstruction | Lists events | Orders the chain | Cites each phase, maps ATT&CK, excludes benign noise |
| Detection | One rule | Three rules | Thresholds justified, false positives tested against the extract |
| Hardening | Some changes | All six applied | Each verified by query; path re-tested; side effects considered |
| Recovery | Checklist | Ordered runbook | Decision owner, consequences, persistence checks |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Add-KdsRootKey` fails | Key already exists | `Get-KdsRootKey`; reuse if present |
| gMSA install fails on client | Computer not allowed to retrieve password | Add `WS01$` to `PrincipalsAllowedToRetrieveManagedPassword` |
| Protected Users breaks logon | Application requires NTLM | Test before enabling; scope the group to interactive admins |
| Spooler restarts | Dependency or policy | Check `Get-Service Spooler`; disable via GPO |
| Path still present | ACL not removed, or stale collection | Remove ACL, re-collect, re-query |
| Audit events absent | Subcategory not enabled, or SACL missing | `auditpol /get`; enable directory access SACL |

## References

1. Microsoft — Kerberos authentication and event 4768/4769 reference. Accessed 2026-10-29.
2. Microsoft — Protected Users security group. Accessed 2026-10-29.
3. Microsoft — Group Managed Service Accounts. Accessed 2026-10-29.
4. Microsoft — KRBTGT account and reset guidance. Accessed 2026-10-29.
5. MITRE ATT&CK — T1558.003, T1558.004, T1003.006, T1070.001. Accessed 2026-10-29.

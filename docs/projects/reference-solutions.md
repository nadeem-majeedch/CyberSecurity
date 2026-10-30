---
title: "Reference Solutions — Read After Attempting"
description: "Worked reference solutions for all six capstones, with the measured results from running them against the supplied datasets."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-508]
estimated_minutes: 60
difficulty: advanced
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, reference-solution, answer-key]
---

# Reference Solutions

!!! warning "Attempt first — this is the answer sheet"
    Each section describes what a strong submission contains. Reading it before you attempt the brief removes
    most of the assessment's value, because you will recognise the shape of a good answer without having
    produced one. Attempt, self-mark against the rubric, **then** read.

    The numbers below were measured by running the published scripts against the published datasets on
    30 October 2026, with Python 3.12.10 and PyYAML 6.0.3.

---

## Capstone 1 — Network Security Assessment

There is no fixed answer, because you build the network. What is fixed is the **shape** of a complete submission,
and the weaknesses a learner typically plants. If you planted the standard set, your findings should resemble
these.

| ID | Finding | Severity | Evidence | Remediation and retest |
| --- | --- | --- | --- | --- |
| F-01 | Legacy FTP service with anonymous login enabled | High | `ftp 10.10.10.30` returns `230 Anonymous login ok`; `nmap -sV` banner recorded | Disable anonymous access or remove the service; retest with the same `ftp` command and record `530` |
| F-02 | Database bound to all interfaces | Medium | `ss -ltnp` on the host shows `0.0.0.0:3306`; connection from analyst host succeeds | Bind to `127.0.0.1` or restrict at the firewall; retest from the analyst host and from the host itself |
| F-03 | SSH permits password authentication and root login | High | `sshd -T` reports `permitrootlogin yes`, `passwordauthentication yes` | Drop-in file, `sshd -t`, reload, new session test; retest `sshd -T` |
| F-04 | World-writable directory under the web root | Medium | `find /var/www -xdev -perm -0002 -type d` returns the uploads directory | Correct ownership and mode; rerun the same `find` and show no output |
| F-05 | Host firewall absent on the file server | Medium | Allowed and denied probes behave identically; `nft list ruleset` empty | Default-deny inbound with explicit allows; retest an allowed flow and a denied flow, with counters |

**What separates merit from distinction here** is not the number of findings. It is:

- one scanner claim correctly **rejected** (for example, a version banner that the package manager shows as
  backported-patched);
- a severity rationale that names likelihood, impact and one contextual factor;
- a retest that states what it proves — "the anonymous login now returns 530" — and what it does not — "no other
  FTP configuration was reviewed".

Common loss of marks: treating the inventory as a findings list, and rating five issues "critical" on a lab
network.

---

## Capstone 2 — Web Application Security

The [Level 3 model findings](../assessments/level-3-key.md#level-3-integrated-assessment-model-answers) give the
finding set for the course sample application: IDOR on invoices, reflected XSS in search, SQL injection in login,
MD5 password storage, absent login rate limiting, verbose errors. A capstone submission should go further in two
ways: **six or more findings** and **two implemented fixes with tests**.

### Fix 1 — object-level authorization (IDOR)

```python
# vulnerable
@app.get("/invoice/<int:invoice_id>")
def invoice(invoice_id):
    return render_template("invoice.html", inv=db.get_invoice(invoice_id))

# fixed
@app.get("/invoice/<int:invoice_id>")
def invoice(invoice_id):
    inv = db.get_invoice(invoice_id)
    if inv is None or inv.owner_id != current_user.id:
        abort(404)
    return render_template("invoice.html", inv=inv)
```

```python
def test_invoice_of_another_user_is_not_readable(client, login):
    login("alice@example.test")
    r = client.get("/invoice/1043")          # belongs to bob
    assert r.status_code == 404

def test_own_invoice_still_works(client, login):
    login("alice@example.test")
    assert client.get("/invoice/1042").status_code == 200
```

Full marks require running the first test against the vulnerable commit and showing it **fail** (200 with Bob's
data), then pass on the fixed commit. A 404 rather than 403 is a defensible choice: it does not confirm the
object exists.

### Fix 2 — SQL injection in login

```python
# vulnerable
cur.execute("SELECT * FROM users WHERE email = '" + email + "'")
# fixed
cur.execute("SELECT * FROM users WHERE email = ?", (email,))
```

Test: `' OR '1'='1` returns no user; a legitimate account still authenticates. Keep the vulnerable commit in
history and cite its hash.

**Distinction-level work** includes a threat model with a trust boundary that the fixes actually respect, and a
statement of residual risk — for example, that the session cookie still lacks `SameSite`, which is a separate
finding and not fixed by either change.

---

## Capstone 3 — SOC Investigation

### The clock correction

`hosts.csv` records `FS-01` at `+420` seconds: its clock is seven minutes **ahead** of UTC. Its local timestamps
must be reduced by seven minutes before comparison. Without the correction, the file server appears to act seven
minutes *after* events that actually followed it, and the causal chain looks wrong in a way that sends analysts
down the wrong path.

### Corrected timeline (UTC)

| UTC | Host | Event | User | Observation |
| --- | --- | --- | --- | --- |
| 08:58:02 | WS-014 | 11 | m.hassan | `invoice_Q3.docm` saved from Outlook |
| 09:01:15 | WS-014 | 1 | m.hassan | `WINWORD.EXE` opens the document |
| 09:01:40 | WS-014 | 1 | m.hassan | `powershell.exe` spawned by `winword.exe`, `-nop -w hidden -enc` |
| 09:01:50 | WS-014 | 22 | m.hassan | DNS A query for `cdn-sync.example` → `203.0.113.66` |
| 09:02:05 | WS-014 | 3 | m.hassan | Outbound connection to `203.0.113.66:443` |
| 09:02:30 | WS-014 | 1 | m.hassan | Scheduled task `Updater` created, `/ru SYSTEM`, every 5 minutes |
| 09:03:10 | FS-01 | 4624 | svc_backup | Network logon (type 3) from `10.10.20.14` |
| 09:03:12 | FS-01 | 4672 | svc_backup | Special privileges assigned |
| 09:03:40–09:04:05 | FS-01 | 11 | svc_backup | Three rename bursts, 25 files renamed `.locked` |
| 09:05:30 | FS-01 | 1 | svc_backup | `vssadmin delete shadows /all /quiet` |
| 09:06:40 | WS-014 | 4732 | m.hassan | `svc_helpdesk2` added to local administrators |
| 09:09:14–09:10:02 | DC-01 | 4625, 4625, 4624 | m.hassan | Two failures then a successful network logon |
| 09:07:00–09:22:00 | WS-014 | 22 | m.hassan | Four DNS TXT queries to `cdn-sync.example`, every 300 s |
| 09:18:20 | FS-01 | 4624 | svc_backup | Second network logon from WS-014 — unresolved |

Measured: **26 events**, **4 hosts**, **12 flagged**, and **4 DNS TXT queries at exactly 300-second intervals**.

### Narrative a strong submission gives

1. **Initial access:** a document attachment opened in Word; a macro or exploit spawns encoded PowerShell.
2. **Execution and command and control:** an outbound TLS connection to `203.0.113.66`, with DNS lookups of
   `cdn-sync.example` repeating on a fixed interval — beaconing.
3. **Persistence:** a scheduled task running every five minutes as `SYSTEM`.
4. **Credential use and lateral movement:** `svc_backup` authenticates to the file server from the workstation —
   note that the service account rarely logs on interactively, which makes the type-3 logon from WS-014 the pivot.
5. **Impact:** mass renames with a `.locked` suffix and deletion of shadow copies, the standard inhibitor before
   encryption.
6. **Unresolved:** the local administrator addition at 09:06:40 and the DC authentication at 09:09–09:10 are
   consistent with attacker activity but lack a supporting process event; label them **inferred**, and say what
   additional data would confirm them (4624 logon type on the DC with process context, or 4769/4776 events).

### What to mark strictly

- **Timeline without the correction** — every FS-01 row is misplaced; this is the central technical failure.
- **Claiming the DC was compromised.** Two failed logons and one success are evidence of credential use, not of
  domain compromise. A strong answer says "possible", not "confirmed".
- **Calling 09:15 `admin.javed` malicious.** It is an encoded PowerShell command run by an administrator from
  Explorer; it matches the encoded-PowerShell keyword but not the Office parentage, and no other evidence
  supports malice. A good submission names it as a benign administrative action and explains why the rule must
  not be widened to catch it — the tuning lesson from CYB-506.
- **Containment order.** Isolate the workstation and file server from the network without powering off, disable
  `svc_backup` and `m.hassan`, revoke sessions, acquire memory before disk, then remediate. A submission that
  starts with "restore from backup" has destroyed its own evidence.

---

## Capstone 4 — Linux Hardening

A strong control table has one row per control with the command that proves its state. Examples that recur:

| Control | Verification command | Expected after |
| --- | --- | --- |
| Unattended security upgrades | `systemctl is-enabled unattended-upgrades` and `apt-config dump APT::Periodic::Unattended-Upgrade` | `enabled` and `"1"` |
| No empty passwords | `awk -F: '($2==""){print $1}' /etc/shadow` | no output |
| SSH root login disabled | `sshd -T \| grep permitrootlogin` | `permitrootlogin no` |
| Password auth disabled | `sshd -T \| grep passwordauthentication` | `passwordauthentication no` |
| Firewall default deny | `nft list ruleset` plus an allowed and a denied probe | deny counter increments on the denied probe |
| Unused services removed | `systemctl list-unit-files --state=enabled` | only expected units |
| Audit rules loaded | `auditctl -l` and `systemctl is-active auditd` | rules listed; `active` |
| World-writable files reviewed | `find / -xdev -type f -perm -0002` | empty, or a documented allowlist |

Two exceptions that are usually *good* answers:

1. **`/tmp` with `noexec` not applied** — the host's package builds and a vendor installer require execution from
   `/tmp`. Compensating control: `nodev,nosuid` applied, `noexec` recorded for review before the host's role
   changes. Owner: platform team. Review date: three months.
2. **Remote log forwarding not configured** — no log server exists in the lab. Compensating control: local
   retention of 90 days with rotation, and an exception with a review date tied to the logging project.

A re-assessment example: Lynis hardening index from **62 to 78**, OpenSCAP failed rules from **41 to 19**, with
the thirteen remaining failures itemised as exceptions rather than ignored. The exact numbers depend on your
image and profile; what matters is that both runs use the same profile and that every remaining failure has a row
in the exception register.

**Common loss of marks:** `ufw status` accepted as proof of filtering (it is configuration, not behaviour), and a
control marked applied without a verification command.

---

## Capstone 5 — Threat Detection

### The reference rules

Four Sigma rules, one per behaviour: Office spawning PowerShell (`Image|endswith` + `ParentImage|endswith`),
`certutil -urlcache` download, `schtasks /create` with `/ru SYSTEM`, and `vssadmin delete shadows`. They are in
[`reference/detection/rules/`](../assets/assessments/reference/detection/rules/office-spawns-powershell.yml).

### Measured results

Running the reference harness against the 43-event corpus:

```text
events=43 rules=4
rule                                    TP  FP
certutil-urlcache-download.yml           2   1
office-spawns-powershell.yml             2   0
schtasks-create-system.yml               2   1
shadow-copy-deletion.yml                 1   0

union TP=7 FP=2 FN=0 precision=0.78 recall=1.00
```

The two "false positives" are `E010` (an administrator fetching a vendor installer under change `CHG-1042`) and
`E011` (an approved weekly patch task running as `SYSTEM`). Both are **benign true positives**: the rules
behaved correctly; the activity was authorised.

### What a strong submission says about that

- Do **not** add an exception for `admin.javed` or for `/ru SYSTEM`; that suppresses the behaviour the rules
  exist to detect, and an attacker using those accounts would become invisible.
- If tuning is needed, add **context** — for example, correlate `certutil` downloads with change-ticket
  presence, or require the scheduled task's parent to be a script interpreter — and state the trade-off.
- Precision 0.78 on a 7-positive corpus is illustrative only. One extra false positive moves precision to 0.70;
  one miss moves recall to 0.86. Say so before someone quotes the number in a report.
- Coverage is **partial**: the rules cover execution, ingress tool transfer, persistence and inhibitor techniques,
  and say nothing about credential access, discovery or lateral movement. That is an honest coverage note.

**Common loss of marks:** writing rules after reading `labels.csv`, then presenting the fitted result as a test.

---

## Capstone 6 — Security Automation

### Reference behaviour

```text
lines_read=30 events_normalised=27 skipped=3 findings=8 exit=0
by_format: syslog 9, csv 8, json 10
by_action: login_failed 9, login_success 9, dns_query 6, http_request 2, logout 1
```

Skipped lines: 28 (truncated JSON), 29 (CSV with four fields instead of five), 30 (unrecognised marker). The
skipped rate is 10%, at the threshold, so the tool exits `0` but reports the skips prominently; a stricter tool
should exit non-zero at or above that rate, which is a defensible design choice either way — provided the README
says which one you chose.

The eight findings aggregate per indicator, host and action. The three largest:

| Indicator | Type | Events | First → last | Severity |
| --- | --- | --- | --- | --- |
| `cdn-sync.example` | domain | 4 DNS queries | 08:25:33 → 09:07:12 | High |
| `203.0.113.45` | IP | 3 failed logons, 1 HTTP request, 1 failed logon elsewhere | 08:12:03 → 09:10:00 | High |
| `198.51.100.23` | IP | 3 failed logons, 1 HTTP request, 1 login success, 1 logout | 08:15:44 → 08:41:00 | Medium (High for the success) |

Note the enrichment bug the reference fixes: matching the domain but reporting the source IP as the indicator is
wrong. A finding must name the indicator that triggered it.

### Guardrail behaviours expected

From [LAB-505-03](../levels/level-5-advanced/05-security-automation/lab-03-guarded-automation.md), the measured
refusal paths are: dry run `0`, missing token `2`, wrong scale `3`, authentication failure `4`, partial failure
after two bounded retries `1`. A capstone tool with action mode should produce an equivalent matrix, with each
exit code documented.

### Known limits a strong README states

- Parses only the three documented formats; other syslog daemons produce different lines.
- Enrichment is offline and static; an indicator's verdict can be stale, and `first_seen` is not confidence.
- Aggregation collapses repeated events, which is right for triage and wrong for forensics.
- The tool does not validate indicator syntax; a malformed IOC row is ignored rather than reported.

---

## How to use these solutions

1. Mark your own submission against the brief's rubric **first**, and write down your score.
2. Compare only the criteria you marked below 4. Reading the whole solution invites rewriting rather than
   learning.
3. For the three data-driven capstones, run the reference scripts and diff your output against the published
   numbers. A difference is either a bug in your tool or a difference in interpretation — find out which.
4. Keep the reference open while you fix your submission? No. Fix it, then compare again.

---

## Related

- [Capstone overview](index.md) · [Starter files](starter-files.md)
- [Level 5 answer key](../assessments/level-5-key.md) — the module-level equivalents
- [How Assessment Works](../policies/assessment-format.md) — the 100-mark rubrics and integrity rules

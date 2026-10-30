---
title: "LAB-401-01 · Triage a Synthetic Alert Queue"
description: "Work a twelve-alert queue, decide what matters, and write the case notes and handover another analyst could continue."
module_code: CYB-401
level: 4
kind: lab
prerequisites: [CYB-401]
estimated_minutes: 120
difficulty: intermediate
safety: local-only
lab_ids: [LAB-401-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [triage, soc, case-notes, severity, escalation]
---

# LAB-401-01 · Triage a Synthetic Alert Queue

## Scenario and background

It is 09:00 on a Monday. Overnight, twelve alerts accumulated in the queue. You are the only analyst on shift for
the next two hours, and the incident response team is available but expensive to wake.

Your job is not to investigate everything. It is to decide, for each alert, whether the activity is real, whether
it was expected, and whether it matters — then write enough that the next analyst does not repeat your work.

All data is synthetic: documentation-range addresses, `.test` domains, fictional hosts and users.

## Learning objectives

By the end of this lab you can:

1. Triage an alert queue using evidence rather than the severity label.
2. Assign one of four dispositions with a written rationale.
3. Identify the five alerts that require escalation and justify the rest as closures.
4. Record case notes in a form another analyst can act on.
5. Produce a handover that names open questions and next actions.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python 3 | 3.10+ | Queue generation and summaries |
| `jq` | 1.6+ | Reading and filtering the queue |
| A text editor | — | `triage.md`, `case-notes.md`, `handover.md` |

!!! warning "Authorized scope — read before you begin"
    **What this lab uses:** a synthetic queue you generate locally, and notes you write. No live system, no network
    connection, no real indicators.
    **What it must not do:** query the internet for any address or domain in the dataset. They are documentation
    ranges and reserved names; a lookup would either fail or hit an unrelated real host.

    This is an analysis exercise. There is nothing to scan, block, or contain.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The queue simulates a mixed environment: a file server holding finance data, a domain controller, workstations, a
developer host, and an HR laptop. The fictional adversary's goal is data theft followed by extortion. Some alerts
are that adversary; most are operational noise that a real SOC sees every day.

The exercise's difficulty is deliberately in the **mixture** — you cannot tell which is which from the rule names.

## Environment

| Host | Role | Criticality | Address |
| --- | --- | --- | --- |
| `dc-01` | Domain controller | Critical | 192.0.2.10 |
| `fs-01` | Finance file server | Critical | 192.0.2.20 |
| `ws-03`, `ws-07`, `ws-12` | Workstations | Medium | 192.0.2.31–33 |
| `dev-02` | Developer workstation | Medium | 192.0.2.44 |
| `hr-lt-04` | HR laptop, roaming | High (data) | 198.51.100.24 |
| `fw-01` | Perimeter firewall | Critical | 203.0.113.1 |

## Before you start

1. Create a working directory: `mkdir -p ~/lab/level-4/lab-401-01/{data,evidence}`.
2. Snapshot nothing — this lab makes no system changes.
3. Generate the queue:

```bash
cd ~/lab/level-4/lab-401-01
cat > data/queue.jsonl <<'JSONL'
{"id":"A-1001","ts":"2026-10-26T01:12:04Z","rule":"Multiple failed logons","host":"fs-01","user":"svc-backup","severity":"high","src":"198.51.100.77","details":"14 x 4625 (logon type 3) in 90s, then 1 x 4624","asset_criticality":"critical","evidence":"4625 target: svc-backup; 4624 at 01:13:41; no change record for svc-backup"}
{"id":"A-1002","ts":"2026-10-26T02:40:11Z","rule":"Outbound to newly registered domain","host":"dev-02","user":"analyst2","severity":"medium","src":"192.0.2.44","details":"HTTPS to cdn-update.example.test, first seen 9 days ago, 1 connection, 18 KB out","asset_criticality":"medium","evidence":"parent process python3; change CHG-2214 references a package mirror test"}
{"id":"A-1003","ts":"2026-10-26T03:02:55Z","rule":"Credential dumping tool behaviour","host":"ws-07","user":"r.hassan","severity":"critical","src":"192.0.2.32","details":"rundll32.exe comsvcs.dll, MiniDump 624 C:\\Windows\\Temp\\d.dmp full","asset_criticality":"medium","evidence":"parent: cmd.exe from outlook.exe; file d.dmp created, 41 MB"}
{"id":"A-1004","ts":"2026-10-26T03:15:20Z","rule":"Antivirus update failed","host":"ws-12","user":"SYSTEM","severity":"low","src":"192.0.2.33","details":"Signature update returned HTTP 503 from update.example.test","asset_criticality":"medium","evidence":"repeated every 6h for 3 days; other hosts updated successfully"}
{"id":"A-1005","ts":"2026-10-26T03:22:09Z","rule":"New service installed","host":"dc-01","user":"SYSTEM","severity":"high","src":"192.0.2.10","details":"Service 'WinMgmtHelper' created, binary C:\\ProgramData\\upd\\svc.exe","asset_criticality":"critical","evidence":"7045 at 03:22; parent process powershell.exe (encoded command); no change record; file unsigned"}
{"id":"A-1006","ts":"2026-10-26T04:05:42Z","rule":"High-entropy DNS labels","host":"ws-12","user":"j.ali","severity":"medium","src":"192.0.2.33","details":"38 queries to <32-char base32>.sync.example.test in 4 minutes","asset_criticality":"medium","evidence":"queries succeeded; average label entropy 4.7 bits/char; same host contacted 203.0.113.55:443 afterwards"}
{"id":"A-1007","ts":"2026-10-26T05:11:03Z","rule":"Sudo authentication failure","host":"dev-02","user":"analyst2","severity":"low","src":"192.0.2.44","details":"1 x sudo authentication failure, then success 4s later","asset_criticality":"medium","evidence":"command: sudo apt update; user stated 'typo' in chat at 05:12"}
{"id":"A-1008","ts":"2026-10-26T06:30:18Z","rule":"USB mass storage connected","host":"hr-lt-04","user":"s.qureshi","severity":"medium","src":"198.51.100.24","details":"USB device 0951:1666 mounted; 212 files copied to removable media in 6 min","asset_criticality":"high","evidence":"files under /HR/Compensation; no approved transfer request; user on leave from 2026-10-27"}
{"id":"A-1009","ts":"2026-10-26T07:02:44Z","rule":"Inbound port scan","host":"fw-01","user":"-","severity":"low","src":"203.0.113.90","details":"1,024 ports probed in 30s; all denied","asset_criticality":"critical","evidence":"no successful connection; source not previously seen"}
{"id":"A-1010","ts":"2026-10-26T07:40:12Z","rule":"Impossible travel","host":"vpn-gw","user":"svc-reporting","severity":"high","src":"203.0.113.12, 198.51.100.31","details":"Service account authenticated from two countries within 12 minutes","asset_criticality":"critical","evidence":"both sessions used the same client certificate; account is a service account with interactive logon enabled"}
{"id":"A-1011","ts":"2026-10-26T08:05:33Z","rule":"Encoded PowerShell from scheduled task","host":"ws-03","user":"SYSTEM","severity":"high","src":"192.0.2.31","details":"schtasks task 'OneDriveSync' ran powershell.exe -enc <base64> at 08:05","asset_criticality":"medium","evidence":"task created 2026-10-25 23:58 by user a.khan; decoded command downloads from 203.0.113.55"}
{"id":"A-1012","ts":"2026-10-26T08:20:00Z","rule":"Backup job failed","host":"fs-01","user":"SYSTEM","severity":"medium","src":"192.0.2.20","details":"Nightly backup to NAS-02 failed: destination full","asset_criticality":"critical","evidence":"last successful backup 2026-10-23; retention policy would delete oldest set tonight"}
JSONL
wc -l data/queue.jsonl
```

**Expected:** `12 data/queue.jsonl`.

## Procedure

### 1. Read the queue as data, not prose

```bash
jq -r '[.id, .ts, .severity, .asset_criticality, .rule, .host] | @tsv' data/queue.jsonl | column -t -s $'\t'
```

**Expected:** a one-screen table. Resist the urge to start with the "critical" rows; severity was assigned by a
rule author who did not know your asset inventory.

### 2. First pass: sort by what would hurt most

```bash
# Critical assets first, then by time
jq -r 'select(.asset_criticality=="critical") | [.ts,.id,.rule,.host] | @tsv' data/queue.jsonl | sort
```

For each of these, ask the three triage questions from the lesson. Write one line per alert in
`evidence/triage.md` using this table:

| ID | Real? | Expected? | Matters? | Disposition | Priority | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| A-1001 | | | | | | |

Dispositions are: **true positive → escalate**, **benign true positive → close**, **false positive → close and
tune**, **needs investigation → keep open**.

### 3. Look for pairs, not singles

Several alerts become significant only when combined. Query by host and by source address:

```bash
jq -r 'select(.host=="ws-12") | [.ts,.id,.rule,.details] | @tsv' data/queue.jsonl
jq -r 'select(.src|test("203.0.113.55")) | [.ts,.id,.host,.details] | @tsv' data/queue.jsonl
```

**Why this matters:** one high-entropy DNS alert is a maybe. A DNS alert plus a later connection to the same
address from another host is a campaign. The queue is deliberately ordered so that the related items are hours
apart.

### 4. Decide the five escalations

You should end with **exactly five** escalations. That number is not a hint about which five; it is a calibration
target:

- **Nine or more** means you are escalating operational noise and will burn the IR team's attention.
- **Two or three** means you are accepting explanations without evidence — the most common and most dangerous
  failure.
- **Five** means you distinguished "the rule fired" from "something happened that matters".

For each escalation, write a case note in `evidence/case-notes.md` with this structure:

```text
CASE A-10xx — <one-line title>
Time (UTC):        first and last relevant event
What happened:     3–5 sentences, facts only
Evidence:          alert fields, plus any correlated alert IDs
Assessment:        technique(s) and why this is malicious rather than expected
Impact if true:    which asset, which data, what an attacker gains
Actions taken:     what you did (in this lab: who you notified and what you asked for)
Open questions:    what you could not determine from the queue alone
```

**Why the open questions section is mandatory:** it is what the responder needs, and it is the part analysts skip.

### 5. Close the rest with a reason

For every non-escalated alert, write a closure line containing the evidence, not a label:

```text
A-1007 — Benign true positive. One sudo failure followed by success 4 s later, same user, same host;
user confirmed a typo in chat; command was apt update. No subsequent privileged change. Rule unchanged.
```

If your closure says only "benign" or "FP", rewrite it. The test is whether another analyst could re-close it in
ten seconds without re-reading the alert.

### 6. Produce the handover

`evidence/handover.md`, at most one page:

| Section | Content |
| --- | --- |
| Open cases | IDs, one-line status, owner |
| Escalated | IDs, severity, who was notified, when |
| Incomplete | What you could not verify and why |
| Next actions | Specific, ordered, with a time |
| Watch items | Alerts that are benign now but might not be |

**Expected:** a handover that a colleague could act on at 17:00 without contacting you.

### 7. Compare your dispositions with a second pass

Leave the queue for ten minutes, then re-read your table. Change anything you justified with "probably". Record
the changes in `evidence/revisions.md` — a triage that never changes is usually a triage that never looked.

## Evidence to collect

- `data/queue.jsonl` — the generated queue.
- `evidence/triage.md` — twelve rows, all cells filled.
- `evidence/case-notes.md` — five structured notes.
- `evidence/closures.md` — seven closures with evidence sentences.
- `evidence/handover.md` — the one-page handover.
- `evidence/revisions.md` — what you changed on second pass and why.

## Verification

- [ ] All twelve alerts have a disposition and a priority.
- [ ] Exactly five are escalated, and each has a case note with all seven fields.
- [ ] Every closure names the evidence, not just a category.
- [ ] At least two alerts were correlated by host or source address.
- [ ] The handover lists next actions with times and names an owner.
- [ ] No disposition relies on the severity label alone.

## Teardown and reset

```bash
# Nothing was changed on any system.
rm -rf ~/lab/level-4/lab-401-01/data
```

Keep `evidence/` — the triage table and case notes are reused in LAB-401-02 and in the Level 4 assessment.

## Reflection

1. Which alert was hardest to close, and what single piece of missing evidence would have settled it?
2. Two alerts in the queue are "real but harmless". Explain why calling them false positives would be wrong and what
   a detection engineer should do instead.
3. If you had to delete one rule from the queue's source set to reduce noise, which would it be, and what detection
   would you lose?
4. Your handover says "watch items". What makes an item a watch item rather than an open case?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Dispositions | Fewer than eight decided | All twelve, mostly evidence-based | All twelve, with the five escalations correct and defensible |
| Correlation | Alerts read individually | One pair correlated | Multiple correlations across host and address, with reasoning |
| Case notes | Titles only | Structured notes | Notes a responder could act on without asking a question |
| Closures | "Benign"/"FP" labels | Reasons given | Evidence sentences plus a tuning suggestion where relevant |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `jq` prints nothing | Field name typo, or JSONL file empty | `head -1 data/queue.jsonl \| jq keys` |
| Every alert looks malicious | Reading rule names as facts | Start from the evidence field; ask what a benign explanation would look like |
| Exactly five is hard to hit | Escalating "interesting" rather than "impactful" | Re-rank by asset criticality and whether the activity succeeded |
| Case notes feel repetitive | Copying alert text | Write what the *combination* of evidence means, not what each field says |

## References

1. NIST SP 800-61 Rev. 3 — Incident Response Recommendations (April 2025). <https://csrc.nist.gov/pubs/sp/800/61/r3/final>
2. MITRE ATT&CK — Enterprise tactics and techniques. <https://attack.mitre.org/> Accessed 2026-10-29.
3. CISA — Incident and Vulnerability Response Playbooks. Accessed 2026-10-29.
4. RFC 5737 — IPv4 Address Blocks Reserved for Documentation.

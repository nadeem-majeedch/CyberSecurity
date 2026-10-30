---
title: "LAB-506-02 · Coverage and Blind Spots"
description: "Audit a detection inventory against its own evidence, downgrade overclaimed coverage, rank blind spots and design three detections you can actually build."
module_code: CYB-506
level: 5
kind: lab
prerequisites: [CYB-506]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-506-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [threat-hunting, attck, coverage, blind-spots, detection-engineering]
---

# LAB-506-02 · Coverage and Blind Spots

## Prerequisites

The CYB-506 lesson and LAB-506-01's hunt record. The detection inventory (`detections.csv`) and its evidence
columns are supplied in the lab, and Python 3.10 or newer reads them.

## Scenario and background

The team's slide says "82% ATT&CK coverage". The inventory behind it says something else: rules that were never
tested, rules that failed their last test, techniques with no data source at all.

You will audit the inventory against its own evidence, produce a defensible coverage figure, rank the gaps, and design
three detections — with the data source, the logic and the test for each.

## Learning objectives

1. Define coverage states with evidence requirements.
2. Audit a rule inventory and downgrade claims that the evidence does not support.
3. Distinguish "no rule" from "no data" — different problems, different owners.
4. Rank blind spots by exposure and effort.
5. Specify a detection completely enough that someone else could build and test it.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | `csv`, `collections` |
| ATT&CK reference | current | For technique names and tactics |

## Safety

The inventory is synthetic; no system is scanned or changed.

## Environment

```bash
mkdir -p ~/hunt-lab/coverage && cd ~/hunt-lab/coverage
```

`detections.csv`:

```csv
rule_id,name,technique,technique_name,data_source,data_source_present,last_tested,fires_on_test,owner,declared_status
D-001,Scheduled task with remote action,T1053.005,Scheduled Task,Windows 4698,true,2026-10-15,true,soc,present
D-002,Encoded PowerShell command,T1059.001,PowerShell,PowerShell 4104,true,2026-09-02,true,soc,present
D-003,LSASS handle access,T1003.001,LSASS Memory,Sysmon 10,true,,,soc,present
D-004,DNS query to newly seen domain,T1071.004,DNS,Sysmon 22,true,,,soc,present
D-005,Service installed,T1543.003,Windows Service,Windows 7045,true,2026-08-11,false,soc,present
D-006,Run key persistence,T1547.001,Registry Run Keys,Sysmon 13,true,2026-10-01,true,soc,present
D-007,Credential dump via comsvcs,T1003.001,LSASS Memory,Sysmon 1 command line,false,,,soc,absent
D-008,WMI event subscription,T1546.003,WMI Event Subscription,Sysmon 19-21,false,,,soc,absent
D-009,Service created remotely,T1021.002,SMB/Windows Admin Shares,Windows 4697,true,2026-07-20,true,soc,present
D-010,RC4 service ticket burst,T1558.003,Kerberoasting,Windows 4769,true,2026-10-10,true,soc,present
D-011,TGT without pre-auth,T1558.004,AS-REP Roasting,Windows 4768,true,,,soc,present
D-012,Mailbox rule creation,T1114.003,Email Forwarding Rule,Exchange mailbox audit,false,,,soc,absent
D-013,Archive written then uploaded,T1560.001,Archive Collected Data,Sysmon 11 + proxy,true,2026-09-30,true,soc,present
D-014,RDP between workstations,T1021.001,RDP,Windows 4624 type 10,true,2026-06-01,true,soc,present
D-015,USB mass storage inserted,T1091,Replication Through Removable Media,Windows 6416,true,,,soc,present
D-016,Certutil decode,T1140,Deobfuscate/Decode,Sysmon 1 command line,true,2026-10-05,true,soc,present
D-017,Cloud audit logging stopped,T1562.008,Disable Cloud Logs,CloudTrail,true,,,soc,present
D-018,DNS tunnelling volume,T1071.004,DNS,DNS query logs,true,2026-09-15,false,soc,present
```

## Procedure

### 1. Define the rule before counting

Write the definition in `coverage.md` first:

| State | Requirement |
| --- | --- |
| **Present** | Data source exists, rule has been tested, and the test produced an alert |
| **Partial** | Data exists, but the rule is untested, failed its test, or is manual |
| **Absent** | No usable data source, or no rule at all |

The `declared_status` column is what the team believes. Your job is to compare it with the evidence columns.

### 2. Audit

```bash
python3 - <<'PY'
import csv, collections

rows = list(csv.DictReader(open("detections.csv", encoding="utf-8")))


def evidenced(row):
    if row["data_source_present"] != "true":
        return "absent"
    if row["last_tested"] and row["fires_on_test"] == "true":
        return "present"
    return "partial"


for row in rows:
    row["evidenced"] = evidenced(row)

counts = collections.Counter(r["evidenced"] for r in rows)
print("rules:", len(rows), "techniques:", len({r["technique"] for r in rows}))
print("evidenced:", dict(counts))

print("\noverclaimed:")
for r in rows:
    if r["declared_status"] != r["evidenced"]:
        print(f"  {r['rule_id']} {r['technique']:12} declared={r['declared_status']:8} evidenced={r['evidenced']:8}"
              f" tested={r['last_tested'] or 'never':10} fires={r['fires_on_test'] or 'n/a'}")

print("\nno data source:")
for r in rows:
    if r["data_source_present"] != "true":
        print(f"  {r['rule_id']} {r['technique']:12} {r['name']:32} needs {r['data_source']}")

print("\nfailed last test:")
for r in rows:
    if r["last_tested"] and r["fires_on_test"] == "false":
        print(f"  {r['rule_id']} {r['technique']:12} {r['name']:32} tested {r['last_tested']}")
PY
```

**Expected:**

```text
rules: 18 techniques: 16
evidenced: {'present': 8, 'partial': 7, 'absent': 3}

overclaimed:
  D-003 T1003.001    declared=present  evidenced=partial  tested=never      fires=n/a
  D-004 T1071.004    declared=present  evidenced=partial  tested=never      fires=n/a
  D-005 T1543.003    declared=present  evidenced=partial  tested=2026-08-11 fires=false
  D-011 T1558.004    declared=present  evidenced=partial  tested=never      fires=n/a
  D-015 T1091       declared=present  evidenced=partial  tested=never      fires=n/a
  D-017 T1562.008    declared=present  evidenced=partial  tested=never      fires=n/a
  D-018 T1071.004    declared=present  evidenced=partial  tested=2026-09-15 fires=false

no data source:
  D-007 T1003.001    Credential dump via comsvcs     needs Sysmon 1 command line
  D-008 T1546.003    WMI event subscription          needs Sysmon 19-21
  D-012 T1114.003    Mailbox rule creation           needs Exchange mailbox audit

failed last test:
  D-005 T1543.003    Service installed               tested 2026-08-11
  D-018 T1071.004    DNS tunnelling volume           tested 2026-09-15
```

Three different problems are now visible, and they need different fixes:

| Problem | Rules | Fix | Owner |
| --- | --- | --- | --- |
| Never tested | D-003, D-004, D-011, D-015, D-017 | Run the test; record the date and result | Detection engineer |
| Test fails | D-005, D-018 | Fix the logic; the rule does not do what it claims | Detection engineer |
| No data source | D-007, D-008, D-012 | Enable the telemetry, or accept the gap in writing | Platform / SOC lead |

### 3. Compute the defensible number

```bash
python3 - <<'PY'
import csv, collections
rows = list(csv.DictReader(open("detections.csv", encoding="utf-8")))
techniques = collections.defaultdict(set)
for r in rows:
    if r["data_source_present"] == "true" and r["last_tested"] and r["fires_on_test"] == "true":
        techniques[r["technique"]].add("present")
    elif r["data_source_present"] == "true":
        techniques[r["technique"]].add("partial")
    else:
        techniques[r["technique"]].add("absent")
tally = collections.Counter(next(iter(v)) if len(v) == 1 else "mixed" for v in techniques.values())
print("techniques:", len(techniques), dict(tally))
print("present share:", f"{tally['present'] / len(techniques):.0%}")
PY
```

**Expected:** 16 techniques; the exact split depends on your classification of `mixed` techniques (T1003.001 has one
present-capable rule and one with no data; T1071.004 has two partials). Report the number **with its definition and its
qualifier**, for example: "6 of 16 techniques have a tested detection; 2 of those also have untested or failed rules;
3 have no data at all."

A single percentage is not the deliverable. The deliverable is the sentence a manager can repeat without becoming
wrong.

### 4. Rank the blind spots

Order the gaps by **exposure × ease of fixing**, not by how alarming the technique name sounds:

| Rank | Gap | Why it ranks here | Effort |
| --- | --- | --- | --- |
| 1 | T1071.004 DNS — two rules, neither working | DNS is the most common egress path; data already collected | Low: fix two rules |
| 2 | T1003.001 credential dumping — one rule untested, one without data | Highest impact if it succeeds; partial data already exists | Medium: test one, enable command-line audit |
| 3 | T1546.003 WMI persistence — no data | Common persistence, but no telemetry at all | High: Sysmon config change, rollout |
| 4 | T1114.003 mailbox rules — no data | High impact, but requires Exchange audit configuration and another team | High: cross-team |
| 5 | T1091 USB — rule untested | Lower prevalence in a cloud-first estate | Low: test only |

Defend your own ordering in one paragraph. "Because it is scary" is not a reason; "because the data exists and the
technique is the most common egress channel" is.

### 5. Specify three detections

For each, complete this template — a detection that cannot be built from its specification is not specified:

```markdown
### D-019 · Encoded PowerShell in a scheduled task action

- **Technique:** T1053.005, T1059.001
- **Data source:** Windows 4698 (task created), field `TaskContent`; fallback Sysmon 1 for `schtasks.exe`
- **Logic:** action contains `-enc` or `-EncodedCommand`, OR the action path is under `%TEMP%`, `%APPDATA%`, or `%PUBLIC%`
- **Threshold:** any single event; no aggregation
- **Known false positives:** endpoint-management agents that install encoded tasks; software installers using
  `%TEMP%`
- **Tuning:** exclude only signed binaries from `Program Files` under a service account; never exclude by task name
- **Test (positive):** create a task whose action is `powershell -enc <base64 of a print statement>`; expect one alert
- **Test (negative):** create a task that runs `cmd /c echo hello`; expect none
- **Boundary:** a task action containing the literal text `-enc` in a file path should alert; document the decision
- **Response:** decode the payload statically, check the parent process and account, isolate if unexplained
```

Repeat for **T1071.004** (DNS) and one of your choice from the blind-spot list.

### 6. Say what the number cannot tell you

Add to `coverage.md`:

1. Why an 18-rule inventory cannot represent ATT&CK coverage for an estate.
2. What a "present" detection still misses (variants, evasion, different parents).
3. Which gap needs a budget decision rather than an engineering one.
4. What you would measure next month to show the work changed anything.

## Evidence to collect

- The audit output (counts, overclaims, no-data list, failed tests).
- `coverage.md` with the definition, the number and its qualifier, the ranked gaps and three specifications.
- One paragraph defending the ranking.

## Verification

- [ ] Coverage states defined before counting, with evidence requirements.
- [ ] Seven overclaims identified, each with the reason it was downgraded.
- [ ] The three no-data techniques are listed with the telemetry they need.
- [ ] The reported figure includes its definition and qualifier, not a bare percentage.
- [ ] Blind spots ranked by exposure and effort, with a defence.
- [ ] Three detections specified with data source, logic, false positives, positive test and negative test.

## Teardown and reset

Nothing to tear down.

## Reflection

1. D-005 was tested and failed. Is a failed test worse or better than no test? For whom?
2. The inventory has two DNS rules, both partial. What does duplication without testing tell you about the process?
3. If you could enable exactly one data source next quarter, which would move the most techniques from absent to
   partial, and why?
4. Your manager asks for "90% coverage". What do you say, and what do you offer instead?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Definition | None | Three states | Each state tied to required evidence |
| Audit | Counted rows | Found overclaims | Separated untested, failing and no-data problems with owners |
| Reporting | One percentage | Qualified figure | Figure plus what it cannot tell you |
| Specifications | Named techniques | Logic and source | Logic, thresholds, FPs, positive and negative tests, response |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Every rule "present" | Reading `declared_status` | Compute from evidence columns only |
| Technique counted twice | One technique, several rules | Group by technique and record `mixed` |
| Empty `last_tested` treated as false | String vs boolean | `if row["last_tested"]` before comparing |
| Overclaim list empty | Evidence function too lenient | Check that `fires_on_test` equals `"true"` |

## References

1. MITRE ATT&CK — technique pages and data source mappings. Accessed 2026-10-29.
2. MITRE — Detection Engineering and ATT&CK coverage guidance. Accessed 2026-10-29.
3. NIST SP 800-137 — continuous monitoring. Accessed 2026-10-29.

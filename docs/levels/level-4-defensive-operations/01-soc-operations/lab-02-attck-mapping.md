---
title: "LAB-401-02 · Map Activity to ATT&CK"
description: "Map ten observed behaviours to ATT&CK tactics and techniques, state the evidence, and name the data source that would confirm each."
module_code: CYB-401
level: 4
kind: lab
prerequisites: [CYB-401]
estimated_minutes: 120
difficulty: intermediate
safety: local-only
lab_ids: [LAB-401-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [mitre-attack, mapping, detection-coverage, telemetry]
---

# LAB-401-02 · Map Activity to ATT&CK

## Scenario and background

A detection programme needs to know what it can see. Not "how many rules do we have" — which adversary behaviours
would we notice, and which would pass silently?

You will map ten synthetic observations to ATT&CK, and for each one state the evidence in the observation, the
data source that would confirm it at scale, and one way the mapping could be wrong. That last column is the one
that separates a useful coverage map from a wall chart.

## Learning objectives

By the end of this lab you can:

1. Identify the tactic and technique for a described behaviour, and cite the technique by ID and official name.
2. Distinguish an observation from an inference, and say what evidence would settle it.
3. Name the log source that would detect each technique at scale.
4. Explain two ways a mapping can be wrong, and how you would check.
5. Build a coverage view by tactic rather than a single percentage.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python 3 | 3.10+ | Generate the observation set |
| `jq` | 1.6+ | Filter and tabulate |
| A browser | current | Verify technique IDs on attack.mitre.org |

!!! warning "Authorized scope — read before you begin"
    **What this lab uses:** ten synthetic observations and public ATT&CK documentation.
    **What it must not do:** reproduce any behaviour on a live system, or look up the fictional indicators. The
    observations describe activity; you are not asked to perform it.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The fictional adversary is a financially motivated intrusion that begins with credential guessing against a file
server, establishes persistence, performs credential access, exfiltrates over DNS, and ends with extortion. The ten
observations are fragments of that intrusion mixed with two benign operational events.

## Environment

No hosts are required. The lab produces a JSON file and a mapping table.

## Before you start

```bash
mkdir -p ~/lab/level-4/lab-401-02/{data,evidence}
cd ~/lab/level-4/lab-401-02
cat > data/observations.jsonl <<'JSONL'
{"id":"O-01","host":"fs-01","observation":"14 failed network logons for svc-backup from 198.51.100.77 within 90 seconds, followed by a successful logon from the same address","artefact":"Security 4625 x14, 4624 x1"}
{"id":"O-02","host":"dc-01","observation":"A service named WinMgmtHelper was created with a binary in C:\\ProgramData\\upd\\svc.exe, unsigned, parent process powershell.exe with an encoded command line","artefact":"System 7045, Sysmon 1, PowerShell 4104"}
{"id":"O-03","host":"ws-07","observation":"rundll32.exe executed comsvcs.dll with the MiniDump export against a process ID, writing a 41 MB file to C:\\Windows\\Temp","artefact":"Sysmon 1, file create 11"}
{"id":"O-04","host":"ws-03","observation":"A scheduled task named OneDriveSync was created at 23:58 and ran an encoded PowerShell command that downloaded a file from an external address","artefact":"Security 4698, Sysmon 1, proxy log"}
{"id":"O-05","host":"ws-12","observation":"38 DNS queries in four minutes to 32-character base32 labels under sync.example.test, followed by an HTTPS connection to the same hosting provider","artefact":"DNS query log, Zeek dns.log, proxy"}
{"id":"O-06","host":"hr-lt-04","observation":"A removable device was mounted and 212 files under an HR directory were copied in six minutes, outside business hours, with no transfer request","artefact":"Windows 6416/2003, Sysmon 11, file audit"}
{"id":"O-07","host":"fw-01","observation":"1,024 destination ports probed from a single external address in 30 seconds; all denied","artefact":"Firewall deny log"}
{"id":"O-08","host":"vpn-gw","observation":"A service account authenticated from two countries within twelve minutes using the same client certificate","artefact":"VPN authentication log"}
{"id":"O-09","host":"dev-02","observation":"A Python process made one 18 KB HTTPS connection to a nine-day-old domain during a documented package-mirror test","artefact":"Proxy log, change record CHG-2214"}
{"id":"O-10","host":"fs-01","observation":"Nightly backup failed because the destination was full; retention would delete the oldest set that night","artefact":"Backup job log, NAS capacity metric"}
JSONL
wc -l data/observations.jsonl
```

**Expected:** `10 data/observations.jsonl`.

## Procedure

### 1. Separate observation from interpretation

For each row, split the text into **what was recorded** and **what it might mean**. O-03 records a command line;
"credential dumping" is your interpretation. Both belong in the mapping, in different columns.

Create `evidence/mapping.md`:

| ID | Tactic | Technique (ID + official name) | Sub-technique | Evidence in the observation | Data source for scale | Could be wrong because |
| --- | --- | --- | --- | --- | --- | --- |
| O-01 | | | | | | |

### 2. Verify every ID

For each technique you choose:

1. Open <https://attack.mitre.org/> and confirm the ID exists **and** the official name matches what you wrote.
2. Check the technique's own tactic list — a technique can serve several tactics, and the tactic you name must be
   one of them.
3. If you use a sub-technique, confirm the parent technique and the exact sub-technique ID.

**Why this is not pedantic:** reports with invented technique IDs lose credibility immediately, and the IDs change
between ATT&CK versions. The current version at the time of writing is v20.0 (October 2026); record the version you
checked against in your table header.

### 3. Name the data source honestly

For each mapping, name the log that would show this behaviour **across the estate**, not just on the host in the
observation. Examples of the answer shape: *Windows Security 4625/4624 with logon type and source address*,
*Sysmon Event ID 1 with parent and command line*, *DNS query logs with full query name*, *proxy logs with SNI and
bytes out*.

If you cannot name a data source, that is a coverage gap. Write **"no source — gap"** rather than guessing, and add
it to the gap list in step 5.

### 4. Add the "could be wrong" column

Every mapping gets one concrete alternative explanation or failure mode. Examples of the form:

- The observation is a real event but the technique label is wrong (a legitimate admin tool that resembles the
  technique).
- The telemetry is incomplete (command line logging disabled, so the real arguments are unknown).
- The behaviour is a fragment; the technique requires a second step that is not observed.

This column is what a reviewer reads first, because it shows whether you understood the technique or matched a
keyword.

### 5. Build the coverage view by tactic

```bash
# Count your mappings per tactic once the table is written
awk -F'|' 'NR>2 && NF>3 {gsub(/ /,"",$2); if ($2!="") print $2}' evidence/mapping.md \
  | sort | uniq -c | sort -rn
```

Produce `evidence/coverage.md` with:

| Tactic | Observations mapped | Data source exists? | Gap to close |
| --- | --- | --- | --- |
| … | … | yes / no | … |

Then answer in three sentences: which tactic is best covered, which is worst, and which single data source would
improve the most tactics at once.

### 6. Compare with a second analyst (or your own second pass)

Re-map O-01 and O-05 without looking at your first answer. If the tactic or technique changed, record both and say
which you now prefer and why. Disagreement is normal; unexplained disagreement is the problem.

### 7. Write the summary

`evidence/summary.md`, under 300 words, for a detection engineering lead:

- How many of the ten observations map to a technique you could detect today.
- Two coverage gaps, each with the data source that would close it.
- One mapping you are least confident about and the test that would resolve it.

## Evidence to collect

- `data/observations.jsonl`.
- `evidence/mapping.md` — ten rows, eight columns, ATT&CK version in the header.
- `evidence/coverage.md` — the tactic table and the three-sentence analysis.
- `evidence/summary.md` — the 300-word brief.

## Verification

- [ ] Every technique ID exists on attack.mitre.org with the official name you wrote.
- [ ] Every tactic you named appears in that technique's own tactic list.
- [ ] Every row names a data source or states "no source — gap".
- [ ] Every row has a "could be wrong" entry that is specific to that observation.
- [ ] The coverage table aggregates by tactic, not by count of rules.
- [ ] Two observations were re-mapped blind, with any change explained.

## Teardown and reset

Nothing to tear down. Keep `evidence/`; the coverage table is reused in LAB-404-02 when you decide which detection
to write first.

## Reflection

1. Which observation was hardest to map, and was the difficulty in the behaviour or in the telemetry?
2. O-09 is benign. Does a benign observation still deserve a mapping? Argue both ways in one sentence each.
3. Your coverage table says a tactic has no data source. What is the cost of that gap compared with a tactic that
   has a source and no rule?
4. Why does ATT&CK allow one technique to belong to several tactics, and what does that mean for a coverage
   percentage?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Mapping accuracy | Several IDs invented or mismatched | All IDs valid, most tactics correct | All valid, sub-techniques used only where justified |
| Evidence discipline | Interpretation only | Observation and inference separated | Separation plus a specific alternative explanation per row |
| Coverage view | Counts rules | Table by tactic | Table by tactic with the highest-leverage gap named |
| Honesty | Gaps hidden | Gaps listed | Gaps listed with the data source that closes each |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Technique ID returns 404 | Remembered ID, or deprecated technique | Search by technique name on attack.mitre.org |
| Tactic does not appear on the technique page | Technique serves different tactics | Use one of the listed tactics, or pick a better technique |
| Every row maps to "Execution" | Matching the action, not the goal | Ask what the adversary gained, not what ran |
| Coverage table is a single percentage | Aggregated too early | Keep it per tactic; percentages hide which gaps matter |

## References

1. MITRE ATT&CK v20.0. <https://attack.mitre.org/resources/versions/> Accessed 2026-10-29.
2. MITRE ATT&CK — Enterprise tactics. <https://attack.mitre.org/tactics/enterprise/> Accessed 2026-10-29.
3. MITRE ATT&CK — Data sources. <https://attack.mitre.org/datasources/> Accessed 2026-10-29.
4. NIST SP 800-61 Rev. 3 (April 2025) — detection and analysis. <https://csrc.nist.gov/pubs/sp/800/61/r3/final>

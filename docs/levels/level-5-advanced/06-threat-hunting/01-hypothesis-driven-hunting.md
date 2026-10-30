---
title: "Hypothesis-Driven Hunting"
description: "Falsifiable hypotheses, data-source requirements, ATT&CK coverage as a map rather than a score, false-positive reduction by logic, and validation with safe simulations."
module_code: CYB-506
level: 5
kind: lesson
prerequisites: [CYB-506]
estimated_minutes: 90
difficulty: advanced
safety: conceptual
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [threat-hunting, attck, detection, false-positives, validation]
---

# Hypothesis-Driven Hunting

## Learning objectives

1. Write a hunting hypothesis that can be falsified by data.
2. Derive the required data sources and identify gaps before querying.
3. Treat ATT&CK coverage as a map of evidence, not a percentage score.
4. Reduce false positives by tightening logic rather than adding exceptions.
5. Validate a detection with a simulation and state what the simulation does not prove.

## 1. What makes a hunt a hunt

A hunt is not "looking at dashboards". It starts with a statement you can prove wrong:

> **Hypothesis:** If an adversary maintains access with a scheduled task that beacons to infrastructure, then at least
> one host will show a task whose command line references a remote destination, and that host will contact the same
> destination at regular intervals.

Two properties make it usable:

- **Falsifiable** — a specific observation would prove it wrong (no task referencing a remote destination).
- **Bounded** — a time range, an estate scope, and at least one data source that must exist.

| Bad hypothesis | Why | Better |
| --- | --- | --- |
| "Are we compromised?" | Unfalsifiable, unbounded | "Did any host create a scheduled task with a URL in the command line in the last 30 days?" |
| "Hunt for APT41" | Names a group, not an observation | "Do any hosts show the TTPs we attribute to that group, in this dataset?" |
| "Check for malware" | No data source implied | "Do any processes run from `%APPDATA%` with a parent in `%TEMP%`?" |

## 2. Knowledge drives the hypothesis

Three sources, in decreasing reliability:

1. **Your own telemetry** — what you have seen before, and what looked odd but was never explained. The richest source,
   and the only one that is about *your* estate.
2. **Threat intelligence** — a campaign against your sector. Converts to TTPs, not to indicator lists.
3. **Assumption** — "we would notice if X happened". Test it; this is where blind spots hide.

Intelligence is most useful as *behaviour*: "uses `certutil` to decode a payload" is huntable; a list of 400 IPs is a
blocklist problem, not a hunt.

## 3. Data sources before queries

Before writing a query, write the data requirement:

| Hypothesis element | Needs | Have it? |
| --- | --- | --- |
| Scheduled task created | Windows 4698, or Sysmon 1 for `schtasks.exe`, or task XML | |
| Task references remote destination | Command line in the creation event | |
| Regular outbound contact | Proxy logs, DNS logs, firewall logs, Sysmon 3 | |
| Regularity over time | At least several days of the above | |

**If a required source is missing, the hunt is not "failed" — it is answered by the gap.** "We cannot test this because
we do not log command lines for task creation" is a finding that changes the roadmap, and it is a legitimate hunt
output.

## 4. Queries: from broad to specific

Start broad enough to see the data, then narrow:

```sql
-- Broad: every scheduled task created in the window
SELECT ts, host, user, command FROM tasks WHERE ts >= '2026-10-01'

-- Narrow: tasks whose action references a network destination
SELECT * FROM tasks
WHERE command LIKE '%http%' OR command LIKE '%\\\\%'
```

Then quantify regularity, which is what separates a beacon from a chatty application:

```python
intervals = [b - a for a, b in zip(times, times[1:])]
mean = sum(intervals) / len(intervals)
variance = sum((i - mean) ** 2 for i in intervals) / len(intervals)
cv = (variance ** 0.5) / mean          # coefficient of variation
```

| CV | Interpretation |
| --- | --- |
| < 0.1 | Machine-regular; a scheduler or a beacon |
| 0.1–0.5 | Somewhat regular; polling with backoff, or busy user traffic |
| > 0.5 | Human or highly variable traffic |

**Low CV is not malicious.** Backup agents, monitoring and software update checks are machine-regular by design. The
finding is the *combination*: regular contact, to an unusual destination, from a task nobody documented.

## 5. Coverage: a map, not a score

Teams love "we cover 68% of ATT&CK". The number is meaningless without definitions. Use three states plus evidence:

| State | Definition | Evidence required |
| --- | --- | --- |
| **Present** | A detection exists, has fired on a test, and has an owner | Rule ID + last test date |
| **Partial** | Logged, but detection is manual or unreliable | Data source + why it is manual |
| **Absent** | No data, or no logic | Gap statement |

Then overlay **data sources**, because coverage without telemetry is fiction:

| Technique | Data source | Detection | State |
| --- | --- | --- | --- |
| T1053.005 Scheduled Task | 4698 | Rule fires on task creation with remote URL | Present |
| T1059.001 PowerShell | 4104 | Encoded command rule; misses file-based scripts | Partial |
| T1071.004 DNS | Sysmon 22 | No rule | Absent |

The useful output is the **blind-spot list**, ordered by (technique prevalence in your sector) × (ease of gaining the
data). Not a heat map for a slide.

## 6. False positives: fix the logic, not the symptom

The lazy fix is an exception list: "ignore `backup.exe`". It grows until the rule is meaningless.

Better, in order:

1. **Add the distinguishing attribute** — the beacon uses a *user-writable* path, or an unsigned binary, or a specific
   parent. `backup.exe` from `C:\Program Files` under the service account is not the same event.
2. **Use a ratio, not a threshold** — failures per account vs failures per IP distinguishes brute force from spraying.
3. **Correlate** — task creation *and* regular egress from the same host within an hour is rarer than either.
4. **Tune the window** — five failures in 10 minutes is different from five in a day.
5. **Baseline** — alert on deviation from the host's own normal, not on an absolute number.

Document each change with the false positive it removed and the true positive it might now miss. Tuning always trades
recall for precision; say which side you chose.

## 7. Validation with safe simulations

A rule is untested until it has fired on purpose:

| Test | Method | What it proves |
| --- | --- | --- |
| Positive | Perform the benign equivalent of the technique | The rule can fire |
| Negative | Perform a similar benign action | The rule does not fire on everything |
| Boundary | The exact threshold, either side | The rule's arithmetic |
| Data path | Check the event arrived in the SIEM | The pipeline works, not just the endpoint |

**Safe simulation examples** you can run on your own VM: create a scheduled task that echoes a string; run PowerShell
with an encoded command that prints text; write a file to `%TEMP%` and copy it to `%APPDATA%`. Each is reversible, and
each generates the telemetry a real technique would.

What the simulation does **not** prove: that the rule catches a real adversary who evades, uses a different parent, or
runs in a context you did not simulate. Write that sentence in every validation report.

## 8. The hunting loop

1. **Hypothesis** — falsifiable, bounded.
2. **Data** — sources identified; gaps recorded.
3. **Query** — broad, then specific.
4. **Analysis** — evidence, including absence; no speculation.
5. **Outcome** — detection, tuning, or a data gap with an owner.
6. **Record** — hypothesis, query, result, decision. A hunt that is not recorded cannot be repeated.

## Common mistakes and troubleshooting

| Mistake | Consequence | Fix |
| --- | --- | --- |
| Hypothesis with no falsifier | Endless hunt | State the observation that would disprove it |
| Querying before checking data | "No results" mistaken for "no activity" | Confirm the event exists for a known action |
| ATT&CK percentage as a goal | Coverage theatre | Present/partial/absent with evidence |
| Exception list for FPs | Rule erosion | Distinguishing attribute, ratio, correlation |
| Testing only the positive | Rule matches everything | Negative and boundary tests |
| Hunt not recorded | Unrepeatable, unlearnable | Write the record |

## Summary

Hunting is the discipline of asking a question your data can answer, and being honest when it cannot. Coverage is a map
of evidence with gaps named. Tuning is a deliberate trade, and validation is a simulation with a stated boundary.

## Review questions

1. Rewrite "hunt for lateral movement" as a falsifiable hypothesis with a data source.
2. Why is "we do not log that" a valid hunt outcome?
3. Give a CV you would treat as beacon-like, and two benign explanations.
4. What is wrong with suppressing false positives by process name?
5. What does a positive simulation prove, and what does it not?
6. Why must a hunt record include the query, not only the conclusion?

## Knowledge check

1. Your hunt returns zero rows. Name the two very different conclusions and how you tell them apart.
2. A rule fires on every `schtasks.exe` execution. Name two distinguishing attributes to add.
3. ATT&CK shows T1071.004 as "covered" because DNS is logged. What state should it be?
4. You add `AND user != 'svc-backup'` to stop false positives. What have you just created?

<details>
<summary>Answers</summary>

1. No activity, or no data. Confirm by testing a known action that should produce the same event.
2. Parent process, command-line content (remote path/URL), user context, binary path or signature.
3. Partial at best — logging is not detection.
4. A blind spot shaped exactly like the account an attacker would target.

</details>

## Next lesson

[LAB-506-01 · Hunt a Hypothesis](lab-01-hunt-hypothesis.md) — take a hypothesis from statement to evidence.

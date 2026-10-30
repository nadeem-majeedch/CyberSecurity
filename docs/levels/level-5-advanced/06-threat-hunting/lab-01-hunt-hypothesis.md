---
title: "LAB-506-01 · Hunt a Hypothesis"
description: "Take a falsifiable hypothesis through data requirements, queries, beacon-interval analysis and a written outcome — including one benign host that looks exactly like a beacon."
module_code: CYB-506
level: 5
kind: lab
prerequisites: [CYB-506]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-506-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [threat-hunting, hypothesis, beaconing, queries, attck]
---

# LAB-506-01 · Hunt a Hypothesis

## Prerequisites

The CYB-506 lesson and Python 3.10 or newer. The 62-row telemetry extract is reproduced in the lab; nothing
is collected from a live network.

## Scenario and background

A sector advisory says: "actors establish persistence with a scheduled task that runs a hidden PowerShell command every
five minutes and beacons to command infrastructure."

That is intelligence, not a hunt. Your job is to convert it into a hypothesis, test it against 62 rows of synthetic
endpoint and proxy telemetry, and write an outcome that a colleague can act on — including the part where one benign
server looks *more* like a beacon than the suspicious one.

## Learning objectives

1. Write a falsifiable, bounded hypothesis with a stated data requirement.
2. Query mixed telemetry to test it, and record what you could not test.
3. Quantify connection regularity and interpret it alongside context.
4. Distinguish a beacon from a scheduled backup with the same statistical shape.
5. Produce a hunt record: hypothesis, query, evidence, outcome, follow-up.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | Standard library only |
| A text editor or `jq` | — | For reading events |

## Safety

All telemetry is synthetic. Addresses are documentation ranges and `203.0.113.50` is not a real host. No query leaves
the machine.

## Environment

```bash
mkdir -p ~/hunt-lab && cd ~/hunt-lab
```

`gen_hunt.py`:

```python
#!/usr/bin/env python3
"""Generate synthetic proxy/endpoint telemetry for a hunting exercise."""
import csv
from datetime import datetime, timedelta, timezone

START = datetime(2026, 10, 20, 9, 15, tzinfo=timezone.utc)
JITTER = [0, 3, -2, 5, -4, 1, -3, 2, -1, 4, -5, 0]
rows = []

rows.append({"ts": "2026-10-20T09:12:00Z", "host": "WS01", "event_type": "task_created", "user": "a.khan",
             "detail": 'schtasks /create /tn SyncUpdate /tr "powershell -nop -w hidden -enc U1lOVEg=" /sc minute /mo 5'})

for i in range(36):
    moment = START + timedelta(seconds=300 * i + JITTER[i % len(JITTER)])
    rows.append({"ts": moment.strftime("%Y-%m-%dT%H:%M:%SZ"), "host": "WS01", "event_type": "net_connect",
                 "user": "a.khan", "detail": "203.0.113.50:443"})

for i in range(13):
    moment = START + timedelta(seconds=900 * i)
    rows.append({"ts": moment.strftime("%Y-%m-%dT%H:%M:%SZ"), "host": "FS01", "event_type": "net_connect",
                 "user": "svc-backup", "detail": "198.51.100.20:445"})

gaps = [40, 900, 120, 3000, 60, 7200, 800, 240, 5400, 130, 600, 1800]
moment = START
for i, gap in enumerate(gaps):
    moment = moment + timedelta(seconds=gap)
    rows.append({"ts": moment.strftime("%Y-%m-%dT%H:%M:%SZ"), "host": "WS01", "event_type": "net_connect",
                 "user": "a.khan", "detail": ["198.51.100.77:443", "203.0.113.9:80", "192.0.2.45:443"][i % 3]})

rows.sort(key=lambda r: r["ts"])
with open("hunt-events.csv", "w", encoding="utf-8", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=["ts", "host", "event_type", "user", "detail"])
    writer.writeheader()
    writer.writerows(rows)
print("rows:", len(rows))
```

```bash
python3 gen_hunt.py
head -3 hunt-events.csv
```

**Expected:** `rows: 62`, and the first data row is the `task_created` event at `2026-10-20T09:12:00Z`.

## The hypothesis

Write this in `hunt.md` before you look at the data — the point is to commit to a test:

> **Hypothesis H1:** If an actor is maintaining access via a five-minute scheduled task, then at least one host will
> show a task-creation event containing an encoded PowerShell command, and that host will connect repeatedly to the same
> destination at approximately 300-second intervals with low variance.

**Falsified if:** no task-creation event contains an encoded command, or no host shows a regular interval near 300s.

**Bounded by:** hosts `WS01`, `FS01`; window 2026-10-20T09:00Z to 2026-10-21T00:00Z; sources: task-creation events and
proxy connection logs.

**Data requirements:**

| Requirement | Source | Present? |
| --- | --- | --- |
| Task created, with command line | `task_created` events | Yes |
| Destination per connection | proxy log (`net_connect.detail`) | Yes |
| Enough history to measure interval | 15 hours | Yes |
| Process lineage for the PowerShell | process creation telemetry | **No** — gap |

That last row matters. The dataset cannot show *which* process ran the task, so you will be able to say "a task exists"
but not "the task spawned this connection". Write that down now; it belongs in the report.

## Procedure

### 1. Broad pass

```bash
python3 - <<'PY'
import csv
rows = list(csv.DictReader(open("hunt-events.csv", encoding="utf-8")))
print("rows:", len(rows))
for r in rows:
    if r["event_type"] == "task_created":
        print(r["ts"], r["host"], r["user"], "\n  ", r["detail"])
PY
```

**Expected:** one `task_created` event on `WS01` for `a.khan` at `09:12:00Z`, with `/sc minute /mo 5` and an encoded
PowerShell payload. That satisfies the first half of H1.

Note what an analyst must not do: run the encoded payload to see what it does. Decode it in a safe context — it is
`U1lOVEg=`, base64 for `SYNTH` — and record the decoding, not the execution.

### 2. Narrow to the host

```bash
python3 - <<'PY'
import csv, collections
rows = [r for r in csv.DictReader(open("hunt-events.csv", encoding="utf-8")) if r["event_type"] == "net_connect"]
per_host = collections.Counter(r["host"] for r in rows)
print("connections per host:", dict(per_host))
for (host, dest), count in sorted(collections.Counter((r["host"], r["detail"]) for r in rows).items()):
    print(f"{host:5} -> {dest:22} {count:3}")
PY
```

**Expected:** `WS01` has 48 connections, `FS01` 13. `WS01` connects to `203.0.113.50:443` **36** times — one destination
dominates, which is the shape of a beacon rather than browsing.

### 3. Quantify regularity

```bash
python3 - <<'PY'
import csv, collections, statistics
from datetime import datetime

rows = [r for r in csv.DictReader(open("hunt-events.csv", encoding="utf-8")) if r["event_type"] == "net_connect"]
groups = collections.defaultdict(list)
for r in rows:
    groups[(r["host"], r["detail"])].append(datetime.fromisoformat(r["ts"].replace("Z", "+00:00")))

print(f"{'HOST':5} {'DESTINATION':22} {'N':>3} {'MEAN_S':>8} {'CV':>6}")
for (host, dest), times in sorted(groups.items()):
    times.sort()
    gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:])]
    mean = statistics.mean(gaps)
    print(f"{host:5} {dest:22} {len(times):3} {mean:8.1f} {statistics.pstdev(gaps) / mean:6.3f}")
PY
```

**Expected:**

```text
HOST  DESTINATION              N   MEAN_S     CV
FS01  198.51.100.20:445       13    900.0  0.000
WS01  192.0.2.45:443           4   6410.0  0.492
WS01  198.51.100.77:443        4   5950.0  0.278
WS01  203.0.113.50:443        36    300.0  0.019
WS01  203.0.113.9:80           4   5850.0  0.355
```

Read this table properly. **The most regular connection in the dataset is the backup server, and it is benign.** `FS01`
hits its backup target every 900 seconds with zero variance because it is a cron-style agent; `WS01`'s beacon has a CV
of 0.019 because the generator adds a few seconds of jitter.

So CV ranks candidates; it does not decide. You need the other attributes:

| Attribute | FS01 → backup | WS01 → 203.0.113.50 |
| --- | --- | --- |
| Documented business function | Yes (backup) | No |
| Account | Service account | Interactive user |
| Port | 445, internal range | 443, external range |
| Preceded by a task creation | No | Yes, 3 minutes earlier, with an encoded payload |
| Interval | 900s | 300s, matching the task's `/mo 5` |

The pair — task creation with an encoded payload, then a 300-second cadence to the same external address — is the
finding. Neither half alone would justify escalation.

### 4. Check the negative cases

```bash
python3 - <<'PY'
import csv
rows = list(csv.DictReader(open("hunt-events.csv", encoding="utf-8")))
print("task events:", sum(1 for r in rows if r["event_type"] == "task_created"))
print("hosts:", sorted({r["host"] for r in rows}))
print("users:", sorted({r["user"] for r in rows}))
print("external destinations:", sorted({r["detail"] for r in rows if not r["detail"].startswith(("192.0.2.", "198.51.100.20"))}))
PY
```

**Expected:** one task event, two hosts, two users. `FS01` has no task creation event, which is why it fails the
hypothesis even though its interval is perfect.

### 5. Write the hunt record

`hunt.md`:

```markdown
# Hunt H1 — scheduled-task beacon

## Hypothesis
If an actor maintains access via a five-minute scheduled task, then a task-creation event with an encoded command exists,
and that host connects to one destination at ~300s intervals with low variance.

## Data
Task creation (present), proxy connections (present), process lineage (ABSENT — gap).

## Query
Group connections by (host, destination); compute mean interval and coefficient of variation.

## Evidence
- WS01, 2026-10-20T09:12:00Z, task "SyncUpdate", `/tr "powershell -nop -w hidden -enc U1lOVEg=" /sc minute /mo 5`, user a.khan.
- WS01 → 203.0.113.50:443, n=36, mean 300.0s, CV 0.019.
- FS01 → 198.51.100.20:445, n=13, mean 900.0s, CV 0.000 — benign backup, documented, service account, no task event.

## Assessment
H1 is SUPPORTED for WS01. Confidence: medium-high on the coexistence of task and cadence; low on attribution, because
the process lineage is not available and the payload was not executed.

## False positives considered
Backup agent, monitoring agent, software update checker. None explains an encoded command in a task with an external
destination from an interactive user's session.

## Gap and follow-up
No process-creation telemetry for the task's child process. Detection proposal: task creation where the action contains
`-enc`, a remote URL, or a user-writable path; correlate with egress from the same host within 10 minutes.
```

Note the "Assessment" wording: **supported**, not "confirmed compromise". The dataset shows the pattern; it does not
show an adversary.

### 6. Answer the honest questions

Add to `hunt.md`:

1. Which part of H1 could this dataset *not* test?
2. A colleague says "FS01 has the lowest CV, so it is the beacon". What is wrong with that reasoning?
3. What would you need in order to attribute the connection to the scheduled task rather than to the user's browser?
4. If the task had been created but no regular connection appeared, would the hunt be negative?

## Evidence to collect

- `hunt-events.csv` and `gen_hunt.py`.
- The registration table with counts, means and CVs.
- `hunt.md` with all six sections and the four answers.
- The decoded payload, decoded statically and documented as such.

## Verification

- [ ] Hypothesis written before analysis, with an explicit falsifier.
- [ ] Data requirements table includes the missing process-lineage source.
- [ ] 36 connections to one destination, mean 300s, CV 0.019, reproduced from your own run.
- [ ] `FS01` identified as benign despite CV 0.000, with reasons.
- [ ] Outcome uses "supported", not "confirmed".
- [ ] Follow-up names a concrete detection and its data source.
- [ ] Payload decoded, never executed.

## Teardown and reset

Nothing to tear down. Keep `hunt.md`; LAB-506-03 references the detection idea.

## Reflection

1. Why is the missing process-lineage source a finding rather than a failure?
2. Could an attacker make a beacon *less* regular to evade this analysis? What would you use instead of CV?
3. What is the risk of hunting with a 300-second expectation when the adversary uses a 4-hour interval?
4. Your detection will key on `-enc` in a task action. Name two legitimate uses that would produce false positives.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Hypothesis | Vague goal | Falsifiable | Falsifiable, bounded, with data requirement and stated gap |
| Analysis | Eyeballed rows | Counted connections | Interval statistics, context, and benign comparison |
| Judgement | Called everything suspicious | Excluded backup | Explained why the benign host has a *better* score |
| Record | Bullet points | Structured notes | Repeatable, with confidence and follow-up detection |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `statistics.mean` on empty list | One event for a destination | Require `len(times) > 1` |
| CV division by zero | All timestamps identical | Guard `mean > 0` |
| Wrong interval | Timestamps not sorted | Sort before differencing |
| Base64 decode fails | Padding or URL-safe alphabet | Decode the exact string; report the failure rather than guessing |
| Table includes task rows | Filtered on wrong event type | Filter `event_type == "net_connect"` |

## References

1. MITRE ATT&CK — T1053.005 (Scheduled Task), T1059.001 (PowerShell), T1071 (Application Layer Protocol). Accessed 2026-10-29.
2. The ThreatHunting Project — hypothesis-driven hunting model. Accessed 2026-10-29.
3. NIST SP 800-61 Rev. 3 — detection and analysis. Accessed 2026-10-29.

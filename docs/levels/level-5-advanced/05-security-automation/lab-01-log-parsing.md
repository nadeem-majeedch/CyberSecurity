---
title: "LAB-505-01 · Parse and Normalise Logs"
description: "Turn sshd syslog, JSON application logs and CSV firewall logs into one schema, skip malformed lines without crashing, and cover it with tests."
module_code: CYB-505
level: 5
kind: lab
prerequisites: [CYB-505]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-505-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [automation, python, parsing, normalisation, testing]
---

# LAB-505-01 · Parse and Normalise Logs

## Prerequisites

The CYB-505 lesson, Python 3.10 or newer, and `pytest`. The three log samples are written out in the lab
below, so no dataset has to be obtained and no network access is used.

## Scenario and background

Three data sources, three formats, one question: what happened on the gateway this morning? A SOC pipeline that cannot
answer that in one query is three pipelines wearing a trench coat.

You will write a parser that normalises all three into one event schema, refuses to crash on garbage, counts what it
could not parse, and is covered by tests. The output feeds LAB-505-02 and LAB-505-03.

## Learning objectives

1. Define a minimal event schema that supports detection and reporting.
2. Parse syslog, JSON lines and CSV into that schema, including timestamp normalisation to UTC.
3. Handle malformed input by skipping and counting, not raising.
4. Write unit tests for the happy path, boundaries and failures.
5. Produce a summary that makes data loss visible.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | `datetime.fromisoformat` with `Z` handling |
| `pytest` | 7+ | `pip install pytest` |

## Safety

All data is synthetic and refers to documentation address ranges (`192.0.2.0/24`, `198.51.100.0/24`,
`203.0.113.0/24`). No production log is used, and nothing in this lab makes a network call.

## Environment

```bash
mkdir -p ~/auto-lab/data && cd ~/auto-lab
```

`data/auth.log`:

```text
Oct 29 08:12:03 gw sshd[2211]: Failed password for invalid user admin from 192.0.2.61 port 51234 ssh2
Oct 29 08:12:19 gw sshd[2213]: Failed password for a.khan from 192.0.2.61 port 51240 ssh2
Oct 29 08:12:35 gw sshd[2215]: Failed password for a.khan from 192.0.2.61 port 51246 ssh2
Oct 29 08:12:51 gw sshd[2217]: Accepted password for a.khan from 192.0.2.74 port 51252 ssh2
Oct 29 08:13:07 gw sshd[2219]: Failed password for root from 192.0.2.61 port 51258 ssh2
Oct 29 08:13:22 gw sshd[2221]: Connection closed by authenticating user deploy 192.0.2.61 port 51264 [preauth]
this line is not syslog at all
Oct 29 08:13:40 gw sshd[2225]: Accepted publickey for deploy from 198.51.100.9 port 51270 ssh2
```

`data/app.jsonl`:

```json
{"ts":"2026-10-29T08:20:00Z","level":"warn","event":"login_failed","user":"a.khan","src_ip":"192.0.2.61","action":"deny"}
{"ts":"2026-10-29T08:20:14Z","level":"info","event":"login_ok","user":"a.khan","src_ip":"192.0.2.61","action":"allow"}
{"ts":"2026-10-29T08:21:02Z","level":"warn","event":"login_failed","user":"svc-report","src_ip":"203.0.113.77","action":"deny"}
{"ts":"2026-10-29T08:22:00Z","level":"info","event":"logout
```

The last line is truncated on purpose.

`data/fw.csv`:

```csv
ts,src,dst,port,action,rule
2026-10-29T08:25:01Z,192.0.2.61,192.0.2.20,22,deny,mgmt-ssh
2026-10-29T08:25:09Z,192.0.2.61,192.0.2.20,443,deny,egress-web
2026-10-29T08:26:00Z,192.0.2.74,192.0.2.20,22,allow,mgmt-ssh
bad,row,here
```

## Procedure

### 1. Decide the schema before the code

| Field | Type | Why |
| --- | --- | --- |
| `ts` | ISO 8601, UTC, `Z` | Sortable and unambiguous across sources |
| `source` | string | Which parser produced it — essential for debugging |
| `event_type` | string | The only field detections should key on |
| `user` | string or null | Absent in firewall events |
| `src_ip` | string or null | Entity for correlation |
| `action` | `allow` / `deny` / `info` | Comparable across sources |
| `raw` | string | Evidence, and the fallback when parsing is wrong |

The rule that matters: **`event_type` is normalised, `raw` is not.** If `ts` can be compared, the sources can be
joined.

### 2. Write the parser

`parse_logs.py`:

```python
#!/usr/bin/env python3
"""Normalise sshd syslog, JSON application logs and CSV firewall logs into one schema."""
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

YEAR = 2026  # syslog has no year; a real parser handles Dec/Jan rollover explicitly

SSHD = re.compile(
    r"^(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+sshd\[(?P<pid>\d+)\]:\s+(?P<msg>.*)$"
)
FAILED = re.compile(r"^Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+) port (?P<port>\d+)")
ACCEPTED = re.compile(r"^Accepted \S+ for (?P<user>\S+) from (?P<ip>\S+) port (?P<port>\d+)")
CLOSED = re.compile(r"^Connection closed by authenticating user (?P<user>\S+) (?P<ip>\S+) port (?P<port>\d+)")


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_sshd(line: str, source: str) -> dict:
    match = SSHD.match(line)
    if not match:
        raise ValueError("not an sshd syslog line")
    when = datetime.strptime(f"{YEAR} {match['ts']}", "%Y %b %d %H:%M:%S").replace(tzinfo=timezone.utc)
    msg = match["msg"]
    event_type, user, ip, action = "ssh_other", None, None, "info"
    for pattern, kind, act in ((FAILED, "auth_failure", "deny"), (ACCEPTED, "auth_success", "allow")):
        found = pattern.match(msg)
        if found:
            event_type, user, ip, action = kind, found["user"], found["ip"], act
            break
    else:
        found = CLOSED.match(msg)
        if found:
            event_type, user, ip = "ssh_closed", found["user"], found["ip"]
    return {
        "ts": iso(when),
        "source": source,
        "event_type": event_type,
        "user": user,
        "src_ip": ip,
        "action": action,
        "raw": line.strip(),
    }


def parse_json(line: str, source: str) -> dict:
    record = json.loads(line)
    for key in ("ts", "event"):
        if key not in record:
            raise ValueError(f"missing key: {key}")
    when = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
    return {
        "ts": iso(when),
        "source": source,
        "event_type": record["event"],
        "user": record.get("user"),
        "src_ip": record.get("src_ip"),
        "action": record.get("action", "info"),
        "raw": line.strip(),
    }


def parse_csv_row(row: dict, source: str) -> dict:
    for key in ("ts", "src", "dst", "action"):
        if not row.get(key):
            raise ValueError(f"missing column: {key}")
    when = datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))
    return {
        "ts": iso(when),
        "source": source,
        "event_type": "fw_" + row["action"],
        "user": None,
        "src_ip": row["src"],
        "action": row["action"],
        "raw": ",".join(row.get(k) or "" for k in ("ts", "src", "dst", "port", "action", "rule")),
    }


def main() -> int:
    data = Path("data")
    events, skipped, counts = [], [], {"auth.log": 0, "app.jsonl": 0, "fw.csv": 0}

    for n, line in enumerate((data / "auth.log").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(parse_sshd(line, "auth.log"))
            counts["auth.log"] += 1
        except ValueError as exc:
            skipped.append({"file": "auth.log", "line": n, "reason": str(exc)})

    for n, line in enumerate((data / "app.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(parse_json(line, "app.jsonl"))
            counts["app.jsonl"] += 1
        except (ValueError, json.JSONDecodeError) as exc:
            skipped.append({"file": "app.jsonl", "line": n, "reason": type(exc).__name__})

    with (data / "fw.csv").open(encoding="utf-8", newline="") as fh:
        for n, row in enumerate(csv.DictReader(fh), 2):
            try:
                events.append(parse_csv_row(row, "fw.csv"))
                counts["fw.csv"] += 1
            except ValueError as exc:
                skipped.append({"file": "fw.csv", "line": n, "reason": str(exc)})

    events.sort(key=lambda e: e["ts"])
    with open("events.jsonl", "w", encoding="utf-8") as fh:
        for event in events:
            fh.write(json.dumps(event, sort_keys=True) + "\n")

    summary = {
        "parsed": counts,
        "total": len(events),
        "skipped": len(skipped),
        "skipped_detail": skipped,
        "by_event_type": {},
    }
    for event in events:
        summary["by_event_type"][event["event_type"]] = summary["by_event_type"].get(event["event_type"], 0) + 1
    with open("summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print(json.dumps({k: summary[k] for k in ("total", "skipped", "parsed")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Run it:

```bash
python3 parse_logs.py
cat summary.json
head -3 events.jsonl
```

**Expected output:**

```text
{"parsed": {"app.jsonl": 3, "auth.log": 7, "fw.csv": 3}, "skipped": 3, "total": 13}
```

and in `summary.json`:

```json
{
  "by_event_type": {
    "auth_failure": 4,
    "auth_success": 2,
    "fw_allow": 1,
    "fw_deny": 2,
    "login_failed": 2,
    "login_ok": 1,
    "ssh_closed": 1
  },
  "parsed": {"app.jsonl": 3, "auth.log": 7, "fw.csv": 3},
  "skipped": 3,
  "skipped_detail": [
    {"file": "auth.log", "line": 7, "reason": "not an sshd syslog line"},
    {"file": "app.jsonl", "line": 4, "reason": "JSONDecodeError"},
    {"file": "fw.csv", "line": 5, "reason": "missing column: action"}
  ],
  "total": 13
}
```

Check the arithmetic yourself: 8 + 4 + 4 input lines, 3 unparseable, 13 events. **A parser that silently drops the
three would look identical in the output files** — which is why `skipped` is reported, not swallowed.

Note the timestamp round-trip: `Oct 29 08:12:03` became `2026-10-29T08:12:03Z`. The syslog line has no year, so the
parser assumes one; a production parser must handle the December/January boundary explicitly. Say so in your notes.

### 3. Test it

`test_parse_logs.py`:

```python
import json
import pytest
import parse_logs

FAILED_LINE = "Oct 29 08:12:19 gw sshd[2213]: Failed password for a.khan from 192.0.2.61 port 51240 ssh2"
INVALID_LINE = "Oct 29 08:12:03 gw sshd[2211]: Failed password for invalid user admin from 192.0.2.61 port 51234 ssh2"
CLOSED_LINE = "Oct 29 08:13:22 gw sshd[2221]: Connection closed by authenticating user deploy 192.0.2.61 port 51264 [preauth]"


def test_failed_password():
    event = parse_logs.parse_sshd(FAILED_LINE, "auth.log")
    assert event["event_type"] == "auth_failure"
    assert event["user"] == "a.khan"
    assert event["src_ip"] == "192.0.2.61"
    assert event["action"] == "deny"


def test_invalid_user_keeps_username():
    assert parse_logs.parse_sshd(INVALID_LINE, "auth.log")["user"] == "admin"


def test_closed_connection():
    assert parse_logs.parse_sshd(CLOSED_LINE, "auth.log")["event_type"] == "ssh_closed"


def test_timestamp_is_utc():
    assert parse_logs.parse_sshd(FAILED_LINE, "auth.log")["ts"].endswith("Z")


def test_garbage_raises():
    with pytest.raises(ValueError):
        parse_logs.parse_sshd("this is not syslog", "auth.log")


def test_json_missing_event_raises():
    with pytest.raises(ValueError):
        parse_logs.parse_json(json.dumps({"ts": "2026-10-29T08:20:00Z"}), "app.jsonl")


def test_csv_row_requires_action():
    with pytest.raises(ValueError):
        parse_logs.parse_csv_row({"ts": "2026-10-29T08:25:01Z", "src": "192.0.2.61", "dst": "192.0.2.20"}, "fw.csv")
```

```bash
pip install pytest
pytest -q
```

**Expected:** `7 passed`. Note what the tests do and do not prove: they pin the behaviour of three parsers on known
input. They do not prove the schema is right, nor that a new log format will parse.

### 4. Use the output

```bash
python3 - <<'PY'
import json, collections
rows = [json.loads(l) for l in open("events.jsonl", encoding="utf-8")]
by_src = collections.Counter(r["src_ip"] for r in rows if r["src_ip"])
print("top sources:", by_src.most_common(3))
fails = [r for r in rows if r["event_type"] in ("auth_failure", "login_failed")]
print("failures by user:", collections.Counter(r["user"] for r in fails))
allowed = [r for r in rows if r["action"] == "allow"]
print("first allow after failures:", allowed[0]["ts"], allowed[0]["user"])
PY
```

**Expected:** `192.0.2.61` dominates; `a.khan` has the most failures; the first allow is `2026-10-29T08:12:51Z` for
`a.khan` — from `192.0.2.74`, a **different** source address than the failures. That single observation is the reason
normalisation exists: no individual log showed it.

## Evidence to collect

- `parse_logs.py`, `test_parse_logs.py`.
- `summary.json` and the pytest output.
- The three-line analysis output above.
- A note on the year assumption and what would break in January.

## Verification

- [ ] Total 13 events, 3 skipped, with the skip line numbers matching the inputs.
- [ ] All timestamps end in `Z` and sort correctly across sources.
- [ ] Malformed line, truncated JSON and short CSV row are all skipped without a traceback.
- [ ] 7 tests pass.
- [ ] The "allow after failures from a different IP" observation is reproduced from `events.jsonl`, not from the raw logs.
- [ ] The syslog year assumption is documented.

## Teardown and reset

Nothing to tear down. Keep `events.jsonl` for the next lab.

## Reflection

1. Why is `event_type` normalised while `raw` is preserved verbatim?
2. The parser assumed the year 2026. Describe the failure that occurs on 1 January and how you would handle it.
3. Your tests pass, but a new application log format appears next month. What test would have caught the gap, and what
   would not?
4. Is skipping a malformed line the right default? When should the pipeline fail loudly instead?

## Extensions

- Add a Windows Security event export (CSV) as a fourth source with `event_type` mapping for 4624/4625.
- Add a `--fail-on-skip` flag and use it in CI, where silent data loss is unacceptable.
- Deduplicate identical events from two sources that both reported the same login.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Schema | Ad hoc fields | Common fields | Justified per field; sorting works across sources |
| Parsing | One format | Three formats | Malformed input counted and reported |
| Tests | None | Happy path | Failure and boundary cases; limits of tests stated |
| Analysis | Ran the script | Counted sources | Derived a cross-source observation from the output |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `JSONDecodeError` uncaught | Using `json.loads` outside the `try` | Wrap the call, as in `main` |
| All timestamps identical | Sorting strings before normalising | Normalise first, then sort |
| `KeyError` on `row["port"]` | Short CSV row | Access with `.get`, as the parser does |
| Off-by-one line numbers | `enumerate` start value | Start at 1 for text lines, 2 for CSV after the header |
| Tests import fails | Running pytest outside the project dir | `cd ~/auto-lab` first, or add `conftest.py` |

## References

1. Python — `datetime`, `re`, `csv`, `json` standard library documentation. Accessed 2026-10-29.
2. `pytest` documentation — `raises`, fixtures. Accessed 2026-10-29.
3. RFC 5424 — syslog protocol (for the year and timestamp discussion). Accessed 2026-10-29.
4. Elastic Common Schema — field naming reference for normalised security events. Accessed 2026-10-29.

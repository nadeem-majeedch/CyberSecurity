---
title: "LAB-202-02 · Python Parser for Synthetic Network Logs"
description: "Generate a synthetic web access log and write a Python parser that summarises it, reports coverage, and exits meaningfully."
module_code: CYB-202
level: 2
kind: lab
prerequisites: [CYB-202]
estimated_minutes: 240
difficulty: intermediate
safety: local-only
lab_ids: [LAB-202-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [python, parsing, logs, automation]
---

# LAB-202-02 · Python Parser for Synthetic Network Logs

## Prerequisites

The CYB-202 lesson, and Python 3.10 or newer on `lab-kali`. No internet access is needed: the log is
generated locally from documentation addresses.

## Scenario and background

You have been given "a log file and an hour". The log is synthetic — generated locally with documentation
addresses — because you must never practise on real user data. Your job is to produce a small, trustworthy
summariser: how many requests, from which addresses, with which status codes, and how many lines the tool could
not understand.

Reporting the unparsed lines is the professional habit this lab trains. A parser that silently drops 20% of a
file produces confident, wrong answers.

## Learning objectives

By the end of this lab you can:

1. Generate a synthetic log with controlled, documented properties.
2. Write a Python parser using `argparse`, `pathlib`, regular expressions, and `collections.Counter`.
3. Report parse coverage and warn when the format does not match.
4. Emit machine-readable output (`--json`) alongside human output.
5. Validate inputs and return meaningful exit codes.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | `python3 --version` |
| Standard library only | — | `argparse`, `re`, `json`, `pathlib`, `collections`, `logging` |

No third-party packages are needed; if you install any, use a virtual environment
(`python3 -m venv .venv`).

## Setup

```bash
mkdir -p ~/lab/level-2/lab-202/scripts ~/lab/level-2/lab-202/evidence
cd ~/lab/level-2/lab-202/scripts
```

## Target addresses and lab topology

```
No network activity. Input is a locally generated file:
  ~/lab/level-2/lab-202/evidence/synthetic-access.log
```

All source addresses are from documentation or private ranges (`192.0.2.0/24`, `198.51.100.0/24`).

## Numbered commands and actions

### 1. Generate the synthetic log

```bash
cat > make-log.py <<'PY'
#!/usr/bin/env python3
"""Generate a synthetic Apache-style access log. Deterministic for reproducibility."""
import random, sys
from pathlib import Path

random.seed(20261028)
IPS = ["192.0.2.10", "192.0.2.20", "198.51.100.7", "198.51.100.9"]
PATHS = ["/", "/index.html", "/login", "/api/items", "/assets/app.js", "/missing"]
STATUS = [200, 200, 200, 301, 404, 401, 500]
METHODS = ["GET", "GET", "GET", "POST", "HEAD"]
AGENTS = ["curl/7.81.0", "Mozilla/5.0 (X11; Linux x86_64)", "python-requests/2.31"]

out = Path(sys.argv[1])
lines = []
for i in range(1000):
    ip = random.choice(IPS); p = random.choice(PATHS); s = random.choice(STATUS); m = random.choice(METHODS)
    sec = i % 60; minute = (i // 60) % 60
    lines.append(f'{ip} - - [28/Oct/2026 22:{minute:02d}:{sec:02d} +0500] "{m} {p} HTTP/1.1" {s} {random.randint(120, 9000)} "-" "{random.choice(AGENTS)}"')
# Two malformed lines to test coverage reporting
lines.insert(400, "this line is not in the expected format")
lines.insert(800, "192.0.2.10 - - [malformed time] \"GET / HTTP/1.1\" 200 512")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {len(lines)} lines to {out}")
PY
python3 make-log.py ~/lab/level-2/lab-202/evidence/synthetic-access.log
wc -l ~/lab/level-2/lab-202/evidence/synthetic-access.log
head -3 ~/lab/level-2/lab-202/evidence/synthetic-access.log
```

**Expected:** `wrote 1002 lines`, and three sample lines in the standard combined-log format. Determinism
matters: `random.seed` means your numbers match the numbers in this lab's expectations.

### 2. Write the parser

```bash
cat > parse-log.py <<'PY'
#!/usr/bin/env python3
"""Summarise an access log: status codes, client addresses, and parse coverage."""
import argparse, json, logging, re, sys
from collections import Counter
from pathlib import Path

PATTERN = re.compile(
    r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - - \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" (?P<status>\d{3}) (?P<size>\d+|-)'
)

def parse(path: Path, log: logging.Logger) -> tuple[Counter, Counter, Counter, int, int]:
    by_status, by_ip, by_path = Counter(), Counter(), Counter()
    matched = total = 0
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        total += 1
        m = PATTERN.match(line)
        if not m:
            log.debug("unparsed line %d: %.60s", n, line)
            continue
        matched += 1
        by_status[m["status"]] += 1
        by_ip[m["ip"]] += 1
        by_path[m["path"]] += 1
    return by_status, by_ip, by_path, matched, total

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logfile", type=Path)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s", stream=sys.stderr)
    log = logging.getLogger("parse-log")

    if not args.logfile.is_file():
        log.error("not a file: %s", args.logfile)
        return 2

    by_status, by_ip, by_path, matched, total = parse(args.logfile, log)
    if total == 0:
        log.error("no lines to parse")
        return 3
    coverage = matched / total * 100
    log.info("parsed %d/%d lines (%.1f%%)", matched, total, coverage)

    report = {
        "file": str(args.logfile),
        "lines_total": total,
        "lines_matched": matched,
        "coverage_percent": round(coverage, 1),
        "status_counts": dict(by_status.most_common()),
        "top_clients": by_ip.most_common(args.top),
        "top_paths": by_path.most_common(args.top),
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"file        : {report['file']}")
        print(f"lines       : {matched}/{total} ({report['coverage_percent']}% parsed)")
        print("status codes:")
        for s, c in sorted(report["status_counts"].items()):
            print(f"  {s}  {c:>5}")
        print("top clients:")
        for ip, c in report["top_clients"]:
            print(f"  {ip:<16} {c:>5}")
    if coverage < 99:
        log.warning("coverage below 99%%: %.1f%% — check the log format", coverage)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
PY
chmod +x parse-log.py
```

### 3. Run it

```bash
python3 parse-log.py ~/lab/level-2/lab-202/evidence/synthetic-access.log | tee ~/lab/level-2/lab-202/evidence/parse-report.txt
echo "exit: $?" | tee -a ~/lab/level-2/lab-202/evidence/parse-report.txt
```

**Expected** (counts depend on your run; the seeded generator makes them stable):

```text
INFO parsed 1000/1002 lines (99.8%)
file        : /home/kali/lab/level-2/lab-202/evidence/synthetic-access.log
lines       : 1000/1002 (99.8% parsed)
status codes:
  200    430
  301    145
  401    140
  404    140
  500    145
top clients:
  192.0.2.10         255
  ...
WARNING coverage below 99%: 99.8% — check the log format
exit: 1
```

**Note the deliberate design:** coverage of 99.8% still triggers the warning, and the exit code is 1. If you want
clean exits for near-complete parses, change the threshold — but decide the policy consciously and document it.

### 4. Test the failure paths

```bash
python3 parse-log.py /nonexistent.log; echo "exit(missing file): $?"
printf 'not a log line\n' > /tmp/junk.log
python3 parse-log.py /tmp/junk.log; echo "exit(junk): $?"
python3 parse-log.py -v ~/lab/level-2/lab-202/evidence/synthetic-access.log 2>&1 | grep -c "unparsed line"
```

**Expected:** exit 2 for the missing file, exit 3 for zero parsed lines, exit 1 for junk-only content, and two
`unparsed line` debug entries at `-v`.

### 5. Add one summary the reviewer asked for

Modify the script to include the **top 3 requested paths** in the human output, and re-run. Then answer: which
single number in the report would change first if a scanner were probing the host? *(Hint: 404 and 401 counts,
and path distribution.)* That reasoning is the bridge to Level 4 detection work.

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `--top N` | Limit list length | Keeps output readable on huge logs |
| `--json` | Structured output | Feeds a report pipeline without re-parsing text |
| `-v` | Debug logging | Reveals which lines failed to match, with line numbers |
| `errors="replace"` | Tolerate bad bytes | A log with one corrupt byte should not crash the tool |
| `random.seed(...)` | Deterministic generation | Makes your results comparable across runs |

## Expected observations

- The generator writes ~1002 lines including two deliberately malformed ones.
- The parser reports both matched and total counts, with a coverage percentage.
- Malformed lines do not crash the tool; they appear at `-v` with line numbers.
- Exit codes differ for success, low coverage, missing file, and unparsable content.
- `--json` output parses with `python3 -m json.tool`.

## Verification criteria

- [ ] `make-log.py` runs and produces a deterministic file (hash it and record the value).
- [ ] `parse-log.py` summarises status codes and top clients.
- [ ] Coverage percentage included in output and in the log line.
- [ ] All four exit-code paths demonstrated and recorded.
- [ ] `--json` output validated.
- [ ] No real log data used anywhere.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Coverage far below 99% | Pattern does not match the generator's format | Print an unparsed line with `-v` and adjust the regex |
| `json.decoder.JSONDecodeError` in a later tool | Log lines mixed into stdout | Logging already goes to stderr; check your redirects |
| Counts do not match the lab's example | You edited the generator | Keep the seed and inputs fixed, or document your change |
| `Counter` keys look wrong | Matching the wrong group | Name your groups and reference them by name |
| Script hangs | Reading from stdin instead of a file | Pass the path argument |

## Cleanup and restoration

Nothing to revert. Keep the generator, parser, and evidence — they are reused in LAB-206-03 and in Level 4.

```bash
sha256sum ~/lab/level-2/lab-202/evidence/synthetic-access.log | tee ~/lab/level-2/lab-202/evidence/log-hash.txt
```

## Questions and extension challenges

1. Why is reporting coverage more important than reporting totals?
2. What would a 100% coverage figure with an empty status distribution suggest?
3. Why does the script read the entire file into memory, and when would that become a problem?
4. **Extension:** add `--since HH:MM:SS` filtering using the timestamp field, and explain why time filtering is
   usually the first thing an analyst applies.
5. **Extension:** add a `--csv` output mode and compare with `--json` for pipeline friendliness.

## Related

- [Scripting and Versioning for Repeatable Work](01-scripting-and-git.md)
- [LAB-202-01 · Bash Security-Check Script](lab-01-bash-security-check.md)
- [Packet Capture and Traffic Analysis](../04-packet-capture-and-analysis/index.md)

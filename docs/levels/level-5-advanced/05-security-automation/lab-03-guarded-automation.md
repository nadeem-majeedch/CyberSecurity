---
title: "LAB-505-03 · Final Challenge: Guarded Automation"
description: "Test detection logic against fixtures, then build a containment script that defaults to dry-run, refuses out-of-scope and protected targets, authenticates, retries safely and audits every decision."
module_code: CYB-505
level: 5
kind: lab
prerequisites: [CYB-505]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-505-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [automation, testing, incident-response, secrets, api, final-challenge]
---

# LAB-505-03 · Final Challenge: Guarded Automation

## Scenario and background

Your SOC has a brute-force detection and a containment API. The obvious next step — "block the source
automatically" — is how teams discover that their detection can select the domain controller.

This challenge is in two parts. First you prove the detection works against fixtures, including the ones it must *not*
fire on. Then you build the containment script, and you will be graded on what it refuses to do.

## Learning objectives

1. Test detection logic against positive, negative and boundary fixtures.
2. Implement a dry-run default with a scale confirmation.
3. Refuse out-of-scope and protected targets, with an audited reason.
4. Authenticate with a bearer token from the environment, failing closed.
5. Retry only transient failures, handle 401/403 by stopping, and report per-target outcomes.
6. Produce an audit trail sufficient to answer "who blocked what, and why".

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | Standard library only |
| `pytest` | 7+ | Test harness |

## Safety

The API is a **mock** on loopback, the addresses are documentation ranges, and the token is a placeholder. No real
firewall, identity provider or ticketing system is contacted, and no real credential is used.

## Part A — Test the detection before trusting the action

`detect.py`:

```python
#!/usr/bin/env python3
"""Brute-force detection over normalised events, with a testable interface."""
import collections
from datetime import datetime

THRESHOLD = 5
WINDOW_SECONDS = 600
FAILURE_TYPES = {"auth_failure", "login_failed"}


def _parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def detect(events):
    failures = collections.defaultdict(list)
    successes = collections.defaultdict(list)
    for event in events:
        moment = _parse(event["ts"])
        if event.get("event_type") in FAILURE_TYPES:
            failures[event["src_ip"]].append(moment)
        elif event.get("action") == "allow":
            successes[event["src_ip"]].append(moment)

    alerts = []
    for ip, times in failures.items():
        times.sort()
        for start in times:
            window = [t for t in times if 0 <= (t - start).total_seconds() <= WINDOW_SECONDS]
            if len(window) >= THRESHOLD:
                alerts.append({
                    "rule": "ssh_bruteforce",
                    "src_ip": ip,
                    "count": len(window),
                    "first": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "success_after": any(0 < (s - start).total_seconds() <= WINDOW_SECONDS for s in successes[ip]),
                })
                break
    return alerts
```

`test_detect.py` — the matrix is the deliverable, not just the green ticks:

```python
import pytest
import detect


def ev(ts, ip, event_type="auth_failure", action="deny"):
    return {"ts": ts, "src_ip": ip, "event_type": event_type, "action": action}


def test_bruteforce_with_success_fires():
    events = [ev(f"2026-10-29T08:0{i}:00Z", "10.0.0.5") for i in range(6)]
    events.append(ev("2026-10-29T08:06:00Z", "10.0.0.5", "auth_success", "allow"))
    alerts = detect.detect(events)
    assert len(alerts) == 1
    assert alerts[0]["src_ip"] == "10.0.0.5"
    assert alerts[0]["count"] == 6
    assert alerts[0]["success_after"] is True


def test_two_failures_do_not_fire():
    events = [ev(f"2026-10-29T08:2{i}:00Z", "10.0.0.7") for i in range(2)]
    assert detect.detect(events) == []


def test_failures_spread_over_hours_do_not_fire():
    events = [ev(f"2026-10-29T{8 + i:02d}:00:00Z", "10.0.0.8") for i in range(6)]
    assert detect.detect(events) == []


def test_window_boundary_is_inclusive():
    events = [ev(f"2026-10-29T08:{m:02d}:00Z", "10.0.0.9") for m in (0, 2, 4, 6, 8, 10)]
    alerts = detect.detect(events)
    assert len(alerts) == 1 and alerts[0]["count"] == 6


@pytest.mark.parametrize("source", ["10.0.0.5"])
def test_alert_shape(source):
    events = [ev(f"2026-10-29T08:0{i}:00Z", source) for i in range(5)]
    alert = detect.detect(events)[0]
    assert set(alert) == {"rule", "src_ip", "count", "first", "success_after"}
```

```bash
pytest -q
```

**Expected:** 5 passed (the parametrised test counts once).

**Read the boundary test carefully.** Six failures exactly ten minutes apart *do* fire, because the window comparison
is `<=`. That is a decision, and the test pins it. If your detection says "within ten minutes" exclusive, change the
operator and the test together — never one without the other.

**Also note what the rule cannot distinguish:** six failures against one account and six failures against six accounts
from the same IP both fire, labelled "brute force". Labelling a spray as brute force is acceptable noise; missing it is
not. Say so in your report.

## Part B — The containment script

`alerts.jsonl`:

```json
{"alert_id":"A-1001","rule":"ssh_bruteforce","src_ip":"192.0.2.61","host":"web01","events":14,"success_after":true}
{"alert_id":"A-1002","rule":"ssh_bruteforce","src_ip":"192.0.2.99","host":"app02","events":9,"success_after":false}
{"alert_id":"A-1003","rule":"ssh_bruteforce","src_ip":"192.0.2.20","host":"dc01","events":22,"success_after":true}
{"alert_id":"A-1004","rule":"ssh_bruteforce","src_ip":"198.51.100.44","host":"web01","events":31,"success_after":true}
{"alert_id":"A-1005","rule":"port_scan","src_ip":"192.0.2.74","host":"web01","events":3,"success_after":false}
```

Five alerts, of which:

| Alert | Why it matters |
| --- | --- |
| A-1001 | In scope, qualifies — should be blocked |
| A-1002 | In scope — the mock API fails for this target, testing partial failure |
| A-1003 | The **domain controller** — must be refused |
| A-1004 | Outside `192.0.2.0/24` — must be refused |
| A-1005 | Below the event threshold — must be skipped |

`mock_api.py` — loopback only, bearer auth, and one failing target:

```python
#!/usr/bin/env python3
"""Mock containment API: bearer auth, per-target results, one deliberately failing target."""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = "lab-token-123"
CALLS = []


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"unauthorized"}')
            return
        ip = self.path.rsplit("/", 1)[-1]
        CALLS.append(ip)
        if ip.endswith(".99"):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error":"backend failure"}')
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"blocked": ip, "calls": len(CALLS)}).encode())

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
```

`contain.py`:

```python
#!/usr/bin/env python3
"""Block the source address of qualifying alerts. Dry run unless --apply --confirm N."""
import argparse
import ipaddress
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

ALLOWED = [ipaddress.ip_network("192.0.2.0/24")]
PROTECTED = {"192.0.2.1", "192.0.2.20"}
MIN_EVENTS = 5
RUN_ID = str(uuid.uuid4())[:8]


class AuthError(Exception):
    pass


class Forbidden(Exception):
    pass


class Transient(Exception):
    pass


def audit(entry):
    entry = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "run_id": RUN_ID,
             "actor": os.environ.get("USER", "unknown"), **entry}
    with open("audit.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def load_alerts(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def scope_reason(ip):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return "invalid-address"
    if str(addr) in PROTECTED:
        return "protected"
    if not any(addr in net for net in ALLOWED):
        return "out-of-scope"
    return None


def post_block(url, ip, token):
    request = urllib.request.Request(
        f"{url.rstrip('/')}/block/{ip}", method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=b"{}",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise (AuthError if exc.code == 401 else Forbidden)(f"HTTP {exc.code}")
        if exc.code == 429:
            time.sleep(min(float(exc.headers.get("Retry-After", "1")), 5))
            raise Transient("HTTP 429")
        if 500 <= exc.code < 600:
            raise Transient(f"HTTP {exc.code}")
        raise


def with_retry(fn, attempts=3, base=0.2):
    for attempt in range(attempts):
        try:
            return fn()
        except Transient as exc:
            if attempt == attempts - 1:
                raise
            time.sleep(base * (2 ** attempt) + 0.05)
            print(f"    retry {attempt + 1} after {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alerts", default="alerts.jsonl")
    parser.add_argument("--apply", action="store_true", help="perform actions; default is a dry run")
    parser.add_argument("--confirm", help="must equal the number of targets when --apply is used")
    parser.add_argument("--url", default=os.environ.get("LAB_API_URL", "http://127.0.0.1:8099"))
    args = parser.parse_args()

    alerts = load_alerts(args.alerts)
    targets, decisions = [], []
    for alert in alerts:
        ip = alert["src_ip"]
        if alert["events"] < MIN_EVENTS:
            decisions.append((alert["alert_id"], ip, "skipped-below-threshold"))
            continue
        reason = scope_reason(ip)
        if reason:
            decisions.append((alert["alert_id"], ip, f"refused-{reason}"))
            continue
        decisions.append((alert["alert_id"], ip, "selected"))
        if ip not in targets:
            targets.append(ip)

    for alert_id, ip, decision in decisions:
        audit({"event": "decision", "alert_id": alert_id, "target": ip, "decision": decision})

    print(f"run {RUN_ID}: {len(alerts)} alerts, {len(targets)} unique targets")
    for alert_id, ip, decision in decisions:
        print(f"  {alert_id}  {ip:16} {decision}")

    if not args.apply:
        print(f"DRY RUN - nothing was changed. Re-run with --apply --confirm {len(targets)} to act.")
        return 0

    if args.confirm != str(len(targets)):
        print(f"refusing to apply: --confirm must equal {len(targets)}", file=sys.stderr)
        audit({"event": "aborted", "reason": "confirm-mismatch", "expected": len(targets)})
        return 3

    token = os.environ.get("LAB_API_TOKEN")
    if not token:
        print("LAB_API_TOKEN is not set; refusing to run without authentication", file=sys.stderr)
        audit({"event": "aborted", "reason": "missing-token"})
        return 2

    failures = 0
    for ip in targets:
        try:
            result = with_retry(lambda ip=ip: post_block(args.url, ip, token))
            print(f"  blocked {ip}: {result}")
            audit({"event": "blocked", "target": ip, "result": result})
        except AuthError:
            print("authentication failed; stopping", file=sys.stderr)
            audit({"event": "aborted", "reason": "auth-failed", "target": ip})
            return 4
        except Forbidden:
            print(f"not authorised to block {ip}; stopping", file=sys.stderr)
            audit({"event": "aborted", "reason": "forbidden", "target": ip})
            return 4
        except Exception as exc:
            failures += 1
            print(f"  failed {ip}: {exc}", file=sys.stderr)
            audit({"event": "failed", "target": ip, "error": str(exc)})

    print(f"done: {len(targets) - failures} ok, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
```

## Procedure

### 1. Start the mock API

```bash
python3 mock_api.py 8099 &
```

### 2. Dry run, no credentials

```bash
python3 contain.py
```

**Expected:**

```text
run 036eada6: 5 alerts, 2 unique targets
  A-1001  192.0.2.61       selected
  A-1002  192.0.2.99       selected
  A-1003  192.0.2.20       refused-protected
  A-1004  198.51.100.44    refused-out-of-scope
  A-1005  192.0.2.74       skipped-below-threshold
DRY RUN - nothing was changed. Re-run with --apply --confirm 2 to act.
```

The dry run needs no token: it cannot change anything, so it must not require a credential. The `run` id differs each
time; the decisions do not.

### 3. Prove the refusals

```bash
python3 contain.py --apply --confirm 2; echo "exit=$?"
```

**Expected:** `LAB_API_TOKEN is not set; refusing to run without authentication`, exit `2`.

```bash
LAB_API_TOKEN=lab-token-123 python3 contain.py --apply --confirm 5; echo "exit=$?"
```

**Expected:** `refusing to apply: --confirm must equal 2`, exit `3`. Note that the token alone does not authorise the
action; the scale confirmation is separate.

### 4. Apply

```bash
rm -f audit.jsonl
LAB_API_TOKEN=lab-token-123 python3 contain.py --apply --confirm 2; echo "exit=$?"
```

**Expected:**

```text
run 91bdf5c9: 5 alerts, 2 unique targets
  ...
  blocked 192.0.2.61: {'blocked': '192.0.2.61', 'calls': 1}
    retry 1 after HTTP 500
    retry 2 after HTTP 500
  failed 192.0.2.99: HTTP 500
done: 1 ok, 1 failed
exit=1
```

**This is the most important result in the lab.** One target succeeded, one failed after bounded retries, and the exit
code is `1` — not `0`. A script that reported success here would tell an analyst the estate is contained when half of
it is not.

### 5. Authentication failure stops the run

```bash
LAB_API_TOKEN=wrong python3 contain.py --apply --confirm 2; echo "exit=$?"
```

**Expected:** `authentication failed; stopping`, exit `4`, and **no** attempt to continue to the next target. Retrying a
401 cannot succeed and looks like a brute-force attack on your own API.

### 6. Read the audit trail

```bash
cat audit.jsonl
```

**Expected:** one `decision` line per alert (including every refusal and skip), then `blocked` and `failed` events with
the target and result. The output in step 4 produced six such lines. Answer from the file alone:

1. Who ran it? (`actor` — `unknown` on this shell; explain how you would populate it from a real identity)
2. Which run? (`run_id`)
3. Why was `192.0.2.20` not blocked? (`decision: refused-protected`)
4. What failed, and with what error? (`failed`, `HTTP 500`)
5. Was the token ever written to the audit log? (It must not be — check.)

### 7. Test the script, not just the API

```python
import json
import subprocess


def run(args, env=None):
    return subprocess.run(["python3", "contain.py", *args], capture_output=True, text=True, env=env)


def test_dry_run_exit_zero_without_token():
    result = run([])
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout


def test_apply_without_token_refuses():
    result = run(["--apply", "--confirm", "2"], env={"PATH": "/usr/bin:/bin"})
    assert result.returncode == 2
    assert "refusing" in result.stderr.lower()


def test_wrong_confirm_refuses():
    env = {"PATH": "/usr/bin:/bin", "LAB_API_TOKEN": "lab-token-123"}
    result = run(["--apply", "--confirm", "9"], env=env)
    assert result.returncode == 3


def test_protected_target_never_selected():
    run([])
    decisions = [json.loads(l) for l in open("audit.jsonl", encoding="utf-8")]
    chosen = {d["target"] for d in decisions if d.get("decision") == "selected"}
    assert "192.0.2.20" not in chosen
    assert "198.51.100.44" not in chosen
```

**Expected:** 4 passed. The fourth test asserts on the audit log, which is the artifact you would rely on in a review —
not on stdout.

## Deliverables

- `detect.py`, `test_detect.py`, `contain.py`, `mock_api.py`, `alerts.jsonl`.
- A test matrix for the detection: fixture, expected, actual.
- `audit.jsonl` from a successful run.
- `review.md` covering:
  1. The five alert dispositions and why each was chosen.
  2. The exit-code table (`0`, `1`, `2`, `3`, `4`) and what a pipeline should do with each.
  3. What the script would need before it could touch a real firewall.
  4. The one behaviour you would add, and the one you would refuse to add, and why.

## Verification

- [ ] Detection fires on the brute-force fixture with `success_after: true`.
- [ ] Detection does not fire on two failures, nor on six spread across hours.
- [ ] The window boundary is tested and the operator is documented.
- [ ] Dry run works with no credential and changes nothing.
- [ ] Missing token → exit 2; wrong scale → exit 3; bad credential → exit 4; partial failure → exit 1.
- [ ] Protected and out-of-scope targets appear in the audit log as refusals.
- [ ] Audit log contains no token.
- [ ] 500s are retried a bounded number of times, then reported as failed.

## Teardown and reset

```bash
# stop the mock API started in step 1
kill %1 2>/dev/null
unset LAB_API_TOKEN
rm -f audit.jsonl
```

Nothing outside loopback was contacted.

## Reflection

1. Your script refuses `192.0.2.20` because it is on a static list. What happens when the DC's address changes, and
   what control replaces a hardcoded list?
2. The exit code is `1` on partial failure, which most CI pipelines treat as "failed". Is that the right behaviour for
   an incident-response tool? What would you want instead?
3. `--confirm N` forces the operator to state the scale. Describe a scenario where that alone prevents an outage, and
   one where it does not.
4. You now have automated containment. What would you require before enabling it without a human in the loop?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Detection tests | Happy path | Positive and negative | Boundary pinned; spray/brute limitation stated |
| Refusals | None | Scope check | Scope **and** protected, both audited with reasons |
| Failure handling | Crashes | Retries everything | Bounded retries for 5xx only; 401/403 stop; exit codes distinct |
| Audit | Print statements | JSON log | Decisions, refusals, results, actor and run id; no secret |
| Judgement | Followed steps | Explained choices | States what is missing before production use |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Connection refused` | Mock API not running | Start it on 8099 and check the port |
| Every action refused | Allowlist does not contain the test IPs | Add the lab range, never widen to `0.0.0.0/0` |
| Exit 3 unexpectedly | Duplicate IPs collapsed the target count | Count unique targets, as the script does |
| Token appears in logs | Logging request headers | Log a credential identifier, never the value |
| Tests fail on `audit.jsonl` | Previous run's file | Clear it before the run under test |

## References

1. Python — `urllib.request`, `ipaddress`, `argparse`. Accessed 2026-10-29.
2. RFC 6750 — Bearer token usage and the 401/403 distinction. Accessed 2026-10-29.
3. NIST SP 800-61 Rev. 3 — incident response handling and containment decisions. Accessed 2026-10-29.
4. CISA — playbook guidance for automated containment (concept). Accessed 2026-10-29.

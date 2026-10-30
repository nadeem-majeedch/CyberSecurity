---
title: "Automation Discipline"
description: "Idempotency, dry-run, least privilege, secrets, retries, audit logging, testing and the human-in-the-loop decisions that keep security automation safe."
module_code: CYB-505
level: 5
kind: lesson
prerequisites: [CYB-505]
estimated_minutes: 90
difficulty: advanced
safety: conceptual
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [automation, python, testing, secrets, audit]
---

# Automation Discipline

## Learning objectives

1. Explain why security automation needs guard rails proportional to its blast radius.
2. Design an action that is idempotent, reversible where possible, and dry-runnable.
3. Handle secrets so they never enter code, logs or process arguments.
4. Write retries that do not amplify an outage, and audit logs that survive the incident.
5. Test automation the way you test detection logic: fixtures, negative cases, pass/fail.

## 1. Blast radius is the design constraint

Every automation can be described by three numbers: how many targets it can touch, how fast, and how hard the action is
to undo.

| Action | Targets | Reversible | Verdict |
| --- | --- | --- | --- |
| Enrich an alert | 1 | N/A | Low risk — automate freely |
| Open a ticket | 1 | Yes | Low risk |
| Disable an account | 1 | Yes, with care | Medium — require confirmation or a policy |
| Isolate a host | 1 | Yes | Medium — same |
| Block an IP range | many | Yes | High — human approval |
| Delete data / revoke all sessions | many | No | Highest — two-person rule |

The mistake is not automating high-impact actions; it is automating them with the same guard rails as enrichment.

## 2. Dry-run by default

A script that changes state should do nothing until told twice:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="perform actions; default is a dry run")
parser.add_argument("--confirm", help="must equal the target count when --apply is used")
args = parser.parse_args()

if args.apply and args.confirm != str(len(targets)):
    raise SystemExit("refusing to apply: pass --confirm <number-of-targets> to proceed")
```

The `--confirm <count>` pattern makes the operator state the scale of the action. It has caught more incidents than any
amount of documentation, because it forces a second look at "12 targets" when you expected one.

## 3. Idempotency

Running the automation twice must not double the effect. Techniques:

- **Check before acting**: is the account already disabled? Is the rule already present?
- **Key actions by a stable identity**, not by timestamped names.
- **Make the state observable**: after the action, verify it and record the verified state.

```python
def ensure_blocked(ip, table):
    if ip in table:
        return "already-present"
    table.add(ip)
    return "added"
```

A re-run that reports `already-present` is a success, not an error.

## 4. Allowlist, denylist, and the thing you must never touch

Automation should refuse to act on targets outside an explicit scope:

```python
ALLOWED_NETWORKS = [ipaddress.ip_network("192.0.2.0/24")]
PROTECTED = {"192.0.2.1", "192.0.2.10"}   # gateway and DNS — never isolate

def is_actionable(ip):
    addr = ipaddress.ip_address(ip)
    return any(addr in net for net in ALLOWED_NETWORKS) and str(addr) not in PROTECTED
```

Two checks, not one: in-scope **and** not protected. The gateway is in scope and must still never be blocked; a
containment script that isolates the domain controller is an availability incident with a security justification.

## 5. Secrets

| Never | Instead |
| --- | --- |
| Hardcode a token | Load from environment or a secret manager |
| Pass a token as a CLI argument | Read from a file descriptor or env — arguments are visible in `ps` |
| Log the request headers | Log a redacted form and the credential's identifier |
| Store a token in the repo, even "temporarily" | Rotate immediately if it was ever committed |
| Reuse one token across environments | Separate credentials, separate scope |

```python
import os

def get_token():
    token = os.environ.get("LAB_API_TOKEN")
    if not token:
        raise SystemExit("LAB_API_TOKEN is not set; refusing to run without authentication")
    return token

def redact(value):
    return value[:4] + "…" + value[-2:] if len(value) > 8 else "…"
```

**Fail closed.** A missing credential must stop the script, not silently disable authentication. The most dangerous
automation bug is the one that "helpfully" continues unauthenticated.

## 6. Logging and audit trails

Two different logs, both required:

- **Operational log** for the operator: what the script did, to what, and what happened. Structured (JSON lines), with
  timestamps, target, action, result and a correlation ID.
- **Audit log** for the organisation: append-only, with who ran it, from where, with which credential, and the full
  target list. This is what you produce when someone asks "who blocked that range at 03:14?".

```python
import json, logging, sys, uuid

run_id = str(uuid.uuid4())
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='{"ts":"%(asctime)s","level":"%(levelname)s","run":"%s","msg":%(message)s}' % run_id)

def audit(entry):
    entry.update(run_id=run_id, actor=os.environ.get("USER", "unknown"))
    with open("audit.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
```

Never log the secret, the full request body, or personal data you do not need. Retention is a decision: audit logs are
evidence, so treat them like evidence (CYB-406).

## 7. Failure handling

| Failure | Wrong response | Right response |
| --- | --- | --- |
| API timeout | Retry immediately, forever | Bounded retries with backoff and jitter, then fail loudly |
| 401 | Retry with the same token | Stop; authentication failure is not transient |
| 403 | Treat as success | Stop; you are not authorised — a policy problem |
| 429 | Hammer harder | Honour `Retry-After`, back off |
| Partial success | Report "done" | Report per-target results; never hide partial failure |
| Malformed input line | Crash the whole run | Skip, count, report the count, continue |

```python
import time, random

def with_retry(fn, attempts=4, base=1.0):
    for i in range(attempts):
        try:
            return fn()
        except TransientError:
            if i == attempts - 1:
                raise
            time.sleep(base * (2 ** i) + random.uniform(0, 0.3))
```

Exit codes matter in automation: `0` success, non-zero failure, and never `0` after a partial failure. A pipeline that
cannot tell success from failure is worse than a manual process.

## 8. Testing

The tests that catch real problems are boring:

1. **Happy path** — one well-formed input produces the expected output.
2. **Malformed input** — a truncated line does not crash the parser; it is counted and skipped.
3. **Empty input** — zero records is handled, not a division by zero.
4. **Boundary** — the allowlist edge (first and last address) behaves as specified.
5. **Refusal** — a protected target causes a refusal, with a non-zero exit.
6. **Idempotency** — running twice produces one effect.
7. **Secret absence** — with the token unset, the script exits non-zero and does not attempt a call.
8. **Redaction** — the audit log contains no token.

```python
def test_refuses_protected_target():
    result = run_script(["--apply", "--confirm", "1", "--target", "192.0.2.1"])
    assert result.returncode != 0
    assert "protected" in result.stderr.lower()
```

## 9. Detection logic is code too

Sigma rules, KQL queries and Wazuh rules all deserve the same treatment: a positive fixture that must fire, a negative
fixture that must not, and a version in source control. Testing a rule against the alert that prompted it is not
testing; testing it against a month of benign data is.

## 10. Human in the loop

Automate the decision only when all three hold:

1. The signal is reliable (measured false-positive rate, not a feeling).
2. The action is reversible or low impact.
3. The action is logged and attributable.

Otherwise automate the *preparation* — enrich, correlate, draft the ticket — and leave the click to a person. That
split captures most of the time saving with almost none of the risk.

## Common mistakes and troubleshooting

| Mistake | Symptom | Fix |
| --- | --- | --- |
| No dry-run | First test is in production | `--apply` gate |
| Token in argv | Visible in `ps`, shell history | Env var or file |
| Unbounded retries | Outage amplified | Bounded attempts, backoff |
| Swallowed exceptions | "0 failures" with 12 failures | Per-target results, non-zero exit |
| Timestamped rule names | Duplicate rules on re-run | Stable identifiers |
| Logging the payload | Secret in the log | Redact before logging |

## Summary

Safe automation is mostly refusals: refuse to run without a credential, refuse to act out of scope, refuse to proceed
without confirmation of scale, refuse to report success when part of it failed. The parsing and API calls are the easy
part; the guard rails are the engineering.

## Review questions

1. Why is `--confirm <count>` more effective than a `--yes` flag?
2. What is the difference between an operational log and an audit log, and why do you need both?
3. Which HTTP status codes should never be retried, and why?
4. Give a test that catches a script acting on a protected host.
5. Why is a partial failure reported as success a worse bug than a crash?
6. When should an automated action stay human-approved?

## Knowledge check

1. An API returns 403. Your script retries four times. What is wrong?
2. Your allowlist is `192.0.2.0/24` and the gateway is `192.0.2.1`. What second check is missing?
3. Your script logs `response.request.headers`. What have you just leaked?
4. A re-run reports "already-present" for all targets. Is that a failure?

<details>
<summary>Answers</summary>

1. 403 is an authorisation decision, not a transient fault; retrying cannot succeed and may trigger alerting.
2. A protected-target check — in-scope is not the same as safe to act on.
3. The bearer token, in plaintext, in the logs.
4. No. It is idempotency working, assuming the verification confirms the desired state.

</details>

## Next lesson

[LAB-505-01 · Parse and Normalise Logs](lab-01-log-parsing.md) — build the ingestion layer that everything else depends
on.

---
title: "LAB-404-03 · Correlation, Tuning and a Detection Report"
description: "Correlate SSH, account and web events into one sequence, break it with clock skew and ordering, tune a false positive, and write the report."
module_code: CYB-404
level: 4
kind: lab
prerequisites: [CYB-404]
estimated_minutes: 210
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-404-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [correlation, wazuh, tuning, false-positives, detection-report, attck]
---

# LAB-404-03 · Correlation, Tuning and a Detection Report

## Scenario and background

A single failed login is noise. Six failures are a burst. A burst followed by a success, followed by a new local
account, is an incident — and no individual rule in your SIEM says so.

This lab builds that composite view across three log sources, then attacks it: out-of-order events, a different source
address, and ten minutes of clock skew. Each failure should teach you something specific about correlation rather
than producing a vague "it didn't fire".

You finish with the artefact a detection engineer is actually judged on: a report that says what the rule catches,
what it misses, and how you know.

## Learning objectives

1. Write a Sigma correlation rule of type `temporal_ordered`, with grouping.
2. Implement the equivalent sequence in Wazuh using composite rules and a shared grouping field.
3. Generate multi-source synthetic evidence whose timestamps you control.
4. Demonstrate three correlation failure modes: wrong order, wrong entity, clock skew.
5. Tune a false positive by narrowing the entity, and state what coverage the tuning costs.
6. Write a detection report whose coverage claim is supported by tests.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Wazuh | 4.14.9 | LAB-404-01 deployment, LAB-404-02 rule |
| lab-ubuntu agent | 4.14.9 | Monitored |
| sigma-cli | current | Validation and conversion |
| Python | 3.10+ | Synthetic event generator |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab-siem` and `lab-ubuntu`.
    **Targets you must not use:** any other host. All "attack" events are synthetic lines written to monitored files.

    **No real authentication attempts**, no account creation on a real system, and no web requests to anything outside
    the lab. The synthetic line for `useradd` must be a log line, not an actual account.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

An external actor with a credential list gains SSH access, creates a local persistence account, and interacts with a
web application from the same address. The detection question is whether the sequence is visible when the three
sources are correlated, and whether that correlation survives normal operational imperfections.

## Prerequisites

- LAB-404-02 complete: burst rule `100420` firing, base SID recorded, field map verified.
- A second monitored file for web logs: `/var/log/lab404/web-test.log`, added to `ossec.conf` the same way as the auth
  file. Confirm with `wazuh-logtest` that its lines decode (the `web` decoder or a generic syslog fallback is fine —
  record which).

## Procedure

### 1. Generate controlled multi-source evidence

`gen_events.py` on `lab-ubuntu` — keeps timestamps explicit so you can shift them deliberately:

```python
#!/usr/bin/env python3
"""Generate synthetic lab events with controlled timestamps. Lab use only."""
import argparse, datetime as dt, pathlib

AUTH = pathlib.Path("/var/log/lab404/auth-test.log")
WEB  = pathlib.Path("/var/log/lab404/web-test.log")

def auth_line(ts, pid, msg):
    return f"{ts.strftime('%b %e %H:%M:%S')} lab-ubuntu sshd[{pid}]: {msg}"

def build(src, failures):
    """Return (kind, builder) pairs in logical attack order; builders take a timestamp."""
    items = []
    for i in range(failures):
        items.append(("auth", lambda ts, i=i: auth_line(
            ts, 5000 + i,
            f"Failed password for invalid user labtest from {src} port {51000+i} ssh2")))
    items.append(("auth", lambda ts: auth_line(
        ts, 5100, f"Accepted password for labtest from {src} port 52000 ssh2")))
    items.append(("auth", lambda ts: (
        f"{ts.strftime('%b %e %H:%M:%S')} lab-ubuntu useradd[5200]: new user: name=svcbackup, "
        "UID=1002, GID=1002, home=/home/svcbackup, shell=/bin/bash")))
    items.append(("web", lambda ts: (
        f'{src} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
        '"POST /admin/users HTTP/1.1" 201 512 "-" "curl/8.5.0"')))
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="192.0.2.55")
    ap.add_argument("--skew-minutes", type=int, default=0)
    ap.add_argument("--order", choices=["normal", "reversed"], default="normal")
    ap.add_argument("--failures", type=int, default=6)
    a = ap.parse_args()

    items = build(a.src, a.failures)
    if a.order == "reversed":
        items.reverse()          # web -> account -> success -> failures, timestamps follow the new order

    start = dt.datetime.now() + dt.timedelta(minutes=a.skew_minutes)
    for idx, (kind, make) in enumerate(items):
        ts = start + dt.timedelta(seconds=5 * idx)
        text = make(ts)
        with (AUTH if kind == "auth" else WEB).open("a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"{ts.isoformat()} {kind} {text}")

if __name__ == "__main__":
    main()
```

The generator assigns timestamps **after** deciding the order, so `--order reversed` produces a success that genuinely
precedes the failure burst — in file order and in its own timestamp. A test where only one of those is reversed proves
nothing, and that mistake is common enough to be worth stating.

Run the baseline sequence:

```bash
sudo python3 gen_events.py | tee ~/lab404-sequence.txt
sleep 30
```

**Expected:** six failure alerts (base rule), one alert for the custom burst rule `100420`, a success event, a
`useradd` event, and a web POST event. Confirm each in the dashboard before writing correlation rules — correlate only
what you can already see.

### 2. Write the Sigma correlation rule

`detections/rules/linux/correlation_ssh_takeover.yml`:

```yaml
title: SSH Takeover Followed by Local Account Creation
id: e2a4c9d1-7b38-4f52-9c60-8d1e5a3b7f02
status: experimental
description: A successful SSH login from a source that just produced an authentication failure burst, followed by a new local account.
correlation:
  type: temporal_ordered
  rules:
    - ssh_auth_failure_burst
    - ssh_auth_success
    - local_account_created
  group-by:
    - src_ip
  timespan: 15m
level: critical
tags:
  - attack.credential_access
  - attack.t1110
  - attack.persistence
  - attack.t1136.001
falsepositives:
  - Authorized onboarding script run over SSH after a user mistyped their password
  - Configuration management that creates service accounts during a deployment window
```

```bash
sigma check detections/rules/linux/correlation_ssh_takeover.yml
```

**Expected:** validation passes. Note that two of the referenced rules are not yet written — correlation rules
reference rule **titles or IDs** in the same repository, so add `ssh_auth_success` and `local_account_created` as
single-event Sigma rules. A correlation rule that references missing rules is a broken chain, and `sigma check` may not
tell you.

### 3. Implement the sequence in Wazuh

Native correlation uses the parent rule that already fired. On `lab-siem`, add to `local_rules.xml`:

```xml
<group name="lab404,sshd,">
  <!-- Success following a burst: the event must match a success SID,
       and the burst rule must have fired within the timeframe -->
  <rule id="100421" level="12">
    <if_sid>5715</if_sid>
    <if_matched_sid>100420</if_matched_sid>
    <same_source_ip />
    <description>LAB404: SSH success following an authentication failure burst</description>
    <mitre>
      <id>T1110</id>
    </mitre>
  </rule>

  <!-- New local account shortly after the sequence -->
  <rule id="100422" level="12">
    <if_sid>5902</if_sid>
    <if_matched_sid>100421</if_matched_sid>
    <same_source_ip />
    <description>LAB404: local account created after SSH takeover sequence</description>
    <mitre>
      <id>T1136.001</id>
    </mitre>
  </rule>
</group>
```

Two substitutions are mandatory: replace `5715` and `5902` with the SIDs **your** success and account-creation events
matched (find them with `wazuh-logtest`), and confirm that the parent events carry a `srcip` field. `useradd` lines
often do not, in which case `same_source_ip` cannot match and the chain must use a different grouping field — such as
the agent name plus a short window. **Discovering that and documenting the workaround is part of the lab.**

Validate before generating anything:

```bash
docker compose exec wazuh.manager /var/ossec/bin/wazuh-analysisd -t
docker compose exec wazuh.manager /var/ossec/bin/wazuh-logtest
docker compose restart wazuh.manager
```

**Expected:** configuration test passes, and `wazuh-logtest` shows the parent rule matching. The composite rule fires
only through real event flow, not necessarily in a single logtest paste — that is expected.

### 4. Positive test of the chain

```bash
sudo python3 gen_events.py --src 192.0.2.55 | tee ~/chain-positive.txt
sleep 45
```

**Expected:** `100420` then `100421` then (if the grouping field resolved) `100422`, with increasing timestamps and
the same source. Save the three alert JSONs to `detections/tests/chain/`.

If `100422` does not fire, do not weaken the rule. Record which condition failed — `if_sid`, `if_matched_sid`, or
`same_source_ip` — using the parent alert's fields. That determination is the deliverable.

### 5. Break it three ways

**5a. Wrong order.** Generate the sequence backwards — web request, account creation, success, then the failures:

```bash
sudo python3 gen_events.py --src 192.0.2.56 --order reversed | tee ~/chain-reversed.txt
sleep 45
```

**Expected:** the burst rule may fire when the failures arrive (six failures still occurred), but the ordered sequence
does not: no `100421`, because the success preceded the burst. Record why this matters — a `temporal` (unordered)
rule would have produced a false positive here.

**5b. Different entity.** Modify the generator's web step or run two sources so the failures come from `.57` and the
success from `.58`. The simplest controlled version: run the failure loop with `--src 192.0.2.57`, then append a
success line manually from `192.0.2.58`.

**Expected:** no sequence alert, because grouping is by source. This is the grouping working correctly — not a bug —
and it is also why address-spoofing or NAT can hide a real chain.

**5c. Clock skew.** Run with `--skew-minutes -10` and note that the events are written with timestamps ten minutes in
the past. Then answer:

1. Does Wazuh use the log line's timestamp or the ingest time for `timeframe`?
2. With a 15-minute window and a 10-minute skew, why does the chain still (or no longer) match?
3. What is the operational fix — and is it a rule change or an infrastructure change?

**Expected conclusion:** clock discipline is an infrastructure control. Widening the window to compensate for skew
increases false positives and should be a documented, temporary compromise, not the fix.

### 6. Tune a false positive

The nightly authorized scanner at `192.0.2.77` fails authentication six times at 02:00, every night. It is legitimate.

First reproduce it, then tune:

```bash
sudo python3 gen_events.py --src 192.0.2.77 --failures 6 | tee ~/scanner-fp.txt
```

Then narrow the entity rather than the technique, by excluding that source from **the burst rule only**:

```xml
<rule id="100420" level="10" frequency="6" timeframe="120">
  <if_matched_sid>5710</if_matched_sid>
  <same_source_ip />
  <srcip negate="yes">192.0.2.77</srcip>
  <description>LAB404: SSH authentication failure burst from a single source</description>
</rule>
```

**Expected after restart:** `.77` no longer produces `100420`; `.55` still does. The individual failure events for
`.77` remain visible in the index, which is the point.

Then state the cost, explicitly: because the sequence rule depends on `100420`, suppressing the burst for `.77` also
removes the takeover sequence for that address. Options are (a) accept and monitor the scanner's own logs, (b) add a
lower-severity rule for scanner-window anomalies, or (c) replace suppression with a time-scoped condition. Pick one
and defend it in the report.

### 7. Write the detection report

`detections/report.md`:

| Section | Content |
| --- | --- |
| Detection | ID, title, version, owner, date |
| Hypothesis | Behaviour, observable, negative case |
| Data sources | Files/agents, decoders, fields used, retention |
| Logic | Sigma rule plus the Wazuh implementation, and where they differ |
| ATT&CK | Techniques, sub-techniques, why each mapping is justified |
| Tests | The four tests plus the three correlation failures, with outcomes |
| False positives | Observed, expected, and the tuning decisions with their cost |
| Coverage claim | "Tested coverage" statement — what fired and what stayed quiet |
| Limitations | Grouping field issues, clock dependency, sources not covered |
| Maintenance | Review cadence, owner, what would trigger a re-test |

The coverage claim must be one sentence a sceptical reviewer would accept. "We detect SSH brute force" is not one.
"Rule 100420 fired on six failures from one source within 120 s and stayed silent for two failures followed by a
success; the sequence rule fired only when the order and source matched, and did not fire under 10-minute clock skew"
is.

## Evidence to collect

- `gen_events.py` and the four generated log transcripts.
- Sigma correlation rule plus the two referenced single-event rules.
- Wazuh rule excerpts, with the substituted SIDs marked.
- Alert JSONs for the positive chain and the reversed-order test.
- `detections/tests/skew/notes.md` — the three answers in 5c.
- `detections/tuning/decision.md` — the FP reproduced, the tuning applied, the cost accepted.
- `detections/report.md`.

## Verification

- [ ] Every synthetic event is visible before correlation is attempted.
- [ ] The Sigma correlation rule is `temporal_ordered` and `sigma check` passes.
- [ ] All referenced rules exist; the chain is not broken.
- [ ] Wazuh SIDs are the ones observed, and the grouping field was verified on the parent events.
- [ ] Positive chain produces increasing timestamps and the same source.
- [ ] Reversed order produces the burst but not the sequence.
- [ ] Different source produces no sequence.
- [ ] Clock skew behaviour is explained in terms of event time versus ingest time.
- [ ] Tuning is entity-scoped, and the base events remain visible.
- [ ] The report states the coverage cost of the tuning.
- [ ] The coverage claim cites specific test outcomes, not a technique name.

## Teardown and reset

Remove rules `100420`–`100422` from `local_rules.xml`, restart the manager, and clear the synthetic files:

```bash
sudo truncate -s 0 /var/log/lab404/auth-test.log /var/log/lab404/web-test.log
```

Keep `detections/` outside the VM. Revert snapshots if you want a clean SIEM for CYB-407.

## Reflection

1. The account-creation event may lack a source address, breaking `same_source_ip`. What grouping field would you use
   instead, and what does that choice assume?
2. `temporal_ordered` versus `temporal`: give one real behaviour where the ordered variant prevents a false positive.
3. You suppressed `.77` from the burst rule. Describe an attack that now succeeds from `.77` undetected, and the
   cheapest control that would still catch it.
4. Your coverage claim mentions clock skew. Why does a reviewer care more about that sentence than about the ATT&CK
   tags?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correlation | Single-event rules only | Sequence fires on the happy path | Ordering, grouping and skew all tested and explained |
| Implementation | Rules copied with unknown SIDs | SIDs substituted and validated | Grouping-field limitation discovered and documented |
| Tuning | Suppresses the host or technique | Entity-scoped exclusion | Cost of the exclusion stated, with a compensating option |
| Report | Lists rules | Tests and results recorded | Coverage claim is test-backed, limitations explicit, maintenance owned |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Sequence never fires | Parent SID wrong, or parent lacks the grouping field | `wazuh-logtest` the parent; inspect `data.srcip` in the alert |
| Fires on a single event | Composite rule missing `frequency`/`if_matched_sid` semantics | Check the rule type; a two-event chain needs the matched SID |
| `same_source_ip` unmatched for `useradd` | Event has no source address | Group by agent and window instead; document it |
| Reversed-order test still alerts | Using `temporal` semantics, not `temporal_ordered` | Verify the correlation type and the parent rule order |
| All tests fail after edit | XML not reloaded, or manager rejected config | `wazuh-analysisd -t`, then restart and read `ossec.log` |
| Skew test behaves inconsistently | Mixing event time and ingest time in your reasoning | Query the stored `timestamp` and compare with the line's own time |
| Tuning removed all alerts | `negate` applied to the wrong rule or field | Re-read the rule; verify `.55` still fires before concluding |

## References

1. SigmaHQ — correlation rule specification (`temporal`, `temporal_ordered`, grouping, timespan).
   <https://sigmahq.io/docs/basics/correlations.html> Accessed 2026-10-29.
2. Wazuh — composite rules and `if_matched_sid`, `same_source_ip`, `frequency`, `timeframe`.
   <https://documentation.wazuh.com/current/user-manual/ruleset/ruleset-xml-syntax/rules.html> Accessed 2026-10-29.
3. Wazuh — `wazuh-logtest` and `wazuh-analysisd -t`. Accessed 2026-10-29.
4. MITRE ATT&CK — T1110, T1136.001. <https://attack.mitre.org/> Accessed 2026-10-29.
5. NIST SP 800-92 — log management, time synchronisation and retention. Accessed 2026-10-29.

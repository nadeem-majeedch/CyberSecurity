---
title: "From Hypothesis to Tested Rule"
description: "Detection as a falsifiable statement, Sigma as a portable spec, correlation, and the four tests every rule needs."
module_code: CYB-404
level: 4
kind: lesson
prerequisites: [CYB-402]
estimated_minutes: 240
difficulty: advanced
safety: none
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [detection-engineering, sigma, siem, correlation, normalisation, false-positives]
---

# From Hypothesis to Tested Rule

## What this lesson covers

1. Why a detection is a hypothesis, and what makes one falsifiable.
2. Starting from data sources rather than from a list of techniques.
3. Rule anatomy: selection, condition, context, and metadata that a reviewer can use.
4. Field normalisation, and why correlation fails when it is wrong.
5. Threshold, sequence and absence correlation — and their failure modes.
6. The four tests: positive, negative, no-data, regression.
7. Tuning false positives without allowlisting the behaviour.
8. Detection as code, coverage claims, and the metrics that keep rules honest.

## Why it matters

Alert volume is not a measure of detection quality. A rule that fires on every `sudo` invocation and a rule that
catches Kerberoasting with no false positives can both produce "alerts"; only one changes an outcome.

The difference is testing. An untested rule is a guess with a schedule attached, and it fails in two directions: it
misses the behaviour it claims to cover, or it buries the analyst in noise until they stop reading. Both failures are
invisible on a dashboard and both are preventable with about twenty minutes of work per rule.

## 1. Detection as a falsifiable hypothesis

Write the sentence before the query:

> **If** an attacker tries many passwords against SSH and then succeeds, **then** `sshd` logs will show more than
> five `Failed password` lines from one source followed by an `Accepted password` from the same source within ten
> minutes, **and** a legitimate user who mistypes a password twice will not meet that threshold.

That sentence contains four things a query alone does not:

- **Behaviour**, not tooling. "Many failures then success" survives a change of SSH server.
- **Data source** with a field-level observable, so you can check the source exists and is ingested.
- **A threshold and window**, which are claims you must test, not constants handed down.
- **A negative case**, stated up front, which becomes your false-positive test.

If you cannot state the negative case, you do not yet understand the behaviour well enough to detect it.

## 2. Start from data, not from techniques

Before writing a rule, answer: does the data exist, is it parsed, is it retained long enough, and what does it cost?

| Source | Answers questions about | Blind spots |
| --- | --- | --- |
| Linux `auth.log` / `journald` | SSH logins, `sudo`, `su`, PAM failures, service starts | Anything not logged by those services; log tampering |
| `auditd` | File access, `execve` with arguments, syscall-level context | Rules must exist; high volume; can be disabled |
| Windows Security log | Logons, privilege use, account changes, 4688 process creation | Requires audit policy; command line needs its own setting |
| Sysmon | Process creation with hashes, network connections, DNS, file writes | Configuration-dependent; kernel-level tampering |
| Web server logs | Requests, status codes, user agents, timing | Bodies; what happened after the request |
| Firewall / proxy | Flows, denies, DNS names, bytes | Content; encryption hides payload |
| IDS (Suricata) | Network signatures and protocol anomalies | Encrypted traffic; signatures age |

Two disciplines follow. **Inventory before you write**: if the source is not ingested, the rule is documentation.
**Record the gap**: "no DNS logging on the internal resolver" is a finding worth writing down, not a reason to write a
weaker rule and call it coverage.

## 3. Rule anatomy

Every rule has the same four parts, whether it is Sigma, Wazuh XML or a KQL query:

| Part | Question it answers | Common mistake |
| --- | --- | --- |
| **Selection** | Which events match? | Using a field that is not populated by the parser |
| **Condition** | How many, in what order, over what window? | Thresholds copied from a blog without testing |
| **Context** | Which log source, host, user, asset tier? | No logsource, so the rule matches unrelated data |
| **Metadata** | Who owns it, what it detects, what it false-positives on? | A title and nothing else |

### A Sigma rule for one event

```yaml
title: SSH Authentication Failure Burst
id: 3b7e5c1a-9d24-4f6b-8a10-6c2f4e9d7b31
status: experimental
description: More than five SSH authentication failures from one source in two minutes.
references:
  - https://attack.mitre.org/techniques/T1110/
author: CYB-404 lab
date: 2026/10/29
logsource:
  product: linux
  service: sshd
detection:
  selection:
    message|contains: 'Failed password'
  timeframe: 2m
  condition: selection | count(src_ip) by src_ip > 5
fields:
  - src_ip
  - user
falsepositives:
  - A user with a stale saved password retrying in a loop
  - Vulnerability scanners with default credential lists (authorized)
level: high
tags:
  - attack.credential_access
  - attack.t1110
```

The `falsepositives` block is not decoration. It is the test plan for the negative case, and it is the first thing an
experienced reviewer reads.

### A Sigma correlation rule for a sequence

Sigma handles sequences with correlation rules rather than by gluing selections together in one `condition`:

```yaml
title: SSH Success After Failure Burst
id: c41d8a72-5f3b-4e08-b6d9-1a7c0e2f9b64
status: experimental
correlation:
  type: temporal_ordered
  rules:
    - ssh_auth_failure_burst
    - ssh_auth_success
  group-by:
    - src_ip
  timespan: 10m
level: critical
tags:
  - attack.credential_access
  - attack.t1110
```

`temporal_ordered` requires the order; `temporal` does not. Choose deliberately: a success before a failure burst is
not the same behaviour, and using `temporal` there will produce nonsense.

**Backend reality:** correlation support varies. pySigma converts to Splunk, Elastic, OpenSearch, Sentinel and others;
there is **no official Wazuh backend**, so Wazuh correlation is implemented natively with composite rules (next
section). Community Sigma-to-Wazuh converters exist and their output needs review like any other generated code.

## 4. Normalisation decides whether correlation works

The same SSH failure arrives as:

- `sshd[3122]: Failed password for invalid user admin from 192.0.2.55 port 51234 ssh2` in a raw log line;
- `data.srcip` in Wazuh after decoding;
- `source.ip` in ECS-flavoured pipelines;
- `src_ip` in the field list of the Sigma rule you wrote.

Correlation joins on field names **and** values. If one source calls it `srcip` and another `src_ip`, your sequence
rule silently matches nothing — and "no alerts" looks exactly like "no attacks".

Practical discipline:

1. Pick the canonical field names for your platform and write them down.
2. After ingesting a new source, run one query that prints the parsed fields for a known event. If the field is
   missing, fix the decoder before writing rules.
3. Add a **field presence check** to your test plan: a rule that depends on `src_ip` must fail loudly when `src_ip`
   is absent, not quietly match nothing.

## 5. Correlation and its failure modes

| Type | Shape | Example | Characteristic failure |
| --- | --- | --- | --- |
| **Threshold** | N events in T | 6 SSH failures in 2 min | Threshold too low (noise) or too high (misses slow attacks) |
| **Sequence** | A then B in T | Failure burst then success | Clock skew, late logs, missing intermediate event |
| **Absence** | No event in T | No backup completion by 03:00 | Fires when the *logging* breaks, not the process |
| **Aggregation** | Distinct values | One source, many usernames (spraying) | Cardinality blowups and memory cost |

Four failure modes worth memorising:

- **Clock skew.** A sequence rule comparing a 10-second window across two hosts with 30 seconds of drift will miss.
  Fix the clocks (NTP) before blaming the rule.
- **Duplicate events.** Two collectors forwarding the same log make a threshold of 5 fire on 2.5 real failures.
- **Late arrival.** Batch-forwarded logs arrive after the window closed. Widen the window or use event time, not
  ingest time.
- **The absence trap.** "No event" is indistinguishable from "no data". Any absence rule needs a heartbeat check on
  the source, or it will page you about a broken pipeline and call it a security incident.

## 6. The four tests

Every rule gets four, and you record the result of each:

1. **Positive** — generate the behaviour and confirm the alert. Use synthetic logs or safe activity, never live
   malware.
2. **Negative** — generate realistic benign activity that resembles the behaviour and confirm **no** alert. "User
   mistypes password twice, then succeeds" is the negative case for the brute-force rule.
3. **No-data** — stop or redirect the source and confirm the rule does not report success. A rule that passes because
   its data vanished is worse than no rule.
4. **Regression** — after any tuning change, re-run the positive and negative tests. Tuning is a code change.

### Generating test events safely

For log-source rules, write **synthetic lines** to a monitored file and label them:

```bash
# On lab-ubuntu, in a file the agent monitors as /var/log/lab404/auth-test.log
for i in $(seq 1 6); do
  echo "$(date -Is) lab-ubuntu sshd[4000]: Failed password for invalid user labtest from 192.0.2.55 port 5$i ssh2" \
    >> /var/log/lab404/auth-test.log
done
echo "$(date -Is) lab-ubuntu sshd[4001]: Accepted password for labtest from 192.0.2.55 port 6000 ssh2" \
  >> /var/log/lab404/auth-test.log
```

This produces deterministic, harmless events with the exact shape the rule expects. Record the file path in the
report; a reviewer must be able to tell synthetic from real.

**Validate the rule itself before the pipeline.** Wazuh ships an interactive tester:

```bash
sudo /var/ossec/bin/wazuh-logtest
# paste a log line, inspect the decoder, the matched rule IDs, and the level
```

If `wazuh-logtest` does not match your rule, the problem is the rule or the decoder — not the dashboard.

## 7. False positives without blind spots

Classify before tuning:

| Class | Example | Right fix |
| --- | --- | --- |
| Benign trigger | Scanner with default creds | Allowlist the scanner's **source address**, scope it to an authorized window |
| Environment quirk | A cron job that restarts SSH nightly | Suppress that specific parent process or host role |
| Parser artefact | One event logged twice | Fix the pipeline, not the rule |
| Threshold too tight | 5 failures catches fat-fingered humans | Raise to 8, or add "distinct usernames > 3" to catch spraying instead |

**The rule of tuning:** allowlist the *entity*, never the *technique*. Suppressing "all alerts from host X" because X
is noisy removes your visibility into X being compromised. Suppressing "this scanner address during its scheduled
window" does not.

After every tuning change, ask: what would an attacker do to fit inside the exception I just created?

## 8. Detection as code

Treat rules like software, because they are:

```text
detections/
├── rules/
│   ├── linux/ssh_auth_failure_burst.yml
│   └── linux/ssh_success_after_failure.yml
├── tests/
│   ├── positive/ssh_burst.log
│   └── negative/ssh_typo_then_success.log
├── mappings/field-map.md
└── README.md          # owner, review cadence, deployment steps
```

Minimum review checklist for a new rule: hypothesis stated, logsource verified as ingested, fields present in a real
parsed event, positive and negative tests recorded, `falsepositives` populated, ATT&CK mapping justified, owner named,
and a note on what the rule does **not** cover.

Deployment is the part teams skip: a rule merged into Git but not loaded into the SIEM is documentation. Record the
deployment step (and how you verified the loaded rule ID) in the pull request.

## 9. Coverage claims and metrics

"Coverage" means different things and the differences matter:

- **Technique coverage** — a rule mentions T1110. Cheap, and nearly meaningless on its own.
- **Data-source coverage** — the telemetry needed for a technique is actually ingested. Necessary, not sufficient.
- **Tested coverage** — the rule fired on the behaviour in a test and stayed quiet on the negative case. This is the
  only claim worth making in a report.

Metrics that keep rules honest:

| Metric | Why |
| --- | --- |
| Alerts per rule per week | A rule at zero for 90 days is stale or broken; investigate which |
| Triage sample true-positive rate | Sample 20 alerts, classify; precision you can actually compute |
| Mean time from event to alert | Measures the pipeline, not the analyst |
| Rules with no owner | Orphans that nobody will tune |
| Open tuning exceptions | The blind spots you have chosen, in one place |

## Common misconceptions

| Belief | Reality |
| --- | --- |
| "More rules means better detection" | More rules means more noise unless each is tested and owned. |
| "The SIEM detects; the analyst just reads" | The SIEM matches patterns. Judgement is the analyst's, and the rule only supplies evidence. |
| "Sigma converts to anything" | Official backends cover several targets; Wazuh is not one of them. |
| "A high-severity rule is more important" | Severity is a label. A medium rule with a tested negative case beats a critical rule nobody validated. |
| "No alerts means no incidents" | No alerts also means a broken decoder, an expired agent, or a full disk. |
| "Tuning is suppressing" | Good tuning narrows the entity and window. Bad tuning removes the behaviour. |

## Key terms

**hypothesis** · **observable** · **logsource** · **selection** · **condition** · **decoder** · **normalisation** ·
**canonical field** · **threshold** · **temporal** · **temporal_ordered** · **absence rule** · **clock skew** ·
**positive/negative/no-data/regression test** · **precision** · **stale rule** · **detection as code**

## Check your understanding

**1. Rewrite "detect brute force" as a hypothesis with a negative case.**

<details><summary>Answer</summary>
"If one source produces more than five SSH failures in two minutes and then a success, `sshd` logs will show it; a
user who mistypes twice and succeeds will not meet the threshold." The second clause is the negative test.
</details>

**2. A sequence rule produces nothing for a week. What are the three most likely causes?**

<details><summary>Answer</summary>
The referenced rule ID is wrong or not firing; the field used for grouping is named differently after decoding; or
the events are arriving outside the window (clock skew, late forwarding). A fourth: the rule was never loaded.
</details>

**3. Why is an absence rule dangerous without a heartbeat?**

<details><summary>Answer</summary>
Because "no backup event" and "no data from the backup host" are the same observation. Without a heartbeat you cannot
distinguish a failed process from a failed pipeline, and you will report the wrong incident.
</details>

**4. Your rule fires on 400 alerts a day, all from the vulnerability scanner. What do you change?**

<details><summary>Answer</summary>
Scope the exception to the scanner's source address during its authorized window, and verify the rule still fires
from another source. Suppressing the host or the technique would remove real coverage.
</details>

**5. What is the difference between "the rule exists" and "the behaviour is covered"?**

<details><summary>Answer</summary>
Existence is a file. Coverage requires the data source to be ingested, the fields to be parsed, and the rule to have
fired on a positive test while staying quiet on a negative one.
</details>

## Summary

- A detection is a hypothesis with a stated observable and a stated negative case.
- Start from data-source inventory, and record gaps instead of writing weaker rules.
- Selection, condition, context and metadata — the metadata is what makes a rule reviewable.
- Normalisation decides whether correlation can work; verify parsed fields on real events.
- Threshold, sequence and absence correlation each fail in characteristic ways; clocks and duplicates are usual
  suspects.
- Four tests: positive, negative, no-data, regression.
- Tune entities, not techniques.
- Coverage claims need a positive and a negative test, not a tag.

## Next

[LAB-404-01](lab-01-wazuh-deployment.md) deploys the SIEM this module assumes, with the indexer preconditions that
catch most first attempts.

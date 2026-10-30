---
title: "SOC Workflow, ATT&CK and Intelligence"
description: "The alert lifecycle, triage judgement, ATT&CK mapping and how to turn threat intelligence into an action."
module_code: CYB-401
level: 4
kind: lesson
prerequisites: [CYB-206]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-401-01, LAB-401-02, LAB-401-03]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [soc, triage, alert-lifecycle, mitre-attack, cti, ioc, metrics]
---

# SOC Workflow, ATT&CK and Intelligence

**Level 4** · 240 minutes · **Prerequisites:** CYB-206 · **Labs:**
[Triage a Queue](lab-01-alert-triage.md) · [ATT&CK Mapping](lab-02-attck-mapping.md) ·
[Intelligence Brief](lab-03-ioc-brief.md)

## Why this matters

An analyst's day is a sequence of small judgements made under incomplete information: this alert fired, is it real,
does it matter, who needs to know, and what do I write down so the next person is not starting over?

Tools do not make those judgements. A SIEM can correlate a thousand events per second and still hand you an alert
that says "suspicious activity" with no context. The skill this module builds is the one that turns that alert into
a decision you can defend — and, just as often, into a closure with a reason.

## Learning outcomes

By the end of this lesson you will be able to:

- Describe each stage of the alert lifecycle and the decision required at that stage.
- Prioritise a queue using asset criticality, technique severity, and evidence quality.
- Classify outcomes as true positive, benign true positive, or false positive, with reasoning.
- Map an observed behaviour to an ATT&CK tactic and technique, and state what the mapping does not prove.
- Assess an indicator for confidence and actionability, and choose block, hunt, or monitor.
- Select metrics that describe detection quality rather than activity volume.

## Prerequisites and setup

- Python 3.10+ and `jq` for the labs; no SIEM required in this module.
- Familiarity with the log sources named in [CYB-402](../02-endpoint-telemetry/index.md) helps, but the lesson
  defines each one it uses.

---

## Core concepts

### 1. The pipeline, and where judgement lives

```text
Telemetry → Detection → Alert → Triage → Investigation → Escalation → Response → Closure → Learning
             (rules)          (human)   (human + data)   (handover)   (IR)      (notes)   (metrics)
```

Every stage has a failure mode, and most incidents that go badly wrong failed early:

| Stage | Typical failure | Consequence |
| --- | --- | --- |
| Telemetry | A log source silently stopped | Blind spot nobody notices until an incident |
| Detection | Rule fires on a field that is not normalised | Alert storms, or nothing at all |
| Triage | Closed as "benign" without evidence | The intrusion continues |
| Investigation | Only the alerting host examined | Scope missed; attacker persists elsewhere |
| Escalation | No severity definition, so nobody agrees | Delay, or an unnecessary war room |
| Closure | Notes say "FP" with no reason | The same alert wastes time next week |

**The SOC's real product is a decision record**, not a closed ticket. A well-written closure teaches the next
analyst something; a bare "false positive" guarantees the alert is re-investigated from zero.

### 2. Alert lifecycle states

Most platforms use some variant of these. Learn the transitions, because the awkward ones are where incidents are
lost.

| State | Meaning | Must record |
| --- | --- | --- |
| New | Ingested, unowned | Arrival time |
| In progress | An analyst is working it | Owner, start time |
| Escalated | Needs incident response or another team | Reason, severity, who was told |
| Closed — true positive | Confirmed malicious, handled | Scope, actions, evidence |
| Closed — benign true positive | Activity happened, but it was legitimate | Why it was legitimate (the evidence) |
| Closed — false positive | The detection was wrong | Which field or logic was wrong |
| Closed — duplicate | Same event as an existing case | Link to the parent case |
| Suppressed | Known and accepted noise | Rule change or exception with an expiry |

**Benign true positive is the category most often collapsed into "false positive".** A developer running `curl` at
02:00 is not a detection failure; a rule that treats all `curl` as suspicious is a tuning problem. Recording the
distinction is what lets detection engineering fix the right thing.

### 3. Triage: three questions, in order

1. **Is the underlying activity real?** Evidence: the raw event, not the alert summary. A rule can mis-parse a
   field and invent an event that never happened.
2. **Is it authorised or expected?** Change records, known admin activity, baseline behaviour, asset role. This is
   where most alerts die, and where most mistakes are made — "it looks like an admin" is not evidence.
3. **Does it matter?** Asset criticality × data sensitivity × technique severity × confidence.

A useful triage order that ignores the severity label:

| Priority | Situation | Why |
| --- | --- | --- |
| 1 | Credential access or defence evasion on a critical asset | The attacker is already inside and trying to stay |
| 2 | Initial access attempts that succeeded (not just failed) | Success is rarer and far more important than volume |
| 3 | Lateral movement or new administrative behaviour | Blast radius is expanding |
| 4 | Repeated failures with no success | Noise until proven otherwise, but check the source |
| 5 | Single low-confidence anomaly on a low-value host | Queue it; do not spend an hour on it |

**Severity labels are inputs, not orders.** "Critical" from a scanner that flags every outbound connection is
worth less than "Medium" on a domain controller with a new service account.

### 4. The evidence standard for closing

Before you close anything, you should be able to write one sentence of this shape:

> *Closed as benign true positive: the 4625 burst came from `lab-win` (192.0.2.40) authenticating to the file
> server with a stale mapped drive, confirmed by the user's ticket CHG-1042 and the absence of a subsequent 4624.*

That sentence contains the event, the source, the corroboration, and the reason it is not malicious. If you cannot
write it, you are guessing, and the case stays open.

Three habits that make this fast:

- **Read the raw event.** Alert summaries drop fields; the fields are where the answer is.
- **Check the asset, not just the event.** A workstation behaving oddly at 14:00 is different from a domain
  controller behaving oddly at 03:00.
- **Look for the pair.** A failed login matters more when followed by a success from the same source; a new service
  matters more when it is followed by an outbound connection.

### 5. MITRE ATT&CK: what it is for

ATT&CK is a curated knowledge base of **adversary behaviours**, organised by tactic (the adversary's goal) and
technique (how they achieve it). Current version at the time of writing is **v20.0 (October 2026)** — check the
version page before citing technique IDs in a report, because techniques are added, renamed, and deprecated.

| Tactic (enterprise) | The adversary's goal | Example technique |
| --- | --- | --- |
| Initial Access | Get in | T1566 Phishing |
| Execution | Run code | T1059 Command and Scripting Interpreter |
| Persistence | Stay | T1053 Scheduled Task/Job |
| Privilege Escalation | Gain rights | T1068 Exploitation for Privilege Escalation |
| Defense Evasion | Avoid detection | T1562 Impair Defenses |
| Credential Access | Steal identity | T1003 OS Credential Dumping |
| Discovery | Learn the environment | T1087 Account Discovery |
| Lateral Movement | Move | T1021 Remote Services |
| Collection | Gather data | T1560 Archive Collected Data |
| Command and Control | Talk home | T1071 Application Layer Protocol |
| Exfiltration | Take data | T1041 Exfiltration Over C2 Channel |
| Impact | Damage | T1486 Data Encrypted for Impact |

**Use ATT&CK for three things and no more:**

1. **Common language.** "T1110.003 password spraying against VPN" is unambiguous across teams and vendors.
2. **Coverage analysis.** Which tactics have no detection at all? That gap list is more useful than a coverage
   percentage.
3. **Hypothesis generation.** Given a technique, what telemetry would prove it happened?

**What ATT&CK does not do:** it does not tell you whether activity is malicious, it does not score risk, and a
mapping is not evidence. Two analysts can map the same event differently and both be reasonable. Write the
reasoning next to the ID, and never let a technique ID stand in for an explanation.

### 6. Threat intelligence: three products, three audiences

| Type | Answers | Audience | Example |
| --- | --- | --- | --- |
| Strategic | What threats matter to us, and why? | Leadership, risk owners | "Ransomware targeting our sector doubled this quarter" |
| Operational | Who is likely to attack us, and how? | Detection and IR leads | Campaign report with TTPs and targeting |
| Tactical | What specific artefacts do we look for? | SOC analysts, tooling | Domains, hashes, user-agent strings |

Most "threat feeds" sold to small teams are tactical indicators with no context. They are the least durable form of
intelligence: a domain lives for days, a hash for hours, and a technique for years. That ordering is the **Pyramid
of Pain** — blocking a hash costs the adversary almost nothing; detecting a technique costs them their toolkit.

**Indicator assessment, four questions:**

1. **What is it?** Domain, IP, hash, URL, user-agent, registry key, mutex, email address.
2. **How confident are we?** Say why: first-party observation, single vendor, corroborated by two sources, or
   inferred. "High confidence" without a basis is noise.
3. **How old is it, and what is its half-life?** An IP from eighteen months ago is archaeology, not intelligence.
4. **What action does it justify?** Block (high confidence, low false-positive cost), hunt (moderate confidence,
   high value), or monitor (low confidence, or high cost of blocking).

```text
Indicator: hxxps://cdn-update[.]example[.]test/gate.php     (defanged for transport)
Type:      URL
Confidence: moderate — single vendor report, no first-party sighting
Age:       9 days
Action:    hunt in proxy and DNS logs for 30 days; do not block the parent domain (shared hosting)
```

That block is worth more than a list of five hundred indicators, because it says what to do and why.

**Sharing has rules.** TLP 2.0 (Traffic Light Protocol) marks distribution: **RED** (named recipients only),
**AMBER** (organisation, need-to-know), **AMBER+STRICT** (organisation only), **GREEN** (community), **CLEAR**
(public). Mark anything you produce, and treat a received indicator as sensitive until you know otherwise.

### 7. Metrics that describe quality

| Metric | Definition | What it tells you |
| --- | --- | --- |
| MTTD | Detection time minus event time | Whether you can see it at all |
| MTTA | Acknowledgement time | Staffing and queue health |
| MTTR | Resolution time | Process friction, not skill |
| False-positive rate | FP ÷ total alerts, per rule | Which rules to tune |
| Alert-to-incident ratio | Incidents ÷ alerts | Whether the queue is worth a human |
| Coverage by tactic | Tactics with at least one tested detection | Where the blind spots are |
| Reopen rate | Cases reopened after closure | Quality of triage |

**Vanity metrics to distrust:** total events ingested, number of rules deployed, "threats blocked" without a
definition, and any dashboard that goes up when the product is working harder rather than working better.

### 8. Writing it down

Three artefacts cover almost everything:

- **Case notes** — chronological, timestamped, evidence-linked. Written for someone who was not there.
- **Handover** — open cases, what you did, what you would do next, what you are unsure about. The last item is the
  most valuable and the most often omitted.
- **Escalation summary** — five lines: what happened, what it means, what you have done, what you need, by when.

---

## Worked example: one alert, three dispositions

A rule fires: *Outbound connection to low-reputation domain from `lab-ubuntu`*.

**Pass 1 — is the activity real?** The raw proxy log shows a DNS query and an HTTPS connection at 10:14:22 to
`cdn-update.example.test`, initiated by `python3` (PID 4412), user `analyst`. Real.

**Pass 2 — expected?** The host is the analyst workstation; `python3` is the user's own script; the change record
shows a package-manager test. Expected, but the rule is worth keeping.

**Pass 3 — does it matter?** Domain reputation is low because the domain is nine days old; the connection succeeded
once, with no preceding credential or persistence activity.

| Disposition | Would be wrong because |
| --- | --- |
| True positive, escalate | Nothing indicates compromise; escalation would waste IR time |
| False positive | The connection did happen — the detection was right |
| **Benign true positive, close** | Correct: real activity, understood, documented, no action |

Then the improvement note: *"Reputation-only rule; add an allowlist for the analyst host's package tests, or require
two signals (new domain + unsigned binary)."* That note is detection engineering's input, and it is why closures
matter.

---

## Defender's view

| Signal | Source | What it suggests |
| --- | --- | --- |
| 4625 burst from one source, then 4624 | Windows Security log | Password guessing that succeeded — treat as compromise |
| Failed logins spread across many accounts | Auth logs | Password spraying, not brute force |
| New local admin or service account | 4720/4732, `/etc/passwd` | Persistence |
| Process with an encoded command line | Sysmon 1, PowerShell 4104 | Obfuscated execution |
| Outbound beacon at regular intervals | Proxy, Zeek `conn` | Command and control |
| Large outbound transfer after archive creation | File server + proxy | Exfiltration |
| Log source stops sending | SIEM ingestion metrics | Someone impaired defences, or a broken pipeline |

---

## Common mistakes

1. **Triaging the alert text instead of the event.** Summaries lose fields; the fields decide the case.
2. **Closing as "false positive" when the activity was real.** It hides a tuning problem and misleads the next
   analyst.
3. **Treating ATT&CK as a score.** A technique ID is a label, not a severity and not proof.
4. **Blocking every indicator you receive.** Blocklists age badly and break business traffic; hunt first.
5. **Escalating without a summary.** "Suspicious activity on host" wastes the responder's first ten minutes.
6. **Measuring activity instead of outcomes.** A rising alert count may mean better detection or a worse rule.

---

## Practice

1. [LAB-401-01 · Triage a Synthetic Alert Queue](lab-01-alert-triage.md) — twelve alerts, five that matter.
2. [LAB-401-02 · Map Activity to ATT&CK](lab-02-attck-mapping.md) — ten events, with reasoning.
3. [LAB-401-03 · Write a Threat-Intelligence Brief](lab-03-ioc-brief.md) — from report to action.

**Stretch task.** Take any three alerts you closed as benign and write the rule change that would have prevented the
alert without losing the detection. If you cannot, the closure was not understood well enough.

## Knowledge check

1. Name the three triage questions and the evidence each requires.
2. What is the difference between a benign true positive and a false positive, and why does it matter?
3. Which ATT&CK tactic would a scheduled task created by a phishing payload map to, and what does the mapping not
   prove?
4. Why is a hash a weaker indicator than a technique?
5. You receive an IP with "high confidence" from a single vendor, aged fourteen months. What do you do, and why?
6. What does TLP:AMBER permit, and what does it forbid?
7. Give one metric that describes detection quality and one that is vanity.
8. What must a handover contain that a case note often omits?

## Summary

- The SOC is a decision pipeline; the decision record is the product.
- Triage asks: is it real, is it expected, does it matter — in that order.
- Benign true positive and false positive are different, and the distinction drives tuning.
- ATT&CK gives shared language and coverage gaps, not severity or proof.
- Indicators are perishable; assess confidence, age and action before blocking.
- Metrics should describe quality of detection, not volume of activity.

## References

1. NIST SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations for Cybersecurity Risk Management.
   April 2025. <https://csrc.nist.gov/pubs/sp/800/61/r3/final>
2. MITRE ATT&CK v20.0 — Tactics, techniques, and version history.
   <https://attack.mitre.org/resources/versions/> Accessed 2026-10-29.
3. FIRST — Traffic Light Protocol 2.0. <https://www.first.org/tlp/> Accessed 2026-10-29.
4. David Bianco — The Pyramid of Pain. Accessed 2026-10-29.
5. CISA — Incident and Vulnerability Response Playbooks. Accessed 2026-10-29.

---
title: "LAB-407-04 · The Incident Report and Post-Incident Review"
description: "Write the report a manager can act on, run a four-inject tabletop, and produce a blameless review with verifiable actions."
module_code: CYB-407
level: 4
kind: lab
prerequisites: [CYB-407]
estimated_minutes: 120
difficulty: advanced
safety: none
lab_ids: [LAB-407-04]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [incident-report, post-incident-review, tabletop, metrics, root-cause, actions]
---

# LAB-407-04 · The Incident Report and Post-Incident Review

## Scenario and background

The incident is contained and the service is restored. Now comes the part that determines whether the next incident is
cheaper: the report, the review, and the actions that come out of them.

You will use `INC-407-03` (the simulated ransomware) as the case, run a short tabletop with four injects, and produce
both artefacts. The report is for a mixed audience; the review is for the team.

## Learning objectives

1. Write an executive summary that states impact without jargon or speculation.
2. Produce a technical timeline and root cause that is causal rather than a single blamed action.
3. Quantify impact across confidentiality, integrity, availability, and business terms.
4. Run a time-boxed tabletop with injects and record decisions as they were made.
5. Write a blameless review with action items that have owners, dates and verification.
6. Choose metrics that inform, and state how each could mislead.

## Required tools and versions

None beyond a text editor and the artefacts from LAB-407-03.

!!! warning "Authorized scope — read before you begin"
    The tabletop is a **discussion**. Do not simulate the injects by changing systems, and do not send any
    communication to real external parties. Inject 3 involves a journalist; the correct action is to route it to the
    organisation's communications lead, not to reply.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Procedure

Three deliverables, in order: the report (Part A), the tabletop that tests the plan (Part B), and the review that
turns both into actions (Part C). Part B is discussion only; nothing is changed on any system.

## Part A — The incident report

Write `INC-407-03-report.md` with these sections. Target length: three pages, not thirteen.

### 1. Executive summary

Five sentences maximum, covering: what happened, what was affected, what you did, current status, and what you need.
No acronyms without expansion, no CVSS scores, no tool names.

**Example of the required tone** (adapt to your own findings):

> On 29 October, a file server was affected by a simulation of ransomware that renamed seven documents and left a
> note. No data left the organisation and no real encryption occurred. We isolated the host, preserved evidence,
> removed the payload, and restored the documents from a backup taken that morning; all seven verified successfully.
> The service was unavailable for 41 minutes. The main gap is that the backup was stored on the affected host, which
> we are asking to change this quarter.

### 2. Timeline

A table with the events from LAB-407-02/03, in UTC, with a `source` column. Include the declaration time, the
preservation time, isolation time, eradication time, and restore completion.

| Time (UTC) | Event | Source | Confidence |
| --- | --- | --- | --- |

### 3. Root cause

Distinguish three layers, because they produce different fixes:

| Layer | Question | Example for this case |
| --- | --- | --- |
| **Technical** | How did the payload execute? | A user-level process wrote and renamed files in a writable directory |
| **Systemic** | Why was that possible and undetected? | Writable share with no execution control, no alert on mass rename, backup on the same host |
| **Contributing** | What made it worse? | Backup reachable from the affected account; restore never tested |

**"The user clicked" is not a root cause.** It is an event that a control should have limited. Write the control gap.

### 4. Impact

| Dimension | Assessment | Evidence |
| --- | --- | --- |
| Confidentiality | No evidence of data access or transfer | No outbound flow in the evidence set; state the gap |
| Integrity | Seven documents altered, then restored | Hash comparison |
| Availability | 41 minutes (or your measured value) | Declaration to restore completion |
| Business | One file share unavailable during a working morning | Affected team, estimated hours lost |
| Regulatory / legal | Assess with counsel; no personal data in synthetic set | Refer, do not conclude |

**State what you cannot assess.** "We cannot determine whether the account was used elsewhere" is a legitimate and
important sentence.

### 5. Response narrative

Four short subsections: detection, containment, eradication, recovery — each with what was done, when, by whom, and
what was **not** done and why. The last part is what a reviewer reads most closely.

### 6. Evidence and custody

Reference the evidence register from LAB-406-01/407-03, list exhibits with hashes, and state where they are stored and
when they will be destroyed.

### 7. Open questions

At least three, each with the log or system that would answer it. "Was the account used from another host?" →
authentication logs for the account across the estate, 30-day window.

### 8. Communications log

| Time | Audience | Message summary | Channel | By |
| --- | --- | --- | --- | --- |

## Part B — Tabletop with four injects

Time-box: 45 minutes. Roles: facilitator (reads injects), incident commander, scribe, communications, technical lead.
If you are alone, play commander and scribe and note the limitation.

**Rules:** decisions are made with the information available at that moment. The facilitator does not answer
questions the scenario does not answer. The scribe records the decision, the reasoning, and what was unknown.

| # | Inject | Read at | What it tests |
| --- | --- | --- | --- |
| 1 | "The off-host backup copy is 36 hours old. Your RPO is 24 hours." | T+10 min | Whether RPO breach is escalated and who decides to accept it |
| 2 | "A second host shows the same marker string in a shared directory." | T+20 min | Scope expansion, re-declaration to SEV1, containment widening |
| 3 | "A journalist has emailed asking whether you paid a ransom." | T+30 min | Communications discipline, no speculation, legal routing |
| 4 | "A user reports they paid the address in the note." | T+38 min | Legal/law-enforcement engagement, payment handling, support for the user |

`tabletop.md`:

| Time | Inject | Decision | Reasoning at the time | What we did not know | Owner |
| --- | --- | --- | --- | --- | --- |

**Marked question:** for inject 1, who has authority to accept an RPO breach? If nobody knows, that is the finding —
and it is worth more than the exercise itself.

## Part C — Post-incident review

`pir.md`:

### 1. What happened

One paragraph, no blame, facts only, referencing the report rather than repeating it.

### 2. Decisions and alternatives

| Decision | Alternative considered | Why we chose this | Would we choose it again? |
| --- | --- | --- | --- |
| Isolated rather than powered off | Shutdown | Preserve volatile state; avoid destructive trigger | Yes |
| Restored rather than rebuilt | Rebuild from image | User-level payload, no persistence, package verification clean | Yes, with 72 h monitoring |
| Kept SSH open during isolation | Full network cut | Needed for evidence collection | Yes, with a documented exception |

### 3. What worked / what did not

Three of each, specific. "Detection worked" is not specific; "the mass-rename pattern was visible in the file listing
within four minutes" is.

### 4. Action items

| # | Action | Addresses | Owner | Due | Verified by |
| --- | --- | --- | --- | --- | --- |
| 1 | Move backups off-host and restrict access from production | RPO credibility | Platform lead | 2026-11-30 | Restore test from the off-host copy |
| 2 | Alert on bulk rename in shared directories | Detection gap | SOC engineer | 2026-11-15 | Rule fires in a lab replay; negative test on a legitimate archive job |
| 3 | Add RPO breach to the SEV2 playbook with a named decision owner | Tabletop inject 1 | IR lead | 2026-11-10 | Next tabletop confirms the name is known |
| 4 | Test restore quarterly and record the result | Recovery verification | Platform lead | 2026-12-01 | First test record filed |

Every action needs all five columns. An action without a verification method will be marked done without being done.

### 5. Metrics

| Metric | This incident | Definition used | How it could mislead |
| --- | --- | --- | --- |
| Time to declare | | Alert to declaration | Fast declaration of a trivial event inflates the number |
| Time to contain | | Declaration to isolation | "Contained" may mean one host, not the campaign |
| Time to recover | | Declaration to verified restore | Excludes the 72 h monitoring period |
| Recurrence | | Same root cause within 90 days | Undercounted if the root cause was misattributed |

Compute your own values from the timestamps; leave a cell blank rather than inventing a number.

### 6. What we would do differently

Two or three sentences, each naming a concrete alternative and the condition under which it would be right. This is
the section that makes the review worth reading.

## Evidence to collect

- `INC-407-03-report.md` with all eight sections.
- `tabletop.md` with the decision log and the authority finding.
- `pir.md` with decisions, worked/did-not-work, actions and metrics.
- The evidence register and hashes referenced by the report.

## Verification

- [ ] Executive summary is five sentences or fewer and contains no unexplained jargon.
- [ ] Every timeline entry has a UTC time and a source.
- [ ] Root cause covers technical, systemic and contributing layers; no individual is blamed.
- [ ] Impact covers all five dimensions and states what could not be assessed.
- [ ] At least three open questions, each with the data source that would answer it.
- [ ] All four injects have a recorded decision and what was unknown at the time.
- [ ] The RPO authority question is answered or recorded as a finding.
- [ ] Communications inject routed to a communications lead, with no speculation about payment.
- [ ] Every action item has owner, due date and verification method.
- [ ] Metrics include the definition and a way each could mislead.
- [ ] No statement presents inference as established fact.

## Teardown and reset

Nothing to tear down. Retain the three documents; together they are the module's portfolio artefact and the model for
the Level 4 assessment report.

## Reflection

1. Your executive summary had five sentences. Which detail was hardest to leave out, and why was it safe to omit?
2. Inject 1 exposed an authority gap. Why is "nobody knew who could accept an RPO breach" a more valuable finding than
   "the backup was old"?
3. Which action item would you expect to be marked done without real verification, and how does the "verified by"
   column prevent that?
4. A reviewer asks why the host was restored rather than rebuilt. Which evidence from LAB-407-03 supports your answer,
   and what would have changed it?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Report | Narrative only | Structured sections | Executive summary usable by a non-technical reader; limits stated |
| Root cause | Blames the user | Technical cause | Technical, systemic and contributing layers with control gaps |
| Tabletop | Discussion only | Decisions recorded | Decisions with reasoning and unknowns; authority gap surfaced |
| Review | Lists problems | Actions with owners | Actions verifiable, metrics defined with their failure modes |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Summary exceeds five sentences | Trying to include the timeline | Move detail to section 2; keep impact and ask |
| Impact cannot be quantified | No timestamps for availability | Use declaration and restore times; state the definition |
| Tabletop stalls | Facilitator answering questions | Answer only from the scenario; record the unknown |
| Actions are vague | No verification imagined | Write the test that would prove completion, then the action |
| Metrics disagree with the timeline | Different start points | Define the start and end of each metric explicitly |

## References

1. NIST SP 800-61 Rev. 3 — post-incident activity and improvement. Accessed 2026-10-29.
2. NIST SP 800-34 Rev. 1 — RTO/RPO and contingency planning. Accessed 2026-10-29.
3. CISA — Incident and Vulnerability Response Playbooks. Accessed 2026-10-29.
4. ISO/IEC 27035 — incident management and lessons learned. Accessed 2026-10-29.

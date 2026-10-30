---
title: "Phases, Decisions and Evidence"
description: "The incident response lifecycle, roles, containment trade-offs, recovery objectives, communications and the review that makes the next incident cheaper."
module_code: CYB-407
level: 4
kind: lesson
prerequisites: [CYB-406]
estimated_minutes: 180
difficulty: advanced
safety: none
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [nist-800-61, containment, eradication, recovery, rto, rpo, communications, post-incident-review]
---

# Phases, Decisions and Evidence

## What this lesson covers

1. What makes an event an incident, and who declares it.
2. The NIST SP 800-61 lifecycle, and what each phase actually produces.
3. Roles: commander, scribe, technical lead, communications.
4. Evidence during response: preserve first, contain second — and the exceptions.
5. Containment options and their costs.
6. Eradication, recovery, and the rebuild-versus-clean decision.
7. Recovery objectives, backups, and verifying a restore.
8. Communications and legal boundaries, without pretending to give legal advice.
9. Metrics that inform, and metrics that flatter.
10. The post-incident review and the tabletop.

## Why it matters

An incident is a period when decisions have costs you cannot undo: shutting down a host destroys memory; disabling an
account destroys the attacker's access but also your visibility into what they were doing; restoring from backup may
restore the vulnerability.

Response discipline is what keeps those decisions deliberate. The alternative is a team of capable people making
irreversible choices quickly, in parallel, without a record — which is how organisations both lose evidence and miss
the second foothold.

## 1. Event, alert, incident

- **Event** — something observable happened. Most events are normal.
- **Alert** — a rule or person flagged an event for attention.
- **Incident** — an event (or set) that has confirmed or suspected negative impact and requires coordinated response.

**Declaration is a decision, not a diagnosis.** Organisations define severity criteria in advance so that declaring is
fast and not political. A workable scheme:

| Severity | Criteria | Response |
| --- | --- | --- |
| SEV1 | Confirmed compromise of critical systems, data loss, or safety impact | Incident commander, all-hands, executive notification |
| SEV2 | Confirmed compromise of a non-critical system, or credible attempted compromise of a critical one | IC plus technical lead, business-hours escalation |
| SEV3 | Suspicious activity requiring investigation, no confirmed impact | On-call analyst, ticket |
| SEV4 | Policy violation or low-impact event | Normal queue |

**Under-declaring is the common failure.** Teams wait for certainty, spend six hours investigating alone, and discover
on day two that three other hosts were involved. Declaring early and downgrading later is cheaper than the reverse —
provided the criteria say so.

## 2. The lifecycle

NIST SP 800-61 Rev. 3 (April 2025) frames incident response within cybersecurity risk management and the CSF 2.0
functions, and emphasises governance and continuous improvement alongside the operational phases. The operational core
remains:

| Phase | Question | Artefacts produced |
| --- | --- | --- |
| **Preparation** | Can we respond at all? | Playbooks, contacts, tooling, backups, training, authority to act |
| **Detection and analysis** | What happened, and how far did it go? | Triage notes, scope statement, evidence register, timeline |
| **Containment, eradication, recovery** | How do we stop it, remove it, and return safely? | Containment record, eradication steps, restore verification |
| **Post-incident activity** | What do we change? | Report, review, action items with owners and dates |

**Preparation is where most incidents are won or lost**, and it is invisible until something happens. A playbook that
says who can isolate a production host, and how, is worth more than a faster scanner.

## 3. Roles

One person can do all of these in a small incident, but not simultaneously and not while also investigating.

| Role | Responsibility | Failure if absent |
| --- | --- | --- |
| **Incident commander** | Decisions, priorities, authority | Parallel, contradictory actions |
| **Scribe** | Timestamped record of decisions and evidence | A report reconstructed from memory |
| **Technical lead** | Investigation and remediation execution | Commander drowns in detail |
| **Communications** | Internal and external messaging | Speculation reaches customers |
| **Legal / privacy** | Notification obligations | Regulatory breach on top of the incident |

The scribe is the role most often skipped and the one whose absence shows up in the post-incident review, when nobody
can explain why a host was shut down at 03:40.

## 4. Evidence during response

**Default order: preserve, then contain.** The exceptions are narrow and must be recorded:

- The compromise is actively spreading and containment cannot wait.
- There is a safety or life-safety risk.
- The system is being wiped by the attacker as you watch.

Even then, capture what you can first: a memory image if it takes minutes, a copy of logs, a screenshot of a process
list. "We had to isolate it immediately" is a defensible sentence; it is much stronger with a timestamp and a note
about what was captured before isolation.

**Practical sequence for a suspected endpoint:**

1. Record the time, the host, and who is acting.
2. Capture volatile state (network connections, process list) — the tools are in CYB-406.
3. Image memory if within your capability and time budget.
4. Isolate at the network layer (segmentation policy from CYB-405) rather than powering off.
5. Preserve logs centrally — the SIEM copy is unaffected by host cleanup.
6. Only then begin eradication.

**Shutting down is a last resort**: it clears memory, may trigger destructive payloads, and can make a ransomware
host's encryption keys unrecoverable. Network isolation usually achieves containment with less loss.

## 5. Containment options and their costs

| Option | Stops | Costs |
| --- | --- | --- |
| Network isolation (ACL/VLAN/quarantine) | Lateral movement, C2 | Attacker may detect and accelerate; remote admin lost |
| Account disable / password reset | Credential-based access | Loses session visibility; helpdesk load; possible lockout of a service account |
| Block IOC at proxy/DNS/firewall | Specific infrastructure | Attacker rotates; may break legitimate services on shared infrastructure |
| Application shutdown | Exploitation of that service | Business impact; may be the only revenue path |
| Host shutdown | Everything on the host | Memory lost; possible destructive trigger; recovery slower |
| Full segment isolation | Spread within segment | Broad outage; political cost |

**Choose the narrowest option that stops the spread**, then widen if evidence shows you were too narrow. Write down
what you chose, when, and what you expected it to achieve — the review will ask.

## 6. Eradication and recovery

Eradication is removing the attacker's presence: malware, persistence, added accounts, scheduled tasks, modified
binaries, and **credentials**. Rotating credentials is the step most often missed; a rebuilt host that still accepts a
stolen password is not recovered.

Recovery is returning to service with confidence:

- **Clean vs rebuild.** Cleaning is faster and often incomplete; rebuilding from a known-good image is slower and more
  trustworthy. For anything with kernel-level or firmware persistence, rebuild.
- **Verify before return.** The vulnerability that allowed entry must be closed, not just the symptom removed.
- **Heightened monitoring.** After recovery, watch the host and its neighbours closely for a defined period. Re-entry
  attempts are common and are valuable intelligence.

## 7. Recovery objectives and backups

- **RTO (Recovery Time Objective)** — how long the service may be down.
- **RPO (Recovery Point Objective)** — how much data loss is acceptable, expressed as time.

These are business decisions. Your job is to know them before an incident, because they decide whether you restore in
an hour or rebuild over a weekend.

**Backups fail in predictable ways:** never tested, stored with the same credentials as production, reachable from
production, or encrypted by the same ransomware. A backup is a control only after a restore has been verified.

**Verify a restore** by restoring to an isolated environment, checking integrity and application function, and
recording the date. An untested backup is a hope with a retention policy.

## 8. Communications

- **One channel, one spokesperson.** Parallel updates produce contradictions that outlive the incident.
- **Facts, impact, next update time.** "We have isolated two servers; customer data access is being assessed; next
  update at 14:00" is a usable message.
- **No speculation about attribution.** "We believe this was an external actor" is a claim you may have to retract.
- **Legal and regulatory notification is jurisdiction-specific** and time-bound. This course does not give legal
  advice; know who to ask, and ask early. In many organisations that is legal counsel, not the security team.
- **Preserve communications.** They are part of the record and may be discoverable.

## 9. Metrics

| Metric | Useful because | Misleading when |
| --- | --- | --- |
| Time to detect | Measures monitoring coverage | Detection was reported by a customer |
| Time to acknowledge | Measures on-call responsiveness | Alerts auto-close without review |
| Time to contain | Measures decision speed | Containment was "disable the account" and the attacker kept a session |
| Time to recover | Measures recovery capability | Recovery was "restore and hope", unverified |
| Recurrence rate | Measures whether eradication worked | Root cause was never identified |

Report medians and distributions, not averages, and always pair a metric with its definition. A "15-minute MTTD" that
excludes weekends is a different metric from one that does not.

## 10. Post-incident review and tabletop

A **post-incident review** is blameless in tone and specific in content:

1. What happened, in order, with timestamps.
2. What we decided, and what we knew at the time.
3. What worked, and what did not.
4. Action items: owner, date, and how completion will be verified.
5. What we would do differently, with the alternative named.

"Communication was poor" is not an action item. "Add a 30-minute update cadence to the SEV2 playbook, owned by the
on-call lead, verified by the next tabletop" is.

A **tabletop** is a discussion-based exercise: a scenario, a facilitator, and decisions made out loud. It finds the
gaps — who has authority to isolate a domain controller, where the contact list lives, whether the backup team knows
the RTO — before they are needed at 03:00.

## Common misconceptions

| Belief | Reality |
| --- | --- |
| "Contain first, investigate later" | Containment destroys evidence. Preserve what is volatile, then contain, and record the order. |
| "Shut it down, it's safer" | Shutdown loses memory and may trigger destructive behaviour. Isolate instead. |
| "We removed the malware, so we're done" | Persistence and stolen credentials usually outlive the file. |
| "The backup is fine, it runs nightly" | Untested backups fail at restore time. Verify. |
| "Notifying anyone will cause panic" | Delayed notification is often the bigger regulatory and reputational failure. |
| "The review is about finding who made a mistake" | Blameless reviews surface process gaps; blame surfaces silence. |

## Key terms

**event** · **alert** · **incident** · **severity** · **incident commander** · **scribe** · **containment** ·
**eradication** · **recovery** · **RTO** · **RPO** · **persistence** · **credential rotation** · **tabletop** ·
**post-incident review** · **blameless**

## Check your understanding

**1. When is shutdown the right containment choice?**

<details><summary>Answer</summary>
Rarely: when the host is actively destroying data, when isolation is impossible, or when a destructive payload is
imminent and the loss of memory is the lesser cost. It is a documented decision, not a default.
</details>

**2. Why rotate credentials after rebuilding a host?**

<details><summary>Answer</summary>
Because the attacker had valid credentials, and those credentials are independent of the host. A clean host with a
stolen password is re-compromised immediately.
</details>

**3. Your RTO is four hours and the rebuild takes six. What now?**

<details><summary>Answer</summary>
Escalate the conflict before committing: restore a degraded service if possible, agree a temporary risk acceptance
with the business, and record the decision. The gap between RTO and capability is a finding for the review.
</details>

**4. An analyst wants to delete a suspicious file to "stop it running". What do you say?**

<details><summary>Answer</summary>
Preserve a copy and its metadata first (hash, path, timestamps), and check for persistence and other hosts. Deleting
the file removes the evidence and rarely removes the capability.
</details>

**5. What makes a post-incident action item useful?**

<details><summary>Answer</summary>
A named owner, a date, a verifiable completion condition, and a link to the decision it addresses.
</details>

## Summary

- Incident declaration follows pre-agreed criteria; declaring early and downgrading is cheaper than the reverse.
- NIST's lifecycle: prepare, detect and analyse, contain/eradicate/recover, review.
- Roles matter; the scribe is the one people skip and later need.
- Preserve volatile evidence before containment, except for narrow, recorded exceptions.
- Contain narrowly, then widen on evidence; record the decision and its cost.
- Eradicate persistence and rotate credentials; rebuild when trust is in doubt.
- RTO/RPO are business decisions; verify restores.
- One spokesperson, facts only, next update time; legal notification is jurisdiction-specific.
- Blameless, specific reviews with owned actions.

## Next

[LAB-407-01](lab-01-phishing-triage.md) starts with the most common real incident: a reported email, and the question
of who else received it.

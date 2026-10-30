---
title: "Engagements, Evidence and Impact"
description: "Scope, rules of engagement, validation, restrained exploitation, evidence standards, risk rating and the report a client can retest against."
module_code: CYB-501
level: 5
kind: lesson
prerequisites: [CYB-501]
estimated_minutes: 180
difficulty: advanced
safety: none
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [scoping, rules-of-engagement, validation, evidence, cvss, reporting, retest]
---

# Engagements, Evidence and Impact

## What this covers

1. The four documents that authorize an assessment, and what each must contain.
2. The assessment lifecycle, and where restraint belongs in it.
3. Validation: turning a scanner claim into a confirmed finding.
4. Proving impact without exceeding the brief.
5. Evidence standards that survive review.
6. Rating by severity and by business context.
7. The report structure, and retesting as a separate deliverable.
8. Legal and professional responsibilities that are not optional.

## Why it matters

A finding you cannot reproduce is an opinion. An action you were not authorized to take is an incident. Both are
common, and both are avoidable with documents written before testing starts and evidence captured while it happens.

The technical skills get you a shell. The discipline in this lesson is what makes the shell a defensible finding
rather than a liability.

## 1. The four documents

| Document | Purpose | Must contain |
| --- | --- | --- |
| **Authorization letter** | Proves permission exists | Signed by someone with authority, names the organization and the range, states the dates |
| **Scope** | Defines what may be touched | In-scope hosts/URLs/accounts, exclusions, environments (prod/staging), data handling |
| **Rules of engagement (RoE)** | Defines how you may touch it | Permitted techniques, prohibited techniques, testing windows, stop conditions, contacts, escalation path |
| **Test plan** | Defines what you will do | Phases, methods, tooling, deliverables, schedule, assumptions |

**A scope without exclusions is not a scope.** It is an invitation to argue later about what "the website" meant.
Write the out-of-scope list explicitly: third-party services, shared infrastructure, production databases, staff
mailboxes, anything owned by another legal entity.

**Prohibited techniques** normally include denial of service, social engineering without separate written approval,
physical access, data exfiltration beyond a proof, and persistence. If a technique is not listed as permitted, it is
not permitted.

**Stop conditions** are the part teams forget: what makes you stop and call someone? Examples: evidence of an active
intrusion by a third party, access to data that looks like real customer records, a service becoming unavailable,
or reaching a system outside the agreed scope.

## 2. The lifecycle

| Phase | Question | Restraint |
| --- | --- | --- |
| Reconnaissance | What exists? | Passive first; active scanning only in-window |
| Enumeration | What is exposed, and how? | Rate-limit; avoid destructive verbs |
| Validation | Is the finding real? | Reproduce manually; never rate a scanner output |
| Exploitation | Can impact be demonstrated? | Minimum necessary; read a marker, do not dump the database |
| Post-exploitation | What else does this access reach? | Bounded by scope; no persistence, no lateral movement into out-of-scope hosts |
| Cleanup | What did I leave? | Remove uploads, accounts, files; verify |
| Reporting | What should change? | Reproducible, prioritised, with owners implied |
| Retest | Did the fix work? | Same method, same evidence, new date |

**The proof-of-impact ladder** is the practical expression of restraint:

1. Demonstrate the flaw with a harmless marker (`id`, `whoami`, a file you created).
2. Read one record that proves access to sensitive data, if the scope allows it.
3. Stop. Do not download the table, do not modify data, do not establish persistence.

If a client asks for "full exploitation", that is a separate, explicitly authorized objective with its own data
handling agreement.

## 3. Validation

A scanner reports a possible issue. Validation answers three questions:

- **Reproducible?** Does the same request produce the same result, twice, from a clean session?
- **Real impact?** Is the data or action genuinely sensitive, or is it a public value the scanner misunderstood?
- **In scope?** Is the affected component part of the agreed target?

Record one of three states: **confirmed** (reproduced, impact demonstrated), **potential** (behaviour observed, impact
not provable within scope), **false positive** (does not reproduce, or the claim is wrong). A report that contains
only "confirmed" findings is either a very good target or an undisciplined tester.

**Validation is where most false criticals die.** A reflected parameter that returns your own input in a header is
not cross-site scripting. A version banner is not a vulnerability. A directory listing of public assets is not
information disclosure worth a critical rating.

## 4. Evidence standards

Every confirmed finding needs evidence that a second person can use to reproduce it without asking you a question:

| Evidence | Requirement |
| --- | --- |
| Request/response | Full method, path, headers that matter, body; redact session tokens |
| Command | Exact command line, tool version, working directory |
| Timestamp | UTC, with the timezone stated |
| Identity | Which test account, with which role |
| Output | The marker output that proves impact, not a screenshot of a shell prompt |
| Hash | For any file you upload or extract |
| Custody | Where the evidence is stored and who has access |

**Screenshots are supporting evidence, not primary evidence.** They are easy to fabricate, hard to search, and lose
the headers that matter. Keep the raw text and add a screenshot where the visual state is the point.

**Redact secrets.** A report containing a live credential is a new incident. Replace tokens with `[REDACTED]` and
note that the original is held in the evidence store.

## 5. Rating

Rate twice, then reconcile:

- **Technical severity** — CVSS v4.0 base score, with the vector string so the reader can see your reasoning.
- **Business risk** — likelihood × impact in this environment, considering exposure, data sensitivity, compensating
  controls and detectability.

| Finding | CVSS | Context | Final rating | Why |
| --- | --- | --- | --- | --- |
| SQL injection, authenticated, internet-facing | 8.8 | Customer data, no WAF, logged | Critical | Direct path to regulated data |
| Same flaw, internal-only tool with synthetic data | 8.8 | Low-value data, network-restricted | Medium | Real flaw, limited consequence |
| Reflected input in a header, no execution | 4.3 (if it were XSS) | Not exploitable as claimed | Informational | Validation failed; report as a hardening note |

**Do not inflate to get attention, and do not deflate to look clever.** The rating is a prediction about consequence;
the report should make the reasoning visible so the client can disagree with the inputs rather than the conclusion.

## 6. The report

Structure that clients can act on:

1. **Executive summary** — one page: what was tested, what was found in aggregate, the three things to fix first, and
   the limitations.
2. **Scope and methodology** — what was in and out, what techniques were used, dates.
3. **Findings** — ordered by risk. Each with: title, rating and vector, affected component, description, reproduction
   steps, evidence, impact, remediation, references.
4. **Positive observations** — controls that worked. This is not decoration; it tells the client what to preserve.
5. **Retest status** — for each finding: not retested, fixed, partially fixed, unresolved.
6. **Appendix** — tooling, raw evidence index, glossary.

**Remediation advice must be specific.** "Sanitise input" is not remediation. "Use parameterised queries in
`/api/search`; the current string concatenation is at line 42 of `search.py`" is.

## 7. Retesting

A retest is a new, smaller engagement with the same discipline:

- Same method, so the comparison is valid.
- Same accounts and roles, so access differences do not masquerade as fixes.
- Evidence of the **fix**, not just absence of the symptom: the vulnerable request now fails, and the legitimate
  function still works.
- A partial fix is reported as partial. "Cannot reproduce" is not the same as "fixed" if the component changed.

## 8. Legal and professional responsibilities

- **Stay inside authorization**, including time windows. Permission at 10:00 does not cover 23:00.
- **Minimise data.** If you encounter real personal data, stop, record what you saw, and follow the data-handling
  agreement.
- **Report immediately** if you find evidence of an actual intrusion — that is an incident, not a finding.
- **Do not disclose** beyond the agreed recipients. Reports are sensitive documents.
- **Do not use** findings, credentials or access for anything outside the engagement.
- **Say what you did not test.** Coverage limits are part of the deliverable.

## Common misconceptions

| Belief | Reality |
| --- | --- |
| "The scanner found it, so it's a finding" | Unvalidated scanner output is noise; reproduce it or drop it. |
| "We had permission, so anything goes" | Permission is specific to hosts, techniques and time. |
| "Critical findings get fixed faster" | Inflated ratings get discounted; accurate context gets action. |
| "A shell proves everything" | A shell proves access. Impact needs a demonstrated consequence. |
| "Retest means running the scanner again" | It means reproducing the original method against the fix. |
| "No findings means secure" | It means nothing was found within scope, in the time available. |

## Key terms

**authorization letter** · **scope** · **rules of engagement** · **stop condition** · **validation** ·
**proof of impact** · **evidence chain** · **CVSS vector** · **business risk** · **retest** · **partial fix** ·
**coverage limitation**

## Check your understanding

**1. A scanner reports SQL injection on a URL that returns a generic error page. What is your next step?**

<details><summary>Answer</summary>
Validate manually: reproduce with a benign payload, check whether the response differs in a way that indicates query
influence, and confirm the parameter reaches a database. If it does not reproduce, record it as a false positive with
the evidence for that conclusion.
</details>

**2. You gain domain admin in a lab. What do you do before anything else?**

<details><summary>Answer</summary>
Stop and record: timestamp, account, command, and the marker output. Then check the scope — does it permit further
access? Demonstrate the minimum needed to prove impact, remove anything you created, and report.
</details>

**3. Why is "we tested the production site" not enough for a scope document?**

<details><summary>Answer</summary>
It does not define hosts, paths, accounts, exclusions, techniques or windows. Two people reading it would test
different things.
</details>

**4. A finding is fixed by disabling the feature. Is it fixed?**

<details><summary>Answer</summary>
It may be mitigated, not fixed. Record the control, its owner, and the condition under which the feature returns; a
retest should confirm both that the flaw is gone and that the business function still works as intended.
</details>

**5. What belongs in a report's limitations section?**

<details><summary>Answer</summary>
What was out of scope, what was not tested, time constraints, credential limitations, and the fact that the
assessment is a point-in-time sample rather than proof of absence.
</details>

## Summary

- Four documents authorize the work: letter, scope, RoE, plan. Exclusions and stop conditions are mandatory.
- Validate before rating; three states, each with evidence.
- Prove impact with the minimum necessary action, then stop.
- Evidence must be reproducible, timestamped in UTC, redacted and custody-tracked.
- Rate technically and contextually, and show the reasoning.
- Report findings, positives, remediation and retest status. Retest with the same method.
- Stay in scope, minimise data, report real intrusions immediately.

## Next

[LAB-501-01](lab-01-engagement-package.md) writes the documents before any tool is run — which is the correct order.

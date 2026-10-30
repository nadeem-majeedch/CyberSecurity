---
title: "LAB-501-01 · Scope, Rules of Engagement and Test Plan"
description: "Write the four documents that authorize an assessment of a lab range, with exclusions, stop conditions and evidence handling specific enough to enforce."
module_code: CYB-501
level: 5
kind: lab
prerequisites: [CYB-501]
estimated_minutes: 180
difficulty: advanced
safety: local-only
lab_ids: [LAB-501-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [scoping, roe, authorization, test-plan, evidence-handling]
---

# LAB-501-01 · Scope, Rules of Engagement and Test Plan

## Scenario and background

*Northwind Labs* (fictional) has asked for an assessment of its lab web range before a demo. You are the tester. No
tool runs until the paperwork exists, because the paperwork is what makes the testing lawful and bounded.

You will write an authorization letter, a scope, rules of engagement and a test plan for a range that exists in your
own lab. The documents must be specific enough that a second tester could pick them up and know exactly what is
permitted — and what would make them stop.

## Learning objectives

1. Define scope at host, path and account level, with explicit exclusions.
2. Write rules of engagement covering permitted and prohibited techniques, windows, and stop conditions.
3. Produce a test plan with phases, methods, tooling and deliverables.
4. Specify evidence handling, data minimisation and retention.
5. Rewrite ambiguous scope statements into enforceable ones.

## Required tools and versions

None beyond a text editor. This lab produces documents, not traffic.

!!! warning "Authorized scope — read before you begin"
    **This lab authorizes nothing by itself.** It is an exercise in writing authorization for a fictional client and
    your own lab range. Do not send these documents to anyone, and do not treat them as permission to test a system
    you do not own.

    The only addresses that appear are documentation ranges and your own host-only lab.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

Not an attacker: the failure mode is **scope drift**. An ambiguous boundary, an unlisted technique, or a missing stop
condition turns a lawful assessment into an incident. The control is a document set that a reviewer can check line by
line.

## The range

| Asset | Address | Role | In scope? |
| --- | --- | --- | --- |
| `lab-analyst` | 192.0.2.10 | Tester workstation | Only as a source of traffic |
| `lab-web` (DVWA) | 192.0.2.50:4280 | Vulnerable web application | Yes — web application only |
| `lab-api` | 192.0.2.51:8080 | Local API with synthetic data | Yes — API endpoints under `/api/v1` |
| `lab-siem` | 192.0.2.30 | Monitoring | **No** — excluded; do not test |
| Host hypervisor | host-only gateway | Lab platform | **No** |

Business context: a two-day window, no production data, the client wants the demo to proceed on the third day.

## Procedure

### 1. The authorization letter

`01-authorization.md`, addressed from the fictional client to you:

- Names the organization, the signatory and their role.
- Names the range by host and address, and the environment (lab).
- States the testing window with timezone.
- References the scope and RoE as attachments, and states that the signatory has authority to grant access.
- States what the client has agreed to: monitoring, data handling, and the emergency contact.
- Includes a signature block and a date.

**Why a letter and not a ticket:** the letter identifies who had authority. In a dispute, "someone in IT said it was
fine" is not authorization.

### 2. The scope

`02-scope.md`:

| Section | Content |
| --- | --- |
| In scope | Exact host, port, path prefixes, accounts provided |
| Out of scope | Everything else, listed explicitly, including the SIEM, the hypervisor and any third-party service |
| Data | Synthetic only; no real personal data expected; what to do if that changes |
| Accounts | Test accounts and their roles |
| Environments | Lab only; production explicitly excluded |
| Access method | Host-only network from `lab-analyst` |
| Assumptions | Application is running, credentials valid, no WAF interference |

Then rewrite these three ambiguous statements into enforceable ones:

1. "The web application is in scope."
2. "Testing will not disrupt operations."
3. "Any critical findings should be reported immediately."

**Expected quality:** statement 1 becomes host + port + path prefix + method boundary; statement 2 becomes a named
prohibited technique list and a rate limit; statement 3 becomes a named contact, a definition of "critical", and a
time limit for notification.

### 3. Rules of engagement

`03-roe.md`:

| Item | Your entry |
| --- | --- |
| Permitted techniques | Manual web testing, authenticated API testing, controlled injection validation, non-destructive enumeration |
| Prohibited techniques | Denial of service, stress or load testing, social engineering, physical access, persistence, data exfiltration beyond a one-record proof, testing the SIEM |
| Testing window | Two consecutive days, 09:00–17:00 UTC, with a defined freeze before the demo |
| Rate limits | Maximum 5 requests/second per endpoint; no automated fuzzing without a stated ceiling |
| Stop conditions | Evidence of a third-party intrusion; access to real personal data; service unavailability; reaching an out-of-scope host |
| Escalation | Named contact, channel, response expectation |
| Cleanup | Remove uploaded files, test accounts, test records; verify |
| Evidence | Encrypted store, access list, retention date |
| Insurance/legal | Named responsible party and governing agreement |

**The stop-condition test:** for each condition, write the exact action and the person to call. "Stop and assess" is
not an action.

### 4. The test plan

`04-plan.md`:

| Phase | Activities | Outputs | Time |
| --- | --- | --- | --- |
| Reconnaissance | Headers, technology fingerprint, public paths | Asset notes | 1 h |
| Enumeration | Endpoint inventory, authentication behaviour, input points | Endpoint map | 2 h |
| Validation | Reproduce candidate issues, record false positives | Validation log | 3 h |
| Controlled exploitation | Minimum proof of impact per confirmed issue | Evidence pack | 2 h |
| Reporting | Findings, ratings, remediation | Report draft | 2 h |
| Cleanup and handover | Remove artefacts, verify, list coverage limits | Cleanup record | 1 h |

Add a tooling table with versions (browser, proxy, `curl`, `nmap`, `nikto` only if used) and a "not used and why"
line for anything a reader might expect.

### 5. The communication plan

`05-comms.md`:

- Who is told what, when: start, daily summary, critical finding, stop event, completion.
- The emergency contact and the out-of-hours path.
- What must never be sent over chat or email (credentials, personal data, full exploit payloads).

### 6. Self-review against enforceability

Answer in `06-review.md`:

1. Could a second tester determine whether a given host is in scope without asking you? Quote the line.
2. Is there any technique you would use that is not explicitly permitted?
3. Does every stop condition name an action and a person?
4. If the client asked for "one more endpoint", what is the process for changing scope mid-engagement?
5. What will you do with the evidence at the end, and who decides?

**Expected:** at least one gap found and fixed. A self-review with no findings is a review that did not happen.

## Evidence to collect

- `01-authorization.md`, `02-scope.md`, `03-roe.md`, `04-plan.md`, `05-comms.md`, `06-review.md`.
- The three rewritten scope statements, before and after.
- The stop-condition table with actions and contacts.

## Verification

- [ ] Authorization names a signatory, a range and a window.
- [ ] Scope lists in-scope hosts by address and port, and exclusions explicitly.
- [ ] Every prohibited technique is named, not implied.
- [ ] Testing window includes timezone and a freeze before the demo.
- [ ] Every stop condition has an action and a contact.
- [ ] Evidence handling covers storage, access, redaction and retention.
- [ ] The plan names tools and versions and states what is not used.
- [ ] Self-review found and fixed at least one gap.

## Teardown and reset

Nothing was changed. Keep the documents; LAB-501-02 and LAB-501-03 reference them, and the set is the portfolio
artefact for this module.

## Reflection

1. Which exclusion would be hardest to defend if the client later said "we assumed you'd check it"?
2. Why is a rate limit part of the rules of engagement rather than a technical detail?
3. Your stop conditions include "access to real personal data". What exactly would you do in the first five minutes?
4. If the client's signatory turns out not to have authority, what is the status of the work already done?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Scope | Host named loosely | Hosts and exclusions listed | Host, port, path, account and method boundaries, with a change process |
| RoE | Techniques listed | Permitted and prohibited stated | Rate limits, windows, stop conditions with actions and contacts |
| Plan | Phase names | Phases with outputs | Phases, tooling versions, time, and explicit non-use |
| Review | Not done | Questions answered | Gaps found and fixed, with the reasoning |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Scope reads like marketing copy | Writing for the client rather than the tester | Write for the person who must decide whether a host is in scope |
| Everything is prohibited | Fear of consequences | Permit what you need, bound it with rate limits and windows |
| Stop conditions vague | No named contact decided | Invent the role (lab manager) and make the action explicit |
| Plan has no time budget | Copied from a template | Allocate hours; a plan without time is a wish |

## References

1. PTES — pre-engagement interactions and scoping. <http://www.pentest-standard.org/> Accessed 2026-10-29.
2. NIST SP 800-115 — security testing and assessment planning. Accessed 2026-10-29.
3. CREST — penetration testing code of conduct. Accessed 2026-10-29.
4. OWASP WSTG v4.2 — testing scope and reporting. Accessed 2026-10-29.

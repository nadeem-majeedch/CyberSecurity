---
title: "The CIA Triad, Design Principles and Risk"
description: "Confidentiality, integrity and availability; Saltzer and Schroeder's principles; qualitative risk assessment and treatment."
module_code: CYB-102
level: 1
kind: lesson
prerequisites: [CYB-101]
estimated_minutes: 120
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [foundations, risk, principles]
---

# The CIA Triad, Design Principles and Risk

## Learning objectives

By the end of this lesson you can:

1. Define confidentiality, integrity, and availability, and give a concrete failure for each.
2. Explain why the three properties conflict, using a real trade-off.
3. Apply at least six security design principles to critique a simple system.
4. Define threat, vulnerability, exposure, likelihood, and impact precisely.
5. Rate a risk qualitatively and choose one of four treatments, recording residual risk.

## Prerequisites

[CYB-101](../01-introduction-to-cybersecurity/index.md). Bring a system you use daily and would be
willing to criticise.

---

## 1. The three properties

| Property | Plain meaning | Fails when… | Example failure |
| --- | --- | --- | --- |
| **Confidentiality** | Only intended people can read it | Data is disclosed | A misconfigured storage bucket exposes student records |
| **Integrity** | It is accurate and has not been altered | Data is changed, silently or otherwise | An attacker edits a bank transfer amount in transit |
| **Availability** | It works when needed | Access is lost | Ransomware encrypts a file server; or a bad update bricks a service |

A useful test: for any incident, ask *which of the three was harmed, and which was harmed worst?* Most
real incidents harm more than one.

### They conflict, and that is the job

- Encrypt everything → confidentiality improves, availability suffers when a key is lost.
- Log everything → detection improves, confidentiality suffers because logs hold sensitive data.
- Allow everything → availability improves, confidentiality and integrity collapse.

There is no free option. Skilled practitioners state the trade-off explicitly rather than pretending it
does not exist. Two related properties are often added:

- **Authenticity** — you can verify who sent something.
- **Non-repudiation** — the sender cannot credibly deny it.

Both are usually implemented with cryptography, which you meet in CYB-113.

## 2. Design principles

These come from Saltzer and Schroeder's 1975 paper and remain the best short checklist in the field.
Learn them as questions you ask about a design.

| Principle | The question | Example failure |
| --- | --- | --- |
| **Least privilege** | Does each user or process have only the access it needs? | A web app connects to the database as `root` |
| **Defence in depth** | If one control fails, is another there? | Only a password, with no MFA and no rate limiting |
| **Fail-safe defaults** | On error, does it deny or allow? | An access check throws an exception and the request is allowed |
| **Complete mediation** | Is every access checked, every time? | Authorization checked in the UI but not the API |
| **Separation of duties** | Can one person complete a sensitive action alone? | The same admin approves and executes payments |
| **Economy of mechanism** | Is the design as simple as it can be? | Custom authentication instead of a maintained library |
| **Open design** | Does security depend on secrecy of the design? | "Nobody knows our URL scheme" as the only control |
| **Psychological acceptability** | Will people actually use it correctly? | A password policy so strict that users write passwords on monitors |

**Least privilege** and **complete mediation** explain a large share of real breaches: an application that
trusts its own client, or a service account with more power than its job requires.

## 3. Vocabulary that must not blur

| Term | Definition | Example |
| --- | --- | --- |
| **Asset** | Something of value worth protecting | Student records, a payment API |
| **Threat** | A potential cause of harm | A criminal group, a careless employee, a failed disk |
| **Vulnerability** | A weakness that a threat could use | Unpatched library, missing authorization check |
| **Exposure** | Being reachable or discoverable by the threat | Admin panel on the public internet |
| **Exploit** | A technique or code that uses a vulnerability | A crafted request that bypasses the check |
| **Impact** | The harm if it happens | Regulatory fine, downtime, lost trust |
| **Likelihood** | How probable it is in a given period | "Plausible within a year" |

A sentence that uses all of them correctly: *"The exposed admin panel (exposure) is vulnerable to
authentication bypass (vulnerability); a criminal group (threat) could exploit it to read records
(impact), and given the panel is indexed by search engines, likelihood is high."*

## 4. Risk, properly

**Risk = likelihood × impact.** Both are estimates, and labelling them as estimates is what makes them
useful rather than rhetorical.

A simple qualitative scale is enough for most decisions:

| Level | Likelihood | Impact |
| --- | --- | --- |
| Low | Would require unusual conditions | Minor inconvenience |
| Medium | Plausible within a year | Service degraded; some data affected |
| High | Expected; has happened before | Outage, regulated data exposed, safety affected |

### Four treatments

| Treatment | Meaning | Example |
| --- | --- | --- |
| **Avoid** | Remove the activity that creates the risk | Retire an unused legacy service |
| **Mitigate** | Reduce likelihood or impact | Add MFA, patch, segment the network |
| **Transfer** | Move the financial consequence | Cyber insurance (the risk itself remains) |
| **Accept** | Decide to live with it, in writing | A lab-only system with a documented exception |

Acceptance is legitimate **only when it is explicit and owned**. "We never got around to it" is not
acceptance; it is neglect with better branding.

### A tiny risk register

| ID | Risk | L | I | Treatment | Control | Owner | Residual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Admin panel reachable from internet | H | H | Mitigate | Restrict to VPN + MFA | Ops lead | Medium |
| R2 | Backups untested | M | H | Mitigate | Monthly restore test | DBA | Low |
| R3 | Legacy reporting server unpatched | M | M | Accept (12 months) | Isolated segment, monitoring | IT manager | Medium |

The two columns people skip — **owner** and **residual** — are the ones that make a register useful. If
nobody owns it, nobody fixes it; if residual risk is unrecorded, everyone assumes it is zero.

---

## Practical exercises

### Exercise 1 — Classify the harm (10 minutes)

For each scenario, name the property harmed most, and a second property also affected:

1. A ransomware infection encrypts a hospital's imaging archive.
2. A support agent can see any customer's order history by changing an ID in a URL.
3. A nightly job silently truncates a price column to two decimal places.

*Write your reasoning; the classification matters less than the argument.*

### Exercise 2 — Critique a design (20 minutes)

Take a system you know (a university portal is ideal) and answer:

| Principle | Question | Your assessment |
| --- | --- | --- |
| Least privilege | Can a student account do anything beyond reading its own record? | |
| Complete mediation | Is authorization enforced on every request, or only in the interface? | |
| Fail-safe defaults | If the permission check errors, is access denied? | |
| Defence in depth | Besides a password, what protects the account? | |
| Psychological acceptability | Do people share credentials because the process is painful? | |

### Exercise 3 — Build a five-line risk register (20 minutes)

For the same system, write five rows using the table format above. Rules: one row per distinct risk, an
owner for each, and a residual rating that is honest.

### Exercise 4 — Demonstrate fail-safe versus fail-open (10 minutes, optional)

A tiny simulation using nothing but shell logic:

```bash
# Fail-open: the check errors and access is granted anyway
allowed() { grep -q "^$1$" allowlist.txt 2>/dev/null || return 0; }
# Fail-safe: the check errors and access is denied
allowed_safe() { grep -q "^$1$" allowlist.txt 2>/dev/null; }

printf 'alice\n' > allowlist.txt
allowed bob && echo "fail-open: bob allowed"
allowed_safe bob || echo "fail-safe: bob denied"
```

**Expected output:**

```text
fail-open: bob allowed
fail-safe: bob denied
```

The difference is the `|| return 0` — one line of code that decides whether an error becomes an incident.
Clean up:

```bash
rm allowlist.txt
```

## Expected observations and verification

- You can name which CIA property a scenario harms, and justify it in one sentence.
- Your risk register has owners and residual ratings, not just descriptions.
- You can explain fail-open versus fail-safe without notes.
- You can point to one principle your chosen system violates.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Treating "risk" as "vulnerability" | Everyday language conflates them | Risk includes likelihood and impact; a vulnerability is only an ingredient |
| Rating everything "high" | Fear, or no calibration | Compare risks against each other; most things are medium |
| Skipping residual risk | The mitigation feels like the end | Ask "what remains after this control, and who accepts it?" |
| Confusing transparency with open design | Similar words | Open design means the mechanism is public; transparency is about disclosure of incidents |
| Assuming MFA makes an account safe | Marketing | MFA raises cost; session theft and phishing still work |
| Logging everything "for security" | No retention reasoning | Logs are sensitive data; decide what you need and for how long |

## Review questions

1. Which CIA property is harmed when a backup cannot be restored, and why?
2. Give an example of a design that violates least privilege, and the smallest fix.
3. Why is "fail-safe defaults" easier to state than to implement?
4. Distinguish threat, vulnerability, and exposure using one system.
5. When is accepting a risk the correct decision?
6. What two columns turn a list of worries into a risk register?

## Knowledge check

1. A pricing bug lets customers buy at 1% of list price. Which property is primarily harmed?
2. Name the principle violated when an application checks permissions only in its user interface.
3. If a control fails and the system grants access, that is a **fail-____** behaviour.
4. Risk is a function of which two factors?
5. A team decides a legacy server is too expensive to patch and isolates it instead. Which treatment is
   that, and what must be recorded?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. If you cannot answer 3 and 5 from memory, re-read sections 2 and 4.)*

## Summary

- Confidentiality, integrity, and availability are the properties; they conflict, and the trade-off is the
  engineering work.
- Design principles are questions, not slogans — least privilege and complete mediation catch most flaws.
- Threat, vulnerability, exposure, exploit, and impact are distinct; blurring them produces bad decisions.
- Risk = likelihood × impact, and every risk needs a treatment, an owner, and a residual rating.
- Acceptance is a decision, not a default.

## Next lesson

[CYB-103 · Threats, Vulnerabilities, Exploits and Controls](../03-threats-vulnerabilities-controls/index.md) —
who the threats are, how vulnerabilities become exploits, and how controls are classified.

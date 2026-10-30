---
title: "Threat Modeling and Attack Surfaces"
description: "The four-question framework, STRIDE, trust boundaries, and how to inventory and reduce an attack surface."
module_code: CYB-104
level: 1
kind: lesson
prerequisites: [CYB-103]
estimated_minutes: 120
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [threat-modeling, design, stride, architecture]
---

# Threat Modeling and Attack Surfaces

## Learning objectives

By the end of this lesson you can:

1. Explain what a threat model is, and when in a project it is worth doing.
2. Draw a simple data-flow diagram showing processes, data stores, external entities, and trust boundaries.
3. Apply the four-question framework to a small system.
4. Generate threats systematically with STRIDE and turn each into a concrete mitigation.
5. Inventory an attack surface and identify at least two reductions.
6. State a model's assumptions and limits so it is not mistaken for a guarantee.

## Prerequisites

[CYB-103](../03-threats-vulnerabilities-controls/index.md). Bring a system you can describe in a
paragraph — a course project, a club website, or something you use daily.

---

## 1. What a threat model is

A threat model is a **structured argument** about what could go wrong with a system, what you are doing
about it, and what you have chosen not to do. It is not a penetration test, not a compliance document, and
not a one-time deliverable.

Its value is timing. A threat model costs an hour during design and saves weeks during remediation,
because design flaws are the expensive ones: they cannot be patched, only rebuilt.

**When to model:** before building something new, before a significant change (new integration, new data
type, new exposure), or when a system's risk profile changes. Not every sprint, and not never.

## 2. The four questions

A practical framework you can use on anything:

1. **What are we building?** — a diagram and a paragraph, not a specification.
2. **What can go wrong?** — systematic threat generation (STRIDE below).
3. **What are we going to do about it?** — mitigations, owners, or explicit acceptance.
4. **Did we do a good job?** — review the model against the design, and revisit after changes.

Question 4 is the one teams skip, which is why models drift out of date and stop being trusted.

## 3. The diagram

Four symbols are enough. Draw boxes and lines; do not worry about notation.

| Element | Meaning | Example |
| --- | --- | --- |
| **External entity** | A person or system outside your control | Student, browser, payment provider |
| **Process** | Code that transforms data | Login service, upload handler |
| **Data store** | Where data rests | Database, file share, log store |
| **Data flow** | Movement of data | HTTPS request, database query |
| **Trust boundary** | Where trust level changes | Browser → server; server → database |

```text
  [Student]                                   ← external entity
      │  (1) HTTPS login
  ════╪════════════════════════  trust boundary (untrusted → trusted)
      ▼
  ┌──────────────┐   (2) SQL    ┌──────────────┐
  │ Login service│─────────────▶│  Users DB    │   ← data store
  └──────────────┘              └──────────────┘
      │ (3) session cookie
      ▼
  ┌──────────────┐   (4) file   ┌──────────────┐
  │ Upload handler│────────────▶│ Uploads dir  │
  └──────────────┘              └──────────────┘
```

**Trust boundaries are where threats concentrate.** Every arrow crossing one deserves a question: what
does the receiver assume about this data, and is that assumption enforced?

## 4. STRIDE

Six threat categories, each a prompt rather than a checklist item:

| Letter | Threat | The question | Example |
| --- | --- | --- | --- |
| **S** | Spoofing | Can someone pretend to be another identity? | Stolen session cookie reused |
| **T** | Tampering | Can data be changed without detection? | Price field edited in the request body |
| **R** | Repudiation | Can an action be denied later? | No audit log of an admin deletion |
| **I** | Information disclosure | Can data leak? | Verbose error pages reveal stack traces |
| **D** | Denial of service | Can the service be made unavailable? | Unbounded file upload fills the disk |
| **E** | Elevation of privilege | Can a user gain rights they should not have? | A student account reaches an admin endpoint |

STRIDE works because it forces coverage: without it, people model the threats they find interesting and
miss the boring ones that get exploited.

### From threat to mitigation

Each threat should produce a decision, not a paragraph of worry:

| Threat (STRIDE) | Mitigation | Owner |
| --- | --- | --- |
| S: session cookie theft | `HttpOnly`, `Secure`, short lifetime, rotation on login | Web dev |
| T: price tampering | Server recalculates price from the database | Backend dev |
| R: unlogged deletion | Append-only audit log with actor, time, object | Platform |
| I: stack traces shown | Generic error page; details to server logs only | Web dev |
| D: upload fills disk | Size cap, type allowlist, quota, monitoring | Ops |
| E: student reaches admin route | Server-side role check on every request | Backend dev |

## 5. Attack surface

**Attack surface** is the set of points where an attacker can interact with the system. It is not
theoretical; it can be listed.

Categories to inventory:

- **Network** — listening services and their exposure (internet, VPN, localhost only).
- **Application** — input fields, file uploads, APIs, authentication endpoints, integrations.
- **Human** — support staff, password reset, onboarding.
- **Supply chain** — dependencies, third-party scripts, vendor access.
- **Physical/operational** — devices, backups, removable media.

### Reduction beats defence

Two systems with the same budget: one has ten services exposed and defended, the other has two. The second
is safer, and cheaper to operate. Reductions to look for:

- Retire unused services and old endpoints.
- Put administrative interfaces behind a VPN or bastion, never the open internet.
- Bind internal tools to `localhost` instead of all interfaces (you will do this in the lab).
- Remove default accounts and sample applications.
- Replace a custom protocol or home-grown auth with a maintained library.
- Reduce data collected — data you do not hold cannot leak.

## 6. Assumptions and limits

A threat model without stated assumptions is a false comfort. Write them down:

> Assumes the database is not reachable from the internet, that TLS terminates at the load balancer, that
> administrators use MFA, and that the upload directory is not executed by the web server. Out of scope:
> insider abuse by platform staff, physical access to the data centre, and denial of service at the ISP.

If an assumption later turns out to be false, the model was wrong — and now you can see exactly which
threats become live.

---

## Practical exercises

### Exercise 1 — Draw the diagram (20 minutes)

For your chosen system, draw the four element types and mark every trust boundary. Rule: if you cannot say
what a boundary protects, you have probably missed one.

### Exercise 2 — STRIDE sweep (25 minutes)

Complete one row per STRIDE letter for the most exposed process in your diagram:

| Letter | Specific threat | Mitigation | Owner |
| --- | --- | --- | --- |
| S | | | |
| T | | | |
| R | | | |
| I | | | |
| D | | | |
| E | | | |

Specific means *this system*, not "attackers might hack it". "Password reset emails a temporary password
in plaintext" is specific.

### Exercise 3 — Attack surface inventory (20 minutes)

List every entry point you can identify, then mark each as **public**, **authenticated**, **internal**, or
**localhost only**. Any "public" that does not need to be public is a reduction opportunity.

### Exercise 4 — Propose two reductions (10 minutes)

For two inventory items, write what you would change and what would break. A reduction that breaks the
product is not a recommendation; it is a wish.

## Expected observations and verification

- Your diagram has at least one trust boundary marked, and you can name what changes across it.
- Each STRIDE row names a specific threat *and* a decision.
- You found at least one surface that could be reduced without user-visible loss.
- Your assumptions section exists and is honest.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Modelling only the happy path | It is the part you know | Start from boundaries and ask what the receiver assumes |
| Threats without mitigations | Feels like brainstorming | Every row needs a decision: mitigate, transfer, accept, or remove |
| Modelling a whole company at once | Ambition | Model one system, one data flow |
| Ignoring insiders and supply chain | They are not in the diagram tradition | Add them as external entities; the model improves immediately |
| Treating the model as a one-off document | No owner, no revisit | Revisit when the design changes; date it |
| Confusing threat modelling with penetration testing | Both are "security testing" | Testing verifies implementation; modelling challenges design |

## Review questions

1. Why is a design flaw more expensive than an implementation bug?
2. What does a trust boundary represent, and why do threats concentrate there?
3. Name the six STRIDE categories and one question each forces.
4. Give two attack-surface reductions that do not reduce functionality.
5. Why must a threat model state its assumptions?
6. When should a threat model be revisited?

## Knowledge check

1. A session cookie without `HttpOnly` primarily enables which STRIDE threat?
2. An endpoint that lets a student read another student's record by changing an ID is which category?
3. What is the fourth question of the framework, and why is it skipped?
4. True or false: binding an internal admin tool to `localhost` reduces attack surface. Why?
5. What is the difference between a threat model and a penetration test?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Check your reasoning against sections 2–5.)*

## Summary

- A threat model is a structured argument about what can go wrong, made cheaply at design time.
- Four questions: what are we building, what can go wrong, what will we do, did we do it well.
- Trust boundaries are where assumptions break — model them explicitly.
- STRIDE gives systematic coverage instead of inspiration.
- Reduction of attack surface is usually stronger and cheaper than defending every exposed point.
- Record assumptions; a model without them is a false comfort.

## Next lesson

[CYB-105 · Ethics, Authorization, Responsible Disclosure and Cyber Law](../05-ethics-authorization-disclosure-law/index.md) —
the rules that decide when this knowledge may be used, and on what.

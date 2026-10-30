# Lesson Template

**Applies to:** every lesson page (`kind: lesson`) in this course.
**Status:** mandatory from Phase 2. Deviations require a reviewer's written note in the PR.

A lesson explains one coherent idea and ends with the learner able to *do* something. If a page
needs two labs, two new mental models, and three unrelated tools, it is two lessons.

---

## 1. Required structure (in this order)

| # | Section | Purpose | Rules |
| --- | --- | --- | --- |
| 1 | Front matter | Machine-readable metadata | All keys in site-architecture §5; `status` and `last_reviewed` mandatory |
| 2 | Title block | `CYB-1xx · Title` as H1, then level, time, prerequisites, difficulty, lab link | One H1 only |
| 3 | Why this matters | 60–120 words, concrete and job-relevant | No hype, no "hackers are everywhere" framing |
| 4 | Learning outcomes | 3–5 items, measurable | Start with a Bloom verb; no "understand" as the only verb |
| 5 | Prerequisites and setup | Module/lab dependencies, tools, VM state | Explicit versions; link to environment page |
| 6 | Core concepts | The teaching body, 2–6 sub-sections | Define each new term at first use, then link to glossary |
| 7 | Worked example or walkthrough | Concrete demonstration with real (sanitized) output | Show expected output; explain *why* each step exists |
| 8 | Defender's view | How this is detected, logged, prevented, or mitigated | Mandatory even for purely conceptual lessons |
| 9 | Common mistakes | 3–5 items learners actually make | Include the misconception, not just the correction |
| 10 | Practice | Link to the module lab, plus one optional stretch task | No practice that violates the safety policy |
| 11 | Knowledge check | 5–10 items with answers withheld | Answers live in the private key store |
| 12 | Summary | 5 bullets maximum | No new material |
| 13 | References | Numbered, with access dates | Prefer primary sources: RFCs, vendor docs, NIST, OWASP |
| 14 | Footer metadata | Version, review date, reviewer, licence | Auto-rendered from front matter |

---

## 2. Writing rules

1. **Second person, active voice.** "You will capture traffic on `eth0`", not "traffic is captured".
2. **Define before use.** Every acronym expanded on first use in the page (`SIEM (Security
   Information and Event Management)`), even if defined in an earlier page.
3. **Commands are copy-paste safe.** One command per line, no `$` prompt prefix inside the block,
   no line-continuation ambiguity. Where a value must be substituted, use `UPPER_SNAKE` placeholders
   and explain each one immediately after the block.
4. **Every command explains its blast radius.** For anything with side effects, state what it
   changes and how to undo it.
5. **Show expected output.** A learner must be able to tell success from failure without guessing.
6. **Pin versions.** "Wireshark 4.2.x on Ubuntu 22.04" — never "the latest version".
7. **Scope targets explicitly.** Any command touching a network names the target and states that it
   is local/lab-only. Never write an example against a public hostname or IP.
8. **Prefer text to screenshots.** Terminal output as text; screenshots only for GUI-only steps, with
   alt text and a text description of the expected state.
9. **No answer leakage.** Model answers, flags, and full solutions never appear on the page.
10. **Neutral, professional tone about adversaries.** Describe behaviours, not nationality, ideology,
    or "criminal masterminds".
11. **Time estimates are honest.** Include reading plus practice; round up.
12. **One idea per page.** If a page exceeds ~2,500 words of body text, split it.

---

## 3. Learning outcomes: good and bad

| Bad | Why | Better |
| --- | --- | --- |
| "Understand TCP" | Not observable | "Explain how a TCP three-way handshake establishes a connection, using a packet capture as evidence" |
| "Learn nmap" | Tool-centric | "Select and justify scan types appropriate to a lab host, and interpret the output to build a service inventory" |
| "Know about SQL injection" | Not measurable | "Identify a parameterised-query fix for a given vulnerable code snippet and explain why it blocks injection" |
| "Be aware of phishing" | Untestable | "Classify five email samples as phishing or legitimate and cite the indicators used" |

---

## 4. Page skeleton (copy this)

````markdown
---
title: "CYB-105 · Networking Foundations"
description: "Layered networking model, addressing, protocols, and the path of a request."
module_code: CYB-105
level: 1
kind: lesson
prerequisites: [CYB-104]
estimated_minutes: 90
difficulty: beginner
safety: none
lab_ids: [LAB-105-01]
assessment: knowledge-check
version: 0.1.0
last_reviewed: 2026-10-28
reviewers: []
status: draft
tags: [networking, tcp-ip]
---

# CYB-105 · Networking Foundations

**Level 1** · 90 minutes · **Prerequisites:** CYB-104 · **Lab:** `lab-01-subnetting.md` (shipped with the module)

## Why this matters

…60–120 words…

## Learning outcomes

By the end of this lesson you will be able to:

- Explain how data is encapsulated as it moves down the TCP/IP stack.
- Convert between CIDR notation and host ranges for a /24 and /26 network.
- Trace a single HTTP request from browser to server and name the protocol at each hop.

## Prerequisites and setup

- Ubuntu 22.04 VM built to the [lab specification](../labs/index.md), snapshot `clean-l1`.
- Packages: `iproute2`, `dnsutils`, `curl`, `traceroute` (installed by default).
- No network access to the internet is required for the drills.

## Core concepts

### Encapsulation

…

!!! note "Terminology"
    A **socket** is … (the glossary lists the term under its first letter: [glossary](../resources/glossary.md)).

## Worked example: the path of a request

```bash
# Resolve the name first; record the answer address
dig +short example.test
```

Expected output:

```text
192.0.2.10
```

Why it matters: `192.0.2.0/24` is documentation space (RFC 5737), which is why it is safe to use in
examples.

## Defender's view

What this looks like in logs, which fields matter, and what a defender would baseline.

## Common mistakes

1. **Confusing a subnet mask with a wildcard mask.** …
2. **Assuming NAT is a security control.** …

## Practice

Complete LAB-105-01 `lab-01-subnetting.md` (part of the module, not of this template). Optional stretch: …

## Knowledge check

1. …
2. …

## Summary

- …
- …

## References

1. RFC 791 — Internet Protocol. IETF. Accessed 2026-10-28.
2. NIST SP 800-41 Rev. 1 — Guidelines on Firewalls and Firewall Policy. Accessed 2026-10-28.
````

---

## 5. Review gate

A lesson is publishable only when the [quality-checklist](quality-checklist.md) passes and a
reviewer confirms:

- Outcomes are measurable and matched by the content and the knowledge check.
- Every command was executed on the stated platform and version.
- No example targets anything outside the allowlist in the [safety policy](../policies/safety-policy.md).
- The defender's view is present and specific, not filler.
- No answers, flags, or credentials appear anywhere in the page or its assets.

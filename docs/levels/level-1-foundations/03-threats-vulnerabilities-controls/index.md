---
title: "CYB-103 · Threats, Vulnerabilities, Exploits and Controls"
description: "Who threatens systems, how weaknesses become exploits, and how controls are classified and layered."
module_code: CYB-103
level: 1
kind: reference
prerequisites: [CYB-102]
estimated_minutes: 120
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [foundations, threats, controls]
---

# CYB-103 · Threats, Vulnerabilities, Exploits and Controls

**Level 1** · 2 hours · **Prerequisites:** [CYB-102](../02-cia-triad-principles-risk/index.md)

## Why this module exists

CYB-102 gave you the words. This module connects them into a causal chain: a **threat** finds a
**vulnerability** and uses an **exploit** to cause **impact**, which a **control** is supposed to prevent,
detect, or correct. Every finding you write for the rest of the course follows that chain.

It also introduces the sobering part: most successful attacks use no vulnerability at all. They use a
working credential, a default configuration, or a person in a hurry.

## Module outcomes

By the end of this module you can:

- Categorise threat actors and explain how each changes the risk calculus.
- Distinguish design, implementation, configuration, and operational vulnerabilities.
- Explain the vulnerability management lifecycle and why "patch everything" is not a strategy.
- Describe what an exploit is, what a zero-day is, and why exploit code is not the same as a vulnerability.
- Classify controls by function and by type, and design a layered defence for a small scenario.

## Lessons

| # | Lesson | Time |
| --- | --- | --- |
| 01 | [Threats, Vulnerabilities, Exploits and Controls](01-threats-and-controls.md) | 2 h |

## What you need

- Your risk register from CYB-102 (five rows).
- Notes. No software.

## Assessment

- Knowledge check at the end of the lesson.
- Written exercise: a control map for one risk from your register.

## Related

- [Threat Modeling and Attack Surfaces](../04-threat-modeling-attack-surfaces/index.md) — applies this to design
- [Ethics, Law and Responsible Disclosure](../05-ethics-authorization-disclosure-law/index.md) — the bounds on using this knowledge
- [Glossary](../../../resources/glossary.md)

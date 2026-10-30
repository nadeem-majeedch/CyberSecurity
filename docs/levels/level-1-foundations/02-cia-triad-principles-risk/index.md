---
title: "CYB-102 · CIA Triad, Security Principles and Risk"
description: "The three properties security protects, the design principles that make systems defensible, and how risk is actually assessed."
module_code: CYB-102
level: 1
kind: reference
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

# CYB-102 · CIA Triad, Security Principles and Risk

**Level 1** · 2 hours · **Prerequisites:** [CYB-101](../01-introduction-to-cybersecurity/index.md)

## Why this module exists

Every security conversation you will ever have reduces to three questions: *what are we protecting, what
could go wrong, and what should we do first?* This module gives you precise language for all three.

Without it, findings sound like opinions. With it, "the backup job fails silently" becomes "availability
risk, high likelihood, high impact, detective control missing" — which is a sentence someone can act on.

## Module outcomes

By the end of this module you can:

- Apply confidentiality, integrity, and availability to a concrete system, and identify which is at risk.
- Use at least six design principles (least privilege, defence in depth, fail-safe defaults, and others)
  to critique a simple architecture.
- Define threat, vulnerability, exposure, and impact without conflating them.
- Estimate risk qualitatively and choose a treatment: avoid, mitigate, transfer, or accept.
- Record a small risk register with owners and residual risk.

## Lessons

| # | Lesson | Time |
| --- | --- | --- |
| 01 | [The CIA Triad, Design Principles and Risk](01-cia-principles-risk.md) | 2 h |

## What you need

- Notes from CYB-101.
- A system you know well enough to criticise (a website, an app, a university portal).

## Assessment

- Knowledge check at the end of the lesson.
- Written exercise: a five-line risk register for the system you chose. Keep it in your notes; CYB-103
  builds on it.

## Related

- [Threats, Vulnerabilities, Exploits and Controls](../03-threats-vulnerabilities-controls/index.md)
- [Threat Modeling and Attack Surfaces](../04-threat-modeling-attack-surfaces/index.md)
- [Glossary](../../../resources/glossary.md)

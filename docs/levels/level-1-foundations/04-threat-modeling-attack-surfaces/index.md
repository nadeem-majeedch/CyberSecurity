---
title: "CYB-104 · Threat Modeling and Attack Surfaces"
description: "How to find design-level weaknesses on paper, before code exists, using STRIDE and data-flow diagrams."
module_code: CYB-104
level: 1
kind: reference
prerequisites: [CYB-103]
estimated_minutes: 120
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [threat-modeling, design, stride]
---

# CYB-104 · Threat Modeling and Attack Surfaces

**Level 1** · 2 hours · **Prerequisites:** [CYB-103](../03-threats-vulnerabilities-controls/index.md)

## Why this module exists

Every previous module looked at systems as they are. This one looks at them as they are *designed* — the
cheapest possible moment to find a flaw.

A design flaw cannot be patched. If an application trusts a client-supplied price, no amount of coding
discipline fixes it; the architecture has to change. Threat modelling is the discipline that catches those
problems on paper, in an hour, instead of in production, in a quarter.

It is also the skill that most distinguishes applicants in interviews. Anyone can run a scanner. Fewer can
sit with a whiteboard and say "here is where this design will fail".

## Module outcomes

By the end of this module you can:

- Draw a data-flow diagram with processes, data stores, external entities, and trust boundaries.
- Apply the four-question threat modelling framework to a small system.
- Use STRIDE to generate threats systematically rather than by inspiration.
- Inventory an attack surface and propose reductions that do not break the product.
- Record assumptions and out-of-scope items so a model cannot be mistaken for a guarantee.

## Lessons

| # | Lesson | Time |
| --- | --- | --- |
| 01 | [Threat Modeling and Attack Surfaces](01-threat-modeling.md) | 2 h |

## What you need

- Paper or a diagram tool. This module is deliberately offline — the thinking is the exercise.
- One system to model: a small web app is ideal (login, upload, admin view).

## Assessment

- Knowledge check at the end of the lesson.
- Deliverable: a one-page threat model (diagram + STRIDE table + five mitigations) kept in your notes.
  CYB-107's lab expects the habit, not the artefact.

## Related

- [Threats, Vulnerabilities and Controls](../03-threats-vulnerabilities-controls/index.md)
- [Secure coding and threat modelling at Level 3](../../level-3.md) — where this becomes a project skill
- [Glossary](../../../resources/glossary.md)

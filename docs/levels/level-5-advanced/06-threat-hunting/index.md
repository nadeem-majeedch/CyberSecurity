---
title: "CYB-506 · Threat Hunting and Detection Engineering"
description: "Hypothesis-driven hunting, ATT&CK coverage mapping, querying sample telemetry, finding blind spots, reducing false positives and validating detections with safe simulations."
module_code: CYB-506
level: 5
kind: module
prerequisites: [CYB-401, CYB-404]
estimated_minutes: 900
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-506-01, LAB-506-02, LAB-506-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [threat-hunting, attck, coverage, false-positives, detection-validation]
---

# CYB-506 · Threat Hunting and Detection Engineering

## Why this module exists

Detection engineering builds the net. Threat hunting asks where the net has holes, and proves it by looking rather than
asserting.

The two are the same loop: a hypothesis, a query, a result that changes what you monitor. This module runs that loop
three times — on an unknown, on your coverage, and on your own rules.

## Module outcomes

By the end you can:

1. Turn intelligence or an assumption into a falsifiable hunting hypothesis.
2. Identify the data sources a hypothesis needs, and state the gap when they are missing.
3. Query sample telemetry to answer the hypothesis, including "no evidence found".
4. Map detection coverage to ATT&CK and distinguish present, partial and absent.
5. Reduce false positives by changing the logic, not by widening an exception.
6. Validate a detection with a safe simulation and record what the test does not cover.

## Lessons and labs

| Page | Type | Time |
| --- | --- | --- |
| [Hypothesis-Driven Hunting](01-hypothesis-driven-hunting.md) | Lesson | 90 min |
| [LAB-506-01 · Hunt a Hypothesis](lab-01-hunt-hypothesis.md) | Lab | 180 min |
| [LAB-506-02 · Coverage and Blind Spots](lab-02-coverage.md) | Lab | 180 min |
| [LAB-506-03 · Final Challenge: Validate and Tune](lab-03-validate-and-tune.md) | Lab | 180 min |

## What you need

- Python 3.10+ (standard library), a text editor, and the sample datasets each lab generates.
- Optional: Wazuh from CYB-404 if you want to run the queries against a real SIEM.

## Safety

Synthetic telemetry and safe local simulations only. The "attack" actions in LAB-506-03 are the kind of benign actions
you can audit on your own VM — a scheduled task, an encoded command that prints a string — and every one is reversible
by snapshot. Nothing contacts a third party.

## Assessment

LAB-506-03 is the practical assessment. A hunt that finds nothing but proves the hypothesis was testable scores higher
than one that "finds" activity by pattern-matching a single string.

## Where this fits

Builds directly on CYB-401 (SOC workflow), CYB-404 (detection engineering) and CYB-504 (artifacts). Feeds the capstone's
detection and response work.

## Related

- [LAB-506-01](lab-01-hunt-hypothesis.md) · [LAB-506-02](lab-02-coverage.md) · [LAB-506-03](lab-03-validate-and-tune.md)
- [Level 5 overview](../../level-5.md) · [Lab catalogue](../../../labs/index.md) · [Glossary](../../../resources/glossary.md)

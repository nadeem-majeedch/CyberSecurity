---
title: "CYB-206 · Host Inspection and Hardening Assessment"
description: "Inventory a Linux host, run a baseline hardening assessment, and report findings in a professional template."
module_code: CYB-206
level: 2
kind: reference
prerequisites: [CYB-205]
estimated_minutes: 960
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-206-01, LAB-206-02, LAB-206-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [lynis, hardening, audit, reporting]
---

# CYB-206 · Host Inspection and Hardening Assessment

**Level 2** · 16 hours · **Prerequisites:** [CYB-205](../05-ssh-secure-administration/index.md)

## Why this module exists

Level 2 has taught tools. This module turns them into an assessment: you inspect a host systematically, compare
it to a baseline, and write findings someone else can act on. The reporting template you build here is reused at
every later level, so it is worth doing properly once.

## Module outcomes

- Inventory users, groups, permissions, processes, services and listening sockets.
- Identify common local misconfigurations without a scanner.
- Run Lynis, read its output critically, and separate real findings from noise.
- Prioritise findings by risk, with evidence and a remediation step for each.
- Produce a professional assessment report using the course template.

## Lessons, labs and templates

| # | Item | Time |
| --- | --- | --- |
| 01 | [Inspecting a Linux Host](01-host-inspection.md) | 4 h |
| Lab | [LAB-206-01 · Host Inspection Inventory](lab-01-host-inventory.md) | 4 h |
| Lab | [LAB-206-02 · Hardening Assessment with Lynis](lab-02-lynis-assessment.md) | 4 h |
| Lab | [LAB-206-03 · Write the Assessment Report](lab-03-assessment-report.md) | 4 h |
| Ref | [Assessment Report Template](../../../policies/assessment-report-template.md) | — |

## What you need

- `lab-ubuntu` (target) and `lab-kali` (analyst).
- `lynis` 3.x: `sudo apt install lynis`.
- A snapshot before remediation, so you can compare before and after.

## A word about scanners

Lynis is a starting point, not an answer. It reports what its tests know about; it cannot see business context,
compensating controls, or the reason a setting is the way it is. Every finding it produces must still be verified,
justified and prioritised by you.

## Assessment

Three labs culminating in a marked report. LAB-206-03 is the Level 2 capstone assessment and is graded against
the report rubric in the [Assessment Guide](../../../start-here/assessment-guide.md).

## Related

- [CYB-204 · Packet Capture and Traffic Analysis](../04-packet-capture-and-analysis/index.md)
- [Assessment Report Template](../../../policies/assessment-report-template.md)
- [Quality Checklist](../../../maintainer/quality-checklist.md)

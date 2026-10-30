---
title: "CYB-505 · Security Automation"
description: "Python log parsing, offline IOC enrichment, vulnerability-report normalisation, detection-rule testing and guarded incident-response automation with secrets and audit trails."
module_code: CYB-505
level: 5
kind: module
prerequisites: [CYB-202, CYB-404]
estimated_minutes: 900
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-505-01, LAB-505-02, LAB-505-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [automation, python, enrichment, sigma, testing, incident-response]
---

# CYB-505 · Security Automation

## Why this module exists

Automation is how a small team covers a large estate — and how a small mistake becomes a large incident. A script that
disables accounts is either your fastest containment tool or your fastest outage, depending on whether it was tested,
guarded and logged.

This module builds the pipeline in the safe order: parse, normalise, enrich, test, then act — with the guard rails
before the actions.

## Module outcomes

By the end you can:

1. Parse heterogeneous logs into one normalised schema, with malformed input handled rather than crashing.
2. Enrich indicators from a local dataset without sending data to a third party.
3. Normalise findings from two different scanners into one comparable record.
4. Test detection logic against fixtures and report a pass/fail matrix.
5. Write an automation that defaults to dry-run, restricts its targets, logs every action and handles secrets safely.
6. Authenticate to an API without embedding credentials, and fail closed when authentication fails.

## Lessons and labs

| Page | Type | Time |
| --- | --- | --- |
| [Automation Discipline](01-automation-discipline.md) | Lesson | 90 min |
| [LAB-505-01 · Parse and Normalise Logs](lab-01-log-parsing.md) | Lab | 180 min |
| [LAB-505-02 · Enrichment and Report Normalisation](lab-02-enrichment.md) | Lab | 180 min |
| [LAB-505-03 · Final Challenge: Guarded Automation](lab-03-guarded-automation.md) | Lab | 180 min |

## What you need

- Python 3.10+ with `pytest`, `requests`, `pyyaml`.
- A Linux VM or WSL. No internet required after installation.
- The synthetic datasets in each lab, generated locally.

## Safety

Every lab uses synthetic data and a **mock** API on loopback. No lab contacts a real ticketing system, firewall, cloud
provider or identity provider, and no lab contains real credentials. The secrets you use are generated placeholders.

## Assessment

LAB-505-03 is the practical assessment. Grading emphasises guard rails and tests over features: a script that does
less but refuses to do the wrong thing scores higher than a powerful one with no allowlist.

## Where this fits

Depends on Bash/Python (CYB-209/210) and detection engineering (CYB-404). Feeds the security-automation parts of the
capstone and the SOC workflows in CYB-401.

## Related

- [LAB-505-01](lab-01-log-parsing.md) · [LAB-505-02](lab-02-enrichment.md) · [LAB-505-03](lab-03-guarded-automation.md)
- [Level 5 overview](../../level-5.md) · [Lab catalogue](../../../labs/index.md) · [Glossary](../../../resources/glossary.md)

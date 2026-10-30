---
title: "CYB-202 · Bash, Python and Git for Lab Work"
description: "Automate repetitive checks in Bash, parse synthetic logs in Python, and version lab artefacts with Git without leaking secrets."
module_code: CYB-202
level: 2
kind: reference
prerequisites: [CYB-201]
estimated_minutes: 960
difficulty: intermediate
safety: local-only
lab_ids: [LAB-202-01, LAB-202-02, LAB-202-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [bash, python, git, automation]
---

# CYB-202 · Bash, Python and Git for Lab Work

**Level 2** · 16 hours · **Prerequisites:** [CYB-201](../01-lab-environment-and-kali/index.md)

## Why this module exists

Analysts repeat themselves constantly: check the same ten settings, parse the same log format, compare the same
two captures. Every repetition is a chance to invent a different result — which is why repeatable scripts are a
reliability control, not a convenience.

This module teaches three tools that make work reproducible: **Bash** for quick system checks, **Python** for
structured parsing, and **Git** for tracking what you did and when. It also teaches the failure modes: scripts
that act on the wrong target, parsers that silently drop lines, and repositories that accidentally contain a
private key.

## Module outcomes

By the end of this module you can:

- Write a defensive Bash script with strict mode, validation, clear output, and exit codes.
- Parse a structured log file in Python with validation, error handling, and useful summaries.
- Version lab artefacts with Git while excluding secrets, captures, and large binaries.
- Explain why `set -euo pipefail`, argument validation, and dry-run modes prevent incidents.
- Review a script for the ways it could act outside its intended scope.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Scripting and Versioning for Repeatable Work](01-scripting-and-git.md) | 3 h |
| Lab | [LAB-202-01 · Bash Security-Check Script](lab-01-bash-security-check.md) | 3 h |
| Lab | [LAB-202-02 · Python Parser for Synthetic Logs](lab-02-python-log-parser.md) | 4 h |
| Lab | [LAB-202-03 · Git for Lab Artefacts](lab-03-git-for-artifacts.md) | 2 h |

## What you need

- `lab-kali` or `lab-ubuntu` with `bash`, `python3`, `git`, `shellcheck` (optional but recommended).
- The evidence folders from CYB-201.
- A synthetic log file — the lab provides one, so no real data is used.

## Assessment

Three labs, rubric-marked. The scripts are assessed on correctness, failure behaviour, and safety as much as on
whether they produce output.

## Related

- [System Inspection, Hardening and Reporting](../06-host-inspection-and-hardening/index.md) — where the
  scripts are used for real
- [Quality Checklist](../../../maintainer/quality-checklist.md) — the standard your documentation should meet
- [Safety Policy](../../../policies/safety-policy.md)

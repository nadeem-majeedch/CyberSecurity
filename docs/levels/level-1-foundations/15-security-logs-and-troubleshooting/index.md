---
title: "CYB-115 · Introduction to Security Logs and Basic Troubleshooting"
description: "Where logs come from, how to read them without drowning, and a repeatable method for diagnosing what broke."
module_code: CYB-115
level: 1
kind: reference
prerequisites: [CYB-114]
estimated_minutes: 150
difficulty: beginner
safety: local-only
lab_ids: [LAB-115-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [logs, troubleshooting, detection]
---

# CYB-115 · Introduction to Security Logs and Basic Troubleshooting

**Level 1** · 2.5 hours · **Prerequisites:** [CYB-114](../14-passwords-mfa-phishing/index.md)

## Why this module exists

Level 1 ends where professional work begins: with evidence. Everything you have learned — processes,
permissions, networking, credentials — becomes useful only when you can *see* it happening and explain it.

This module teaches you to read logs with purpose, and to troubleshoot in a fixed order instead of by
guessing. It is the bridge to Level 2, where you will do this continuously.

## Module outcomes

By the end of this module you can:

- Name the main log sources on Linux and Windows and what each answers.
- Read a log line: timestamp, source, actor, action, outcome.
- Filter logs by time, unit, severity, and event ID instead of scrolling.
- Follow an evidence trail from symptom to cause across two or more logs.
- Apply a fixed troubleshooting order, and record the steps you tried.
- Explain why "no log entry" is itself evidence, and what it might mean.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Reading Logs and Troubleshooting Methodically](01-logs-and-troubleshooting.md) | 1.5 h |
| Lab | [LAB-115-01 · Follow an Evidence Trail](lab-01-evidence-trail.md) | 1 h |

## What you need

- `lab-ubuntu` with `journalctl`, `rsyslog` or `systemd-journald`, `ss`, `sudo`.
- Optional: `lab-win` for the Event Viewer comparison.

## Assessment

- Knowledge check at the end of the lesson.
- Lab marked against the lab rubric, with the evidence trail as the main artefact.
- Level 1 readiness assessment follows this module.

## Related

- [Reading Logs and Troubleshooting](01-logs-and-troubleshooting.md)
- [Processes, Listening Ports and Logs lab](../09-linux-command-line/lab-02-processes-listeners-logs.md)
- [Level 2 — Tooling and Lab Craft](../../level-2.md)

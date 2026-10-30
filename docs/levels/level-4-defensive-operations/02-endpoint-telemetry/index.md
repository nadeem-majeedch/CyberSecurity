---
title: "CYB-402 · Endpoint Telemetry and Authentication Monitoring"
description: "Windows Security logs, Sysmon, journald and auth logs: the evidence base for every detection that follows."
module_code: CYB-402
level: 4
kind: reference
prerequisites: [CYB-401, CYB-110, CYB-109]
estimated_minutes: 720
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-402-01, LAB-402-02, LAB-402-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [windows-event-log, sysmon, journald, auditd, authentication, edr]
---

# CYB-402 · Endpoint Telemetry and Authentication Monitoring

**Level 4** · 12 hours · **Prerequisites:** [CYB-401](../01-soc-operations/index.md), [CYB-110](../../level-1-foundations/10-windows-powershell-basics/index.md), [CYB-109](../../level-1-foundations/09-linux-command-line/index.md)

## Why this module exists

Every detection in the rest of this level is a query over telemetry. If the telemetry is wrong, incomplete, or
misparsed, the detection is worthless — and worse, it looks like coverage.

This module builds the evidence base on both operating systems: what Windows records when someone logs on, what
Sysmon records when a process starts, what `journald` and `auth.log` record on Linux, and what each of those logs
**cannot** tell you. Authentication gets its own attention because it is where most intrusions become visible first.

## Module outcomes

By the end of this module you can:

- Identify the Windows event IDs that matter for authentication, process creation and persistence, and explain each.
- Enable the audit settings that make those events useful, and verify the change.
- Install and tune Sysmon with a community configuration, and explain the event IDs you rely on.
- Query `journald` and `auth.log` for authentication events, and distinguish brute force from password spraying.
- Recognise a suspicious parent-child process relationship using command lines, not process names.
- State the limits of endpoint telemetry: what is not logged, what can be tampered with, and what requires a
  network sensor instead.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Endpoint and Authentication Telemetry](01-endpoint-and-auth-logs.md) | 4 h |
| Lab | [LAB-402-01 · Windows Event Log Triage](lab-01-windows-event-logs.md) | 3 h |
| Lab | [LAB-402-02 · Linux Authentication Log Analysis](lab-02-linux-auth-logs.md) | 2.5 h |
| Lab | [LAB-402-03 · A Suspicious Process Sequence](lab-03-sysmon-process-sequence.md) | 2.5 h |

## What you need

- `lab-win` (Windows 11 or 10) and `lab-ubuntu`, both on the host-only network from Level 1.
- Administrative rights on both VMs — telemetry configuration is an administrative task.
- Sysmon 15.22 (Microsoft Sysinternals) and a community configuration; download it inside the lab with NAT attached.
- No internet access is required after installation.

## Assessment

Three labs, rubric-marked. Each produces a query, an evidence file, and a short written finding. LAB-402-01 and
LAB-402-03 together form the endpoint half of the Level 4 assessment's evidence expectations.

## Where this fits

[CYB-404](../04-detection-and-siem/index.md) turns these queries into rules and ingests the same events into a SIEM.
[CYB-406](../06-digital-forensics/index.md) reads the same artefacts forensically, with custody requirements.

## References

1. Microsoft Learn — Audit logon events; Command line process auditing; Sysmon. Accessed 2026-10-29.
2. Microsoft — Sysmon v15.22. <https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon> Accessed 2026-10-29.
3. Sysmon community configurations: SwiftOnSecurity and Olaf Hartong `sysmon-modular`. Accessed 2026-10-29.
4. `systemd` journald and `journalctl` documentation. Accessed 2026-10-29.
5. Linux `auditd` — `auditctl`, `ausearch`, `aureport` man pages.

---
title: "CYB-110 · Windows Fundamentals and PowerShell Basics"
description: "Windows accounts, services, registry, ACLs, event logs, and the PowerShell commands that inspect them."
module_code: CYB-110
level: 1
kind: reference
prerequisites: [CYB-109]
estimated_minutes: 180
difficulty: beginner
safety: local-only
lab_ids: [LAB-110-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [windows, powershell, active-directory]
---

# CYB-110 · Windows Fundamentals and PowerShell Basics

**Level 1** · 3 hours · **Prerequisites:** [CYB-109](../09-linux-command-line/index.md)

## Why this module exists

Most enterprise desktops and the majority of servers in business networks run Windows, and Active Directory
— the identity system you will study in Level 5 — is a Windows technology. An analyst who cannot read a
Windows event log or interpret an ACL is limited to half the estate.

This module covers the same concepts as the Linux module, in a different model: accounts instead of
users-plus-groups, ACLs instead of mode bits, the registry instead of `/etc`, Event Viewer instead of
syslog. The comparison is the lesson.

## Module outcomes

By the end of this module you can:

- Describe the Windows security model: accounts, groups, tokens, UAC, and how they differ from Linux.
- Read an NTFS ACL and explain what each entry grants.
- Inspect services, processes, listening ports, and local users from PowerShell.
- Read the Security and System event logs, and filter for a specific event ID.
- Explain why PowerShell is heavily used by both defenders and attackers, and what logging exists.
- Compute a file hash on Windows and compare it with the Linux result for the same content.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Windows Security Model and PowerShell](01-windows-powershell.md) | 2 h |
| Lab | [LAB-110-01 · Inspect a Windows Host](lab-01-windows-inspection.md) | 1 h |

## What you need

- `lab-win`: Windows 11 (or 10) evaluation VM, snapshotted, with an administrator account you control.
- PowerShell 5.1 (built in). PowerShell 7 is optional and noted where behaviour differs.
- No domain: workgroup only. Active Directory comes in Level 5.

## Assessment

- Knowledge check at the end of the lesson.
- Lab marked against the lab rubric.

## Related

- [Linux Command-Line Fundamentals](../09-linux-command-line/index.md) — the contrast
- [Introduction to Cryptography and Hashing](../13-cryptography-hashing-signatures/index.md) — the hash comparison
- [Glossary](../../../resources/glossary.md)

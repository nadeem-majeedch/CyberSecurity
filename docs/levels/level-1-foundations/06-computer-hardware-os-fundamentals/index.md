---
title: "CYB-106 · Computer Hardware, Operating Systems, Files, Processes and Permissions"
description: "How a computer actually runs: CPU, memory, disk, kernel and user space, files, processes, and permissions."
module_code: CYB-106
level: 1
kind: reference
prerequisites: [CYB-105]
estimated_minutes: 150
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [operating-systems, fundamentals, permissions]
---

# CYB-106 · Computer Hardware, Operating Systems, Files, Processes and Permissions

**Level 1** · 2.5 hours · **Prerequisites:** [CYB-105](../05-ethics-authorization-disclosure-law/index.md)

## Why this module exists

Security work is full of statements like "the process runs as root", "the file is world-writable", or "the
service listens on all interfaces". If the underlying model is fuzzy, those statements are just words.

This module builds the model: what a CPU actually does with your program, where memory comes from, what a
file really is, what a process is doing while you wait, and how permission decisions are made on Linux and
Windows. Every later module — hardening, detection, forensics — assumes this.

## Module outcomes

By the end of this module you can:

- Describe the boot sequence and where the kernel fits.
- Explain user space versus kernel space, and why that boundary is a security boundary.
- Read file metadata, ownership, and permissions on Linux, and interpret NTFS/SMB ACLs at a basic level.
- Explain what a process is, how it is created, and what its states mean.
- Use the standard commands to inspect hardware, files, processes, and permissions.
- Identify three common permission mistakes that create real risk.

## Lessons

| # | Lesson | Time |
| --- | --- | --- |
| 01 | [Hardware, Operating Systems, Files, Processes and Permissions](01-hardware-os-files-processes.md) | 2.5 h |

## What you need

- A Linux environment: your Ubuntu VM if built, otherwise WSL2 or any Linux host.
- A Windows environment for the comparison sections (your own machine is fine).
- No elevated privileges required beyond `sudo` in your own VM.

## Assessment

- Knowledge check at the end of the lesson.
- Permissions drills are completed in the lesson; the formal lab appears in CYB-109.

## Related

- [Linux Command-Line Fundamentals](../09-linux-command-line/index.md)
- [Windows Fundamentals and PowerShell](../10-windows-powershell-basics/index.md)
- [Glossary](../../../resources/glossary.md)

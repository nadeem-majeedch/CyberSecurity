---
title: "CYB-109 · Linux Command-Line Fundamentals"
description: "Navigate, inspect and administer a Linux system from the shell: paths, files, permissions, processes, services and packages."
module_code: CYB-109
level: 1
kind: reference
prerequisites: [CYB-108]
estimated_minutes: 210
difficulty: beginner
safety: local-only
lab_ids: [LAB-109-01, LAB-109-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [linux, shell, permissions, processes]
---

# CYB-109 · Linux Command-Line Fundamentals

**Level 1** · 3.5 hours · **Prerequisites:** [CYB-108](../08-addressing-and-protocols/index.md)

## Why this module exists

Every serious security tool runs on Linux, and most run *from* a shell. More importantly, the shell forces
you to know what you are doing: there is no button to click past an error.

This module is deliberately taught on Ubuntu Server, not Kali. Kali is excellent at what it is for — a
pre-loaded toolkit — but it hides the mechanics you need now. Learn the system first; the tools come later
(CYB-112).

## Module outcomes

By the end of this module you can:

- Navigate the filesystem, and explain absolute versus relative paths.
- Create, inspect, move, and remove files safely, including the risky cases to avoid.
- Read and set permissions and ownership, and explain `umask`.
- Inspect processes, map a listening port to its process, and stop a process deliberately.
- Manage services and packages, and read system logs.
- Use `man`, `--help`, and exit codes to solve problems without guessing.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Working in the Linux Shell](01-linux-shell.md) | 2 h |
| Lab | [LAB-109-01 · Files, Permissions and Ownership](lab-01-files-permissions.md) | 45 min |
| Lab | [LAB-109-02 · Processes, Listening Ports and Logs](lab-02-processes-listeners-logs.md) | 45 min |

## What you need

- `lab-ubuntu` VM with `sudo` access and a snapshot (`clean-base` or newer).
- Nothing else installed — everything here ships with Ubuntu Server.

## Assessment

- Knowledge check at the end of the lesson.
- Two labs, each marked against the lab rubric; evidence saved per lab.

## Related

- [Computer Hardware, OS, Files, Processes and Permissions](../06-computer-hardware-os-fundamentals/index.md)
- [Windows Fundamentals and PowerShell](../10-windows-powershell-basics/index.md) — the contrast
- [Troubleshooting](../../../start-here/troubleshooting.md)

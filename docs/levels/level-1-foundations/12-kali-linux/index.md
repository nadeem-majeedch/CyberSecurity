---
title: "CYB-112 · Introduction to Kali Linux"
description: "What Kali is for, what it is not, and how to use it without letting a toolkit replace understanding."
module_code: CYB-112
level: 1
kind: reference
prerequisites: [CYB-111]
estimated_minutes: 90
difficulty: beginner
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [kali, linux, tooling]
---

# CYB-112 · Introduction to Kali Linux

**Level 1** · 1.5 hours · **Prerequisites:** [CYB-111](../11-virtualization-and-lab-networks/index.md)

## Why this module exists

Kali is the most recognisable name in security tooling, and the most misunderstood. It is a Debian-based
distribution with several hundred security tools pre-installed — useful when you need a specific tool
quickly, and actively unhelpful when it encourages you to skip the fundamentals.

This module is deliberately placed late in Level 1. By now you have administered a clean Linux system, so
you can see Kali for what it is: a Linux distribution with a large toolbox, not a magic wand.

## Module outcomes

By the end of this module you can:

- Explain what Kali contains and how it differs from Ubuntu or Debian.
- Decide, for a given task, whether Kali, a standard Linux host, or a built-in OS tool is the better choice.
- Install Kali as a VM, change its default credentials, and snapshot it.
- Update the system safely, and explain why a rolling release needs regular updates.
- Locate tools and wordlists, and check a tool's version before trusting a tutorial.
- Describe why "tool-first" thinking produces findings you cannot defend.

## Lessons

| # | Lesson | Time |
| --- | --- | --- |
| 01 | [Kali Linux in Context](01-kali-in-context.md) | 1.5 h |

## What you need

- A Kali VM (installer or pre-built image) on the **host-only** network, snapshotted after setup.
- 2 vCPU, 2–4 GB RAM, 20 GB disk recommended.

## Assessment

- Knowledge check at the end of the lesson.
- No separate lab: the setup steps and comparisons are the exercise. The first tool-based lab is in Level 2.

## Related

- [Linux Command-Line Fundamentals](../09-linux-command-line/index.md) — the skills Kali assumes
- [Virtualization and Isolated Lab Design](../11-virtualization-and-lab-networks/index.md)
- [Safety Policy](../../../policies/safety-policy.md)

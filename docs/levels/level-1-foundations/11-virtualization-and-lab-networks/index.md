---
title: "CYB-111 · Virtualization, Snapshots and Isolated Lab Networks"
description: "Build a reproducible, isolated lab: hypervisors, adapter modes, snapshots and clones, isolation verification, and reset strategy."
module_code: CYB-111
level: 1
kind: reference
prerequisites: [CYB-110]
estimated_minutes: 180
difficulty: beginner
safety: isolated-vm
lab_ids: [LAB-111-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [virtualization, lab, isolation, snapshots]
---

# CYB-111 · Virtualization, Snapshots and Isolated Lab Networks

**Level 1** · 3 hours · **Prerequisites:** [CYB-110](../10-windows-powershell-basics/index.md)

## Why this module exists

This is the module the rest of the course stands on. Every practical exercise from here to the capstone
happens inside the environment you build in this module.

Two failure modes cause almost all beginner incidents: a lab VM accidentally exposed on a real network, and
an environment that cannot be reset, so a single mistake ends the level. This module fixes both by design —
isolation verified with evidence, and snapshots as a discipline rather than an emergency measure.

## Module outcomes

By the end of this module you can:

- Explain what a hypervisor does, and choose between type 1 and type 2 for a study lab.
- Configure host-only and NAT adapters, and explain when each is appropriate.
- Verify isolation with evidence rather than assumption.
- Snapshot, revert, and clone a VM deliberately, and describe the cost of each.
- Write a reset procedure so a broken lab costs minutes instead of evenings.
- Record a lab environment document that reproduces your setup.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Virtualization and Isolated Lab Design](01-virtualization-lab-design.md) | 2 h |
| Lab | [LAB-111-01 · Build and Verify an Isolated Network](lab-01-isolated-network.md) | 1 h |

## What you need

- A hypervisor: VirtualBox 7.0.x (Windows/Linux), VMware Fusion/UTM (macOS on Apple silicon).
- At least two VMs to place on the isolated network (`lab-ubuntu`, `lab-win`).
- 8 GB RAM minimum on the host; 16 GB comfortable.

## Assessment

- Knowledge check at the end of the lesson.
- Lab marked against the lab rubric, including the isolation evidence.

## Related

- [Lab Safety Guide](../../../start-here/lab-safety.md) — the practical companion
- [Labs](../../../labs/index.md) — the canonical environment specification
- [Troubleshooting](../../../start-here/troubleshooting.md)

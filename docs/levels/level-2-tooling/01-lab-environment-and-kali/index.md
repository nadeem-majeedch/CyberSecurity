---
title: "CYB-201 · Lab Environment, Kali and Network Foundations"
description: "Prepare the Kali analyst VM, build the host-only network, assign lab addresses, and validate connectivity with evidence."
module_code: CYB-201
level: 2
kind: reference
prerequisites: [CYB-112, CYB-111]
estimated_minutes: 720
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-201-01, LAB-201-02, LAB-201-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [kali, networking, lab, virtualization]
---

# CYB-201 · Lab Environment, Kali and Network Foundations

**Level 2** · 12 hours · **Prerequisites:** [CYB-112](../../level-1-foundations/12-kali-linux/index.md),
[CYB-111](../../level-1-foundations/11-virtualization-and-lab-networks/index.md)

## Why this module exists

Every later lab in this level assumes a specific, verified environment: a Kali analyst host, a target host,
static addresses on an isolated segment, and a documented connectivity baseline. When that baseline is wrong,
every scan result is suspect and every capture is misleading.

This module builds that baseline and, more importantly, produces **evidence** that it is correct — an address
register, a connectivity matrix, and the isolation transcript.

## Module outcomes

By the end of this module you can:

- Prepare a Kali VM from an official image, change its credentials, update it, and snapshot it.
- Configure a host-only virtual network with static addresses on both analyst and target hosts.
- Record a lab address register that a colleague could use to reproduce your environment.
- Validate connectivity with a repeatable matrix and save the output as evidence.
- Diagnose the three common failures: wrong adapter, wrong subnet, service bound to loopback.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Preparing the Analyst Environment](01-lab-environment.md) | 3 h |
| Lab | [LAB-201-01 · Prepare and Verify a Kali VM](lab-01-prepare-kali-vm.md) | 2 h |
| Lab | [LAB-201-02 · Configure Host-Only Networking](lab-02-host-only-network.md) | 2 h |
| Lab | [LAB-201-03 · Validate Connectivity](lab-03-connectivity-validation.md) | 2 h |

## What you need

- A hypervisor with at least 12 GB RAM available to guests.
- Kali Linux (installer ISO or pre-built VM image) and Ubuntu Server 22.04.x.
- The [Lab Safety Guide](../../../start-here/lab-safety.md) read and understood.

## Assessment

Three labs, each rubric-marked. The address register and connectivity matrix from LAB-201-02 and LAB-201-03
are reused by every later lab in the level, so keep them.

## Related

- [Bash, Python and Git](../02-bash-python-git/index.md)
- [Labs](../../../labs/index.md) — canonical environment specification
- [Safety Policy](../../../policies/safety-policy.md)

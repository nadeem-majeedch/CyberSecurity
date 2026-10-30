---
title: "CYB-107 · Networking Fundamentals and the OSI/TCP-IP Models"
description: "How layered networking works: encapsulation, the OSI and TCP/IP models, addressing, and where security controls sit."
module_code: CYB-107
level: 1
kind: reference
prerequisites: [CYB-106]
estimated_minutes: 180
difficulty: beginner
safety: local-only
lab_ids: [LAB-107-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, osi, tcp-ip, encapsulation]
---

# CYB-107 · Networking Fundamentals and the OSI/TCP-IP Models

**Level 1** · 3 hours · **Prerequisites:** [CYB-106](../06-computer-hardware-os-fundamentals/index.md)

## Why this module exists

Almost every incident involves a network: a connection that should not exist, a domain that resolved to
the wrong place, a service reachable from the internet that should not be. Without a layered model, network
evidence is a wall of noise.

This module gives you the map. Every later skill — packet analysis, detection, segmentation, cloud
security — is navigation on that map.

## Module outcomes

By the end of this module you can:

- Name the seven OSI layers and the four TCP/IP layers, and map between them.
- Explain encapsulation and name the protocol data unit at each step.
- Identify which device or control operates at which layer.
- Distinguish MAC, IP, and port as three different identifiers.
- Capture and explain a simple local exchange, layer by layer.
- Explain why "the port is open" does not mean "the service works".

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Layered Networking and Encapsulation](01-osi-tcpip.md) | 2 h |
| Lab | [LAB-107-01 · Capture a Local Exchange](lab-01-capture-local-traffic.md) | 1 h |

## What you need

- Your Ubuntu VM (recommended) or WSL2, with `sudo` access.
- `tcpdump`, `curl`, `iproute2` — installed by default on Ubuntu Server.
- Wireshark is optional; the lab uses `tcpdump` so it works over SSH and without a GUI.

## Assessment

- Knowledge check at the end of the lesson.
- Lab marked against the lab rubric: correctness, methodology, evidence, safety.

## Related

- [IP Addressing, Subnets and Core Protocols](../08-addressing-and-protocols/index.md) — the next layer of detail
- [Lab Safety Guide](../../../start-here/lab-safety.md) — capture only inside your own lab
- [Glossary](../../../resources/glossary.md)

---
title: "CYB-203 · Host Discovery and Service Enumeration"
description: "Discover hosts and enumerate services inside your own lab with nmap and netcat, and interpret the results honestly."
module_code: CYB-203
level: 2
kind: reference
prerequisites: [CYB-202]
estimated_minutes: 1080
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-203-01, LAB-203-02, LAB-203-03, LAB-203-04]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [nmap, netcat, enumeration, tcp, udp]
---

# CYB-203 · Host Discovery and Service Enumeration

**Level 2** · 18 hours · **Prerequisites:** [CYB-202](../02-bash-python-git/index.md)

## Why this module exists

Enumeration is where most assessments start and where most beginners embarrass themselves. A scan produces
hundreds of lines of output; a finding requires knowing which lines mean something, which are artefacts of the
scan itself, and what the tool cannot see.

This module teaches you to scan **your own lab** deliberately: choose options for a reason, verify by hand,
and write down what the evidence does and does not support.

!!! warning "Scope"
    Every scan in this module targets `192.0.2.0/24` — your own isolated lab. Scanning any other address,
    including your university's or employer's network, is prohibited by the
    [Safety Policy](../../../policies/safety-policy.md) and is a criminal offence in most jurisdictions.

## Module outcomes

By the end of this module you can:

- Perform host discovery on a lab subnet and explain which discovery method answered.
- Enumerate TCP ports and identify services, verifying each with an independent tool.
- Explain the difference between a filtered, closed, and open port from evidence you produced.
- Demonstrate TCP and UDP behaviour differences with `netcat` and `nmap`.
- Use `netcat` for controlled local demonstrations, and describe its limitations.
- Document an inventory that distinguishes confirmed services from scanner guesses.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Scanning Your Own Lab](01-scanning-your-lab.md) | 3 h |
| Lab | [LAB-203-01 · Host Discovery](lab-01-host-discovery.md) | 3 h |
| Lab | [LAB-203-02 · Port and Service Enumeration](lab-02-service-enumeration.md) | 4 h |
| Lab | [LAB-203-03 · TCP and UDP Behaviour](lab-03-tcp-udp-behaviour.md) | 3 h |
| Lab | [LAB-203-04 · Netcat for Controlled Demonstrations](lab-04-netcat-local.md) | 3 h |

## What you need

- `lab-kali` (analyst) and `lab-ubuntu` (target) on `192.0.2.0/24`.
- `nmap` 7.94+ and `netcat` on both hosts; `curl`, `ss`, `tcpdump` for verification.
- The connectivity matrix from LAB-201-03.

## Assessment

Four labs, rubric-marked. LAB-203-02 produces the inventory you will reuse in LAB-206-03's report, so keep the
evidence and the output files.

## Related

- [Packet Capture and Traffic Analysis](../04-packet-capture-and-analysis/index.md) — see your own scans on the wire
- [System Inspection, Hardening and Reporting](../06-host-inspection-and-hardening/index.md)
- [Safety Policy](../../../policies/safety-policy.md)

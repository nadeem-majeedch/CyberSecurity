---
title: "CYB-405 · Network Defence and Monitoring"
description: "Segment a lab network with a default-deny policy, place an IDS where it can see something, and analyse DNS for behaviour rather than signatures."
module_code: CYB-405
level: 4
kind: reference
prerequisites: [CYB-404, CYB-206]
estimated_minutes: 720
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-405-01, LAB-405-02, LAB-405-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [segmentation, nftables, firewall, suricata, ids, dns, zeek, tls]
---

# CYB-405 · Network Defence and Monitoring

**Level 4** · 12 hours · **Prerequisites:** [CYB-404](../04-detection-and-siem/index.md), [CYB-206](../../level-2-tooling/04-packet-capture-and-analysis/index.md)

## Why this module exists

Endpoint telemetry tells you what happened on a host. The network tells you what happened *between* hosts, including
the traffic a compromised endpoint cannot hide: the connection it made, the name it resolved, the bytes it moved.

This module builds the network half of the defensive picture. You will enforce a segmentation policy and prove it with
a test matrix rather than a diagram. You will place an IDS where it can actually see traffic and write a rule that
fires on traffic you generated. Then you will analyse DNS — the protocol attackers most often leave intact, because
blocking it breaks everything — and learn why "many domains" is weak evidence while "long labels, TXT records, regular
intervals" is stronger.

## Module outcomes

By the end of this module you can:

- Define zones and a default-deny policy, and justify each allowed flow.
- Implement the policy with `nftables` and verify it with allowed *and* denied probes.
- Place a network sensor where it sees the traffic you care about, and state what it cannot see.
- Write a Suricata rule, generate matching traffic, and confirm the alert in `eve.json`.
- Explain what TLS hides, what metadata remains, and why interception is a legal and ethical decision, not a technical one.
- Analyse DNS traffic for tunnelling and beaconing behaviour, distinguishing it from legitimate CDN and resolver patterns.
- Write a network finding that states confidence and limitations.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Zones, Sensors and What Encryption Hides](01-segmentation-and-monitoring.md) | 3.5 h |
| Lab | [LAB-405-01 · Segmentation You Can Prove](lab-01-segmentation.md) | 3 h |
| Lab | [LAB-405-02 · Suricata: Detect Traffic You Generated](lab-02-suricata-ids.md) | 3 h |
| Lab | [LAB-405-03 · DNS Behaviour Analysis](lab-03-dns-analysis.md) | 2.5 h |

## What you need

- `lab-ubuntu` (192.0.2.20), `lab-siem` (192.0.2.30), `lab-win` (192.0.2.40), and a Kali or analyst VM
  (192.0.2.10).
- A second VirtualBox **internal network** for the simulated DMZ (`10.10.10.0/24`), with `lab-siem` dual-homed.
- Suricata **8.0.7** and Zeek **9.0.1 LTS** installed on `lab-siem`.
- Python 3.10+ with Scapy for generating the synthetic DNS capture; `tshark` for extraction.
- NAT attached only for package installation. Every address in this module is documentation or private space.

## A note on placement

An IDS on the wrong interface is an expensive way to collect nothing. Before you install anything, answer: which
segment carries the traffic I care about, and does my sensor see it? In this lab the answer is the DMZ link, because
that is where the simulated lateral movement crosses.

## Assessment

LAB-405-01 is marked on the verification matrix — a policy without denied-path tests is a claim. LAB-405-02 requires
a positive and a negative test, plus an explicit statement of what the sensor cannot see. LAB-405-03 requires a
behaviour-based judgement with a stated false-positive alternative, not just a list of long domains.

## Where this fits

[CYB-406](../06-digital-forensics/index.md) uses packet captures as evidence, with hashing and custody. [CYB-407](../07-incident-response/index.md)
uses the segmentation policy to decide what containment is even possible.

## References

1. Suricata 8.0.7 — configuration, AF_PACKET, rule syntax, `eve.json`. <https://docs.suricata.io/> Accessed 2026-10-29.
2. Zeek 9.0.1 LTS — `dns.log`, scripting, notices. <https://docs.zeek.org/> Accessed 2026-10-29.
3. `nftables` wiki — tables, chains, sets, verdict maps, counters. <https://wiki.nftables.org/> Accessed 2026-10-29.
4. NIST SP 800-41 Rev. 1 — Guidelines on Firewalls and Firewall Policy. Accessed 2026-10-29.
5. NIST SP 800-94 — Guide to Intrusion Detection and Prevention Systems. Accessed 2026-10-29.
6. MITRE ATT&CK — T1071.004 DNS, T1048 Exfiltration Over Alternative Protocol, T1572 Protocol Tunneling.
   <https://attack.mitre.org/> Accessed 2026-10-29.

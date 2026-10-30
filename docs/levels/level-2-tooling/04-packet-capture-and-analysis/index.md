---
title: "CYB-204 · Packet Capture and Traffic Analysis"
description: "Capture with tcpdump, analyse with Wireshark, and read DNS, TCP, HTTP and TLS exchanges without guessing."
module_code: CYB-204
level: 2
kind: reference
prerequisites: [CYB-203]
estimated_minutes: 960
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-204-01, LAB-204-02, LAB-204-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [tcpdump, wireshark, pcap, tls, dns]
---

# CYB-204 · Packet Capture and Traffic Analysis

**Level 2** · 16 hours · **Prerequisites:** [CYB-203](../03-host-discovery-and-enumeration/index.md)

## Why this module exists

Logs tell you what a system recorded. A capture tells you what actually crossed the wire — including the
attempts that never reached a log, the retransmissions that explain a timeout, and the TLS metadata that reveals
a destination without decrypting anything.

Packet analysis is also the skill that most quickly exposes whether you understand protocols. You cannot bluff
your way through a three-way handshake in front of a capture.

## Module outcomes

By the end of this module you can:

- Capture traffic safely on a lab interface, with a bounded filter and a documented purpose.
- Use BPF capture filters and Wireshark display filters for different jobs.
- Read a pcap in both `tcpdump` and Wireshark without a GUI dependency.
- Explain DNS queries and responses, a TCP handshake, an HTTP exchange, and TLS metadata from real captures.
- Handle capture files as evidence: naming, hashing, retention, and sanitisation.
- State what a capture cannot show — encryption boundaries, host-internal activity, dropped traffic.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Capture and Read Traffic](01-capture-and-analysis.md) | 3 h |
| Lab | [LAB-204-01 · Capture with tcpdump and Inspect a pcap](lab-01-tcpdump-capture.md) | 4 h |
| Lab | [LAB-204-02 · Capture and Analyse with Wireshark](lab-02-wireshark-analysis.md) | 4 h |
| Lab | [LAB-204-03 · Protocol Analysis: DNS, TCP, HTTP, TLS](lab-03-protocol-analysis.md) | 4 h |

## What you need

- `lab-kali` and `lab-ubuntu` on `192.0.2.0/24`.
- `tcpdump` 4.99+, `tshark` 4.x, and optionally the Wireshark GUI.
- `curl`, `dig`, `openssl` for generating traffic.
- Disk discipline: captures grow quickly. Bound every capture with `-c` or a time limit.

## Assessment

Three labs, rubric-marked. LAB-204-03 produces the analysis note that LAB-206-03's report cites, so keep the pcaps
and the written narrative.

## Related

- [Host Discovery and Service Enumeration](../03-host-discovery-and-enumeration/index.md)
- [OpenSSH and Secure Remote Administration](../05-ssh-secure-administration/index.md)
- [Troubleshooting](../../../start-here/troubleshooting.md)

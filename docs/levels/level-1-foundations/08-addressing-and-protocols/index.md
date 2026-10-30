---
title: "CYB-108 · IP Addressing, Subnets and Core Protocols"
description: "IPv4 addressing and subnetting, DNS, DHCP, ARP, TCP and UDP, and what HTTP/HTTPS/TLS actually exchange."
module_code: CYB-108
level: 1
kind: reference
prerequisites: [CYB-107]
estimated_minutes: 240
difficulty: beginner
safety: local-only
lab_ids: [LAB-108-01, LAB-108-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, subnetting, dns, tcp, http, tls]
---

# CYB-108 · IP Addressing, Subnets and Core Protocols

**Level 1** · 4 hours · **Prerequisites:** [CYB-107](../07-networking-fundamentals/index.md)

## Why this module exists

This is the module that makes network evidence readable. When a log line says `10.0.0.5 -> 203.0.113.9:443`,
you should be able to answer: is that internal or external, is the destination expected, and what protocol
is on that port?

It is also the module where beginners usually quit — subnetting looks like arithmetic homework. It is not
difficult, it is just unfamiliar, and it is unavoidable: address reasoning appears in every firewall rule,
every cloud security group, and every incident timeline.

## Module outcomes

By the end of this module you can:

- Convert between CIDR notation and address ranges, and identify network, broadcast, and usable hosts.
- Recognise private, loopback, link-local, and documentation ranges on sight.
- Explain how ARP, DNS, and DHCP each solve a different problem, and what fails when each is broken.
- Compare TCP and UDP, and place common services on their ports.
- Read an HTTP request and response, and explain what TLS adds and what it does not.
- Diagnose "the name does not resolve" versus "the port is closed" versus "the service is broken".

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [IPv4 Addressing, Subnets, ARP, DNS and DHCP](01-addressing-subnets-dns.md) | 2 h |
| 02 | [TCP, UDP, HTTP, HTTPS and TLS](02-tcp-udp-http-tls.md) | 1.5 h |
| Lab | [LAB-108-01 · Inspect Network Configuration](lab-01-network-configuration.md) | 45 min |
| Lab | [LAB-108-02 · Read DNS Lookups](lab-02-dns-lookups.md) | 45 min |

## What you need

- Ubuntu VM with `iproute2`, `dnsutils` (`dig`), `curl`, `openssl`.
- The ability to install `ipcalc` inside the VM (optional but recommended):

  ```bash
  sudo apt install -y ipcalc
  ```

## Assessment

- Knowledge check at the end of each lesson.
- Two labs, each marked against the lab rubric.

## Related

- [Layered Networking](../07-networking-fundamentals/index.md) — the model this module fills in
- [Linux Command-Line Fundamentals](../09-linux-command-line/index.md)
- [Lab Safety Guide](../../../start-here/lab-safety.md)

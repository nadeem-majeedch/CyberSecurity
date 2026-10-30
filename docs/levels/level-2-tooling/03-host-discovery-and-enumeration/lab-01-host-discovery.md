---
title: "LAB-203-01 · Host Discovery in an Isolated Lab"
description: "Discover hosts on 192.0.2.0/24 with three methods, compare results, and record what each method proves."
module_code: CYB-203
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-203-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [nmap, discovery, arp, icmp]
---

# LAB-203-01 · Host Discovery in an Isolated Lab

## Prerequisites

The CYB-203 lesson and the Level 2 topology from CYB-201: `lab-kali` and `lab-ubuntu` on the host-only
`192.0.2.0/24` segment, both booted and reachable. A NAT adapter is not required and should be removed
before scanning.

## Scenario and background

You have inherited a lab segment with no documentation beyond an address plan that may be stale. Before
enumerating services, you must establish which hosts actually exist. Different discovery methods see different
things, and knowing **why** a method missed a host is more valuable than the host list itself.

All activity is confined to `192.0.2.0/24`, your own host-only segment.

## Learning objectives

By the end of this lab you can:

1. Run ICMP, ARP, and TCP-based host discovery and compare the results.
2. Explain why ARP is authoritative on a local segment and useless across a router.
3. Use `--reason` to justify each host's inclusion.
4. Cross-check scan results against the local ARP cache and direct pings.
5. Record a host inventory with evidence and stated limitations.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| `nmap` | 7.94+ | `nmap --version` |
| `ip` | iproute2 | `ip neigh`, `ip route` |
| `ping` | iputils | Cross-check |

## Setup

```bash
mkdir -p ~/lab/level-2/lab-203/evidence
cd ~/lab/level-2/lab-203
```

Ensure `lab-ubuntu` (`192.0.2.20`) is powered on. Optionally start `lab-win` (`192.0.2.30`) to have a second
host; a third address (`192.0.2.99`) is deliberately not assigned, so discovery should not find it.

## Target addresses and lab topology

```
192.0.2.0/24 (host-only, no gateway)
  192.0.2.10  lab-kali     (analyst — you are here)
  192.0.2.20  lab-ubuntu   (target)
  192.0.2.30  lab-win      (optional)
  192.0.2.99  (unassigned — must NOT appear)
```

## Numbered commands and actions

### 1. Baseline: what does the local system already know?

```bash
ip -br addr
ip route
ip neigh
```

**Why first:** the ARP cache often lists hosts you have recently contacted. It is a free, zero-traffic inventory
of the segment.

### 2. ICMP echo discovery

```bash
nmap -sn -PE 192.0.2.0/24 -oN evidence/discovery-icmp.txt
cat evidence/discovery-icmp.txt
```

**Expected:** one `Nmap scan report for 192.0.2.20` block per responding host, and a summary line
`Nmap done: 256 IP addresses (2 hosts up) scanned`. If a host is missing here but present in `ip neigh`, that is
a real finding about ICMP filtering or host configuration.

### 3. ARP discovery (local segment, authoritative)

```bash
sudo nmap -sn -PR 192.0.2.0/24 -oN evidence/discovery-arp.txt
cat evidence/discovery-arp.txt
```

**Expected:** the same hosts, plus MAC addresses. ARP cannot be blocked on a local segment without breaking
connectivity, which is why it is the most reliable method here.

### 4. TCP-based discovery with reasons

```bash
sudo nmap -sn -PS22,80,443 --reason 192.0.2.0/24 -oN evidence/discovery-tcp.txt
head -40 evidence/discovery-tcp.txt
```

**Why:** a SYN to a closed port still returns RST, so the host answers even when ICMP is blocked. Compare the
`Reason:` line per host.

### 5. Cross-check by hand

```bash
ping -c1 -W1 192.0.2.20 >/dev/null && echo "20 responds to icmp"
ping -c1 -W1 192.0.2.99 >/dev/null && echo "99 responds (unexpected!)" || echo "99 absent (expected)"
ip neigh show
```

**Expected:** `20 responds`, `99 absent (expected)`, and ARP entries for the hosts that replied.

### 6. Record the inventory

Create `evidence/host-inventory.md`:

| Address | Hostname | Discovered by | MAC | Evidence file | Confidence |
| --- | --- | --- | --- | --- | --- |
| 192.0.2.20 | lab-ubuntu | ICMP, ARP, TCP | | discovery-arp.txt | Confirmed |
| 192.0.2.99 | — | none | — | all three | Confirmed absent |

Then answer in the same file: **which method would still work if the target blocked ICMP and you were on a
different subnet?** (Answer: TCP SYN to a common port, or ARP only if local.)

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `-sn` | Ping scan, no port scan | Discovery only — no enumeration yet |
| `-PE` | ICMP echo request | The classic method |
| `-PR` | ARP requests | Authoritative on the local segment |
| `-PS22,80,443` | TCP SYN to those ports | Works when ICMP is filtered |
| `--reason` | Show what produced each result | The justification column in your inventory |
| `-oN FILE` | Normal-format output file | Evidence that survives terminal scrollback |

## Expected observations

- ARP discovery returns every powered-on host with MAC addresses.
- ICMP and TCP discovery may differ from ARP if a host blocks ICMP.
- `192.0.2.99` never appears.
- `ip neigh` corroborates the ARP results.
- The inventory records which method found each host, with a confidence level.

## Verification criteria

- [ ] Three output files saved (`discovery-icmp.txt`, `discovery-arp.txt`, `discovery-tcp.txt`).
- [ ] Inventory table complete, including the deliberately absent address.
- [ ] You quoted the `Reason:` line for at least one host.
- [ ] Manual ping and `ip neigh` cross-checks recorded.
- [ ] No scan targeted anything outside `192.0.2.0/24`.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `nmap: command not found` | Tool missing | `sudo apt install -y nmap` |
| 0 hosts up | Wrong interface/subnet | `ip -br addr`; confirm `192.0.2.x/24` |
| ARP scan finds nothing | VM on a NAT or bridged adapter | Switch to host-only and re-test |
| `-PR` requires root | Raw sockets | `sudo` |
| ICMP finds fewer hosts than ARP | Host blocking ICMP | Not a failure — record it as a finding |
| Scan lists many unrelated hosts | Wrong subnet (e.g. `/16`) | Use `192.0.2.0/24` exactly |

## Cleanup and restoration

Read-only lab; nothing to revert. Keep the evidence files — LAB-203-02 builds on this inventory.

```bash
ls -l ~/lab/level-2/lab-203/evidence/
```

## Questions and extension challenges

1. Why can ARP discovery not cross a router, and what would you use instead?
2. What does a host's ability to answer a TCP SYN to a closed port prove?
3. Why record confidence levels rather than a simple "up/down"?
4. **Extension:** temporarily block ICMP on `lab-ubuntu` (`sudo sysctl -w net.ipv4.icmp_echo_ignore_all=1`) and
   re-run all three methods. Record what changed, then restore it with `sysctl -w net.ipv4.icmp_echo_ignore_all=0`.
5. **Extension:** add a discovery run that uses `-PU` (UDP) and explain why it is slow and ambiguous.

## Related

- [Scanning Your Own Lab](01-scanning-your-lab.md)
- [LAB-203-02 · Port and Service Enumeration](lab-02-service-enumeration.md)
- [LAB-201-03 · Validate Connectivity](../01-lab-environment-and-kali/lab-03-connectivity-validation.md)

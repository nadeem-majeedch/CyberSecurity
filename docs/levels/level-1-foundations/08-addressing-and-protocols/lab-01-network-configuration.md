---
title: "LAB-108-01 · Inspect Network Configuration"
description: "Document interfaces, addresses, routes, DNS configuration and isolation state on your own lab host."
module_code: CYB-108
level: 1
kind: lab
prerequisites: [CYB-108]
estimated_minutes: 45
difficulty: beginner
safety: local-only
lab_ids: [LAB-108-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, iproute2, documentation]
---

# LAB-108-01 · Inspect Network Configuration

**Module:** CYB-108 · **Time:** 45 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-108-01`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** your own lab VM's interfaces and the hosts inside your lab network.
    **Targets you must not use:** anything outside your lab — including your host's network, your
    university's network, or the internet.

    This lab is read-only: you inspect configuration and record it. You change nothing except a temporary
    hosts entry, which you remove at the end.

## Objective

Produce a one-page configuration record of your lab host — interfaces, addresses, routes, resolver
settings, and isolation status — that a colleague could use to reproduce your environment.

## Threat model

None. Read-only inspection of your own system. The only risk is confusing your host with your lab VM, which
the verification steps below are designed to catch.

## Environment

| Host | Role | Notes |
| --- | --- | --- |
| `lab-ubuntu` | The system being documented | Ubuntu Server 22.04.x |

Software: `iproute2` (provides `ip`, `ss`), `systemd-resolved` (provides `resolvectl`),
`dnsutils` (provides `dig`, installed via `sudo apt install -y dnsutils`).

## Before you start

```bash
hostname
uname -sr
```

Confirm you are inside the VM (hostname should match your lab VM, not your laptop).

## Procedure

### Step 1 — Create the evidence folder

```bash
mkdir -p ~/cyber/level-1/lab-108-01/evidence
cd ~/cyber/level-1/lab-108-01
```

### Step 2 — Capture interface and address state

```bash
ip -br link > evidence/interfaces.txt
ip -br addr >> evidence/interfaces.txt
ip route show >> evidence/interfaces.txt
cat evidence/interfaces.txt
```

**Expected output** (names and addresses vary):

```text
lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
enp0s3           UP             08:00:27:1a:2b:3c <BROADCAST,MULTICAST,UP,LOWER_UP>
lo               UNKNOWN        127.0.0.1/8 ::1/128
enp0s3           UP             192.0.2.20/24
default via 192.0.2.1 dev enp0s3 proto static
```

### Step 3 — Capture resolver configuration

```bash
resolvectl status 2>/dev/null | head -20 > evidence/dns.txt || cat /etc/resolv.conf > evidence/dns.txt
cat /etc/hosts >> evidence/dns.txt
cat evidence/dns.txt
```

**Expected:** on Ubuntu Server with `systemd-resolved`, a section naming the DNS server (often
`127.0.0.53` stub, or your gateway). Without it, `nameserver 192.0.2.1` in `/etc/resolv.conf`.

### Step 4 — Verify isolation (the important step)

```bash
printf '=== isolation checks ===\n' > evidence/isolation.txt
ping -c1 -W2 8.8.8.8 >> evidence/isolation.txt 2>&1; echo "internet ping exit: $?" >> evidence/isolation.txt
ping -c1 -W2 192.0.2.1 >> evidence/isolation.txt 2>&1; echo "gateway ping exit: $?" >> evidence/isolation.txt
cat evidence/isolation.txt
```

**Expected:** the internet ping fails (exit non-zero, "Network is unreachable" or timeout) while the gateway
ping may succeed. If internet ping succeeds, your lab is not isolated — stop and fix the adapter
([Lab Safety Guide](../../../start-here/lab-safety.md)).

### Step 5 — Inventory listening ports

```bash
ss -tulpn > evidence/listeners.txt 2>/dev/null
cat evidence/listeners.txt
```

**Expected** (varies): `sshd` on `0.0.0.0:22` or `[::]:22`, plus `systemd-resolved` on `127.0.0.53:53`.
Record every listener and its bind address. `0.0.0.0` means all interfaces; `127.0.0.1` means local only.

### Step 6 — Write the configuration record

Create `configuration-record.md`:

| Field | Value |
| --- | --- |
| Hostname | |
| OS / kernel | |
| Interface(s) | |
| Address / prefix | |
| Default gateway | |
| DNS resolver | |
| Notable listeners | |
| Internet reachable? | |
| Snapshot taken? | |

Add one sentence for each listener explaining whether it needs to be reachable from the network, or only
locally. This is your first real hardening question.

## Evidence to collect

`evidence/interfaces.txt`, `evidence/dns.txt`, `evidence/isolation.txt`, `evidence/listeners.txt`, and
`configuration-record.md`.

## Verification

- [ ] The host is identified as the lab VM, not the physical host.
- [ ] Address and prefix are recorded, with the network and broadcast derived.
- [ ] The isolation check failed as required, and the output is saved.
- [ ] Every listener is listed with its bind address.
- [ ] The record is complete enough for someone else to rebuild the host.

## Teardown and reset

The lab is read-only, so nothing needs reverting. Confirm:

```bash
git -C ~/cyber status 2>/dev/null || ls -la ~/cyber/level-1/lab-108-01
```

If you added a temporary `/etc/hosts` entry at any point, remove it:

```bash
sudo sed -i '/example.test/d' /etc/hosts
```

## Reflection

1. Which listener on your host is reachable from other lab hosts, and does it need to be?
2. Why does `127.0.0.53` appear as a DNS server on some Ubuntu systems?
3. What would change in your record if the VM used NAT instead of host-only?
4. Which single fact in your record proves isolation?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Missing addresses or isolation evidence | Complete record, correct derivations | Complete, plus listener necessity analysis |
| Methodology | Commands run without purpose | Ordered inspection | Explains why each command answers a specific question |
| Evidence | Unsaved terminal output | Saved transcripts | Timestamped, reproducible, with commands included |
| Safety | Ran on the host or scanned outside the lab | Stayed local, read-only | Stayed local and documented the isolation proof |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `resolvectl: command not found` | `systemd-resolved` absent | Read `/etc/resolv.conf` instead |
| `ip: command not found` | Minimal container image | Install `iproute2` |
| All pings fail including the gateway | No route on the lab interface | Check netplan config and `ip route` |
| Internet ping succeeds | Bridged adapter, or NAT still attached | Switch to host-only; disable the NAT adapter |
| `ss` shows nothing without `sudo` | Process names need privileges | Run `sudo ss -tulpn` |

## Related

- [IPv4 Addressing, Subnets, ARP, DNS and DHCP](01-addressing-subnets-dns.md)
- [LAB-108-02 · Read DNS Lookups](lab-02-dns-lookups.md)
- [Lab Safety Guide](../../../start-here/lab-safety.md)

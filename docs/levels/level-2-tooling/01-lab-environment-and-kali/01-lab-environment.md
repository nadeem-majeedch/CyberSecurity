---
title: "Preparing the Analyst Environment"
description: "Kali installation choices, host-only networking with static addresses, the address register, and connectivity validation."
module_code: CYB-201
level: 2
kind: lesson
prerequisites: [CYB-112, CYB-111]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [kali, networking, lab, nmcli, netplan]
---

# Preparing the Analyst Environment

## Learning objectives

By the end of this lesson you can:

1. Choose between a Kali installer ISO and a pre-built VM image, and justify the choice.
2. Configure a host-only virtual network with static addresses on multiple guests.
3. Write an address register that makes your lab reproducible.
4. Validate connectivity with a matrix of checks and interpret each result.
5. Diagnose wrong-adapter, wrong-subnet, and loopback-binding failures.

## Prerequisites

Level 1 complete, especially CYB-111 (isolation and snapshots) and CYB-112 (Kali context).

---

## 1. Kali: image or installer?

| Option | Good for | Watch out for |
| --- | --- | --- |
| Pre-built VM image (`.7z` / OVA) | Fastest start, known-good drivers | Default credentials; large download; must change password immediately |
| Installer ISO | Learning the install, custom partitioning | More steps; you must install tools you want |
| Live USB / bare metal | Not recommended for this course | No isolation, no snapshots |

For this course, the pre-built VM is fine **provided** you change the default password, update, and snapshot
before use. If you want the install experience, use the ISO — it is a legitimate exercise, just a longer one.

Official documentation and downloads live at <https://www.kali.org/get-kali/>. Always verify the download
hash against the published value before importing it.

## 2. Sizing the VMs

| Host | vCPU | RAM | Disk | Purpose |
| --- | --- | --- | --- | --- |
| `lab-kali` | 2 | 4096 MB | 25 GB | Analyst workstation |
| `lab-ubuntu` | 2 | 2048 MB | 20 GB | Target and reference host |
| `lab-win` | 2 | 4096 MB | 50 GB | Optional secondary host |

Give the analyst VM the RAM: Wireshark, a browser, and a terminal session together will use it.

## 3. Host-only networking with static addresses

Create the virtual network once (VirtualBox: File → Tools → Network Manager → Host-only; VMware: Virtual
Network Editor → `vmnet1`), then attach each VM and assign addresses.

Kali uses NetworkManager. The modern way:

```bash
ip -br link                                  # find the interface name, e.g. eth0
sudo nmcli connection add type ethernet ifname eth0 con-name lab-static \
  ipv4.method manual ipv4.addresses 192.0.2.10/24 ipv4.gateway "" ipv6.method disabled
sudo nmcli connection up lab-static
ip -br addr show eth0
```

**Expected:**

```text
eth0             UP             192.0.2.10/24
```

On Ubuntu Server, netplan:

```bash
sudo tee /etc/netplan/60-lab.yaml >/dev/null <<'YAML'
network:
  version: 2
  ethernets:
    enp0s8:
      addresses: [192.0.2.20/24]
YAML
sudo chmod 600 /etc/netplan/60-lab.yaml
sudo netplan apply
```

**Why no gateway?** A gateway on an isolated segment invites traffic to leave it. If a lab genuinely needs
internet access, attach NAT as a second adapter temporarily and remove it afterwards.

## 4. The address register

Write this file once and keep it with your notes. Every later lab refers to it.

| Host | Role | Interface | Address | MAC | Snapshot | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `lab-kali` | Analyst | `eth0` | `192.0.2.10/24` | 08:00:27:aa:bb:01 | `kali-baseline` | Host-only `vboxnet0` |
| `lab-ubuntu` | Target | `enp0s8` | `192.0.2.20/24` | 08:00:27:aa:bb:02 | `ubuntu-baseline` | Host-only `vboxnet0` |
| `lab-win` | Optional | `Ethernet` | `192.0.2.30/24` | 08:00:27:aa:bb:03 | `win-baseline` | Host-only `vboxnet0` |
| Gateway | none | — | — | — | — | No route out, by design |

Collect the MAC addresses from the hypervisor settings (or `ip link show` inside the guest). Recording them
saves an hour later when a scan reports a MAC you cannot place.

## 5. Validating connectivity

Run a fixed matrix and save the output. Five checks, each answering a different question:

| # | Check | Command | What it proves |
| --- | --- | --- | --- |
| 1 | Interface up | `ip -br link` | Link state |
| 2 | Address applied | `ip -br addr` | Correct subnet |
| 3 | Route table | `ip route` | No unintended default route |
| 4 | Peer reachable | `ping -c2 192.0.2.20` | Layer 3 path between guests |
| 5 | Internet blocked | `ping -c1 -W2 8.8.8.8` | Isolation is real |

```bash
mkdir -p ~/lab/level-2/lab-201/evidence
{
  echo "== $(date -Is) $(hostname) =="
  ip -br link; ip -br addr; ip route
  ping -c2 -W2 192.0.2.20; echo "peer exit: $?"
  ping -c1 -W2 8.8.8.8; echo "internet exit: $?"
} | tee ~/lab/level-2/lab-201/evidence/connectivity.txt
```

**Expected:** checks 1–4 succeed with output; check 5 fails with exit code 1 or 2 (`Network is unreachable`
or timeout). If check 5 succeeds, stop — your lab is not isolated.

## 6. Three failures and what they look like

| Symptom | Likely cause | How to confirm |
| --- | --- | --- |
| Peer ping fails, internet works | VMs on different host-only networks, or one is bridged | Compare network names in hypervisor settings |
| Address disappears after reboot | NetworkManager/netplan profile not persisted | `nmcli connection show`, `netplan get` |
| Ping works, service unreachable | Service bound to `127.0.0.1` | `ss -tlnp` on the target, check the bind address |

The third is the one that wastes afternoons: the network is fine, and the service is deliberately local. Bind
to the lab address (`192.0.2.20`) when a lab needs cross-host access, and say so in your notes.

---

## Practical exercises

### Exercise 1 — Version inventory (15 minutes)

```bash
for t in nmap tcpdump tshark nc python3 git ssh lynis; do
  printf '%-8s ' "$t"; command -v "$t" >/dev/null && "$t" --version 2>&1 | head -1 || echo "missing"
done
```

Record every version in your address register file. These are the versions your evidence was produced with,
and version differences explain most "it worked in the tutorial" problems.

### Exercise 2 — Adapter audit (10 minutes)

For each VM, list every adapter and its mode. Confirm none is bridged. Save the list.

### Exercise 3 — Address plan (10 minutes)

Design addresses for a fourth host (a deliberately vulnerable target) without overlapping the existing three.
Write the row you would add to the register, including the snapshot name.

### Exercise 4 — Break and observe (15 minutes)

Temporarily set the Kali address to `192.0.2.99/24`, re-run the matrix, and record what changed. Then restore
`192.0.2.10`. This teaches you what a wrong-subnet failure looks like before it wastes a lab.

## Expected observations and verification

- Both hosts have static addresses and no default route.
- The connectivity matrix is saved with exit codes.
- Internet reachability fails, and you can quote the exit code.
- Every tool version is recorded.
- You predicted what a wrong subnet would break, then confirmed it.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Importing the Kali image and leaving default credentials | Tutorials skip it | `passwd` immediately, then snapshot |
| Two host-only networks with similar names | Hypervisor defaults | Rename them clearly (`lab-net`) |
| Adding a gateway "so ping works" | Internet habit | Remove it; no gateway on an isolated segment |
| Using DHCP then hard-coding an address in a lab | Both at once | Disable DHCP on the host-only network |
| Forgetting to snapshot after setup | Eagerness | Snapshot as `kali-baseline` before any lab |
| Assuming `eth0` | Interface names vary | `ip -br link` first, always |

## Review questions

1. Why does an isolated lab deliberately have no default gateway?
2. What does a `ping` to a peer prove that `ip -br addr` does not?
3. Why record MAC addresses in an address register?
4. What are two reasons a service would be unreachable when the network is fine?
5. Why snapshot immediately after environment setup?

## Knowledge check

1. Which `nmcli` subcommand creates a static IPv4 profile?
2. What exit code does a blocked `ping` commonly return, and what does it mean?
3. Name two items an address register must contain.
4. What does `netplan apply` do, and when is it needed?
5. Why is a NAT adapter removed before scanning?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 3–5 if 1, 2 and 4 are uncertain.)*

## Summary

- Choose a Kali image for speed or the ISO for learning; change credentials and snapshot either way.
- Static addresses on one host-only segment, no gateway, documented in a register.
- Validate connectivity with a fixed matrix and save the evidence.
- Most lab failures are adapters, subnets, or services bound to loopback.
- Record tool versions; they are part of your evidence.

## Next lesson

[CYB-202 · Bash, Python and Git for Lab Work](../02-bash-python-git/index.md) — turning manual work into
repeatable scripts, safely.

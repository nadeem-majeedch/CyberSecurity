---
title: "Virtualization and Isolated Lab Design"
description: "Hypervisor types, adapter modes, snapshots and clones, isolation verification, and a reset procedure you can trust."
module_code: CYB-111
level: 1
kind: lesson
prerequisites: [CYB-110]
estimated_minutes: 120
difficulty: beginner
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [virtualization, isolation, snapshots, lab]
---

# Virtualization and Isolated Lab Design

## Learning objectives

By the end of this lesson you can:

1. Explain what a hypervisor does and distinguish type 1 from type 2.
2. Choose between host-only, NAT, and bridged networking, and justify the choice.
3. Verify isolation with commands whose output is evidence, not opinion.
4. Use snapshots and clones deliberately, and describe the cost of each.
5. Write a reset procedure that returns the lab to a known state.
6. Record an environment document that someone else could reproduce.

## Prerequisites

[CYB-110](../10-windows-powershell-basics/index.md), and a hypervisor installed
([Prerequisites](../../../start-here/prerequisites.md)).

---

## 1. What virtualization gives you

A hypervisor runs guest operating systems as processes on your machine, each believing it owns hardware.
For a security lab that buys four things:

- **Disposability.** Break it, revert it, try again.
- **Isolation.** A private network that nothing else can reach.
- **Multiplicity.** Several operating systems at once on one laptop.
- **Repeatability.** Snapshots make "same starting point" a fact rather than a hope.

| Type | Runs on | Examples | Notes |
| --- | --- | --- | --- |
| **Type 1** (bare metal) | Hardware directly | ESXi, Hyper-V Server, Proxmox | Production; better performance |
| **Type 2** (hosted) | Your OS | VirtualBox, VMware Workstation/Fusion, UTM | Right choice for a study lab |

**Containers are not VMs.** A container shares the host kernel, so a kernel exploit or a privileged
container escapes the boundary. For deliberately vulnerable software and malware analysis, use a VM.

## 2. Adapter modes: the decision that matters

| Mode | Guest can reach | Others can reach the guest | Use for |
| --- | --- | --- | --- |
| **Host-only** | Host and other guests on the same virtual network | No | All lab targets and all offensive testing |
| **NAT** | Internet (via host), host | No (unless port-forwarded) | Installing packages, updates |
| **Bridged** | The physical LAN | Yes — anything on your LAN | Rarely; only with a documented reason |
| **Internal network** | Other guests only | No | Strict isolation without host access |

The default for this course is **host-only**, with a NAT adapter added temporarily for package installation
and then removed. Bridged mode turns a deliberately vulnerable VM into a target for your entire home or
office network — the single most common lab mistake.

### Setting it up

**VirtualBox:** File → Tools → Network Manager → Host-only Networks → Create. Attach each VM under
Settings → Network → Adapter 1 → Host-only Adapter.

**VMware Workstation/Fusion:** Virtual Network Editor → add a host-only network (`vmnet1` by default).
Attach the VM's adapter to "Host-only".

**UTM (Apple silicon):** create a "Shared Network" (host-only equivalent) or "Emulated VLAN"; bridged is
available but should not be used here.

Static addressing avoids DHCP surprises:

```bash
# Ubuntu (netplan). Confirm the interface name with: ip -br link
sudo tee /etc/netplan/60-lab.yaml >/dev/null <<'YAML'
network:
  version: 2
  ethernets:
    enp0s8:
      addresses: [192.0.2.20/24]
YAML
sudo netplan apply
ip -br addr show
```

**Expected:**

```text
enp0s8           UP             192.0.2.20/24
```

## 3. Proving isolation

```bash
ip route show
ping -c 2 8.8.8.8
dig +short example.com
ping -c 2 192.0.2.30
```

| Check | Required result | What it proves |
| --- | --- | --- |
| `ip route show` | No default route via the lab interface | Traffic cannot leave the segment |
| `ping 8.8.8.8` | Fails (unreachable or timeout) | No internet path |
| `dig example.com` | Fails or times out | No working resolver path |
| `ping 192.0.2.30` | Succeeds | Guests can reach each other |

Save the output. "I checked" is not evidence; the transcript is, and future-you will want it when a lab
behaves strangely.

**Beware the silent bridge:** a VM with two adapters can look isolated while the second one is bridged.
List every adapter, not just the first.

## 4. Snapshots and clones

| Operation | What it does | Cost | When |
| --- | --- | --- | --- |
| **Snapshot** | Freezes state; later changes are stored as deltas | Disk grows with each snapshot | Before every lab; revert after |
| **Revert** | Returns to that state | Loses everything since | After evidence is saved |
| **Full clone** | Independent copy | Full disk space | New role, separate machine |
| **Linked clone** | Copy sharing the parent disk | Small, but depends on the parent | Many throwaway targets |

Rules that prevent pain:

- Snapshot **with the VM powered off** where possible ("clean" snapshots).
- Keep 3–4 snapshots per VM maximum; delete old ones.
- Snapshots are **not backups**: they live on the same disk and die with it.
- Never store VMs in a cloud-synced folder (OneDrive/Dropbox/iCloud) — sync clients corrupt disk images.
- After reverting, re-verify networking; an old snapshot may carry a stale adapter configuration.

## 5. A reset procedure you can trust

Write this down once, and follow it every time:

```text
Lab reset — lab-ubuntu
1. Save evidence outside the VM (text transcripts, hashes).
2. Power off the VM.
3. Revert to snapshot: pre-<lab-id> (or clean-base).
4. Power on; log in as the normal user.
5. Verify: hostname, ip -br addr, ping 8.8.8.8 fails, ping 192.0.2.30 succeeds.
6. Append to lab-log.md: date, lab id, snapshot used, anomalies.
```

A reset that takes two minutes means you will experiment. A reset that takes two hours means you will avoid
anything risky, which is the opposite of learning.

## 6. Document the environment

Create `lab-environment.md` once, keep it current:

| Field | Example |
| --- | --- |
| Host OS / version | Windows 11 23H2 |
| Hypervisor / version | VirtualBox 7.0.20 |
| Host RAM / free disk | 16 GB / 120 GB free |
| VMs | `lab-ubuntu` 192.0.2.20, `lab-win` 192.0.2.30 |
| Adapters | Both host-only `vboxnet0`; NAT removed after updates |
| Snapshots | `clean-base`, `pre-lab-111-01` |
| Isolation verified | 2026-10-28, transcript saved |

This document is what you paste into a bug report, a lab submission, or a forum question — and it is why
your problems become solvable.

---

## Practical exercises

### Exercise 1 — Adapter audit (10 minutes)

For each VM, list every adapter, its mode, and its MAC address (VirtualBox: Settings → Network → Advanced).
Answer: does any VM have a bridged adapter? If yes, why?

### Exercise 2 — Isolation transcript (10 minutes)

Run the four checks in section 3 and save the output to `evidence/isolation.txt`. Then change one adapter to
NAT and re-run the internet check. Record what changed, and change it back.

### Exercise 3 — Snapshot cost (10 minutes)

Record the VM's disk size, take a snapshot, delete a large file, and re-check the size. Explain the result in
one sentence. (VirtualBox: `VBoxManage list hdds`; VMware: datastore browser.)

### Exercise 4 — Linked versus full clone (15 minutes, optional)

If your hardware allows, create a linked clone and note how quickly it is created and how large it is. Then
delete it. This is the technique you will use for throwaway targets in Level 2.

## Expected observations and verification

- No VM has a bridged adapter.
- The isolation transcript shows internet checks failing and cross-VM checks succeeding.
- You can explain the difference between a snapshot and a backup in one sentence.
- Your `lab-environment.md` exists and matches reality.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Bridged adapter "just to install packages" | Convenience | Use NAT temporarily, then remove it |
| Snapshot before every command | Anxiety | Snapshot per lab, with the VM off |
| Snapshots never deleted | Nobody notices | Check disk use monthly; delete old chains |
| VM in OneDrive | Default folder choice | Move the VM directory outside sync folders |
| Reverting loses evidence | Evidence was inside the VM | Save transcripts to the host first |
| Assuming isolation from the hypervisor setting alone | Trust | Verify with commands and keep the output |

## Review questions

1. Why is a container unsuitable for malware analysis where a VM is suitable?
2. Which adapter mode should never be used for a deliberately vulnerable VM, and why?
3. What three checks prove a lab network is isolated?
4. Why are snapshots not backups?
5. What belongs in a lab environment document, and who uses it?
6. What does a two-minute reset procedure change about how you learn?

## Knowledge check

1. Which adapter mode exposes a guest to your physical LAN?
2. What does `ping 8.8.8.8` failing from a guest indicate?
3. Name one cost of keeping many snapshots.
4. What is the difference between a linked clone and a full clone?
5. Which directory should never contain VM disk images?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 2–4 if 1, 3 and 4 are uncertain.)*

## Summary

- A hosted hypervisor gives disposability, isolation, multiplicity, and repeatability — the four things a
  study lab needs.
- Host-only is the default; NAT is temporary for updates; bridged is a risk, not a convenience.
- Isolation is proved with commands and saved output, not assumed from a checkbox.
- Snapshots are per-lab reset points, not backups, and they cost disk.
- A written reset procedure and an environment document turn lab problems into solvable ones.

## Next lesson

[CYB-112 · Introduction to Kali Linux](../12-kali-linux/index.md) — the toolkit distribution, and when *not*
to use it.

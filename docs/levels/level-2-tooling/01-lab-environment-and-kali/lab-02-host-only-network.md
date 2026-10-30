---
title: "LAB-201-02 · Configure Host-Only Networking and Record Addresses"
description: "Create the isolated lab segment, assign static addresses to analyst and target, and produce an address register."
module_code: CYB-201
level: 2
kind: lab
prerequisites: [CYB-201]
estimated_minutes: 120
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-201-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, netplan, nmcli, lab]
---

# LAB-201-02 · Configure Host-Only Networking and Record Addresses

## Prerequisites

LAB-201-01 complete: a Kali VM that boots, is fully updated, and has a `clean-base` snapshot. A second VM
(Ubuntu Server) if you are building the full Level 2 topology rather than only the analyst host.

## Scenario and background

Before any enumeration can be meaningful, the lab needs a stable, documented address plan. You are setting up
a two-host segment — an analyst workstation and a target — on a private network with no route to the internet,
and recording the plan so that later results can be reproduced and explained.

## Learning objectives

By the end of this lab you can:

1. Create a host-only virtual network with DHCP disabled.
2. Assign static addresses on Kali (NetworkManager) and Ubuntu Server (netplan).
3. Record a complete address register including MAC addresses and snapshots.
4. Prove that no default route exists on the lab segment.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Hypervisor | VirtualBox 7.0.x / VMware | Host-only network support |
| Kali | 2024.x+ | `nmcli` (NetworkManager) |
| Ubuntu Server | 22.04.x | `netplan`, `iproute2` |

## Setup

1. Both VMs powered off, snapshotted (`kali-baseline`, `ubuntu-baseline`).
2. `lab-kali` and `lab-ubuntu` exist and boot.
3. Note your host-only network name from the hypervisor.

## Target addresses and lab topology

```
       192.0.2.0/24  (host-only, no gateway, DHCP disabled)
        ┌───────────────────────┴────────────────────────┐
  lab-kali 192.0.2.10/24                        lab-ubuntu 192.0.2.20/24
  (analyst, eth0)                               (target, enp0s8)
```

| Host | Role | Address | Reserved for later |
| --- | --- | --- | --- |
| `lab-kali` | Analyst | `192.0.2.10` | — |
| `lab-ubuntu` | Target / reference | `192.0.2.20` | — |
| `lab-win` | Optional | `192.0.2.30` | LAB-203-01 discovery |
| `lab-target` | Vulnerable services (Level 3) | `192.0.2.40` | DVWA, Juice Shop |

## Numbered commands and actions

### 1. Create the host-only network

**VirtualBox:** File → Tools → Network Manager → Host-only Networks → Create. Set IPv4 `192.0.2.1/24`,
DHCP **disabled**.

**VMware:** Virtual Network Editor → Add Network → host-only → subnet `192.0.2.0`, DHCP off.

**Why disable DHCP?** With static addresses assigned, a DHCP server can hand out a conflicting lease and you
would spend an hour guessing why a host changed address mid-lab.

### 2. Attach adapters

For each VM: Settings → Network → Adapter 1 → Host-only Adapter → select your network. Remove Adapter 2 if a
NAT adapter remains from setup.

### 3. Assign the analyst address (Kali, NetworkManager)

```bash
ip -br link
sudo nmcli connection show
sudo nmcli connection add type ethernet ifname eth0 con-name lab-static \
  ipv4.method manual ipv4.addresses 192.0.2.10/24 ipv4.gateway "" ipv6.method disabled
sudo nmcli connection up lab-static
ip -br addr show eth0
ip route
```

**Expected:**

```text
eth0             UP             192.0.2.10/24
```

`ip route` should show no `default via` line. If a default route appears, something else (a NAT adapter or
DHCP) is still active.

### 4. Assign the target address (Ubuntu, netplan)

```bash
ip -br link
sudo tee /etc/netplan/60-lab.yaml >/dev/null <<'YAML'
network:
  version: 2
  ethernets:
    enp0s8:
      addresses: [192.0.2.20/24]
YAML
sudo chmod 600 /etc/netplan/60-lab.yaml
sudo netplan apply
ip -br addr show enp0s8
```

**Expected:** `enp0s8 UP 192.0.2.20/24`. If the file is world-readable, netplan warns — hence the `chmod 600`.

### 5. Record MAC addresses

Kali and Ubuntu:

```bash
ip link show | grep -A1 "eth0\|enp0s8" | grep link/ether
```

or read them from the hypervisor's adapter settings. Paste them into the register.

### 6. Persistence check

Reboot both guests and re-check:

```bash
ip -br addr show
ip route
```

**Expected:** the same address, still no default route. A configuration that does not survive a reboot is not a
configuration.

### 7. Write the address register

Create `~/lab/level-2/address-register.md`:

| Host | Role | Interface | Address | MAC | Snapshot | Network | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| lab-kali | Analyst | | | | | | |
| lab-ubuntu | Target | | | | | | |

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `ipv4.method manual` | Static configuration | DHCP could reassign addresses |
| `ipv4.gateway ""` | No gateway | Prevents traffic leaving the isolated segment |
| `ipv6.method disabled` | No IPv6 on this profile | Avoids surprise link-local reachability |
| `con-name` | Profile name | One predictable profile to inspect or remove |
| `chmod 600` on netplan | Restrict config permissions | Netplan warns on world-readable files |

## Expected observations

- The host-only network exists with `192.0.2.0/24` and DHCP disabled.
- Kali is `192.0.2.10/24` with no default route.
- Ubuntu is `192.0.2.20/24` with no default route.
- Both addresses survive a reboot.
- The register lists MAC addresses and snapshot names.

## Verification criteria

- [ ] `ip -br addr` on both hosts shows the planned addresses.
- [ ] `ip route` shows no `default via` on either host.
- [ ] MAC addresses recorded for both adapters.
- [ ] Addresses persist after reboot (evidence captured twice).
- [ ] Register committed to your notes folder (not yet to Git — that is LAB-202-03).

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `nmcli: device 'eth0' not found` | Interface name differs | Use the name from `ip -br link` |
| Old DHCP profile keeps overriding | Two profiles active | `nmcli connection show`, then delete the stale profile |
| Netplan warns "Permissions for file are too open" | Mode not 600 | `sudo chmod 600 /etc/netplan/60-lab.yaml` |
| Address reverts after reboot | Netplan file name ordering, or NetworkManager managing the interface | Check `netplan get` and `nmcli device status` |
| Both hosts have `192.0.2.x` but cannot ping | Different host-only networks | Compare network names in the hypervisor |
| `ip route` shows a default route | NAT adapter still attached | Remove or disable Adapter 2 |

## Cleanup and restoration

Keep this configuration — the rest of Level 2 depends on it. To rebuild from scratch:

```bash
# Kali
sudo nmcli connection delete lab-static

# Ubuntu
sudo rm /etc/netplan/60-lab.yaml && sudo netplan apply
```

Then revert both VMs to their baselines and repeat the lab. Do not leave a NAT adapter enabled "just in case";
that is how isolation quietly disappears.

## Questions and extension challenges

1. Why does eliminating the default route matter more than merely "not using" the internet in a lab?
2. What could cause a static address to persist but the *interface name* to change, and what would break?
3. **Extension:** add a third host on `192.0.2.30` and a DHCP server on `192.0.2.1` that hands out addresses
   only in `192.0.2.128–192.0.2.160`. Explain why that range is safe alongside static assignments.
4. **Extension:** write a one-paragraph explanation of why `192.0.2.0/24` appears throughout this course instead
   of `192.168.1.0/24`.

## Related

- [Preparing the Analyst Environment](01-lab-environment.md)
- [LAB-201-03 · Validate Connectivity](lab-03-connectivity-validation.md)
- [Labs](../../../labs/index.md)

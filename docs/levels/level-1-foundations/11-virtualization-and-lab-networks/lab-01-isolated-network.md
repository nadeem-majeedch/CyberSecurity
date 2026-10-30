---
title: "LAB-111-01 · Build and Verify an Isolated Network"
description: "Create a host-only virtual network, place two VMs on it, and prove isolation with saved evidence."
module_code: CYB-111
level: 1
kind: lab
prerequisites: [CYB-111]
estimated_minutes: 60
difficulty: beginner
safety: isolated-vm
lab_ids: [LAB-111-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [virtualization, isolation, networking, lab]
---

# LAB-111-01 · Build and Verify an Isolated Network

**Module:** CYB-111 · **Time:** 60 minutes · **Safety:** isolated-vm · **Snapshot:** `pre-lab-111-01`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** your own virtual machines, on a host-only virtual network you create.
    **Targets you must not use:** hosts on your physical network, your university or employer network, or
    any public system.

    You will change adapter settings on your own VMs. Do this with the VMs powered off, and confirm no
    adapter is bridged when you finish.

## Objective

Create a host-only virtual network, attach `lab-ubuntu` and `lab-win`, assign static documentation-range
addresses, and produce a transcript proving the segment is isolated from the internet but functional
between guests.

## Threat model

A misconfigured adapter is the most common way a study lab becomes a real exposure. This lab exists to make
that failure visible and to leave evidence that it did not happen.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-ubuntu` | Guest 1 | `192.0.2.20/24` |
| `lab-win` | Guest 2 | `192.0.2.30/24` |
| Virtual network | Host-only | `192.0.2.0/24`, no DHCP |

## Before you start

1. Power off both VMs.
2. Take a snapshot of each named `pre-lab-111-01`.
3. Confirm host free disk: at least 10 GB.

## Procedure

### Step 1 — Create the host-only network

**VirtualBox:** File → Tools → Network Manager → Host-only Networks → **Create**. Note the name (usually
`vboxnet0`) and set:

- IPv4 address `192.0.2.1`, mask `255.255.255.0`
- DHCP server: **disabled**
- Adapter: enabled

**VMware:** Virtual Network Editor → Add Network → `vmnet1` → host-only → subnet `192.0.2.0/24`, DHCP off.

**Verified by:** the network appears in the manager with the address you set. Record a screenshot or the
manager text in `evidence/network-created.txt`.

### Step 2 — Attach the adapters

For each VM: Settings → Network → Adapter 1 → **Host-only Adapter** → select the network. Remove or disable
Adapter 2 (NAT) if present.

### Step 3 — Configure static addressing

On `lab-ubuntu`, confirm the interface name and apply netplan:

```bash
ip -br link
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

**Expected:** `enp0s8 UP 192.0.2.20/24` (interface name may be `enp0s3` or `ens33`; use yours).

On `lab-win`, in an elevated PowerShell:

```powershell
Get-NetAdapter | Select-Object Name, Status, MacAddress
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.0.2.30 -PrefixLength 24
Get-NetIPAddress -AddressFamily IPv4 | Select-Object InterfaceAlias, IPAddress
```

**Expected:** `192.0.2.30` on the lab adapter. (If your adapter is named differently, use that name.)

### Step 4 — Verify isolation

On `lab-ubuntu`:

```bash
mkdir -p ~/cyber/level-1/lab-111-01/evidence
cd ~/cyber/level-1/lab-111-01/evidence
{
  echo "=== hostname ==="; hostname
  echo "=== routes ==="; ip route show
  echo "=== internet check (must fail) ==="; ping -c 2 -W 2 8.8.8.8; echo "exit: $?"
  echo "=== dns check (must fail) ==="; dig +short example.com; echo "exit: $?"
  echo "=== peer check (must succeed) ==="; ping -c 2 -W 2 192.0.2.30; echo "exit: $?"
} | tee isolation.txt
```

**Expected:**

- Internet ping fails, exit non-zero.
- DNS lookup fails or returns nothing.
- Peer ping succeeds with `2 received`.

On `lab-win`:

```powershell
Test-NetConnection -ComputerName 192.0.2.20 -InformationLevel Detailed | Select-Object ComputerName, PingSucceeded
Test-NetConnection -ComputerName 8.8.8.8 -InformationLevel Quiet
```

**Expected:** `PingSucceeded : True` for the peer, `False` for `8.8.8.8`.

### Step 5 — Reset the Windows VM to a known state

Power off `lab-win`, take a snapshot named `isolated-net-verified`, and power on. Re-run the peer check —
this proves your reset point preserves networking.

### Step 6 — Document the environment

Create `lab-environment.md`:

| Field | Your value |
| --- | --- |
| Host OS / version | |
| Hypervisor / version | |
| Virtual network name and subnet | |
| Guest addresses | |
| DHCP on virtual network | disabled |
| Snapshots | |
| Isolation verified (date) | |

## Evidence to collect

`evidence/network-created.txt`, `evidence/isolation.txt`, the Windows `Test-NetConnection` output, and
`lab-environment.md`.

## Verification

- [ ] The host-only network exists with `192.0.2.0/24` and DHCP disabled.
- [ ] Both guests have static addresses in that range.
- [ ] Internet and DNS checks fail from the Linux guest.
- [ ] Peer-to-peer checks succeed in both directions.
- [ ] No adapter on either VM is bridged.
- [ ] A snapshot named `isolated-net-verified` exists.

## Teardown and reset

The lab's end state is the desired state for the rest of the course, so there is nothing to undo. If you
want a clean slate:

```bash
# On lab-ubuntu: remove the static config and fall back to DHCP
sudo rm /etc/netplan/60-lab.yaml && sudo netplan apply
```

```powershell
# On lab-win
Remove-NetIPAddress -IPAddress 192.0.2.30 -Confirm:$false
```

Revert both VMs to `pre-lab-111-01` if you prefer to start over; then re-run the lab from step 1.

## Reflection

1. Why is `192.0.2.0/24` a better choice than `192.168.56.0/24` for course labs?
2. What makes `ping 8.8.8.8` a better isolation test than checking the hypervisor setting?
3. Why disable DHCP on the host-only network when you are assigning static addresses?
4. If peer ping succeeds but internet ping also succeeds, what is the most likely configuration error?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Network created but checks inconclusive | Isolation and peer checks both demonstrated | Both directions verified, with snapshots and documented state |
| Methodology | Adapters changed at random | Sequential attachment and addressing | Explains each adapter's purpose and why it is needed |
| Evidence | No saved output | Transcript saved | Transcript with exit codes, dates, and environment record |
| Safety | Bridged adapter left enabled | Host-only only | Host-only, verified, with a note on the bridged risk |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Guests cannot see each other | Different host-only networks | Attach both to the same network name |
| `192.0.2.20` applied but disappears after reboot | Netplan file not read (wrong interface name) | `ip -br link`, correct the name, re-apply |
| Internet still reachable | NAT adapter present on adapter 2 | Disable or remove it |
| Windows IP assignment fails | Adapter alias wrong | `Get-NetAdapter` for the exact name |
| `netplan apply` warns about permissions | File mode too open | `sudo chmod 600 /etc/netplan/60-lab.yaml` |
| Peer ping works, but ports are unreachable | Service bound to `127.0.0.1` | Bind to the lab address when the lab requires cross-host access |

## Related

- [Virtualization and Isolated Lab Design](01-virtualization-lab-design.md)
- [Lab Safety Guide](../../../start-here/lab-safety.md)
- [Labs](../../../labs/index.md)

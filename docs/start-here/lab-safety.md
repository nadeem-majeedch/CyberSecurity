# Lab Safety Guide

Every practical exercise in this course happens inside a lab you control. This guide shows you how to
build that lab, prove it is isolated, and reset it when (not if) you break it.

The **rules** are in the [Safety Policy](../policies/safety-policy.md). This page is the **how**.

---

## The model

```
        ┌──────────────────── Host machine (your laptop/desktop) ────────────────────┐
        │  Hypervisor (VirtualBox / VMware)                                          │
        │                                                                            │
        │   ┌──────────────┐        host-only network        ┌──────────────────┐   │
        │   │  attacker VM │◀────── 192.0.2.0/24 ──────────▶│   target VM      │   │
        │   │  (Kali/Ubu)  │        no internet route       │  (DVWA, Ubuntu)  │   │
        │   └──────────────┘                                 └──────────────────┘   │
        │          │                                                                 │
        └──────────┼─────────────────────────────────────────────────────────────────┘
                   │  optional NAT adapter, only when you need updates
                   ▼
              internet  (never used as a test target)
```

Two principles:

1. **The lab network is private.** VMs talk to each other on a host-only segment; nothing on that
   segment is reachable from your home network or the internet.
2. **The internet is for installing things, not for testing them.** You may patch a VM. You may not
   aim a scanner at anything outside the lab.

---

## Choosing the right network mode

| Mode | What it does | Use it for | Risk |
| --- | --- | --- | --- |
| **Host-only** | VMs see the host and each other; no route to the internet | All scanning, exploitation, and vulnerable services | None to others — this is the default |
| **NAT** | VMs reach the internet through the host, but are not reachable from outside | Installing packages, updates | Vulnerable services can reach out; keep them bound to localhost |
| **Bridged** | VM appears as a peer on your physical network | Rarely, and only with a documented reason | **High** — a vulnerable VM becomes reachable by your whole network. Avoid |

If an exercise ever seems to require bridged mode, treat that as a lab defect and report it.

---

## Building the lab (first time)

### 1. Plan the addresses

Use documentation ranges so nothing you type can ever be a real host:

| Role | Example address |
| --- | --- |
| Analyst/attacker VM | `192.0.2.10/24` |
| Target VM | `192.0.2.20/24` |
| Second target (later levels) | `192.0.2.30/24` |

`192.0.2.0/24`, `198.51.100.0/24`, and `203.0.113.0/24` are reserved for documentation (RFC 5737).
They will never belong to someone else, so a typo cannot scan a stranger's system.

### 2. Create the host-only network

VirtualBox: **File → Tools → Network Manager → Host-only Networks → Create**. Note the adapter name
and disable the DHCP server unless you want automatic addressing.

### 3. Attach each VM

For every lab VM: **Settings → Network → Adapter 1 → Host-only Adapter →** select your network.
Add a second adapter in NAT mode only when the VM needs updates, and disable it afterwards.

### 4. Configure static addresses in the guest

```bash
# Ubuntu (netplan). Replace the interface name with yours (ip -br link)
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

### 5. Bind vulnerable applications to localhost

```bash
# Correct: reachable only from inside this VM
python3 -m http.server 8080 --bind 127.0.0.1

# Wrong for a lab: exposed on every interface
python3 -m http.server 8080 --bind 0.0.0.0
```

When a lab genuinely needs two VMs to talk, bind to the host-only address, never `0.0.0.0` on a NAT or
bridged adapter.

---

## Prove isolation before you test

Run these checks and paste the output into your notes. **Every lab in this course starts here.**

```bash
# 1. Confirm the lab address and that no default route exists on the lab interface
ip -br addr show
ip route show

# 2. This MUST fail (blocked or no route). If it succeeds, you are not isolated.
ping -c 2 8.8.8.8

# 3. This MUST fail: no DNS resolution to the outside
dig +short example.com

# 4. Confirm the target is reachable from the analyst VM only
ping -c 2 192.0.2.20
```

Expected outcome:

- Checks 2 and 3 fail with "Network is unreachable" or a timeout.
- Check 4 succeeds.
- The target VM's service is reachable from the analyst VM and **not** from your phone or another
  machine on your home network.

If check 2 succeeds, stop: disable the NAT adapter, re-run, and do not proceed until it fails.

---

## Snapshots: your reset button

| When | Action |
| --- | --- |
| After a clean OS install and updates | Snapshot `clean-base` |
| Before each lab | Snapshot `pre-<lab-id>` |
| After a lab, once evidence is saved | Revert to `pre-<lab-id>` |
| Before a risky step inside a lab | Snapshot `mid-<lab-id>` if the lab is long |

Rules:

- Snapshots are not backups. They live on the same disk and grow.
- Keep at most 3–4 per VM; delete old ones to reclaim space.
- Take snapshots **with the VM powered off** ("clean" snapshots) for reliability.
- Never store personal files in a VM you will revert.

---

## Evidence hygiene

- Capture output as **text** wherever possible; screenshots only for GUI-only steps.
- Scrub secrets, tokens, and real personal data before saving anything you might share.
- Keep evidence inside `notes/level-N/module/evidence/`, dated.
- If you must handle a genuinely suspicious file (Level 5), it never leaves the isolated VM.

---

## Which lab do you need, by level?

| Level | Lab shape | Notes |
| --- | --- | --- |
| 1 | Ubuntu Server + Windows VM on a host-only segment | No vulnerable services needed yet; you are learning administration |
| 2 | Add an analyst VM (Kali) and a target VM with common services | All scanning stays inside `192.0.2.0/24` |
| 3 | Add DVWA and OWASP Juice Shop, bound to localhost or the lab interface | Web testing against your own apps only |
| 4 | Add a logging/monitoring VM (Wazuh or ELK) and optionally Suricata/Zeek | Detection labs generate traffic inside the lab |
| 5 | Add an AD lab (instructor-provided build), a cloud sandbox account, and a malware-analysis VM | Malware VM has no network and no shared folders |

A canonical, version-pinned specification is maintained on the [Labs](../labs/index.md) page.

---

## Teardown and reset

After each lab:

1. Save evidence outside the VM.
2. Revert to `pre-<lab-id>`.
3. Confirm the VM still boots and networking is as expected.
4. Update your lab log: date, lab ID, snapshot reverted, anything anomalous.

Before a long break, revert every VM to `clean-base` and shut them down. A dormant vulnerable VM with
a bridged adapter is exactly the mistake that turns a study lab into an incident.

---

## If something goes wrong

| Situation | Do this |
| --- | --- |
| You accidentally scanned or touched something outside the lab | Stop immediately. Do not hide it. Record time, target, command. Report the same day — see [policy §10](../policies/safety-policy.md#10-if-something-goes-wrong) |
| A vulnerable VM is reachable from your home network | Disconnect the adapter now, then investigate the network configuration |
| A lab VM becomes unstable or unbootable | Revert the snapshot; if that fails, rebuild from the documented steps |
| You find what appears to be a real vulnerability in a real system | Do not test further. Report to the instructor, who will handle disclosure |

---

## Pre-lab checklist

- [ ] Host-only adapter attached; NAT disabled unless installing packages.
- [ ] Static lab address set; no default route on the lab interface.
- [ ] `ping 8.8.8.8` fails; `ping <target>` succeeds.
- [ ] Vulnerable services bound to localhost or the lab interface only.
- [ ] `pre-<lab-id>` snapshot taken.
- [ ] Evidence folder created and dated.
- [ ] Lab scope (in-scope and out-of-scope targets) read and understood.

---

## Related

- [Safety Policy](../policies/safety-policy.md) — the binding rules and prohibitions
- [Prerequisites and Setup](prerequisites.md) — installing the hypervisor and base VMs
- [Troubleshooting](troubleshooting.md) — when networking or a VM misbehaves
- [Labs](../labs/index.md) — the canonical lab environment specification

---
title: "LAB-110-01 · Inspect a Windows Host"
description: "Document accounts, groups, services, listening ports and event log evidence on your own Windows lab VM."
module_code: CYB-110
level: 1
kind: lab
prerequisites: [CYB-110]
estimated_minutes: 60
difficulty: beginner
safety: local-only
lab_ids: [LAB-110-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [windows, powershell, event-logs, hardening]
---

# LAB-110-01 · Inspect a Windows Host

**Module:** CYB-110 · **Time:** 60 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-110-01`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** your own `lab-win` VM, on the host-only lab network.
    **Targets you must not use:** your physical machine's Windows installation, any work or university
    device, or any other host on any network.

    You will read configuration and logs, create one account, then delete it. Nothing here touches another
    system.

## Objective

Produce an inventory of a Windows host — accounts, privileged groups, running services, listening ports and
recent security events — and identify three settings you would change before exposing such a host to a
network.

## Threat model

None. Read-only inspection plus one temporary local account used to observe how account creation is logged.

## Environment

| Host | Role | Notes |
| --- | --- | --- |
| `lab-win` | Target | Windows 11/10 evaluation VM, workgroup, host-only adapter |
| `lab-ubuntu` | Hash comparison | Optional; reusable for the cross-platform hash check |

## Before you start

```powershell
hostname
[Environment]::OSVersion.Version
whoami
```

Confirm you are in the VM. Take a snapshot named `pre-lab-110-01`.

## Procedure

### Step 1 — Evidence folder

```powershell
New-Item -ItemType Directory -Force "$HOME\cyber\level-1\lab-110-01\evidence" | Out-Null
Set-Location "$HOME\cyber\level-1\lab-110-01"
```

### Step 2 — Accounts and privileged groups

```powershell
Get-LocalUser | Select-Object Name, Enabled, LastLogon, PasswordRequired |
  Out-File evidence\users.txt
Get-LocalGroupMember -Group Administrators | Out-File evidence\admins.txt -Append
Get-Content evidence\users.txt
Get-Content evidence\admins.txt
```

**Expected:** a list including `Administrator` (usually disabled), your account, `DefaultAccount`, `Guest`
(disabled), and the members of Administrators. Record which accounts are *enabled* — enabled-but-unused
accounts are a standard audit finding.

### Step 3 — Services and their start modes

```powershell
Get-Service |
  Where-Object {$_.Status -eq 'Running'} |
  Sort-Object DisplayName |
  Select-Object -First 20 Name, DisplayName, StartType |
  Out-File evidence\services.txt
Get-Content evidence\services.txt
```

Answer in your notes: which of these services does the VM need? Any service you cannot justify is a
candidate for disabling — but do not disable anything in this lab. Disabling services is a hardening change
you will verify properly in Level 4.

### Step 4 — Listening ports and their processes

```powershell
Get-NetTCPConnection -State Listen |
  Select-Object LocalAddress, LocalPort, OwningProcess |
  Sort-Object LocalPort |
  Out-File evidence\ports.txt
Get-Content evidence\ports.txt | Select-Object -First 20

# Resolve the top listeners to process names and paths
Get-NetTCPConnection -State Listen |
  Select-Object -First 8 LocalPort, OwningProcess |
  ForEach-Object {
    $p = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    [pscustomobject]@{ Port = $_.LocalPort; PID = $_.OwningProcess; Process = $p.ProcessName; Path = $p.Path }
  } | Format-Table -AutoSize
```

**Expected:** ports such as 135, 445, 3389 (if RDP is enabled), and several high-numbered dynamic ports.
Flag in your notes every listener bound to `0.0.0.0` or `::` (all interfaces) and ask whether it needs to
be.

### Step 5 — Observe account creation in the event log

```powershell
New-LocalUser -Name labtemp -NoPassword -Description "LAB-110-01 temporary"
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4720} -MaxEvents 5 |
  Format-List TimeCreated, Id, Message |
  Out-File evidence\event-4720.txt
Get-Content evidence\event-4720.txt | Select-Object -First 25
```

**Expected:** event ID 4720 (a user account was created), naming `labtemp` and the acting account.

If no events appear, note that in your findings — it means this audit category is not enabled, which is a
finding in itself, not a failure of the lab.

### Step 6 — Failed logon evidence

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 3 |
  Format-List TimeCreated, Id, Message
```

Record whether any 4625 events exist and whether auditing is enabled for them.

### Step 7 — Cross-platform hash check

```powershell
"same content" | Out-File -Encoding ascii "$HOME\cyber\level-1\lab-110-01\same.txt"
(Get-FileHash "$HOME\cyber\level-1\lab-110-01\same.txt" -Algorithm SHA256).Hash |
  Tee-Object evidence\hash.txt
```

Compare with Linux — the same file content must produce the same digest. On `lab-ubuntu`:

```bash
printf 'same content\n' > /tmp/same.txt
sha256sum /tmp/same.txt
```

**Expected:** identical 64-character values. If they differ, the bytes differ — check encoding and line
endings (`Format-Hex` on Windows, `xxd` on Linux) rather than assuming the hash function is at fault.

### Step 8 — Write the hardening findings

Create `findings.md` with three rows:

| Finding | Evidence | Recommended change | Risk if unchanged |
| --- | --- | --- | --- |
| | | | |

Candidate findings, if they apply to your VM: an enabled unused account; a listener on all interfaces;
PowerShell logging not enabled; SMBv1 present; RDP reachable.

## Evidence to collect

`evidence/users.txt`, `evidence/admins.txt`, `evidence/services.txt`, `evidence/ports.txt`,
`evidence/event-4720.txt`, `evidence/hash.txt`, and `findings.md`.

## Verification

- [ ] Enabled accounts and Administrators members are listed.
- [ ] Running services are listed with start types.
- [ ] Every listening port has an owning process and path.
- [ ] Account creation produced event 4720, or you documented that auditing is off.
- [ ] The SHA-256 digest matches the Linux result.
- [ ] Three findings have evidence and a recommended change.

## Teardown and reset

```powershell
Remove-LocalUser -Name labtemp
Remove-Item -Recurse -Force "$HOME\cyber\level-1\lab-110-01\same.txt" -ErrorAction SilentlyContinue
Get-LocalUser | Where-Object Name -eq labtemp   # should return nothing
```

Revert to `pre-lab-110-01` if you changed any service, port, or policy setting — the lab does not require it.

## Reflection

1. Which enabled account on your VM would you disable first, and why?
2. Why does a listener on `0.0.0.0` create more risk than one on `127.0.0.1`?
3. What does "no 4625 events" tell you: no failures, or no auditing? How would you distinguish?
4. Why is the same SHA-256 value evidence of identical content rather than identical files?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Lists incomplete | Complete inventory with processes resolved | Findings tied to evidence with justified remediation |
| Methodology | Scrolled event logs | Filtered by event ID | Chose IDs deliberately and noted auditing gaps |
| Evidence | Unsaved output | Six artefacts saved | Annotated, reproducible, with hash comparison documented |
| Safety | Inspected the physical host | Stayed in the lab VM | Stayed in the VM and cleaned up the temporary account |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Get-WinEvent` access denied | Security log needs elevation | Run the shell elevated |
| No 4720 event | Auditing category disabled | Record it as a finding; continue |
| `Get-NetTCPConnection` not recognised | Very old PowerShell or module missing | Use `netstat -ano` and map with `tasklist` |
| Hashes differ | Different bytes or encoding | Compare with `Format-Hex` / `xxd` |
| `Remove-LocalUser` fails | Account still in use | Log off the session, then retry |
| `New-LocalUser` requires password policy | Policy enforced | Add `-Password (ConvertTo-SecureString ...)` or disable the policy in the VM only |

## Related

- [The Windows Security Model and PowerShell](01-windows-powershell.md)
- [Introduction to Cryptography, Hashing and Digital Signatures](../13-cryptography-hashing-signatures/index.md)
- [Safety Policy](../../../policies/safety-policy.md)

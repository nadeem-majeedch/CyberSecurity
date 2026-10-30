---
title: "LAB-502-01 · Build the Isolated Domain"
description: "Stand up a single-domain lab on an internal-only network: promote a DC, seed realistic objects, join a client, and prove there is no route out."
module_code: CYB-502
level: 5
kind: lab
prerequisites: [CYB-502]
estimated_minutes: 240
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-502-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [active-directory, windows-server, domain-controller, isolation, powershell]
---

# LAB-502-01 · Build the Isolated Domain

## Scenario and background

You need a domain that behaves like a real one and cannot reach anything real. That means a domain controller, a
joined client, a small but realistic set of users and groups, and a service account with an SPN — because the
weaknesses in the next lab need something to be weak.

The isolation proof comes first. A domain controller on a bridged adapter is the single most dangerous mistake in this
course.

## Learning objectives

1. Build a Windows Server 2025 evaluation domain controller on an internal-only network.
2. Create an OU structure, users, groups and a service account with an SPN.
3. Join a Windows client and verify Kerberos authentication.
4. Prove isolation with routing and connectivity tests.
5. Snapshot a known-good baseline and record the environment.

## Required tools and versions

| Component | Version | Notes |
| --- | --- | --- |
| Windows Server | 2025 Evaluation | 180-day evaluation; registration required |
| Windows 11 | 23H2+ | Client |
| Hypervisor | VirtualBox 7.x or equivalent | Internal network or host-only only |

!!! warning "Authorized scope — read before you begin"
    **This domain is `lab.local` and exists only on an internal virtual network.** No NAT, no bridged adapter, no
    route to any other network after activation.

    **Activation needs internet.** Attach NAT only for activation and updates, then **remove the adapter** and
    re-verify isolation before creating any accounts. Do not leave NAT attached "just in case".

    **Never join a real forest or reuse real credentials.** The passwords in this lab are training values.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The domain exists to be attacked safely. The relevant risk in *this* lab is environmental: an isolated-intent VM that
is actually reachable, or a domain that trusts something outside itself. Both are checked explicitly before the next
lab.

## Environment

| Host | Role | Address | RAM |
| --- | --- | --- | --- |
| `DC01` | Domain controller, DNS | 192.0.2.60/24, gateway none | 4 GB |
| `WS01` | Joined client | 192.0.2.61/24, gateway none | 4 GB |
| `lab-siem` | Optional collector | 192.0.2.30 | 8 GB, not running concurrently |

Network: VirtualBox **internal network** `lab-ad`, or host-only with the host adapter disabled.

## Procedure

### 1. Install and activate, then isolate

1. Install Windows Server 2025 (Desktop Experience).
2. Attach NAT, activate, install updates. Confirm activation:

```powershell
slmgr /xpr
```

**Expected:** a permanent or evaluation expiration message. If activation fails, resolve it now — the evaluation
requires activation within 10 days.

3. **Shut down, remove the NAT adapter, add the internal adapter, start.**
4. Set the static address and DNS:

```powershell
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.0.2.60 -PrefixLength 24
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses 127.0.0.1
Rename-Computer -NewName DC01 -Restart
Get-NetIPConfiguration
Get-NetRoute -DestinationPrefix "0.0.0.0/0"
```

**Expected:** one address, DNS pointing at itself, and **no default route**. An empty `Get-NetRoute` result is the
proof that there is no path out.

### 2. Promote the domain controller

```powershell
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
Install-ADDSForest `
  -DomainName "lab.local" `
  -DomainNetbiosName "LAB" `
  -InstallDns `
  -SafeModeAdministratorPassword (Read-Host -AsSecureString "DSRM password") `
  -Force
```

The server reboots. Log in as `LAB\Administrator`.

```powershell
Get-ADDomain | Select-Object DNSRoot, NetBIOSName, DomainMode
Get-ADForest | Select-Object Name, ForestMode
dcdiag /test:dns /v:yes | Select-String "PASS|FAIL" | Select-Object -First 10
```

**Expected:** `lab.local`, functional levels reported, and DNS tests passing. `dcdiag` failures here will make every
later lab confusing — fix them before continuing.

### 3. Seed a realistic structure

```powershell
Import-Module ActiveDirectory

$root = "DC=lab,DC=local"

New-ADOrganizationalUnit -Name "Users" -Path $root
New-ADOrganizationalUnit -Name "Workstations" -Path $root
New-ADOrganizationalUnit -Name "Servers" -Path $root
New-ADOrganizationalUnit -Name "ServiceAccounts" -Path $root
New-ADOrganizationalUnit -Name "Tier0" -Path $root

$pw = ConvertTo-SecureString "Lab502-Training-Only!" -AsPlainText -Force

New-ADUser -Name "Ayesha Khan" -SamAccountName "a.khan" -UserPrincipalName "a.khan@lab.local" `
  -Path "OU=Users,$root" -AccountPassword $pw -Enabled $true
New-ADUser -Name "Raza Hassan" -SamAccountName "r.hassan" -UserPrincipalName "r.hassan@lab.local" `
  -Path "OU=Users,$root" -AccountPassword $pw -Enabled $true
New-ADUser -Name "Helpdesk" -SamAccountName "helpdesk1" -UserPrincipalName "helpdesk1@lab.local" `
  -Path "OU=Users,$root" -AccountPassword $pw -Enabled $true

New-ADGroup -Name "Helpdesk" -GroupScope Global -Path "OU=Users,$root"
New-ADGroup -Name "Server Admins" -GroupScope Global -Path "OU=Users,$root"
Add-ADGroupMember -Identity "Helpdesk" -Members "helpdesk1"
Add-ADGroupMember -Identity "Server Admins" -Members "r.hassan"

# Service account with an SPN: the deliberate Kerberoasting target for LAB-502-02
New-ADUser -Name "svc-sql" -SamAccountName "svc-sql" -UserPrincipalName "svc-sql@lab.local" `
  -Path "OU=ServiceAccounts,$root" -AccountPassword $pw -Enabled $true `
  -Description "SQL service account (training)"
Set-ADUser -Identity "svc-sql" -ServicePrincipalNames @{Add="MSSQLSvc/sql01.lab.local:1433"}

Get-ADUser -Filter * -SearchBase $root | Select-Object SamAccountName, Enabled
Get-ADUser svc-sql -Properties ServicePrincipalNames | Select-Object -ExpandProperty ServicePrincipalNames
```

**Expected:** five users in the tree, two group memberships, and one SPN on `svc-sql`.

**Why this shape:** a helpdesk group, a server-admin group and a service account with an SPN are enough to produce a
real privilege path in the next lab without inventing an unrealistic enterprise.

### 4. Join the client

On `WS01` (NAT removed, internal adapter set to 192.0.2.61, DNS 192.0.2.60):

```powershell
Add-Computer -DomainName "lab.local" -Credential (Get-Credential LAB\Administrator) -Restart
```

After reboot, log in as `LAB\a.khan` and verify Kerberos:

```powershell
whoami /fqdn
klist
nltest /dsgetdc:lab.local
```

**Expected:** the FQDN of the user, a cached TGT in `klist`, and `DC01` returned as the domain controller.

### 5. Prove isolation

On both hosts:

```powershell
Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Format-Table
Test-NetConnection 8.8.8.8 -Port 443 -InformationLevel Quiet
Test-NetConnection 192.0.2.60 -Port 389 -InformationLevel Quiet
```

**Expected:** no default route, `False` for the internet test, `True` for LDAP on the DC. Record the output with the
date in `isolation.md`.

Also confirm the hypervisor: the VM has **one** adapter, attached to the internal network, not bridged.

### 6. Snapshot and record

Snapshot `ad-clean` and record:

| Item | Value |
| --- | --- |
| DC name / address | |
| Domain / NetBIOS | `lab.local` / `LAB` |
| DSRM password location | your lab password manager (not in this file) |
| Client name / address | |
| Evaluation expiry | |
| Snapshot names | `ad-clean` (both VMs) |

## Evidence to collect

- `build.md` — commands used, outputs, and any deviations.
- `isolation.md` — route table, connectivity tests, adapter configuration.
- `objects.txt` — `Get-ADUser`, `Get-ADGroupMember`, SPN output.
- `dcdiag.txt`, `klist.txt`, `nltest.txt`.
- Snapshot list.

## Verification

- [ ] Server activated before isolation; NAT removed afterwards.
- [ ] No default route on either host; internet test fails; LDAP to DC succeeds.
- [ ] `dcdiag` DNS tests pass.
- [ ] OU structure, five users, two groups and one SPN exist.
- [ ] Client joined and authenticating with Kerberos (`klist` shows a TGT).
- [ ] DSRM password stored outside the repository.
- [ ] Snapshots taken and named.

## Teardown and reset

Revert both VMs to `ad-clean` to remove anything from later labs. Do not delete the VMs — the module depends on them.

## Reflection

1. Why does the domain controller point DNS at itself, and what breaks if it points elsewhere?
2. The service account has a 20-character password. Why is it still a Kerberoasting target in a real environment?
3. What would you check first if `klist` on the client showed NTLM instead of Kerberos?
4. Your evaluation expires in 180 days. What happens to the lab, and how would you plan for it?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Build | DC promoted, DNS unreliable | Domain healthy, client joined | `dcdiag` clean, structure deliberate, deviations recorded |
| Isolation | Adapter left on NAT | Internal only | Route and connectivity proof recorded on both hosts |
| Objects | Users created | Groups and SPN present | Structure supports the next lab's findings, documented |
| Hygiene | Passwords in notes | DSRM stored safely | Snapshots, expiry and evidence all recorded |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Promotion fails at DNS | Static IP/DNS not set, or IPv6 interference | Set DNS to 127.0.0.1; disable IPv6 if it breaks resolution |
| Client cannot join | Wrong DNS, or no route to DC | Point client DNS at 192.0.2.60; test LDAP 389 |
| `dcdiag` DNS failures | Forwarders configured to unreachable servers | Remove forwarders in an isolated lab |
| `klist` empty | Logged in with cached credentials before DC reachable | Log off and on with the DC reachable |
| Evaluation shutdown warning | Not activated within 10 days | Attach NAT, activate, remove NAT, re-verify isolation |
| OU creation errors | Path string malformed | Create OUs one at a time with explicit `-Path` |

## References

1. Microsoft — Install AD DS and promote a domain controller. Accessed 2026-10-29.
2. Microsoft — Windows Server 2025 Evaluation. <https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2025> Accessed 2026-10-29.
3. Microsoft — `dcdiag`, `klist`, `nltest` documentation. Accessed 2026-10-29.
4. Microsoft — Active Directory security best practices. Accessed 2026-10-29.

---
title: "The Windows Security Model and PowerShell"
description: "Accounts, groups, tokens, UAC, NTFS ACLs, services, the registry, event logs, and PowerShell object pipelines."
module_code: CYB-110
level: 1
kind: lesson
prerequisites: [CYB-109]
estimated_minutes: 120
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [windows, powershell, acls, event-logs]
---

# The Windows Security Model and PowerShell

## Learning objectives

By the end of this lesson you can:

1. Explain how a Windows logon produces an access token, and what UAC changes about it.
2. Read an NTFS ACL and describe what each principal may do.
3. Inspect services, processes, ports, and local users with PowerShell.
4. Read the Security and System event logs, and filter by event ID.
5. Explain why PowerShell is used by attackers and what logging defenders have.
6. Hash a file on Windows and explain why the value matches the Linux result.

## Prerequisites

[CYB-109](../09-linux-command-line/index.md). A running `lab-win` VM with administrative access.

---

## 1. The model in one page

| Concept | Linux equivalent | Security consequence |
| --- | --- | --- |
| Local account (SAM) | Entry in `/etc/passwd` | Password hashes live in the registry; protect the host |
| Group | Group | Group membership is the main privilege path |
| Access token | Process credentials (UID/GID) | Every process carries a token; that is what is checked |
| UAC | `sudo` (roughly) | Admin approval mode splits the token: standard vs elevated |
| NTFS ACL | File mode + POSIX ACLs | Fine-grained allow/deny per principal |
| Registry | `/etc` + more | Configuration and persistence live here |
| Event log | syslog/journal | Evidence, organized by channel |

**The key idea:** when you log on, Windows builds a **token** containing your identity and group memberships.
Every process you start gets a copy. Access checks compare that token against an object's ACL. That is the
whole model — everything else is detail.

### UAC in practice

An administrator account does not run with full privileges by default. It holds a *filtered* token; elevation
produces a second, unfiltered token after consent. This is why "I am an administrator" and "Access is denied"
coexist — and why running a shell elevated is a deliberate act, not a default.

## 2. ACLs

```powershell
New-Item -ItemType Directory -Force C:\lab | Out-Null
"demo" | Out-File C:\lab\demo.txt
icacls C:\lab\demo.txt
```

**Expected** (names and SIDs vary):

```text
C:\lab\demo.txt DESKTOP-ABC\student:(F)
                BUILTIN\Administrators:(F)
                NT AUTHORITY\SYSTEM:(F)
```

| Code | Meaning |
| --- | --- |
| `(F)` | Full control |
| `(M)` | Modify |
| `(RX)` | Read and execute |
| `(R)` | Read |
| `(W)` | Write |
| `(D)` | Delete |
| `(OI)(CI)` | Inherit to objects/containers (applies to directory children) |

The security question is always the same as on Linux: *who has what, and is that the minimum?* A share
with `Everyone:(F)` is the Windows version of `chmod 777`.

## 3. PowerShell: objects, not text

Bash pipelines move text. PowerShell pipelines move **objects**, so you filter and select structured
properties instead of parsing strings.

```powershell
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name, Id, CPU
```

| Task | Command |
| --- | --- |
| Files | `Get-ChildItem C:\lab -Force` |
| Processes | `Get-Process` |
| Services | `Get-Service` |
| Listening ports | `Get-NetTCPConnection -State Listen` |
| Local users | `Get-LocalUser` |
| Members of a group | `Get-LocalGroupMember -Group Administrators` |
| Network config | `Get-NetIPConfiguration` |
| Port test | `Test-NetConnection -ComputerName 127.0.0.1 -Port 445` |
| Events | `Get-WinEvent -LogName Security -MaxEvents 20` |
| Hash | `Get-FileHash C:\lab\demo.txt -Algorithm SHA256` |

```powershell
Get-NetTCPConnection -State Listen |
  Select-Object LocalAddress, LocalPort, OwningProcess |
  Sort-Object LocalPort | Select-Object -First 10
```

**Expected** (ports vary; `LocalAddress ::` or `0.0.0.0` means all interfaces):

```text
LocalAddress LocalPort OwningProcess
------------ --------- -------------
::                 135          1080
0.0.0.0            445             4
127.0.0.1         49664          1120
```

`OwningProcess` is a PID; resolve it with `Get-Process -Id 1080`. Mapping port → process is the same skill
you practised on Linux, which is the point: the concepts transfer, the syntax does not.

## 4. Event logs: the evidence

```powershell
Get-WinEvent -LogName System -MaxEvents 5 | Format-Table TimeCreated, Id, ProviderName -AutoSize
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} -MaxEvents 3 |
  Format-List TimeCreated, Id, Message
```

**Event IDs worth knowing now:**

| ID | Log | Meaning |
| --- | --- | --- |
| 4624 | Security | Successful logon |
| 4625 | Security | Failed logon |
| 4672 | Security | Special privileges assigned (admin logon) |
| 4688 | Security | Process creation (only if auditing enabled) |
| 4720 | Security | User account created |
| 7045 | System | New service installed (a common persistence clue) |

You will build detections on these in Level 4. For now, learn to read them and to filter by ID rather than
scrolling.

## 5. Why PowerShell is everywhere

Both attackers and defenders use it because it is installed, signed, and powerful. That creates three
defensive realities:

- **Script block logging** records what code ran.
- **Module logging** records which commands executed.
- **Transcription** records sessions to files.

When these are off — the default on many systems — PowerShell activity is nearly invisible. Turning them on
is a hardening decision you will make in Level 4 (CYB-403). For now, know that the logging exists and that
its absence is a finding.

Do **not** change the execution policy to `Unrestricted` on a real machine to "make things work". On your
lab VM, use `-ExecutionPolicy Bypass` per command if needed, and understand that this is exactly what
attackers do too.

## 6. Hashes match across operating systems

```powershell
"same content" | Out-File -Encoding ascii C:\lab\same.txt
(Get-FileHash C:\lab\same.txt -Algorithm SHA256).Hash
```

Then, on Linux with the same bytes:

```bash
printf 'same content\n' > /tmp/same.txt
sha256sum /tmp/same.txt
```

**Expected:** the same 64-character digest (assuming identical bytes and line endings). That is the point of
a cryptographic hash: it describes content, not the platform. The lab has you prove this.

---

## Practical exercises

### Exercise 1 — Token and elevation (10 minutes)

```powershell
whoami /groups | Select-String -Pattern "Mandatory Label|Administrators"
whoami /priv | Select-Object -First 10
```

Answer: is your current shell elevated? Which line tells you? Then open a second, elevated shell and repeat —
record the difference.

### Exercise 2 — ACL audit (15 minutes)

```powershell
New-Item -ItemType Directory -Force C:\lab\share | Out-Null
"report" | Out-File C:\lab\share\report.txt
icacls C:\lab\share
```

List every principal and permission. Identify one entry you would remove on a real file server, and say why.

### Exercise 3 — Port to process (10 minutes)

```powershell
$c = Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 445
Get-Process -Id $c.OwningProcess | Select-Object Id, ProcessName, Path
```

**Expected:** `System` (PID 4) owning port 445 (SMB). SMB on a workstation is worth understanding: it is a
major lateral-movement path in enterprise incidents.

### Exercise 4 — Read a failed logon (10 minutes)

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 3 |
  Format-List TimeCreated, Id, Message
```

If no events appear, that is itself informative: failed-logon auditing may not be enabled. Note which case
you observed — "no events" and "no failures" are different facts.

## Expected observations and verification

- You can say whether your shell is elevated, and how you know.
- You identified every principal on a file and one to remove.
- You mapped a listening port to a process and its path.
- You filtered the event log by ID rather than scrolling.
- You can explain what script block logging would add.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| `Access is denied` despite admin rights | UAC filtered token | Run the shell elevated deliberately |
| `Get-WinEvent` access denied on Security log | Requires elevation | Elevate, and note that this is by design |
| `icacls` output unreadable | Dense format | Use `Get-Acl` for object form, `icacls` for quick view |
| Assuming `0.0.0.0` and `::` mean the same thing | Both are "any" but for different stacks | Check both when auditing exposure |
| Disabling execution policy globally | Convenience | Use per-invocation bypass in the lab; policy change is a real hardening decision |
| Comparing hashes of different files | Line endings or encoding differ | Compare identical bytes; check with `Format-Hex` |

## Review questions

1. What is an access token, and why does every process need one?
2. How does UAC change what an administrator account can do by default?
3. What does `(OI)(CI)(M)` mean on a directory ACL?
4. Why do PowerShell pipelines pass objects rather than text, and what does that buy you?
5. Which event IDs indicate a successful logon and a failed one?
6. Why is PowerShell a favourite of both attackers and defenders?

## Knowledge check

1. Where are local account password hashes stored on Windows?
2. What does the `(F)` in `icacls` output grant?
3. Which command lists listening TCP ports with owning PIDs?
4. Event ID 7045 records what, and why does it matter?
5. Why can the same file produce the same SHA-256 on Windows and Linux?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 1–4 if 1, 2 and 4 are uncertain.)*

## Summary

- Logon produces a token; ACLs are evaluated against it. UAC splits administrator tokens.
- ACLs are allow/deny entries per principal; inheritance makes directory permissions spread.
- PowerShell passes objects, which makes inspection and filtering precise.
- Event logs are the evidence layer, and specific IDs carry specific meaning.
- PowerShell logging is a hardening decision, and its absence is a finding.

## Next lesson

[CYB-111 · Virtualization, Snapshots and Isolated Lab Networks](../11-virtualization-and-lab-networks/index.md) —
where both operating systems live side by side, safely.

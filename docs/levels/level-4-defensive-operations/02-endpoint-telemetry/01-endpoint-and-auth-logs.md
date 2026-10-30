---
title: "Endpoint and Authentication Telemetry"
description: "Windows event IDs, Sysmon, journald and auth logs — what each records, how to enable it, and what it cannot see."
module_code: CYB-402
level: 4
kind: lesson
prerequisites: [CYB-401]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-402-01, LAB-402-02, LAB-402-03]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [windows-event-log, sysmon, journald, auditd, authentication, edr]
---

# Endpoint and Authentication Telemetry

**Level 4** · 240 minutes · **Prerequisites:** CYB-401 · **Labs:**
[Windows Logs](lab-01-windows-event-logs.md) · [Linux Auth Logs](lab-02-linux-auth-logs.md) ·
[Process Sequence](lab-03-sysmon-process-sequence.md)

## Why this matters

Detection is a query over evidence. When an alert says "suspicious PowerShell", the analyst's next question is
always the same: *show me the command line*. If command-line auditing was off, there is no answer, and the
investigation stops at a guess.

This lesson is about making sure the answer exists — and about knowing which answers your telemetry can never give
you. That second part is what separates an analyst who trusts a dashboard from one who knows its blind spots.

## Learning outcomes

By the end of this lesson you will be able to:

- Identify the Windows event IDs for logon, process creation, and persistence, and explain what each proves.
- Enable command-line process auditing and PowerShell script-block logging, and verify both.
- Explain the Sysmon event IDs used by most endpoint detections, and the trade-off of a broad configuration.
- Query `journald` and `auth.log` for authentication events with specific filters.
- Distinguish brute force, password spraying, and credential stuffing from log patterns.
- State three things endpoint telemetry cannot tell you, and what would.

## Prerequisites and setup

- `lab-win` and `lab-ubuntu` running, host-only network, snapshots taken.
- Administrative access on both.
- Sysmon available for LAB-402-03 (downloaded during the lab, with NAT attached only for the download).

---

## Core concepts

### 1. Windows: three logs, one audit policy

Windows records security events only if an audit policy says to. A default workstation logs almost nothing useful,
which is why "we have no logs" is a configuration statement, not a vendor limitation.

| Log | Contains | Typical use |
| --- | --- | --- |
| Security | Logon, privilege use, account changes, process creation (if enabled) | Authentication and authorization investigations |
| System | Service installation (7045), driver load, unexpected shutdowns | Persistence and stability |
| Application | Application errors, some service failures | Context, rarely primary evidence |

Enable the categories you need, then **verify the events appear**. On a lab VM:

```powershell
# Logon success and failure, process creation, account management
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /set /subcategory:"Process Creation" /success:enable
auditpol /set /subcategory:"User Account Management" /success:enable /failure:enable
auditpol /get /category:* | Select-String "Logon|Process Creation|User Account"
```

Command-line auditing is a **separate** setting and is off by default even when process creation is on:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" `
  /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f

# PowerShell script blocks (4104) and module logging (4103)
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" `
  /v EnableScriptBlockLogging /t REG_DWORD /d 1 /f
```

**Why script-block logging matters:** an encoded command line is opaque, but 4104 records the **decoded** script
that PowerShell executed. It is the single highest-value Windows logging setting for detection work.

### 2. The event IDs that carry most investigations

| ID | Meaning | What it proves | Common false trail |
| --- | --- | --- | --- |
| 4624 | Successful logon | Access happened; logon **type** and source matter | Service accounts logging on constantly |
| 4625 | Failed logon | Attempt, not access | Stale mapped drives, scheduled tasks with old passwords |
| 4634 / 4647 | Logoff (system / user) | Session ended | Missing on abrupt shutdown |
| 4648 | Explicit credentials used | A process used alternate credentials | Admin scripts using `runas` |
| 4672 | Special privileges assigned | Admin-level logon | Every admin session, including legitimate |
| 4688 | Process created | What ran, and (if enabled) command line | Very high volume; needs filtering |
| 4698 | Scheduled task created | Persistence | Software updaters create tasks |
| 4720 / 4722 / 4732 | Account created / enabled / added to group | Persistence or privilege escalation | IT onboarding |
| 4740 | Account locked out | Policy triggered | User error, or spraying |
| 4768 / 4769 | Kerberos TGT / service ticket | Domain authentication | Normal domain traffic |
| 4771 | Kerberos pre-authentication failed | Wrong password against the KDC | Expired machine passwords |
| 4776 | NTLM credential validation | NTLM use, including failures | Legacy applications |
| 7045 | Service installed (System log) | Persistence | Legitimate installers |
| 1102 | Audit log cleared | Defence evasion | Rare; treat as high priority |

**Logon types are the field analysts skim and regret.** The same 4624 means something different depending on the
type: `2` interactive (someone at the console), `3` network (SMB, a share), `4` batch, `5` service, `7` unlock,
`8` network cleartext, `9` explicit credentials, `10` remote interactive (RDP), `11` cached interactive.

The classic detection is a **4625 burst followed by a 4624 from the same source** — guessing that succeeded. The
classic false positive is a service account with a stale password producing 4625s forever, which is why the pair
matters more than the count.

### 3. Sysmon: the telemetry most detections assume

Sysmon is a Microsoft Sysinternals driver plus service that writes detailed endpoint events to its own log. It does
not alert; it records. Current build at the time of writing is **15.22** — check Sysinternals before installing,
and record the version in your notes.

| ID | Event | Why it matters |
| --- | --- | --- |
| 1 | Process created | Image, command line, parent, user, hashes |
| 3 | Network connection | Process-to-address mapping, the pivot to network logs |
| 7 | Image loaded | Unsigned or unusual DLLs |
| 8 | Create remote thread | Injection into another process |
| 10 | Process access | Credential dumping tools reading LSASS |
| 11 | File created | Dropped payloads, ransomware notes |
| 12/13/14 | Registry create/set/rename | Run keys, services, policy tampering |
| 17/18 | Named pipe created/connected | Lateral movement and C2 channels |
| 22 | DNS query | Domain lookups with the querying process |
| 25 | Process tampering | Process hollowing or herpaderping indicators |

**Install shape** (detailed in LAB-402-03):

```powershell
# Download, verify the signature, install with a community configuration
Invoke-WebRequest https://download.sysinternals.com/files/Sysmon.zip -OutFile Sysmon.zip
Expand-Archive Sysmon.zip -DestinationPath Sysmon
Get-AuthenticodeSignature .\Sysmon\Sysmon64.exe | Select-Object Status, SignerCertificate
.\Sysmon\Sysmon64.exe -accepteula -i .\sysmonconfig.xml
Get-Service Sysmon64
```

**On configurations.** Two community options dominate: **SwiftOnSecurity/sysmon-config** (readable, heavily
commented, a good learning baseline) and **Olaf Hartong's sysmon-modular** (maintained as composable modules, better
for role-specific profiles). Neither should be deployed unchanged: a broad configuration can generate thousands of
events per minute, and a narrow one silently omits the thing you needed. The right question is not "which config"
but "which events does my detection need, and is this config producing them?"

### 4. Linux: journald, auth.log and auditd

Linux has three overlapping sources, and which one has the answer depends on the distribution and the service.

| Source | Command | Contains |
| --- | --- | --- |
| journald | `journalctl` | Everything systemd services log, structured, with metadata |
| `auth.log` (Debian/Ubuntu) or `secure` (RHEL family) | `grep`, `awk` | Authentication: sshd, sudo, su, PAM, CRON |
| `auditd` | `ausearch`, `aureport` | Syscall-level audit: file access, execve, identity changes |

```bash
# Authentication events from the journal, last boot, warnings and above
journalctl -b -p warning --no-pager | grep -Ei 'sshd|sudo|pam|login'

# Structured output for parsing
journalctl -u ssh --since "2026-10-29 00:00" -o json | jq -r 'select(.MESSAGE) | [.__REALTIME_TIMESTAMP, .MESSAGE] | @tsv'

# Debian-family auth log: failures and successes with counts by source
grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head
grep 'Accepted' /var/log/auth.log | tail -20
```

The common `sshd` messages, in the order an investigation reads them:

| Message | Meaning |
| --- | --- |
| `Failed password for invalid user X from A` | A username that does not exist was tried — spraying signal |
| `Failed password for X from A` | Real account, wrong password |
| `Accepted publickey for X from A` | Key-based success; check the key fingerprint |
| `maximum authentication attempts exceeded` | Client gave up, often after automated tries |
| `Connection closed by authenticating user` | Ambiguous; can be a scan or a misconfigured client |

`auditd` is for what the application logs do not cover: file watches and command execution.

```bash
# Watch identity files, then search by key
sudo auditctl -w /etc/passwd -p wa -k identity
sudo ausearch -k identity -i --start recent
sudo aureport --auth --summary
```

**Why auditd is worth the trouble:** it records `execve` with arguments, and file writes to paths you name, even
when the application logs nothing. It is also the source most often missing in a lab, which is why detections that
assume it fail silently.

### 5. Authentication patterns, and what each looks like

| Pattern | Shape in logs | Distinguishing feature |
| --- | --- | --- |
| Brute force | Many failures, **one** account, one source | Volume against a single username |
| Password spraying | Few failures, **many** accounts, one source | Low-and-slow across usernames; avoids lockout |
| Credential stuffing | Successes across many accounts, many sources | Distributed sources, valid credentials, no failure burst |
| Stuffing with MFA fatigue | Repeated MFA prompts, then success | Push notifications, not passwords |
| Service-account misuse | Interactive logon (type 2/10) for a service account | Service accounts should use type 5 |
| Impossible travel | Two successes, distant sources, short interval | Same account, same credential, different geography |

**Why spraying is the one juniors miss:** it produces *fewer* failures per account than brute force, so
failure-count thresholds never fire. The signal is breadth — one source touching many usernames — which is a
different query: group by source, count distinct usernames.

### 6. What endpoint telemetry cannot tell you

1. **What happened before the log.** If process creation auditing was off, the parent is unknown. Absence of
   evidence is not evidence of absence.
2. **What left the host.** Sysmon 3 shows a connection, not its content. Data volume and destination require
   network telemetry (CYB-405).
3. **Whether the log is complete.** A local administrator can clear the Security log (1102) or stop the Sysmon
   service (Sysmon 4). Central forwarding is the control, not the local log.
4. **Who the human was.** A session ID is not a person; shared accounts and RDP sessions break attribution, which
   is why identity logs and physical access records matter.

### 7. Normalising before you analyse

Three habits that prevent most false conclusions:

- **Work in UTC.** Every log source, every note. Local time zones produce timelines that are wrong by hours and
  look plausible.
- **Join on identifiers, not timestamps alone.** Process ID plus host plus time; session ID; source address plus
  account. Second-resolution timestamps collide.
- **Record the field you filtered on.** "Failed logons from 198.51.100.77" is reproducible; "suspicious logons" is
  not.

---

## Worked example: from event to hypothesis

A workstation shows a 4688 for `rundll32.exe` with the command line
`rundll32.exe comsvcs.dll, MiniDump 624 C:\Windows\Temp\d.dmp full`.

Reading it in four steps:

1. **What is it?** `comsvcs.dll` exports `MiniDump`, which can dump a process's memory. Combined with a PID and an
   output file, this is a credential-dumping technique (T1003.001) using a signed Windows binary.
2. **What is the parent?** If the parent is `outlook.exe` or `winword.exe`, the chain is a document spawning a
   shell — a phishing execution path. If the parent is an admin's `powershell.exe`, it may be a legitimate support
   action, and you need the change record.
3. **What did it write?** A 41 MB file in `C:\Windows\Temp` is consistent with a memory dump. Check Sysmon 11 for
   creation and the file hash, then look for the file leaving the host (Sysmon 3, proxy).
4. **What is missing?** Whether the dump succeeded, and what the attacker did with it. That requires file access
   telemetry or network logs — a gap to state, not to guess.

The finding writes itself: *"Credential dumping via comsvcs.dll MiniDump on ws-07, spawned by Outlook, writing a
41 MB dump to Temp; technique T1003.001; dump exfiltration unconfirmed because proxy logs retain only metadata."*

---

## Defender's view

| Control | What it buys | Its limit |
| --- | --- | --- |
| Advanced audit policy | The events exist at all | Only for categories you enabled |
| Command-line auditing | The *what* of execution | Truncation at 1024 characters in some paths |
| PowerShell script-block logging | Decoded script content | Obfuscation inside the script still applies |
| Sysmon with a tuned config | Process ancestry, network, registry, DNS | Kernel-level evasion; event volume |
| Central log forwarding | Tamper resistance | Forwarding latency and storage cost |
| `auditd` execve rules | Arguments for every execution | Performance cost; rule maintenance |

---

## Common mistakes

1. **Assuming `4688` includes the command line.** It does not until you enable it, and the setting is separate from
   the audit policy.
2. **Treating 4625 volume as compromise.** Count is weak; the pair of failure then success is strong.
3. **Filtering by process name.** Attackers rename binaries. Filter by parent-child relationship, command-line
   arguments, signature, and path.
4. **Reading local logs as authoritative.** An attacker with admin can clear them; central collection is the
   control.
5. **Mixing time zones.** A timeline assembled from local times will be wrong and will look right.
6. **Deploying Sysmon with a maximal config.** The event volume can overwhelm a small SIEM and hide the signal.

---

## Practice

1. [LAB-402-01 · Windows Event Log Triage](lab-01-windows-event-logs.md)
2. [LAB-402-02 · Linux Authentication Log Analysis](lab-02-linux-auth-logs.md)
3. [LAB-402-03 · A Suspicious Process Sequence](lab-03-sysmon-process-sequence.md)

**Stretch task.** Write the two queries you would run to distinguish spraying from brute force across a month of
`auth.log`, and state the threshold you chose and why.

## Knowledge check

1. Which event ID records a successful logon, and which field changes its meaning?
2. What must be enabled for `4688` to include a command line, and why is that separate from the audit policy?
3. Name four Sysmon event IDs and the behaviour each reveals.
4. Why is 4104 more useful than an encoded command line?
5. Give the log signature that distinguishes password spraying from brute force.
6. What does `auditd` record that `auth.log` does not?
7. Name three things endpoint telemetry cannot tell you, and the source that would.
8. Why does clearing the Security log (1102) matter even when you forward logs centrally?

## Summary

- Windows logs exist only where audit policy creates them; command lines and script blocks are separate switches.
- Logon type and the failure-then-success pair matter more than counts.
- Sysmon supplies process ancestry, network, registry and DNS telemetry; the configuration decides what you can see.
- `journald`, `auth.log` and `auditd` overlap; `auditd` is the syscall record.
- Spraying is breadth across accounts, not depth against one.
- Endpoint telemetry has blind spots: known gaps beat confident guesses.

## References

1. Microsoft Learn — Audit logon events; Command line process auditing; PowerShell script block logging.
   Accessed 2026-10-29.
2. Microsoft Sysinternals — Sysmon v15.22 and configuration guidance.
   <https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon> Accessed 2026-10-29.
3. SwiftOnSecurity/sysmon-config; Olaf Hartong/sysmon-modular. Accessed 2026-10-29.
4. `journalctl` and `systemd-journald` documentation. Accessed 2026-10-29.
5. Linux `auditd` — `auditctl(8)`, `ausearch(8)`, `aureport(8)`.
6. MITRE ATT&CK — T1003 OS Credential Dumping; T1110 Brute Force. Accessed 2026-10-29.

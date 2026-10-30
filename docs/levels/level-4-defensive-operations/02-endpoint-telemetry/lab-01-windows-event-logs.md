---
title: "LAB-402-01 · Windows Event Log Triage"
description: "Enable the audit settings that matter, generate real authentication events, and turn them into a defensible finding."
module_code: CYB-402
level: 4
kind: lab
prerequisites: [CYB-402]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-402-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [windows-event-log, audit-policy, 4625, 4688, powershell]
---

# LAB-402-01 · Windows Event Log Triage

## Scenario and background

A workstation reported "slow logins" and the service desk wants to know whether anything suspicious happened. You
have the host, administrative access, and a Security log that — before this lab — does not contain what you need.

You will enable the audit settings, generate authentication events you can actually see, query them, and write the
finding. Generating the events yourself is deliberate: you know the ground truth, so you can tell a parsing bug
from a real pattern.

## Learning objectives

By the end of this lab you can:

1. Enable logon, process-creation, and PowerShell script-block auditing, and verify each took effect.
2. Generate benign authentication failures that produce 4625 events, without locking out a real account.
3. Parse 4625 fields (account, source address, logon type) into a structured table.
4. Identify the failure-then-success pattern and explain why the pair matters more than the count.
5. Confirm that 4688 includes a command line, and state what it looked like before you enabled it.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Windows 11 or 10 | lab VM | `lab-win`, host-only network |
| PowerShell | 5.1+ | Built in |
| Sysmon | 15.x | Optional here; used in LAB-402-03 |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab-win` only, with the local administrator account you created.
    **Targets you must not use:** any domain controller, any real user account, any production host.

    **Do not lock out a real account.** The failures in this lab use usernames that do not exist. Attempting five
    bad passwords against a real account can trigger lockout policy and, on a shared domain, a service desk ticket
    you cannot close.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The simulated adversary is guessing credentials against a workstation over SMB. The events you generate are real
Windows events produced by real (if pointless) authentication attempts — the only thing synthetic is the intent.

## Environment

| Host | Role | Address | Notes |
| --- | --- | --- | --- |
| `lab-win` | Target and analyst host | 192.0.2.40 | Host-only adapter |
| — | No second host required | — | Failures target `127.0.0.1` |

## Before you start

1. Snapshot `pre-lab-402-01`.
2. Open an elevated PowerShell prompt (`Run as Administrator`).
3. Create the evidence directory: `New-Item -ItemType Directory -Force C:\lab\402-01\evidence`.

## Procedure

### 1. Record the baseline

Before changing anything, check what the Security log currently contains:

```powershell
auditpol /get /category:* | Select-String "Logon|Process Creation"
(Get-WinEvent -ListLog Security).RecordCount
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} -MaxEvents 3 -ErrorAction SilentlyContinue |
  Select-Object TimeCreated, Id
```

**Expected:** logon auditing may be partly on by default; `4688` is usually absent on a workstation; record count is
whatever the VM accumulated. **Write down the baseline** — the before/after comparison is part of the evidence.

### 2. Enable the audit policy

```powershell
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /set /subcategory:"Process Creation" /success:enable
auditpol /set /subcategory:"User Account Management" /success:enable /failure:enable

# Command lines in 4688 — separate from the audit policy
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" `
  /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f

# PowerShell script-block logging (4104)
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" `
  /v EnableScriptBlockLogging /t REG_DWORD /d 1 /f

auditpol /get /subcategory:"Logon"
auditpol /get /subcategory:"Process Creation"
```

**Expected:** both subcategories report `Success and Failure` or `Success`. If the policy shows `No Auditing`, the
command did not apply — check that the prompt is elevated.

### 3. Generate authentication events

Five failures for accounts that do not exist, then one success with your current credentials:

```powershell
1..5 | ForEach-Object {
  cmd /c "net use \\127.0.0.1\IPC$ /user:LAB\ghost$_ WrongPassword!23 2>&1" | Out-Null
  Start-Sleep -Milliseconds 400
}

# A successful network logon using the current account's credentials
cmd /c "net use \\127.0.0.1\IPC$ 2>&1" | Out-Null
cmd /c "net use \\127.0.0.1\IPC$ /delete" | Out-Null
```

**Why `127.0.0.1`:** it produces genuine network logon events (type 3) on the local machine, with a source address,
without involving any other host. The failures are for `ghost1`…`ghost5`, so no real account can be locked out.

### 4. Query and parse the events

```powershell
$since = (Get-Date).AddMinutes(-15)

Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625; StartTime=$since} -ErrorAction SilentlyContinue |
  ForEach-Object {
    $m = $_.Message
    [pscustomobject]@{
      Time   = $_.TimeCreated.ToUniversalTime()
      User   = ([regex]::Match($m,'Account Name:\s+(.+)')).Groups[1].Value.Trim()
      Domain = ([regex]::Match($m,'Account Domain:\s+(.+)')).Groups[1].Value.Trim()
      Type   = ([regex]::Match($m,'Logon Type:\s+(\d+)')).Groups[1].Value
      Source = ([regex]::Match($m,'Source Network Address:\s+(\S+)')).Groups[1].Value
      Status = ([regex]::Match($m,'Status:\s+(0x[0-9A-Fa-f]+)')).Groups[1].Value
    }
  } | Export-Csv C:\lab\402-01\evidence\failed-logon.csv -NoTypeInformation

Import-Csv C:\lab\402-01\evidence\failed-logon.csv | Format-Table -AutoSize
```

**Expected:** five rows, `User` values `ghost1`…`ghost5`, `Type` `3`, `Source` `127.0.0.1`, and a `Status` of
`0xC000006D` (bad username or password) or `0xC0000064` (user does not exist) — the exact code depends on whether
the account name is checked first.

**Why parse `Message` with regex:** the structured fields are available as XML properties, but their indices vary
between Windows versions. Message parsing is more portable and, for a lab, easier to verify. Note the trade-off in
your report: regex over prose is brittle, which is why production pipelines use XML or a normalising agent.

### 5. Find the success that followed

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624; StartTime=$since} -ErrorAction SilentlyContinue |
  ForEach-Object {
    $m = $_.Message
    [pscustomobject]@{
      Time   = $_.TimeCreated.ToUniversalTime()
      User   = ([regex]::Match($m,'Account Name:\s+(.+)')).Groups[1].Value.Trim()
      Type   = ([regex]::Match($m,'Logon Type:\s+(\d+)')).Groups[1].Value
      Source = ([regex]::Match($m,'Source Network Address:\s+(\S+)')).Groups[1].Value
    }
  } | Where-Object Type -in 3,10 | Format-Table -AutoSize
```

**Expected:** at least one type-3 success for your account from `127.0.0.1`, after the failures.

**The analytical step:** join the two sets on source address and time.

```powershell
$fail = Import-Csv C:\lab\402-01\evidence\failed-logon.csv
$fail | Group-Object Source, User | Sort-Object Count -Descending | Select-Object Count, Name -First 10
```

Answer three questions in `evidence/analysis.md`:

1. How many distinct usernames were attempted from the same source, and what pattern does that suggest?
2. Did a success follow the failures, and from where?
3. What would you need to conclude compromise rather than a misconfigured client?

### 6. Verify command-line auditing

```powershell
cmd /c "whoami /priv" | Out-Null
Start-Sleep -Seconds 2

Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688; StartTime=(Get-Date).AddMinutes(-3)} |
  ForEach-Object {
    [pscustomobject]@{
      Time = $_.TimeCreated.ToUniversalTime()
      Msg  = ($_.Message -split "`n" | Where-Object { $_ -match 'Process Command Line|New Process Name' }) -join ' | '
    }
  } | Format-List
```

**Expected:** the 4688 event includes `Process Command Line: whoami /priv`. **If the command line is missing**, the
registry setting did not apply or the process started before it did — re-run step 2 and generate a new process.

Record in `evidence/analysis.md`: the exact command line as logged, and what you would have seen without the
setting (process name only).

### 7. Check PowerShell script-block logging

```powershell
powershell -NoProfile -Command "Write-Output 'lab402-visible-script'"
Start-Sleep -Seconds 2

Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 50 |
  Where-Object Id -eq 4104 |
  Select-Object -First 3 TimeCreated, @{n='Snippet';e={($_.Message -split "`n")[0]}} | Format-List
```

**Expected:** a 4104 event whose message contains `lab402-visible-script`.

### 8. Write the finding

`evidence/finding.md`, under 300 words: what was enabled, what was observed (counts, source, accounts, logon
types), what the pattern suggests, what it does **not** prove, and two detection ideas with the event IDs they
would use.

## Evidence to collect

- `evidence/baseline.txt` — audit policy and record count before changes.
- `evidence/audit-policy-after.txt` — the same commands after changes.
- `evidence/failed-logon.csv` — five parsed rows.
- `evidence/success-after-failure.txt` — the 4624 query output.
- `evidence/cmdline-4688.txt` — the command line as logged.
- `evidence/scriptblock-4104.txt` — the decoded script.
- `evidence/analysis.md` and `evidence/finding.md`.

## Verification

- [ ] Baseline recorded before any change.
- [ ] Logon and process-creation auditing enabled, with `auditpol` output as proof.
- [ ] Five 4625 events produced for non-existent accounts, with source and logon type parsed.
- [ ] At least one type-3 success after the failures.
- [ ] 4688 contains a command line, and you recorded what it would show without the setting.
- [ ] A 4104 event contains the script text you ran.
- [ ] The finding distinguishes "pattern consistent with guessing" from "compromise proven".

## Teardown and reset

```powershell
# Leave auditing enabled — it is useful for later labs.
# Remove the lab artefacts and the share connection.
cmd /c "net use \\127.0.0.1\IPC$ /delete" 2>$null
Remove-Item C:\lab\402-01 -Recurse -Force -ErrorAction SilentlyContinue
```

Revert `pre-lab-402-01` if you want the original audit policy back. Note that reverting also removes the events you
generated — copy `evidence/` to the host first.

## Reflection

1. Five failures against five different non-existent accounts is closer to spraying than brute force. What would a
   brute-force pattern look like in the same fields?
2. You generated the events, so you knew the answer. How would your analysis change if the failures came from a
   source you could not identify?
3. Command-line auditing was a separate switch from the audit policy. Why might Microsoft have designed it that
   way, and what does that imply for a detection that assumes command lines are present?
4. Which of the events you enabled would an attacker with local admin try to disable first, and what would that look
   like in the log?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Enablement | Audit not verified | Policy and registry set, verified | Verified plus baseline comparison |
| Parsing | Reads messages by eye | CSV with user, source, type | CSV plus grouping and a correlation step |
| Interpretation | "Suspicious logins" | Pattern described | Pattern described, limits stated, detection ideas named |
| Evidence | Screenshots | Command output saved | Reproducible commands with before/after state |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No 4625 events | Logon auditing off, or `net use` failed before authentication | Recheck `auditpol`; run `net use` manually and read its error |
| `net use` succeeds unexpectedly | An existing IPC$ session with cached credentials | `net use * /delete /y`, then retry |
| 4688 has no command line | Registry setting applied after the process started | Run a new process after the change |
| No 4104 events | Script-block logging not enabled, or the log is filtered | Check the registry value; query the Operational log directly |
| Regex returns empty fields | Message format differs by Windows version | Print one full `Message` and adjust the pattern |
| CSV has duplicate rows | Query window overlaps two runs | Use a narrower `StartTime` |

## References

1. Microsoft Learn — Audit logon events; 4624/4625 event documentation. Accessed 2026-10-29.
2. Microsoft Learn — Command line process auditing. Accessed 2026-10-29.
3. Microsoft Learn — PowerShell script block logging (4104). Accessed 2026-10-29.
4. MITRE ATT&CK — T1110 Brute Force; T1078 Valid Accounts. Accessed 2026-10-29.

---
title: "LAB-402-03 · A Suspicious Process Sequence"
description: "Install Sysmon, generate a benign but structurally suspicious execution chain, and prove the sequence from telemetry alone."
module_code: CYB-402
level: 4
kind: lab
prerequisites: [CYB-402]
estimated_minutes: 150
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-402-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [sysmon, process-tree, encoded-powershell, detection, sigma]
---

# LAB-402-03 · A Suspicious Process Sequence

## Scenario and background

"Encoded PowerShell" is on every detection list and half of every false-positive report. The alert is only useful
when it includes the sequence: which process started it, what it ran next, whether it touched the network, and
whether anything landed on disk.

You will install Sysmon with a community configuration, generate a **harmless** execution chain that has the shape
of a real intrusion, and then prove the sequence from the telemetry — including the part that makes it benign.

## Learning objectives

By the end of this lab you can:

1. Install Sysmon 15.x with a reviewed community configuration and verify it is collecting.
2. Extract process image, command line, parent image, user, and hashes from Sysmon Event ID 1.
3. Reconstruct a process tree from `ProcessId` and `ParentProcessId`.
4. Explain why an encoded command line alone is weak evidence, and what surrounding events strengthen it.
5. Write a detection rule with an explicit false-positive section.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Windows 11 or 10 | lab VM | `lab-win`, administrator |
| Sysmon | 15.x | 15.22 at the time of writing; check Sysinternals for the current build |
| Sysmon config | SwiftOnSecurity `sysmon-config` | Readable baseline; review before use |
| PowerShell | 5.1+ | Built in |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab-win` only.
    **Targets you must not use:** any other host. Do not point the generated chain at a network service, do not
    download a payload, and do not run any tool that touches credentials.

    **The generated activity is benign by construction:** it decodes a string that writes the output of `whoami` to
    a file. It is *shaped* like an intrusion so the telemetry is realistic, and it must stay harmless.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The simulated adversary has code execution as a standard user and uses a signed Microsoft binary with an encoded
command to run a second-stage command, then drops a file. No credential access, no persistence, no network
communication beyond what Windows does normally. The detection question is whether the sequence, not the string,
distinguishes it.

## Environment

| Host | Role | Address | Notes |
| --- | --- | --- | --- |
| `lab-win` | Target and analyst | 192.0.2.40 | Host-only; NAT only for downloads |
| `lab-ubuntu` | Optional collector | 192.0.2.20 | Not required |

## Before you start

1. Snapshot `pre-lab-402-03`.
2. Attach NAT for the download step, then detach it and confirm `ping 8.8.8.8` fails.
3. Open an elevated PowerShell prompt and create `C:\lab\402-03\{evidence,tools}`.

## Procedure

### 1. Download and verify Sysmon

```powershell
Set-Location C:\lab\402-03\tools
Invoke-WebRequest https://download.sysinternals.com/files/Sysmon.zip -OutFile Sysmon.zip
Expand-Archive Sysmon.zip -DestinationPath .
Get-AuthenticodeSignature .\Sysmon64.exe | Format-List Status, SignerCertificate
(Get-Item .\Sysmon64.exe).VersionInfo.FileVersion
```

**Expected:** `Status: Valid`, signer `CN=Microsoft Corporation`, and a file version in the 15.x range. Record the
version — it belongs in your report, and Sysmon's schema changes between major versions.

**Why check the signature:** you are about to install a kernel driver. Downloading it over TLS is not enough; the
signature is the integrity check that survives a compromised mirror.

### 2. Install with a community configuration

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml `
  -OutFile .\sysmonconfig.xml
(Get-Content .\sysmonconfig.xml | Measure-Object -Line).Lines
Select-String -Path .\sysmonconfig.xml -Pattern 'ProcessCreate|NetworkConnect|DnsQuery' | Select-Object -First 5

.\Sysmon64.exe -accepteula -i .\sysmonconfig.xml
Get-Service Sysmon64
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 3 | Select-Object TimeCreated, Id
```

**Expected:** the service is `Running`, and the log already contains events (Sysmon logs its own start).

**On the configuration choice:** SwiftOnSecurity's file is heavily commented, which makes it good for learning what
each include/exclude does. Olaf Hartong's `sysmon-modular` is the better base for a maintained deployment because
you can compose profiles per host role. Whichever you use, read the ProcessCreate and DnsQuery sections and note
what is **excluded** — that is what your detection will not see.

### 3. Generate the sequence

```powershell
New-Item -ItemType Directory -Force C:\lab\402-03\evidence | Out-Null

$inner = "cmd.exe /c whoami /priv > C:\lab\402-03\evidence\whoami.txt; Write-Output 'lab402-03 benign payload'"
$enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($inner))

# Record the decoded text so the report can show that the payload is harmless
$inner | Set-Content C:\lab\402-03\evidence\decoded.txt

powershell.exe -NoProfile -WindowStyle Hidden -EncodedCommand $enc
Start-Sleep -Seconds 3
Get-Content C:\lab\402-03\evidence\whoami.txt | Select-Object -First 3
```

**Expected:** the file contains privilege information for your account. The command line you just ran contains
`-EncodedCommand` and a long base64 string, and it spawned `cmd.exe`.

### 4. Extract the process events

Sysmon's event data is XML; index-based access breaks between versions, so select by field name:

```powershell
function Get-SysmonField {
    param($Event, [string]$Name)
    $xml = [xml]$Event.ToXml()
    ($xml.Event.EventData.Data | Where-Object { $_.Name -eq $Name }).'#text'
}

Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' `
  -FilterHashtable @{Id=1; StartTime=(Get-Date).AddMinutes(-10)} |
  ForEach-Object {
    [pscustomobject]@{
      Time     = $_.TimeCreated.ToUniversalTime()
      PID      = Get-SysmonField $_ 'ProcessId'
      PPID     = Get-SysmonField $_ 'ParentProcessId'
      Image    = Split-Path (Get-SysmonField $_ 'Image') -Leaf
      Parent   = Split-Path (Get-SysmonField $_ 'ParentImage') -Leaf
      User     = Get-SysmonField $_ 'User'
      CmdLine  = Get-SysmonField $_ 'CommandLine'
      Hashes   = Get-SysmonField $_ 'Hashes'
    }
  } | Sort-Object Time |
  Export-Csv C:\lab\402-03\evidence\process-events.csv -NoTypeInformation

Import-Csv C:\lab\402-03\evidence\process-events.csv |
  Select-Object Time, PID, PPID, Image, Parent, @{n='Cmd';e={$_.CmdLine.Substring(0,[Math]::Min(90,$_.CmdLine.Length))}} |
  Format-Table -AutoSize
```

**Expected:** at least two rows — `powershell.exe` with `-EncodedCommand`, then `cmd.exe` whose `Parent` is
`powershell.exe`. The `PPID` of the second row equals the `PID` of the first.

**Why the fields matter more than the alert:** the image name is legitimate in both rows. The evidence is the
command-line shape, the parent relationship, and the file that appeared afterwards.

### 5. Reconstruct the tree

```powershell
$events = Import-Csv C:\lab\402-03\evidence\process-events.csv
foreach ($e in $events) {
    $parent = $events | Where-Object { $_.PID -eq $e.PPID } | Select-Object -First 1
    "{0}  {1} (PID {2}) <- {3}" -f $e.Time, $e.Image, $e.PID, $(if ($parent) { $parent.Image } else { $e.Parent })
}
```

**Expected:** a two-level chain rooted at the PowerShell process you started, with the parent of that root being
your terminal or Explorer. Draw it in `evidence/tree.txt`:

```text
explorer.exe (or pwsh)
└── powershell.exe  -NoProfile -WindowStyle Hidden -EncodedCommand <base64>
    └── cmd.exe     /c whoami /priv > C:\lab\402-03\evidence\whoami.txt
```

### 6. Add the file and network context

```powershell
# File created (Sysmon 11)
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' `
  -FilterHashtable @{Id=11; StartTime=(Get-Date).AddMinutes(-10)} -ErrorAction SilentlyContinue |
  ForEach-Object { [pscustomobject]@{ Time=$_.TimeCreated; Target=(Get-SysmonField $_ 'TargetFilename') } } |
  Where-Object Target -match '402-03' | Format-Table -AutoSize

# DNS queries (Sysmon 22), if your config enables them
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' `
  -FilterHashtable @{Id=22; StartTime=(Get-Date).AddMinutes(-10)} -ErrorAction SilentlyContinue |
  ForEach-Object { [pscustomobject]@{ Time=$_.TimeCreated; Query=(Get-SysmonField $_ 'QueryName'); Image=(Get-SysmonField $_ 'Image') } } |
  Select-Object -First 10 | Format-Table -AutoSize
```

**Expected:** a file-creation event for `whoami.txt` attributed to `cmd.exe` (or its parent), and DNS events if the
configuration includes them. If Sysmon 22 is absent, that is a configuration exclusion — record it as a coverage gap
rather than a failure.

### 7. Write the detection, with false positives

`evidence/detection.md`:

| Field | Value |
| --- | --- |
| Title | Encoded PowerShell spawning a shell |
| Logic | Event 1 where `CommandLine` contains `-enc` or `-EncodedCommand`, **and** a child Event 1 has `ParentImage` ending `powershell.exe` and `Image` ending `cmd.exe`, within 60 s |
| Data source | Sysmon 1 (process create) |
| Why it is stronger than the string alone | Requires both the encoded flag and the child shell, which is the actual behaviour |
| False positives | Software deployment agents (SCCM, Intune), some installers, administrative scripts, endpoint management tooling |
| Tuning | Allowlist by parent image and signer for known deployment agents; require the child to be `cmd.exe`/`wscript.exe`/`mshta.exe` rather than any child |
| What it misses | Encoded PowerShell that does not spawn a child; PowerShell 7 naming differences; script-block-only execution |

Then answer: would your rule have fired on **this** activity? It should — this is a true positive by shape, even
though the payload is benign. The distinction between "suspicious behaviour" and "malicious intent" belongs in the
finding, not in the rule.

### 8. State the limitation

In `evidence/limitations.md`, answer: what would an attacker do to avoid this detection, and what telemetry would
catch that variant? Two sentences, specific.

## Evidence to collect

- `evidence/sysmon-version.txt` — file version and signature status.
- `evidence/process-events.csv` — at least two rows with PID, PPID, image, parent, command line, hashes.
- `evidence/tree.txt` — the reconstructed process tree.
- `evidence/decoded.txt` — the harmless decoded payload.
- `evidence/detection.md` — rule, logic, false positives, tuning, gaps.
- `evidence/limitations.md`.

## Verification

- [ ] Sysmon service running, version and signature recorded.
- [ ] The configuration's ProcessCreate and DnsQuery exclusions were read and noted.
- [ ] The generated chain produced at least a PowerShell parent and a `cmd.exe` child, linked by PID/PPID.
- [ ] Command line, parent image, user and hashes all captured from Event ID 1.
- [ ] The decoded payload is recorded and is demonstrably harmless.
- [ ] The detection names a false-positive source and a tuning method.
- [ ] The report distinguishes "suspicious shape" from "malicious".

## Teardown and reset

```powershell
# Keep Sysmon for CYB-404 and CYB-407; remove it only if you need the original state
# & C:\lab\402-03\tools\Sysmon64.exe -u
Remove-Item C:\lab\402-03 -Recurse -Force
```

Detach NAT and confirm isolation. Revert `pre-lab-402-03` if you want no Sysmon and no events.

## Reflection

1. The image names in this chain are all Microsoft binaries. Why does that make name-based detection useless here?
2. Your rule requires a child shell. Describe an encoded-PowerShell intrusion that would not trigger it.
3. Which single field would you add to the rule to reduce deployment-agent false positives, and what does adding it
   cost you in coverage?
4. The payload was harmless, but the rule fired. Is that a false positive? Justify your answer using the categories
   from CYB-401.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Collection | Sysmon not verified | Service running, events present | Version, signature, and config exclusions documented |
| Reconstruction | Reads events individually | PID/PPID chain shown | Chain plus file and DNS context, with gaps named |
| Detection | String match | Behavioural logic | Behavioural logic plus tuning and a named evasion |
| Judgement | Calls it malware | Calls it suspicious | Distinguishes shape from intent and says so in writing |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Sysmon64.exe` will not install | Not elevated, or an old version is running | Run as administrator; `-u` the old install first |
| No Event ID 1 rows | Config excludes the images, or the filter window is too narrow | Widen `StartTime`; check the config's ProcessCreate section |
| `Get-SysmonField` returns nothing | Event XML uses a different structure for that ID | Print `$Event.ToXml()` once and inspect the field names |
| `-EncodedCommand` produces no output | Base64 must be UTF-16LE | Use `[Text.Encoding]::Unicode.GetBytes()` as shown |
| Service running but no events after generation | Sysmon log filter or config update pending | `Sysmon64.exe -c .\sysmonconfig.xml` to reload |
| Hashes field empty | Config excludes hashing for that image | Note it; hashing is optional per configuration |

## References

1. Microsoft Sysinternals — Sysmon v15.22 and configuration schema.
   <https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon> Accessed 2026-10-29.
2. SwiftOnSecurity/sysmon-config; Olaf Hartong/sysmon-modular. Accessed 2026-10-29.
3. MITRE ATT&CK — T1059.001 PowerShell; T1027 Obfuscated Files or Information. Accessed 2026-10-29.
4. SigmaHQ — rule specification. <https://sigmahq.io/> Accessed 2026-10-29.

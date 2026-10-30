---
title: "LAB-403-02 · Windows Controls You Can Prove"
description: "Apply six Windows security controls, verify each by querying its state, and prove two of them with events the system generated."
module_code: CYB-403
level: 4
kind: lab
prerequisites: [CYB-403]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-403-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [windows-hardening, auditpol, sysmon, asr, smb, powershell-logging, laps]
---

# LAB-403-02 · Windows Controls You Can Prove

## Scenario and background

`lab-win` is about to be joined to a monitored segment. A previous administrator "hardened" it by clicking through a
benchmark tool and rebooting. There is no record of what changed, no verification, and no telemetry.

You will apply a small, defensible set of controls, verify each by querying its state, and for two of them produce an
event that the control itself caused — because a configured setting and an observed effect are different claims.

## Learning objectives

1. Enable process-creation auditing with command lines and prove it with a 4688 event.
2. Enable PowerShell script block logging and prove it with a 4104 event containing script text.
3. Remove SMBv1 and require SMB signing, verified by configuration query rather than by wizard.
4. Configure attack surface reduction rules in a way that reports its own state, and discuss why audit mode precedes
   block mode.
5. Capture a before/after control matrix with residual risk for each control.
6. Explain which controls cannot be fully implemented in a workgroup lab, and why.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Windows 11 | 23H2 or later | Windows LAPS is built in from 23H2 |
| PowerShell | 5.1+ | Administrator prompt |
| Microsoft Defender | platform as shipped | `Get-MpPreference`, `Get-MpComputerStatus` |
| Microsoft Security Compliance Toolkit | 1.0 | Optional, for GPO-based deployment; contains LGPO |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab-win` only.
    **Targets you must not use:** any other host or any network service.

    **Two controls change access paths.** Removing SMBv1 is irreversible without a reboot and a feature reinstall;
    requiring SMB signing can break an old appliance that does not support it. In this lab there is no such appliance,
    which is exactly why you test here first.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The host is a workstation on an internal segment with a local administrator account. Covered threats: credential
theft via SMB relay and NTLM coercion, malicious macro and script execution, lateral movement using local admin
credentials, and loss of accountability because process and script activity was never recorded. Not covered here:
domain-based controls, application allowlisting (WDAC/AppLocker), and enterprise password rotation.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-win` | Target and analyst | 192.0.2.40 |
| `lab-ubuntu` | Not used | 192.0.2.20 |

## Before you start

1. Snapshot `pre-lab-403-02`.
2. Open **Windows PowerShell as Administrator**.
3. Create the workspace and capture the baseline state:

```powershell
New-Item -ItemType Directory -Force C:\lab\403-02\evidence | Out-Null
Set-Location C:\lab\403-02

function Get-ControlState {
    [pscustomobject]@{
        Time                = (Get-Date).ToString('o')
        AuditProcessCreation= (auditpol /get /subcategory:"Process Creation" | Out-String).Trim()
        CmdLineInEvents     = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' -ErrorAction SilentlyContinue).ProcessCreationIncludeCmdLine_Enabled
        ScriptBlockLogging  = (Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' -ErrorAction SilentlyContinue).EnableScriptBlockLogging
        SMB1Feature         = (Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol).State
        SMBServer           = Get-SmbServerConfiguration | Select-Object EnableSMB1Protocol, RequireSecuritySignature
        ASR                 = (Get-MpPreference).AttackSurfaceReductionRules_Ids
        ASRActions          = (Get-MpPreference).AttackSurfaceReductionRules_Actions
        Defender            = Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusEnabled
        PUAPolicy           = (Get-MpPreference).PUAProtection
    }
}

Get-ControlState | ConvertTo-Json -Depth 4 | Tee-Object evidence\before.json
```

**Expected:** SMBv1 likely `Enabled` or `Disabled` depending on the image, `RequireSecuritySignature` likely `False`,
script block logging empty, and ASR lists empty. This is your "before" record — keep it exactly as captured.

## Procedure

### 1. Process-creation auditing with command lines

```powershell
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable
New-Item -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' -Force | Out-Null
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' `
  -Name ProcessCreationIncludeCmdLine_Enabled -Value 1 -Type DWord
gpupdate /force | Out-Null
auditpol /get /subcategory:"Process Creation"
```

**Expected:** `Success and Failure` in the auditpol output, and the registry value reads `1`.

Generate a process and find it:

```powershell
cmd.exe /c "echo lab403-02 audit test"
Start-Sleep -Seconds 2

Get-WinEvent -LogName Security -FilterHashtable @{Id=4688; StartTime=(Get-Date).AddMinutes(-2)} -MaxEvents 20 |
  ForEach-Object {
    $x = [xml]$_.ToXml()
    [pscustomobject]@{
      Time    = $_.TimeCreated
      Process = ($x.Event.EventData.Data | Where-Object Name -eq 'NewProcessName').'#text'
      Parent  = ($x.Event.EventData.Data | Where-Object Name -eq 'ParentProcessName').'#text'
      CmdLine = ($x.Event.EventData.Data | Where-Object Name -eq 'CommandLine').'#text'
      User    = ($x.Event.EventData.Data | Where-Object Name -eq 'SubjectUserName').'#text'
    }
  } | Where-Object Process -match 'cmd.exe' |
  Format-Table -AutoSize | Tee-Object evidence\4688-test.txt
```

**Expected:** a `cmd.exe` row with the `/c "echo lab403-02 audit test"` command line and a parent process. If the
`CmdLine` column is empty, the policy registry value has not taken effect — reboot or re-run `gpupdate`, then repeat.

**Why this control first:** almost every detection you write in CYB-404 depends on a command line existing. 4688
without command-line auditing is a process name and a timestamp.

### 2. PowerShell script block logging

```powershell
$key = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging'
New-Item -Path $key -Force | Out-Null
Set-ItemProperty -Path $key -Name EnableScriptBlockLogging -Value 1 -Type DWord
(Get-ItemProperty $key).EnableScriptBlockLogging

# Generate a script block with a distinctive marker
@'
$marker = 'LAB403-02-SCRIPTBLOCK'
Write-Output "hello $marker"
Get-Date
'@ | Set-Content C:\lab\403-02\probe.ps1

powershell.exe -NoProfile -File C:\lab\403-02\probe.ps1
Start-Sleep -Seconds 3

Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' `
  -FilterHashtable @{Id=4104; StartTime=(Get-Date).AddMinutes(-3)} -MaxEvents 10 |
  Where-Object { $_.Message -match 'LAB403-02-SCRIPTBLOCK' } |
  Select-Object TimeCreated, Id, @{n='Excerpt';e={($_.Message -split "`n" | Select-Object -First 6) -join ' | '}} |
  Format-List | Tee-Object evidence\4104-test.txt
```

**Expected:** at least one 4104 event whose text contains `LAB403-02-SCRIPTBLOCK`. That is the script's **content**,
recorded independently of the file — which is why this logging matters: deleting `probe.ps1` does not delete the
evidence.

**If no event appears:** script block logging applies to new PowerShell processes, so the probe must run *after* the
policy is set (it does here); check the policy value and retry in a fresh `powershell.exe`.

### 3. Remove SMBv1

```powershell
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol | Select-Object FeatureName, State
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol | Select-Object FeatureName, State
Get-SmbServerConfiguration | Select-Object EnableSMB1Protocol
```

**Expected:** state moves to `Disabled` (or `DisablePending` until reboot) and `EnableSMB1Protocol` is `False`.

**Why it is safe here and not everywhere:** some legacy scanners, NAS appliances and industrial systems still speak
SMBv1. In this lab there are none. In production you would inventory SMBv1 clients first, because the control breaks
them silently.

### 4. Require SMB signing

```powershell
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature, EnableSecuritySignature
Set-SmbServerConfiguration -RequireSecuritySignature $true -Force
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature
Get-SmbClientConfiguration | Select-Object RequireSecuritySignature
```

**Expected:** server-side `RequireSecuritySignature` is `True`.

**The threat this addresses:** NTLM relay. An attacker who can coerce authentication and relay it to an SMB server
that does not require signing can act as the victim without knowing the password. Signing breaks the relay because
the attacker cannot produce a valid signature for the relayed session.

### 5. Attack surface reduction rules — audit first

Verify the GUIDs against Microsoft's ASR reference before applying them: a mistyped GUID is accepted silently and
protects nothing.

```powershell
$rules = @{
  '9e6c4e1f-7d60-472f-ba1a-a39ef669e4b2' = 'Block credential stealing from lsass.exe'
  'd4f940ab-401b-4efc-aadc-ad5f3c50688a' = 'Block Office applications from creating child processes'
  '5beb7efe-fd9a-4556-801d-275e5ffc04cc' = 'Block execution of potentially obfuscated scripts'
}

# Stage 1: audit mode - observe before enforcing
Add-MpPreference -AttackSurfaceReductionRules_Ids $rules.Keys -AttackSurfaceReductionRules_Actions AuditMode
(Get-MpPreference).AttackSurfaceReductionRules_Ids
(Get-MpPreference).AttackSurfaceReductionRules_Actions
```

**Expected:** three IDs and three `AuditMode` actions. Record both, in the same order, and check they line up — the
two arrays are positional.

Then observe a real trigger attempt in audit mode:

```powershell
$inner = "Write-Output 'LAB403-02-ASR benign'"
$enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($inner))
powershell.exe -NoProfile -EncodedCommand $enc

Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' `
  -FilterHashtable @{Id=1121,1122; StartTime=(Get-Date).AddMinutes(-3)} -ErrorAction SilentlyContinue |
  Select-Object TimeCreated, Id, @{n='Rule';e={($_.Message -split "`n" | Where-Object {$_ -match 'rule|ASR'} | Select-Object -First 1)}} |
  Format-List | Tee-Object evidence\asr-events.txt
```

**Expected:** event **1122** (rule audited) if the obfuscated-script rule considered the encoded command suspicious.
It may not fire — the rule inspects script content and behaviour, not merely the presence of base64. **Either result
is a valid finding.** Record what happened: "audit event observed" or "no audit event; rule did not classify this
invocation".

Then switch to block mode and re-query state:

```powershell
Add-MpPreference -AttackSurfaceReductionRules_Ids $rules.Keys -AttackSurfaceReductionRules_Actions Enabled
(Get-MpPreference).AttackSurfaceReductionRules_Actions
```

**Expected:** three `Enabled` actions. The configuration is now provably on; whether it blocks a given behaviour is a
separate question that depends on the rule, the application and the Defender platform version. Write that distinction
in your notes rather than claiming the control "works".

### 6. Defender baseline and PUA protection

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AMServiceEnabled
Set-MpPreference -PUAProtection Enabled
(Get-MpPreference).PUAProtection
```

**Expected:** real-time protection enabled (if it is not, this is a finding — investigate before continuing), and
`PUAProtection` set to `1` (Enabled).

**Workgroup limitation.** Windows LAPS manages local administrator password rotation and is built into Windows 11
23H2 and later — but it needs Active Directory or Entra ID to escrow the password, so it cannot be completed in a
workgroup lab. Legacy Microsoft LAPS (the MSI) is deprecated. Note this as an environmental limitation; the control
matrix must say "not applicable in this environment", not "done".

## Deliverable: the control matrix

`evidence/control-matrix.md`:

| # | Control | Threat addressed | Configured state (query) | Effect proven? | Residual risk | What it could break |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 4688 + command line | Accountability for execution | `auditpol` output; registry `=1` | Yes — 4688 with command line | Log volume; 4688 can be disabled by an admin | Performance on very busy hosts |
| 2 | Script block logging | Obfuscated script visibility | Registry `=1` | Yes — 4104 with marker text | Scripts can be run in ways that log less | Log size; secrets appearing in logs |
| 3 | SMBv1 removed | Legacy protocol exploitation | Feature `Disabled` | Configuration only | Other legacy protocols remain | Old scanners, NAS, appliances |
| 4 | SMB signing required | NTLM relay | `RequireSecuritySignature=True` | Configuration only | Signing is not encryption | Legacy clients without signing |
| 5 | ASR rules | Credential theft, macro spawn, script abuse | Three IDs, actions `Enabled` | Attempted; see `asr-events.txt` | Not a sandbox; bypasses exist | Line-of-business macros and installers |
| 6 | Defender PUA | Unwanted software | `PUAProtection=1` | Configuration only | Does not replace allowlisting | Some legitimate admin tools flagged |

Add a short paragraph: which of the six would you roll out to 500 workstations first, and why?

## Evidence to collect

- `evidence/before.json` and `evidence/after.json` — the same state function, run before and after.
- `evidence/4688-test.txt` — process event with a command line.
- `evidence/4104-test.txt` — script block event containing the marker.
- `evidence/asr-events.txt` — audit or block events, or a note that none appeared.
- `evidence/control-matrix.md`
- `evidence/notes.md` — rollout order, limitations, and the configuration-vs-effect distinction.

## Verification

- [ ] Before/after JSON captured with the same function, so the diff is meaningful.
- [ ] 4688 evidence includes the command line, parent process and user.
- [ ] 4104 evidence contains the marker from the probe script.
- [ ] SMBv1 state queried after the change, and `EnableSMB1Protocol` is `False`.
- [ ] SMB signing requirement queried on both server and client side.
- [ ] ASR GUIDs checked against the vendor reference before use, and ID-to-action alignment confirmed.
- [ ] The ASR section reports what actually happened, including "no event".
- [ ] LAPS is recorded as not applicable, with the reason.
- [ ] Every row in the matrix names a residual risk.

## Teardown and reset

```powershell
# Remove the audit policy and logging changes
auditpol /set /subcategory:"Process Creation" /success:disable /failure:disable
Remove-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' -Name ProcessCreationIncludeCmdLine_Enabled -ErrorAction SilentlyContinue
Remove-Item 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' -Recurse -Force -ErrorAction SilentlyContinue

# Clear ASR rules
$ids = (Get-MpPreference).AttackSurfaceReductionRules_Ids
if ($ids) { Remove-MpPreference -AttackSurfaceReductionRules_Ids $ids }

# Copy evidence out before reverting
New-Item -ItemType Directory -Force C:\Users\Public\lab403-02-evidence | Out-Null
Copy-Item C:\lab\403-02\evidence\* -Destination C:\Users\Public\lab403-02-evidence -Recurse -Force
```

Reboot if SMBv1 removal is pending. Revert `pre-lab-403-02` to restore the original image; note that SMB1 removal is
not undone by deleting files.

## Reflection

1. You proved 4688 and 4104 with events, but only configured SMB signing. Is "configuration queried" weaker
   evidence than "event observed"? For which control would you insist on an effect test, and why?
2. The ASR obfuscated-script rule may not fire on a base64 command. What does that tell you about rule names as
   descriptions of behaviour?
3. Why is audit mode a prerequisite for block mode in a real deployment, even when you are confident in the rule?
4. Which of these six controls would an attacker with local administrator rights simply turn off, and what would you
   need to detect that?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Configuration | Applied without verification | State queried per control | Before/after captured with one function, alignment checked |
| Evidence | Screenshots of dialogs | One event demonstrated | Both event-backed controls demonstrated, ASR result reported honestly |
| Reasoning | Controls listed | Threats mapped | Residual risk and breakage named per control; audit-before-block justified |
| Judgement | Claims "hardened" | Notes limitations | Distinguishes configuration from effect and states what cannot be done here |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| 4688 events have no command line | Policy value not applied | Reboot or `gpupdate /force`; re-check the registry value |
| No 4104 events | Logging enabled after the script ran | Re-run `powershell.exe -File` after setting the policy |
| `Disable-WindowsOptionalFeature` fails | Feature in use, or not elevated | Reboot, run elevated; check `Get-WindowsOptionalFeature` |
| `Set-SmbServerConfiguration` access denied | Not elevated | Administrator PowerShell |
| ASR IDs show but actions do not match | Arrays applied positionally in a different order | Re-apply with `-Ids` and `-Actions` in the same order |
| Defender log empty | Events filtered by time window | Widen `StartTime`; check `Get-WinEvent -ListLog *Defender*` |
| `Get-MpComputerStatus` says real-time off | Tamper protection or policy | Investigate as a finding; do not simply toggle it |

## References

1. Microsoft — Security Compliance Toolkit 1.0 and LGPO.
   <https://learn.microsoft.com/en-us/windows/security/operating-system-security/device-management/windows-security-configuration-framework/security-compliance-toolkit-10> Accessed 2026-10-29.
2. Microsoft — Attack surface reduction rules reference (verify GUIDs here).
   <https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-reference> Accessed 2026-10-29.
3. Microsoft — Command line process auditing (4688) and PowerShell script block logging (4104). Accessed 2026-10-29.
4. Microsoft — Windows LAPS overview; legacy LAPS deprecation.
   <https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview> Accessed 2026-10-29.
5. Microsoft — SMB security settings and NTLM relay mitigations. Accessed 2026-10-29.
6. MITRE ATT&CK — T1566, T1059, T1003, T1557.001. Accessed 2026-10-29.

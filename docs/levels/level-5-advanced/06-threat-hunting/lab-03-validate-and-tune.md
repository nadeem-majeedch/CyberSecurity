---
title: "LAB-506-03 · Final Challenge: Validate and Tune"
description: "Simulate a technique safely, prove the rule fires, measure false positives on labelled hits, then tune without silencing the LOLBins you excluded."
module_code: CYB-506
level: 5
kind: lab
prerequisites: [CYB-506]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-506-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [detection-validation, false-positives, tuning, lolbins, final-challenge]
---

# LAB-506-03 · Final Challenge: Validate and Tune

## Scenario and background

You proposed a detection in LAB-506-02: a scheduled task whose action contains an encoded command. Now you have to
prove it works, then survive the part that kills most detections — the false positives.

This lab has three movements: **validate** the rule with a safe simulation, **measure** it on 30 labelled hits, and
**tune** it without turning off the alerts that matter. The measured result is uncomfortable on purpose: the obvious
tuning removes every false positive *and* three real detections.

## Learning objectives

1. Validate a detection with a positive, negative and boundary test.
2. Measure precision and recall on a labelled hit set instead of estimating them.
3. Tune by adding distinguishing attributes, and quantify what the tuning loses.
4. Recognise when a rule excludes the exact binaries attackers abuse (LOLBins).
5. Record the trade-off in a form a reviewer can challenge.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Windows VM | 10/11 evaluation | From CYB-504, snapshot first |
| Sysmon | 15.x | From CYB-402 |
| Python | 3.10+ | For the measurement |

## Safety

The simulation creates a scheduled task that runs an **encoded command which prints a string**. It makes no network
connection, changes no security setting, and is removed at the end. Snapshot first; revert is the reset.

Do not simulate anything that alters defences (disabling logging, tampering with AV). That is out of scope for a course
lab and is a real incident if done on a system you do not own.

## Part A — Validate with a safe simulation

### 1. Positive test

On the analysis VM, elevated PowerShell:

```powershell
$payload = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("Write-Output 'SYNTH-VALIDATION-OK'"))
$action  = "powershell -nop -w hidden -enc $payload"
schtasks /create /tn "SynthValidation" /tr $action /sc once /st 23:59 /f
schtasks /query /tn "SynthValidation" /v /fo LIST
```

**Expected:** the task exists and its "Task To Run" contains `-enc` and the base64 string. Now confirm the telemetry:

```powershell
Get-WinEvent -FilterHashtable @{LogName="Security"; Id=4698} -MaxEvents 5 |
  Where-Object { $_.Message -match "SynthValidation" } |
  Select-Object TimeCreated, Id, Message
```

**Expected:** one event 4698 with the task XML, including the encoded action. If you see nothing, your audit policy does
not log task creation — that is a **data gap**, and you must record it rather than assume the rule works.

**The negative test:**

```powershell
schtasks /create /tn "SynthBenign" /tr "cmd /c echo hello" /sc once /st 23:58 /f
```

**Expected:** the task is created, and your rule does **not** alert, because there is no encoded command and no
user-writable path. A rule that fires here is matching "task created", not "task is suspicious".

**The boundary test:** a task whose action contains the literal text `-enc` inside a file path, for example:

```powershell
schtasks /create /tn "SynthBoundary" /tr "cmd /c echo C:\temp\-enc-notes.txt" /sc once /st 23:57 /f
```

Decide whether it should alert. Either answer is defensible; **not deciding is not**, because the rule will decide for
you and nobody will know which way.

Clean up:

```powershell
schtasks /delete /tn "SynthValidation" /f
schtasks /delete /tn "SynthBenign" /f
schtasks /delete /tn "SynthBoundary" /f
```

### 2. Record the test

`validation.md`:

| Test | Action | Expected | Observed | Pass? |
| --- | --- | --- | --- | --- |
| Positive | Task with `-enc` payload | Alert | | |
| Negative | Task running `cmd /c echo hello` | No alert | | |
| Boundary | Path containing `-enc` | Documented decision | | |
| Data path | Event present in collector | Event with task XML | | |

**What this does not prove:** that the rule catches an adversary who uses a different parent process, a different
encoding, or a signed binary. Write that sentence; it is the most important line in the document.

## Part B — Measure false positives

### 3. The hit set

```bash
mkdir -p ~/hunt-lab/tuning && cd ~/hunt-lab/tuning
```

`rule-hits.csv` — 30 historical hits from the naive version of your rule (any process with a suspicious parent or
path), labelled by an analyst:

```csv
hit_id,image,path,parent,signed,user,label
H-01,powershell.exe,C:\Users\a.khan\AppData\Local\Temp\svch0st.exe,outlook.exe,false,a.khan,malicious
H-02,certutil.exe,C:\Windows\System32\certutil.exe,cmd.exe,true,a.khan,malicious
H-03,schtasks.exe,C:\Windows\System32\schtasks.exe,powershell.exe,true,a.khan,malicious
H-04,rundll32.exe,C:\Users\public\upd.dat,explorer.exe,false,a.khan,malicious
H-05,powershell.exe,C:\ProgramData\sync\run.ps1,wscript.exe,false,a.khan,malicious
H-06,mshta.exe,C:\Users\a.khan\AppData\Roaming\cache\x.hta,chrome.exe,true,a.khan,malicious
H-07,wmic.exe,C:\Windows\System32\wbem\wmic.exe,cmd.exe,true,a.khan,malicious
H-08,powershell.exe,C:\Users\a.khan\AppData\Local\Temp\a.ps1,winword.exe,true,a.khan,malicious
H-09,backup.exe,C:\Program Files\Acme\backup.exe,services.exe,true,svc-backup,benign
H-10,monitor.exe,C:\Program Files\Acme\monitor.exe,services.exe,true,svc-mon,benign
H-11,powershell.exe,C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe,explorer.exe,true,a.khan,benign
H-12,update.exe,C:\Program Files\Acme\update.exe,services.exe,true,system,benign
H-13,powershell.exe,C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe,code.exe,true,a.khan,benign
H-14,inventory.exe,C:\Program Files\Acme\inventory.exe,services.exe,true,system,benign
H-15,cmd.exe,C:\Windows\System32\cmd.exe,explorer.exe,true,a.khan,benign
H-16,powershell.exe,C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe,excel.exe,true,a.khan,benign
H-17,agent.exe,C:\Program Files\Acme\agent.exe,services.exe,true,system,benign
H-18,schtasks.exe,C:\Windows\System32\schtasks.exe,mmc.exe,true,admin1,benign
H-19,robocopy.exe,C:\Windows\System32\Robocopy.exe,cmd.exe,true,admin1,benign
H-20,powershell.exe,C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe,explorer.exe,true,admin1,benign
H-21,notepad.exe,C:\Windows\System32\notepad.exe,explorer.exe,true,a.khan,benign
H-22,excel.exe,C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE,explorer.exe,true,a.khan,benign
H-23,certutil.exe,C:\Windows\System32\certutil.exe,mmc.exe,true,admin1,benign
H-24,powershell.exe,C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe,svchost.exe,true,system,benign
H-25,wmic.exe,C:\Windows\System32\wbem\wmic.exe,services.exe,true,system,benign
H-26,installer.exe,C:\Program Files\Acme\installer.exe,explorer.exe,true,a.khan,benign
H-27,cmd.exe,C:\Windows\System32\cmd.exe,services.exe,true,system,benign
H-28,powershell.exe,C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe,explorer.exe,true,a.khan,benign
H-29,mshta.exe,C:\Windows\System32\mshta.exe,explorer.exe,true,a.khan,benign
H-30,powershell.exe,C:\Program Files\Acme\agent\health.ps1,services.exe,true,system,benign
```

### 4. Baseline measurement

`tune.py`:

```python
#!/usr/bin/env python3
"""Compare the baseline rule with a tuned version on labelled hits."""
import csv

rows = list(csv.DictReader(open("rule-hits.csv", encoding="utf-8")))
USER_DIRS = ("/temp/", "/appdata/", "/users/public/", "/programdata/")
OFFICE_PARENTS = {"outlook.exe", "winword.exe", "excel.exe", "chrome.exe"}


def normalise(path):
    return path.lower().replace("\\", "/")


def baseline(row):
    return True


def tuned(row):
    path = normalise(row["path"])
    in_system = path.startswith("c:/windows/system32") or path.startswith("c:/program files")
    if row["signed"] == "true" and in_system:
        return False
    return any(d in path for d in USER_DIRS) or row["parent"].lower() in OFFICE_PARENTS


for name, rule in (("baseline", baseline), ("tuned", tuned)):
    hits = [r for r in rows if rule(r)]
    tp = sum(1 for r in hits if r["label"] == "malicious")
    fp = len(hits) - tp
    print(f"{name:9} alerts={len(hits):2} tp={tp} fp={fp:2} precision={tp / len(hits):.2f} recall={tp / 8:.2f}")
    if name == "tuned":
        print("  missed:", [r["hit_id"] for r in rows if r["label"] == "malicious" and not rule(r)])
        print("  remaining fp:", [r["hit_id"] for r in hits if r["label"] == "benign"])
```

```bash
python3 tune.py
```

**Expected:**

```text
baseline  alerts=30 tp=8 fp=22 precision=0.27 recall=1.00
tuned     alerts= 5 tp=5 fp= 0 precision=1.00 recall=0.62
  missed: ['H-02', 'H-03', 'H-07']
  remaining fp: []
```

### 5. Read the result honestly

The tuned rule looks perfect — precision 1.00 — and it is **worse in the way that matters**. The three events it lost are
`certutil.exe`, `schtasks.exe` and `wmic.exe`: signed Microsoft binaries, in `System32`, abused as LOLBins. The tuning
excluded exactly the population that real intrusions hide in.

This is the lesson of the lab, and it repeats everywhere:

| Tuning move | FPs removed | What it costs |
| --- | --- | --- |
| Exclude signed binaries in `System32` | 22 | Drops three LOLBin detections |
| Exclude by process name (`backup.exe`) | Many | Attacker names their binary `backup.exe` |
| Raise threshold | Some | Slow attacks fall below it |
| Alert only on unsigned binaries | Many | Misses signed-but-abused tooling |

**The fix is not to revert.** It is to add the *command line* as a third dimension, which the hit set does not contain —
a data gap you should name:

```text
Rule: process created where
  (path in user-writable dir OR parent is a mail client/browser) AND (unsigned OR command line matches LOLBin flags)
```

`certutil -urlcache -f`, `schtasks /create /tr ... -enc`, `wmic process call create` are the flags that separate
abuse from administration. Without command-line telemetry you cannot write that rule, and "we cannot write it" is the
finding.

### 6. Write the tuning record

`tuning.md`:

```markdown
## Change
Replaced "any suspicious-parent process" with "user-writable path OR office/browser parent", excluding signed system
binaries.

## Measured effect
Hits 30 → 5. Precision 0.27 → 1.00. Recall 1.00 → 0.62.
Lost: H-02 certutil, H-03 schtasks, H-07 wmic — all LOLBin abuse.

## Decision
Do not deploy as tuned. Add command-line conditions for LOLBins, then re-measure on this same set (expected: recover
H-02/03/07, keep FP at 0).

## Trade-off stated
Precision without recall is a quiet failure: fewer alerts, more breaches.

## Not covered
The set is 30 labelled hits; it says nothing about prevalence in production. A real evaluation needs a month of
untuned hits.
```

### 7. Recover the LOLBins

Add the command-line dimension (invent plausible command lines for H-02/H-03/H-07, or extend the CSV with a
`cmdline` column and label it). Re-run and report the new precision/recall. The expected outcome is precision 1.00
with recall 1.00 **on this set** — and the note that a 30-row set cannot validate a rule for production.

## Deliverables

- `validation.md` with the four-row test table and the "does not prove" sentence.
- `rule-hits.csv`, `tune.py`, and both measurement outputs.
- `tuning.md` with change, measurement, decision, trade-off and limits.
- The LOLBin-recovered rule with its new numbers.

## Verification

- [ ] Positive test produced a real 4698 event containing the encoded action, or the gap is documented.
- [ ] Negative test produced a task and no alert.
- [ ] Boundary decision recorded, not left implicit.
- [ ] Baseline and tuned precision/recall measured, matching `tp=8 fp=22` and `tp=5 fp=0`.
- [ ] The three lost LOLBin detections identified by name and technique.
- [ ] Decision is not "deploy the tuned rule" without addressing the loss.
- [ ] Limitations of a 30-row labelled set stated.

## Teardown and reset

```powershell
schtasks /delete /tn "SynthValidation" /f 2>$null
schtasks /delete /tn "SynthBenign" /f 2>$null
schtasks /delete /tn "SynthBoundary" /f 2>$null
```

Then revert the VM snapshot. Nothing was sent anywhere.

## Reflection

1. Precision went to 1.00 and the rule got worse. Explain that to a manager in two sentences.
2. Why is "exclude signed binaries" a defensible *starting* filter and an indefensible *only* filter?
3. Your positive test used `powershell.exe`. What other binaries could achieve the same outcome, and would the rule
   catch them?
4. What would it take to measure this rule's false-positive rate in production, and why is a lab hit set not enough?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Validation | Ran the task | Positive and negative | Boundary decided; data path confirmed; limits stated |
| Measurement | Estimated | Computed | Precision and recall both, on labelled data |
| Tuning | Removed alerts | Reduced FPs | Quantified recall loss and identified LOLBin exclusion |
| Judgement | Deployed anyway | Noted the risk | Chose to keep recall and specified the missing dimension |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No 4698 events | Audit policy not enabled | `auditpol /set /subcategory:"Other Object Access Events" /success:enable` |
| Task creation denied | Not elevated | Run PowerShell as administrator |
| `tune.py` precision 1.00 immediately | Baseline function returns True only for one class | Check the `baseline` function |
| Zero recall | Encoding mismatch in labels | Print the label column and confirm `malicious` spelling |
| Path comparisons fail | Backslash escaping | Normalise separators, as `normalise()` does |

## References

1. MITRE ATT&CK — T1053.005, T1059.001, T1140; LOLBins in T1218 and sub-techniques. Accessed 2026-10-29.
2. Microsoft — `schtasks` and event 4698 documentation. Accessed 2026-10-29.
3. LOLBAS Project — living-off-the-land binaries and their command lines. Accessed 2026-10-29.
4. NIST SP 800-137 — continuous monitoring and metric definition. Accessed 2026-10-29.

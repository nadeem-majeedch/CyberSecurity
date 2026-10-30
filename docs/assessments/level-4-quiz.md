---
title: "Level 4 Module Quizzes — Defensive Operations"
description: "Thirty-five self-check items across CYB-401 to CYB-407: triage, telemetry, hardening, detection, network defence, forensics and incident response."
module_code: ASM-L4
level: 4
kind: assessment
prerequisites: [CYB-401]
estimated_minutes: 110
difficulty: advanced
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, quiz, level-4, soc, detection, forensics]
---

# Level 4 Module Quizzes

Five items per module, seven modules, thirty-five items. Every scenario uses synthetic logs or the isolated lab.
Do not paste real organisational logs into an external service to answer a question.

**Protocol.** Attempt on paper, then mark against the [Level 4 answer key](level-4-key.md). Target 4 of 5 per
module. Items marked (Scenario) expect a decision **and** the evidence that supports it.

---

## CYB-401 · SOC Operations, ATT&CK and Threat Intelligence

**Q401.1** (MCQ) Two alerts arrive together. Which do you escalate first?

- A. A critical-severity signature hit on a developer laptop with no follow-on activity
- B. A medium-severity alert on a domain controller showing a new service created and a successful network logon
  from an unusual host
- C. A low-severity alert that fired 400 times yesterday
- D. A high-severity alert on a test system that is decommissioned

**Q401.2** (MCQ) A user really did install a legitimate remote-support tool, and the rule fired correctly. What
is this?

- A. False positive
- B. Benign true positive
- C. False negative
- D. True negative

**Q401.3** (MCQ) A scheduled task is created to run a script at logon. Which ATT&CK tactic does this primarily
represent?

- A. Initial Access
- B. Persistence
- C. Exfiltration
- D. Reconnaissance

**Q401.4** (Short) An indicator is a domain seen in a six-month-old report with medium confidence. State the
action you would take and why, naming the three properties you weighed.

**Q401.5** (Scenario) Write the four elements a handover note must contain for an alert you are leaving open at
the end of your shift, and explain why "investigating" is not one of them.

---

## CYB-402 · Endpoint Telemetry and Authentication Monitoring

**Q402.1** (MCQ) Windows event 4624 with logon type 3 indicates what?

- A. An interactive console logon
- B. A network logon, such as an SMB or IIS authentication
- C. A remote-desktop session
- D. A service account start

**Q402.2** (MCQ) Which parent-child relationship is most suspicious?

- A. `explorer.exe` → `notepad.exe`
- B. `winword.exe` → `powershell.exe` with an encoded command
- C. `services.exe` → `svchost.exe`
- D. `cmd.exe` → `ping.exe`

**Q402.3** (MCQ) Which Sysmon event records process creation with a command line?

- A. Event ID 1
- B. Event ID 3
- C. Event ID 11
- D. Event ID 22

**Q402.4** (Short) Why is the command line more informative than the process name when judging whether an
execution is malicious?

**Q402.5** (Scenario) `auth.log` shows 200 failures for `admin` from one address and 3 failures each for 60
different usernames from another. Name both patterns, and the control each one defeats.

---

## CYB-403 · Hardening, Baselines and Vulnerability Management

**Q403.1** (MCQ) Which combination best prioritises a vulnerability list?

- A. CVSS score alone, highest first
- B. Exploitability (KEV/EPSS), exposure, asset value, and compensating controls
- C. Age of the CVE
- D. Vendor severity rating alone

**Q403.2** (MCQ) What distinguishes a CIS Level 2 profile from Level 1?

- A. Level 2 is for servers, Level 1 for workstations
- B. Level 2 applies stricter controls intended for high-security environments, with more operational impact
- C. Level 2 is optional and Level 1 is mandatory by law
- D. Level 2 excludes auditing controls

**Q403.3** (MCQ) Which metric actually shows whether patch SLAs are being met?

- A. Number of patches released this month
- B. Percentage of assets remediated within the SLA for their severity, measured by exposure age
- C. Mean CVSS of open findings
- D. Number of scans completed

**Q403.4** (Short) Name four fields a deviation or exception register must contain to be accepted by a reviewer.

**Q403.5** (Scenario) OpenSCAP reports 40 failed rules on a web server. Describe your triage in three steps and
state what you would record for a rule you decide not to fix.

---

## CYB-404 · Detection Engineering and SIEM

**Q404.1** (MCQ) Why does field normalisation decide whether correlation works?

- A. It makes queries faster
- B. Rules join on common field names and types; inconsistent names silently prevent matches
- C. It compresses storage
- D. It removes the need for a parser

**Q404.2** (MCQ) Which set of tests should every new detection rule pass?

- A. A positive test and a performance test
- B. Positive, negative, no-data, and a tuned/regression test after any exception
- C. A positive test only, in production
- D. A review by two analysts

**Q404.3** (MCQ) What does the no-data test prove?

- A. That the rule performs well under load
- B. That the rule would not silently pass when its data source is missing or misnamed
- C. That the rule has no false positives
- D. That the alert will reach the ticketing system

**Q404.4** (Short) State the three components of a falsifiable detection hypothesis.

**Q404.5** (Scenario) A rule fires 300 times a day. You add an exception for the noisy service account and it
drops to 10. Why is that not tuning, and what would you do instead?

---

## CYB-405 · Network Defence and Monitoring

**Q405.1** (MCQ) What does a default-deny zone policy require to be usable?

- A. A list of every application in the organisation
- B. An explicit, justified allowlist of flows, with logging of what is denied
- C. A firewall on every host
- D. Encrypted DNS

**Q405.2** (MCQ) How do you verify a new `nftables` ruleset?

- A. Reload it and check the service is active
- B. Test an allowed flow and a denied flow, and confirm both the behaviour and the deny counter
- C. Run `nft list ruleset`
- D. Reboot and see whether the network works

**Q405.3** (MCQ) Which statement about TLS interception is correct?

- A. It is a technical decision that SIEM teams can make alone
- B. It is a legal, ethical and privacy decision that requires authorization and a documented scope
- C. It is required by every IDS
- D. It has no effect on user trust

**Q405.4** (Short) Name two things TLS hides from a network sensor and three pieces of metadata that remain.

**Q405.5** (Scenario) You see periodic 60-second DNS queries to random-looking subdomains of one parent domain,
each returning a TXT record. Give two hypotheses and the evidence that distinguishes them.

---

## CYB-406 · Digital Forensics

**Q406.1** (MCQ) What does forensic soundness require?

- A. Using the newest tools available
- B. Acquiring a copy, hashing before and after, verifying the hash, and analysing only the copy
- C. Working quickly before the attacker returns
- D. Encrypting the evidence drive

**Q406.2** (MCQ) Which item does a chain-of-custody record NOT need?

- A. Who handled the evidence, when, and why
- B. The hash of the evidence at each transfer
- C. The investigator's opinion of the suspect
- D. Storage location and conditions

**Q406.3** (MCQ) In a MACB timeline, what does the "B" represent?

- A. Backup time
- B. Birth (creation) time
- C. Block allocation time
- D. Boot time

**Q406.4** (Short) Why is a YARA match a lead rather than a conclusion?

**Q406.5** (Scenario) You need to establish which process opened a connection at the time of an incident. Name the
evidence source you would use, why disk alone may not answer it, and what you must preserve first.

---

## CYB-407 · Incident Response

**Q407.1** (MCQ) Which sequence matches the NIST SP 800-61 phases?

- A. Preparation; detection and analysis; containment, eradication and recovery; post-incident activity
- B. Detection; containment; reporting; billing
- C. Identify; protect; detect; respond; recover
- D. Triage; escalation; closure; review

**Q407.2** (MCQ) Why is "power off the infected host" often the wrong first containment step?

- A. It voids the warranty
- B. It destroys volatile evidence and may trigger destructive malware behaviour
- C. It takes too long
- D. It is always right; the question is a trick

**Q407.3** (MCQ) Which action preserves the most evidence on a suspected ransomware host?

- A. Shut down immediately
- B. Isolate it from the network while keeping it powered, then acquire memory before disk
- C. Run an antivirus scan and delete detections
- D. Reimage it and restore from backup

**Q407.4** (Short) Distinguish root cause from contributing factor, with one example of each.

**Q407.5** (Scenario) Two hosts' logs differ by seven minutes and you must state when a file was encrypted.
Describe your method and how you express the result.

---

## Troubleshooting exercises

**T407.1** A Wazuh rule never fires in production but passes `wazuh-logtest`. Name three causes and the check
for each.

**T407.2** A disk image's hash does not match the acquisition record. State what you do, in order, and what you
must not do.

**T407.3** A packet capture shows a host sending 1.5 MB to an external address at 03:00, but no matching proxy
log exists. Give two explanations consistent with both observations.

---

## Practical challenges

| Module | Challenge | Where |
| --- | --- | --- |
| CYB-401 | Triage a queue and write a handover another analyst can continue | [LAB-401-01](../levels/level-4-defensive-operations/01-soc-operations/lab-01-alert-triage.md) |
| CYB-402 | Reconstruct a process sequence from Sysmon and decide what is suspicious | [LAB-402-03](../levels/level-4-defensive-operations/02-endpoint-telemetry/lab-03-sysmon-process-sequence.md) |
| CYB-403 | Prioritise a vulnerability list and justify the order with evidence | [LAB-403-03](../levels/level-4-defensive-operations/03-hardening-and-patching/lab-03-vulnerability-prioritisation.md) |
| CYB-404 | Write a Sigma rule and validate it with four tests | [LAB-404-02](../levels/level-4-defensive-operations/04-detection-and-siem/lab-02-sigma-rule.md) |
| CYB-405 | Write a Suricata rule, generate traffic, and confirm the alert in `eve.json` | [LAB-405-02](../levels/level-4-defensive-operations/05-network-defence/lab-02-suricata-ids.md) |
| CYB-406 | Acquire, hash, and analyse a disk image without touching the original | [LAB-406-01](../levels/level-4-defensive-operations/06-digital-forensics/lab-01-acquisition-and-custody.md) |
| CYB-407 | Contain a simulated ransomware incident while preserving evidence | [LAB-407-03](../levels/level-4-defensive-operations/07-incident-response/lab-03-ransomware.md) |

---

## Next

- [Level 4 answer key](level-4-key.md)
- [Level 4 integrated assessment](level-4-assessment.md)
- [Level 4 overview](../levels/level-4.md)

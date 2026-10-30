---
title: "CYB-407 · Incident Response"
description: "Run an incident from triage to recovery: preserve evidence, contain without destroying it, decide under uncertainty, and write the report."
module_code: CYB-407
level: 4
kind: reference
prerequisites: [CYB-406, CYB-404]
estimated_minutes: 720
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-407-01, LAB-407-02, LAB-407-03, LAB-407-04]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [incident-response, nist-800-61, containment, ransomware, phishing, reporting, tabletop]
---

# CYB-407 · Incident Response

**Level 4** · 12 hours · **Prerequisites:** [CYB-406](../06-digital-forensics/index.md), [CYB-404](../04-detection-and-siem/index.md)

## Why this module exists

Everything so far produces information. Incident response is where information becomes decisions with consequences:
isolate a host and lose the memory evidence, or preserve it and give the attacker another hour.

The professional skill is not having the right answer immediately. It is acting in a defined order, recording why,
and being able to explain the trade-off afterwards — including when the decision turns out badly.

## Module outcomes

By the end of this module you can:

- Apply the NIST SP 800-61 phases — preparation, detection and analysis, containment/eradication/recovery, and
  post-incident activity — to a concrete incident.
- Triage a reported phishing email, extract defensible indicators, and decide scope before containment.
- Build a master timeline from heterogeneous evidence, correcting for timezone and clock skew.
- Contain a simulated ransomware incident on an isolated host while preserving evidence.
- Decide between restore, rebuild and continued operation, and justify it with recovery objectives.
- Write an incident report with root cause, impact, containment, recovery, and lessons learned that are actionable.
- Run a tabletop exercise and produce a post-incident review that names decisions and alternatives.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Phases, Decisions and Evidence](01-incident-response-phases.md) | 3 h |
| Lab | [LAB-407-01 · Phishing Triage and Scope](lab-01-phishing-triage.md) | 2.5 h |
| Lab | [LAB-407-02 · Master Timeline from Mixed Evidence](lab-02-timeline.md) | 2.5 h |
| Lab | [LAB-407-03 · Simulated Ransomware: Contain and Recover](lab-03-ransomware.md) | 2 h |
| Lab | [LAB-407-04 · The Incident Report and Post-Incident Review](lab-04-report-and-review.md) | 2 h |

## What you need

- The lab from Level 4: `lab-win`, `lab-ubuntu`, `lab-siem`, and the segmentation policy from CYB-405.
- Snapshot capability and a **backup taken before** the ransomware exercise.
- A synthetic email file, synthetic evidence CSVs, and a mock file set — all provided as text in the labs.
- No malware. No real ransomware. No real phishing email.

## On the ransomware lab

The exercise uses a shell script that **renames and overwrites mock files** in a directory created for the purpose. It
does not touch system files, does not encrypt anything, and does not self-propagate. The learning comes from the
response: what you preserve first, what you isolate, and how you decide to recover.

Running real ransomware, even in a VM, is out of scope for this course.

## Assessment

LAB-407-01 is marked on scope: did you determine who else received the email before containing? LAB-407-02 is marked
on the timeline's stated timezone and skew handling. LAB-407-03 is marked on ordering — evidence before containment
where possible — and on a recovery decision tied to stated objectives. LAB-407-04 is the capstone of the module: a
report a non-technical manager could act on, and a review that names what would be done differently.

## Where this fits

This module consumes everything before it: telemetry from CYB-402, detections from CYB-404, network evidence from
CYB-405, and forensic discipline from CYB-406. The [Level 4 assessment](../../level-4.md) reuses its report format.

## References

1. NIST SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations for Cybersecurity Risk Management
   (April 2025). Accessed 2026-10-29.
2. NIST SP 800-86 — forensic techniques in incident response. Accessed 2026-10-29.
3. CISA — Incident and Vulnerability Response Playbooks. <https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks> Accessed 2026-10-29.
4. MITRE ATT&CK v20.0 — technique mapping for incident findings. <https://attack.mitre.org/> Accessed 2026-10-29.
5. ISO/IEC 27035 — information security incident management (concepts). Accessed 2026-10-29.

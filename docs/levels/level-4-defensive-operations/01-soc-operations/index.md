---
title: "CYB-401 · SOC Operations, ATT&CK and Threat Intelligence"
description: "How a security operations centre actually works: alert lifecycle, triage judgement, ATT&CK mapping and indicator handling."
module_code: CYB-401
level: 4
kind: reference
prerequisites: [CYB-206, CYB-308]
estimated_minutes: 600
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-401-01, LAB-401-02, LAB-401-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [soc, triage, mitre-attack, threat-intelligence, ioc, metrics]
---

# CYB-401 · SOC Operations, ATT&CK and Threat Intelligence

**Level 4** · 10 hours · **Prerequisites:** [CYB-206](../../level-2-tooling/06-host-inspection-and-hardening/index.md), [CYB-308](../../level-3-applications/06-api-security/index.md)

## Why this module exists

A security operations centre is not a room full of dashboards. It is a decision pipeline: something happens, a
signal arrives, someone decides whether it matters, and somebody acts. Everything else — the SIEM, the rules, the
threat feeds — exists to make that decision faster and better.

This module teaches the decision. You will triage a queue of synthetic alerts where some are real and some are
noise, map observed behaviour to MITRE ATT&CK, and turn a threat-intelligence report into a small set of
indicators you can actually act on. None of it requires an attack to be running; all of it is what the job
consists of.

## Module outcomes

By the end of this module you can:

- Describe the alert lifecycle and the decisions made at each stage, including when *not* to escalate.
- Triage an alert queue by asset criticality, technique, and evidence rather than by severity label alone.
- Distinguish a true positive, a benign true positive, and a false positive, and record the reasoning.
- Map activity to ATT&CK tactics and techniques, and explain the limits of that mapping.
- Evaluate an indicator for confidence, age, and actionability, and choose block, hunt, or monitor.
- Write case notes and a handover that another analyst can continue without asking you questions.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [SOC Workflow, ATT&CK and Intelligence](01-soc-workflow-and-attck.md) | 4 h |
| Lab | [LAB-401-01 · Triage a Synthetic Alert Queue](lab-01-alert-triage.md) | 2 h |
| Lab | [LAB-401-02 · Map Activity to ATT&CK](lab-02-attck-mapping.md) | 2 h |
| Lab | [LAB-401-03 · Write a Threat-Intelligence Brief](lab-03-ioc-brief.md) | 2 h |

## What you need

- A workstation with Python 3.10+ and `jq`; no SIEM is required for this module.
- The synthetic datasets are generated in the labs, so nothing needs downloading.
- Your Level 1 notes on the CIA triad and risk, and Level 3's vocabulary for access-control failures — triage is
  mostly reasoning about those.

## A note on the data

Every alert, log line, domain, IP, and hash in these labs is **synthetic and fictional**. Addresses come from
documentation ranges (RFC 5737: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) and domains use reserved
`.test` or `.example` names. Nothing here refers to a real organisation, a real person, or a live indicator.

That matters for a practical reason: real indicators age, and an exercise built on them becomes wrong within
months. Synthetic ones stay valid, and they let you practise the judgement without implying that a particular
domain is malicious.

## Assessment

Three labs, rubric-marked. LAB-401-01 is the core skill: a queue of twelve alerts, five of which need action, with
a written rationale for every disposition — including the ones you close.

## Where this fits

[Endpoint Telemetry](../02-endpoint-telemetry/index.md) supplies the evidence this module triages.
[Detection Engineering and SIEM](../04-detection-and-siem/index.md) automates the first pass, so that the human
decision is spent on the cases that deserve it.

## References

1. NIST SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations for Cybersecurity Risk Management
   (April 2025). <https://csrc.nist.gov/pubs/sp/800/61/r3/final>
2. MITRE ATT&CK v20.0 (October 2026). <https://attack.mitre.org/resources/versions/>
3. MITRE ATT&CK — Triage and investigation resources. <https://attack.mitre.org/> Accessed 2026-10-29.
4. FIRST — Traffic Light Protocol 2.0. <https://www.first.org/tlp/> Accessed 2026-10-29.

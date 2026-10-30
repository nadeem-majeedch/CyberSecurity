---
title: "CYB-403 · Hardening, Baselines and Vulnerability Management"
description: "Measure a host against a published baseline, change only what you can verify, and prioritise patching by exploitability rather than by score."
module_code: CYB-403
level: 4
kind: reference
prerequisites: [CYB-402, CYB-204]
estimated_minutes: 720
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-403-01, LAB-403-02, LAB-403-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [hardening, cis-benchmarks, openscap, lynis, asr, patch-management, kev, epss, cvss]
---

# CYB-403 · Hardening, Baselines and Vulnerability Management

**Level 4** · 12 hours · **Prerequisites:** [CYB-402](../02-endpoint-telemetry/index.md), [CYB-204](../../level-2-tooling/06-host-inspection-and-hardening/index.md)

## Why this module exists

Hardening fails in two predictable ways. The first is doing nothing, because every control looks like it might break
something. The second is applying a benchmark wholesale, breaking something, and then rolling the whole baseline back
— which teaches the organisation that hardening is dangerous.

The professional version is narrower and more useful: **measure, change one thing, verify the change with evidence,
and record why any control is deliberately not applied.** Patching follows the same discipline, except the scarce
resource is not effort but attention — you cannot patch everything on the day it is published, so you must be able to
defend the order you chose.

## Module outcomes

By the end of this module you can:

- Explain the relationship between CIS Benchmarks, DISA STIGs, vendor security baselines and SCAP content.
- Assess a Linux host against a published profile with OpenSCAP, and triage the results instead of remediating blindly.
- Apply a defined set of Windows controls and verify each one by querying its state, not by trusting the wizard.
- Write a deviation and exception register that a reviewer can accept.
- Prioritise a vulnerability list using exploitability, exposure, asset value and compensating controls — and justify
  the order in writing.
- Explain why CVSS is a severity score rather than a risk score, and what replaced the assumption that every CVE is
  scored by NVD.
- Define patch SLAs and the one metric that actually tells you whether they are met.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Baselines, Hardening and Patch Priority](01-baselines-and-patch-priority.md) | 3 h |
| Lab | [LAB-403-01 · Linux Baseline Assessment and Verified Remediation](lab-01-linux-baseline.md) | 3 h |
| Lab | [LAB-403-02 · Windows Controls You Can Prove](lab-02-windows-hardening.md) | 3 h |
| Lab | [LAB-403-03 · Vulnerability Prioritisation and Patch Plan](lab-03-vulnerability-prioritisation.md) | 3 h |

## What you need

- `lab-ubuntu` (Ubuntu 24.04 LTS) and `lab-win` (Windows 11), both from Level 1, on the host-only network.
- NAT attached **only** while installing packages and downloading the SSG content; detach before the exercises.
- OpenSCAP 1.4.6, SCAP Security Guide content 0.1.82, Lynis 3.1.7, Microsoft Security Compliance Toolkit 1.0.
- `lab-ubuntu` should be snapshotted: the OpenSCAP evaluation is read-only, but remediation changes the host.

## How the labs fit together

The Linux lab teaches the measure–change–verify loop with a real profile. The Windows lab teaches the same loop with
controls whose state you can query from PowerShell, plus one control whose *effect* you can observe in the event log.
The prioritisation lab supplies a synthetic scan export and asks for the artefact most organisations lack: a patch
plan with reasons, not a sorted list.

## Assessment

Each lab is rubric-marked. LAB-403-01 and LAB-403-02 each require a before/after evidence pair; LAB-403-03 requires a
prioritised plan with a written justification for every ordering decision that contradicts raw CVSS. The Level 4
assessment reuses the exception-register format.

## Where this fits

[CYB-404](../04-detection-and-siem/index.md) monitors the controls you configure here — a baseline without telemetry
is a claim, not a control. [CYB-406](../06-digital-forensics/index.md) assumes you can tell an intentional
configuration from a compromised one.

## References

1. OpenSCAP 1.4.6 (22 October 2026) and ComplianceAsCode/content 0.1.82 (1 September 2026), including Ubuntu 24.04
   profiles. <https://github.com/OpenSCAP/openscap/releases> · <https://github.com/ComplianceAsCode/content/releases>
   Accessed 2026-10-29.
2. CIS Benchmarks (free PDFs for non-commercial use; download form required) and CIS-CAT Lite.
   <https://learn.cisecurity.org/benchmarks> Accessed 2026-10-29.
3. Lynis 3.1.7 (25 June 2026). <https://github.com/CISOfy/lynis/releases> Accessed 2026-10-29.
4. Microsoft Security Compliance Toolkit 1.0 and LGPO. <https://learn.microsoft.com/en-us/windows/security/operating-system-security/device-management/windows-security-configuration-framework/security-compliance-toolkit-10> Accessed 2026-10-29.
5. Microsoft — Windows LAPS (built in from Windows 11 23H2; legacy LAPS deprecated).
   <https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview> Accessed 2026-10-29.
6. CISA Known Exploited Vulnerabilities catalog (active; entries dated 28 October 2026).
   <https://www.cisa.gov/known-exploited-vulnerabilities-catalog> Accessed 2026-10-29.
7. FIRST EPSS v5 (publishing since 15 June 2026), API v1. <https://www.first.org/epss/data> Accessed 2026-10-29.
8. NIST NVD — CVSS v4.0 support and the 15 April 2026 operations update on enrichment priorities.
   <https://www.nist.gov/news-events/news/2026/04/nist-updates-nvd-operations-address-record-cve-growth> Accessed 2026-10-29.

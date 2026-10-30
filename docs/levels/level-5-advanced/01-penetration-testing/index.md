---
title: "CYB-501 · Penetration Testing and Security Assessment"
description: "Run an authorized assessment end to end: scope it, test only what is in scope, prove impact with evidence, and write a report the client can act on."
module_code: CYB-501
level: 5
kind: reference
prerequisites: [CYB-206, CYB-308, CYB-407]
estimated_minutes: 840
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-501-01, LAB-501-02, LAB-501-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [penetration-testing, scoping, rules-of-engagement, risk-rating, reporting, retesting]
---

# CYB-501 · Penetration Testing and Security Assessment

**Level 5** · 14 hours · **Prerequisites:** [CYB-206](../../level-2-tooling/06-host-inspection-and-hardening/index.md), [CYB-308](../../level-3-applications/06-api-security/index.md), [CYB-407](../../level-4-defensive-operations/07-incident-response/index.md)

## Why this module exists

The technical part of penetration testing is the part you have already practised. The professional part is
everything around it: deciding what you are allowed to touch, proving an impact without exceeding the permission you
were given, and writing something a client can fix and later verify.

Most failures in this work are not exploitation failures. They are scope failures, evidence failures and reporting
failures — an unrequested host touched, a finding that cannot be reproduced, a "critical" that nobody prioritises.

## Module outcomes

By the end of this module you can:

- Write a scope, rules-of-engagement document and test plan for a defined lab range, including exclusions and stop
  conditions.
- Perform reconnaissance and enumeration against lab targets and record what you did and when.
- Validate a vulnerability before rating it, and distinguish a scanner's claim from demonstrated impact.
- Exploit a lab target only to the extent needed to prove impact, and capture evidence that a reviewer can reproduce.
- Escalate privileges on a dedicated local training VM, then remediate the cause and verify the fix.
- Rate findings by technical severity and business context, and defend the rating.
- Write a client-style report with an executive summary, reproducible findings, remediation and retest status.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Engagements, Evidence and Impact](01-engagement-and-evidence.md) | 3 h |
| Lab | [LAB-501-01 · Scope, Rules of Engagement and Test Plan](lab-01-engagement-package.md) | 3 h |
| Lab | [LAB-501-02 · Authorized Assessment of a Lab Target](lab-02-lab-assessment.md) | 4 h |
| Lab | [LAB-501-03 · Final Challenge: Escalate, Report, Remediate, Retest](lab-03-privesc-and-report.md) | 4 h |

## What you need

- The Level 3 `lab-web` host with a deliberately vulnerable application (DVWA or OWASP Juice Shop), reachable only
  from the analyst VM on the host-only network.
- A dedicated **privesc training VM**: an Ubuntu 24.04 clone whose misconfigurations are created by the setup script
  in LAB-501-03. Snapshot it before the lab.
- Wireshark or `tcpdump` for evidence capture, and a proxy for web requests.
- No external targets. There is no lab in this module that involves an address outside `192.0.2.0/24`.

## The rule that governs everything here

**Authorization is specific, written, and time-bounded.** "We have permission to test our own lab" is sufficient for
this module because the range is defined and owned by you. In professional work, the equivalent is a signed scope
document naming hosts, techniques, windows and contacts.

!!! warning "What these labs never authorize"
    Scanning or exploiting a public address, an employer's production system, a shared hosting tenant, a cloud
    account you do not own, or a "bug bounty" target whose programme rules you have not read. If an exercise would
    require any of those, it is out of scope for this course.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## How the module is marked

LAB-501-01 is marked on whether the scope is specific enough to be enforceable. LAB-501-02 is marked on evidence and
on restraint — proving impact without going further than necessary. LAB-501-03 is the final challenge: a full
escalation, report, remediation and retest cycle, with the rubric weighting the retest evidence highest.

## Professional relevance and limits

Testing demonstrates that specific weaknesses exist under specific conditions. It cannot demonstrate that a system is
secure, and a clean report is not a guarantee. State that limitation in every report you write, including the ones in
this module.

## Where this fits

[CYB-502](../02-active-directory/index.md) applies the same engagement discipline to a domain environment.
[CYB-506](../06-threat-hunting/index.md) turns the findings into detections, which is how a one-off test becomes
lasting coverage.

## References

1. PTES — Penetration Testing Execution Standard. <http://www.pentest-standard.org/> Accessed 2026-10-29.
2. NIST SP 800-115 — Technical Guide to Information Security Testing and Assessment. Accessed 2026-10-29.
3. OWASP Web Security Testing Guide v4.2 (stable; v5.0 in development). Accessed 2026-10-29.
4. OWASP Top 10:2025. Accessed 2026-10-29.
5. FIRST — CVSS v4.0 specification. <https://www.first.org/cvss/v4-0/> Accessed 2026-10-29.
6. CREST — Code of Conduct and professional standards for penetration testing. Accessed 2026-10-29.

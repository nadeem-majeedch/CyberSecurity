---
title: "CYB-307 · Secure Coding, Dependencies and Remediation"
description: "Threat modeling, code review, supply-chain risk, and the discipline of proving a fix actually works."
module_code: CYB-307
level: 3
kind: reference
prerequisites: [CYB-302, CYB-303, CYB-304]
estimated_minutes: 720
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-307-01, LAB-307-02, LAB-307-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [secure-coding, threat-modeling, code-review, dependencies, sbom, remediation]
---

# CYB-307 · Secure Coding, Dependencies and Remediation

**Level 3** · 12 hours · **Prerequisites:** [CYB-302](../02-injection-and-xss/index.md),
[CYB-303](../03-access-control-and-authentication/index.md), [CYB-304](../04-file-handling-ssrf-misconfiguration/index.md)

## Why this module exists

Finding a vulnerability is half a skill. The other half is the part clients pay for: specifying a fix that
addresses the cause, proving the fix works, and proving it did not break the feature. Most junior reports stop at
"parameterise the query" and leave the hard parts — regression tests, dependency updates, and the difference
between a fix and a mitigation — to someone else.

This module also covers the one attack surface you do not write: your dependencies. [A03:2025 Software Supply Chain
Failures](https://owasp.org/Top10/2025/) is new to the Top 10 and reflects what practitioners already knew — most
of the code in a modern application was written by someone else, and none of it was reviewed by you.

## Module outcomes

By the end of this module you can:

- Build a data-flow diagram, mark trust boundaries, and derive STRIDE threats with mitigations and tests.
- Review a small codebase for the flaw classes taught in CYB-302 to CYB-304, citing file and line.
- Inventory dependencies, interpret advisory output, and prioritise by exploitability rather than CVSS alone.
- Distinguish a fix from a mitigation and place each correctly in a report.
- Write regression tests that fail on the vulnerable version and pass on the fixed one.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Secure Coding, Review and Supply Chain](01-secure-coding-and-supply-chain.md) | 4 h |
| Lab | [LAB-307-01 · Threat Model and Code Review](lab-01-code-review-and-threat-model.md) | 2 h |
| Lab | [LAB-307-02 · Vulnerable Dependencies](lab-02-vulnerable-dependencies.md) | 1.5 h |
| Lab | [LAB-307-03 · Fix, Test and Verify](lab-03-fix-and-verify.md) | 2.5 h |

## What you need

- Python 3.10+, `pip`, `pip-audit`, `pytest`, Flask, `requests`.
- Node.js 18+ and `npm` (optional, for the JavaScript half of LAB-307-02).
- A git repository you create for the seeded application in LAB-307-01.

## A note on the sample application

The three labs use one small application, supplied as source in the lab text rather than as a downloadable archive.
Nothing in this repository ships a running vulnerable service, and nothing you build here should be exposed beyond
`127.0.0.1`. You will read it, run it locally, break it, fix it, and test the fix.

## Assessment

Three labs, rubric-marked, forming a single deliverable: a threat model, a findings table with file-and-line
citations, a dependency report, and a remediation table where every fix is backed by a test that fails without it.

## Where this fits

This module closes Level 3's web block. [API Security](../06-api-security/index.md) applies the same review
discipline to an interface rather than a page; Level 4's detection engineering assumes you can recognise the
patterns you have now learned to find and fix.

## References

1. OWASP Top 10:2025 — A03 Software Supply Chain Failures, A06 Insecure Design. <https://owasp.org/Top10/2025/>
2. OWASP ASVS 5.0 — V1, V2, V13, V15 Secure Coding and Architecture. <https://asvs.owasp.org/>
3. OWASP Code Review Guide v2.0. Accessed 2026-10-29.
4. OWASP Threat Modeling Cheat Sheet. Accessed 2026-10-29.
5. NIST SP 800-218 — Secure Software Development Framework (SSDF) v1.1.

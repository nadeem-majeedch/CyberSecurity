---
title: "CYB-114 · Password Security, MFA, Phishing Awareness and Personal Security"
description: "How credentials are attacked, why MFA works and where it fails, how phishing is constructed, and how to assess a password policy."
module_code: CYB-114
level: 1
kind: reference
prerequisites: [CYB-113]
estimated_minutes: 180
difficulty: beginner
safety: local-only
lab_ids: [LAB-114-01, LAB-114-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [passwords, mfa, phishing, awareness]
---

# CYB-114 · Password Security, MFA, Phishing Awareness and Personal Security

**Level 1** · 3 hours · **Prerequisites:** [CYB-113](../13-cryptography-hashing-signatures/index.md)

## Why this module exists

Credentials remain the most common way into an organisation, and phishing remains the most common way to get
them. Both are human problems wearing a technical costume.

This module teaches you how credential attacks actually work — at the level needed to defend against them —
why MFA helps and where it does not, how to read a phishing email analytically instead of by feel, and how
to evaluate a password policy using fictional data only.

## Module outcomes

By the end of this module you can:

- Explain how password storage, reuse, spraying, and stuffing differ, and which controls stop each.
- Compare MFA factor types and name the attacks that survive MFA.
- Triage a phishing email using a repeatable checklist: headers, links, urgency, requests.
- Assess a password policy against realistic threats, and recommend specific improvements.
- Apply personal security practices that reduce your own risk, without pretending they are sufficient.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Passwords, MFA and Phishing](01-passwords-mfa-phishing.md) | 2 h |
| Lab | [LAB-114-01 · Triage Synthetic Phishing Emails](lab-01-phishing-triage.md) | 45 min |
| Lab | [LAB-114-02 · Assess a Password Policy](lab-02-password-policy.md) | 45 min |

## What you need

- The lesson and two labs; no additional software.
- **Synthetic** phishing samples provided by the instructor or constructed by you from the templates in the
  lab. Do not use real emails from real people.

## Assessment

- Knowledge check at the end of the lesson.
- Both labs marked against the lab rubric.

## Related

- [Cryptography, Hashing and Signatures](../13-cryptography-hashing-signatures/index.md) — password hashing
- [Identity and Access Management at Level 3](../../level-3.md)
- [Safety Policy](../../../policies/safety-policy.md) — no testing against real accounts

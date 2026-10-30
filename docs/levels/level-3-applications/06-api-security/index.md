---
title: "CYB-308 · API Security"
description: "Object-level authorization, mass assignment, token handling and rate limiting — the flaws that dominate modern API assessments."
module_code: CYB-308
level: 3
kind: reference
prerequisites: [CYB-303, CYB-307]
estimated_minutes: 600
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-308-01, LAB-308-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [api-security, bola, bfla, mass-assignment, rate-limiting, jwt]
---

# CYB-308 · API Security

**Level 3** · 10 hours · **Prerequisites:** [CYB-303](../03-access-control-and-authentication/index.md), [CYB-307](../05-secure-coding-and-dependencies/index.md)

## Why this module exists

An API has no buttons to hide. Every operation the application can perform is reachable by anyone who can form the
request, which means the only thing standing between a user and another user's data is a check the server makes —
every time, on every route, for every object.

That is why the OWASP API Security Top 10 (2023 edition) leads with **Broken Object Level Authorization**. It is
the same IDOR you tested in CYB-303, at the scale where most modern applications actually operate: mobile clients,
single-page front ends, and third-party integrations all speak to the API directly.

## Module outcomes

By the end of this module you can:

- Map an API's endpoints, methods, and object references, and build a test matrix.
- Test object-level, function-level, and property-level authorization with two identities.
- Identify mass assignment from an accepted-but-unused field and from a response that echoes more than you sent.
- Explain JWT validation requirements and the specific bugs that come from skipping each check.
- Test and specify rate limiting, including what it must be keyed on to be useful.
- Produce a prioritised API findings table with reproduction steps a developer can follow.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Authorization, Tokens and Resource Limits](01-api-authorization-and-tokens.md) | 3.5 h |
| Lab | [LAB-308-01 · API Authorization Failures](lab-01-api-authorization.md) | 1.5 h |
| Lab | [LAB-308-02 · Mass Assignment and Rate Limiting](lab-02-mass-assignment-and-rate-limiting.md) | 1.75 h |

## What you need

- Juice Shop running at `192.0.2.30:3000`, with two accounts you created.
- `curl`, `jq`, `python3` with Flask and `pytest` for the local sample API.
- Your IDOR evidence from [LAB-303-02](../03-access-control-and-authentication/lab-02-broken-access-control.md).

## Assessment

Two labs, rubric-marked. LAB-308-01 produces the API section of the Level 3 report; LAB-308-02 produces the fix,
with tests, for the two flaws clients most often dispute — "we validate on the client" and "we have a WAF".

## Where this fits

This is the final module of Level 3's application block. Applied cryptography (CYB-305) and identity federation
(CYB-306) remain planned; the access-control fundamentals they build on are already covered in CYB-303.

## References

1. OWASP API Security Top 10 — 2023 edition. <https://owasp.org/API-Security/> Accessed 2026-10-29.
2. OWASP Top 10:2025 — A01 Broken Access Control. <https://owasp.org/Top10/2025/>
3. OWASP ASVS 5.0 — V4 API and Web Service, V8 Authorization, V9 Self-contained Tokens. <https://asvs.owasp.org/>
4. OWASP WSTG v4.2 — WSTG-ATHZ-02, WSTG-ATHZ-04, WSTG-BUSL.

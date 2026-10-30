---
title: "CYB-303 · Access Control, Authentication and Sessions"
description: "Who you are, what you may do, and whether the request that says so can be trusted — the flaws that top every breach list."
module_code: CYB-303
level: 3
kind: reference
prerequisites: [CYB-301, CYB-302]
estimated_minutes: 720
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-303-01, LAB-303-02, LAB-303-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [access-control, idor, authentication, passwords, sessions, csrf]
---

# CYB-303 · Access Control, Authentication and Sessions

**Level 3** · 12 hours · **Prerequisites:** [CYB-301](../01-web-architecture-and-http/index.md), [CYB-302](../02-injection-and-xss/index.md)

## Why this module exists

Broken access control sits at [A01:2025](https://owasp.org/Top10/2025/) for a reason that has nothing to do with
clever exploitation: it is the flaw that requires **no payload at all**. Change a number in a URL, keep your own
valid session, and read someone else's record. Authentication failures ([A07:2025](https://owasp.org/Top10/2025/))
follow the same logic — the attacker logs in legitimately, as themselves, and the application hands over more
than it should.

This module is about the decisions made *after* a request is parsed: is this identity real, what is it allowed to
touch, and can this specific request be proven to come from the person it claims.

## Module outcomes

By the end of this module you can:

- Distinguish authentication from authorization failures, and classify an access-control flaw as vertical,
  horizontal, or contextual.
- Test for IDOR systematically by comparing responses for objects you have unequal rights to.
- Evaluate an authentication workflow for enumeration, lockout, reset, and MFA weaknesses.
- Judge a password-storage implementation and explain why the algorithm, salt, and work factor each matter.
- Identify session fixation, missing rotation, and absent revocation from observable behaviour.
- Explain how CSRF works, why `SameSite` alone is insufficient, and how a token actually prevents it.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Authorization, Identity and Session Integrity](01-authorization-and-session-integrity.md) | 5 h |
| Lab | [LAB-303-01 · Insecure Login Workflow](lab-01-insecure-login-workflow.md) | 3 h |
| Lab | [LAB-303-02 · Broken Access Control and IDOR](lab-02-broken-access-control.md) | 3 h |
| Lab | [LAB-303-03 · Cross-Site Request Forgery](lab-03-csrf.md) | 2 h |

## What you need

- Web lab from [LAB-301-01](../01-web-architecture-and-http/lab-01-web-lab-setup.md); DVWA at **Low**.
- Two Juice Shop accounts, created by you, with different privileges if you can arrange it.
- `curl`, `jq`, `htpasswd` (from `apache2-utils`), Python 3 with `bcrypt` or `argon2-cffi`.
- A browser profile with the proxy configured, for the CSRF lab.

## Assessment

Three labs, rubric-marked. LAB-303-02 produces the access-control section of the Level 3 report and is the one
most likely to resemble real work: the finding is a one-line request, and the value is in the argument that
follows it.

## Where this fits

The session attributes you measured in [LAB-301-03](../01-web-architecture-and-http/lab-03-cookie-and-session-attributes.md)
are the preconditions for this module's findings. [File Handling, SSRF and Misconfiguration](../04-file-handling-ssrf-misconfiguration/index.md)
adds the flaws that turn a low-privilege account into code execution; [API Security](../06-api-security/index.md)
revisits BOLA at the interface where it is most common.

## References

1. OWASP Top 10:2025 — A01 Broken Access Control, A07 Authentication Failures. <https://owasp.org/Top10/2025/>
2. OWASP WSTG v4.2 — WSTG-ATHN-01…10, WSTG-ATHZ-01…04, WSTG-SESS-01…09.
3. OWASP ASVS 5.0 — V6 Authentication, V7 Session Management, V8 Authorization.
4. OWASP Password Storage Cheat Sheet. Accessed 2026-10-29.

---
title: "CYB-302 · Injection and Cross-Site Scripting"
description: "How untrusted data becomes code in SQL, the shell and the browser — and the construction that prevents it."
module_code: CYB-302
level: 3
kind: reference
prerequisites: [CYB-301]
estimated_minutes: 840
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-302-01, LAB-302-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [sql-injection, xss, injection, output-encoding, parameterisation]
---

# CYB-302 · Injection and Cross-Site Scripting

**Level 3** · 14 hours · **Prerequisites:** [CYB-301](../01-web-architecture-and-http/index.md)

## Why this module exists

Injection is the oldest surviving class in the OWASP Top 10, and it survives because the underlying mistake is
conceptual, not technical: **data crossing a boundary into an interpreter**. SQL, a shell, an HTML parser, a
template engine, and a JavaScript engine are all interpreters. Each has a correct way to receive data and several
popular ways to accidentally treat data as instructions.

This module teaches the distinction properly. You will exploit injection in applications built to be exploited,
then write the fix and explain why it works — because "use prepared statements" is not an answer until you can
show what the parser does differently.

!!! warning "Scope"
    Targets are OWASP Juice Shop (`192.0.2.30:3000`) and DVWA (`192.0.2.30:4280`) in your host-only lab, both
    deliberately vulnerable. Their databases contain synthetic data. Never test injection against a system
    holding real records: a careless `DROP` or a lost `WHERE` clause is a data-loss incident, not a finding.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Module outcomes

By the end of this module you can:

- Classify an injection flaw by the interpreter it reaches, not by the payload you used.
- Demonstrate error-based, boolean and union SQL injection against a lab application, and explain what each
  technique tells you about the query.
- Explain why parameterised queries remove the vulnerability class, and where concatenation still creeps back in.
- Distinguish reflected, stored and DOM-based XSS by where the payload executes and where it persists.
- Choose the correct encoding for a given output context, and identify when a filter is not a fix.
- Write a CSP that would have blocked the payload you executed, and state what it still does not stop.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Injection, Contexts and Encoding](01-injection-and-output-encoding.md) | 6 h |
| Lab | [LAB-302-01 · SQL Injection and Its Fix](lab-01-sql-injection.md) | 4 h |
| Lab | [LAB-302-02 · Reflected and Stored XSS](lab-02-xss.md) | 4 h |

## What you need

- The web lab from [LAB-301-01](../01-web-architecture-and-http/lab-01-web-lab-setup.md), DVWA at **Low**.
- Proxy (Burp Community or ZAP), browser devtools, `curl`, `sqlite3` (for the fix exercise).
- Python 3.10+ with `flask` and `sqlite3` for the local parameterisation exercise
  (`pip install flask` inside a virtual environment).

## Assessment

Two labs, rubric-marked. Each requires a **fix artefact**: a patch and a proof that the payload no longer
works, plus a proof that the legitimate function still does. The second half is what separates remediation from
guessing, and it is marked.

## Where this fits

[Access Control and Authentication](../03-access-control-and-authentication/index.md) uses the session
mechanics from CYB-301; the XSS you demonstrate here is the reason `HttpOnly` matters there. CYB-307 turns this
material into a code-review and remediation-verification workflow.

## References

1. OWASP Top 10:2025 — A05 Injection, A03 Software Supply Chain Failures. <https://owasp.org/Top10/2025/>
2. OWASP WSTG v4.2 — WSTG-INPV-01, WSTG-INPV-02, WSTG-INPV-05, WSTG-INPV-12.
3. OWASP ASVS 5.0 — V1 Encoding and Sanitization, V3 Web Frontend Security.
4. OWASP SQL Injection Prevention Cheat Sheet. Accessed 2026-10-29.

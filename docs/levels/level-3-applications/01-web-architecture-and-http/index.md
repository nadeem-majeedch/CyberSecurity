---
title: "CYB-301 · Web Architecture and HTTP for Security"
description: "HTTP messages, cookies, sessions, the same-origin policy, CORS and browser security headers, read as trust decisions."
module_code: CYB-301
level: 3
kind: reference
prerequisites: [CYB-204, CYB-206]
estimated_minutes: 480
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-301-01, LAB-301-02, LAB-301-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [http, cookies, sessions, cors, same-origin-policy, security-headers]
---

# CYB-301 · Web Architecture and HTTP for Security

**Level 3** · 8 hours · **Prerequisites:** [CYB-204](../../level-2-tooling/04-packet-capture-and-analysis/index.md), [CYB-206](../../level-2-tooling/06-host-inspection-and-hardening/index.md)

## Why this module exists

Almost every web vulnerability is a disagreement about **who decides**. The browser decides which origin may
read a response. The server decides whether a cookie is sent. The application decides whether the `user_id` in
a request is trusted. When those decisions are missing, inconsistent, or made by the wrong party, you get the
findings that fill real assessment reports.

You cannot reason about SQL injection, access control, or CSRF until you can read a raw HTTP exchange and say
what each header is claiming. That is the whole job of this module: make the protocol visible, then make the
trust boundaries visible.

!!! warning "Scope"
    All targets in this module are the vulnerable applications running in **your own lab**: OWASP Juice Shop on
    `192.0.2.30:3000` and DVWA on `192.0.2.30:4280`, inside the host-only network. Never point a proxy,
    scanner, or `curl` at a public site, a university system, or an employer's application. See the
    [Safety Policy](../../../policies/safety-policy.md).

## Module outcomes

By the end of this module you can:

- Read a raw request and response and name the function of each header present.
- Explain why a browser blocks a cross-origin read, and what a permissive CORS policy actually exposes.
- Evaluate `Set-Cookie` attributes against the threat each one addresses.
- Configure a proxy to intercept a browser session without breaking your normal browsing.
- Identify missing or weak security headers on a response and state the concrete risk, not just the name.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [HTTP, Sessions and the Browser Security Model](01-http-and-the-browser-security-model.md) | 3 h |
| Lab | [LAB-301-01 · Build the Web Lab](lab-01-web-lab-setup.md) | 1.5 h |
| Lab | [LAB-301-02 · Intercept and Annotate a Session](lab-02-intercept-a-session.md) | 1.5 h |
| Lab | [LAB-301-03 · Evaluate Cookie and Session Attributes](lab-03-cookie-and-session-attributes.md) | 1.5 h |

## What you need

- Your Level 2 lab: `lab-analyst` (Kali) and `lab-web` (Ubuntu Server 22.04) on `192.0.2.0/24`.
- Docker Engine on `lab-web`; NAT attached only while pulling images (LAB-301-01 covers the check).
- Burp Suite Community Edition 2026.10.1 (free download, no licence) **or** OWASP ZAP 2.17.0 (free and open
  source). Both are covered; neither is required to complete the labs, because every step has a `curl`
  equivalent.
- `curl`, `openssl`, `jq`, and Python 3.10+ for the small verification scripts.

## Assessment

Three labs, rubric-marked. LAB-301-03 produces the session-attribute table you will reuse in CYB-303 and in
the Level 3 report. Keep the raw responses: an assertion about a cookie is only credible next to the header that
proves it.

## Where this fits

This module is the reading prerequisite for everything else in Level 3. [Injection and XSS](../02-injection-and-xss/index.md)
assumes you can identify a parameter and its context; [Access Control and Authentication](../03-access-control-and-authentication/index.md)
assumes you understand what a session cookie actually authenticates.

## References

1. RFC 9110 — HTTP Semantics. IETF, June 2022.
2. RFC 6265bis — Cookies: HTTP State Management Mechanism (draft). IETF.
3. OWASP Top 10:2025 — A01 Broken Access Control, A02 Security Misconfiguration. <https://owasp.org/Top10/2025/>
4. OWASP Web Security Testing Guide v4.2 — WSTG-SESS-02 (Cookie Attributes), WSTG-CONF-07 (HSTS).
5. MDN Web Docs — Same-origin policy; CORS; Set-Cookie. Accessed 2026-10-29.

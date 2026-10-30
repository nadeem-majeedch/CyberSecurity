---
title: "CYB-304 · File Handling, SSRF and Misconfiguration"
description: "Uploads, path traversal, server-side request forgery and the configuration mistakes that turn a small flaw into a foothold."
module_code: CYB-304
level: 3
kind: reference
prerequisites: [CYB-303]
estimated_minutes: 720
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-304-01, LAB-304-02, LAB-304-03, LAB-304-04]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [file-upload, path-traversal, ssrf, misconfiguration, headers, tls]
---

# CYB-304 · File Handling, SSRF and Misconfiguration

**Level 3** · 12 hours · **Prerequisites:** [CYB-303](../03-access-control-and-authentication/index.md)

## Why this module exists

Everything so far assumed the attacker's input is a *value* — an id, a password, a search term. This module is
about input that is a **path**, a **file**, or a **URL**, and those types carry capabilities of their own. A
filename can escape a directory. An uploaded file can become executable code. A URL the server fetches can reach
an address the attacker cannot reach themselves.

Separately, the module covers the least glamorous and most common finding in real reports: a system that is
correctly built and incorrectly configured. Directory listing, default credentials, verbose errors, TLS
misconfiguration, and missing security headers rarely make headlines, and they are what a scanner finds on almost
every first assessment.

## Module outcomes

By the end of this module you can:

- Demonstrate and remediate unsafe file upload by validating type, name, storage location, and execution rights.
- Explain path traversal through decoding layers, and fix it with canonicalisation against a fixed base directory.
- Describe the three SSRF classes and why a host allowlist must be checked after DNS resolution.
- Identify and correct the misconfigurations that scanners report most often, with a stated risk for each.
- Write a hardening configuration and verify it with requests rather than assumptions.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Files, Requests and Configuration](01-files-requests-and-configuration.md) | 4 h |
| Lab | [LAB-304-01 · File Upload Validation](lab-01-file-upload.md) | 1.5 h |
| Lab | [LAB-304-02 · Path Traversal and File Inclusion](lab-02-path-traversal.md) | 1.25 h |
| Lab | [LAB-304-03 · Server-Side Request Forgery](lab-03-ssrf.md) | 1.75 h |
| Lab | [LAB-304-04 · Security Headers, TLS and Misconfiguration](lab-04-headers-and-tls.md) | 1.25 h |

## What you need

- Web lab from [LAB-301-01](../01-web-architecture-and-http/lab-01-web-lab-setup.md); DVWA at **Low**.
- Python 3.10+ with Flask, `requests`, `pytest`; `nginx` (or a container) for the hardening lab.
- `curl`, `openssl`, `file`, `xxd`, and `ss` for verification.

## Assessment

Four labs, rubric-marked. LAB-304-04 produces the configuration section of the Level 3 report; its output is a
before/after header table plus a hardening config that you prove with requests.

## Safety note that applies to the whole module

**SSRF is the most dangerous exercise in this level.** A successful SSRF test asks a server to fetch an address of
your choosing. In this course the only permitted targets are `127.0.0.1` and `192.0.2.0/24` **inside your lab** —
never a cloud metadata endpoint, never a public address, never anything on another network. The labs are built so
that the internal service you reach is one you started yourself, on loopback, holding fake data.

## References

1. OWASP Top 10:2025 — A01 Broken Access Control, A02 Security Misconfiguration, A05 Injection.
2. OWASP WSTG v4.2 — WSTG-BUSL-09 (Upload of Malicious Files), WSTG-ATHZ-01 (Directory Traversal),
   WSTG-CONF-06/07/09, WSTG-CRYP-01.
3. OWASP File Upload Cheat Sheet; Unrestricted File Upload. Accessed 2026-10-29.
4. OWASP Server-Side Request Forgery Prevention Cheat Sheet. Accessed 2026-10-29.

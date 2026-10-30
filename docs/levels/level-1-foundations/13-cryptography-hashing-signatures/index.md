---
title: "CYB-113 · Introduction to Cryptography, Hashing and Digital Signatures"
description: "Symmetric and asymmetric encryption, hash properties, digital signatures, PKI, and how cryptographic implementations fail."
module_code: CYB-113
level: 1
kind: reference
prerequisites: [CYB-112]
estimated_minutes: 180
difficulty: beginner
safety: local-only
lab_ids: [LAB-113-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [cryptography, hashing, signatures, pki]
---

# CYB-113 · Introduction to Cryptography, Hashing and Digital Signatures

**Level 1** · 3 hours · **Prerequisites:** [CYB-112](../12-kali-linux/index.md)

## Why this module exists

Cryptography is the only part of security where mathematics does the trusting. When it is implemented
correctly, it is boringly reliable; when it is misused, it fails completely while looking fine.

This module is engineering, not mathematics. You will not derive elliptic curves. You will learn which
primitive solves which problem, what the common mistakes look like, and how to verify your own file
integrity and signatures with tools you already have.

## Module outcomes

By the end of this module you can:

- Distinguish symmetric encryption, asymmetric encryption, hashing, and digital signatures by purpose.
- Explain why a hash is not encryption, and why MD5/SHA-1 are no longer acceptable for integrity.
- Compute and compare hashes on Linux and Windows, and explain what a changed hash proves.
- Sign a file with a private key and verify it with the public key.
- Explain what a certificate binds, and why validation matters more than encryption.
- Name five ways cryptographic implementations fail in practice.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Cryptography You Will Actually Use](01-crypto-hashing-signatures.md) | 2 h |
| Lab | [LAB-113-01 · Hashes, Integrity and Signatures](lab-01-hashing-integrity.md) | 1 h |

## What you need

- `lab-ubuntu` with `openssl` and `sha256sum` (both standard).
- Optionally `lab-win` for the cross-platform hash comparison.

## Assessment

- Knowledge check at the end of the lesson.
- Lab marked against the lab rubric; the integrity demonstration is the core evidence.

## Related

- [TCP, UDP, HTTP and TLS](../08-addressing-and-protocols/02-tcp-udp-http-tls.md) — where TLS applies this
- [Password Security and MFA](../14-passwords-mfa-phishing/index.md) — hashing for authentication
- [Applied Cryptography at Level 3](../../level-3.md) — the deeper treatment

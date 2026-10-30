---
title: "LAB-113-01 · Hashes, File Integrity and Signatures"
description: "Detect a modified file with SHA-256, compare algorithms, and sign and verify a file with OpenSSL."
module_code: CYB-113
level: 1
kind: lab
prerequisites: [CYB-113]
estimated_minutes: 60
difficulty: beginner
safety: local-only
lab_ids: [LAB-113-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [cryptography, hashing, integrity, signatures]
---

# LAB-113-01 · Hashes, File Integrity and Signatures

**Module:** CYB-113 · **Time:** 60 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-113-01`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** files you create in `/tmp` inside your own lab VM.
    **Targets you must not use:** real documents, credentials, or another person's files. Do not hash or
    share any file that contains personal or confidential data.

    The keys you generate here are for teaching only. Never reuse them, and never publish a private key.

## Objective

Establish a baseline digest for a file, modify it, prove the change with SHA-256, compare MD5 and SHA-256
behaviour, then sign a file with an RSA key and verify it — including a deliberate verification failure.

## Threat model

You are simulating the integrity check a download page performs, and the detection an analyst would make on
a tampered file. No offensive activity; keys never leave the VM.

## Environment

| Host | Role | Notes |
| --- | --- | --- |
| `lab-ubuntu` | Target | `openssl`, `sha256sum`, `md5sum`, `base64` (standard) |

## Before you start

```bash
mkdir -p ~/cyber/level-1/lab-113-01/evidence
cd ~/cyber/level-1/lab-113-01
work=/tmp/lab113 && mkdir -p "$work" && cd "$work"
```

## Procedure

### Step 1 — Establish a baseline

```bash
printf 'Task report\nOwner: analyst\nStatus: draft\n' > report.txt
sha256sum report.txt | tee ~/cyber/level-1/lab-113-01/evidence/baseline.txt
md5sum report.txt   | tee -a ~/cyber/level-1/lab-113-01/evidence/baseline.txt
wc -c report.txt
```

**Expected** (digests differ every run only if the content differs — here they are deterministic):

```text
<64 hex chars>  report.txt
<32 hex chars>  report.txt
43 report.txt
```

### Step 2 — Change one character

```bash
sed -i 's/draft/final/' report.txt
sha256sum -c ~/cyber/level-1/lab-113-01/evidence/baseline.txt 2>&1 | head -3
```

**Expected:**

```text
report.txt: FAILED
sha256sum: WARNING: 1 computed checksum did not match
```

That `FAILED` is the entire point of the lab: a one-word change produces a completely different digest, and
the check catches it without knowing anything about the file's contents.

### Step 3 — Compare algorithms

```bash
sha256sum report.txt
md5sum report.txt
```

Note in your notes: both changed, so is MD5 "working"? Explain why MD5 still detects *accidental* change but
is unacceptable for *security* (collisions can be constructed deliberately).

### Step 4 — Generate a signing key

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out priv.pem 2>/dev/null
openssl pkey -in priv.pem -pubout -out pub.pem
ls -l priv.pem pub.pem
head -1 priv.pem; head -1 pub.pem
```

**Expected:** `priv.pem` begins `-----BEGIN PRIVATE KEY-----` and `pub.pem` begins
`-----BEGIN PUBLIC KEY-----`. Protect the private key:

```bash
chmod 600 priv.pem
```

### Step 5 — Sign and verify

```bash
openssl dgst -sha256 -sign priv.pem -out report.sig report.txt
openssl dgst -sha256 -verify pub.pem -signature report.sig report.txt
```

**Expected:** `Verified OK`.

### Step 6 — Prove tampering is detected

```bash
printf 'Status: approved by finance\n' >> report.txt
openssl dgst -sha256 -verify pub.pem -signature report.sig report.txt
echo "verify exit: $?"
```

**Expected:**

```text
Verification failure
verify exit: 1
```

### Step 7 — Prove the wrong key fails

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out other.pem 2>/dev/null
openssl pkey -in other.pem -pubout -out other-pub.pem
openssl dgst -sha256 -verify other-pub.pem -signature report.sig report.txt; echo "exit: $?"
```

**Expected:** `Verification failure`, exit 1. A valid signature only verifies against the matching key —
which is why key distribution and trust matter as much as the mathematics.

### Step 8 — Record findings

Write `findings.md`:

1. What did the failed checksum prove, and what did it not prove?
2. Why does changing one word change the whole digest?
3. What does a signature add that a hash alone does not?
4. Why must `priv.pem` never be shared, while `pub.pem` can be?

## Evidence to collect

`evidence/baseline.txt` (both digests), the `FAILED` check output, `Verified OK` and `Verification failure`
outputs, and `findings.md`.

## Verification

- [ ] Baseline SHA-256 and MD5 recorded before modification.
- [ ] `sha256sum -c` reported `FAILED` after a one-word change.
- [ ] A signature verified as `Verified OK` on unmodified content.
- [ ] The same signature failed after modification and with a different public key.
- [ ] Private key mode is `600`.

## Teardown and reset

```bash
chmod 600 /tmp/lab113/priv.pem 2>/dev/null
rm -rf /tmp/lab113
ls /tmp/lab113 2>/dev/null || echo "lab files removed"
```

Keep only the evidence folder on the host filesystem. Never copy `priv.pem` out of the VM — even a lab key
teaches the wrong habit.

## Reflection

1. Why is a checksum published next to a download insufficient protection against a compromised server?
2. What would an attacker need in order to forge a valid signature?
3. Why is `sha256sum -c` more useful than comparing digests by eye?
4. Where would a signature be useless even though it verifies?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Hash computed, no integrity test | Change detected and signature verified | Both failure cases demonstrated with exit codes |
| Methodology | Commands copied | Ordered baseline → change → verify | Explains why each step establishes a specific fact |
| Evidence | Output not saved | All outputs saved | Annotated evidence with digest comparison and key handling note |
| Safety | Private key world-readable or exported | Key protected in VM | Key protected, never exported, deleted at teardown |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `sha256sum: no properly formatted checksum lines found` | Saved output contains extra text | Keep only the `digest  filename` line |
| `Verified OK` on modified file | Signature created after modification | Recreate baseline, then re-sign before tampering |
| `unable to load key` | Wrong key type or truncated file | Regenerate; check `head -1` markers |
| `Verification failure` on unmodified file | Line-ending change (CRLF) | Recreate the file with `printf`, not a Windows editor |
| `md5sum` unchanged after edit | Edited a different file | Check `pwd` and `ls -l` |
| Permission denied writing `priv.pem` | Directory not writable | Work inside `/tmp/lab113` |

## Related

- [Cryptography You Will Actually Use](01-crypto-hashing-signatures.md)
- [LAB-110-01 · Inspect a Windows Host](../10-windows-powershell-basics/lab-01-windows-inspection.md) — cross-platform hash
- [Password Security, MFA and Phishing](../14-passwords-mfa-phishing/index.md)

---
title: "Cryptography You Will Actually Use"
description: "Encryption versus hashing, key exchange, digital signatures, certificates, and the failure modes that matter."
module_code: CYB-113
level: 1
kind: lesson
prerequisites: [CYB-112]
estimated_minutes: 120
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [cryptography, hashing, signatures, pki]
---

# Cryptography You Will Actually Use

## Learning objectives

By the end of this lesson you can:

1. Match four primitives — symmetric encryption, asymmetric encryption, hashing, signatures — to the problem
   each solves.
2. Explain why hashing is not encryption, and why MD5 and SHA-1 are unfit for integrity.
3. Compute and compare a SHA-256 digest, and explain what a mismatch proves.
4. Sign a file and verify the signature, explaining what each key does.
5. Describe what a certificate binds and why validation is the security-critical step.
6. Name five real-world cryptographic failures.

## Prerequisites

[CYB-112](../12-kali-linux/index.md). `openssl` and `sha256sum` are already installed on Ubuntu.

---

## 1. Four primitives, four jobs

| Primitive | Job | Key(s) | Example |
| --- | --- | --- | --- |
| **Symmetric encryption** | Keep data confidential | One shared key | AES-256-GCM |
| **Asymmetric encryption** | Confidentiality or key exchange without a shared secret | Public + private key | RSA-OAEP, ECDH for exchange |
| **Hashing** | Detect change; fingerprint data | None | SHA-256 |
| **Digital signature** | Prove origin and integrity | Sign with private, verify with public | RSA/ECDSA signatures |

Three rules of thumb that prevent most confusion:

- **Hashing is one-way.** You cannot "decrypt" a hash; you can only guess inputs and compare.
- **Encryption hides content; signatures prove authorship.** A signed message can be public.
- **Never invent your own scheme.** Use vetted libraries and standard constructions.

### Why hashes matter even without secrecy

A hash is a fixed-length fingerprint. Any change to the input changes the output unpredictably
(*avalanche effect*). That is why hashes verify downloads, detect tampering, and store password
verifiers.

| Algorithm | Status |
| --- | --- |
| MD5 | Broken for security; collisions are trivial |
| SHA-1 | Broken for security; collisions demonstrated |
| SHA-256 / SHA-512 | Acceptable |
| bcrypt, scrypt, Argon2 | Correct choices for **passwords** (deliberately slow) |

A password hashed with SHA-256 is a design flaw: it is fast, so billions of guesses per second are feasible.
Password hashing needs a slow, salted, memory-hard function — see CYB-114.

## 2. Symmetric versus asymmetric, in practice

Real systems use both, because each is good at a different thing:

```text
TLS handshake (simplified)
1. Client and server agree on a shared secret  ← asymmetric (or ECDH) to protect the exchange
2. All traffic is encrypted with that secret   ← symmetric, because it is fast
3. The server proves its identity              ← certificate + signature
```

Symmetric encryption alone cannot solve key distribution: both sides need the same key, and sharing it
securely is the hard part. Asymmetric cryptography solves distribution but is slow. Hence the hybrid.

**Forward secrecy** matters operationally: with ephemeral key exchange (ECDHE), a stolen long-term private
key cannot decrypt past sessions. That is why modern TLS configurations prefer it.

## 3. Digital signatures

A signature is a hash of the data, encrypted with the signer's **private** key. Anyone with the **public**
key can verify it.

| Step | Who | Key used |
| --- | --- | --- |
| Sign | Sender | Private |
| Verify | Anyone | Public |

What a valid signature proves: the data was signed by the holder of that private key, and has not changed
since. What it does not prove: that the signer is trustworthy, that the key was not stolen, or that the
content is correct.

```bash
cd /tmp && mkdir -p sigdemo && cd sigdemo
printf 'release notes v1\n' > notes.txt
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out priv.pem 2>/dev/null
openssl pkey -in priv.pem -pubout -out pub.pem
openssl dgst -sha256 -sign priv.pem -out notes.sig notes.txt
openssl dgst -sha256 -verify pub.pem -signature notes.sig notes.txt
```

**Expected:**

```text
Verified OK
```

Now change one byte and verify again:

```bash
printf 'release notes v2\n' > notes.txt
openssl dgst -sha256 -verify pub.pem -signature notes.sig notes.txt
```

**Expected:**

```text
Verification failure
```

That single word is the entire value of signatures: the change is detected, and the origin is bound to a key.

Cleanup:

```bash
cd /tmp && rm -rf sigdemo
```

## 4. Certificates and trust

A certificate binds a **public key** to an **identity** (a hostname or organisation) and is signed by a
certificate authority. Your browser trusts a set of root authorities; a server's certificate must chain to
one of them, match the hostname, and be within its validity period.

Three consequences:

- Encryption without validation is encryption to an unknown party.
- A compromised or mis-issued CA breaks the model for everyone who trusts it.
- Self-signed certificates are fine for labs and internal testing, and unacceptable for public services
  without an explicit trust decision.

You demonstrated validation failing in CYB-108 (`curl` exit code 60). That error is the control working.

## 5. How cryptography fails in the real world

| Failure | What it looks like | Why it happens |
| --- | --- | --- |
| Weak algorithm | MD5 for integrity, DES for encryption | Legacy compatibility |
| Fast hashing for passwords | SHA-256 password digests | Misunderstanding the threat model |
| Reused IV/nonce | Same key and IV in CTR/GCM | Copy-pasted code |
| ECB mode | Identical plaintext blocks produce identical ciphertext | Defaults in old libraries |
| No integrity check | Encryption without a MAC/AEAD | "We encrypted it, so it is safe" |
| Homemade crypto | XOR with a repeating key | Not invented here syndrome |
| Key management | Keys in source code, shared over chat | Operational neglect |
| Disabled validation | `verify=False`, `-k` in scripts | Convenience, then habit |

Almost none of these are mathematical breaks. They are engineering mistakes, which is why this module is
about usage rather than number theory.

## 6. What to do in practice

1. **Do not implement cryptography.** Use a maintained library.
2. **Use high-level APIs.** `age`, `openssl enc` with a modern cipher, libsodium sealed boxes.
3. **Verify integrity separately from confidentiality.** AEAD modes (AES-GCM, ChaCha20-Poly1305) do both.
4. **Store passwords with Argon2id, bcrypt, or scrypt** — never a general-purpose hash.
5. **Never disable certificate validation** in code you ship.
6. **Rotate and store keys properly**, and record where they live.

---

## Practical exercises

### Exercise 1 — Hash and change (10 minutes)

```bash
cd /tmp && printf 'integrity check\n' > f1.txt
sha256sum f1.txt | tee before.txt
printf 'integrity check!\n' >> f1.txt
sha256sum f1.txt | tee after.txt
diff <(cut -d' ' -f1 before.txt) <(cut -d' ' -f1 after.txt) && echo "same" || echo "different"
```

Answer: what does the difference prove, and what does it not prove about *who* changed the file?

### Exercise 2 — Cross-platform digests (10 minutes)

Create the same content on Windows and hash it with `Get-FileHash -Algorithm SHA256`. Compare with
`sha256sum`. Explain why identical bytes give identical digests even though the operating systems differ.

### Exercise 3 — Signature workflow (20 minutes)

Run the sign/verify demonstration in section 3. Then:

- verify with the **wrong** public key (generate a second key pair) and record the error;
- explain in your notes why the signature does not hide the file's contents.

### Exercise 4 — Classify the failure (15 minutes)

For each, name the primitive misused and the consequence:

1. A site stores passwords as `sha256(password)`.
2. A backup tool encrypts with AES-CBC and no MAC.
3. An internal API client sets `verify=False`.
4. A file-transfer tool publishes MD5 checksums.

## Expected observations and verification

- You produced `Verified OK` and `Verification failure` from the same signature.
- You can explain the difference between a hash and a signature in one sentence.
- You classified all four failures correctly.
- You can state why SHA-256 is wrong for passwords but right for file integrity.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| "Hash the password with SHA-256" | Looks cryptographic | Use Argon2id/bcrypt; slow is the point |
| Comparing hashes of different files | Line endings, encoding | Compare identical bytes |
| Treating a signature as encryption | Both use keys | Signatures prove origin; they do not hide content |
| Trusting `md5sum` output for security | Habit from downloads | Use SHA-256; MD5 is for accidental corruption only |
| Using `openssl enc` with a password and no KDF awareness | Old tutorials | Prefer `age` or explicit `-pbkdf2`/`-iter` with modern ciphers |
| Believing TLS means the server is trustworthy | Padlock psychology | Validation proves domain control, not intent |

## Review questions

1. Why can a hash not be "decrypted"?
2. What does a signature prove, and what does it not prove?
3. Why is MD5 unacceptable for integrity in a security context?
4. Why is a fast hash wrong for password storage?
5. What does a certificate bind together?
6. Name three cryptographic failures that are engineering, not mathematics.

## Knowledge check

1. Which primitive detects that a file changed?
2. Which key signs, and which verifies?
3. What does `Verification failure` from `openssl dgst -verify` mean?
4. Why is ECB mode unsuitable for encrypting structured data?
5. What does `curl` exit code 60 indicate?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 1, 3 and 5 if 1, 2 and 4 are uncertain.)*

## Summary

- Four primitives, four jobs: symmetric, asymmetric, hash, signature — do not substitute one for another.
- Hashes detect change; signatures prove origin and integrity.
- Certificates bind keys to identities, and validation is the security-critical step.
- Real failures are implementation mistakes: weak algorithms, fast password hashing, missing integrity, key
  mismanagement, disabled validation.
- Use vetted libraries and standard constructions; never invent cryptography.

## Next lesson

[CYB-114 · Password Security, MFA, Phishing Awareness and Personal Security](../14-passwords-mfa-phishing/index.md) —
where cryptography meets human behaviour.

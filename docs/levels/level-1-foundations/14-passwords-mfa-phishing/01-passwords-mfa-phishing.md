---
title: "Passwords, MFA and Phishing"
description: "Credential attack patterns, password storage and policy, MFA's real coverage, and how phishing is constructed."
module_code: CYB-114
level: 1
kind: lesson
prerequisites: [CYB-113]
estimated_minutes: 120
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [passwords, mfa, phishing, awareness]
---

# Passwords, MFA and Phishing

## Learning objectives

By the end of this lesson you can:

1. Distinguish guessing, spraying, stuffing, and phishing, and name the control that stops each.
2. Explain how passwords should be stored, and why salting and slow hashing matter.
3. Evaluate a password policy against current guidance rather than folklore.
4. Compare MFA factor types and name the attacks that survive them.
5. Analyse a phishing email using a repeatable checklist rather than intuition.
6. Apply personal security practices proportionate to real risk.

## Prerequisites

[CYB-113](../13-cryptography-hashing-signatures/index.md).

---

## 1. How credentials are attacked

| Attack | What it is | What stops it |
| --- | --- | --- |
| **Guessing** | Trying likely passwords against one account | Lockout/backoff, strong passwords, MFA |
| **Spraying** | One common password across many accounts | Rate limiting, breached-password screening, MFA |
| **Stuffing** | Reusing credentials leaked from another site | Unique passwords, breach monitoring, MFA |
| **Phishing** | Convincing a person to hand over credentials | Awareness plus technical controls (phishing-resistant MFA) |
| **Session theft** | Stealing a cookie or token after login | Short sessions, binding, rotation on privilege change |
| **MFA fatigue** | Repeated push prompts until the user approves | Number matching, rate limits, phishing-resistant factors |
| **Reset abuse** | Attacking the recovery flow instead of the password | Strong identity proofing for resets |

Two observations that change how you think about this:

- **Stuffing is the dominant real-world pattern.** It requires no cleverness: breaches leak credentials, and
  people reuse them. Unique passwords per site break the chain.
- **The password is often not the weakest link; the reset flow is.** Support desks under time pressure are a
  classic target.

## 2. Storing passwords correctly

A server must never store the password itself, and must never store a fast hash of it.

| Approach | Verdict |
| --- | --- |
| Plaintext | Catastrophic |
| Encrypted (reversible) | Bad: key compromise exposes everything |
| MD5/SHA-1/SHA-256 | Wrong: too fast, billions of guesses per second |
| Salted SHA-256 | Still too fast |
| bcrypt / scrypt / Argon2id | Correct: slow and memory-hard by design |

**Salting** ensures two users with the same password get different hashes, defeating precomputed tables.
**Peppering** adds a server-side secret for defence in depth. **Work factors** must be tuned so verification
takes a deliberate fraction of a second.

## 3. What a good policy looks like now

Current guidance (notably NIST SP 800-63B) reverses several decades of habit:

| Old habit | Current guidance | Why |
| --- | --- | --- |
| Force 90-day rotation | Rotate only on evidence of compromise | Rotation produces `Summer2026!` → `Autumn2026!` |
| Require symbols, mixed case, numbers | Require length; screen against breached lists | Composition rules produce predictable patterns |
| Cap length at 12–16 | Allow at least 64 characters | Long passphrases are stronger and easier |
| Security questions | Avoid; use other recovery | Answers are often public or guessable |
| Email a temporary password | Use a time-limited, single-use reset link | Email is not a secure channel |

What actually helps: **length**, **blocklists of breached passwords**, **rate limiting**, **MFA**, and
**password managers** so nobody has to memorise thirty unique secrets.

## 4. MFA: what it covers, what it does not

| Factor type | Example | Strength | Weakness |
| --- | --- | --- | --- |
| Something you know | Password, PIN | Low alone | Reused, phished, guessed |
| Something you have | TOTP app, hardware key | Medium–high | Real-time phishing can relay codes; device loss |
| Something you are | Fingerprint, face | Medium | Not revocable; template storage risk |
| Push approval | App notification | Medium | MFA fatigue, prompt bombing |
| Passkey / FIDO2 | Hardware key, platform authenticator | High | Origin-bound, phishing-resistant; recovery must be designed |

MFA is the single highest-value control for account takeover, and it is not a guarantee:

- **Real-time phishing proxies** relay a session after the user authenticates; only origin-bound credentials
  (passkeys/FIDO2) resist this.
- **Session tokens** can be stolen after MFA; that is why session binding and short lifetimes matter.
- **Recovery flows** can bypass MFA entirely if they are weaker than the front door.

## 5. Reading a phishing email

Work through the same list every time, in this order:

| # | Check | Red flag |
| --- | --- | --- |
| 1 | **Sender address**, not display name | Lookalike domain, free mail provider, reply-to differs |
| 2 | **Authentication results** (SPF/DKIM/DMARC) | `fail` or `none` on a domain that should publish them |
| 3 | **Link destination**, hovered or copied, never clicked | Domain differs from the claimed organisation |
| 4 | **Urgency and threat** | "Within 24 hours or your account is closed" |
| 5 | **Request type** | Credentials, MFA code, payment change, gift cards |
| 6 | **Context** | Unexpected invoice, unusual sender, wrong tone |
| 7 | **Attachment** | HTML file, archive, macro-enabled document |

Two rules that prevent most harm: **never authenticate from a link in an email**, and **verify through a
channel you initiate** (type the address yourself, or call the number on the official site).

### Why awareness training alone is not enough

People click. Under time pressure, with a plausible pretext, most people will eventually make a mistake. So
the technical controls must assume that: phishing-resistant MFA, least privilege, and rapid detection of
credential use.

## 6. Personal security that actually helps

1. **A password manager**, so every account has a unique, long password.
2. **MFA everywhere it is offered** — preferably an app or passkey, not SMS.
3. **Updates** on by default, including the browser and the phone.
4. **Encrypted backups** you have tested restoring.
5. **Device encryption and screen lock** — a stolen laptop should not be a data breach.
6. **Check breach exposure** for your own accounts, and change reused passwords.
7. **Slow down on urgency.** Urgency is the attacker's primary tool, not a coincidence.

None of these make you "secure"; together they remove the cheapest attacks.

---

## Practical exercises

### Exercise 1 — Classify the attack (10 minutes)

For each scenario, name the attack type and one control:

1. `Spring2026!` is tried against 400 accounts.
2. A leaked credential list is replayed against a shopping site.
3. An email asks you to "re-authenticate" through a link.
4. A user approves a push notification they did not request.

### Exercise 2 — Policy critique (15 minutes)

> "Passwords must be 8–12 characters, include upper case, lower case, a number and a symbol, and must be
> changed every 60 days. Security questions are required for recovery."

List five problems and rewrite the policy in three sentences. *(Hint: length, blocklist, rotation, recovery,
MFA.)*

### Exercise 3 — Hash comparison (10 minutes)

On `lab-ubuntu`:

```bash
printf 'password123' | sha256sum
printf 'password123' | sha256sum
printf 'password124' | sha256sum
```

Answer: why do the first two match exactly, and what would a salt change? Then explain why this hash is
still unsuitable for storing a password.

### Exercise 4 — Header habits (10 minutes)

Take any legitimate marketing email in your own inbox and identify: `From`, `Return-Path`, `Reply-To`, and the
authentication results (in most clients: "Show original" or "View headers"). You are practising the read, not
investigating anyone.

## Expected observations and verification

- You classified all four attacks correctly and named a control for each.
- Your rewritten policy uses length, blocklists, MFA, and a safe recovery flow.
- You can explain salt's purpose in one sentence.
- You found the authentication headers in a real (legitimate) email.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Judging phishing by grammar alone | Many real phishes are well written | Check sender, links, and requests instead |
| Clicking to "see if it is real" | Curiosity | Never authenticate from a link; verify independently |
| Believing MFA ends credential attacks | Marketing | Session theft and relay phishing exist |
| Enforcing rotation to "improve security" | Tradition | Rotate on compromise evidence, not on a calendar |
| Storing passwords with SHA-256 | Looks cryptographic | Use Argon2id or bcrypt with tuned work factors |
| Password reuse "only for unimportant sites" | Convenience | Reuse chains escalate: email → everything |

## Review questions

1. What is the difference between spraying and stuffing?
2. Why does salting not make a fast hash acceptable for passwords?
3. Give two NIST-aligned policy changes that contradict common practice.
4. Which MFA type resists real-time phishing, and why?
5. What are the first three checks on a suspicious email?
6. Why do technical controls have to assume users will click?

## Knowledge check

1. Which attack does a breached-password blocklist primarily stop?
2. What property must a password hashing function have that SHA-256 lacks?
3. What does DMARC `fail` in the authentication results suggest?
4. Why is SMS-based MFA weaker than a passkey?
5. What is MFA fatigue?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 1, 3 and 5 if 2, 3 and 5 are uncertain.)*

## Summary

- Credential attacks are mostly reuse and phishing; unique passwords and strong MFA address both.
- Passwords must be stored with a slow, salted, memory-hard function — never a general-purpose hash.
- Current policy guidance favours length, blocklists, rate limiting, and avoiding forced rotation.
- MFA is the highest-value control, but not a guarantee; phishing-resistant factors are stronger.
- Phishing is read analytically: sender, authentication, links, urgency, request, context.
- Personal security is a set of cheap habits, not a product.

## Next lesson

[CYB-115 · Introduction to Security Logs and Basic Troubleshooting](../15-security-logs-and-troubleshooting/index.md) —
turning everything you have learned into evidence you can read.

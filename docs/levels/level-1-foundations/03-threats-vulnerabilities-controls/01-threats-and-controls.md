---
title: "Threats, Vulnerabilities, Exploits and Controls"
description: "Threat actors and motivations, vulnerability classes and lifecycle, how exploits work, and how controls are classified."
module_code: CYB-103
level: 1
kind: lesson
prerequisites: [CYB-102]
estimated_minutes: 120
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [foundations, threats, controls, vulnerability-management]
---

# Threats, Vulnerabilities, Exploits and Controls

## Learning objectives

By the end of this lesson you can:

1. Describe six threat actor categories and what each is optimising for.
2. Distinguish design, implementation, configuration, and operational vulnerabilities with examples.
3. Outline the vulnerability management lifecycle, including prioritisation and verification.
4. Explain what an exploit is and why most breaches do not require one.
5. Classify controls by function (preventive, detective, corrective, compensating) and by type
   (administrative, technical, physical).
6. Design a three-layer defence for a small scenario and justify each layer.

## Prerequisites

[CYB-102](../02-cia-triad-principles-risk/index.md), including your five-line risk register.

---

## 1. Who the threats are

| Actor | Motivation | Capability | What changes in your defence |
| --- | --- | --- | --- |
| **Opportunistic criminal** | Money, at scale | Moderate, automated | Patching and basic hardening removes you from their list |
| **Organised crime** | Money, targeted | High, patient | Detection and response matter; they will get in somewhere |
| **Nation state** | Espionage, disruption | Very high, long-term | Assume compromise; focus on containment and attribution limits |
| **Insider** | Grievance, money, coercion | Legitimate access | Least privilege, separation of duties, logging of privileged actions |
| **Hacktivist** | Ideology, publicity | Variable | Availability and reputation protection, rapid disclosure planning |
| **Accidental insider** | Speed, confusion | None required | Design that makes the safe path the easy path |

Two non-human threat sources matter just as much: **environmental** (power, flood, hardware failure) and
**supply chain** (a compromised dependency, a vendor's breach). Both are routinely omitted from
amateur risk assessments.

Most incidents are unglamorous: a reused password, a missing patch, an over-privileged service account, a
backup that was never tested. Plan for the boring majority.

## 2. Vulnerability classes

| Class | Where it comes from | Example |
| --- | --- | --- |
| **Design** | The architecture is wrong | Password reset by security question; unlimited login attempts by design |
| **Implementation** | A coding defect | Missing bounds check; string-concatenated SQL |
| **Configuration** | Correct software, wrong settings | Directory listing enabled; default admin password |
| **Operational** | Process fails over time | Patches approved but not deployed; certificates expire unnoticed |

The last two are where most real-world findings live, and they are the ones a beginner can find without
advanced skills. That is encouraging: careful configuration review catches a lot.

### The vulnerability lifecycle

1. **Discover** — scan, review, report, or observe.
2. **Triage** — is it real? Is it reachable? Does it matter here?
3. **Prioritise** — impact × likelihood × exposure, not scanner severity alone.
4. **Remediate** — patch, reconfigure, isolate, or accept with an owner.
5. **Verify** — prove the fix worked (re-scan is not enough; test the behaviour).
6. **Track** — record the decision and the residual risk.

### Identifiers you will meet

- **CVE** — a public identifier for a disclosed vulnerability, e.g. `CVE-2021-44228`.
- **CVSS** — a 0–10 severity score with a vector string describing the conditions. Useful for comparison,
  dangerous as a substitute for judgement: a 9.8 in an unreachable service may matter less than a 6.5 in
  an internet-facing login.
- **CWE** — a taxonomy of weakness types (e.g. CWE-89, SQL injection), useful when writing findings.

## 3. What an exploit is, and what it is not

An **exploit** is a technique or piece of code that uses a vulnerability to produce an effect the designer
did not intend. A **payload** is what runs after; a **proof of concept (PoC)** demonstrates the flaw
minimally, often without harm.

- A vulnerability can exist without a public exploit.
- An exploit can exist without a vulnerability — using valid credentials, or a misconfiguration, is not
  exploiting a flaw in code.
- **Zero-day** means no patch exists publicly at the time of use. It does not mean "unfixable", and it is
  rarer in practice than marketing suggests.

The professional point: findings describe **the weakness and its impact**, not the cleverness of the
exploit. "Unrestricted file upload allows server-side code execution as the web user" is a finding. "I
used a famous tool" is not.

## 4. Controls

Classify every control on two axes — that is how control maps are built.

### By function

| Function | Purpose | Example |
| --- | --- | --- |
| **Preventive** | Stop the event | MFA, input validation, firewall deny rule |
| **Detective** | Reveal the event | Log alert on failed logins, file-integrity monitoring |
| **Corrective** | Reduce harm after the event | Restore from backup, revoke a session, isolate a host |
| **Compensating** | Substitute when the primary control is impossible | Network isolation instead of patching a legacy system |
| **Deterrent** | Discourage the attempt | Warning banners, visible monitoring, prosecution policy |

### By type

- **Administrative** — policies, training, approval workflows, separation of duties.
- **Technical** — configuration, code, cryptography, monitoring.
- **Physical** — locks, badges, camera coverage, server-room access.

### Layering

A single control is a single point of failure. A defensible design layers them:

```text
Login to an admin panel
  preventive   → VPN required, MFA enforced, least-privilege role
  detective    → alert on 5 failed attempts, alert on new source country
  corrective   → automatic session revocation, account lock with self-service unlock
  compensating → read-only fallback account for emergencies
```

Each layer answers a different question, and the failure of one does not become the failure of all.

## 5. Matching control to risk

For each risk in your register, ask in order:

1. Can we remove the exposure entirely? (best, often impossible)
2. Can we prevent it with a control people will actually use?
3. If not, can we detect it quickly enough to limit impact?
4. If not, can we correct it fast — backups, failover, revocation?
5. If none of the above, document the acceptance and the owner.

---

## Practical exercises

### Exercise 1 — Classify the actors (10 minutes)

For each scenario, name the most likely actor and one control that specifically addresses them:

1. A university web server is brute-forced with credentials from an old breach.
2. A departing employee copies a client list to personal storage.
3. A widely used file-transfer product is compromised at the vendor and used to reach customers.

### Exercise 2 — Vulnerability classification (10 minutes)

Label each as design, implementation, configuration, or operational:

1. A session token never expires.
2. A backup runs nightly but restores have never been attempted.
3. `/var/www/uploads` is served with directory listing enabled.
4. A search function concatenates user input into a database query.

### Exercise 3 — Read a CVSS vector (15 minutes)

```text
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H  → 9.8
```

Decode it with the table below, then answer the question after it.

| Component | This value means |
| --- | --- |
| `AV:N` | Attackable over the network |
| `AC:L` | Low complexity — no special conditions |
| `PR:N` | No privileges required |
| `UI:N` | No user interaction |
| `C:H / I:H / A:H` | High confidentiality, integrity, availability impact |

**Question:** the affected service is only reachable from an isolated management VLAN with no route from
the internet. Does it remain a 9.8 *for this organisation*? Write two sentences justifying your answer.
*(There is no single correct number; the reasoning is the exercise.)*

### Exercise 4 — Build a control map (25 minutes)

Choose one risk from your CYB-102 register and complete:

| Layer | Control | Type | Function | How you would verify it works |
| --- | --- | --- | --- | --- |
| Preventive | | | | |
| Detective | | | | |
| Corrective | | | | |

### Exercise 5 — Find the missing control (10 minutes)

A team stores nightly database backups on the same server as the database, unencrypted, with no restore
test. List three distinct risks and one control for each. This scenario is common enough that it is worth
recognising instantly.

## Expected observations and verification

- You can place any finding into the chain: threat → vulnerability → exploit → impact → control.
- Your control map has at least one detective control; beginners over-invest in prevention.
- You can argue why a high CVSS score may be low priority in a specific environment.
- You can name one compensating control and when it is appropriate.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| "We have a firewall, so we are protected" | Single-control thinking | Ask what happens when it is misconfigured — it will be |
| Chasing CVSS scores | It is a convenient number | Multiply by exposure and business impact |
| Treating patching as the whole programme | Visible, measurable, satisfying | Configuration and identity are usually the bigger gaps |
| Writing findings as tool output | Fast, and it feels objective | State weakness, evidence, impact, fix |
| Forgetting corrective controls | Prevention gets the budget | A tested restore beats an untested "we have backups" |
| Assuming insider threats are rare | They are under-reported, not rare | Least privilege and logging of privileged actions |

## Review questions

1. Which threat actor is best countered by least privilege, and why?
2. Why is "patch everything immediately" not a complete vulnerability management strategy?
3. What is the difference between an exploit and a payload?
4. Give an example of a compensating control and the situation that justifies it.
5. Why are detective controls under-funded in many organisations, and what does that cost?
6. What are the six steps of the vulnerability lifecycle?

## Knowledge check

1. A default administrator password left unchanged is which class of vulnerability?
2. A CVSS 9.8 vulnerability in a service unreachable from any network is best treated how, initially?
3. Name the control function that limits harm *after* an event.
4. What does "zero-day" actually mean?
5. Which control type is a security-awareness training programme: administrative, technical, or physical?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 2 and 4 if 1 and 3 are uncertain.)*

## Summary

- Threat actors differ in capability and patience; your defences should differ accordingly.
- Vulnerabilities are design, implementation, configuration, or operational — and the last two dominate.
- Exploits are not required for most breaches; credentials and misconfigurations suffice.
- Controls are classified by function and type, and layered so one failure is not total.
- Every finding should name the weakness, the evidence, the impact, and the fix.

## Next lesson

[CYB-104 · Threat Modeling and Attack Surfaces](../04-threat-modeling-attack-surfaces/index.md) — using
this vocabulary *before* anything is built, which is when it is cheapest to act on.

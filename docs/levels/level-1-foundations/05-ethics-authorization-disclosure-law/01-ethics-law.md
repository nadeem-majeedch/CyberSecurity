---
title: "Ethics, Authorization, Responsible Disclosure and Cyber Law"
description: "Authorization artefacts, scope writing, coordinated disclosure, and the legal framework around unauthorized access."
module_code: CYB-105
level: 1
kind: lesson
prerequisites: [CYB-104]
estimated_minutes: 150
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [ethics, law, disclosure]
---

# Ethics, Authorization, Responsible Disclosure and Cyber Law

!!! warning "This lesson is orientation, not legal advice"
    Laws change, and they differ by jurisdiction. The summary here is for professional awareness. For any
    real situation, consult a qualified lawyer and your institution's policy.

## Learning objectives

By the end of this lesson you can:

1. Define authorization and list the four elements it must contain.
2. Write a scope statement for your own lab that a reviewer could accept.
3. Explain the responsible disclosure process, including timelines and escalation paths.
4. Identify the main legal provisions covering unauthorized access in Pakistan and comparable laws
   elsewhere, and explain why "educational purpose" is not a defence.
5. Classify realistic scenarios as authorized or unauthorized with a written justification.
6. State the course rules and complete the acknowledgement.

## Prerequisites

[CYB-104](../04-threat-modeling-attack-surfaces/index.md), and the
[Safety Policy](../../../policies/safety-policy.md) open in another tab.

---

## 1. Ethics is not a formality

Three ideas do the work:

- **Authorization** — permission from someone entitled to give it, for a defined activity, in advance.
- **Proportionality** — the least intrusive action that answers the question. You do not need to dump a
  database to prove a query is injectable.
- **Duty of care** — you are responsible for the consequences of your actions, including accidental ones.

A professional asks three questions before touching anything: *Am I allowed? Am I staying inside what I am
allowed to do? What happens if this goes wrong?* If any answer is unclear, the correct action is to stop
and ask.

## 2. What authorization must contain

Verbal permission from a colleague is not authorization. A defensible authorization is written and
contains:

| Element | Why it matters | Weak example | Strong example |
| --- | --- | --- | --- |
| **Who** | Identifies the authorizing party | "IT said it was fine" | Signed by the CIO, named individual |
| **What** | Defines the targets precisely | "our website" | `staging.example.edu`, IP `192.0.2.50`, port 443 |
| **Which methods** | Rules out prohibited activity | unstated | "Non-destructive testing; no DoS, no social engineering" |
| **When** | A window, so activity is expected | unstated | 2026-11-03 09:00–17:00 PKT |
| **Data handling** | What may be collected and kept | unstated | "Screenshots only; no exfiltration of personal data" |
| **Escalation** | Who to call if something breaks | unstated | Named contact and phone number |

That list is the core of a **rules of engagement** document. You will write a full engagement package in
Level 5 (CYB-501); for now, you need the shape.

### Scope statement for your own lab

You own your lab, so you authorize yourself. Write it down anyway — it builds the habit and protects you
from drift:

```text
Scope statement — personal lab
Authorized by: <your name>, owner of the hardware and hypervisor
Targets: lab VMs on host-only network 192.0.2.0/24 (lab-ubuntu 192.0.2.20, lab-win 192.0.2.30)
Methods: configuration review, local service enumeration, packet capture on lab interfaces,
         exploitation of intentionally vulnerable applications inside the lab
Excluded: any host outside 192.0.2.0/24, the host OS, the home network, the internet,
          university or employer systems
Data: no real personal data; synthetic test data only
Window: ongoing, re-confirmed at the start of each lab
Signature / date:
```

If you cannot fill a line, you do not yet have scope — you have an intention.

## 3. Responsible disclosure

You will find real problems eventually, often by accident. The professional response has a shape:

1. **Stop testing.** Confirm enough to describe the issue; do not enumerate further.
2. **Do not access data.** If you saw records, note the count and stop; do not copy, download, or read.
3. **Document minimally and safely.** Host, time, observed behaviour, and the smallest evidence needed.
4. **Notify the owner privately.** Use a security contact, `security.txt`, or the responsible department.
   If none exists, escalate through a trusted channel rather than publishing.
5. **Agree a timeline.** Common practice is 90 days before public detail, negotiable for critical
   infrastructure. Never publish a working exploit before a fix is available.
6. **Coordinate the write-up.** Credit only if the owner agrees; omit details that would help an attacker.
7. **Escalate if ignored.** For serious, unaddressed risk, a national CERT or regulator may be appropriate.

**Bug bounty programmes** are authorization — but only within their stated scope, rules, and exclusions.
A programme covering `*.example.com` does not authorize testing a subsidiary, an employee's laptop, or a
third-party service the company uses.

## 4. The law, at awareness level

Unauthorized access is criminalised almost everywhere, with similar structure: access, interference,
data acquisition, and identity misuse.

**Pakistan — Prevention of Electronic Crimes Act, 2016 (PECA).** Broadly, it criminalises unauthorized
access to an information system or data, unauthorized copying or transmission of data, interference with a
system or data, unauthorized access to critical infrastructure systems, and unauthorized use of identity
information (ss. 3–6 and 13 in the Act as originally passed; it has been amended since). Penalties include
imprisonment and fines, aggravated for critical infrastructure and sensitive data. **Verify the current text
with counsel** — this paragraph is orientation only.

**Comparable provisions elsewhere:** the U.S. Computer Fraud and Abuse Act; the UK Computer Misuse Act
1990; Canada's Criminal Code computer offences; Australia's Criminal Code computer offences; India's
Information Technology Act 2000; EU Directive 2013/40/EU. Data protection law (GDPR and equivalents) adds
obligations the moment personal data is involved, even if access was authorized.

**Why "educational purpose" fails as a defence.** Criminal provisions turn on *authorization*, not
motivation. A student scanning a university server without permission has committed the same act as an
attacker, whatever the intent. Mitigation at sentencing is not the same as innocence.

**Civil and institutional exposure.** Terms of service, acceptable-use policies, and contracts create
liability independent of criminal law. Suspension, expulsion, and lost job offers are common outcomes, and
they are not appealable on the grounds that nothing was damaged.

## 5. Applying it: the classification test

Before any action, run this sequence:

1. **Whose system is it?** If not yours, stop.
2. **Do I have written authorization covering this target and method?** If not, stop.
3. **Is this the least intrusive way to answer the question?** If not, reduce it.
4. **Would I be comfortable explaining this action to the owner, in writing, tomorrow?** If not, stop.

The fourth question catches most grey areas before they become incidents.

## 6. This course's rules

You may test only: localhost services you started, your own isolated lab network, intentionally vulnerable
applications provided for the course, an instructor-provided range, systems you own outright, or systems
for which you hold written permission.

Prohibited, without exception: scanning public systems, DoS, credential attacks on real accounts, social
engineering real people, accessing real personal data, distributing malware or flags, or using
anonymisation to hide out-of-scope activity.

Full rules, consequences, and the incident procedure: [Safety Policy](../../../policies/safety-policy.md).

---

## Practical exercises

### Exercise 1 — Classify the scenario (25 minutes)

For each, answer **authorized / not authorized / unclear**, with one sentence of reasoning and what you
would do next.

1. You find a login page on your university's portal and try three common passwords to "check" it.
2. A friend asks you to test their personal website; they say "go for it" in a chat message.
3. You are in a bug bounty programme covering `*.example.com`; you test `admin.example.com`.
4. You are in that same programme and test `example.com`'s third-party payment provider.
5. Your lab VM has an intentionally vulnerable app; you exploit it.
6. You notice a public S3 bucket with what looks like customer data while searching for something else.
7. Your employer's IT team asks you in writing to test a staging server, with a defined window.

### Exercise 2 — Write your scope statement (20 minutes)

Use the template in section 2. Then ask a peer (or yourself, a day later) to find three ambiguities. Fix
them.

### Exercise 3 — Draft a disclosure email (20 minutes)

Write the first message you would send to an organisation whose public web application you believe has an
authentication flaw. Constraints: under 200 words, no exploit details beyond what is needed, no demands, a
clear ask, and a suggested timeline.

### Exercise 4 — Spot the bad authorization (10 minutes)

> "Our marketing team said you can test the campaign site, it's fine, just don't break anything."

List five things missing from that authorization. (Who, what, methods, when, data handling, escalation —
name at least five.)

## Expected observations and verification

- You classified all seven scenarios and can defend each.
- Your scope statement names an address range, a method list, and an exclusion list.
- Your disclosure email contains no working exploit and a proposed timeline.
- You can state, without notes, why educational intent is not a legal defence.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Treating a chat message as authorization | It feels like permission | Written, scoped, dated, from someone entitled to grant it |
| "It's my university, so it's fine" | Familiarity implies ownership | You are a user, not the owner; ask the owner |
| Reading data "to confirm" the finding | Curiosity, and it seems harmless | Count and stop; do not view records |
| Publishing a PoC immediately | Reputation, urgency | Coordinate; 90 days is normal, negotiate if critical |
| Assuming a bounty scope is unlimited | Excitement | Read the programme's scope and exclusions first |
| Testing "just the login page" of a public site | Small target feels low-risk | Unauthorized is unauthorized, regardless of size |

## Review questions

1. What are the six elements a defensible authorization must contain?
2. Why is written scope more protective than verbal permission — for both parties?
3. What is the standard disclosure sequence, and why is a timeline agreed rather than announced?
4. Why does "I was learning" fail as a legal defence?
5. What should you do if you accidentally access real personal data during authorized testing?
6. What is the difference between a bug bounty scope and general permission to test?

## Knowledge check

1. Which PECA 2016 category covers copying data you were not authorized to access?
2. A bug bounty covers `*.example.com`. Does it authorize testing `example.com`'s payment processor?
3. What is the least intrusive way to demonstrate an SQL injection flaw without extracting data?
4. Name two consequences of unauthorized testing that are not criminal.
5. Which question in the classification test would catch "testing a friend's site because they said it was
   fine"?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 2, 3, and 5 if 2 and 5 are uncertain.)*

## Summary

- Authorization is written, scoped, time-bound, and granted by the owner — everything else is not
  authorization.
- Proportionality and duty of care govern *how* you act inside an authorized scope.
- Responsible disclosure is coordinated, minimal, and never publishes a working exploit before a fix.
- Unauthorized access is criminal in Pakistan (PECA 2016) and comparable jurisdictions; intent is not a
  defence.
- This course restricts all practical work to owned, isolated, or instructor-provided systems.

## Next lesson

[CYB-106 · Computer Hardware, Operating Systems, Files, Processes and Permissions](../06-computer-hardware-os-fundamentals/index.md) —
where the abstractions become concrete, and where your lab begins.

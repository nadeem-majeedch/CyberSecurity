---
title: "What Cybersecurity Is, and What Practitioners Do"
description: "The four activities of security work, the roles around them, and the authorization rule that governs this course."
module_code: CYB-101
level: 1
kind: lesson
prerequisites: []
estimated_minutes: 45
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [orientation, foundations, careers]
---

# What Cybersecurity Is, and What Practitioners Do

## Learning objectives

By the end of this lesson you can:

1. State what cybersecurity protects, in one sentence, without using the word "hacker".
2. Name the four recurring activities of security work and give one example of each.
3. Distinguish defensive, offensive, engineering, and governance roles, and explain why none works alone.
4. Explain the asymmetry between attacker and defender, and one strategy that compensates for it.
5. State the authorization rule this course enforces, and where to read the full policy.

## Prerequisites

None. You need roughly 45 minutes and something to take notes with.

---

## 1. A plain-language definition

**Cybersecurity is the practice of keeping computer systems and the information in them working
correctly, unchanged by anyone who should not change them, and readable only by those who should.**

That sentence contains three properties you will meet formally in the next module — availability,
integrity, confidentiality — but the important part is what it *isn't*. Security is not secrecy, not a
product you install, and not a list of tools. It is a set of engineering decisions about **risk**:
what could go wrong, how likely it is, how bad it would be, and what is worth doing about it.

Two consequences follow immediately:

- **Perfect security does not exist.** Every control costs money, time, or convenience, and every system
  has a finite budget for all three. The job is to reduce risk to an acceptable level, and to be honest
  about what remains.
- **Security is a property of a system, not of a component.** A perfectly configured server behind an
  application that trusts any input is still insecure.

## 2. The four activities

Whatever the job title, security work tends to fall into four repeating activities.

| Activity | The question it answers | Typical output |
| --- | --- | --- |
| **Prevent** | How do we stop this from happening? | Hardened hosts, patched software, access rules, secure design |
| **Detect** | How would we know if it happened? | Logs, alerts, detection rules, dashboards, audits |
| **Respond** | What do we do when it happens? | Incident reports, containment, recovery, lessons learned |
| **Assure** | How do we know any of that works? | Tests, assessments, audits, metrics, threat models |

Notice that only the first is about blocking. Most real security work is the other three, because
prevention eventually fails somewhere. A useful mental model: **prevention buys time; detection and
response decide how much the failure costs.**

## 3. The roles

| Role | Focus | Works mostly on |
| --- | --- | --- |
| **SOC analyst** (defensive) | Watching, triaging, escalating | Alerts, logs, playbooks |
| **Incident responder** (defensive) | Containing and recovering | Evidence, timelines, communication |
| **Detection engineer** (defensive/engineering) | Turning behaviour into reliable signals | Log pipelines, rule logic, tuning |
| **Security engineer / administrator** | Building and hardening systems | Baselines, configuration, automation |
| **Penetration tester / red team** (offensive) | Finding weaknesses before attackers | Scoping, exploitation, reporting |
| **Application security engineer** | Making software hard to break | Code review, threat models, secure patterns |
| **GRC / governance** | Policy, compliance, risk acceptance | Frameworks, audits, documentation |

These roles argue with each other, and that is healthy: the offensive team says "this is exploitable",
the defensive team says "we would see it", and the governance team asks who accepted the residual risk.
A functioning organisation needs all three answers, in writing.

**A note on the word "hacker".** In professional use, *attacker* or *adversary* describes someone acting
without authorization, and *penetration tester* describes someone doing the same technical work with a
contract. The distinction is legal, not technical. This course uses those words precisely, because
sloppy language leads to sloppy boundaries.

## 4. The asymmetry problem

Attackers choose the time, the target, and the technique. Defenders must cover everything, continuously,
with a budget. That asymmetry never disappears, so professionals compensate:

- **Reduce the attack surface** instead of defending every possible door.
- **Assume compromise** and invest in detection and response, not only prevention.
- **Prioritise by impact**, not by how interesting a vulnerability is.
- **Design for recovery**, because some incidents will succeed.

You will see this reasoning again in CYB-103 (controls) and CYB-104 (threat modelling).

## 5. The rule that governs this course

Everything practical in this course happens on systems **you own or are explicitly authorized to test**:
your own virtual machines, localhost services, deliberately vulnerable applications, synthetic data, or a
lab range provided by the instructor.

The technical skills are identical whether a target is yours or a stranger's. The legal situation is not.
Unauthorized access is a criminal offence in most jurisdictions — in Pakistan, under the Prevention of
Electronic Crimes Act 2016 — and "I was learning" is not a defence.

!!! warning "Read the policy before your first lab"
    The binding rules, the prohibited actions, and what to do if something goes wrong are in the
    [Safety Policy](../../../policies/safety-policy.md). CYB-105 covers it in depth. Skim it now.

## 6. What "good" looks like

Three habits separate professionals from enthusiasts, and this course assesses all three:

1. **You can explain what you did.** Not "I ran the tool", but why that tool, what the output shows, and
   what it cannot show.
2. **You keep evidence.** Commands, outputs, timestamps, environment. Someone else could reproduce it.
3. **You know your boundary.** You can state, out loud, what you were authorized to touch.

None of these are technical skills. All three are what employers actually screen for.

---

## Practical exercises

### Exercise 1 — Write your own definition (5 minutes)

In your notes, write one sentence answering: *what does a security team protect, and from what?*

Then rewrite it so that a non-technical relative would understand it. Keep both versions; comparing them
in six months shows how your thinking changed.

### Exercise 2 — Map a familiar system (10 minutes)

Pick a system you use daily — a university portal, a messaging app, an online shop. List:

| Question | Your answer |
| --- | --- |
| What is the valuable asset? | |
| What would "unavailable" cost the owner? | |
| What would "changed" cost? | |
| What would "leaked" cost? | |
| One control the owner obviously applied | |

You are not expected to be right; you are practising the habit of asking. CYB-102 gives you the
vocabulary to do this properly.

### Exercise 3 — Set up your evidence folder (10 minutes)

```bash
mkdir -p ~/cyber/level-1/{notes,evidence}
cd ~/cyber/level-1
printf '# Level 1 lab log\n\n| Date | Module | Activity | Result |\n| --- | --- | --- | --- |\n' > lab-log.md
ls -R ~/cyber
```

**Expected output** (paths will differ on Windows):

```text
/home/student/cyber:
level-1
/home/student/cyber/level-1:
evidence  lab-log.md  notes
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\cyber\level-1\notes", "$HOME\cyber\level-1\evidence" | Out-Null
Get-ChildItem "$HOME\cyber\level-1"
```

If you are doing this on your host machine before building the lab VM in CYB-111, that is fine — you will
copy the structure into the VM later.

## Expected observations and verification

- You created `notes/`, `evidence/`, and `lab-log.md` in one place you can find again.
- You can name the four activities (prevent, detect, respond, assure) without looking.
- You can state the authorization rule in one sentence.
- Your notes contain your own definition of security, not a copied one.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Equating security with tools | Tool marketing shapes expectations | Ask "which activity does this tool serve?" — most serve detect or prevent only |
| Believing compliance equals security | Audits are periodic; attacks are not | Treat frameworks as a floor, not a ceiling |
| Skipping the ethics material as "not technical" | It feels like paperwork | It is the part that keeps you employable and out of court |
| Scattered notes | No single starting point | One root folder per level, one log file, dated entries |
| `mkdir: cannot create directory` | Parent path missing | `mkdir -p` creates parents; on Windows use `-Force` |

## Review questions

1. In your own words, what does cybersecurity protect?
2. Name the four recurring activities of security work and one output of each.
3. Why does "prevention buys time" matter for how teams spend budget?
4. What distinguishes a penetration tester from an attacker, if the technical work is similar?
5. What are the three professional habits this course assesses, and why are they not technical skills?

## Knowledge check

Answer from memory before checking your notes.

1. Which of these is *detection* rather than *prevention*: a firewall rule, a log alert on failed logins, a
   patched library, or a password policy?
2. A defender cannot cover every possible attack. Name one strategy that compensates for this asymmetry.
3. What authorization do you need before running a network scan against a host?
4. Why is "we passed an audit" not the same as "we are secure"?
5. What are the four activities, in the order a defender typically experiences an incident?

*(These lesson questions are not keyed one by one. The module's quiz and its explained key cover the same
ground — [Level 1 quiz](../../../assessments/level-1-quiz.md) and [key](../../../assessments/level-1-key.md) —
so mark yourself against the lesson and treat anything you cannot justify as a gap to revisit.)*

## Summary

- Security is risk management applied to systems: reduce likelihood and impact, then be honest about
  what remains.
- Practitioners prevent, detect, respond, and assure. Prevention is only the first quarter of the work.
- Roles differ, but the discipline is shared: explain your work, keep evidence, respect boundaries.
- Attackers choose the moment; defenders reduce surface, assume compromise, and design for recovery.
- All practical work in this course is authorized work, on your own or instructor-provided systems.

## Next lesson

[CYB-102 · CIA Triad, Security Principles and Risk](../02-cia-triad-principles-risk/index.md) — the
vocabulary you will use to describe every finding, control, and trade-off for the rest of the course.

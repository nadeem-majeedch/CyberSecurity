# Cyber Security — A Guided Self-Study Program

A complete, safety-first cybersecurity curriculum for university students and independent learners:
from first principles to a portfolio-grade capstone.

## Instructor

Engr. Dr. Muhammad Nadeem Majeed  
Professor  
Department of Data Science (PUCIT)  
University of the Punjab, Lahore, Pakistan.

[About the instructor](instructor/index.md) — role in the course and answers to common student questions.

!!! note "Publication status"
    Levels 1 and 4 are **complete** (22 modules, 33 labs). Levels 2, 3 and 5 each have **six of their eight**
    modules published — 18, 17 and 18 labs respectively. In total: 40 modules, 86 labs. Assessment is published
    for every level: 200 keyed questions, five integrated assessments and six capstone briefs. The six unwritten
    modules have no page, so nothing in the navigation looks available before it is.

---

## What cybersecurity actually is

Cybersecurity is the practice of keeping computer systems and the information in them **available,
uncorrupted, and confidential** — while still letting people use them. It is not a single skill and
not a single tool. It is a set of engineering judgements about risk:

- **What are we protecting?** Assets: data, accounts, services, reputations, physical processes.
- **What could go wrong?** Threats and vulnerabilities: mistakes, misconfigurations, malicious actors,
  design flaws, supply chains.
- **What do we do about it?** Controls: prevention, detection, response, and recovery — chosen because
  they reduce risk enough to justify their cost and friction.

Professionals work on both sides of that judgement. **Defensive** work hardens systems, watches for
what slips through, and responds when something breaks. **Offensive** work — authorized penetration
testing, red teaming — finds weaknesses before someone else does, and exists to make defence better.
This course teaches both, defender-first, and it teaches the part most courses skip: **explaining
what you found and why it matters.**

---

## What this course covers

Five levels, each building on the last, ending in a capstone project. Roughly **400 guided hours published**, or
about 480 with the planned modules; the compressed fast track is about 150 hours.

| Level | Theme | You finish able to | Hours |
| --- | --- | --- | --- |
| [1 — Foundations](levels/level-1.md) | Security concepts, ethics and law, computing, networking, Linux, Windows, virtualization | Build and reset an isolated lab; explain how a request reaches a server; administer both major operating systems | ~52 |
| [2 — Tooling and Lab Craft](levels/level-2.md) | Command line, scripting, reconnaissance, packet analysis, SSH, host assessment | Operate tools deliberately, document evidence, and produce defensible findings | ~90 |
| [3 — Applications, Cryptography and Identity](levels/level-3.md) | Web vulnerabilities, access control, secure coding, APIs | Identify a flaw class, reproduce it locally, explain the root cause, prescribe and verify the fix | ~68 |
| [4 — Defensive Operations](levels/level-4.md) | Hardening, logging, detection engineering, SIEM, threat intelligence, forensics, incident response | Harden against a baseline, write detections that work, investigate and report an incident | ~86 |
| [5 — Advanced Practice](levels/level-5.md) | Assessment methodology, Active Directory, cloud, sandboxed malware analysis, automation, threat hunting | Plan an engagement, work in AD and cloud, hunt with hypotheses, automate safely | ~70 |
| [Capstone](projects/index.md) | Six briefs: network assessment, web application security, SOC investigation, Linux hardening, threat detection, security automation | Deliver and defend a complete piece of professional work | ~48 |

The full module catalogue, prerequisites, study plans, and assessment design are in the
[course roadmap](curriculum/roadmap.md).

**What the course does not cover:** hardware and embedded security, ICS/SCADA, mobile application
security, and large-scale adversary emulation. These are named as exclusions so you know the
boundaries rather than discovering them later.

---

## What you need

| Requirement | Minimum | Recommended |
| --- | --- | --- |
| RAM | 8 GB (slow with two VMs) | 16 GB |
| Free disk | 60 GB | 100 GB |
| CPU | 64-bit with virtualization enabled in firmware | 4 cores |
| Software | Free only: a hypervisor (VirtualBox or VMware Player), Ubuntu Server, a Windows evaluation VM, DVWA or OWASP Juice Shop, Python 3 | — |
| Prior knowledge | Comfort using a computer and following technical instructions | Basic programming helps from Level 2 |

No paid tools, subscriptions, cloud accounts or textbooks are required at any level: Level 5's cloud labs use
local emulation. Full detail, including optional software: [Prerequisites and Setup](start-here/prerequisites.md).

---

## How you progress

```
Level 1 ──▶ Level 2 ──┬──▶ Level 3 ──┐
                      └──▶ Level 4 ──┴──▶ Level 5 ──▶ Capstone
```

Levels 3 and 4 can be taken in either order after Level 2 — Level 3 gives you the web and identity
knowledge that Level 4 assumes when reading logs. Everything else is sequential, and each level has
an assessment before the next one makes sense.

At every stage the rhythm is the same: **read → practise in an isolated lab → check your understanding
→ write down what you did.** Reporting is the deliverable, not an afterthought.

- Recommended sequence and time plans: [Learning Sequence](start-here/learning-sequence.md)
- How to study effectively: [How to Study](start-here/how-to-study.md)
- How you will be assessed: [Assessment Guide](start-here/assessment-guide.md)

---

## How you build a safe lab

Every practical exercise in this course runs inside **your own isolated environment**: virtual
machines on a host-only network, deliberately vulnerable applications bound to `localhost`, or a lab
range provided by the instructor. Nothing in this course asks you to touch a system you do not own.

That is not a formality. Running the same commands against a system you do not control is a criminal
offence in most jurisdictions, including under Pakistan's PECA 2016 — and "I was studying" is not a
defence.

Start here, before your first lab:

1. [Lab Safety Guide](start-here/lab-safety.md) — how to build and verify an isolated lab
2. [Safety Policy](policies/safety-policy.md) — the binding rules, and what is prohibited

---

## Where to start right now

| If you are… | Begin with |
| --- | --- |
| New to security entirely | [Start Here](start-here/index.md) → Level 1 overview → Prerequisites |
| Deciding whether this course fits you | [Full roadmap](curriculum/roadmap.md) and the [level overviews](levels/index.md) |
| Ready to build a lab | [Prerequisites and Setup](start-here/prerequisites.md), then the [Lab Safety Guide](start-here/lab-safety.md) |
| Want to check your understanding | [Assessments](assessments/index.md) — 200 questions with explained answer keys |
| Looking for the capstone | [Project Guide](start-here/project-guide.md) → [Six Briefs](projects/index.md) |
| An instructor or reviewer | [Maintainer documentation](maintainer/index.md) |

---

## About the site

This site is a static learning resource: no accounts, no analytics, no tracking, and no data
collection. There is no certificate unless the instructor establishes one — see
[the roadmap](curriculum/roadmap.md#16-open-decisions-for-the-instructor).

Build and deployment details are deliberately kept out of the student-facing pages; they live in the
[maintainer documentation](maintainer/index.md).

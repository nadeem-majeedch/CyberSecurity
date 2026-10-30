# Levels Overview

The course is five levels plus a capstone. Each level is a coherent chunk of capability — roughly one
semester of part-time study — and ends with an assessment before the next one begins.

```
Level 1 ──▶ Level 2 ──┬──▶ Level 3 ──┐
                      └──▶ Level 4 ──┴──▶ Level 5 ──▶ Capstone
```

---

## The five levels

| Level | Theme | The shift it makes | Hours | Status |
| --- | --- | --- | --- | --- |
| [1 — Foundations](level-1.md) | Security concepts, ethics, computing, networking, Linux, Windows, virtualization, cryptography basics | From "user of computers" to "administrator who can explain what is happening" | ~52 | **Published** — 15 modules, 11 labs |
| [2 — Tooling and Lab Craft](level-2.md) | Command line, Python, reconnaissance, packet analysis, vulnerability assessment | From following instructions to operating tools deliberately and documenting evidence | ~90 | **Published** — 6 modules, 18 labs |
| [3 — Applications, Cryptography and Identity](level-3.md) | Web vulnerabilities, applied crypto, IAM, secure coding, APIs | From "it is broken" to "here is the class of flaw, the root cause, and the fix" | ~68 published | **Partially published** — 6 of 8 modules, 17 labs |
| [4 — Defensive Operations](level-4.md) | Hardening, logging, detection engineering, SIEM, network defence, forensics, incident response | From reacting to operating: baseline, detect, triage, investigate, respond | ~86 | **Published** — 7 modules, 22 labs |
| [5 — Advanced Practice](level-5.md) | Assessment methodology, Active Directory, cloud, threat hunting, malware analysis, automation | From competent to professional depth in the hardest environments | ~70 | **Published** — 6 modules, 18 labs |
| [Capstone](../projects/index.md) | Six briefs: network assessment, web application security, SOC investigation, Linux hardening, threat detection, security automation | From coursework to a portfolio artefact you can defend | ~48 | **Published** — 6 briefs, 100 marks each |

---

## What each level assumes

| Level | Assumes you can already… | Do not start it if… |
| --- | --- | --- |
| 1 | Use a computer and follow technical instructions | You cannot install software or use a terminal at all |
| 2 | Build an isolated VM lab; use Linux and Windows basics | Your lab is not stable and isolated |
| 3 | Use a proxy, read HTTP, run a script you wrote | You cannot explain what a TCP connection is |
| 4 | Read a capture and write a findings table | You have never documented evidence |
| 5 | Reason about detection and risk; work in a team setting | You cannot yet justify your methodology in writing |

The prerequisites for each module are also listed in the [roadmap](../curriculum/roadmap.md).

---

## Time and pacing

| Plan | Duration | Weekly load |
| --- | --- | --- |
| Standard (two semesters) | 32 weeks | 12–14 h |
| Extended (recommended for working learners) | 12–18 months | 6–8 h |
| Fast track | ~10 weeks | 15 h |

Details, including which modules the fast track includes and what it omits:
[Learning Sequence](../start-here/learning-sequence.md).

---

## Publication status

Level 1 is **published** (fifteen modules, eleven labs), Level 2 **published** (six modules, eighteen labs),
Level 4 **published** (seven modules, twenty-two labs), and Level 5 **published** (six modules, eighteen labs) with
its capstone briefs. Level 3 is **partially published**: six of its eight modules are complete with seventeen labs.
Applied cryptography (CYB-305) and identity/federation (CYB-306) remain planned at Level 3, and professional
reporting (CYB-507) at Level 5.

Assessment is published for every level: **200 quiz items** with explained answer keys, five **integrated level
assessments** (practical plus written justification), and six **capstone briefs** with 100-mark rubrics.
See [Assessments](../assessments/index.md).

One Level 5 module is not written: professional reporting (CYB-507). Two Level 3 modules remain planned (applied
cryptography and identity/federation). Those gaps are listed in the
[progress report](../maintainer/progress-report.md) rather than hidden.

Every published lab carries scope, expected output, verification and teardown steps. Nothing is listed as
available before it exists.

This is stated plainly because the alternative — publishing empty module pages — would waste your time
and misrepresent the course.

---

## Related

- [Full Roadmap](../curriculum/roadmap.md) — every module, prerequisite, and hour
- [Learning Sequence](../start-here/learning-sequence.md) — the recommended order
- [Prerequisites and Setup](../start-here/prerequisites.md) — what to have ready

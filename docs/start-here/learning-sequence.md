# Learning Sequence

The course is ordered, not just categorised. This page explains the path, the plans for different time
budgets, and what to do when you skip, pause, or return.

---

## The dependency graph

```
CYB-100  Foundations
    │      security concepts · ethics · computing · networking · Linux · Windows · virtualization
    ▼
CYB-200  Tooling and Lab Craft
    │      command line · Python · reconnaissance · packet analysis · vulnerability assessment
    ├──────────────────────────────┐
    ▼                              ▼
CYB-300  Applications,        CYB-400  Defensive Operations
         Cryptography,                  hardening · logging · detection · SIEM
         Identity                       threat intel · forensics · incident response
    └──────────────┬───────────────┘
                   ▼
CYB-500  Advanced Practice
         assessment methodology · Active Directory · cloud · hunting · malware analysis · automation
                   ▼
CYB-600  Capstone
```

**Why 3 and 4 are siblings:** both need the tooling fluency from Level 2, but they need different
things from each other. Level 3 teaches how applications fail; Level 4 teaches how to see failure in
logs. The recommended order is 3 then 4, because detection engineering reads web and authentication
telemetry constantly — but a learner concentrating on defensive operations may take 4 first and
return to 3.

**Why everything else is sequential:** each level's labs assume the environment, vocabulary, and habits
of the previous one. Jumping into Level 3 without Level 2 produces commands that run but results that
cannot be interpreted.

---

## Do not skip the gates

Each level ends with an assessment, and each module with a knowledge check and a lab. They are not
bureaucracy; they are the feedback loop that tells you whether the previous weeks worked.

A practical rule: **if you cannot pass the level assessment, the next level will feel like memorising
someone else's vocabulary** — which is exactly the failure mode this course is designed to avoid.

Exception: experienced practitioners may attempt level assessments directly (see the
[assessment format](../policies/assessment-format.md)). The capstone is still required if a certificate
of completion is ever issued.

---

## Study plans

### Standard — two semesters (32 weeks, 12–14 h/week)

| Weeks | Content | Milestone |
| --- | --- | --- |
| 1–7 | Level 1 | Lab built and verified; readiness assessment |
| 8–14 | Level 2 | Replayable lab notebooks; level assessment |
| 15–21 | Level 3 | Vulnerable-app assessment and fix report |
| 22–28 | Level 4 | Detection lab, incident report |
| 29–32 | Level 5 + capstone start | Engagement or hunt report |

This is the pacing the material is written for: one module per week at Level 1, slightly slower later.

### Extended — self-paced (12–18 months, 6–8 h/week)

The recommended plan for working learners. One module every two weeks. Levels may be paused between
modules — pause at a module boundary, never mid-module, and always finish the lab write-up before
stopping.

| Level | Realistic duration |
| --- | --- |
| 1 | 5–7 weeks |
| 2 | 6–8 weeks |
| 3 | 7–9 weeks |
| 4 | 9–11 weeks |
| 5 + capstone | 12–16 weeks |

### Fast track (~150 hours)

For learners who already have IT or development experience and need the core rather than the whole
program:

| Level | Modules | Hours |
| --- | --- | --- |
| 1 | CYB-102, 103, 105, 106, 108 | ~43 |
| 2 | CYB-202, 203, 204, 205 | ~48 |
| 3 | CYB-301, 302, 303 | ~34 |
| 4 | CYB-401, 404, 405 | ~34 |

The fast track is **not a substitute for the full program**. It omits Windows administration, applied
cryptography, IAM, threat intelligence, forensics, and incident response — all of which appear in
professional job descriptions.

### Weekly intensive (10 weeks, 15 h/week)

Only realistic with no other commitments. Risky: the labs need thinking time, and cramming evidence
collection produces reports that miss the point. If you choose it, protect the lab sessions and cut
reading time instead.

---

## Module-level order inside a level

Within a module, the order is fixed:

1. **Overview page** — outcomes, prerequisites, time estimate, lab link.
2. **Lessons** in numeric order. Each ends with a knowledge check.
3. **Lab** — do it after the lessons, not before.
4. **Write-up** — against the rubric, before reading any model answer.
5. **Review** — revisit the knowledge check a week later. Anything you miss, re-read that section.

The one-page **review questions** at the end of each module exist for that spacing step; they are
deliberately answerable only from memory.

---

## Pausing and resuming

**Pause at a module boundary.** Reverting a VM mid-lab is fine; abandoning a half-written report is not.

When you return after more than two weeks:

1. Re-read your last module's notes, especially the "questions" file.
2. Rerun one command from the last lab to confirm the environment still works (VMs age: snapshots
   corrupt, packages expire, certificates fail).
3. Retake the last knowledge check. Below 70%? Re-read that module's lessons before moving on.
4. Continue with the next module. Do not restart the level.

---

## What to do if you are ahead

- Do the **stretch tasks** listed at the end of labs.
- Read the primary sources linked in each lesson rather than only the lesson.
- Write a short explainer of the module for a peer — teaching exposes gaps faster than reading.
- Start the capstone literature review early; see the [Project Guide](project-guide.md).

## What to do if you are behind

- Cut optional reading first, never the lab.
- Reduce a module to: lesson skim → lab → write-up → knowledge check. That is the irreducible core.
- Keep the weekly slot even if it is only 45 minutes; continuity beats intensity.
- Do not skip the ethics and reporting content to save time. It is assessed, and it is the part
  employers actually notice.

---

## Related

- [Full roadmap](../curriculum/roadmap.md) — module catalogue, prerequisites, hours
- [How to Study](how-to-study.md) — the weekly rhythm this plan assumes
- [Assessment Guide](assessment-guide.md) — how each gate works

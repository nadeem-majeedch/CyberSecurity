# Practical Lab Template

**Applies to:** every practical exercise (`kind: lab`) in this course.
**Status:** mandatory from Phase 2.

A lab is a procedure a learner can complete alone, safely, with a verifiable result. It is written
for someone who has read the lesson but has never used the tool. If a step can be misread, it will
be misread — write for that learner.

---

## 1. Hard requirements

1. **Explicit scope.** Every lab names its in-scope targets and its out-of-scope targets. "The lab"
   is never left implicit.
2. **Allowlisted target types only:** `localhost`, the learner's own isolated lab subnet
   (documentation ranges such as `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, or a private
   range assigned in the lab spec), intentionally vulnerable applications running locally, or an
   instructor-provided isolated range.
3. **Reproducible environment.** OS, tool versions, VM specs, network mode, and starting snapshot
   are stated. No "install the latest".
4. **A verification step.** The learner can prove the lab worked, without the instructor.
5. **A reset path.** Steps to restore the starting state, and what to destroy afterwards.
6. **A rubric.** Four criteria, five bands, aligned to the learning outcomes.
7. **No answer key.** Flags, model exploits, and expected final values are not published.

---

## 2. Required structure

| # | Section | Content |
| --- | --- | --- |
| 1 | Front matter | `kind: lab`, `safety:` classification, `lab_ids`, versions, review date |
| 2 | Header block | Lab ID, module, time, difficulty, safety badge, prerequisite snapshot |
| 3 | Objective | One sentence: what will exist at the end |
| 4 | Authorization and scope | Scope table (in/out), authorization artefact reference, what to do if unsure |
| 5 | Threat model | What is being simulated, what is deliberately vulnerable, what is *not* real |
| 6 | Environment | VM list with role/IP/resources, network diagram, software versions, expected snapshots |
| 7 | Before you start | Snapshot instruction, isolation verification, stop conditions |
| 8 | Procedure | Numbered steps, each with a purpose, a command, and expected output |
| 9 | Evidence collection | Exactly what to capture (files, hashes, timestamps, screenshots) and where to store it |
| 10 | Verification | Self-check list that proves completion |
| 11 | Teardown and reset | Revert snapshot, remove artefacts, confirm containment |
| 12 | Reflection questions | 3–5 questions requiring interpretation, not recall |
| 13 | Rubric | Criteria, bands, and what distinguishes a 3 from a 5 |
| 14 | Troubleshooting | Symptom → likely cause → fix, at least four rows |
| 15 | References | Tool documentation with versions and access dates |

---

## 3. Safety block (mandatory in every lab)

Each lab opens with the following block, filled in and never abbreviated:

```markdown
!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `192.0.2.10` (lab VM `target-01`), `localhost:8080` (DVWA).
    **Targets you must not use:** any host outside your own isolated lab network, any address
    belonging to your university, employer, ISP, or another person, and any public system.

    This lab is authorized only because you own or have been given the environment. The same
    commands run anywhere else may be a criminal offence. If you are unsure whether a target is
    in scope, **stop and ask** — do not test it to find out.

    Full rules: [Safety Policy](../policies/safety-policy.md).
```

The lab must also state the isolation check (for example, "confirm `ping 8.8.8.8` fails from the
lab VM") before any enumeration step, so that a misconfigured network adapter cannot silently
turn a lab exercise into internet-wide scanning.

---

## 4. Lab skeleton (copy this)

````markdown
---
title: "LAB-105-01 · Subnetting drills"
description: "Convert CIDR notation to host ranges and verify with local tooling."
module_code: CYB-105
level: 1
kind: lab
prerequisites: [CYB-105]
estimated_minutes: 45
difficulty: beginner
safety: local-only
lab_ids: [LAB-105-01]
version: 0.1.0
last_reviewed: 2026-10-28
reviewers: []
status: draft
tags: [networking, subnetting]
---

# LAB-105-01 · Subnetting drills

**Module:** CYB-105 · **Time:** 45 minutes · **Safety:** local-only · **Snapshot:** `clean-l1`

!!! warning "Authorized scope — read before you begin"
    …

## Objective

Given five network briefs, produce correct CIDR conversions and verify each with `ipcalc`,
recording your reasoning for two of them.

## Threat model

No offensive activity. This lab builds the addressing literacy required before any host discovery
exercise in Level 2.

## Environment

| Host | Role | Address | Resources |
| --- | --- | --- | --- |
| `lab-ubuntu` | Learner workstation | 192.0.2.20/24 | 2 vCPU, 4 GB, host-only adapter |
| — | No target host required | — | — |

Software: Ubuntu 22.04.3, `ipcalc` 0.42.

## Before you start

1. Take a snapshot named `pre-lab-105-01`.
2. Confirm isolation: `ping -c1 -W1 8.8.8.8` must fail.

## Procedure

### Step 1 — Convert the first brief

Purpose: practise the /26 boundary.

```bash
ipcalc 192.0.2.0/26
```

Expected output (abridged):

```text
Network:   192.0.2.0/26
HostMin:   192.0.2.1
HostMax:   192.0.2.62
Broadcast: 192.0.2.63
```

## Evidence to collect

- `subnetting-worksheet.md` with all five answers and reasoning.
- Terminal transcript of the five `ipcalc` runs.

## Verification

- [ ] All five conversions match the expected ranges in your worksheet.
- [ ] Two answers include written reasoning.
- [ ] Isolation check failed as required.

## Teardown and reset

```bash
# No persistent changes were made.
```

Revert to snapshot `pre-lab-105-01` if any interface configuration was altered.

## Reflection

1. Why does a /26 have 62 usable addresses rather than 64?
2. …

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | More than two errors | One error | All correct |
| Method | Answers only | Some working shown | Clear method, edge cases noted |
| Evidence | Missing | Transcript present | Transcript plus annotated reasoning |
| Safety | Isolation unchecked | Checked | Checked and documented |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ipcalc: command not found` | Package missing | `sudo apt install ipcalc` |
| Isolation check succeeds | Bridged adapter | Switch VM to host-only, re-test |
````

---

## 5. Author verification record

Before publication, the author records in `docs/instructor/review-log.md`:

- Date and time of the verification run.
- Host OS, hypervisor version, VM images and checksums.
- Every step that failed first time and the correction made.
- Confirmation that the isolation check failed as expected.
- Confirmation that teardown returned the environment to the documented state.

A lab without a verification record is `status: draft`, regardless of how complete it looks.

---

## 6. Anti-patterns to reject at review

- Copy-paste blocks containing live public IPs, real domains, or another organisation's hostnames.
- "Now try this on any website you like."
- Undocumented destructive commands (`rm -rf`, `dd`, disk formatting) without a warning block.
- Instructions that assume internet access without saying so.
- A "solution" section that removes the learning.
- Scanning or exploitation steps with no isolation check preceding them.
- Labs that require a paid product, account, or cloud spend without an alternative.

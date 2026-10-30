# Project Guide

The capstone (CYB-508) is where the course stops being coursework and becomes evidence you can show
someone. It is a single, self-directed piece of work — chosen by you, scoped by you, defended by you.

This guide explains what counts, how to choose, and how to avoid the failure modes that produce an
unfinished project.

---

## What the capstone is

A **complete piece of professional work**: a problem, an approach, evidence, a report, and a
ten-minute defence of your conclusions. Roughly 48 hours of effort, spread over 4–6 weeks.

It is not a tutorial follow-along, not a tool demo, and not a topic summary. It must contain something
*you* decided.

---

## Routes, and the six published briefs

There are six capstone briefs, each with its own 100-mark rubric, starter data and reference solution:
network security assessment, web application security, SOC investigation, Linux hardening, threat detection and
security automation. Read them in [Capstone Projects](../projects/index.md).

They fall into four routes:

| Option | The question it answers | Typical artefact |
| --- | --- | --- |
| **A — Defensive build** | Can you build and operate something that detects and responds? | Hardened lab, three working detections, an incident-response playbook, a tabletop record, a post-incident review |
| **B — Offensive assessment** | Can you plan, execute, and report a scoped assessment? | Scope and rules of engagement, methodology log, findings with reproduction steps, risk ratings, remediation advice, retest plan |
| **C — Engineering** | Can you build a tool that solves a real problem safely? | Threat model, design, tested code, usage documentation, measured outcome |
| **D — Applied research** | Can you answer a question with evidence rather than opinion? | Research question, method, ATT&CK mapping, evidence, limitations, defensive guidance |

Choose based on the role you want next, not on what looks most impressive. A finished defensive build
beats an abandoned "full red team engagement" every time. The [six briefs](../projects/index.md) share the same
shape — problem, scope, tasks, artefacts, validation, rubric — so you can compare them before committing.

---

## Choosing and scoping

A good capstone scope has all five properties:

1. **Bounded.** One question, one environment, one audience. "Security of the web" is not a scope.
2. **Verifiable.** Someone else can check whether you achieved it.
3. **Safe.** Everything happens in your lab, in a sandbox account, or on an instructor-provided range.
4. **Documented as you go.** The report is assembled from notes, not reconstructed afterwards.
5. **Defensible.** You can explain every decision, including the ones you would change.

Write a **one-page brief** before you build anything:

```text
Title:
Option:            A / B / C / D
Problem:           one paragraph — what gap or question
Scope:             in scope / out of scope (be explicit about targets)
Approach:          4–6 steps
Artefacts:         what will exist at the end
Evidence:          what proves it worked
Success criteria:  3 measurable statements
Risks:             what could go wrong, and the mitigation
Ethics:            why this is authorized and safe
Timeline:          milestones against 4–6 weeks
```

If the brief takes more than a page, the scope is too large.

---

## Suggested timeline

| Week | Milestone | Deliverable |
| --- | --- | --- |
| 1 | Brief approved (instructor or self-review against the rubric) | One-page brief |
| 2 | Environment ready and verified isolated | Lab diagram, isolation evidence |
| 3 | Core work: build, assess, or hunt | Raw evidence, work log |
| 4 | Analysis: what the evidence shows | Findings or detection results |
| 5 | Report: technical annex and executive summary | Draft report |
| 6 | Defence: 10-minute presentation, questions | Final report + slides |

Front-load the environment. Most stalled capstones die in week 3 because the lab was never stable.

---

## Deliverables

Every capstone, regardless of option, includes:

1. **Report** (8–15 pages): problem, scope, method, results, analysis, limitations, recommendations.
2. **Technical annex**: commands, configurations, rules, code, or captures that support the report.
3. **Evidence log**: dated, reproducible, with environment details.
4. **Ethics statement**: what was authorized, what was in scope, confirmation nothing outside it was
   touched.
5. **Defence**: 10 minutes plus questions — the test of whether you understand your own work.

### What "good" looks like

| Weak | Strong |
| --- | --- |
| "I ran Nmap and found open ports" | "Service inventory on the lab segment showed three unexpected listeners; two were default installs with known exposure, one was a misconfigured management interface" |
| "The detection worked" | "The Sigma rule fired on 4 of 5 simulated technique executions and produced 2 false positives in 24 hours of baseline traffic; the tuning change and its trade-off are documented" |
| "The system is now secure" | "Six controls applied against the CIS baseline; two could not be applied because of a lab constraint, which is recorded with residual risk" |

Notice what the strong examples share: **numbers, trade-offs, and honest limits**.

---

## Common failure modes

- **Scope creep.** Adding "one more target" until nothing is finished. Freeze the scope at week 1.
- **Tool-first thinking.** Starting with a tool and looking for a use, instead of a problem and choosing
  a tool.
- **No baseline.** Claiming improvement without measuring before and after.
- **Report written from memory** in the final two days, producing vague findings.
- **Ignoring the audience.** A report only a specialist can read fails the communication criterion.
- **Unverified environment.** Building on a lab that was never proven isolated.
- **Overclaiming.** "Critical" severity for everything destroys credibility; calibrate with CVSS or a
  stated rationale.

---

## Assessment

The capstone is marked on five dimensions — problem definition and scope, technical execution, evidence
and analysis, reporting and communication, and ethics and professionalism. Pass requires 60 overall
with no dimension below 50 and full marks on ethics. Distinction requires 85 overall.

Full descriptors: [capstone rubric](../policies/assessment-format.md#6-capstone-rubric).

---

## Before you start

- [ ] You have completed Levels 1–5, or the fast track plus the modules your option depends on.
- [ ] Your lab is stable, snapshotted, and verified isolated.
- [ ] Your one-page brief is written and reviewed.
- [ ] You know which audience the report is for.
- [ ] You have read the [Safety Policy](../policies/safety-policy.md) again — capstones are where scope
      discipline matters most.

---

## Related

- [Project options and requirements](../projects/index.md) — the formal briefs
- [Assessment Guide](assessment-guide.md) — how marking works
- [Level 5 — Advanced Practice](../levels/level-5.md) — the modules the capstone builds on

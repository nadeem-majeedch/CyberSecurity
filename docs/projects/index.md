---
title: "Capstone Projects — Six Briefs"
description: "Six complete capstone briefs, each with a 100-mark rubric, starter data, submission checklist and a clearly marked reference solution."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-501]
estimated_minutes: 1200
difficulty: advanced
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, projects, assessment, portfolio]
---

# Capstone Projects

The capstone is the final requirement: one substantial piece of security work, delivered and defended. This
section holds six complete briefs. Each is worth **100 marks**, each has starter files, and each has a reference
solution you should open only after submitting your own attempt.

Choose **one**. Six good projects finished beat six ambitious projects started.

| # | Brief | Route | Hours | Starter data |
| --- | --- | --- | --- | --- |
| 1 | [Network Security Assessment](01-network-security-assessment.md) | Defensive/offensive assessment | 24 | Asset register |
| 2 | [Web Application Security](02-web-application-security.md) | Offensive + remediation | 24 | Findings register, sample app |
| 3 | [SOC Investigation](03-soc-investigation.md) | Defensive investigation | 20 | 26-event synthetic dataset |
| 4 | [Linux Hardening](04-linux-hardening.md) | Engineering | 16 | Hardening checklist |
| 5 | [Threat Detection](05-threat-detection.md) | Detection engineering | 20 | 43-event labelled corpus |
| 6 | [Security Automation](06-security-automation.md) | Engineering | 24 | Mixed-format log, IOC list |

Starter files: [download list](starter-files.md) · Reference solutions: [read after attempting](reference-solutions.md)

---

## What every capstone must contain

| Requirement | Why |
| --- | --- |
| A one-page brief, written before any work | Prevents scope drift; makes the question explicit |
| A bounded scope with named in- and out-of-scope targets | Safety, and the ability to say what you did not claim |
| An isolated environment, verified | The work must be reproducible without touching anyone else's systems |
| Dated, reproducible evidence | Notes, commands, outputs, hashes, configuration snapshots |
| A report for two audiences | Technical annex plus a plain-language summary |
| An ethics statement | What was authorised, what was in scope, confirmation of restraint |
| A 10-minute defence | The test of whether you understand your own work |

If you are self-paced, the defence is a recorded walkthrough plus a written answer to the questions in the
[Project Guide](../start-here/project-guide.md#deliverables).

---

## The rules that apply to all six

1. **Local only.** Your lab, your VM, the supplied synthetic data. A public system is never an acceptable target,
   whatever the intent.
2. **No live malware.** Analyses use the supplied inert artefacts or documentation samples. Nothing functional is
   distributed or executed.
3. **No real data.** Every dataset here is synthetic and labelled as such. Do not substitute real logs, real
   credentials, or real personal data.
4. **Preserve the evidence.** Hash before you analyse, work on copies, keep a custody record where relevant.
5. **State your limits.** A report that claims more than the evidence supports loses marks on the criterion it
   was trying to win.

---

## How the marks work

Each brief carries its own 100-mark rubric, split across six or seven criteria. In every rubric:

- **50 marks or more** come from work that can be checked: artefacts, tests, evidence, code.
- **No criterion below 50%** is required for a pass.
- **Ethics and scope is a gate.** A scope violation, a public target, or destructive action voids the submission
  regardless of technical quality.

Bands: below 60 not yet · 60–69 pass · 70–84 merit · 85+ distinction. The capstone rubric in
[How Assessment Works §6](../policies/assessment-format.md#6-capstone-rubric) maps these criteria to the five
program-level dimensions.

---

## Choosing a brief

| If you want to work in… | Choose | Because |
| --- | --- | --- |
| SOC, incident response | 3 — SOC Investigation | Timeline and report discipline are the job |
| Penetration testing, consulting | 1 or 2 | Scoping, evidence and client reporting |
| Detection engineering | 5 — Threat Detection | Rules, tests and honest coverage claims |
| Infrastructure, platform security | 4 — Linux Hardening | Baseline, deviation and verification |
| Security engineering, automation | 6 — Security Automation | Guardrails, tests and failure handling |
| Application security | 2 — Web Application Security | Finding, fixing and proving the fix |

Difficulty is comparable. The difference is which evidence you will be asked to defend.

---

## Before you start

- [ ] Levels 1–5 complete, or the modules your chosen brief depends on
- [ ] Lab built, snapshotted, and verified isolated
- [ ] One-page brief written
- [ ] Starter data downloaded and hashed
- [ ] Report template open: [Assessment Report Template](../policies/assessment-report-template.md)
- [ ] [Safety Policy](../policies/safety-policy.md) re-read

---

## Related

- [Project Guide](../start-here/project-guide.md) — scoping, timeline, failure modes
- [Capstone rubric](../policies/assessment-format.md#6-capstone-rubric) — program-level marking
- [Starter files](starter-files.md) — every dataset, with hashes
- [Reference solutions](reference-solutions.md) — measured outputs, clearly marked

---
title: "LAB-206-03 · Write the Assessment Report"
description: "Turn the Level 2 lab evidence into a professional assessment report against the course template."
module_code: CYB-206
level: 2
kind: lab
prerequisites: [CYB-206]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-206-03]
version: 1.1.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [reporting, assessment, capstone, level-2]
---

# LAB-206-03 · Write the Assessment Report

| | |
| --- | --- |
| **Level** | 2 (capstone) |
| **Time** | 4 hours |
| **Prerequisites** | LAB-206-01, LAB-206-02, LAB-204-03 |
| **Lab hosts** | `lab-ubuntu` 192.0.2.20 (assessed), `lab-kali` (analyst) |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

Your team must hand over the lab network assessment. All the testing is done: you have an inventory, a hardening
assessment, and protocol evidence. What is missing is the document. In professional work the report *is* the
deliverable — findings that are not written up clearly were, for practical purposes, not found.

This lab is the Level 2 capstone assessment, marked against the
[report rubric](../../../policies/assessment-report-template.md#marking-criteria).

## Learning objectives

1. Assemble evidence collected across several labs into one coherent narrative.
2. Write findings that a peer could verify without asking you anything.
3. Justify severity with likelihood and impact rather than assertion.
4. Order remediation by risk reduced per unit of effort.
5. State limitations and accepted risks honestly.

## Required tools and versions

| Tool | Purpose |
| --- | --- |
| Your artefacts from LAB-204-03, LAB-206-01, LAB-206-02 | Evidence |
| [Assessment Report Template](../../../policies/assessment-report-template.md) | Structure |
| `sha256sum` | Artefact integrity |
| Any Markdown editor | Writing |

## Setup

```bash
mkdir -p ~/lab206/03-report/artefacts && cd ~/lab206/03-report
cp ~/lab206/01-inventory/*.txt artefacts/
cp ~/lab206/02-lynis/lynis-*.txt artefacts/
cp ~/lab204/protocols/protocol-findings.md artefacts/
cp ~/lab204/protocols/*.pcap artefacts/ 2>/dev/null || true
sha256sum artefacts/* | tee artefacts/MANIFEST.sha256
```

**Expected:** a manifest listing every artefact with its hash — this becomes Appendix 9 of the report.

## Target addresses and lab topology

No new targets. This lab consolidates evidence about `lab-ubuntu` (`192.0.2.20`) collected in LAB-204-03,
LAB-206-01 and LAB-206-02, with `lab-kali` (`192.0.2.10`) as the analyst host.

## Numbered commands and actions

### Step 1 — Decide the findings before writing

Do not start with the template. Start with a table on paper:

| Candidate | Retain? | Severity | Why |
| --- | --- | --- | --- |
| SSH password auth enabled at baseline | Yes (remediated) | Medium | Closed by LAB-205-02; report as *fixed during assessment* |
| PostgreSQL on `0.0.0.0` | Yes | High | Reachable from the whole segment |
| `PASS_MAX_DAYS` unset | Justify | Low | Modern guidance favours length over rotation |
| Leftover `python3 -m http.server` on :8000 | Yes | Low | Unintended service, but no data exposed |
| Lynis: unused filesystem modules | Yes (remediated) | Low | Attack surface reduction |

Aim for **four to six findings**. More than eight usually means you are reporting hygiene items as findings.

### Step 2 — Verify every claim against the artefact

For each retained finding, re-run the command and confirm the output still matches what your notes say:

```bash
ssh lab-ubuntu 'sudo ss -tulpn | grep -E ":5432|:8000"'
ssh lab-ubuntu 'sudo sshd -T | grep -Ei "passwordauthentication|permitrootlogin"'
grep -n 'OBS-0' ~/lab206/01-inventory/10-observations.md
```

**Expected:** current output matches the recorded evidence, or you update the finding. A report citing an output
you can no longer reproduce is a defect.

### Step 3 — Write the executive summary last, in one sitting

Rules:

- No tool names, no ports, no command output.
- State the overall risk and the single most important action.
- Assume the reader has 30 seconds.

Draft it, then cut it by a third.

### Step 4 — Write each finding

Use the template's block. Two specific traps:

**Trap 1 — describing a remediation you did not perform as a recommendation.** If you fixed it during the
assessment, add `Status: Remediated during assessment` with the verification command and its output.

**Trap 2 — overstating impact.** "Any host on the lab segment could reach the database port" is a demonstrated
fact. "An attacker could exfiltrate all customer data" is not, in a lab with synthetic data. Write the first.

### Step 5 — Build the remediation plan

```markdown
| Finding | Action | Owner | Effort | Priority |
| --- | --- | --- | --- | --- |
| F-02 | Bind PostgreSQL to 127.0.0.1 | Lab owner | 15 min | 1 |
| F-03 | Install and enable auditd | Lab owner | 20 min | 2 |
| F-04 | Retire the leftover HTTP server | Lab owner | 2 min | 3 |
```

Order by **risk reduced per unit of effort**, and say that is your ordering rule. A one-line, two-minute fix that
removes reachability outranks a two-hour project.

### Step 6 — Limitations and accepted risks

Minimum four limitations, specific to what you actually did. Examples that would be true here:

- Assessment of a lab replica only; no production system was touched.
- No authenticated testing beyond the `student` account.
- No exploitation was attempted; impact beyond reachability is inferred, not demonstrated.
- Lab is isolated from the internet, so no current CVE data was consulted during testing.
- Lynis suggestions were triaged by hand; scored index is not comparable across different images.

Accepted risks: at least one declined suggestion with a compensating control.

### Step 7 — Self-review against the rubric

Before submitting, run this checklist and record the result in the report footer:

| Check | Pass |
| --- | --- |
| Every finding has evidence with a timestamp | |
| Every severity has a stated likelihood and impact | |
| Every remediation is a specific, testable change | |
| No placeholder brackets remain | |
| No finding claims impact that was not demonstrated | |
| Limitations section names what was *not* tested | |
| Artefact manifest included | |
| Report is under 8 pages | |

## Evidence to collect

`assessment-report.md`, `artefacts/` with `MANIFEST.sha256`, and the self-review table.

## Verification criteria

- [ ] Four to six findings, each with all required fields.
- [ ] Every cited command re-run and confirmed before submission.
- [ ] Executive summary free of tool names and jargon.
- [ ] Severity justified, not asserted.
- [ ] Remediation ordered by risk reduced per unit of effort, with the rule stated.
- [ ] At least four specific limitations.
- [ ] At least one accepted risk with a compensating control.
- [ ] Artefact manifest with hashes included.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Report is 20 pages | Pasting full command output | Truncate to the lines that prove the point |
| Findings feel thin | Observations, not findings | Add significance and impact to each |
| Everything is "High" | Severity used as emphasis | Re-derive from likelihood × impact |
| Cannot reproduce an output | Environment drifted | Re-run, update the finding, note the drift |
| Summary reads like a list | Written first | Write it last, from the finished findings |

## Cleanup and restoration

```bash
# Keep the report and artefacts for marking.
# Delete raw pcaps if they contain payloads you no longer need.
rm -f artefacts/*.pcap
sha256sum artefacts/* > artefacts/MANIFEST.sha256
```

## Questions and extension challenges

1. Which finding would you fix first, and does your remediation plan agree?
2. Which finding is most likely to be disputed by the system owner, and how would you defend it?
3. Rewrite your strongest finding for a non-technical executive in three sentences.
4. Add a finding you *decided not to report* and explain the decision in the accepted-risks section.
5. What would you need to test to raise your confidence in the highest-severity finding?

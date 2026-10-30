# Level 5 — Advanced Practice

**~70 guided hours across six published modules · Prerequisite: Levels 3 and 4**

!!! note "Status: six modules and the capstone published (30 October 2026)"
    CYB-501 to CYB-506 are complete: 30 pages and 18 labs. The capstone is published as six briefs with 100-mark
    rubrics. **CYB-507 (professional reporting) is not written.** The level assessment is published as the
    [Level 5 integrated assessment](../assessments/level-5-assessment.md).

---

## What this level is about

Level 5 is where the two hardest environments in real organisations — **Active Directory** and **cloud** — are treated
seriously, alongside the skills that separate a competent analyst from a professional: scoping an engagement, analysing
hostile code without endangering anything, automating without breaking scope, and hunting with a hypothesis instead of
a hunch.

Two constraints shape every module:

- **Active Directory labs are yours, isolated, and built from a guide.** The domain is `lab.local`, the accounts are
  invented, and no lab touches an organisational domain.
- **Malware analysis uses harmless artifacts.** There is no functional malware in this course, and none should be
  obtained for it.

---

## What you will be able to do

By the end of Level 5 you can:

- Write a complete engagement package — scope, rules of engagement, plan and report skeleton — and test only what it
  authorises.
- Explain Active Directory attack paths and, more importantly, break them with controls you can verify.
- Audit identity, storage, network and container configuration in a cloud-shaped environment, and remediate it.
- Triage an unknown file statically, observe behaviour in a sandbox, and write a report with stated confidence.
- Automate a repetitive task with tests, a dry-run default and guard rails against out-of-scope action.
- Hunt with a falsifiable hypothesis and convert a result into a tested detection.
- State the limits of every claim you make.

---

## Modules

| Code | Module | Focus | Final challenge | Hrs | Status |
| --- | --- | --- | --- | --- | --- |
| [CYB-501](level-5-advanced/01-penetration-testing/index.md) | Penetration Testing and Security Assessment | Rules of engagement, reconnaissance, validation, controlled exploitation, privilege escalation, evidence, risk rating, reporting, retest | Escalate, report, remediate, retest | 12 | Published |
| [CYB-502](level-5-advanced/02-active-directory/index.md) | Active Directory Security | Domain architecture, Kerberos and NTLM, delegation, ACL paths, BloodHound, PingCastle, auditing, hardening and recovery | Detect, harden, recover | 14 | Published |
| [CYB-503](level-5-advanced/03-cloud-security/index.md) | Cloud Security | Shared responsibility, least privilege, object storage, segmentation, secrets, audit logs, misconfiguration scanning, containers | Container hardening | 11 | Published |
| [CYB-504](level-5-advanced/04-malware-analysis/index.md) | Malware Analysis and Reverse Engineering | Static triage, PE structure, strings, capability detection, sandbox design, behavioural observation, YARA | YARA classification | 11 | Published |
| [CYB-505](level-5-advanced/05-security-automation/index.md) | Security Automation | Log parsing, normalisation, offline enrichment, report merging, detection testing, guarded response automation | Guarded automation | 11 | Published |
| [CYB-506](level-5-advanced/06-threat-hunting/index.md) | Threat Hunting and Detection Engineering | Falsifiable hypotheses, data requirements, beacon analysis, ATT&CK coverage, blind spots, tuning, validation | Validate and tune | 11 | Published |
| CYB-507 | Reporting, Communication and Professional Practice | Executive vs technical writing, risk language, presenting findings, portfolio and interviews | Executive brief plus technical annex | 6 | **Not written** |
| [CYB-508](../projects/index.md) | Capstone Project and Portfolio Review | Six briefs: network assessment, web application security, SOC investigation, Linux hardening, threat detection, security automation | Capstone artefact, report and defence | 48 | **Published as six briefs** |

Two changes from the original plan, recorded here rather than in a footnote:

- **Numbering moved.** The plan had hunting as 504, malware as 505 and automation as 506. The published order is
  malware → automation → hunting, because hunting uses the querying and testing habits the other two build, and it is a
  poor first module for someone who has never parsed a log.
- **Cloud replaced LocalStack with local emulation that needs no account.** LocalStack now requires an account token to
  start, so CYB-503 uses MinIO, `moto`-free local tooling and static analysis instead. No student needs a cloud account
  or a credit card for any lab in this course.

---

## Labs

Eighteen labs, three per module. They escalate within each module and end in a challenge that combines its skills.

| Module | Labs |
| --- | --- |
| CYB-501 | [Scope, RoE and test plan](level-5-advanced/01-penetration-testing/lab-01-engagement-package.md) · [Authorized assessment](level-5-advanced/01-penetration-testing/lab-02-lab-assessment.md) · [Escalate, report, retest](level-5-advanced/01-penetration-testing/lab-03-privesc-and-report.md) |
| CYB-502 | [Build the domain](level-5-advanced/02-active-directory/lab-01-build-domain.md) · [Enumerate, map, audit](level-5-advanced/02-active-directory/lab-02-bloodhound-pingcastle.md) · [Detect, harden, recover](level-5-advanced/02-active-directory/lab-03-detect-harden-recover.md) |
| CYB-503 | [Least privilege and storage](level-5-advanced/03-cloud-security/lab-01-identity-and-storage.md) · [Misconfiguration and audit logs](level-5-advanced/03-cloud-security/lab-02-misconfiguration-and-audit.md) · [Container hardening](level-5-advanced/03-cloud-security/lab-03-container-hardening.md) |
| CYB-504 | [Static triage](level-5-advanced/04-malware-analysis/lab-01-static-triage.md) · [Sandbox and behaviour](level-5-advanced/04-malware-analysis/lab-02-sandbox-behaviour.md) · [YARA classification](level-5-advanced/04-malware-analysis/lab-03-yara-classification.md) |
| CYB-505 | [Parse and normalise](level-5-advanced/05-security-automation/lab-01-log-parsing.md) · [Enrichment and merging](level-5-advanced/05-security-automation/lab-02-enrichment.md) · [Guarded automation](level-5-advanced/05-security-automation/lab-03-guarded-automation.md) |
| CYB-506 | [Hunt a hypothesis](level-5-advanced/06-threat-hunting/lab-01-hunt-hypothesis.md) · [Coverage and blind spots](level-5-advanced/06-threat-hunting/lab-02-coverage.md) · [Validate and tune](level-5-advanced/06-threat-hunting/lab-03-validate-and-tune.md) |

Full catalogue with times and status: [Labs](../labs/index.md).

---

## How the level runs

**Lab environment.** Everything from Level 4, plus:

- an Active Directory forest (`lab.local`: one DC, one member server, one workstation) on host-only networking;
- a local object store (MinIO) and a container runtime for CYB-503 — no cloud account;
- an analysis VM with Sysmon for CYB-504, host-only, snapshot before every run.

**Cost.** Zero. Every lab runs locally. If you later repeat the cloud exercises on a real provider, set a budget alert
and tear down the same day — the labs mark which resources bill and which do not.

**Assessment.** Module rubrics are in the [assessment guide](../policies/assessment-format.md). The level's own
assessment is the [Level 5 integrated assessment](../assessments/level-5-assessment.md) — a scoped engagement or a
hunt, plus a written defence. The six capstone briefs carry 100-mark rubrics and reference solutions.

---

## What you need before starting

- Levels 3 and 4 complete, or a documented equivalent.
- 16 GB RAM recommended for the AD labs; 8 GB is enough if you run one VM at a time.
- The [Safety Policy](../policies/safety-policy.md) re-read. This level handles the most sensitive material in the
  course, and the rules do not relax because the material is interesting.

---

## Where learners get stuck

| Sticking point | Why it happens | What helps |
| --- | --- | --- |
| AD complexity | Many moving parts, little visible feedback | Build from the guide, then break it deliberately |
| Snapshot discipline | It feels slower than just continuing | Snapshot before every run; a broken domain costs an hour to rebuild |
| Confusing capability with behaviour | `capa` and scanners produce impressive output | Say "capabilities present", never "the malware did" |
| Automation enthusiasm | Scripts that act on whatever they find | Dry-run default, allowlist, protected targets, tests |
| Hunting that is really browsing | No hypothesis, no data requirement | Write both before the first query |
| Tuning away the detection | Precision improves, recall quietly collapses | Measure both; check what you excluded |
| Capstone scope creep | Ambition outruns the time | Freeze scope in week one; see the [Project Guide](../start-here/project-guide.md) |

---

## Known gaps

Stated so they are not mistaken for completeness:

1. **CYB-507 is not written.** The level ends at hunting; the professional reporting module remains a plan.
2. **The level assessment is new and unmoderated.** It is published with criteria and model answers, but no human
   reviewer has second-marked it yet.
3. **Labs are verified unevenly.** Scripts and datasets that carry the most risk of being wrong were executed and their
   outputs checked; VM-based steps are written to specification. Per-lab verification status is in the
   [progress report](../maintainer/progress-report.md).
4. **BloodHound and PingCastle versions move.** CYB-502 pins what it used and tells you to record your own.

---

## After Level 5

The [capstone](../projects/index.md) is the remaining requirement. After that, the natural next steps are
specialisation — detection engineering, application security, cloud security, incident response — certification aligned
to it, and a portfolio of work you can defend.

---

## Related

- [Full roadmap](../curriculum/roadmap.md) · [Levels overview](index.md) · [Labs](../labs/index.md)
- [Project Guide](../start-here/project-guide.md) · [Safety Policy](../policies/safety-policy.md)

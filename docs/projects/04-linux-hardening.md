---
title: "Capstone 4 — Linux Hardening"
description: "Build a measured baseline for a lab Linux host, apply a justified hardening set, verify every control by querying its state, and record the decisions you did not take."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-109, CYB-205, CYB-403]
estimated_minutes: 960
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-403-01, LAB-205-02]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, hardening, baseline, verification]
---

# Capstone 4 — Linux Hardening

**Route:** engineering · **Effort:** ~16 hours over 2 weeks · **Marks:** 100

---

## Problem statement

> A small team runs one Linux server that will soon face the internet. It was installed from a default image,
> has never been baselined, and nobody can say which controls are in place. You have a maintenance window, a
> snapshot, and a requirement not to lock anyone out.

Hardening without measurement is decoration. This capstone is marked on the **evidence that each control is
actually in effect**, and on the record of what you decided not to do.

---

## Learning outcomes

1. Establish a defensible baseline from observed state, not from a checklist alone.
2. Choose controls appropriate to the host's role, and reject the ones that do not apply.
3. Apply changes safely, with a rollback path and no loss of administrative access.
4. Verify each control by querying its state rather than trusting a wizard or a summary.
5. Record deviations and exceptions with reasons, compensating controls and review dates.
6. Quantify the change: what improved, measured before and after.
7. Report to an owner who cares about risk and downtime, not about flags.

---

## Scope and constraints

| Item | Detail |
| --- | --- |
| In scope | One lab Linux VM (Ubuntu 24.04, Debian 12, or Rocky 9), its configuration, services and local accounts |
| Out of scope | The hypervisor, other VMs, the host OS, any production system, the network beyond the lab |
| Permitted | Package installation from configured repositories, configuration changes, service restarts, snapshot reverts |
| Forbidden | Disabling auditing to make a scan pass, removing SSH access without a console path, applying controls you cannot explain |
| Downtime | Your own; the VM is yours to break, provided you can restore it |
| Data | Synthetic accounts and files only |

**Hard requirement:** console or hypervisor access must be available for the whole exercise. If your only path
into the VM is SSH, you are one configuration change away from a rebuild.

---

## Prerequisites

- [CYB-109](../levels/level-1-foundations/09-linux-command-line/index.md) — shell, permissions, services
- [CYB-205](../levels/level-2-tooling/05-ssh-secure-administration/index.md) — SSH hardening without lockout
- [CYB-403](../levels/level-4-defensive-operations/03-hardening-and-patching/index.md) — baselines and exceptions
- [LAB-403-01](../levels/level-4-defensive-operations/03-hardening-and-patching/lab-01-linux-baseline.md) — OpenSCAP practice

---

## Lab setup

1. Build a VM from a current official image; record the exact release and kernel.
2. Create a non-root administrative account with `sudo`, and an SSH key for it.
3. Install the assessment tools you will use: `lynis`, `openscap-scanner` with the appropriate SCAP Security
   Guide content, and `auditd` if you plan to include auditing.
4. Snapshot the VM as `baseline-clean`, and record the snapshot name.
5. Confirm console access works. Log in on the console once, deliberately, before changing anything.
6. Create a working directory `/root/hardening/` (or in your home) for evidence.

---

## Required tasks

| # | Task | Output |
| --- | --- | --- |
| 1 | Host profile: role, exposed services, users, data, uptime expectations | `01-profile.md` |
| 2 | Baseline: Lynis and OpenSCAP results plus manual observation of users, services, listeners, permissions | `02-baseline.md`, `evidence/baseline/` |
| 3 | Control selection: at least 12 controls from the checklist, with apply/decide/verify and a reason per row | `03-controls.csv` |
| 4 | Implementation: apply at least 8 controls, using drop-in files where possible | `04-implementation.md`, `configs/` |
| 5 | Verification: for each applied control, the command and output proving its state | `05-verification.md` |
| 6 | Lockout prevention: demonstrate you retained access after SSH changes | `06-access.md` |
| 7 | Exception register: controls not applied, with reason, compensating control, owner and review date | `07-exceptions.csv` |
| 8 | Re-assessment: re-run Lynis/OpenSCAP and compare with the baseline | `08-reassessment.md` |
| 9 | Rollback test: revert one control, verify the state changed back, then restore | `09-rollback.md` |
| 10 | Report: what changed, what it reduces, what it costs operationally, residual risk | `10-report.md` |

Minimum: one control each for patching, accounts, SSH, firewall, services, logging and filesystem permissions.

---

## Expected artefacts

```text
capstone-hardening/
├── README.md
├── 01-profile.md
├── 02-baseline.md
├── 03-controls.csv
├── 04-implementation.md
├── 05-verification.md
├── 06-access.md
├── 07-exceptions.csv
├── 08-reassessment.md
├── 09-rollback.md
├── 10-report.md
├── configs/                 # drop-in files, with the path they belong at
└── evidence/
    ├── baseline/
    ├── after/
    └── hashes.txt
```

---

## Testing and validation

| Check | Standard |
| --- | --- |
| Baseline completeness | Tool output plus manual observation; disagreements noted |
| Control justification | Each row names the risk it addresses and the host role it fits |
| Implementation safety | Changes in drop-ins where possible; original files preserved |
| Verification | Command, output and interpretation per control — not "the wizard said applied" |
| Access retention | A new SSH session succeeds after the change, from a fresh terminal |
| Re-assessment | Same tools, same profile, before/after comparison |
| Rollback | One control reverted and restored, with evidence of both states |
| Exceptions | Reason, compensating control, owner, review date — not a list of omissions |

A control marked "applied" without a verification command scores zero, even if it is genuinely in place.

---

## Security and ethical requirements

- Work only on your own lab VM. Do not harden a system you do not own, even helpfully.
- Do not disable logging, auditing, or the package manager to improve a score.
- Keep console access; do not rely on a single SSH session.
- Record every command that changes state, so the work is reversible.
- Never paste real credentials, keys or internal hostnames into artefacts you publish.
- If a control would break the host's stated role, record it as an exception rather than applying it blindly.

---

## Submission checklist

- [ ] Host profile with role and exposure
- [ ] Baseline from two tools plus manual checks
- [ ] Twelve or more controls considered, with reasons
- [ ] Eight or more applied, with configuration files
- [ ] Verification command and output for every applied control
- [ ] Access retained, demonstrated from a new session
- [ ] Exception register with owners and review dates
- [ ] Re-assessment comparison with the baseline
- [ ] Rollback demonstrated
- [ ] Report with operational cost and residual risk

---

## Rubric — 100 marks

| Criterion | Marks | What earns full marks |
| --- | --- | --- |
| Baseline and measurement | 15 | Two tools plus manual checks; discrepancies explained; evidence timestamped |
| Control selection and justification | 15 | Role-appropriate; 12 or more considered; rejections reasoned |
| Implementation | 20 | Eight or more applied correctly; drop-ins used; originals preserved |
| Verification | 20 | Every control verified by querying state; interpretation correct |
| Exception register | 10 | Reasons, compensating controls, owners, review dates |
| Reporting | 10 | Operational impact stated; residual risk; readable by an owner |
| Safety and reversibility | 10 | Console path maintained; rollback tested; no lockout |

Bands: [How Assessment Works](../policies/assessment-format.md#6-capstone-rubric).

---

## Starter files

| File | Use |
| --- | --- |
| [`hardening-checklist.csv`](../assets/assessments/starters/hardening-checklist.csv) | Twelve candidate controls with CIS references and decision columns |
| [Assessment Report Template](../policies/assessment-report-template.md) | Report structure |
| [CYB-403 lesson](../levels/level-4-defensive-operations/03-hardening-and-patching/01-baselines-and-patch-priority.md) | Baseline and prioritisation method |

The [reference solution](reference-solutions.md#capstone-4-linux-hardening) shows a complete control table with
verification commands and two justified exceptions.

---

## Suggested extensions

- Convert the applied controls into an Ansible role and prove idempotency by running it twice.
- Add `auditd` rules for privilege escalation and file integrity, and test them with harmless actions.
- Build a CIS profile with tailoring, and report the delta from the unmodified profile.
- Measure the operational cost: what now requires a change request, and what broke during testing.

---

## Common pitfalls

- **Scanner-driven hardening.** Applying every failed rule, including ones for services the host does not run.
- **Trusting the tool's summary.** `ufw status` is not a packet test; verify with an actual probe.
- **No console.** The classic rebuild story.
- **Silent exceptions.** A control not applied and not recorded reads as an oversight.
- **Score chasing.** Disabling auditd to improve a hardening index is the opposite of the task.
- **No before/after.** "It is hardened now" without the baseline cannot be assessed.

---

## Related

- [Capstone overview](index.md) · [Project Guide](../start-here/project-guide.md)
- [CYB-403 · Hardening, Baselines and Vulnerability Management](../levels/level-4-defensive-operations/03-hardening-and-patching/index.md)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)

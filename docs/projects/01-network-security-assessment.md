---
title: "Capstone 1 — Network Security Assessment"
description: "Assess an isolated five-host lab network, validate every finding, rate it by risk, and deliver a client-style report with remediation and a retest plan."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-203, CYB-204, CYB-206, CYB-403]
estimated_minutes: 1440
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-203-02, LAB-206-03]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, network, assessment, reporting]
---

# Capstone 1 — Network Security Assessment

**Route:** assessment · **Effort:** ~24 hours over 3–4 weeks · **Marks:** 100

---

## Problem statement

> A five-host training network is about to be connected to a shared lab segment. Before that happens, its owner
> needs to know what an attacker on that segment could reach, what is misconfigured, and what to fix first. You
> have written authorisation for that network, and nothing else.

Your job is not to find the most vulnerabilities. It is to produce a **defensible picture** of the network's
exposure: what is there, what is reachable, what is actually wrong, and what the owner should do about it.

---

## Learning outcomes

By completing this capstone you can:

1. Write a scope and rules-of-engagement document that a reviewer would accept.
2. Inventory a network from discovery and enumeration, separating confirmed services from scanner claims.
3. Validate a finding with an independent method before rating it.
4. Rate findings by technical severity and business context, and defend the difference.
5. Write remediation that is specific, ordered and verifiable.
6. Retest a fix and state what the retest proves and does not prove.
7. Handle evidence so that a third party could replay the assessment.

---

## Scope and constraints

| Item | Detail |
| --- | --- |
| In scope | The five lab hosts in `10.10.10.0/24` listed in the [asset register](../assets/assessments/starters/asset-register.csv) |
| Out of scope | The hypervisor host, `10.10.10.0/24` devices not on the register, any other subnet, the internet |
| Permitted | Host discovery, TCP/UDP port scanning at a polite rate, service probing, configuration review with the credentials you were given |
| Forbidden | Denial of service, exploitation beyond a single non-destructive proof, persistence, password attacks beyond three attempts, data modification |
| Window | Stated in your scope document; record actual start and end times in UTC |
| Data handling | Evidence stored locally, hashed, synthetic only; delete at the end of the project or keep in your portfolio with identifiers removed |

**Deliberate constraint:** you may scan only addresses on the register. If discovery returns an unexpected host,
record it, do not test it, and report it.

---

## Prerequisites

- [CYB-203](../levels/level-2-tooling/03-host-discovery-and-enumeration/index.md) — discovery and enumeration
- [CYB-204](../levels/level-2-tooling/04-packet-capture-and-analysis/index.md) — capture and evidence handling
- [CYB-206](../levels/level-2-tooling/06-host-inspection-and-hardening/index.md) — host assessment and reporting
- [CYB-403](../levels/level-4-defensive-operations/03-hardening-and-patching/index.md) — prioritisation
- A working isolated network from [LAB-111-01](../levels/level-1-foundations/11-virtualization-and-lab-networks/lab-01-isolated-network.md)

---

## Lab setup

1. Build the five hosts in the register: a router/firewall VM, a domain controller, a web server, a file server,
   and your analyst workstation. Use the OS versions listed, or record the versions you actually used.
2. Put all five on one host-only or internal virtual network, `10.10.10.0/24`.
3. Introduce **at least three** deliberate weaknesses, such as: a service bound to `0.0.0.0` that should be
   loopback-only, a default credential on a lab service, an unnecessary legacy service (Telnet, FTP), a
   world-writable web directory, or a missing host firewall.
4. Snapshot every host. Record the snapshot names in your scope document.
5. Verify isolation with the four checks from
   [LAB-111-01](../levels/level-1-foundations/11-virtualization-and-lab-networks/lab-01-isolated-network.md), and
   save the output. It is an artefact, not a formality.

---

## Required tasks

| # | Task | Output |
| --- | --- | --- |
| 1 | Scope and rules of engagement, including exclusions, stop conditions and contacts | `01-scope.md` |
| 2 | Host discovery across the registered addresses, with the method that answered | `02-discovery.md` |
| 3 | Service inventory per host: port, protocol, service, version, how confirmed, confidence | `03-inventory.csv` |
| 4 | Configuration review on at least three hosts, using the credentials provided | `04-config-review.md` |
| 5 | Validation log: each claim, the check that confirmed or rejected it | `05-validation.md` |
| 6 | Findings with severity, rationale, impact and reproduction | `06-findings.md` |
| 7 | Remediation plan ordered by risk reduced per unit of effort, with verification steps | `07-remediation.md` |
| 8 | Apply two fixes, then retest both and record the new evidence | `08-retest.md` |
| 9 | Report: executive summary plus technical annex, with limitations | `09-report.md` |
| 10 | Evidence register with SHA-256 for captures and exports | `evidence/register.csv` |

---

## Expected artefacts

```text
capstone-network/
├── README.md
├── 01-scope.md
├── 02-discovery.md
├── 03-inventory.csv
├── 04-config-review.md
├── 05-validation.md
├── 06-findings.md
├── 07-remediation.md
├── 08-retest.md
├── 09-report.md
└── evidence/
    ├── register.csv
    ├── discovery.txt
    ├── scans/
    └── captures/
```

---

## Testing and validation

Your assessment is validated by **replay**, not by assertion:

| Check | How it is done |
| --- | --- |
| Inventory accuracy | A peer picks three rows and reproduces the confirmation method |
| Finding validity | Each finding has a command or request that produces the observed state |
| Severity calibration | Each rating cites likelihood, impact and one contextual factor |
| Remediation quality | Each fix names a command/config change and the command that verifies it |
| Retest | The original test is re-run, output captured, and the claim limited to what changed |
| Evidence integrity | Stor
age files hash to the values in the register |

A finding with no reproduction step is treated as unvalidated and earns no marks for correctness.

---

## Security and ethical requirements

- Written scope before the first packet. If you cannot name the owner and the authorisation, you are not ready.
- Only registered addresses. Unexpected hosts are recorded and reported, never scanned.
- No denial of service, no persistence, no data modification. Validation stops at the minimum needed to prove
  the condition.
- Credentials used only for configuration review, stored in a password manager, removed from artefacts.
- Synthetic data only; screenshots redacted of anything identifying a real system.
- If isolation fails mid-assessment, stop, disconnect, fix, and record the interruption.

---

## Submission checklist

- [ ] Scope document with authorisation reference, exclusions, stop conditions, snapshot names
- [ ] Isolation evidence
- [ ] Inventory with confirmation method and confidence per service
- [ ] Configuration review of three or more hosts
- [ ] Validation log, including at least one rejected claim
- [ ] Findings with severity rationale, impact and reproduction
- [ ] Remediation ordered and verifiable
- [ ] Two fixes applied and retested, with before/after evidence
- [ ] Report with executive summary, technical annex and limitations
- [ ] Evidence register with hashes

---

## Rubric — 100 marks

| Criterion | Marks | What earns full marks |
| --- | --- | --- |
| Scope, authorisation and safety planning | 10 | Targets named and bounded; stop conditions and contacts stated; isolation evidenced |
| Discovery and inventory | 20 | Complete for the registered range; confirmation method per service; UDP ambiguity not overstated |
| Validation and analysis | 20 | Every finding validated; at least one scanner claim rejected with reasoning |
| Findings and risk | 20 | Severity justified by likelihood, impact and context; impact not overstated |
| Remediation and retest | 15 | Fixes specific and verifiable; retest evidence; residual risk stated |
| Reporting and communication | 10 | Two audiences; executive summary free of jargon; annex replayable |
| Ethics and professional conduct | 5 | Scope respected; evidence handled properly; an unmentioned risk identified |

Bands and the program-level mapping: [How Assessment Works](../policies/assessment-format.md#6-capstone-rubric).
A scope violation voids the submission regardless of the mark above.

---

## Starter files

| File | Use |
| --- | --- |
| [`asset-register.csv`](../assets/assessments/starters/asset-register.csv) | Pre-filled host list; complete the service and evidence columns |
| [`findings-register.csv`](../assets/assessments/starters/findings-register.csv) | Optional findings table, if you prefer CSV to Markdown |
| [Assessment Report Template](../policies/assessment-report-template.md) | The report structure the rubric expects |

No scan output is supplied: building the network is part of the work. The
[reference solution](reference-solutions.md#capstone-1-network-security-assessment) describes what a strong
submission contains, not the answers to your specific build.

---

## Suggested extensions

- Add a second subnet and assess the segmentation policy between them with allowed and denied probes.
- Introduce a host firewall and show how it changes the inventory's confidence levels.
- Compare your findings against a CIS benchmark for one host and report the delta.
- Write a one-page executive brief for a non-technical owner and test it on someone outside the course.

---

## Common pitfalls

- **Scanning everything.** Discovery finds a host not on the register; testing it is the mistake that voids the
  capstone.
- **Inventory from one tool.** A version banner from Nmap is a claim; confirm it with the service itself.
- **Severity inflation.** Five "critical" findings on a lab network tells the reader you cannot rank.
- **Remediation as a verb.** "Harden the server" cannot be retested.
- **Retest that proves nothing.** Changing the config and re-running the scan without recording the original
  output leaves no before/after.
- **Report written in the last two days.** The evidence trail will not support it.

---

## Related

- [Capstone overview](index.md) · [Project Guide](../start-here/project-guide.md)
- [CYB-403 · Hardening, Baselines and Vulnerability Management](../levels/level-4-defensive-operations/03-hardening-and-patching/index.md)
- [Assessment Report Template](../policies/assessment-report-template.md)

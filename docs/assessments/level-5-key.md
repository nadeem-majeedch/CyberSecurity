---
title: "Level 5 Answer Key"
description: "Answers and explanations for all 30 Level 5 items, plus marking criteria for the scoped engagement or hunt assessment."
module_code: ASM-L5K
level: 5
kind: assessment
prerequisites: [CYB-501]
estimated_minutes: 45
difficulty: advanced
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, answer-key, level-5, active-directory, cloud, hunting]
---

# Level 5 Answer Key

!!! warning "Attempt first"
    Attempt the [Level 5 quiz](level-5-quiz.md) before reading this page.

**Marking.** One mark per item, 5 per module. At this level, an answer that reaches the right conclusion for a
weak reason is marked as right-for-the-wrong-reason and does not count toward the 4-of-5 threshold.

---

## CYB-501 · Penetration Testing and Assessment

**Q501.1 — B.** Stop conditions, exclusions, contacts and data handling are engagement terms. Tool flags, test
order and CVSS vectors belong in the plan or report.

**Q501.2 — B.** Validate independently before rating. Scanner output is a claim; a finding is a demonstrated
condition with evidence and impact.

**Q501.3 — B.** Request, response, timestamp, target and the identity/role used. Without the identity, an
authorization finding cannot be reproduced — the same request may be legitimate for another role.

**Q501.4.** Severity is the technical impact of the weakness, usually expressed by a scoring system; business
risk combines likelihood with the value of the affected asset and the controls in place. A factor such as
internet exposure, data sensitivity, or an existing compensating control moves the finding between them.

**Q501.5.** Establish the mechanism from configuration or code, demonstrate a single minimal request that shows
resource consumption without sustained load, and state the theoretical impact. If a safe demonstration is not
possible, coordinate a window with the owner or leave it untested. Report: "potential denial of service by
[mechanism]; not tested because the scope forbids availability testing; recommended test in an approved
window." Never "test it briefly and hope".

---

## CYB-502 · Active Directory Security

**Q502.1 — A.** Request a service ticket for an account with a registered SPN, then crack the ticket offline.
Kerberoasting does not need elevated rights; it needs an SPN and a weak service-account password.

**Q502.2 — B.** `GenericAll` grants full control of the object. On a group, that includes adding a member — the
canonical path from a normal user to a privileged group.

**Q502.3 — B.** A single reset leaves existing tickets signed with the old key valid until their lifetime
expires; the second reset (after replication) invalidates them. This is why the order and replication wait
matter.

**Q502.4.** Tiering keeps credentials of higher trust out of systems of lower trust: Tier 0 (domain controllers
and identity infrastructure), Tier 1 (servers), Tier 2 (workstations), with separate administrative accounts and
dedicated administrative workstations. It breaks when administrators log into lower-tier systems with Tier 0
credentials, when local administrator passwords are shared, or when service accounts are reused across tiers.

**Q502.5.** Kerberoasting. Supporting details: 4769 events with RC4 (`0x17`) ticket encryption, and a burst of
requests for multiple SPNs from one workstation in a short window. Benign explanation to exclude: a legitimate
application or scheduled job requesting tickets after a service restart, or a vulnerability scanner; check the
baseline for that host and whether the SPNs correspond to services it normally uses.

---

## CYB-503 · Cloud Security

**Q503.1 — B.** The customer patches the guest OS, configures IAM, and secures data; the provider secures the
physical layer, hypervisor and managed service internals.

**Q503.2 — B.** Explicit actions on named resources with conditions, everything else denied. A wildcard action
limited to a region is still a wildcard.

**Q503.3 — B.** An unauthenticated request for a known object, after public-access blocks are enabled, returning
`403 AccessDenied`. Reading a console checkbox proves configuration intent, not behaviour.

**Q503.4.** Image layers and manifests are readable by anyone with registry or repository access and persist in
history; environment variables are visible through inspection, orchestrator APIs and CI logs. Rotation then
requires a rebuild, and the secret is copied to every host that runs the image. Use a secret manager or mounted
secret with short-lived credentials.

**Q503.5.** The pattern suggests defence evasion: logging was disabled to hide the IAM changes. First steps:
review the identity that called `StopLogging` and the IAM changes made in the window (create user/role, attach
policy, create access key), and check for persistence (new trust, new trail configuration, modified roles).
Control: an organisation-wide, multi-region trail with immutable storage, plus an alert on `StopLogging` and on
trail modification.

---

## CYB-504 · Malware Analysis

**Q504.1 — B.** Static analysis gives structure, strings and metadata; runtime behaviour and decrypted
configuration require execution in a sandbox — or careful emulation.

**Q504.2 — B.** Host-only/internal networking, no shared folders, a snapshot, and simulated services (such as
INetSim) to observe network attempts without real egress.

**Q504.3 — B.** It matches the intended family and stays quiet on a negative corpus. A rule that matches only the
sample it was written from is a hash with extra steps.

**Q504.4.** An indicator is an inference: a domain may be shared infrastructure, a mutex may be a library
artefact, a string may be a false positive. Confidence tells the responder how much weight to give it, separates
observation from inference, and prevents the report from laundering a guess into a fact.

**Q504.5.** Report the abuse chain: the signed utility, its full command line, the parent process, the download
destination, and the hash of the payload. Avoid concluding that the signed binary or vendor is malicious —
legitimate tools are commonly abused, and the finding is the behaviour, not the signature.

---

## CYB-505 · Security Automation

**Q505.1 — B.** Dry-run by default, explicit allowlist, `--apply` to act. Everything else is a hope.

**Q505.2 — B.** Running twice yields the same state, without duplicating or reversing work. It is what makes
retries and re-runs safe.

**Q505.3 — B.** Secret store or runtime injection, never logged, rotated. File permissions on a hard-coded
secret are a mitigation for one failure mode, not a control.

**Q505.4.** Nobody is watching: a failure must propagate to a scheduler, pipeline or alert, and a non-zero exit
is how that happens. Silent success on partial failure leaves the operator believing a task completed.

**Q505.5.** Honour `Retry-After`, use exponential backoff with jitter, bound the number of retries, reduce
concurrency, and checkpoint progress so the run can resume. Must not: retry in a tight loop, ignore the status
and continue, or increase parallelism to get through the backlog faster.

---

## CYB-506 · Threat Hunting and Detection Engineering

**Q506.1 — B.** It names behaviour, data source and expected observable, so the data can prove it false.

**Q506.2 — B.** Hypothesis, data queried, time range, result, and the coverage gap revealed. A null result that
documents a blind spot is a successful hunt.

**Q506.3 — B.** Overclaimed coverage. A related rule is not coverage of the technique unless it observes the
behaviour the technique produces.

**Q506.4.** An exception suppresses the behaviour the rule exists to detect, so a compromised account becomes
invisible. Proper tuning changes the logic — adding context such as destination rarity, parent process or volume
— or splits the rule into a high-fidelity alert plus a lower-severity signal.

**Q506.5.** Analyses: interval regularity (mean, standard deviation, coefficient of variation, including
outside-hours activity), and destination/payload reputation plus baseline comparison with other hosts. Benign if
it matches a documented telemetry or update service, shows consistent payload sizes, and appears across many
hosts with the same pattern — but "it is regular" alone is not benign, because beacons are regular by design.

---

## Troubleshooting exercises — marking criteria

**T506.1** (3 marks) — three of, in a sensible order: confirm the log source is arriving (agent status,
`archives.json`, manager API); confirm the decoder produces the fields the rule uses (verbatim production line
through `wazuh-logtest`); confirm the rule is enabled and not shadowed by a higher-priority rule; confirm the
converted syntax matches the target engine. The proof that data is present at all: a search on the raw index
returning events for the time range.

**T506.2** (3 marks) — the defect: partial failure reported as success means the operator cannot tell that 3
indicators were never enriched, and downstream decisions use incomplete data. Correct behaviour: log each
failure with the indicator and reason, exit non-zero (or a distinct code) when any record fails, and write a
summary with counts. Award the third mark for distinguishing "some records failed" from "the run failed
entirely".

**T506.3** (3 marks) — three of: the container is attached to another network (compose file or `docker network
connect`); it is running with host networking, or an orchestrator overrides the flag; traffic is leaving through
a sidecar or a proxy on the host; the check is wrong (test from inside with `ip route` and a connection attempt).
Each needs its specific verification command.

---

## Level 5 integrated assessment — model answers

The assessment is either a **scoped mini-engagement** on the lab range or a **hunt** on the sample telemetry.
Both are marked against the same structure: methodology, technical depth, reporting, conduct.

### Engagement route — expected shape

| Element | What a strong submission contains |
| --- | --- |
| Scope and RoE | Named targets and exclusions, window, permitted techniques, stop conditions, contact, data handling |
| Method log | What was done, when, with which tool and version; what was deliberately not done |
| Findings | Each validated, with reproduction steps, evidence, severity and business context |
| Exploitation depth | Enough to prove impact, no more; no persistence, no data exfiltration beyond a marker file |
| Remediation | Specific, verifiable, ordered by risk reduced per unit effort |
| Retest | One finding retested after a fix, with the new evidence |

### Hunt route — expected shape

| Element | What a strong submission contains |
| --- | --- |
| Hypothesis | Falsifiable, with behaviour, data source and expected observable |
| Data audit | What telemetry exists, time range, known gaps |
| Query and result | Reproducible query, counts, and the null or positive result |
| Analysis | Statistical or contextual reasoning, with alternative explanations considered |
| Detection | One rule derived from the hunt, with the tests it passed |
| Report | What was found, what was not, and what the gap means |

### Written component criteria

**M1 — Methodology (10 marks).** Scope respected; sequence justified; alternatives named. For a hunt: the
hypothesis is falsifiable and the data audit precedes the query.

**M2 — Technical depth (10 marks).** The work goes beyond the module labs in at least one respect — a second
data source, a measured result, a limitation overcome — and handles failure without hand-waving.

**M3 — Reporting (7 marks).** Two audiences served; claims carry evidence; confidence and limits stated;
recommendations actionable and ordered.

**M4 — Professional conduct (3 marks).** Nothing touched outside scope; evidence handled properly; a risk the
brief did not mention was identified and handled, or its absence explained. This is a small weighting because
conduct is a gate elsewhere: a scope violation voids the assessment regardless of the score.

---

## Scoring

| Module score | Action |
| --- | --- |
| 5/5 | Retake at seven days |
| 4/5 | Reread the missed explanation |
| 3/5 | Revisit the lesson and the lab it came from |
| 0–2/5 | The module's lab is the prerequisite for understanding, not the quiz |

Level total: 30 marks; 24 or above suggests readiness for the integrated assessment and the capstone.

## Related

- [Level 5 quiz](level-5-quiz.md) · [Level 5 integrated assessment](level-5-assessment.md)
- [Capstone briefs](../projects/index.md)
- [Level 5 overview](../levels/level-5.md)

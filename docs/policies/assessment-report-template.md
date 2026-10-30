---
title: "Assessment Report Template"
description: "The professional security assessment report format used from Level 2 onwards: scope, findings, evidence, risk and remediation."
module_code: CYB-206
level: 2
kind: reference
prerequisites: []
estimated_minutes: 0
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [reporting, template, findings, risk]
---

# Assessment Report Template

Use this template for every assessment from Level 2 onwards. Later levels add sections (forensic timelines,
detection rules, incident narratives) but never remove these.

Copy the block below into `assessment-report.md` in your lab folder and fill it in. Do not leave placeholder
brackets in a submitted report — either fill a section or delete it and say why it does not apply.

---

```markdown
# Security Assessment Report

| Field | Value |
| --- | --- |
| Title | [Short descriptive title] |
| Author | [Your name] |
| Date (UTC) | [YYYY-MM-DDThh:mmZ] |
| Version | 1.0 |
| Classification | Training / Internal |
| Module | [e.g. CYB-206] |

## 1. Executive summary

Three to six sentences aimed at a reader who will not read the rest: what was assessed, what was found at the
highest level, what it means for the organisation, and what to do first. No jargon, no tool names, no command
output.

**Overall risk: [High / Medium / Low]**

## 2. Scope and authorisation

| Item | Detail |
| --- | --- |
| Systems in scope | [hostnames, addresses, ranges] |
| Systems explicitly out of scope | [everything else that is nearby] |
| Authorisation | [who authorised, when, reference] |
| Assessment window | [start and end, UTC] |
| Testing constraints | [no DoS, no data modification, no persistence] |
| Data handling | [where artefacts are stored, retention, deletion] |

State plainly: *any target not listed above was not tested*. If something was found incidentally on an
out-of-scope system, say what you did (typically: stopped, recorded, reported).

## 3. Methodology

| Phase | Activities | Tools used (with versions) |
| --- | --- | --- |
| Reconnaissance | | |
| Enumeration | | |
| Analysis | | |
| Verification | | |

Include what you deliberately did **not** do, and why.

## 4. Findings summary

| ID | Title | Severity | CVSS (optional) | Affected asset | Status |
| --- | --- | --- | --- | --- | --- |
| F-01 | | High | | | Open |

Severity must be justified, not asserted. Use likelihood × impact:

| Severity | Meaning |
| --- | --- |
| Critical | Direct path to full compromise of a critical asset; no user interaction |
| High | Serious impact likely, or a clear path to escalation/high-value data |
| Medium | Real but conditional impact, or a weakness requiring a second condition |
| Low | Limited impact, defence-in-depth, or hygiene |
| Info | Observation with no direct risk |

## 5. Detailed findings

Repeat this block per finding. Keep the order: evidence first, opinion second.

### F-01 — [Title]

| Field | Value |
| --- | --- |
| Severity | [High] |
| Asset | [hostname / address / service] |
| Component | [exact version where known] |
| Discovered | [date, UTC] |

**Description.** What the issue is, in plain language, plus the technical mechanism.

**Evidence.** The exact commands and their output, truncated to what matters. Reference the artefact file and its
hash. Include the collection timestamp and the capture point or query used.

```
[command]
[relevant output]
```

**Impact.** What an attacker could achieve, under what preconditions. State what you did *not* attempt and what
impact therefore remains hypothetical.

**Likelihood.** Why this would be reached in practice — this is where context beats a raw score.

**Reproduction.** Numbered steps a competent peer could follow to confirm the finding independently.

**Remediation.** Specific and verifiable. Prefer: *set `PermitRootLogin no` in a drop-in file, run `sshd -t`,
reload*. Avoid: *harden SSH*.

**Verification after remediation.** How you confirmed the fix: the command run and the new output.

**References.** CWE / CVE / vendor advisory, if applicable.

## 6. Remediation plan

| Finding | Action | Owner | Effort | Priority order |
| --- | --- | --- | --- | --- |
| F-01 | | | Low/Med/High | 1 |

Order by risk reduced per unit of effort, and say so explicitly.

## 7. Accepted risks and compensating controls

| Finding | Decision | Reason | Compensating control |
| --- | --- | --- | --- |
| | Accepted | | |

If a recommendation was declined, it is recorded here with the reason — not deleted from the report.

## 8. Limitations

Be specific. Examples:

- Assessment performed against a lab replica, not production.
- Offline network: no vendor advisory or CVE database was consulted at test time.
- Time-boxed to [N] hours; services A and B received enumeration but not exploitation.
- No authenticated testing on host C because no credentials were provisioned.
- Findings were validated manually; no exploit was executed and no impact was demonstrated beyond reachability.

## 9. Appendix

| Item | Detail |
| --- | --- |
| Artefacts | [files, with SHA-256 where applicable] |
| Tool versions | |
| Raw outputs | [filenames] |
| Glossary | [link or short list] |
```

---

## Severity and wording rules

| Do | Don't |
| --- | --- |
| "SSH permits direct root login with password authentication" | "SSH is insecure" |
| "Reachable from any host on the lab segment" | "Wide open" |
| "An attacker with network access could…" | "Hackers will…" |
| "Verified: `sshd -T` reports `permitrootlogin yes`" | "It appears that…" |
| "Not tested — out of scope" | Staying silent about an untested area |
| "Impact was not demonstrated" | Implying impact you did not show |

Language discipline matters because reports are read by people who will act on them, and because overstating a
finding destroys your credibility on the findings that matter.

## Marking criteria

| Criterion | Weight |
| --- | --- |
| Scope and authorisation statements complete and honest | 15% |
| Findings have all required fields, with evidence | 25% |
| Severity justified by likelihood and impact | 15% |
| Remediation specific, verifiable and correctly ordered | 20% |
| Limitations stated, accepted risks recorded | 15% |
| Writing: concise, unambiguous, no sales language | 10% |

## Related

- [CYB-206 · Host Inspection and Hardening](../levels/level-2-tooling/06-host-inspection-and-hardening/index.md)
- [LAB-206-03 · Write the Assessment Report](../levels/level-2-tooling/06-host-inspection-and-hardening/lab-03-assessment-report.md)
- [Assessment Guide](../start-here/assessment-guide.md)
- [Safety Policy](safety-policy.md)

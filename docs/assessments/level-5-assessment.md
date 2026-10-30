---
title: "Level 5 Integrated Assessment — Scoped Engagement or Hunt"
description: "A four-hour scoped mini-engagement or hypothesis-driven hunt on the lab range, plus a written defence of methodology, depth and limits."
module_code: ASM-L5A
level: 5
kind: assessment
prerequisites: [CYB-501, CYB-506]
estimated_minutes: 330
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-501-02, LAB-506-01]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, level-5, engagement, hunting, professional-practice]
---

# Level 5 Integrated Assessment

**Part A:** practical, 4 hours, 70 marks. **Part B:** written defence, 90 minutes, 30 marks.

You choose one route at the start and stay on it:

- **Route A — scoped mini-engagement** on the lab range, with a written engagement package, a bounded test, and a
  client-style report.
- **Route B — hypothesis-driven hunt** on the sample telemetry, with a data audit, a reproducible query, and a
  detection derived from the result.

Both routes are marked against the same criteria, because both test the same professional skill: making a claim
that survives a reviewer who was not there.

---

## The brief

> *You have four hours and one bounded question. Produce work that a competent reviewer could check without
> asking you anything, and state plainly what you did not establish.*

**Route A scope:** one target host on your isolated range, plus the identity service if you use CYB-502's lab.
Ports and services in scope: those you identify. Explicitly out of scope: denial of service, persistence, data
exfiltration beyond a marker file, any host not named in your package.

**Route B scope:** the sample telemetry from
[CYB-506](../levels/level-5-advanced/06-threat-hunting/index.md) — endpoint events, DNS/proxy logs and the
beacon dataset. No live host required; no live adversary; nothing outside the dataset.

**Non-negotiable:** no public target, no real credentials, no real data, no live malware, no traffic leaving the
lab. These are not marked criteria — they are conditions of the assessment existing at all.

---

## Part A — Practical (70 marks)

### Route A

| Task | Marks | Requirements |
| --- | --- | --- |
| A1 Engagement package | 15 | Scope with named targets and exclusions, RoE, window, techniques, stop conditions, contact, data handling |
| A2 Method log | 10 | Timestamped actions with tool and version; what you deliberately did not do |
| A3 Findings | 20 | At least three validated findings with reproduction, evidence, severity and business context |
| A4 Remediation and retest | 15 | Specific fixes with verification steps; one finding retested with new evidence |
| A5 Report | 10 | Executive summary plus technical annex, limitations stated |

### Route B

| Task | Marks | Requirements |
| --- | --- | --- |
| A1 Hypothesis and data audit | 15 | Falsifiable hypothesis; data sources, time range, known gaps |
| A2 Query and result | 10 | Reproducible query, counts, and the null or positive result stated plainly |
| A3 Analysis | 20 | Two or more analyses (e.g. interval regularity, rarity, baseline comparison), alternatives considered |
| A4 Detection | 15 | One rule derived from the hunt, with positive, negative and no-data tests recorded |
| A5 Report | 10 | Finding or null result, gap analysis, recommendation, limitations |

### Artefacts

```text
level-5-assessment/
├── README.md
├── 01-scope-or-hypothesis.md
├── 02-method-or-data-audit.md
├── 03-findings-or-analysis.md
├── 04-remediation-or-detection/
├── 05-report.md
└── evidence/
```

---

## Part B — Written defence (30 marks, 90 minutes)

Answer all four. These are the questions a reviewer or client would actually ask.

**M1 (10 marks).** Defend your methodology: why this sequence, what you rejected, and what would have made you
stop.

**M2 (10 marks).** Name the weakest claim in your submission and the evidence that would settle it. Then state
one limitation you chose not to mention in the report, and why that choice was wrong or right.

**M3 (7 marks).** For Route A: how did you decide severity versus risk for each finding? For Route B: how did
you decide the hunt was complete rather than merely stopped?

**M4 (3 marks).** State one risk the brief did not mention, whether it applied to your work, and what you did
about it.

---

## Marking

### Part A (70)

Marked against the task tables above. Full marks require:

- **Reproducibility** — a reviewer can replay the work from the artefacts.
- **Bounded claims** — nothing asserted beyond what the evidence shows.
- **A retest or a test matrix** — proof that the work is verifiable, not just plausible.
- **A written artefact** — the report is part of the assessment, not an afterthought.

### Part B (30)

| Criterion | Marks | Descriptor |
| --- | --- | --- |
| Methodology | 10 | Sequence defended; rejected alternatives named; stop condition stated |
| Technical depth | 10 | Goes beyond the module labs in one respect; limitations handled honestly |
| Reporting | 7 | Two audiences; claims evidenced; confidence labels; actionable recommendations |
| Professional conduct | 3 | Scope respected; evidence handled properly; an unmentioned risk identified |

### Domain weights

| Domain | Weight |
| --- | --- |
| Methodology | 30% |
| Technical depth | 35% |
| Reporting | 25% |
| Professional conduct | 10% |

The safety gate applies: any traffic outside the lab, any persistence, any real data, or any public target voids
the assessment and, in a real engagement, would end it.

---

## Self-marking

1. Ask whether a reviewer could rerun your work from the artefacts. Pick the claim you are least sure of and try.
2. For Route B, re-run your query from the written text alone; if it differs from what you reported, the
   documentation is wrong.
3. For Route A, check that every finding has a retest or a retest plan.
4. Mark Part B against the elements in the [key](level-5-key.md#level-5-integrated-assessment-model-answers).

---

## Common pitfalls

- **Route choice for the wrong reason.** Route A looks more impressive; Route B is easier to defend honestly. Pick
  the one you can finish and substantiate.
- **A hunt that becomes browsing.** If the hypothesis changed three times, say so and report the null result.
- **Depth without evidence.** "Exploited the domain" with no reproduction steps is a story.
- **A report that argues.** Recommendations should be ordered by risk reduced per unit effort, not by how much
  you enjoyed the finding.
- **Unstated limits.** The reviewer assumes you missed them; stating them earns marks.

---

## Submission checklist

- [ ] One route, declared at the top of the README
- [ ] Scope or hypothesis, with exclusions or data gaps
- [ ] Method log or data audit with timestamps
- [ ] Findings or analysis, each with evidence
- [ ] Remediation with verification, or a detection with its test matrix
- [ ] Report for two audiences, with limitations
- [ ] Four written answers, each defending a decision
- [ ] Nothing outside the lab

---

## Related

- [Level 5 quiz](level-5-quiz.md) · [Answer key](level-5-key.md)
- [CYB-501 · Penetration Testing and Security Assessment](../levels/level-5-advanced/01-penetration-testing/index.md)
- [CYB-506 · Threat Hunting and Detection Engineering](../levels/level-5-advanced/06-threat-hunting/index.md)
- [Capstone briefs](../projects/index.md) — the same skills at ten times the scope

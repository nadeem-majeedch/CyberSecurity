# Assessment Format

**Status:** mandatory for all graded components · **Version:** 2.0 · **Date:** 30 October 2026

*Version 2.0 publishes answer keys for self-study use; see §7 for the reasoning and the trade-off.*

---

## 1. Principles

1. **Authentic over convenient.** A learner who can produce a defensible report, a working detection,
   or a hardened host has demonstrated more than one who can pass a quiz. Practical work carries the
   majority of the weight at every level.
2. **Criterion-referenced.** Results describe what a learner can do against stated criteria, not how
   they compare with peers.
3. **Transparent.** Criteria, bands, weights, answer keys and model answers are published. Only live
   flags, cohort variants, and personal data are withheld.
4. **Self-study first.** A learner with no instructor must be able to check their own work, which
   means keys cannot live in a private repository. What stays unpublished is what would let someone
   fake completion rather than verify it: flags for live cohort labs, results, and marking records.
5. **Safety is assessed.** A technically correct submission that violated scope is not a passing
   submission, at any level.
6. **Time-boxed honesty.** Estimates are stated so learners can plan; they are not a grading factor.

---

## 2. Components per level

| Component | Where it appears | Weight | Format | Marked by |
| --- | --- | --- | --- | --- |
| Knowledge check | Every module | 15% | 5–10 items, self-scored against the published key | Learner (self-paced) / instructor (cohort) |
| Practical lab | Every module | 45% | Artefact + evidence + short write-up | Rubric (§4) |
| Level assessment | End of each level | 40% | Practical task under time constraint + written justification | Rubric + model answer |
| Capstone | End of program | Pass/fail with distinction | Project, report, defence | Capstone rubric (§6) |

Level result bands: **< 60 fail · 60–69 pass · 70–84 merit · 85+ distinction**, with a hard
requirement that no component scores below 50 and the safety criterion is at least "competent".

---

## 3. Knowledge checks

**Design rules:**

- 5–10 items per module; mix of multiple-choice (one best answer) and short answer.
- Every item maps to a stated learning outcome. No item tests trivia that appears nowhere in the lesson.
- Distractors are plausible and reflect real misconceptions, not obvious nonsense.
- No "all of the above", no double negatives, no trick wording, no "which is FALSE" unless the
  negative is bolded.
- Scenario framing preferred: "A colleague sends you a pcap showing… what is the most likely cause?"
- Short-answer items state the expected depth ("two sentences", "name two controls and justify one").

**Publication:** questions live on a level quiz page (`assessments/level-N-quiz.md`); answers and
explanations live on a separate key page (`assessments/level-N-key.md`). The separation is deliberate:
looking up an answer requires a second, conscious action, and the key page opens with the
attempt-first rule.

**Attempt-first protocol:** attempt all items on paper, mark each as correct, wrong, or *right for the
wrong reason*, then read every explanation, then retake at seven days. Target 4 of 5 with no
right-for-the-wrong-reason answers before moving on. The full protocol is in the
[Assessment Guide](../start-here/assessment-guide.md#1-knowledge-checks-the-honest-protocol).

---

## 4. Practical lab rubric

Four criteria, five bands. The bands are described generically here; each lab adds
domain-specific descriptors for "what good looks like".

| Criterion | Weight | 1 — Not yet | 2 — Developing | 3 — Competent | 4 — Proficient | 5 — Exemplary |
| --- | --- | --- | --- | --- | --- | --- |
| **Correctness** | 35% | Objective not achieved | Partial result, key step wrong | Objective achieved with minor gaps | Achieved efficiently, edge cases handled | Achieved and generalised; explains why it works |
| **Methodology** | 25% | Undirected trial and error | Follows steps without understanding | Sound sequence, justified choices | Alternatives considered and rejected with reasons | Method would survive peer review; limitations stated |
| **Evidence and documentation** | 25% | No evidence or unreproducible | Sparse evidence, missing context | Clear evidence, timestamps, reproducible | Structured report a third party could replay | Professional-grade: findings, impact, remediation, residual risk |
| **Safety and ethics** | 15% | Scope violated or isolation unchecked | Scope correct but undocumented | Scope and isolation documented | Proactive checks; stops appropriately | Identifies a scope risk the instructions missed and handles it correctly |

**Gate:** a score of 1 on *Safety and ethics* voids the submission regardless of other scores.

---

## 5. Level assessment blueprint

Each level assessment has two parts: a **practical task** (70% of the assessment) and a **written
component** (30%). The written component asks the learner to justify decisions, not to recall facts.

| Level | Practical task | Written component | Domain weights |
| --- | --- | --- | --- |
| 1 | Build and verify an isolated lab from a brief; configure hosts; document | Explain architecture choices, isolation proof, and one risk you accepted | Networking 30, OS admin 30, lab design 25, ethics 15 |
| 2 | Enumerate and assess a provided lab host; produce findings table | Justify scan choices; distinguish finding from false positive; state limits of the evidence | Recon 30, analysis 30, reporting 25, safety 15 |
| 3 | Assess a local vulnerable app; fix one flaw in the provided code | Root-cause each finding and defend the fix; explain a crypto decision | Web 40, crypto 20, IAM 20, secure coding 20 |
| 4 | Detect, contain, and report a scripted intrusion in the lab | Post-incident review: timeline, decisions, what you would change | Detection 30, IR 30, forensics 20, hardening 20 |
| 5 | Scoped mini-engagement or hunt on an instructor range | Engagement report or hunt report with confidence levels and limitations | Methodology 30, technical depth 35, reporting 25, professional conduct 10 |

**Time limits** are stated per assessment (typically 2–4 hours for the practical, 90 minutes for the
written part). Open-book by design: the assessment is about judgement under realistic conditions,
not memory.

---

## 6. Capstone rubric

| Dimension | Weight | What distinguishes a pass | What earns distinction |
| --- | --- | --- | --- |
| Problem definition and scope | 15% | Clear question, bounded scope, stated authorization | Scope decisions justified against alternatives and risk |
| Technical execution | 30% | Artefacts work and are reproducible | Depth beyond the module content; handles failure gracefully |
| Evidence and analysis | 25% | Evidence supports each claim; no unsupported conclusions | Quantified impact; distinguishes confidence from certainty |
| Reporting and communication | 20% | Two audiences served (technical + executive), clear structure | Persuasive, concise, actionable; anticipates objections |
| Ethics, safety, and professionalism | 10% | Scope respected and documented; limitations stated | Identifies and mitigates a risk not covered by the brief |

Pass requires ≥ 60 overall with no dimension below 50 and full marks on the ethics dimension (no
scope violation). Distinction requires ≥ 85 overall.

---

## 7. Answer keys and publication rules

**Published in this repository:** question text, answer keys with explanations, acceptable-reasoning
notes for open items, marking criteria and band descriptors, 100-mark capstone rubrics, starter data,
and reference solutions marked as such.

**Never committed:** flags or expected exploit output for live cohort lab variants, learner results,
cohort lists, marking spreadsheets, moderation notes, and any credential or personal data.

**Why keys are published.** A self-study learner has no marker. Without keys, "check your
understanding" reduces to rereading the lesson and hoping, and an item the learner got wrong looks
identical to one they got right. Explanations also carry most of the teaching value: the reason a
plausible distractor is wrong is usually the actual misconception.

**What this costs, stated honestly.** A published item can be read instead of solved, so these items
cannot serve as a closed-book test of recall; and an instructor cannot reuse the exact items for a
graded cohort test. Both are accepted: the course is optimised for one learner with a laptop, and the
items are written to test reasoning that a lookup does not supply.

**Cohort variants.** An instructor assessing a closed cohort should build a variant from the same
outcomes — different scenario, same misconception targets — and keep that variant's key private. The
published key then covers the practice set only.

Enforcement:

- **No automated scanner is committed yet.** Until one is, enforcement is manual: every assessment page is
  reviewed for real hostnames, real people or organisations, live flags, and credential shapes, and synthetic data
  must be labelled synthetic.
- A pattern check and a secret scan are specified in the maintainer documentation as a precondition for enabling
  CI. Once implemented, they should fail the build on flag formats, credential shapes, and real identifiers.
- If a live cohort variant leaks, rotate its flag or scenario, notify the cohort, and record the
  incident in `instructor/review-log.md`.

---

## 8. Academic integrity

**Collaboration.** Discussing concepts, debugging together, and comparing approaches is encouraged.
Submitting another person's artefact, evidence, or report as your own is not. Evidence must come from
your own run: your hostnames, your timestamps, your captures.

**AI assistance.** Permitted as a tutor: explaining an error message, suggesting a debugging step,
reviewing your reasoning, drafting structure. Required: a short disclosure in any assessed submission
stating which tools were used and for what.

Not permitted: submitting AI-generated analysis, findings, or reports as your own work; using AI to
produce exploit content you do not understand; pasting confidential or real data into a third-party
service.

The test is simple: **can you defend every sentence and every command in your submission in a live
conversation?** If not, it is not your work yet.

**Sharing.** Do not publish flags, walkthroughs of assessed labs, or another learner's report.
Publishing a walkthrough of a *published, non-assessed* exercise is allowed and useful.

**Plagiarism of external sources.** Cite everything, including tool documentation and blog posts,
with access dates. Paraphrasing without citation is plagiarism.

---

## 9. Feedback, resubmission, and moderation

- **Feedback turnaround:** 7 working days for labs, 14 for level assessments (cohort mode).
- **Resubmission:** one resubmission per lab within 14 days, capped at "merit" band for the
  resubmitted criterion. Level assessments are not resubmitted; a failed level assessment may be
  re-attempted once with a different scenario.
- **Safety violations** are not resubmittable; they follow the [safety policy](safety-policy.md) §11.
- **Moderation:** a sample of at least 20% of submissions (minimum three) is second-marked. Discrepancy
  greater than one band triggers re-marking of the whole batch for that criterion.
- **Records:** marks are kept in the private system with a retention period set by the institution;
  nothing is stored on the public site.
- **Appeals:** a learner may request re-marking in writing within 14 days, with reference to the rubric.

---

## 10. Accessibility and accommodations

- Extra time (typically 25%) on request, with no effect on the rubric.
- Alternative evidence formats accepted where the criterion allows: written report, recorded
  walkthrough with captions, or a live demonstration.
- Colour-independent rubrics and tables; screen-reader-friendly submission formats.
- Assessments must not require a specific commercial tool where an equivalent open tool exists.

Accommodation requests go to the instructor and are recorded privately.

---

## 11. Self-paced learners

Because no submission is collected by this site, self-paced learners self-assess against the public
rubrics and the published keys. Recommended practice:

1. Complete the lab, then mark your own artefact against the rubric before reading any model answer
   or reference solution.
2. Ask a peer (or a study group) to replay your evidence from your notes alone — this tests the
   documentation criterion honestly.
3. Keep a portfolio: one artefact per level, with the rubric you applied and your own critique.

A certificate of completion, if offered, requires instructor review of the capstone; self-marked
results are not a credential.

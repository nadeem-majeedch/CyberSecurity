---
title: "Capstone 5 — Threat Detection"
description: "Write detection rules for a 43-event labelled corpus, test them for false positives and blind spots, tune without widening exceptions, and report coverage honestly."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-404, CYB-506]
estimated_minutes: 1200
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-404-02, LAB-506-02]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, detection, sigma, testing, attck]
---

# Capstone 5 — Threat Detection

**Route:** detection engineering · **Effort:** ~20 hours over 2–3 weeks · **Marks:** 100

---

## Problem statement

> A small team has endpoint process telemetry and nothing else. They want detection rules for four behaviours
> they are worried about, evidence that the rules work, and an honest statement of what the ruleset still misses.

You are given a labelled corpus of 43 process-creation events: 7 malicious, 36 benign, with two benign events that
a careless rule will match. Your job is a small, tested, documented ruleset — not a rule for everything.

---

## Learning outcomes

1. Turn a threat concern into a falsifiable detection hypothesis.
2. Write Sigma rules with metadata a reviewer can act on.
3. Test a rule for true positives, false positives, and silence when data is missing.
4. Tune by changing logic, not by suppressing the behaviour you meant to catch.
5. Measure precision and recall against labelled data, and explain what the numbers do not mean.
6. Map coverage to ATT&CK without overclaiming.
7. Report a ruleset's blind spots to the people who will rely on it.

---

## Scope and constraints

| Item | Detail |
| --- | --- |
| In scope | `events.jsonl` (43 events), `labels.csv`, and the four behaviours listed below |
| Out of scope | Live endpoints, real telemetry, production SIEM changes, writing to any shared system |
| Permitted | Sigma rules, a local evaluator, Python, spreadsheets; local Wazuh/Elastic for practice |
| Forbidden | Using `labels.csv` to write rules (it is for scoring only), publishing rules as tested when they are not |
| Time box | Suggested 4 hours data review, 8 hours rules, 4 hours testing, 4 hours reporting |
| Output | Three to five Sigma rules, a test matrix, measured results, a coverage note, a report |

**Behaviours to cover** (each from the corpus):

1. An Office application spawning PowerShell.
2. `certutil` used to download a file.
3. A scheduled task created to run as `SYSTEM`.
4. Volume shadow copies deleted.

You may add a fifth rule for another behaviour you can defend with the available fields.

---

## Prerequisites

- [CYB-404](../levels/level-4-defensive-operations/04-detection-and-siem/index.md) — Sigma, testing, tuning
- [CYB-506](../levels/level-5-advanced/06-threat-hunting/index.md) — coverage and overclaiming
- Basic YAML and Python; a local Python 3.10+ environment with `pyyaml`

---

## Lab setup

1. Download [`events.jsonl`](../assets/assessments/threat-detection/events.jsonl),
   [`labels.csv`](../assets/assessments/threat-detection/labels.csv) and the hash file.
2. Verify hashes. Put `labels.csv` aside; do not open it until your rules are written and you have predicted
   their results.
3. Read the event schema: `id`, `ts`, `host`, `user`, `process`, `parent`, `cmdline`, `event_type`, `dest_ip`.
4. Write your rules as YAML files in `rules/`, one file per behaviour, with `title`, `id`, `description`,
   `logsource`, `detection`, `falsepositives`, `level` and ATT&CK tags.
5. Use the [reference harness](../assets/assessments/reference/detection/run_detections.py) **only after** you have
   written your own evaluator or decided how you will test. It supports a documented Sigma subset.

---

## Required tasks

| # | Task | Output |
| --- | --- | --- |
| 1 | Threat statement and hypotheses: behaviour, data source, expected observable | `01-hypotheses.md` |
| 2 | Data audit: fields available, what each can and cannot show | `02-data-audit.md` |
| 3 | Three to five Sigma rules covering the required behaviours | `rules/*.yml` |
| 4 | Positive test per rule: the events it should match, predicted before running | `03-predictions.md` |
| 5 | Negative test per rule: benign lookalikes it must not match | `04-tests.md` |
| 6 | No-data test: what the rule does when the source is absent or misnamed | `05-no-data.md` |
| 7 | Measurement against `labels.csv`: TP, FP, FN, precision, recall per rule and overall | `06-results.csv` |
| 8 | False-positive analysis: one case you accept as benign, one rule you improve | `07-tuning.md` |
| 9 | Coverage note: present, partial, absent per behaviour, with the reason | `08-coverage.md` |
| 10 | Report: rules, tests, measured results, blind spots, deployment caveats | `09-report.md` |

Record predictions **before** running the evaluator. A rule that "worked" after you adjusted it to the labels
has not been tested; it has been fitted.

---

## Expected artefacts

```text
capstone-detection/
├── README.md
├── 01-hypotheses.md
├── 02-data-audit.md
├── 03-predictions.md
├── 04-tests.md
├── 05-no-data.md
├── 06-results.csv
├── 07-tuning.md
├── 08-coverage.md
├── 09-report.md
├── rules/
│   ├── office-spawns-powershell.yml
│   ├── certutil-download.yml
│   ├── schtasks-system.yml
│   └── shadow-copy-deletion.yml
└── harness/                # your evaluator, or a documented call to the reference one
```

---

## Testing and validation

| Test | What it must show |
| --- | --- |
| Positive | Each rule matches the events you predicted, and no others you did not predict |
| Negative | The two approved administrative actions are either not matched, or matched and classified as benign |
| No-data | With the data source renamed or removed, the rule produces zero matches and the harness reports it |
| Measurement | TP/FP/FN computed from `labels.csv`, with the arithmetic shown |
| Tuning | A changed condition, not an added exception, with the before/after result |
| Coverage | Claims named as present, partial or absent, each with the rule or gap that justifies it |

**Interpretation warning:** with 7 malicious events, one false positive moves precision by 0.1. Your report must
say that the corpus is small and that the numbers are illustrative, not production estimates.

---

## Security and ethical requirements

- Synthetic data only; no real telemetry, no production system.
- Do not deploy a rule to a shared SIEM as part of this capstone.
- Do not tune by excluding a user, host, or service account that an attacker could use — that is how detections
  die.
- Rules must not contain real indicators from public reporting without attribution; this corpus is fictional.
- If you publish your rules, state the corpus size and that they were tested only against it.

---

## Submission checklist

- [ ] Hypotheses with behaviour, data source and observable
- [ ] Data audit, including field limitations
- [ ] Three to five Sigma rules with metadata and ATT&CK tags
- [ ] Predictions recorded before testing
- [ ] Positive, negative and no-data tests documented
- [ ] Measured TP/FP/FN, precision and recall, with arithmetic
- [ ] One tuning change by logic, with before/after
- [ ] Coverage note with present/partial/absent
- [ ] Report with blind spots and deployment caveats
- [ ] `labels.csv` used only for scoring

---

## Rubric — 100 marks

| Criterion | Marks | What earns full marks |
| --- | --- | --- |
| Threat framing and data audit | 10 | Hypotheses falsifiable; field limitations stated before rules |
| Rule quality | 25 | Correct logic; metadata actionable; narrow enough to be useful; tags accurate |
| Testing | 20 | Positive, negative and no-data tests; predictions precede results |
| Measurement and tuning | 15 | Correct arithmetic; one logic-based improvement; small-sample caveat |
| Coverage and ATT&CK mapping | 10 | Present/partial/absent justified; no overclaiming |
| Reporting | 10 | Deployment caveats; blind spots; readable by a SOC lead |
| Ethics and professional conduct | 10 | Synthetic data; no production deployment; no dangerous exceptions |

Bands: [How Assessment Works](../policies/assessment-format.md#6-capstone-rubric).

---

## Starter files

| File | Use |
| --- | --- |
| [`events.jsonl`](../assets/assessments/threat-detection/events.jsonl) | 43 process-creation events |
| [`labels.csv`](../assets/assessments/threat-detection/labels.csv) | Ground truth — **scoring only** |
| [`run_detections.py`](../assets/assessments/reference/detection/run_detections.py) | Reference harness for the Sigma subset |
| [Reference rules](../assets/assessments/reference/detection/rules/office-spawns-powershell.yml) | Reference solution — **open only after submitting** |

The [reference solution](reference-solutions.md#capstone-5-threat-detection) reports 7 TP, 2 FP, 0 FN, precision
0.78 and recall 1.00 on this corpus, and explains why that is not a production estimate.

---

## Suggested extensions

- Add a fifth rule for a behaviour the corpus does not contain, and state how you would validate it.
- Implement one rule natively in Wazuh and compare its behaviour with the Sigma version.
- Build a small harness that runs a rule against a negative corpus of 1,000 benign events you generate.
- Add a correlation rule for two of the behaviours occurring within ten minutes on one host.

---

## Common pitfalls

- **Writing rules against the labels.** The result is a description of the corpus, not a detection.
- **A rule with no negative test.** Anything matches if you never check what should not.
- **Exceptions as tuning.** Suppressing the service account hides the attack you were looking for.
- **Precision claims without arithmetic.** Show TP, FP and the division.
- **Coverage inflation.** "We detect persistence" because one scheduled-task rule exists.
- **Ignoring the no-data case.** A silent rule looks healthy when its source is broken.

---

## Related

- [Capstone overview](index.md) · [Project Guide](../start-here/project-guide.md)
- [CYB-404 · Detection Engineering and SIEM](../levels/level-4-defensive-operations/04-detection-and-siem/index.md)
- [SigmaHQ](https://github.com/SigmaHQ/sigma) — rule format and conventions

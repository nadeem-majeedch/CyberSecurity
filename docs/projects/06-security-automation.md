---
title: "Capstone 6 — Security Automation"
description: "Build a tested Python tool that normalises three log formats, enriches indicators offline, and produces findings — with guardrails, exit codes and no secrets in code."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-202, CYB-505]
estimated_minutes: 1440
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-505-01, LAB-505-02, LAB-505-03]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, automation, python, testing, guardrails]
---

# Capstone 6 — Security Automation

**Route:** engineering · **Effort:** ~24 hours over 3–4 weeks · **Marks:** 100

---

## Problem statement

> Three systems log authentication and DNS activity in three different formats. At the end of each day, an
> analyst copies the lines into a spreadsheet, matches addresses against a threat-intelligence list by hand, and
> writes findings from memory. It takes ninety minutes and produces inconsistent results.

Build the tool that replaces that hour and a half — safely enough that it can run unattended, and honestly
enough that its output can be trusted.

---

## Learning outcomes

1. Specify a tool's inputs, outputs and failure modes before writing code.
2. Parse heterogeneous logs into one schema, handling malformed input without crashing.
3. Enrich indicators against a local dataset and produce deduplicated, prioritised findings.
4. Design guardrails: dry-run default, explicit targets, bounded retries, clear exit codes.
5. Write tests for the risky logic, including the refusal paths.
6. Handle secrets and API credentials without embedding or logging them.
7. Evaluate the tool against a measured baseline and report its limits.

---

## Scope and constraints

| Item | Detail |
| --- | --- |
| In scope | [`mixed.log`](../assets/assessments/security-automation/mixed.log) (30 lines, three formats), [`iocs.csv`](../assets/assessments/security-automation/iocs.csv) (8 indicators) |
| Out of scope | Live SIEM integration, real threat-intelligence APIs, production data, any action on a real host |
| Permitted | Python 3.10+, standard library, `pytest`, `pyyaml`; local mock API if you add one |
| Forbidden | Sending data to third-party services, hard-coded credentials, deleting or modifying the input files |
| Time box | Suggested 4 hours design, 12 hours implementation, 4 hours tests, 4 hours evaluation and report |
| Deliverable | Working tool, tests, README, evaluation report, sample output |

**Two modes, both required conceptually:**

- **Read mode** (default): parse, enrich, report. No side effects.
- **Action mode**: only if you add one — must default to dry-run, require an explicit flag, and restrict itself
  to a named target list. Actions are limited to local mock endpoints; nothing may touch a real system.

---

## Prerequisites

- [CYB-202](../levels/level-2-tooling/02-bash-python-git/index.md) — Python, exit codes, Git
- [CYB-505](../levels/level-5-advanced/05-security-automation/index.md) — normalisation, enrichment, guardrails
- [LAB-505-03](../levels/level-5-advanced/05-security-automation/lab-03-guarded-automation.md) — refusal paths

---

## Lab setup

1. Download `mixed.log`, `iocs.csv` and `SHA256SUMS.json`; verify hashes and record the result.
2. Create a Git repository for the tool, and commit the unmodified sample data as the first commit.
3. Create a Python virtual environment and install `pytest` (and `pyyaml` only if you need it).
4. Inspect the log by hand: identify each format, and find the lines that do not parse.
5. Write your design document before the first function. It is a marked artefact.

---

## Required tasks

| # | Task | Output |
| --- | --- | --- |
| 1 | Problem statement and requirements: inputs, outputs, non-goals | `01-requirements.md` |
| 2 | Design: data flow, schema, failure modes, guardrails | `02-design.md` |
| 3 | Parser for all three formats with a documented schema | `normalise.py` |
| 4 | Malformed-input handling: skip, record line number and reason, never crash | in code + `03-skipped.md` |
| 5 | Enrichment: match source IP and domain against `iocs.csv`, attach verdict and confidence | `enrich.py` |
| 6 | Findings: aggregate per indicator and host, prioritise, output JSON and Markdown | `findings.md`, `summary.json` |
| 7 | Guardrails: dry-run default, `--apply`, target allowlist, bounded retries, distinct exit codes | in code + `04-guardrails.md` |
| 8 | Logging and observability: structured log lines, summary counters, failure semantics | `05-logging.md` |
| 9 | Secrets: token from environment or file, never printed, never logged | `06-secrets.md` |
| 10 | Tests: unit tests for parsing, enrichment and refusals; fixture files | `tests/` |
| 11 | Evaluation: run against the corpus, record counts, compare with manual baseline | `07-evaluation.md` |
| 12 | README: install, usage, outputs, limitations, what the tool deliberately will not do | `README.md` |

---

## Expected artefacts

```text
capstone-automation/
├── README.md
├── 01-requirements.md
├── 02-design.md
├── 03-skipped.md
├── 04-guardrails.md
├── 05-logging.md
├── 06-secrets.md
├── 07-evaluation.md
├── src/
│   ├── __init__.py
│   ├── normalise.py
│   ├── enrich.py
│   └── cli.py
├── tests/
│   ├── fixtures/
│   ├── test_parse.py
│   ├── test_enrich.py
│   └── test_guardrails.py
└── out/
    ├── summary.json
    └── findings.md
```

---

## Testing and validation

| Check | Standard |
| --- | --- |
| Parsing | All three formats recognised; malformed lines skipped with line number and reason |
| Counts | Report states lines read, normalised and skipped, and the numbers reconcile |
| Enrichment | Every matched indicator carries verdict, confidence and source; no partial matches |
| Deduplication | One finding per indicator/host/action group, with count and time range |
| Guardrails | Dry-run produces no side effects; `--apply` refuses an unlisted target and exits non-zero |
| Secrets | Token read from environment or file; absent from code, output, logs and Git history |
| Tests | `pytest` passes; at least one test per refusal path; a deliberately broken fixture fails loudly |
| Reproducibility | Output regenerated from a clean checkout with documented commands |

A tool that works only on the supplied file, but crashes on one malformed line, fails the parsing criterion.

---

## Security and ethical requirements

- Operate only on the supplied synthetic files. Do not point the tool at real logs.
- No network calls to third parties. If you add an API mode, use a local mock and document it.
- Never hard-code credentials; never log a token, even partially.
- No destructive actions. If you implement action mode, it must be dry-run by default and target-restricted.
- Do not commit secrets, virtual environments, or generated output containing sensitive fields to Git.
- State the tool's limits: what it does not parse, what enrichment cannot see, where it could mislead.

---

## Submission checklist

- [ ] Requirements and design documents
- [ ] Three-format parser with a documented schema
- [ ] Malformed-line handling with counts and reasons
- [ ] Enrichment with verdict, confidence and source
- [ ] Aggregated findings in JSON and Markdown
- [ ] Guardrails documented and tested, including refusals
- [ ] Structured logging and meaningful exit codes
- [ ] Secrets handled outside code, proven absent from history
- [ ] Test suite passing, with refusal paths covered
- [ ] Evaluation with measured counts against the corpus
- [ ] README with usage, outputs and limitations

---

## Rubric — 100 marks

| Criterion | Marks | What earns full marks |
| --- | --- | --- |
| Problem framing and design | 10 | Clear inputs, outputs, non-goals; failure modes identified before coding |
| Parsing and normalisation | 20 | Three formats; schema documented; malformed input handled without data loss |
| Enrichment and findings | 10 | Correct matching, deduplication, prioritisation; evidence attached to findings |
| Guardrails and safety | 20 | Dry-run default; allowlist; bounded retries; refusals tested and non-zero exits |
| Testing | 15 | Unit tests for parsing, enrichment and refusals; fixtures; failures are informative |
| Observability and error handling | 5 | Structured logs; summary counts reconcile; partial failure visible |
| Secrets and credential handling | 10 | No secrets in code, output, logs or history; documented rotation path |
| Documentation and evaluation | 10 | README usable by a stranger; measured results; limitations stated |

Bands: [How Assessment Works](../policies/assessment-format.md#6-capstone-rubric).

---

## Starter files

| File | Use |
| --- | --- |
| [`mixed.log`](../assets/assessments/security-automation/mixed.log) | 30 lines: syslog, CSV and JSONL, three of which do not parse |
| [`iocs.csv`](../assets/assessments/security-automation/iocs.csv) | Eight indicators with verdict, confidence, source and first-seen date |
| [`SHA256SUMS.json`](../assets/assessments/security-automation/SHA256SUMS.json) | Verify before use |
| [`normalise_logs.py`](../assets/assessments/reference/automation/normalise_logs.py) | Reference tool — **open only after your own attempt** |
| [`summary.json`](../assets/assessments/reference/automation/summary.json) | Reference output, for comparison after submission |

The [reference solution](reference-solutions.md#capstone-6-security-automation) reports 27 normalised events, 3
skipped lines and 8 aggregated findings, with exit code 0.

---

## Suggested extensions

- Add a `--since` filter and a `--format csv` output, with tests.
- Add a local mock API with token authentication, retry with jitter, and a `429` fixture.
- Add a second enrichment source (a local asset register) and resolve conflicts in precedence.
- Package the tool with a `pyproject.toml`, console entry point, and a GitHub Actions test workflow.

---

## Common pitfalls

- **Crashing on the first bad line.** The corpus contains malformed records for a reason.
- **Silent success.** If three lines failed and the exit code is 0, a pipeline cannot tell.
- **Hard-coded tokens.** Even in "just a lab" code, it teaches the wrong habit and ends up in history.
- **Findings per event, not per behaviour.** Fifteen near-identical findings bury the eighth real one.
- **Enrichment by substring.** `203.0.113.4` matching `203.0.113.45` is a false attribution.
- **No tests for refusals.** The guardrail that is never tested is the one that silently stops guarding.
- **A README that describes the code.** Document usage, outputs and limits instead.

---

## Related

- [Capstone overview](index.md) · [Project Guide](../start-here/project-guide.md)
- [CYB-505 · Security Automation](../levels/level-5-advanced/05-security-automation/index.md)
- [Python `argparse` documentation](https://docs.python.org/3/library/argparse.html)

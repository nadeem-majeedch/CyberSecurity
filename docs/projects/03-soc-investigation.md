---
title: "Capstone 3 — SOC Investigation"
description: "Investigate a synthetic multi-host incident from endpoint, authentication and DNS data: build a corrected timeline, scope the compromise, and write the incident report."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-401, CYB-402, CYB-407]
estimated_minutes: 1200
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-401-01, LAB-407-02]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, soc, incident-response, timeline]
---

# Capstone 3 — SOC Investigation

**Route:** defensive investigation · **Effort:** ~20 hours over 2–3 weeks · **Marks:** 100

---

## Problem statement

> At 09:12 on 24 October, a finance user reports that files on the shared drive have been renamed and will not
> open. You are handed three data sources — endpoint and authentication events, a host inventory with clock
> information, and DNS query logs — and asked for a timeline, a scope, a root cause, and a report the incident
> commander can act on.

The data is synthetic. The reasoning is not: the same three sources, with the same imperfections, are what a
first responder actually receives.

---

## Learning outcomes

1. Establish what the evidence can and cannot show before drawing conclusions.
2. Correct host clock offsets and present a single, defensible timeline.
3. Correlate authentication, process and DNS events into one intrusion narrative.
4. Distinguish observed events from inferred ones, and label both.
5. Scope a compromise: which hosts, which accounts, what data.
6. Recommend containment, eradication and recovery in a defensible order.
7. Write an incident report with root cause, impact, limitations and lessons.

---

## Scope and constraints

| Item | Detail |
| --- | --- |
| In scope | The supplied dataset: `events.csv`, `hosts.csv`, `dns.csv` |
| Out of scope | Any live system, any real network, any external lookup that would identify a real organisation |
| Permitted | Local analysis with spreadsheets, Python, `jq`, `grep`, or a SIEM you run locally |
| Forbidden | Uploading the dataset to a third-party service; treating "the tool flagged it" as analysis |
| Time box | Suggested 4 hours data familiarisation, 8 hours analysis, 8 hours reporting |
| Deliverable | A timeline, an incident report, an evidence register and a detection recommendation |

The organisation, hosts, users and domains in the dataset are fictional. Domains use reserved example
namespaces and addresses come from documentation ranges.

---

## Prerequisites

- [CYB-401](../levels/level-4-defensive-operations/01-soc-operations/index.md) — triage and ATT&CK mapping
- [CYB-402](../levels/level-4-defensive-operations/02-endpoint-telemetry/index.md) — endpoint and auth telemetry
- [CYB-407](../levels/level-4-defensive-operations/07-incident-response/index.md) — IR phases and reporting
- Spreadsheet or Python skills sufficient to sort, join and summarise 26 rows

---

## Lab setup

1. Download the three files from
   [`soc-investigation/`](../assets/assessments/soc-investigation/events.csv) and the `SHA256SUMS.json` beside them.
2. Verify the hashes before opening anything; record the result. If a hash does not match, stop and re-download.
3. Copy the files into a working directory and make them read-only. Analyse the copies.
4. **Do not edit the originals.** Every artefact you produce is derived from them.
5. Optional: import the events into a local SIEM (Wazuh, Elastic, Splunk free) to practise queries. The
   assessment does not require it, and a spreadsheet is sufficient.

**Data dictionary**

| File | Rows | Fields |
| --- | --- | --- |
| `events.csv` | 26 | `ts_local`, `host`, `event_id`, `user`, `src_ip`, `process`, `parent`, `cmdline`, `outcome` |
| `hosts.csv` | 4 | `host`, `role`, `os`, `clock_offset_seconds`, `notes` |
| `dns.csv` | 9 | `ts_local`, `host`, `query`, `qtype`, `answer` |

`clock_offset_seconds` is positive when the host clock is **ahead** of UTC. One host is offset; its event
timestamps are local and must be corrected before they are compared with the others.

---

## Required tasks

| # | Task | Output |
| --- | --- | --- |
| 1 | Data audit: sources, time ranges, fields, known gaps, hash verification | `01-data-audit.md` |
| 2 | Clock correction: identify offset hosts, method, corrected examples | `02-clock.md` |
| 3 | Timeline of at least ten events across three sources, UTC, with confidence | `03-timeline.csv` |
| 4 | Intrusion narrative linking initial access to impact, with gaps marked | `04-narrative.md` |
| 5 | Scope: hosts, accounts, data affected, and what you could not determine | `05-scope.md` |
| 6 | ATT&CK mapping for four or more observed behaviours, with the evidence for each | `06-attack.md` |
| 7 | Containment, eradication and recovery actions, in order, with rationale | `07-response.md` |
| 8 | Two detection recommendations: data source, observable, blind spot | `08-detections.md` |
| 9 | Incident report with root cause, impact, timeline, actions, lessons and limitations | `09-report.md` |
| 10 | Evidence register with hashes of inputs and derived artefacts | `evidence/register.csv` |

---

## Expected artefacts

```text
capstone-soc/
├── README.md
├── 01-data-audit.md
├── 02-clock.md
├── 03-timeline.csv          # ts_utc, source, host, actor, event, confidence
├── 04-narrative.md
├── 05-scope.md
├── 06-attack.md
├── 07-response.md
├── 08-detections.md
├── 09-report.md
└── evidence/
    ├── register.csv
    └── queries/             # reproducible filters or scripts
```

---

## Testing and validation

| Check | Standard |
| --- | --- |
| Hash verification | Recorded before analysis; originals unchanged |
| Clock correction | Every timeline row can be recomputed from `ts_local` and the recorded offset |
| Timeline completeness | At least ten events, three sources, no event outside the data |
| Confidence labels | Observed and inferred clearly distinguished |
| Scope claims | Each host or account in scope has at least one supporting event |
| Response order | Evidence preservation before remediation, with the reason stated |
| Detection quality | Names a data source and an observable, and states what it would miss |
| Reproducibility | Queries or scripts included so a reviewer can regenerate the timeline |

A timeline that cannot be regenerated from the scripts and inputs is treated as narrative, not evidence.

---

## Security and ethical requirements

- The dataset is synthetic, but treat it as sensitive: it describes an incident.
- Do not upload it to external services, including AI assistants that retain data. Local analysis only.
- Do not attempt to resolve the domains or contact the addresses in the data.
- Do not name a real organisation, person, or product as the victim. The scenario is fictional; keep it that way.
- If you present the work publicly, state that the data is synthetic and mark it clearly.

---

## Submission checklist

- [ ] Hashes verified and recorded before analysis
- [ ] Data audit with sources, ranges and gaps
- [ ] Clock correction method and corrected examples
- [ ] Timeline of ten or more events, UTC, sourced, confidence-labelled
- [ ] Narrative with gaps marked
- [ ] Scope with supporting evidence per host and account
- [ ] Four or more ATT&CK mappings with evidence
- [ ] Response plan in order, with rationale
- [ ] Two detections with data source, observable and blind spot
- [ ] Report with root cause, impact, limitations and lessons
- [ ] Evidence register and reproducible queries

---

## Rubric — 100 marks

| Criterion | Marks | What earns full marks |
| --- | --- | --- |
| Triage and data audit | 10 | Sources, ranges and gaps established before conclusions; hashes verified |
| Timeline construction | 20 | Clock offset corrected; ten or more events; UTC; confidence per row; gaps explicit |
| Correlation and analysis | 20 | Endpoint, authentication and DNS evidence joined into one narrative; alternatives considered |
| Scope determination | 15 | Hosts and accounts supported by evidence; unknowns stated rather than guessed |
| Response recommendations | 15 | Order justified; evidence preserved; containment proportionate; recovery verifiable |
| Incident report | 15 | Root cause distinguished from contributing factors; impact quantified where possible |
| Evidence handling and conduct | 5 | Originals untouched; synthetic data handled responsibly; limits stated |

Bands: [How Assessment Works](../policies/assessment-format.md#6-capstone-rubric).

---

## Starter files

| File | Use |
| --- | --- |
| [`events.csv`](../assets/assessments/soc-investigation/events.csv) | 26 endpoint and authentication events |
| [`hosts.csv`](../assets/assessments/soc-investigation/hosts.csv) | Host roles and clock offsets |
| [`dns.csv`](../assets/assessments/soc-investigation/dns.csv) | Nine DNS queries, including repeats worth examining |
| [`SHA256SUMS.json`](../assets/assessments/soc-investigation/SHA256SUMS.json) | Integrity values to verify before analysis |
| [`soc_analysis.py`](../assets/assessments/reference/soc_analysis.py) | Reference script — **open only after your own attempt** |

The [reference solution](reference-solutions.md#capstone-3-soc-investigation) gives the corrected timeline, the
narrative and the marking commentary.

---

## Suggested extensions

- Rebuild the timeline in a local SIEM and write the correlation searches.
- Add a fourth source (proxy logs) that you generate yourself, consistent with the existing events.
- Produce a 5-minute incident-commander briefing from the report, then have someone challenge it.
- Write a Sigma rule for the persistence mechanism and test it against the dataset.

---

## Common pitfalls

- **Timeline without correction.** FS-01's events appear seven minutes late until the offset is applied; the
  causal order breaks silently.
- **Confusing initial access with root cause.** "The user opened a document" is a mechanism, not the reason the
  organisation was exposed.
- **Scoping by guess.** Naming every host "potentially compromised" is not scoping.
- **Containment first, evidence never.** Isolating is right; destroying volatile evidence is not.
- **Report without limitations.** The dataset cannot show what happened on hosts it does not cover.
- **Treating a DNS repeat as proof.** Regularity is evidence, not conclusion.

---

## Related

- [Capstone overview](index.md) · [Project Guide](../start-here/project-guide.md)
- [CYB-407 · Incident Response](../levels/level-4-defensive-operations/07-incident-response/index.md)
- [Assessment Report Template](../policies/assessment-report-template.md)

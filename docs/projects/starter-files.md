---
title: "Starter Files and Datasets"
description: "Every starter file used by the six capstones, with size, purpose and SHA-256 values for integrity checking."
module_code: CYB-508
level: 5
kind: reference
prerequisites: []
estimated_minutes: 10
difficulty: intermediate
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, data, starter-files]
---

# Starter Files and Datasets

All data here is **synthetic**. Hosts, users, domains and addresses are fictional; addresses come from
documentation ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`), and domains use reserved example
names.

Download a file, verify its hash, then work on a copy. If a hash does not match, re-download rather than
proceeding — a changed dataset makes every conclusion suspect.

```bash
sha256sum events.csv          # Linux
shasum -a 256 events.csv      # macOS
Get-FileHash events.csv -Algorithm SHA256   # PowerShell
```

---

## SOC investigation

| File | Size | What it contains | SHA-256 |
| --- | --- | --- | --- |
| [`events.csv`](../assets/assessments/soc-investigation/events.csv) | 26 rows | Endpoint and authentication events: `ts_local`, `host`, `event_id`, `user`, `src_ip`, `process`, `parent`, `cmdline`, `outcome` | `a711f7ab…ae37` |
| [`hosts.csv`](../assets/assessments/soc-investigation/hosts.csv) | 4 rows | Host role, OS, clock offset in seconds (positive = clock ahead of UTC) | `938f404f…0279` |
| [`dns.csv`](../assets/assessments/soc-investigation/dns.csv) | 9 rows | DNS queries with type and answer | `c93c2fe3…e766` |
| [`SHA256SUMS.json`](../assets/assessments/soc-investigation/SHA256SUMS.json) | — | Machine-readable hashes | — |

Full values:

```text
events.csv   a711f7abedab29d3994e396782eee7b0d56d28a3d7bc1b95c31e70affc4aae37
hosts.csv    938f404f248bdd97cffc1401cecf11acd1cff27d73c6c345ba489f5b4a480279
dns.csv      c93c2fe3f254db656f265822afc3a78ddb50c1f46a26517ac61dc94cb6fde766
```

**Note:** the dataset covers one hour; one host's clock is offset. The offset is recorded explicitly in
`hosts.csv` — detecting it is not the puzzle, applying it consistently is.

---

## Threat detection

| File | Size | What it contains | SHA-256 |
| --- | --- | --- | --- |
| [`events.jsonl`](../assets/assessments/threat-detection/events.jsonl) | 43 events | Process-creation events: `id`, `ts`, `host`, `user`, `process`, `parent`, `cmdline`, `event_type`, `dest_ip` | `f5c1d3b1…b696` |
| [`labels.csv`](../assets/assessments/threat-detection/labels.csv) | 43 rows | Ground truth: `id`, `label` (malicious/benign), `note` | `aa153451…8712` |

Full values:

```text
events.jsonl  f5c1d3b1e47a7512f84c3e1d1924712847425d562ce563d450172335575eb696
labels.csv    aa1534513257ed72a1edc8d07ed1be5a9428f47d83f1fd521b20878816c38712
```

`labels.csv` is for scoring only. Reading it before writing rules turns detection engineering into curve fitting.

---

## Security automation

| File | Size | What it contains | SHA-256 |
| --- | --- | --- | --- |
| [`mixed.log`](../assets/assessments/security-automation/mixed.log) | 30 lines | Syslog, CSV and JSONL records, plus three that do not parse | `f1e0b1d6…92c5` |
| [`iocs.csv`](../assets/assessments/security-automation/iocs.csv) | 8 indicators | `indicator`, `type`, `verdict`, `confidence`, `source`, `first_seen` | `c42d47d3…61ce` |

Full values:

```text
mixed.log  f1e0b1d6ae4fe5840ad903124baf0c932d9de3d44f88b248a09d7a79099092c5
iocs.csv   c42d47d3b8527748001690e9f880c70cb7605e3d9a2a29c64b3ea566e98c61ce
```

---

## Templates

| File | Use | SHA-256 |
| --- | --- | --- |
| [`asset-register.csv`](../assets/assessments/starters/asset-register.csv) | Network assessment host inventory | `753bcb07…1f12` |
| [`hardening-checklist.csv`](../assets/assessments/starters/hardening-checklist.csv) | Twelve candidate Linux controls with CIS references | `a6c7c8d9…6e2f` |
| [`findings-register.csv`](../assets/assessments/starters/findings-register.csv) | Findings table for web or network work | `95582c25…f830` |

---

## Reference implementations

These are **solutions**, not starters. Each page says what it measured. Download them only after making your own
attempt.

| File | Purpose |
| --- | --- |
| [`soc_analysis.py`](../assets/assessments/reference/soc_analysis.py) | Clock correction, timeline, flagging |
| [`run_detections.py`](../assets/assessments/reference/detection/run_detections.py) | Sigma-subset evaluator with TP/FP/FN measurement |
| [`rules/`](../assets/assessments/reference/detection/rules/office-spawns-powershell.yml) | Four Sigma rules |
| [`normalise_logs.py`](../assets/assessments/reference/automation/normalise_logs.py) | Three-format normaliser, enrichment, findings |
| [`summary.json`](../assets/assessments/reference/automation/summary.json) | Measured output from the reference tool |

---

## Reproducing the reference runs

```bash
# SOC timeline (from the folder holding events.csv, hosts.csv, dns.csv)
python soc_analysis.py --data . --out timeline.md

# Detection tests (from the folder holding events.jsonl, labels.csv and rules/)
python run_detections.py --data . --rules rules

# Automation (from the folder holding mixed.log and iocs.csv)
python normalise_logs.py --log mixed.log --iocs iocs.csv --out out
```

Requires Python 3.10+ and `pyyaml` for the detection harness. Everything else is standard library.

---

## Related

- [Capstone overview](index.md) · [Reference solutions](reference-solutions.md)
- [Safety Policy](../policies/safety-policy.md) — handling rules that still apply to synthetic incident data

---
title: "LAB-401-03 · Write a Threat-Intelligence Brief"
description: "Turn a vendor report into a one-page brief: assessed indicators, actions, ATT&CK mapping and what would change the assessment."
module_code: CYB-401
level: 4
kind: lab
prerequisites: [CYB-401]
estimated_minutes: 120
difficulty: intermediate
safety: local-only
lab_ids: [LAB-401-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [threat-intelligence, ioc, confidence, tlp, reporting]
---

# LAB-401-03 · Write a Threat-Intelligence Brief

## Scenario and background

A sector information-sharing group sends your team a two-page report about a ransomware operator. It contains
fourteen indicators, four described behaviours, and no confidence language at all. Your manager forwards it with the
message: *"Can we block these?"*

The correct answer is not "yes". It is a brief that says which indicators are worth blocking, which are worth
hunting, which are too old or too generic to act on, and which behaviours you could detect regardless of the
indicators.

The report below is **fictional**. The actor name, domains, addresses, hashes and email addresses are invented for
this exercise, and the addresses come from documentation ranges.

## Learning objectives

By the end of this lab you can:

1. Classify indicators by type and assess each for confidence, age, and actionability.
2. Choose block, hunt, or monitor for each, with a stated reason.
3. Map the described behaviours to ATT&CK and propose detections that do not depend on indicators.
4. Mark a product correctly under TLP 2.0.
5. State what evidence would change your assessment.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python 3 | 3.10+ | Optional, for the indicator table |
| A text editor | — | Brief and tables |
| A browser | current | Public ATT&CK documentation only |

!!! warning "Authorized scope — read before you begin"
    **What this lab uses:** a fictional report you write to a file, and public ATT&CK documentation.
    **What it must not do:** resolve, request, or block any indicator. They are reserved names and documentation
    addresses; a lookup is either meaningless or reaches an unrelated real host.

    **Defang every indicator in your written work** so a reader cannot click it accidentally: `example[.]test`,
    `hxxps://`, `192[.]0[.]2[.]10`.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The fictional actor *SANDSTORM-4100* is described as financially motivated, targeting file servers, and using
phishing with an archive attachment, a scheduled task for persistence, and DNS for exfiltration. Some indicators in
the report are strong, some are weak, and one is almost certainly a false positive generator. Deciding which is
which is the exercise.

## Environment

No hosts required. All work happens in one directory.

## Before you start

```bash
mkdir -p ~/lab/level-4/lab-401-03/evidence
cd ~/lab/level-4/lab-401-03
cat > evidence/vendor-report.md <<'REPORT'
# SANDSTORM-4100 — sector advisory (FICTIONAL, for training only)

## Summary
SANDSTORM-4100 is a financially motivated operator observed targeting file servers in the education
sector. The group gains access through phishing emails containing an archive attachment, establishes
persistence with a scheduled task, and exfiltrates data over DNS before deploying ransomware.

## Observed behaviours
1. Phishing email with a ZIP attachment containing a shortcut (.lnk) file.
2. A scheduled task named "OneDriveSync" created shortly after user logon.
3. PowerShell with a base64-encoded command line.
4. High-volume DNS queries with long, random-looking labels.

## Indicators
| Type | Value | First seen | Source |
| --- | --- | --- | --- |
| Domain | cdn-update.example.test | 2026-10-20 | vendor A |
| Domain | sync.example.test | 2026-10-21 | vendor A, vendor B |
| Domain | files-share.example.test | 2025-08-02 | vendor A |
| IP | 203.0.113.55 | 2026-10-20 | vendor A |
| IP | 198.51.100.77 | 2025-09-14 | vendor A |
| URL | hxxps://cdn-update[.]example[.]test/gate.php | 2026-10-20 | vendor A |
| SHA-256 | 3f9a…c21e (64 hex chars, synthetic) | 2026-10-19 | vendor A |
| SHA-256 | 8b41…77aa (64 hex chars, synthetic) | 2024-11-03 | vendor B |
| Email | billing@sandstorm-relay.example.test | 2026-10-18 | vendor B |
| User-Agent | Mozilla/5.0 (Windows NT 10.0) curl/8.4.0 | 2026-10-20 | vendor A |
| Registry key | HKCU\Software\Microsoft\Windows\CurrentVersion\Run\OneDriveSync | 2026-10-21 | vendor A |
| Filename pattern | invoice_<6 digits>.lnk | 2026-10-19 | vendor A, vendor B |
| TLS JA3 | 51c64c77e60f3980eea90869b68c58a8 | 2026-10-20 | vendor B |
| Bitcoin address | bc1q… (synthetic) | 2026-10-22 | vendor B |

## Confidence
[The vendor provided no confidence ratings, no sourcing beyond the table above, and no sighting context.]
REPORT
wc -l evidence/vendor-report.md
```

**Expected:** the report is on disk. Read it once fully before starting the table.

## Procedure

### 1. Build the indicator table

`evidence/ioc-table.csv` with these columns:

```csv
indicator,type,age_days,confidence,confidence_basis,action,reason,expires
```

Rules for filling it:

- **age_days** is calculated from the first-seen date to 2026-10-29. Do the arithmetic; an indicator's half-life is
  part of its value.
- **confidence** is `high`, `moderate`, or `low`. Every rating needs a **basis**: "two independent vendors",
  "single vendor, no first-party sighting", "generic value used by many benign tools".
- **action** is `block`, `hunt`, or `monitor`. Not everything gets a block.
- **expires** is a date. Indicators rot; a block with no expiry is technical debt.

Three of the fourteen deserve particular care. Decide for yourself which; the pattern to watch for is an indicator
whose value is shared with legitimate software, or whose age exceeds the campaign's plausible lifetime.

### 2. Sanity-check the indicator set

```bash
# Count by action, once the table is written
awk -F',' 'NR>1 {print $6}' evidence/ioc-table.csv | sort | uniq -c
```

Ask three questions of your own table:

1. If you blocked everything marked `block`, what legitimate traffic would break? Name a specific example.
2. Which indicator would produce the most false positives if blocked, and why?
3. Which indicator has the longest useful life, and which expires first?

Write the answers in `evidence/indicator-analysis.md`, one short paragraph each.

### 3. Map the behaviours, not the indicators

Indicators expire; behaviours do not. Map the four observed behaviours to ATT&CK (verify IDs at
attack.mitre.org, current version v20.0 at the time of writing) and fill `evidence/detections.md`:

| Behaviour | ATT&CK technique | Data source | Detection idea independent of IOCs | False-positive risk |
| --- | --- | --- | --- | --- |
| ZIP containing .lnk | | | | |
| Scheduled task after logon | | | | |
| Encoded PowerShell | | | | |
| High-volume random DNS labels | | | | |

**Why this table matters more than the indicator list:** the actor can change every domain tomorrow. The behaviours
are expensive to change.

### 4. Write the one-page brief

`evidence/brief.md`, maximum 500 words, in this order:

1. **Bottom line** — three sentences: what the threat is, whether it applies to us, what we should do this week.
2. **Assessment** — which behaviours are credible and why, with confidence language.
3. **Recommended actions** — a table of at most six actions, each with an owner-shaped verb (block, hunt, add
   detection, verify backup, brief staff) and a time frame.
4. **What would change this assessment** — two specific observations that would raise or lower your confidence.
5. **Handling** — the TLP marking and why.

**Expected:** a brief a manager can act on without reading the vendor report.

### 5. Mark and share correctly

Add a TLP marking to the brief. Choose between TLP:CLEAR, GREEN, AMBER, AMBER+STRICT, and RED, and justify it in one
sentence given that the source is a sector sharing group and the content includes indicators.

Then write `evidence/sharing-note.md`: what you would share back with the group, and what you would remove first.

### 6. Self-review against the four questions

Before you finish, answer these in `evidence/self-review.md`:

1. Did every indicator get a confidence **basis**, not just a rating?
2. Is there at least one indicator you deliberately did **not** block? Why?
3. Does every recommended action have a time frame?
4. Could an engineer implement your top detection from the table alone?

## Evidence to collect

- `evidence/vendor-report.md` — the fictional source.
- `evidence/ioc-table.csv` — fourteen rows, all columns filled.
- `evidence/indicator-analysis.md` — the three answers.
- `evidence/detections.md` — four behaviours mapped with detection ideas.
- `evidence/brief.md` — the 500-word brief with TLP marking.
- `evidence/sharing-note.md`, `evidence/self-review.md`.

## Verification

- [ ] Fourteen indicators assessed, with age calculated rather than estimated.
- [ ] Every confidence rating has a stated basis.
- [ ] At least three indicators are marked `hunt` or `monitor` rather than `block`.
- [ ] Every indicator has an expiry date.
- [ ] Four behaviours mapped to verified ATT&CK IDs, with a detection idea that does not depend on an IOC.
- [ ] The brief is under 500 words and includes what would change the assessment.
- [ ] TLP marking present and justified.

## Teardown and reset

Nothing to tear down. Keep `evidence/` — the brief format is reused for incident reporting in CYB-407.

## Reflection

1. Two vendors reporting the same domain is stronger evidence than one vendor reporting it twice. Why?
2. Which indicator in the report is most likely to be a false-positive generator, and what makes it generic?
3. Your brief recommends hunting rather than blocking for a domain. What does the hunt look for, and what would make
   you block it afterwards?
4. If the actor changes domains weekly, what is the half-life of your brief, and what should you do about that?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Indicator assessment | Ratings without basis | Confidence with basis | Basis plus age analysis and expiry dates |
| Action choice | Everything blocked | Mix of block and hunt | Every action justified by cost of false positive |
| Behaviour mapping | Techniques guessed | Four mapped and verified | Mapped with IOC-independent detection ideas and FP risk |
| Brief | Summary only | Structured and actionable | Actionable, confidence-aware, with what would change the assessment |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Everything looks blockable | No false-positive cost considered | Ask which legitimate software uses the same value |
| Age arithmetic inconsistent | Mixed date formats | Normalise to ISO dates before subtracting |
| Technique ID invalid | Remembered rather than looked up | Verify on attack.mitre.org and copy the official name |
| Brief over 500 words | Including the whole vendor report | Move detail to the detection table; the brief is a decision document |

## References

1. FIRST — Traffic Light Protocol 2.0. <https://www.first.org/tlp/> Accessed 2026-10-29.
2. MITRE ATT&CK v20.0. <https://attack.mitre.org/resources/versions/> Accessed 2026-10-29.
3. CISA — Traffic Light Protocol (TLP) definitions. Accessed 2026-10-29.
4. David Bianco — The Pyramid of Pain. Accessed 2026-10-29.

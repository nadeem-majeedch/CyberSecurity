---
title: "Level 4 Integrated Assessment — Detect, Contain, Report"
description: "A four-hour defensive assessment: investigate a scripted intrusion from synthetic logs, build a timeline, contain it without destroying evidence, and write the incident report."
module_code: ASM-L4A
level: 4
kind: assessment
prerequisites: [CYB-401, CYB-404, CYB-407]
estimated_minutes: 330
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-401-01, LAB-407-02, LAB-407-03]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, level-4, incident-response, detection, forensics]
---

# Level 4 Integrated Assessment

**Part A:** practical, 4 hours, 70 marks. **Part B:** written post-incident review, 90 minutes, 30 marks.

This is the closest the course comes to a real shift: a queue, incomplete evidence, a clock that is wrong, and
a decision about containment that you have to defend afterwards.

---

## The brief

> *At 09:12 a user reports that files on the shared drive have been renamed and will not open. You are the only
> analyst on shift. The environment is the isolated lab from Level 4; the evidence is the synthetic data pack
> from [LAB-407-02](../levels/level-4-defensive-operations/07-incident-response/lab-02-timeline.md) and
> [LAB-407-03](../levels/level-4-defensive-operations/07-incident-response/lab-03-ransomware.md), plus the alert
> queue from [LAB-401-01](../levels/level-4-defensive-operations/01-soc-operations/lab-01-alert-triage.md).*

**Environment options.** Either (a) use the supplied synthetic logs and captures without a live host, or (b) run
the scripted simulation in your isolated lab and capture the telemetry yourself. Option (b) earns no extra
marks; it is harder to control and easier to lose evidence in. Choose (a) unless your instructor says otherwise.

**Rules.** The lab is isolated; no real organisational data; no live malware. The "ransomware" is a harmless
script that renames files and writes a marker — never run anything else. Do not power off hosts: containment is
network isolation.

---

## Part A — Practical (70 marks)

**A1. Triage the queue (15 marks).** From the alert queue, decide which alerts are related to the reported
incident. Record for each: alert, disposition (escalate / monitor / close), reason, and the evidence you used.
At least one alert should be correctly closed as unrelated — say why.

**A2. Build the timeline (20 marks).** Produce a minimum eight-event timeline from at least three sources
(endpoint log, authentication log, network capture or DNS log). Requirements:

- UTC for every entry, with the original timestamp and source host recorded;
- one host's clock is offset — detect it, correct it, and state the correction;
- each event carries a confidence label (observed / inferred);
- the chain from initial access to impact is explicit, with gaps marked as gaps.

**A3. Detection (10 marks).** Name two behaviours from the timeline that a detection should cover, and for each:
the data source, the observable, and one reason the rule might miss the behaviour.

**A4. Containment (15 marks).** Contain the incident in the lab (or describe the exact actions if using option
(a)): isolate the host from the network without powering it off, disable the account and revoke sessions, and
acquire or preserve the evidence in the correct order. Record each action with time and rationale.

**A5. Report and evidence register (10 marks).** Incident report using the structure in
[CYB-407](../levels/level-4-defensive-operations/07-incident-response/index.md), plus an evidence register with
hashes and custody entries.

### Artefacts

```text
level-4-assessment/
├── README.md
├── 01-triage.md
├── 02-timeline.csv          # ts_utc, source, host, event, confidence
├── 03-detections.md
├── 04-containment.md
├── 05-incident-report.md
└── evidence/                # logs, captures, hashes
```

---

## Part B — Written post-incident review (30 marks, 90 minutes)

**W1 (10 marks).** Justify your timeline's treatment of the clock offset. What would have changed in your
conclusions if you had not corrected it?

**W2 (8 marks).** Choose one detection you proposed. Explain what it would catch, what it would miss, and one
exception you would refuse to add — with the reason.

**W3 (7 marks).** Justify your containment order. Name one action you deliberately did not take, and what it would
have cost.

**W4 (5 marks).** State the root cause and one contributing factor, then two changes with an owner and a
verification step for each.

---

## Marking

### Part A (70)

| Task | Marks | Full marks requires |
| --- | --- | --- |
| A1 Triage | 15 | Related alerts correctly linked; one unrelated alert closed with reasoning |
| A2 Timeline | 20 | UTC, source, confidence per event; offset detected and corrected; gaps stated |
| A3 Detection | 10 | Two behaviours with data source, observable, and a stated blind spot |
| A4 Containment | 15 | Isolation without power-off; account and sessions handled; evidence preserved before remediation |
| A5 Report | 10 | Root cause, scope, impact, recovery, lessons; evidence register with hashes |

### Part B (30)

| Criterion | Marks | Descriptor |
| --- | --- | --- |
| Timeline reasoning | 10 | Offset method, conversion, and the counterfactual |
| Detection reasoning | 8 | Coverage and blind spot named; refused exception justified |
| Containment judgement | 7 | Order defended; rejected action and its cost |
| Learning | 5 | Root cause vs contributing factor; verifiable changes |

### Domain weights

| Domain | Weight |
| --- | --- |
| Detection | 30% |
| Incident response | 30% |
| Forensics | 20% |
| Hardening and prevention | 20% |

Safety gate: if you power off a host, delete "infected" files, or run anything beyond the supplied simulation,
the assessment is void.

---

## Self-marking

1. Check the timeline against the raw sources yourself: pick three rows at random and re-derive them.
2. Score A4 by asking whether a reviewer could tell, from your notes, what was preserved and in what order.
3. Compare with the [key](level-4-key.md#level-4-integrated-assessment-model-answers) after marking.
4. Note which domain lost most marks; that is the module to revisit.

---

## Common pitfalls

- **Timeline without sources.** An entry with no source cannot be defended or corrected.
- **Treating inferred events as observed.** If you reconstructed a step, say so.
- **Containment as first action.** Isolating before capturing memory is sometimes necessary, but say why.
- **A report that stops at "the user clicked a link".** That is initial access, not root cause.
- **Lessons learned as intentions.** "Improve security awareness" cannot be verified; a control with an owner
  and a test can.

---

## Submission checklist

- [ ] Triage table with dispositions and reasons
- [ ] Timeline of eight or more events, UTC, sourced, confidence-labelled
- [ ] Clock offset identified with the correction applied
- [ ] Two detections with data source, observable and blind spot
- [ ] Containment log in order, with rationale
- [ ] Incident report and evidence register with hashes
- [ ] No host powered off; no data destroyed

---

## Related

- [Level 4 quiz](level-4-quiz.md) · [Answer key](level-4-key.md)
- [CYB-407 · Incident Response](../levels/level-4-defensive-operations/07-incident-response/index.md)
- [Assessment Report Template](../policies/assessment-report-template.md)
- [Level 5](../levels/level-5.md)

---
title: "Level 3 Integrated Assessment — Assess, Fix, Retest"
description: "A three-hour assessment of a local vulnerable application plus a fix with tests, and a ninety-minute written justification of root causes and crypto choices."
module_code: ASM-L3A
level: 3
kind: assessment
prerequisites: [CYB-302, CYB-303, CYB-307, CYB-308]
estimated_minutes: 270
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-302-01, LAB-303-02, LAB-307-03]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, level-3, web-security, remediation, testing]
---

# Level 3 Integrated Assessment

**Part A:** practical, 3 hours, 70 marks. **Part B:** written, 90 minutes, 30 marks.

The practical asks for something the labs teach separately: find flaws, **fix one in code**, and prove the fix
without breaking the feature. A report full of findings with no code change cannot pass the level, because
Level 3 is about being able to build the safe version, not only recognise the unsafe one.

---

## The brief

> *A student society runs a small web application for event sign-ups. It has three user accounts and an admin
> page. You have the source, a local container, and permission to test only that container. Produce an
> assessment, fix the highest-risk flaw you can fix in the time available, and demonstrate that the fix works.*

**Environment:** the sample application from
[CYB-301](../levels/level-3-applications/01-web-architecture-and-http/lab-01-web-lab-setup.md), or Juice Shop
for the assessment portion. **Fixes must be made to the course sample application**, which ships with
deliberate flaws; Juice Shop is not designed to be modified for this task.

**Rules:** localhost or the isolated lab only. No real accounts, no real data, no testing of the public internet.
Do not expose the container on a bridged interface. Record the container's state before you begin.

---

## Part A — Practical (70 marks)

**A1. Map the application (10 marks).** Identify endpoints, authentication mechanism, session handling and the
objects each endpoint acts on. Produce a short table: endpoint, method, authentication required, object acted
on, authorization check present (yes/no/unknown).

**A2. Find and validate at least four flaws (25 marks).** At least one must be an access-control flaw and one
an injection flaw. For each: the request or input, the response or observation, the class, and why it matters.
Unvalidated scanner output does not count.

**A3. Fix the highest-risk flaw you can fix (20 marks).** Change the code. Requirements:

- the change addresses the cause, not the symptom;
- the vulnerable version is kept (branch, copy or patch file) so the test can be run against it;
- a test exists that fails on the vulnerable version and passes on the fixed one;
- the intended feature still works, demonstrated with a request.

**A4. Retest and record (10 marks).** Re-run the original attack against the fixed application, capture the new
response, and state what the new behaviour proves and what it does not.

**A5. Evidence package (5 marks).** Requests, responses, test output, diff, and a README mapping artefacts to
tasks.

### Artefacts

```text
level-3-assessment/
├── README.md
├── 01-endpoint-map.md
├── 02-findings.md
├── 03-fix/                # diff, patched files, test, run instructions
├── 04-retest.md
└── evidence/              # raw requests/responses, screenshots, test output
```

---

## Part B — Written justification (30 marks, 90 minutes)

**B1 (12 marks).** For each finding, state the root cause in terms of the interpreter that received the data
and the check that was missing. Cite file and line where you can. "Insufficient validation" earns nothing.

**B2 (8 marks).** Choose one finding you fixed and one you did not. Explain why the second was not fixed, and
whether your report presents it as a fix, a mitigation, or an accepted risk.

**B3 (5 marks).** The application stores passwords with MD5. State what you would replace it with, why, and how
you would migrate existing accounts without locking users out or leaving weak hashes valid.

**B4 (5 marks).** Your fix passes its test. State two things the test does not prove, and one additional check
you would run before calling the finding closed.

---

## Marking

### Part A (70)

| Task | Marks | Full marks requires |
| --- | --- | --- |
| A1 Map | 10 | Authorization state recorded per endpoint, including "unknown" where honestly unknown |
| A2 Findings | 25 | Four or more validated, including access control and injection; evidence per finding |
| A3 Fix | 20 | Cause addressed; vulnerable version preserved; failing-then-passing test; feature still works |
| A4 Retest | 10 | Original attack re-run; new response; claim limited to what was shown |
| A5 Evidence | 5 | Diff, requests, test output, README |

### Part B (30)

| Criterion | Marks | Descriptor |
| --- | --- | --- |
| Root-cause analysis | 12 | Mechanism named per finding; line references where possible |
| Fix, mitigation, acceptance | 8 | The three are distinguished correctly and the residual risk is stated |
| Cryptographic reasoning | 5 | Specific algorithm, parameters, migration path |
| Test limits | 5 | Says what the test cannot prove; proposes the missing check |

### Domain weights

| Domain | Weight |
| --- | --- |
| Web application security | 40% |
| Identity and access management | 20% |
| Cryptography in practice | 20% |
| Secure coding and remediation | 20% |

The safety gate applies. Testing anything beyond the local application — including a public site that hosts the
same software — voids the assessment.

---

## Self-marking

1. Run your own test against the vulnerable version. If it passes there, the test proves nothing.
2. Apply the removal test to the fix: remove one line of the change and state exactly what breaks.
3. Mark B1 by reading your root-cause sentences for a mechanism. If a sentence would still be true of a
   different vulnerability, it is too vague.
4. Compare with the [model finding set](level-3-key.md#level-3-integrated-assessment-model-answers) only after
   marking.

---

## Common pitfalls

- **Fixing the payload, not the sink.** Blocking `<script>` in the search box is a filter; encoding at output is
  a fix.
- **A test written after the fix, against the fixed code.** It will pass forever.
- **Breaking the feature to pass the test.** A login that rejects everything is secure and useless; demonstrate
  the legitimate path.
- **Claiming the finding closed** because the specific payload no longer works.
- **Report without code.** In this assessment, the diff is a marked artefact.

---

## Submission checklist

- [ ] Endpoint map with authorization state
- [ ] Four or more validated findings, with access control and injection represented
- [ ] Code change, diff, and preserved vulnerable version
- [ ] Test that fails before and passes after
- [ ] Retest evidence and a statement of what it proves
- [ ] Written answers B1–B4 in sentences
- [ ] No traffic outside the local application

---

## Related

- [Level 3 quiz](level-3-quiz.md) · [Answer key](level-3-key.md)
- [CYB-307 · Secure Coding, Dependencies and Remediation](../levels/level-3-applications/05-secure-coding-and-dependencies/index.md)
- [Assessment Report Template](../policies/assessment-report-template.md)
- [Level 4](../levels/level-4.md)

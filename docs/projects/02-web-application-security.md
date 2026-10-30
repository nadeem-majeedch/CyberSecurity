---
title: "Capstone 2 — Web Application Security"
description: "Assess a local training application, reproduce each flaw safely, fix the highest-risk ones in code, and prove the fixes with failing-then-passing tests."
module_code: CYB-508
level: 5
kind: assessment
prerequisites: [CYB-302, CYB-303, CYB-304, CYB-307, CYB-308]
estimated_minutes: 1440
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-302-01, LAB-303-02, LAB-307-03]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [capstone, web-security, remediation, testing]
---

# Capstone 2 — Web Application Security

**Route:** offensive assessment with remediation · **Effort:** ~24 hours over 3–4 weeks · **Marks:** 100

---

## Problem statement

> A student society's event-signup application is being prepared for a new term. It has three user accounts, an
> admin page, and source code you can read. The developer has asked for a security review **and** for help fixing
> what matters most before launch.

The differentiator in this capstone is the second half: a finding you cannot fix or verify is only half the work.
At least two fixes must be implemented, with tests that fail on the vulnerable code and pass on the fixed code.

---

## Learning outcomes

1. Map an application's endpoints, sessions and authorization model before testing it.
2. Find and validate flaws from the OWASP Top 10 in a local application without harming data.
3. Distinguish a fix from a mitigation, and place each correctly in a report.
4. Implement a remediation that addresses the cause, not the payload.
5. Write regression tests that demonstrate the vulnerability existed and is closed.
6. Retest and state precisely what the retest proves.
7. Write for two audiences: the developer who will change code, and the owner who funds it.

---

## Scope and constraints

| Item | Detail |
| --- | --- |
| In scope | The course sample application running in your lab container, its source, and its local database |
| Out of scope | Juice Shop (assessment practice only, not modifiable for this capstone), any public site, any real account, the host network |
| Permitted | Authenticated testing with the three lab accounts, local interception, source review, code changes in your own copy |
| Forbidden | Traffic to any public host, real credentials or data, denial of service, testing the app after exposing it on a bridged interface |
| Time box | Suggested 12 hours assessment, 8 hours remediation, 4 hours reporting |
| Data | Synthetic users and content only; the database may be reset from the seed |

**Hard constraint:** the application must stay bound to `127.0.0.1` (or the isolated lab segment). Exposing it to
your LAN or the internet is a scope violation, even briefly.

---

## Prerequisites

- [CYB-301](../levels/level-3-applications/01-web-architecture-and-http/index.md) — HTTP, sessions, browser model
- [CYB-302](../levels/level-3-applications/02-injection-and-xss/index.md) — injection and XSS
- [CYB-303](../levels/level-3-applications/03-access-control-and-authentication/index.md) — access control and auth
- [CYB-307](../levels/level-3-applications/05-secure-coding-and-dependencies/index.md) — secure coding and testing
- [CYB-308](../levels/level-3-applications/06-api-security/index.md) — API authorization

---

## Lab setup

1. Build the web lab from [LAB-301-01](../levels/level-3-applications/01-web-architecture-and-http/lab-01-web-lab-setup.md);
   confirm the container binds to `127.0.0.1`.
2. Copy the application source into a working directory and initialise Git, so your fixes are reviewable as diffs.
3. Create the three accounts, and record which role each has.
4. Seed the database and snapshot the container. Record the snapshot name.
5. Confirm you can reset to the snapshot; you will need it after destructive tests.
6. Set up Burp Suite Community Edition or use browser developer tools plus `curl`; either is acceptable.

---

## Required tasks

| # | Task | Output |
| --- | --- | --- |
| 1 | Endpoint map: route, method, auth required, object acted on, authorization check present | `01-endpoint-map.md` |
| 2 | Test plan covering authentication, session, access control, injection, file handling, API | `02-test-plan.md` |
| 3 | At least six validated findings across at least four classes | `03-findings.md` |
| 4 | Evidence per finding: request, response, account/role, timestamp | `evidence/` |
| 5 | Threat model for the signup flow with two STRIDE threats and mitigations | `04-threat-model.md` |
| 6 | Fix at least two flaws in code, preserving the vulnerable version in Git history | `fix/` |
| 7 | Regression tests that fail before and pass after each fix | `fix/tests/` |
| 8 | Retest log for each fix, including the legitimate feature still working | `05-retest.md` |
| 9 | Report: executive summary, findings, remediation, residual risk, limitations | `06-report.md` |

Minimum finding coverage: one access-control flaw, one injection flaw, one authentication or session flaw, and
one misconfiguration or dependency issue. File handling or SSRF may replace one of these if the application
supports it.

---

## Expected artefacts

```text
capstone-web/
├── README.md
├── 01-endpoint-map.md
├── 02-test-plan.md
├── 03-findings.md
├── 04-threat-model.md
├── 05-retest.md
├── 06-report.md
├── fix/
│   ├── patches/            # git diff per fix
│   ├── tests/              # regression tests
│   └── NOTES.md            # how to run the tests
└── evidence/
    ├── requests/
    └── responses/
```

---

## Testing and validation

| Check | Standard |
| --- | --- |
| Finding validity | Reproduced twice, from a reset database, with the request recorded |
| Safe reproduction | Minimum requests; no data deleted; no persistence; accounts used as documented |
| Fix quality | Cause addressed; diff readable; no unrelated changes |
| Regression test | Demonstrably fails on the vulnerable commit, passes on the fixed commit |
| Feature preservation | The legitimate use case is demonstrated after the fix |
| Retest honesty | States what the retest proves, and what it does not (e.g. one payload class only) |

Record the vulnerable commit hash and the fixed commit hash. A reviewer must be able to check out either and run
your test.

---

## Security and ethical requirements

- Local application only, bound to loopback or the isolated segment.
- Synthetic accounts; never real credentials, never real personal data.
- Do not use payloads that destroy data; if a test writes, reset from the snapshot afterwards.
- Do not publish a working exploit for a third-party application you do not own.
- If you find a real vulnerability in third-party software during this work, follow responsible disclosure, not
  publication.
- Cite every external source used, with an access date.

---

## Submission checklist

- [ ] Endpoint map with authorization state per route
- [ ] Test plan
- [ ] Six or more validated findings across four or more classes
- [ ] Evidence per finding, including account and timestamp
- [ ] Threat model with two STRIDE threats
- [ ] Two or more code fixes as diffs, vulnerable commit preserved
- [ ] Regression tests failing before and passing after
- [ ] Retest log with feature-preservation evidence
- [ ] Report with executive summary and limitations
- [ ] Container still bound to loopback; nothing exposed

---

## Rubric — 100 marks

| Criterion | Marks | What earns full marks |
| --- | --- | --- |
| Scope, method and test plan | 10 | Endpoint-driven plan; authorization states recorded; stack and limits named |
| Discovery and validation | 20 | Six or more real flaws across four classes; each reproduced and evidenced |
| Safe reproduction and evidence | 15 | Minimum-impact testing; requests and responses captured; data restored |
| Remediation in code | 20 | Cause addressed; two or more fixes; clean diffs; no feature regression |
| Regression testing | 10 | Tests fail before and pass after; test design explained |
| Reporting and communication | 15 | Developer-facing detail plus owner-facing summary; risk prioritised; residual risk |
| Ethics and professional conduct | 10 | Loopback only; synthetic data; disclosure discipline; limitations stated |

Bands: [How Assessment Works](../policies/assessment-format.md#6-capstone-rubric). Exposing the app or testing a
public target voids the submission.

---

## Starter files

| File | Use |
| --- | --- |
| [`findings-register.csv`](../assets/assessments/starters/findings-register.csv) | Findings table with OWASP references and retest columns |
| Course sample application | From [CYB-301](../levels/level-3-applications/01-web-architecture-and-http/lab-01-web-lab-setup.md) |
| [Assessment Report Template](../policies/assessment-report-template.md) | Report structure |
| [Level 3 model findings](../assessments/level-3-key.md#level-3-integrated-assessment-model-answers) | The *shape* of good findings, not answers to your app |

The [reference solution](reference-solutions.md#capstone-2-web-application-security) describes a complete
submission, including the two fixes and their tests.

---

## Suggested extensions

- Add a second identity provider or role and test the authorization matrix again.
- Write a Semgrep or CodeQL query that would have caught the flaw you fixed.
- Add security headers and a CSP, then measure what the CSP would and would not have blocked.
- Build a small API client that exercises the endpoints, and turn it into your regression suite.

---

## Common pitfalls

- **Blocklist fixes.** Stripping `<script>` or banning the payload is not remediation.
- **A test that only passes.** If it never failed on the vulnerable code, it proves nothing.
- **Breaking the feature.** A login that rejects every input is secure and useless.
- **Findings without accounts.** "An attacker could…" without the role you used is not reproducible.
- **Copying CVSS.** A reflected XSS in an admin-only page is not automatically High; state the reasoning.
- **Leaving the container exposed.** The commonest way this capstone is voided.

---

## Related

- [Capstone overview](index.md) · [Project Guide](../start-here/project-guide.md)
- [CYB-307 · Secure Coding, Dependencies and Remediation](../levels/level-3-applications/05-secure-coding-and-dependencies/index.md)
- [OWASP Top 10](https://owasp.org/Top10/)

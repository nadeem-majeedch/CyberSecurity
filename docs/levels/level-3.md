---
title: "Level 3 — Applications, Cryptography and Identity"
description: "Web application security, secure development, dependencies and APIs: six published modules, seventeen labs, two planned."
---

# Level 3 — Applications, Cryptography and Identity

**~68 guided hours published · 6 of 8 modules live · Prerequisite: Level 2**

!!! note "Status: partially published"
    Six modules are complete with lessons and labs: web architecture, injection and XSS, access control and
    authentication, file handling and SSRF, secure coding and dependencies, and API security.

    Two modules remain planned — **CYB-305 Applied Cryptography** and **CYB-306 Identity and Federation**. Their
    structure is defined in the [roadmap](../curriculum/roadmap.md); no lesson pages exist yet, and nothing below
    claims otherwise.

---

## What this level is about

Most breaches enter through an application, a credential, or an identity decision. This level teaches those three
surfaces properly.

The goal is not to memorise a list of vulnerabilities. It is to look at a request, a session, or a configuration
and reason about **what could go wrong, why, and what the correct construction is**. Every vulnerability you
reproduce, you also fix — in code, in configuration, or in design.

All testing is against intentionally vulnerable applications running in your own lab — OWASP Juice Shop, DVWA, and
small services you build yourself. Nothing here is aimed at a system you do not own.

---

## What you will be able to do

By the end of the published modules you can:

- Read an HTTP exchange — headers, cookies, tokens — and explain the trust decision each one represents.
- Reproduce and then remediate SQL injection, XSS, access-control, SSRF, and file-handling flaws.
- Audit an authentication and session design, and measure password-storage choices rather than guessing at them.
- Review a small codebase by taint analysis and cite findings by file and line.
- Inventory dependencies, triage advisories by reachability, and generate an SBOM.
- Test an API for object-, function- and property-level authorization failures, and specify the checks.
- Write a remediation table in which every fix is backed by a test that fails on the old code.

---

## Modules

| Code | Module | Hours | Labs | Status |
| --- | --- | --- | --- | --- |
| [CYB-301](level-3-applications/01-web-architecture-and-http/index.md) | Web Architecture and HTTP for Security | 8 | 3 | **Published** |
| [CYB-302](level-3-applications/02-injection-and-xss/index.md) | Injection and Cross-Site Scripting | 14 | 2 | **Published** |
| [CYB-303](level-3-applications/03-access-control-and-authentication/index.md) | Access Control, Authentication and Sessions | 12 | 3 | **Published** |
| [CYB-304](level-3-applications/04-file-handling-ssrf-misconfiguration/index.md) | File Handling, SSRF and Misconfiguration | 12 | 4 | **Published** |
| CYB-305 | Applied Cryptography | 14 | 3 (planned) | Planned |
| CYB-306 | Identity, Access Management and Federation | 12 | 2 (planned) | Planned |
| [CYB-307](level-3-applications/05-secure-coding-and-dependencies/index.md) | Secure Coding, Dependencies and Remediation | 12 | 3 | **Published** |
| [CYB-308](level-3-applications/06-api-security/index.md) | API Security | 10 | 2 | **Published** |
| CYB-309 | Level 3 Assessment | 6 | — | Planned |

Module codes follow the roadmap, which is why the published sequence runs 301–304 then 307–308. The gap is
deliberate and visible rather than hidden by renumbering.

---

## Labs at a glance

Seventeen labs, all against local targets. Full catalogue: [Labs](../labs/index.md).

| Lab | Title | Module |
| --- | --- | --- |
| LAB-301-01 | Build the Web Lab | CYB-301 |
| LAB-301-02 | Intercept and Annotate a Session | CYB-301 |
| LAB-301-03 | Evaluate Cookie and Session Attributes | CYB-301 |
| LAB-302-01 | SQL Injection and Its Fix | CYB-302 |
| LAB-302-02 | Reflected and Stored XSS | CYB-302 |
| LAB-303-01 | Insecure Login Workflow | CYB-303 |
| LAB-303-02 | Broken Access Control and IDOR | CYB-303 |
| LAB-303-03 | Cross-Site Request Forgery | CYB-303 |
| LAB-304-01 | File Upload Validation | CYB-304 |
| LAB-304-02 | Path Traversal and File Inclusion | CYB-304 |
| LAB-304-03 | Server-Side Request Forgery | CYB-304 |
| LAB-304-04 | Security Headers, TLS and Misconfiguration | CYB-304 |
| LAB-307-01 | Threat Model and Code Review | CYB-307 |
| LAB-307-02 | Vulnerable Dependencies | CYB-307 |
| LAB-307-03 | Fix, Test and Verify | CYB-307 |
| LAB-308-01 | API Authorization Failures | CYB-308 |
| LAB-308-02 | Mass Assignment and Rate Limiting | CYB-308 |

---

## How the level runs

**Lab environment.** Your Level 2 lab plus `lab-web`: an Ubuntu Server VM running OWASP Juice Shop
(`192.0.2.30:3000`) and DVWA (`192.0.2.30:4280`) in containers, bound to the lab address only, plus small Flask
services you write yourself and run on loopback. Pinned versions matter here — these applications change, and the
instructions are written against the releases named in each lab.

**Rule of the level:** every demonstration is paired with a fix, and every fix is paired with a test that fails on
the vulnerable version. A finding without a remediation is half the work, and it is the half clients pay for.

**Tools.** Burp Suite Community Edition 2026.10.1 or OWASP ZAP 2.17.0 (both free), browser devtools, `curl`,
`jq`, `sqlite3`, Python 3 with Flask and `pytest`, plus `pip-audit` and `cyclonedx-bom` for the supply-chain
module. Everything has a `curl` equivalent, so no lab depends on a GUI.

**Assessment.** Each module's labs are rubric-marked. The Level 3 assessment (CYB-309, planned) will ask you to
assess a local application end to end and defend your severity ratings — including the ones you decided were lower
than they first appeared.

---

## What you need before starting

- Level 2 complete: you can read a capture, run a script, document evidence, and reset a snapshot.
- The web lab built and verified — including the isolation check in LAB-301-01. A deliberately vulnerable
  application that answers on your Wi-Fi is a live target, not a lab.
- Two lab accounts you created, for every authorization test. One account cannot prove an access-control flaw.
- A snapshot strategy: take `pre-<lab-id>` before each lab and revert after evidence is saved.

---

## Where learners get stuck

| Sticking point | Why it happens | What helps |
| --- | --- | --- |
| Tool-driven testing | The scanner says "SQL injection" and the learning stops | Ask which line of code, which input, which missing control |
| XSS that "does not work" | Wrong injection context | Identify context first (HTML, attribute, script, URL), then payload |
| One-account testing | It feels sufficient and proves nothing | Always create a second identity before testing authorization |
| Severity inflation | Everything looks critical at first | Use impact × likelihood, write the precondition, defend it |
| Fixing by filtering input | Filters feel like a quick win | Parameterise, encode on output, authorize in the query |
| Treating a mitigation as a fix | WAF rules and CSP are visible and satisfying | Record fix vs mitigate vs accept, and say which you did |
| Copying CVSS from a tool | It looks objective | Prioritise by reachability, exposure, and data sensitivity |

---

## Known limitations, stated plainly

- **No lab in this level has been executed on a real VM pair by the course author.** Commands and expected outputs
  are written to spec but unverified on hardware; that is the main acceptance gap, and it applies to Levels 1–3.
- The pinned application versions and advisory data will age. Each lab records versions so a future reviewer can
  reproduce the state; expect to update them on a review cycle.
- Two modules (CYB-305 applied cryptography, CYB-306 identity and federation) are not written. The level
  assessment **is** published: see the [Level 3 integrated assessment](../assessments/level-3-assessment.md).

---

## After Level 3

[Level 4 — Defensive Operations](level-4.md) builds directly on this material: the logs you will triage are full of
the request patterns you have just learned to recognise, and the attack traffic you generated becomes detection
test data.

---

## Related

- [Full roadmap](../curriculum/roadmap.md) · [Levels overview](index.md)
- [Safety Policy](../policies/safety-policy.md) — scope rules for application testing
- [Assessment Report Template](../policies/assessment-report-template.md)
- [Assessment Guide](../start-here/assessment-guide.md)

---
title: "Secure Coding, Review and Supply Chain"
description: "Threat modeling, code review by taint analysis, dependency risk, and the protocol for proving a remediation."
module_code: CYB-307
level: 3
kind: lesson
prerequisites: [CYB-304]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-307-01, LAB-307-02, LAB-307-03]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [threat-modeling, stride, code-review, supply-chain, sbom, remediation]
---

# Secure Coding, Review and Supply Chain

**Level 3** · 240 minutes · **Prerequisites:** CYB-304 · **Labs:**
[Threat Model and Review](lab-01-code-review-and-threat-model.md) ·
[Dependencies](lab-02-vulnerable-dependencies.md) ·
[Fix and Verify](lab-03-fix-and-verify.md)

## Why this matters

A penetration test tells you which flaws exist today. A threat model and a review process decide which flaws get
written tomorrow. The difference between a team that keeps shipping injection bugs and one that stops is rarely
tooling — it is that the second team reviews for *data crossing a trust boundary* rather than reading code for
style.

The last skill in this lesson is the one most often skipped: proving a fix. A patch without a test that fails
before it and passes after it is a hope, and the same bug returns in the next sprint under a different name.

## Learning outcomes

By the end of this lesson you will be able to:

- Produce a data-flow diagram with trust boundaries and derive STRIDE threats with mitigations and tests.
- Apply the classic secure-design principles to a concrete feature and name the principle a flaw violates.
- Review code by tracing data from source to sink, and cite findings by file and line.
- Inventory dependencies, read advisory output critically, and prioritise by reachability and exploitability.
- Distinguish fix, mitigation, and accepted risk, and verify a remediation with two-directional tests.

## Prerequisites and setup

- Flask and `pytest` installed; `pip-audit` available (`pip install pip-audit`).
- The four-context lab from [LAB-302-02](../02-injection-and-xss/lab-02-xss.md) is useful background.
- A git repository you create for the sample application in LAB-307-01.

---

## Core concepts

### 1. Where security work belongs

Security work is cheapest at design time and most expensive after deployment. The multiplier is not a marketing
claim; it is arithmetic — a design change costs a conversation, a code change costs a review cycle, and a
production fix costs an incident, a patch release, and a disclosure.

| Phase | Security activity | Artefact |
| --- | --- | --- |
| Requirements | Classify data; state abuse cases | Data classification, security requirements |
| Design | Threat model; choose controls | DFD, threat table, control decisions |
| Implementation | Secure patterns; review | Pull request reviews, tests |
| Build | SCA, secret scanning, SAST | Dependency report, SBOM, scan results |
| Deploy | Configuration baseline, headers, TLS | Hardening checklist |
| Operate | Logging, detection, patching | Detections, patch cadence, retest reports |

Two rules make these activities survive contact with a deadline: every gate must be **automatic where possible**
(a check that fails the build beats a policy nobody reads), and every gate must have an **owner**. A checklist with
no owner is documentation of good intentions.

### 2. Threat modeling without ceremony

A threat model is a short, structured answer to four questions: what are we building, what can go wrong, what are
we going to do about it, and did we do a good job. It fits on two pages.

**Step 1 — draw the data flow.** Four element types are enough: external entity (actor), process (your code),
data store, and data flow (arrow). Mark every place data crosses from a lower-trust zone to a higher-trust one —
those lines are **trust boundaries**, and nearly every finding lives on one.

```text
[Browser]──(1) upload──▶│ [Web app] ──(2) store──▶ [Object store]
                        │      │
   trust boundary ──────┘      └──(3) read──▶ [Database]
```

**Step 2 — apply STRIDE to each boundary crossing.** Not to every line of code; to the crossings.

| Threat | Question | Upload example | Typical controls |
| --- | --- | --- | --- |
| **S**poofing | Can an actor claim another identity? | Upload as another user by changing an id | Authentication, signed tokens, per-object authorization |
| **T**ampering | Can data be changed in transit or at rest? | Swap the stored file after validation | Integrity checks, immutable storage, TLS |
| **R**epudiation | Can an action be denied later? | No record of who uploaded what | Audit logs with subject, action, object, time |
| **I**nformation disclosure | Can data leak? | Files served to anyone who guesses the URL | Authorization on read, unguessable names, `no-store` |
| **D**enial of service | Can one actor exhaust a resource? | Gigabyte uploads, zip bombs | Size limits, quotas, timeouts, decompression bounds |
| **E**levation of privilege | Can code or a user gain rights? | Uploaded `.php` executed by the server | Non-executable storage, type allowlist, least privilege |

**Step 3 — turn each threat into a control and a test.** A threat with no test is a wish. The output is a table:

| # | Boundary | Threat | Control | Test |
| --- | --- | --- | --- | --- |
| 1 | Browser → app | E: uploaded file executed | Content allowlist, `uuid` name, store outside web root | Upload `.php` with `image/png`; expect `415` |
| 2 | App → store | I: file readable by URL guessing | Serve through a handler that checks ownership | Request another user's file id; expect `404` |
| 3 | App → DB | T: stored metadata altered | Parameterised writes, append-only audit table | Attempt SQLi in filename; expect no error and literal storage |

That table is the deliverable. It is also the input to the code review, because it tells the reviewer what to look
for.

### 3. Secure design principles, and the flaw each one prevents

These are old and still decisive. Each row pairs a principle with a vulnerability class it removes.

| Principle | Meaning | Flaw it prevents |
| --- | --- | --- |
| Least privilege | Every component gets the minimum rights | Database user that can drop tables turns SQLi into catastrophe |
| Fail-safe defaults | Deny unless explicitly allowed | New endpoint inherits "authenticated = allowed" |
| Complete mediation | Check every access, every time | Authorization checked in the UI, not the API |
| Economy of mechanism | Simple, small, understandable | Clever path handling that nobody can review |
| Separation of duties | No single actor completes a sensitive action | One admin can approve their own payment |
| Least common mechanism | Avoid shared state between users | Cache keyed without the user id |
| Open design | Security does not depend on secrecy | Hidden admin path treated as a control |
| Psychological acceptability | Controls people will actually use | Password policy so strict it is written on a sticky note |

The single most useful question in a design review: **"what happens if the client sends something else?"** Every
answer that begins "the UI won't allow that" is a missing control.

### 4. Reviewing code: follow the data

Reading code line by line for "security" does not scale and produces style comments. Review by **taint**: find
sources, follow propagation, inspect sinks.

**Sources** (untrusted input): HTTP parameters, headers, cookies, body; file contents; queue messages; third-party
API responses; database rows that were themselves user-supplied.

**Sinks** (dangerous operations): SQL execution, shell execution, template rendering, HTML output, filesystem
paths, HTTP clients, deserialisation, logging of secrets, `eval`.

**The review question for each sink:** can any source reach it without validation and encoding appropriate to that
sink?

```python
# Source: query parameter. Sink: SQL. Propagation: concatenation.
q = request.args["q"]                                   # source
sql = f"SELECT * FROM items WHERE name = '{q}'"          # propagation (the bug)
db.execute(sql)                                          # sink
```

```python
# Fixed: the sink receives a statement and a value, never a statement with a value inside it.
db.execute("SELECT * FROM items WHERE name = ?", (q,))
```

Practical aids, in order of usefulness:

1. **Review the diff, not the file.** New lines are where new flaws are.
2. **Grep for sinks by name.** `execute(`, `os.system`, `subprocess`, `render_template_string`, `innerHTML`,
   `open(`, `requests.get`, `pickle.loads`, `eval(`.
3. **Grep for the dangerous idioms.** f-strings near `execute`, `+` near `open`, `|safe` in templates,
   `dangerouslySetInnerHTML`, `verify=False`, `debug=True`.
4. **Check the authorization question at every route**, not only the interesting ones: which user, which object,
   and where is the comparison?
5. **Write down false positives.** "Looks unsafe but is allowlisted at line 42" is a valuable review comment.

**Cite findings by file and line, and classify by consequence**, not by pattern: "`app.py:31` — `q` concatenated
into SQL, reachable pre-authentication, allows reading the `users` table" is reviewable; "possible SQL injection"
is not.

### 5. Supply chain: the code you did not write

A modern application is mostly dependencies. Three properties make that risky: you did not review the code, the
code can execute at install time, and the dependency graph is deeper than the list you wrote down.

| Threat | Mechanism | Control |
| --- | --- | --- |
| Known vulnerability in a dependency | Advisory published for a version you pinned | SCA in CI, patch cadence, reachability triage |
| Typosquatting | `reqeusts` instead of `requests` | Exact-name review, registry allowlist, lockfile |
| Dependency confusion | Internal package name published publicly with a higher version | Scope names to a private registry, pin sources |
| Maintainer account takeover | New version with a payload | Lockfile hashes, version pinning, review diffs on updates |
| Malicious install script | `postinstall` / `setup.py` executes at install | `--ignore-scripts`, install in a sandbox, review hooks |
| Abandoned package | No updates, unpatched advisories | Inventory with maintenance status, replacement plan |
| Transitive depth | Flaw five levels down | SBOM, `npm ls`/`pipdeptree`, automated alerts |

**Controls that actually reduce risk**, in order:

1. **Fewer dependencies.** Every package is attack surface and maintenance debt. Justify each direct dependency.
2. **A lockfile, committed.** Exact versions plus integrity hashes, so an install is reproducible.
3. **Automated advisory scanning in CI**, failing on high-severity findings with a documented exception path.
4. **An SBOM** (CycloneDX or SPDX) per release, so you can answer "are we affected?" in minutes rather than days.
5. **A patch cadence** with an owner. Unpatched is the normal state of a system without one.
6. **Provenance where available** — signed artefacts, attested builds (SLSA), verified publishers.

**Reading advisory output critically.** A scanner reports a package and a CVE. The questions that decide priority
are: is the vulnerable function reachable from our code, is the input attacker-controlled, and is the package in
the runtime path or a dev tool? A critical advisory in a build-only dependency is usually lower priority than a
medium one in a request handler. Write that reasoning down; a list of CVEs sorted by score is not a risk
assessment.

### 6. Secrets

Secrets in source control are permanent: git history survives deletion, forks, and "we removed it in the next
commit". The controls are mundane and effective: secrets in environment variables or a secret manager; a pre-commit
and CI scanner (gitleaks, trufflehog); short-lived credentials where the platform supports them; and rotation as
the response to any exposure — not deletion.

Two specifics learners get wrong. A secret in a **client-side** bundle is public, regardless of minification. And a
secret in a **log line** is exposed to everyone with log access, which is usually a much larger group than you
think.

### 7. Fix, mitigate, accept — and how to verify

Every finding gets exactly one of these dispositions, and the report says which.

| Disposition | Meaning | Example |
| --- | --- | --- |
| **Fix** | Remove the cause | Parameterise the query; scope the query by owner |
| **Mitigate** | Reduce impact without removing the cause | WAF rule, `HttpOnly` on the session cookie, CSP |
| **Accept** | Documented decision with an owner and a review date | Legacy endpoint, compensating network control |

Verification is a protocol, not a feeling. For every fix:

1. **Re-run the original exploit** in the same environment and version. It must fail, and the failure must be the
   intended one (`404`, not a `500` from a broken patch).
2. **Run the legitimate function.** The feature must still work — this is the test teams forget, and it is why
   "fixes" get reverted.
3. **Add both as automated tests.** The exploit test is the regression guard.
4. **Confirm the test fails on the old code.** If it passes on the vulnerable version, it is not testing the fix.
5. **Record evidence**: command, output, version, date, and who verified.
6. **Retest related surfaces.** The same pattern usually exists in more than one place; a fix to one endpoint is
   not a fix to the class.

A worked example of the two-directional test, which is the shape you will write for the rest of the course:

```python
def test_owner_can_read_invoice(client):
    assert client.get("/invoices/1", headers={"X-User": "alice"}).status_code == 200

def test_other_user_gets_404(client):
    assert client.get("/invoices/1", headers={"X-User": "bob"}).status_code == 404
```

**Why both:** the first catches over-restriction (a fix that breaks the product gets reverted, and then you have
neither security nor function). The second catches the vulnerability. Together they define the boundary you
intended.

---

## Worked example: threat model to test, in one page

A team is adding a "share report by link" feature. The model, in the format you will use in the lab:

| # | Boundary | Threat | Control | Test |
| --- | --- | --- | --- | --- |
| 1 | User → app | S: user shares another tenant's report | Authorize report ownership at creation | Attempt share with foreign `report_id`; expect `404` |
| 2 | App → DB | I: token guessable | 128-bit random token, stored hashed | Assert token length and entropy in a unit test |
| 3 | Link → app | E: token grants more than read | Token scoped to `report:read`, single report | Use token on another report; expect `404` |
| 4 | Link → app | I: link leaks via `Referer` | `Referrer-Policy: no-referrer` on the share page | Check header in a request test |
| 5 | Link → app | D: unlimited downloads | Per-token rate limit | 20 requests; expect `429` |
| 6 | App → logs | I: token logged in the URL | Log the report id, never the token | Grep the log fixture for the token value |

Six threats, six controls, six tests, all derivable in twenty minutes at design time. Compare that with finding
them in production.

---

## Defender's view

| Signal | Source | Meaning |
| --- | --- | --- |
| New direct dependency in a lockfile diff | Pull request | Review the need, the maintainer, and the install scripts |
| Advisory count jumping after a lockfile change | CI | A bump pulled in a vulnerable transitive package |
| Secret-shaped strings in a commit | Pre-commit scanner | Rotate, do not just delete |
| `debug=True`, `verify=False`, `|safe`, `innerHTML` in a diff | Code review / SAST | Dangerous idioms, review immediately |
| Repeated fix-and-revert on the same file | Git history | The fix broke a feature; the requirement is unclear |
| Same finding reported in consecutive assessments | Retest reports | Remediation was a mitigation, or was never verified |

The operational habit that makes all of this stick: **close findings with evidence, not with a status change.**
"Fixed" with a linked test and a retest output is worth more than a hundred tickets marked done.

---

## Common mistakes

1. **Threat modeling as a document nobody reads.** If it does not produce tests, it produced nothing. Keep it to a
   page and attach it to the change.
2. **Reviewing style, not data flow.** Formatting comments crowd out the one question that matters: can input
   reach a sink?
3. **Treating CVSS as priority.** Reachability and exposure decide priority; the score is an input.
4. **Updating a dependency without reading the changelog.** Major-version bumps change behaviour, and supply-chain
   attacks arrive as updates.
5. **Verifying only that the attack fails.** A fix that breaks the feature will be reverted, and the
   vulnerability returns with it.
6. **Deleting a leaked secret and calling it handled.** It is in the history, the forks, and possibly a build log.
   Rotate it.

---

## Practice

1. [LAB-307-01 · Threat Model and Code Review](lab-01-code-review-and-threat-model.md) — the seeded application,
   reviewed by inspection and by test.
2. [LAB-307-02 · Vulnerable Dependencies](lab-02-vulnerable-dependencies.md) — inventory, advisory triage, SBOM.
3. [LAB-307-03 · Fix, Test and Verify](lab-03-fix-and-verify.md) — repair every finding and prove each one.

**Stretch task.** Take the threat table from LAB-307-01 and add a row for a threat you decided was out of scope.
Write the justification, the compensating control, and the date you would revisit it. Accepted risks belong in the
report too.

## Knowledge check

1. What is a trust boundary, and why do most findings sit on one?
2. Map STRIDE to a password-reset flow: name one threat per letter.
3. Which secure-design principle does "the UI hides the admin button" violate?
4. Describe taint analysis in one sentence, naming source, propagation, and sink.
5. A scanner reports a critical CVE in a build-only tool. What two questions decide its priority?
6. What is dependency confusion, and which single control most reduces it?
7. Why must a remediation test fail on the vulnerable version?
8. Give one finding where a WAF is a legitimate mitigation and one where it is not.

## Summary

- Security is cheapest at design time; make gates automatic and give them owners.
- A threat model is a diagram, trust boundaries, STRIDE threats, controls, and tests — two pages, not twenty.
- Review by following data from source to sink, and cite file and line with a consequence.
- Supply chain risk is managed with fewer dependencies, lockfiles, scanning, SBOMs, and a patch cadence.
- Every finding is fixed, mitigated, or accepted — and every fix is verified in both directions.

## References

1. OWASP Top 10:2025 — A03 Software Supply Chain Failures, A06 Insecure Design. <https://owasp.org/Top10/2025/>
2. OWASP Threat Modeling Cheat Sheet. Accessed 2026-10-29.
3. OWASP Code Review Guide v2.0. Accessed 2026-10-29.
4. NIST SP 800-218 — Secure Software Development Framework v1.1. Accessed 2026-10-29.
5. OWASP ASVS 5.0 — V15 Secure Coding and Architecture. <https://asvs.owasp.org/>
6. CycloneDX specification — SBOM formats. Accessed 2026-10-29.

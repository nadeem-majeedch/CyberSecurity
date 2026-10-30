---
title: "Level 3 Answer Key"
description: "Answers and explanations for all 30 Level 3 items, plus marking criteria for the application assessment."
module_code: ASM-L3K
level: 3
kind: assessment
prerequisites: [CYB-301]
estimated_minutes: 45
difficulty: intermediate
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, answer-key, level-3, web-security]
---

# Level 3 Answer Key

!!! warning "Attempt first"
    Attempt the [Level 3 quiz](level-3-quiz.md) before reading this page.

**Marking.** One mark per item, 5 per module. For scenario items, the ranking is less important than the
reasoning: a different order with a defensible mechanism earns the mark.

---

## CYB-301 · Web Architecture and HTTP

**Q301.1 — B.** The same-origin policy restricts *reading* responses, not sending requests. The browser sends
the request and withholds the response from the page, which is why CSRF exists: side effects can happen even
when the attacker cannot read the result.

**Q301.2 — B.** `HttpOnly` removes the cookie from `document.cookie`. `Secure` restricts transport; `SameSite`
restricts cross-site sending.

**Q301.3 — B.** A wildcard `Access-Control-Allow-Origin` is invalid for credentialed requests; the browser
blocks the response. Servers must echo an explicit origin and send
`Access-Control-Allow-Credentials: true`.

**Q301.4.** `Secure` means the browser sends the cookie only over HTTPS, which prevents plaintext exposure on
the network. It does not stop JavaScript from reading the cookie, does not prevent CSRF, and does not protect
the cookie at rest on the server.

**Q301.5.** Defensible ranking: **no `HttpOnly` highest** — any XSS becomes full session theft. Then **no
`SameSite`** — cross-site requests carry the session, enabling CSRF. Then **no `Secure`** — exposure requires
network interception, which TLS already makes difficult; HSTS absence matters mainly for downgrade and
first-visit cases. **No CSP** is last: it reduces impact rather than preventing a class, and a CSP without a
nonce strategy is often decorative. Full marks require naming the attack each omission enables.

---

## CYB-302 · Injection and XSS

**Q302.1 — B.** Parsing happens before data binding, so input cannot change the statement's structure. Escaping
is a different (fragile) strategy; parameter binding is structural.

**Q302.2 — B.** Identifiers (column and table names, sort direction) cannot be bound as values, so the design
must map a fixed set of allowed keys to fixed SQL fragments. Quoting or escaping a concatenated identifier is
the bug, not the fix.

**Q302.3 — C.** DOM-based: the sink is in client-side code and the payload may never reach the server.

**Q302.4.** HTML entities are decoded by the HTML parser, not by the JavaScript parser, so inside `<script>` an
entity remains literal text or breaks the script. The correct approach is context-specific encoding (JSON
encoding for data in script, attribute encoding for attributes, HTML encoding for HTML text), avoiding inline
script with untrusted data, and using safe DOM APIs such as `textContent`.

**Q302.5.** Two of: blocklists cannot enumerate every execution context or handler (SVG, MathML, namespaced
attributes, `javascript:` URLs); parser behaviour differs from the filter's string model (mutation XSS,
double-decoding); the sink is still unsafe, so any future context reintroduces the flaw; the filter is applied
on input rather than encoding at output. The fix is output encoding for the context, plus CSP as a backstop.

---

## CYB-303 · Access Control and Sessions

**Q303.1 — B.** Same privilege level, another user's object: horizontal broken access control, commonly called
IDOR. Vertical escalation would be reaching an admin function.

**Q303.2 — B.** A unique salt per password makes precomputation useless and prevents comparing hashes across
accounts. The algorithm and work factor matter too; the salt is not encryption.

**Q303.3 — B.** The attacker fixes a known session identifier before login; if the application does not rotate
on authentication, the attacker's identifier becomes authenticated. Fix: issue a new session ID at login and
invalidate the old one.

**Q303.4.** `SameSite=Lax` is a browser behaviour that varies by browser version, does not protect same-site
subdomains, and leaves GET-based state changes reachable. A synchroniser token is unpredictable, bound to the
session, and verified server-side for state-changing requests, so a cross-site request cannot supply it.

**Q303.5.** User enumeration. Attacker gains: a list of valid usernames, and the ability to target them with
spraying or phishing without wasting attempts. Fix: one generic message ("email or password incorrect"),
constant response timing where practical, rate limiting, and an email-based reset flow that never confirms
whether the address exists.

---

## CYB-304 · File Handling, SSRF and Misconfiguration

**Q304.1 — B.** Content-based validation, storage outside the web root, safe serving, and no execute permission
address the four ways uploads become code execution. Header checks are client-controlled; extension blocklists
are bypassable.

**Q304.2 — B.** Resolve, canonicalise, then compare against the resolved base directory. String rejection of
`../` fails against encodings, absolute paths and symlinks.

**Q304.3 — B.** DNS resolution is where a name becomes an address; checking the name alone allows a record that
points at an internal address, and a rebinding record can change between check and connect. Enforce on the
resolved address, and pin the connection.

**Q304.4.** Loopback has many representations (`127.0.0.1`, `127.1`, `2130706433`, `0x7f000001`, `[::1]`,
`localhost`, any DNS name resolving to it), and a permitted URL can redirect to one. Blocking requires
resolution and address-range checks, not string matching.

**Q304.5.** Directory listing first: it exposes whatever is in `/backup/`, which is often source, dumps or keys
— direct data exposure. Then the missing CSP: it is defence in depth, valuable mainly if XSS exists. Version
disclosure last: it helps an attacker target, but reveals nothing by itself. A different order with this
reasoning still earns full marks.

---

## CYB-307 · Secure Coding and Dependencies

**Q307.1 — B.** A WAF is a mitigation: the vulnerable concatenation remains, and encodings, alternate paths or
parameters may bypass the rule. "Attack blocked" is not "vulnerability removed".

**Q307.2 — B.** Reachability plus exposure plus a public exploit. A high score in dead code is lower risk; a
dev-only package is usually not in the production attack surface.

**Q307.3 — B.** The test must demonstrate the vulnerability existed: fail before, pass after. A test that only
runs on the fixed version proves the fix compiles, not that it fixes anything.

**Q307.4.** CVSS scores the technical characteristics of a vulnerability in the abstract; risk also depends on
whether the vulnerable code is reachable, what the asset is worth, what compensating controls exist, and
whether exploitation is occurring. A CVSS 9.8 in unreachable code can be lower risk than a 6.5 on an
internet-facing login.

**Q307.5.** Root cause: user input concatenated into SQL, so data becomes syntax. Fix: parameter binding (or a
query builder with bound values). Test: send `' OR '1'='1` and assert the response contains no other users'
rows and no database error, while a legitimate username still returns its row — run against the vulnerable
version first to prove the test can fail.

---

## CYB-308 · API Security

**Q308.1 — A.** Object-level authorization (BOLA/IDOR). The role check may exist while the per-object check
does not.

**Q308.2 — B.** Signature with an expected algorithm (never trust the token's `alg`), then expiry, audience and
issuer. Decoding without verification is how `alg: none` and key-confusion attacks succeed.

**Q308.3 — B.** Mass assignment: fields the client should not set are accepted because the request body is
bound to the model. Fix with an explicit allowlist or a dedicated input DTO.

**Q308.4.** Key on the authenticated subject (token or user ID) plus route and action, with a secondary IP-based
limit for unauthenticated traffic. IP alone is shared behind NAT and proxies, is spoofable in some paths, and
does nothing against one authenticated attacker rotating addresses.

**Q308.5.** Excessive data exposure / property-level authorization. Test: request the same object as its owner
and as a second user with equal role; compare fields and status codes; check whether the UI simply hides the
fields. Fix: serialise through a response DTO with an explicit field allowlist, and verify the response no
longer contains the fields for any caller who should not see them.

---

## Troubleshooting exercises — marking criteria

**T308.1** (3 marks) — one for each alternative: malformed input causing a type/conversion error; an
application bug unrelated to SQL; a deliberately verbose error handler. One for the confirmation method:
compare responses for true and false conditions (`' AND '1'='1` versus `' AND '1'='2`), inspect timing, or test
a parameter that cannot be injectable. A 500 alone proves only that something failed.

**T308.2** (3 marks) — diagnosis: encoding applied at input rather than at output, or applied to the wrong
context (HTML-encoding text that is later inserted into an attribute or script), so the stored value is
double-encoded. Award marks for the two tests: the payload must not execute in the context it was aimed at,
**and** legitimate content (`<b>`, quotes, non-ASCII, emoji) must render correctly.

**T308.3** (3 marks) — check: whether the token's claims still reflect current roles (role change after issue,
token revocation, server-side session state), whether the admin token is genuinely valid, and whether the
difference is authorization or caching. The result is not a finding because a stale token may be expected
behaviour or a test artefact; you need a reproducible request from a current, legitimately issued token before
claiming broken access control.

---

## Level 3 integrated assessment — model answers

### A defensible finding set for the sample application

| ID | Finding | Class | Severity | Evidence | Fix |
| --- | --- | --- | --- | --- | --- |
| F-01 | Invoice IDOR | Broken access control | High | Two accounts; `GET /invoice/1043` returns 200 with the other user's data | Server-side ownership check before returning the object |
| F-02 | Reflected XSS in search | Injection into HTML | High | `?q=<svg onload=alert(1)>` executes | Contextual output encoding; CSP as backstop |
| F-03 | SQL injection in login | Injection into SQL | Critical | `' OR '1'='1' --` authenticates | Parameterised query; regression test |
| F-04 | MD5 password storage | Cryptographic failure | High | `SELECT` on the users table shows 32-hex values | Argon2id (or bcrypt) with per-user salt; force reset |
| F-05 | No rate limit on login | Authentication weakness | Medium | 200 attempts in 60 seconds, all processed | Per-account and per-IP limiting with backoff |
| F-06 | Verbose error page | Misconfiguration | Low | Stack trace and framework version in response | Generic error page; log details server-side |

### Written component criteria

**B1 — Root cause per finding (12 marks).** Requires the mechanism, not the payload: which interpreter received
the data, why the check was missing, where the trust boundary was crossed. "The app is vulnerable to XSS
because it does not encode output in the search results template at line 42" earns the marks; "input was not
sanitised" does not.

**B2 — Fix versus mitigation (8 marks).** Requires at least one finding where you distinguish the two and
place both correctly: parameter binding fixes injection; a WAF rule mitigates it. State the residual risk of
the mitigation and what would make it a fix.

**B3 — Defending a cryptographic decision (5 marks).** Requires a specific choice with reasons: algorithm, salt
strategy, work factor or memory cost, and migration path for existing hashes. "Use bcrypt" alone earns half.

**B4 — Retest evidence (5 marks).** Requires the retest command or request and the new response, plus the
legitimate function that still works. A fix that breaks the feature is not a fix.

---

## Scoring

| Module score | Action |
| --- | --- |
| 5/5 | Retake at seven days |
| 4/5 | Reread the missed explanation |
| 3/5 | Re-read the lesson section and redo the corresponding lab step |
| 0–2/5 | Return to the lab: the gap is in execution, not recall |

Level total: 30 marks; 24 or above suggests readiness for the integrated assessment.

## Related

- [Level 3 quiz](level-3-quiz.md) · [Level 3 integrated assessment](level-3-assessment.md)
- [OWASP Top 10](https://owasp.org/Top10/) — the reference points used throughout Level 3
- [Level 3 overview](../levels/level-3.md)

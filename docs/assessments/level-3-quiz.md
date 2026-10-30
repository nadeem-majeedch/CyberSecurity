---
title: "Level 3 Module Quizzes — Applications, Identity and Secure Code"
description: "Thirty self-check items across CYB-301 to CYB-308: HTTP and browser security, injection, access control, file handling, dependencies and APIs."
module_code: ASM-L3
level: 3
kind: assessment
prerequisites: [CYB-301]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, quiz, level-3, web-security, api]
---

# Level 3 Module Quizzes

Five items per module, six modules, thirty items. Every technical item assumes the deliberately vulnerable
application in your own lab — Juice Shop, the course's sample app, or the lab build from
[CYB-301](../levels/level-3-applications/01-web-architecture-and-http/index.md). No public site, no real
account, no real data.

**Protocol.** Attempt on paper, then mark against the [Level 3 answer key](level-3-key.md). Target 4 of 5 per
module. Where an item asks for a payload, it asks for the *class* of payload and the context — not a working
exploit for a system you do not own.

---

## CYB-301 · Web Architecture and HTTP

**Q301.1** (MCQ) A page at `https://app.example.com` tries to read a response from `https://api.example.com`.
By the same-origin policy, what happens?

- A. The request is blocked before it is sent
- B. The request is sent, and the browser prevents the page from reading the response
- C. Both request and response are allowed because both use HTTPS
- D. The browser allows it if the server sends `Access-Control-Allow-Origin: *` and the request includes cookies

**Q301.2** (MCQ) Which `Set-Cookie` attribute prevents JavaScript from reading the cookie?

- A. `Secure`
- B. `HttpOnly`
- C. `SameSite=Strict`
- D. `Domain`

**Q301.3** (MCQ) A response contains `Access-Control-Allow-Origin: *` and the page sends
`credentials: 'include'`. What does the browser do?

- A. Sends the request and exposes the response
- B. Blocks the response from being read, because a wildcard origin cannot be combined with credentials
- C. Sends the request without cookies and exposes the response
- D. Converts the request to a simple request automatically

**Q301.4** (Short) Explain what `Secure` does and what it does not do, in two sentences.

**Q301.5** (Scenario) An application sets a session cookie without `HttpOnly`, `Secure` or `SameSite`, and
returns no CSP or HSTS header. Rank these four omissions by the risk each creates for a logged-in user, and
justify the top one.

---

## CYB-302 · Injection and XSS

**Q302.1** (MCQ) Why does parameterised binding prevent SQL injection?

- A. It escapes dangerous characters in the input
- B. The statement is parsed and planned before the data is supplied, so data cannot become syntax
- C. It encrypts the parameters
- D. It limits the query to one row

**Q302.2** (MCQ) A developer writes `ORDER BY ?` and the results are unsorted. What is the correct fix?

- A. Wrap the placeholder in quotes
- B. Use an allowlist that maps a user-supplied sort key to a fixed column name
- C. Concatenate the column name after escaping it
- D. Switch to a stored procedure

**Q302.3** (MCQ) Which XSS type executes without the payload being stored on, or reflected by, the server?

- A. Reflected
- B. Stored
- C. DOM-based
- D. Self-XSS

**Q302.4** (Short) Why is HTML entity encoding the wrong defence inside a `<script>` block, and what is the
correct approach?

**Q302.5** (Scenario) An application strips `<script>` and the string `onerror`. A tester shows that an image
tag with an SVG `onload` handler executes. Give two reasons the filter is not a fix.

---

## CYB-303 · Access Control, Authentication and Sessions

**Q303.1** (MCQ) A user changes `/invoice/1042` to `/invoice/1043` and sees another customer's invoice. What
class of flaw is this?

- A. Vertical privilege escalation
- B. Horizontal broken access control (IDOR)
- C. CSRF
- D. Session fixation

**Q303.2** (MCQ) Why must a password hash be salted?

- A. To make the hash shorter
- B. So identical passwords do not produce identical hashes, defeating precomputed tables and cross-account
  comparison
- C. To encrypt the password
- D. To allow the password to be recovered

**Q303.3** (MCQ) What is session fixation, and what is the correct fix?

- A. An attacker steals a session cookie after login; fix with `HttpOnly`
- B. An attacker sets a session identifier before authentication and reuses it afterwards; fix by issuing a new
  session identifier at login
- C. A session that never expires; fix with a timeout
- D. A session shared between tabs; fix by using one tab

**Q303.4** (Short) Why is `SameSite=Lax` alone insufficient as CSRF protection, and what does a synchroniser
token add?

**Q303.5** (Scenario) A login endpoint responds `No such user` for unknown accounts and `Incorrect password` for
known ones. State the flaw, the two things an attacker gains, and the fix that keeps the UX usable.

---

## CYB-304 · File Handling, SSRF and Misconfiguration

**Q304.1** (MCQ) Which set of controls makes an upload feature genuinely safe?

- A. Checking the `Content-Type` header and renaming the file
- B. Validating the file by content, storing it outside the web root, serving it through a handler that sets a
  safe content type, and removing execute permission
- C. Blocking `.php` and `.exe` extensions
- D. Storing uploads in the database

**Q304.2** (MCQ) Which implementation correctly prevents path traversal in a download endpoint?

- A. Rejecting any request containing `../`
- B. Resolving the requested path and verifying that the canonical result is inside a fixed base directory
- C. URL-encoding the filename
- D. Restricting filenames to 255 characters

**Q304.3** (MCQ) Why must an SSRF allowlist be enforced after DNS resolution?

- A. Because DNS is slower than HTTP
- B. Because a hostname can resolve to a blocked internal address, or change between check and connection
- C. Because TLS requires an IP address
- D. Because allowlists only work with IPv4

**Q304.4** (Short) Why is blocking the literal string `127.0.0.1` insufficient to prevent SSRF to loopback?

**Q304.5** (Scenario) A scan reports directory listing enabled on `/backup/`, a missing `Content-Security-Policy`
and a `Server` header disclosing the exact version. Rank the three and justify which one you would fix first.

---

## CYB-307 · Secure Coding, Dependencies and Remediation

**Q307.1** (MCQ) A team adds a web application firewall rule that blocks the payload used in a proof of concept.
Is the SQL injection fixed?

- A. Yes, because the attack no longer succeeds
- B. No: it is mitigated, because the vulnerable construction remains and another payload or path may bypass it
- C. Yes, if the rule is in blocking mode
- D. Only if the rule is updated daily

**Q307.2** (MCQ) Which dependency finding should be fixed first?

- A. CVSS 9.8 in a library function the application never calls
- B. CVSS 7.5 in a function reachable from an unauthenticated endpoint, with a public exploit
- C. CVSS 5.3 in a development-only package
- D. A dependency with no advisory but last updated three years ago

**Q307.3** (MCQ) What makes a regression test for a fixed vulnerability trustworthy?

- A. It passes on the fixed version
- B. It fails on the vulnerable version and passes on the fixed one
- C. It is written by the developer who fixed the bug
- D. It runs in CI

**Q307.4** (Short) Explain in two sentences why CVSS is a severity score rather than a risk score.

**Q307.5** (Scenario) A review finds `db.query("SELECT * FROM users WHERE name = '" + name + "'")`. State the
root cause, the fix, and the test that proves it.

---

## CYB-308 · API Security

**Q308.1** (MCQ) Two users with the same role can read each other's orders by changing the ID in
`/api/orders/{id}`. Which OWASP API risk is this?

- A. Broken object-level authorization
- B. Unrestricted resource consumption
- C. Server-side request forgery
- D. Improper inventory management

**Q308.2** (MCQ) Which set of checks must a JWT verification perform?

- A. Decode the payload and read `sub`
- B. Verify the signature with an expected algorithm, then check `exp`, `aud` and `iss`
- C. Check that the token is not expired
- D. Base64-decode and compare with the database

**Q308.3** (MCQ) An API accepts a JSON body and passes it directly to an ORM's create method. What is the
primary risk?

- A. SQL injection
- B. Mass assignment, allowing fields the client should not control (such as `role` or `balance`)
- C. XML external entity injection
- D. Cross-site scripting

**Q308.4** (Short) What should a rate limit be keyed on for an authenticated API, and why is the client IP alone
a poor choice?

**Q308.5** (Scenario) An API response contains `internal_notes`, `cost_price` and `ssn_last4`, none of which the
UI displays. State the flaw, how you would test for it with two accounts, and the fix.

---

## Troubleshooting exercises

**T308.1** A SQL injection payload returns a 500 with a stack trace in the response. A colleague says "the
error proves injection". What else could produce the same response, and what would you do to confirm the class
of flaw?

**T308.2** A fix for reflected XSS is applied and the payload no longer executes, but the page now renders
`&lt;b&gt;` literally in user comments. Diagnose the mistake and state the two tests a fix must pass.

**T308.3** An API returns 403 for a request made with a user token and 200 with an admin token, but the admin
token was issued to the same person before a role change. Explain what you would check and why the result is
not yet a finding.

---

## Practical challenges

| Module | Challenge | Where |
| --- | --- | --- |
| CYB-301 | Evaluate cookie and session attributes and name the threat each addresses | [LAB-301-03](../levels/level-3-applications/01-web-architecture-and-http/lab-03-cookie-and-session-attributes.md) |
| CYB-302 | Execute and then block reflected and stored XSS with correct encoding | [LAB-302-02](../levels/level-3-applications/02-injection-and-xss/lab-02-xss.md) |
| CYB-303 | Demonstrate IDOR with two accounts, then fix the authorization check | [LAB-303-02](../levels/level-3-applications/03-access-control-and-authentication/lab-02-broken-access-control.md) |
| CYB-304 | Bypass an upload filter, then implement content validation and prove it holds | [LAB-304-01](../levels/level-3-applications/04-file-handling-ssrf-misconfiguration/lab-01-file-upload.md) |
| CYB-307 | Fix a vulnerable sample and prove it with a failing-then-passing test | [LAB-307-03](../levels/level-3-applications/05-secure-coding-and-dependencies/lab-03-fix-and-verify.md) |
| CYB-308 | Find object-level and property-level authorization failures with two identities | [LAB-308-01](../levels/level-3-applications/06-api-security/lab-01-api-authorization.md) |

---

## Next

- [Level 3 answer key](level-3-key.md)
- [Level 3 integrated assessment](level-3-assessment.md) — assess, fix and retest a local application
- [Level 3 overview](../levels/level-3.md)

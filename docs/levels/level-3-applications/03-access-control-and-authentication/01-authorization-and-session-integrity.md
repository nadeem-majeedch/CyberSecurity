---
title: "Authorization, Identity and Session Integrity"
description: "Access control models, authentication weaknesses, password storage, session lifecycle and the mechanics of CSRF."
module_code: CYB-303
level: 3
kind: lesson
prerequisites: [CYB-301]
estimated_minutes: 300
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-303-01, LAB-303-02, LAB-303-03]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [access-control, idor, authentication, password-storage, sessions, csrf]
---

# Authorization, Identity and Session Integrity

**Level 3** · 300 minutes · **Prerequisites:** CYB-301 · **Labs:**
[Insecure Login](lab-01-insecure-login-workflow.md) ·
[Broken Access Control](lab-02-broken-access-control.md) ·
[CSRF](lab-03-csrf.md)

## Why this matters

Most breaches do not begin with a clever exploit. They begin with a valid session and a request the application
should have refused. A support portal that returns any customer's record when you change `?id=1041` is not a
subtle bug; it is a missing `WHERE owner_id = ?` and a missing authorization check, and it is the single most
common finding in web assessments.

The skills in this lesson are unglamorous and extremely valuable: knowing which question each control answers,
and being able to prove that the answer is missing using nothing but two requests and their responses.

## Learning outcomes

By the end of this lesson you will be able to:

- Separate authentication from authorization failures and classify access-control flaws as vertical, horizontal,
  or contextual.
- Design and execute an IDOR test that distinguishes "no access" from "different data, same access".
- Evaluate a login workflow against enumeration, lockout, reset, and MFA bypass.
- Judge a password-storage scheme by algorithm, salt, work factor, and comparison method.
- Identify session fixation and missing revocation from observable behaviour.
- Explain why a CSRF token works, and why `SameSite` is a mitigation rather than the control.

## Prerequisites and setup

- Web lab running; DVWA at **Low**; two Juice Shop accounts you created.
- `htpasswd` (`sudo apt install apache2-utils`), Python 3.10+ with `bcrypt` and `argon2-cffi`.
- Your session-attribute table from LAB-301-03.

---

## Core concepts

### 1. Two questions, regularly confused

**Authentication** answers *who is this?* — a login, a token, a certificate.
**Authorization** answers *may this identity do this, to this object, now?* — a policy decision, made per request.

The confusion is not academic. It produces the most common false negative in testing: seeing a login page, logging
in, and concluding the application is protected. Authentication gates the door; authorization decides which rooms
you may enter. A single missing check inside is a breach that no login screen prevents.

| Flaw | Question that failed | Example |
| --- | --- | --- |
| Authentication bypass | Who are you? | SQL injection in login, JWT accepted without signature verification |
| Vertical privilege escalation | May a normal user perform an admin action? | `POST /admin/users/delete` reachable by any authenticated user |
| Horizontal privilege escalation (IDOR) | May *this* user read *this* object? | `GET /invoices/1041` returns another customer's invoice |
| Contextual / state-dependent | Is this action valid in the current state? | Approving your own expense claim, skipping a workflow step |
| Forced browsing | Is this endpoint meant to be reachable at all? | `/backup.zip`, `/admin/`, `/.git/config` |

### 2. Access control models, and where they break

- **RBAC (role-based)** — permissions attached to roles, users assigned roles. Simple, auditable, and prone to
  role explosion. Breaks when a check is applied to a *page* but not the *API* behind it.
- **ABAC (attribute-based)** — decisions from attributes (department, clearance, resource owner). Expressive, hard
  to reason about; breaks when attributes are user-controlled.
- **ReBAC (relationship-based)** — permissions derived from relationships ("owner", "member of team"). Correct
  model for multi-tenant data, and the one most often implemented by hand, badly.
- **ACLs** — per-object lists. Fine for documents, painful at scale.

Whatever the model, three implementation rules decide whether it holds:

1. **Deny by default.** Every endpoint starts closed; access is granted explicitly. Allowlists scale; blocklists
   are always one route behind.
2. **Enforce on the server, at the object.** The UI hiding a button is not a control. The check must run on the
   request that reads or mutates the object.
3. **Check the object, not just the route.** `GET /invoices/:id` passes authentication for every user; the
   question is whether *this* user may read invoice `:id`.

The implementation pattern that prevents most of this, stated once because it is the fix you will write most
often:

```python
# VULNERABLE — the query is scoped by the requested id only
row = db.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()

# SAFE — the query is scoped by the authenticated subject as well
row = db.execute(
    "SELECT * FROM invoices WHERE id = ? AND owner_id = ?",
    (invoice_id, session["user_id"]),
).fetchone()
```

Doing it in the query rather than in an `if` afterwards removes the class of bug where a developer checks, then
forgets to apply the check on a new endpoint. It also makes the intent legible in review.

### 3. IDOR: testing it properly

**IDOR (Insecure Direct Object Reference)** is any case where the client supplies a reference to an object and
the server uses it without verifying the requester's right to that object. The reference need not be a number: a
filename, a UUID, an order code, or a GraphQL node ID all count. UUIDs are not a control either — they leak
through APIs, emails, exports, and logs.

A disciplined test has four steps:

1. **Create two identities** with equal privilege, A and B. (This is the step people skip, and without it you
   cannot distinguish "no access" from "not found".)
2. **As A, create an object** and note every reference the application returns.
3. **As B, request A's object** with the reference — via the API, not the UI.
4. **Compare**: same body as A saw → IDOR. `403`/`404` → control present. A different shape (e.g. empty object,
   generic error) → investigate; it may be a partially applied check.

| Observation as B | Interpretation |
| --- | --- |
| A's full record | Confirmed IDOR |
| `403 Forbidden` | Authorization check present on this route |
| `404 Not Found` | Either a check that masks existence, or genuinely missing — test with A's own reference |
| `200` with an empty object | Often a filter applied after fetch — check whether any field leaked |
| `500` with a stack trace | The check exists but throws; also a verbose-error finding |

**Why "compare" and not "look for 200":** `200` is the normal outcome for a page that legitimately returns an
empty list. The evidence is that B received *A's data*.

### 4. Authentication weaknesses you can observe

| Weakness | How it appears | Test |
| --- | --- | --- |
| User enumeration | Different message or timing for unknown vs known accounts | Register/login with a known-good and a definitely-unknown address |
| No lockout / no rate limit | Unlimited attempts | A bounded loop (20 attempts) and observe `429` or lockout |
| Weak password policy | One-character password accepted | Register with `a` |
| Default credentials | `admin`/`admin` works | Vendor documentation; test before anything clever |
| Predictable reset tokens | Short, numeric, time-based | Request two resets and compare |
| Reset token reuse | Token still valid after use | Use it twice |
| Host-header poisoning in reset links | Reset link points at an attacker-supplied host | Send `Host:` / `X-Forwarded-Host:` on the reset request |
| MFA bypass by response manipulation | `{"mfa_required":false}` accepted | Intercept and change the flag |
| MFA bypass by direct navigation | Post-MFA endpoint reachable before MFA | Skip the second step, request the dashboard |
| Credential stuffing exposure | No device or velocity signal | Reason about it; do not actually stuff credentials |

Two of these deserve emphasis because they are under-tested. **Enumeration through registration**: "this email is
already registered" is a disclosure. **Reset-flow host injection**: if the application builds the reset URL from
the `Host` header, an attacker can send a reset for a victim and have the link point at their own domain — the
victim clicks a genuine email and delivers the token.

### 5. Password storage: four questions

When you review password storage, ask in this order. Each has a specific failure mode.

1. **Is it a password hash, or encryption?** Encryption is reversible; a stolen key means every password. Passwords
   must be hashed with a slow, salted, memory-hard function.
2. **Which function?** Argon2id first, then scrypt or bcrypt. Never MD5, SHA-1, or plain SHA-256 — those are fast
   by design, which is exactly wrong here. A GPU tests billions of SHA-256 candidates per second.
3. **Is it salted, per user?** A unique random salt defeats precomputed tables and makes identical passwords hash
   differently. A single global "pepper" appended to every password is not a salt.
4. **Is the work factor current?** A bcrypt cost of 4 is technically bcrypt and practically useless. OWASP's
   Password Storage Cheat Sheet currently lists bcrypt with work factor 10 or more, Argon2id with at least 19 MiB
   of memory and 2 iterations (or 46 MiB and 1), and scrypt with N=2^17, r=8, p=1. Check the current guidance
   when you write the report — these numbers move with hardware.

```python
# Generating and verifying with a current library, for comparison in the lab
import bcrypt, argon2

hashed = bcrypt.hashpw(b"Lab-Passw0rd-303", bcrypt.gensalt(rounds=12))
bcrypt.checkpw(b"Lab-Passw0rd-303", hashed)          # True

ph = argon2.PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
ph.verify(ph.hash("Lab-Passw0rd-303"), "Lab-Passw0rd-303")
```

Two implementation details that belong in a code review, not a penetration test:

- **Compare in constant time** where you compare secrets (`hmac.compare_digest`). A byte-by-byte comparison leaks
  timing.
- **Do not log the password**, not even in a debug branch, and not in an error object that gets serialised.

### 6. Session lifecycle

A session is a claim with a lifetime. Four properties make it trustworthy, and each is observable:

| Property | Expected | How to test |
| --- | --- | --- |
| Issued only after authentication | No session cookie with privileges before login | Capture cookies at the login page |
| **Regenerated at login** | New identifier after successful auth | Compare pre- and post-login values |
| Bounded lifetime | `Max-Age`, idle timeout, absolute timeout | Leave a session idle; observe expiry |
| Revocable | Logout invalidates server-side | Replay the old cookie after logout |

Session fixation is worth spelling out because the attack is unintuitive: the attacker obtains a session
identifier *before* the victim logs in, plants it in the victim's browser (via a link, a subdomain, or a
vulnerable parameter), and then waits. If the application does not issue a **new** identifier at authentication,
the attacker's identifier is now an authenticated session. The fix is one line in most frameworks — regenerate on
login — and its absence is invisible unless you test for it.

### 7. CSRF, mechanically

CSRF exploits two facts: browsers attach cookies to cross-site requests automatically, and the attacker does not
need to read the response — only to cause the request.

The classic target is a state-changing request that relies solely on the session cookie:

```html
<!-- On an attacker-controlled page the victim visits -->
<form action="http://192.0.2.30:4280/vulnerabilities/csrf/" method="GET">
  <input name="password_new" value="attacker-chosen">
  <input name="password_conf" value="attacker-chosen">
</form>
<script>document.forms[0].submit()</script>
```

If the victim is logged in, their cookie rides along and the password changes. Note that this example uses
`GET`: state-changing `GET` is the worst case, because it can be triggered by an `<img>` tag with no form at all.

**The controls, in order of strength:**

| Control | How it works | Failure mode |
| --- | --- | --- |
| Synchroniser token | Per-session random token in the form, compared server-side | Token not validated; token leaked in URL; token reusable across users |
| Double-submit cookie | Same value in a cookie and a request field | Subdomain can set cookies; value not bound to the session |
| `Origin`/`Referer` validation | Reject requests whose origin is not yours | `Referer` absent → must fail closed, not open |
| `SameSite=Lax`/`Strict` | Browser refuses to send cookies cross-site | `Lax` allows top-level GET; older browsers; same-site subdomains |
| Custom header requirement | JSON APIs reject `text/plain` form posts | Only works if the endpoint truly refuses simple requests |

`SameSite` is the reason CSRF is less common than it was, and the reason juniors now under-test it. Treat it as
defence in depth: report a missing token as the finding, and `SameSite` as the mitigation that currently limits
impact.

For JSON APIs there is a useful structural control: require `Content-Type: application/json` and reject
`text/plain`, because a cross-site HTML form cannot send the former without a CORS preflight. That, plus an
`Origin` check, is a defensible design — but only if the server actually enforces the content type.

---

## Worked example: the one-request finding

A Juice Shop basket belongs to a user. The endpoint is `GET /rest/basket/{id}`, and the identifier is sequential.

**Step 1 — establish two identities.** Register `learner303a@lab.test` and `learner303b@lab.test`. Log in as A
and add an item to the basket.

**Step 2 — capture A's own request.**

```bash
A='http://192.0.2.30:3000'
curl -sS -c evidence/a.jar -X POST "$A/rest/user/login" \
  -H 'Content-Type: application/json' \
  --data '{"email":"learner303a@lab.test","password":"Lab-Passw0rd-303"}' > /dev/null

curl -sS -b evidence/a.jar "$A/rest/basket/1" | jq '{id, UserId, Products: [.Products[].name]}'
```

**Step 3 — as B, request the same object.**

```bash
B='http://192.0.2.30:3000'
curl -sS -c evidence/b.jar -X POST "$B/rest/user/login" \
  -H 'Content-Type: application/json' \
  --data '{"email":"learner303b@lab.test","password":"Lab-Passw0rd-303"}' > /dev/null

curl -sS -b evidence/b.jar -o evidence/b-basket.txt -w 'status=%{http_code}\n' "$B/rest/basket/1"
head -c 400 evidence/b-basket.txt
```

**Expected:** `status=200` and a body containing A's basket, including the item A added. B never had access to
that basket through the UI.

**Step 4 — write the finding so it cannot be argued with.** Include: the exact request as B, the response
proving it is A's object, the mechanism (the handler resolves the basket by path parameter and does not compare
it to the session subject), the impact (any authenticated user reads any other user's basket; the same pattern on
an invoice or message endpoint is a data breach), and the fix (`WHERE user_id = :session_user`).

Note what you must *not* write: "IDOR vulnerability, CVSS 8.1". The number without the argument is the reason
reports get disputed.

---

## Defender's view

| Signal | Source | Meaning |
| --- | --- | --- |
| Sequential object access by one session | Application access log with `user_id` and object id | Enumeration or IDOR testing |
| `403`/`404` spikes per session | WAF, app logs | Someone mapping authorization boundaries |
| Many logins, one account, distributed IPs | Auth logs | Credential stuffing |
| Many logins, many accounts, one IP | Auth logs | Password spraying |
| Login success followed by role change | Audit log | Privilege escalation attempt |
| Password change without prior authenticated session | App audit log | CSRF, or a broken reset flow |
| Session cookie value reused after logout | Session store, logs | Revocation failure or replay |
| Reset requests with unusual `Host` header | Reverse proxy logs | Host-header poisoning |

Design-side controls that remove whole categories: authorize in the data query; deny by default with an explicit
route allowlist; regenerate session IDs at every privilege change; bind CSRF tokens to the session; and log
authorization failures with subject, object, and decision, so that "was this allowed?" is answerable after the
fact.

---

## Common mistakes

1. **Testing with one account.** Without a second identity you cannot distinguish a missing object from a missing
   check. Two accounts, always.
2. **Only testing the UI.** The button is gone; the endpoint is not. Use the API, and read the JavaScript bundle
   to find routes the UI never links.
3. **Reporting `200` as IDOR.** A `200` with no data is not access. The evidence is another user's data in the
   body.
4. **Calling SHA-256 "hashed, therefore fine".** Fast hashes are the vulnerability. Salt and work factor are part
   of the control.
5. **Treating `SameSite` as a CSRF fix.** It is a browser default that limits the attack; the token is the control.
6. **Ignoring the reset flow.** It is an authentication path with its own token, expiry, and host-header risks, and
   it is frequently the weakest one.

---

## Practice

1. [LAB-303-01 · Insecure Login Workflow](lab-01-insecure-login-workflow.md) — enumeration, rate limiting, policy,
   and storage, measured.
2. [LAB-303-02 · Broken Access Control and IDOR](lab-02-broken-access-control.md) — two identities, object
   comparison, forced browsing.
3. [LAB-303-03 · Cross-Site Request Forgery](lab-03-csrf.md) — a working CSRF, then a token that stops it.

**Stretch task.** Find one endpoint in Juice Shop that returns `401` without a token and `200` with any valid
token, then determine whether the returned data is scoped to your account. Write the two requests and the
conclusion in four sentences.

## Knowledge check

1. A login page returns `401` for every invalid attempt. Why is that not sufficient to rule out user enumeration?
2. Name the difference between vertical and horizontal privilege escalation, with one example each.
3. You change `?id=5` to `?id=6` and get a `200` with an empty JSON array. Is that an IDOR? What else do you need
   to know?
4. Why is a UUID not an access control?
5. Give the two reasons bcrypt at cost 4 fails as a password-storage control.
6. An application regenerates the session ID at login. Which attack does that defeat, and why does the timing
   matter?
7. Explain, in two sentences, why `SameSite=Lax` does not prevent CSRF on a state-changing `GET`.
8. A JSON API checks the `Origin` header but allows requests with no `Origin` at all. What is the flaw?

## Summary

- Authentication answers who; authorization answers what, to which object. Most breaches are the second.
- Deny by default, authorize in the query, and check the object rather than the route.
- IDOR is proven by a second identity receiving the first identity's data.
- Password storage is judged by algorithm, per-user salt, work factor, and comparison method.
- Sessions must be regenerated at login, bounded in lifetime, and revocable.
- CSRF tokens are the control; `SameSite` and `Origin` checks are layered mitigations.

## References

1. OWASP Top 10:2025 — A01 Broken Access Control, A07 Authentication Failures. <https://owasp.org/Top10/2025/>
2. OWASP ASVS 5.0 — V6 Authentication, V7 Session Management, V8 Authorization. <https://asvs.owasp.org/>
3. OWASP WSTG v4.2 — WSTG-ATHZ-04 (IDOR), WSTG-SESS-03 (Fixation), WSTG-SESS-05 (CSRF).
4. OWASP Password Storage Cheat Sheet. Accessed 2026-10-29.
5. OWASP Cross-Site Request Forgery Prevention Cheat Sheet. Accessed 2026-10-29.

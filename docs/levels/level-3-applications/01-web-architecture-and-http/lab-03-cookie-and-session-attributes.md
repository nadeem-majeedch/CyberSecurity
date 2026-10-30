---
title: "LAB-301-03 · Evaluate Cookie and Session Attributes"
description: "Collect Set-Cookie headers from two applications, test each attribute's effect, and record the risk of every omission."
module_code: CYB-301
level: 3
kind: lab
prerequisites: [CYB-301]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-301-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [cookies, sessions, samesite, httponly, session-fixation]
---

# LAB-301-03 · Evaluate Cookie and Session Attributes

## Scenario and background

A colleague's report says: "Session cookie is missing the HttpOnly and Secure flags. Severity: Medium." The
client's developer replies: "We use TLS everywhere, so it doesn't matter, and it's only a session ID."

Both documents are weak. The first states an observation without an attack path; the second confuses transport
encryption with protection from script. Your job in this lab is to produce the version that survives that
conversation: for each attribute, the observed value, the requirement, the concrete consequence, and the test
that demonstrates it.

You will assess two applications with different session designs — DVWA (server-side PHP session) and Juice Shop
(signed JWT) — which is exactly the contrast that makes the concepts stick.

## Learning objectives

By the end of this lab you can:

1. Extract and interpret every `Set-Cookie` header an application issues.
2. Test whether a cookie is readable by script, sent cross-site, and revoked at logout.
3. Determine whether the session identifier changes at authentication.
4. Decide whether a token's contents are claims or secrets, and explain the difference.
5. Produce a session-attribute table with a stated risk for each omission.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Firefox with devtools | current | Application → Storage → Cookies |
| Burp Suite Community | 2026.10.1 | Or ZAP 2.17.0 |
| `curl`, `jq`, `base64` | standard | Header and token inspection |
| DVWA | current `master` | `http://192.0.2.30:4280` |
| Juice Shop | 20.3.0 | `http://192.0.2.30:3000` |
| Python 3 | 3.10+ | Serve the cross-site test page |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `192.0.2.30:3000`, `192.0.2.30:4280`, and a five-line static page you serve
    yourself on `192.0.2.10:8000`.
    **Targets you must not use:** any other host. The cross-site test deliberately imitates an attacker page —
    it must only ever point at your own lab.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The simulated adversary has two capabilities: they can run script in the victim's browser origin (XSS), and they
can host a page the victim visits (CSRF). Every attribute you evaluate is a control against one of those two.
Nothing here requires an exploit to succeed; you are measuring whether the control exists.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Browser, proxy, static test page | 192.0.2.10 |
| `lab-web` | DVWA, Juice Shop | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                        lab-web 192.0.2.30
  :8000 cross-site probe page ──▶ :3000 Juice Shop
                              └──▶ :4280 DVWA
```

## Before you start

1. Log in to DVWA at **Security level: Low** (from LAB-301-01).
2. Have a Juice Shop account ready.
3. Create `evidence/` and `evidence/session-attributes.md`.

## Procedure

### 1. Collect the raw headers

```bash
DVWA='http://192.0.2.30:4280'
JUICY='http://192.0.2.30:3000'
mkdir -p evidence

# DVWA: capture the Set-Cookie issued on the login page
curl -sS -i -c evidence/dvwa.jar "$DVWA/login.php" | tee evidence/dvwa-login-headers.txt

# Juice Shop: log in and capture the token cookie
curl -sS -i -c evidence/juice.jar -X POST "$JUICY/rest/user/login" \
  -H 'Content-Type: application/json' \
  --data '{"email":"learner301@lab.test","password":"Lab-Passw0rd-301"}' \
  | tee evidence/juice-login-headers.txt
```

Read only the `Set-Cookie` lines:

```bash
grep -i '^set-cookie' evidence/*-login-headers.txt
```

**Expected shape** (attribute sets vary by version — record *yours*):

```text
set-cookie: PHPSESSID=8m2...; path=/
set-cookie: token=eyJhbGciOiJIUzI1NiIs...; Path=/
```

Neither line carries `HttpOnly`, `Secure`, or `SameSite` in the default lab configuration. That is the subject of
the rest of the lab — not the conclusion.

### 2. Decide what the cookie is

Two very different objects, two different analyses.

```bash
# DVWA — opaque identifier, no structure
value=$(grep -i '^set-cookie: PHPSESSID' evidence/dvwa-login-headers.txt | sed 's/.*PHPSESSID=\([^;]*\).*/\1/')
echo "${#value} chars: $value"

# Juice Shop — three base64url segments
grep -i '^set-cookie: token' evidence/juice-login-headers.txt | sed 's/.*token=\([^;]*\).*/\1/' > evidence/token.txt
cut -d. -f2 evidence/token.txt | tr '_-' '/+' | base64 -d 2>/dev/null | jq .
```

**Expected:** the DVWA value is a short random-looking string with no readable meaning. The Juice Shop value
decodes to JSON containing an identity and a role.

**Why this matters:** the DVWA session ID is a *secret lookup key* — its only security property is
unguessability. The Juice Shop token is a *signed claim set* — its security properties are signature
verification and expiry, and its contents are readable by anyone who holds it. Confusing the two produces bad
findings, such as reporting "the cookie contains an email address" as a disclosure issue.

### 3. Test readability by script (the `HttpOnly` question)

In the browser, log in to each application, open devtools → **Console**, and run:

```javascript
document.cookie
```

**Expected:** DVWA's `PHPSESSID` is absent (PHP sets `HttpOnly` by default in recent versions); Juice Shop's
`token` is present. Record exactly what you see — this is the experiment that turns "missing HttpOnly" into
"any XSS can exfiltrate the session".

Then state the consequence precisely: with XSS present, `document.cookie` is exfiltration; without XSS, the
missing attribute has no immediate attack path and should be reported as a defence-in-depth gap, not a
vulnerability. Both statements are useful; only one is honest about severity.

### 4. Test cross-site sending (the `SameSite` question)

Serve a page from a *different origin* — same host is not enough, and a different port is a different origin:

```bash
mkdir -p ~/lab/level-3/lab-301-03/xsite && cd ~/lab/level-3/lab-301-03/xsite
cat > index.html <<'HTML'
<!doctype html><meta charset="utf-8"><title>xsite probe</title>
<h1>Cross-site probe</h1>
<img src="http://192.0.2.30:4280/index.php" alt="probe" width="1" height="1">
<img src="http://192.0.2.30:3000/rest/user/whoami" alt="probe" width="1" height="1">
HTML
python3 -m http.server 8000 --bind 192.0.2.10
```

With Burp intercepting, open `http://192.0.2.10:8000/` in your proxied profile while logged in to both
applications. Inspect the two requests the browser makes to `192.0.2.30`.

**Expected:** if the session cookies carry no `SameSite` attribute, the browser sends them on these subresource
requests. Note that a modern browser may apply a default (`Lax`) when the attribute is absent — check the
**Cookies** tab in devtools for the value the browser actually uses, which is not always what the server
appeared to omit. This distinction between *server-declared* and *browser-applied* policy is a common source of
wrong findings.

Then stop the server (`Ctrl+C`) so the probe page cannot be revisited by accident.

### 5. Test session identifiers at authentication

1. Note the cookie value on the DVWA login page (unauthenticated).
2. Log in.
3. Note the value again.

```bash
# Unauthenticated value
curl -sS -i -c evidence/pre.jar "$DVWA/login.php" | grep -i '^set-cookie'
# After a login POST using that jar
curl -sS -i -b evidence/pre.jar -c evidence/post.jar -X POST "$DVWA/login.php" \
  --data 'username=admin&password=password&Login=Login' | grep -i '^set-cookie'
```

**Expected:** a different value after login — the identifier was regenerated, which defeats session fixation.

If a value stayed the same across privilege change, the test for exploitation is: can an attacker who knows the
pre-login identifier use it afterwards? That is [WSTG-SESS-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation).

### 6. Test revocation at logout

Stateless tokens have a known weakness: the server cannot easily forget them.

```bash
TOKEN=$(cat evidence/token.txt)
# 1. Confirm the token works
curl -sS -o /dev/null -w 'before=%{http_code}\n' -H "Authorization: Bearer $TOKEN" "$JUICY/rest/user/whoami"

# 2. Log out through the API, using that token
curl -sS -o /dev/null -w 'logout=%{http_code}\n' -X POST -H "Authorization: Bearer $TOKEN" "$JUICY/rest/user/logout"

# 3. Replay the old token
curl -sS -o /dev/null -w 'after=%{http_code}\n' -H "Authorization: Bearer $TOKEN" "$JUICY/rest/user/whoami"
```

**Expected:** `before=200`, and `after=200` on a stateless implementation — the old token remains valid until it
expires. Record the observed behaviour and explain the design reason rather than calling it a bug: this is the
trade-off described in the lesson. The reportable statement is about **residual risk** (a stolen token survives
logout for its full lifetime) and the **mitigation** (short expiry, rotation, or a server-side denylist).

### 7. Check caching of authenticated responses

```bash
curl -sS -i -b evidence/juice.jar "$JUICY/rest/basket/1" | grep -iE '^(cache-control|pragma|expires)'
```

**Expected:** either an explicit `no-store`, or no caching header at all. A shared computer with a browser cache
is a real, unglamorous data-exposure path — and `no-store` on authenticated responses is a one-line fix.

### 8. Complete the attribute table

For each application, fill every row. "Required" is your judgement, defended in the notes column.

| Attribute | DVWA observed | Juice Shop observed | Required? | Risk if absent |
| --- | --- | --- | --- | --- |
| `Secure` | | | Yes (production TLS) | Cookie sent over plaintext if any HTTP path exists |
| `HttpOnly` | | | Yes for session cookies | XSS becomes session theft |
| `SameSite` | | | `Lax` minimum | Cross-site requests carry the session |
| `Domain` | | | Omit unless needed | Widened to sibling hosts |
| `Path` | | | `/` for app-wide sessions | Not a control; note if over-broad |
| `Max-Age` / `Expires` | | | Bounded | Stolen session lives indefinitely |
| Prefix (`__Host-`) | | | Preferred | Weaker guarantees on scope and transport |
| Regenerated at login | | | Yes | Session fixation |
| Invalidated at logout | | | Yes, or short expiry | Replay after logout |

## Evidence to collect

- `evidence/dvwa-login-headers.txt`, `evidence/juice-login-headers.txt` — raw responses.
- `evidence/token.txt` plus the decoded claims, **with any signature removed** before you paste it anywhere.
- `evidence/session-attributes.md` — the completed table.
- `evidence/tests.md` — the five experiments (script readability, cross-site send, login rotation, logout replay,
  cache headers) with the observed result and the interpretation.
- A screenshot of devtools' Cookies panel showing the browser-applied `SameSite` value.

## Verification

- [ ] Both applications' `Set-Cookie` headers are captured verbatim.
- [ ] You have classified each cookie as opaque identifier or signed claim, with evidence.
- [ ] `document.cookie` result recorded for both applications.
- [ ] Cross-site probe observed in the proxy, and the browser-applied `SameSite` value recorded separately from
      the server-declared one.
- [ ] Login rotation tested on DVWA; logout replay tested on Juice Shop.
- [ ] All nine rows of the table filled for both applications.

## Teardown and reset

```bash
rm -rf ~/lab/level-3/lab-301-03/xsite
rm -f evidence/pre.jar evidence/post.jar
```

Stop the Python server if it is still running. Leave the applications running for CYB-302. Revert
`pre-lab-301-03` if you changed DVWA's security level or created extra accounts you no longer need.

## Reflection

1. `Secure` does nothing on a plain-HTTP lab target. Why is it still correct to report its absence in a
   production review, and what evidence would you need before doing so?
2. The Juice Shop token cannot be revoked by logout. Argue for and against calling that a vulnerability, in one
   sentence each.
3. `Path=/admin` scopes a cookie to a directory. Give a concrete scenario showing why that is not an
   authorization control.
4. Your colleague wrote "missing HttpOnly, Medium". Rewrite that finding so it states impact, precondition, and
   fix in three sentences.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Completeness | Fewer than five attributes | All nine rows, both apps | All rows plus the browser-applied `SameSite` distinction |
| Experimental support | Asserts attributes from memory | Header evidence captured | Each claim backed by a specific test and its output |
| Severity reasoning | "Missing flag = Medium" | Consequence stated | Precondition, impact, and false-positive boundary all stated |
| Fix quality | "Add HttpOnly" | Attribute names given | Exact `Set-Cookie` string proposed, with the mechanism named |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `grep` finds no `Set-Cookie` | Application did not set a cookie on that response | Use the login POST, not the login page, for Juice Shop |
| `base64 -d` prints garbage | Padding or URL-safe alphabet | `tr '_-' '/+'` then append `=` until length is a multiple of 4 |
| `document.cookie` shows nothing at all | Cookies are `HttpOnly` **or** you are on a different origin in the console context | Check the devtools Application tab; confirm the console's execution context |
| Cross-site probe sends no cookie | Browser applied `Lax` by default, or the image was cached | Disable cache, reload, and compare with the Cookies panel |
| Logout replay returns `401` | Implementation keeps a denylist | Record it — that is a *better* design; state the trade-off |
| DVWA login POST fails with `302` | Wrong field names | Inspect the real form in devtools and copy the field names |

## References

1. RFC 6265 — HTTP State Management Mechanism, §4.1 (Set-Cookie syntax).
2. OWASP WSTG v4.2 — WSTG-SESS-02 Testing for Cookies Attributes; WSTG-SESS-03 Session Fixation; WSTG-SESS-06
   Logout Functionality.
3. OWASP Top 10:2025 — A07 Authentication Failures. <https://owasp.org/Top10/2025/>
4. MDN — Set-Cookie; SameSite cookies. Accessed 2026-10-29.

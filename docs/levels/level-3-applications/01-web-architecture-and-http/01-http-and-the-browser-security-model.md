---
title: "HTTP, Sessions and the Browser Security Model"
description: "Read requests and responses as trust decisions: headers, cookies, sessions, same-origin policy, CORS and security headers."
module_code: CYB-301
level: 3
kind: lesson
prerequisites: [CYB-204]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-301-02, LAB-301-03]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [http, cookies, sessions, same-origin-policy, cors, csp, hsts]
---

# HTTP, Sessions and the Browser Security Model

**Level 3** · 180 minutes · **Prerequisites:** CYB-204 · **Labs:**
[Intercept a Session](lab-02-intercept-a-session.md) ·
[Cookie and Session Attributes](lab-03-cookie-and-session-attributes.md)

## Why this matters

When you are handed a finding of "session cookie missing HttpOnly", the useful part is not the observation —
it is the sentence that follows: *this means a single XSS becomes full account takeover, and here is the
header that fixes it*. That sentence requires knowing what the browser does with that attribute, which requires
knowing how HTTP actually carries state.

This lesson builds that model on one idea: **HTTP is stateless, so every request must re-prove who is asking,
and every mechanism that does so is a trust decision you can audit.** In an assessment, you will read those
decisions a few hundred times. Being fast and precise at it is most of the skill.

## Learning outcomes

By the end of this lesson you will be able to:

- Break a raw HTTP exchange into request line, headers, and body, and explain the purpose of each header present.
- Distinguish a session cookie from a bearer token, and state where each is validated.
- Explain the same-origin policy using scheme, host, and port, and predict which cross-origin operations a
  browser permits without CORS.
- Evaluate a CORS response for over-permissiveness and describe the exposure it creates.
- Judge `Set-Cookie` attributes and security headers against the specific attack each one mitigates.

## Prerequisites and setup

- `lab-analyst` (Kali) and `lab-web` (Ubuntu 22.04) with Juice Shop and DVWA running, from
  [LAB-301-01](lab-01-web-lab-setup.md).
- `curl` 7.81+, `jq` 1.6+, `openssl` 3.0+, Python 3.10+.
- Snapshot `pre-cyb301` taken before the first lab.

Throughout, the lab addresses are `192.0.2.30:3000` (Juice Shop) and `192.0.2.30:4280` (DVWA). `192.0.2.0/24`
is documentation space (RFC 5737): it cannot route on the public internet, which is exactly why it is used here.

---

## Core concepts

### 1. The shape of an exchange

Every HTTP interaction is one request and one response. Text, in both directions, until TLS encrypts the
channel (and even then, the bytes inside are the same text).

```http
GET /rest/products/search?q=apple HTTP/1.1
Host: 192.0.2.30:3000
User-Agent: curl/7.81.0
Accept: application/json
Cookie: token=eyJhbGciOiJIUzI1NiIs...
```

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 2314
Set-Cookie: token=...; Path=/
X-Content-Type-Options: nosniff
```

Read it in four passes, in this order. It becomes automatic within a week:

| Pass | Question | What you are looking for |
| --- | --- | --- |
| Request line | What is being asked for? | Method, path, query string — the *inputs* |
| Request headers | Who is asking, and with what? | `Cookie`, `Authorization`, `Origin`, `Referer`, custom headers |
| Status line | How did the server answer? | `200`, `302`, `401`, `403`, `500` — each means something different about authorization |
| Response headers | What is the server telling the browser to do? | `Set-Cookie`, `Content-Type`, CSP, HSTS, CORS |

Two habits to build now. First, **the query string and body are attacker-controlled by definition** — anything
the client sends can be changed, replayed, or omitted. Second, **a `302` to a login page is not an
authorization control**; it is a redirect. The control is the `403` on the endpoint itself, and you should test
for it directly rather than trusting the browser's experience.

### 2. Methods and status codes that carry security meaning

| Method | Safe? | Idempotent? | Security-relevant note |
| --- | --- | --- | --- |
| `GET` | yes | yes | Must not change state. State-changing `GET` is how CSRF becomes one click. |
| `HEAD` | yes | yes | Same headers, no body — useful for header review with less noise. |
| `POST` | no | no | The normal state-changing method; needs CSRF protection. |
| `PUT` / `PATCH` | no | yes / no | `PATCH` with a partial object is where mass assignment lives (CYB-308). |
| `DELETE` | no | yes | Authorization must be checked per object, not per route. |
| `OPTIONS` | yes | yes | CORS preflight; also reveals allowed methods when misconfigured. |

| Status | Meaning | What it usually tells a tester |
| --- | --- | --- |
| `200` | Success | The request was authorized *and* the object exists. |
| `201` | Created | Check what was created — including fields you did not send. |
| `301`/`302` | Redirect | Not a control. Follow it, and also request the target directly. |
| `401` | Not authenticated | Credential missing or invalid. |
| `403` | Authenticated, not authorized | The right answer. Its absence is the finding. |
| `404` | Not found | Can also be deliberate masking of a `403`. Compare with a known-good object. |
| `429` | Too many requests | Evidence that rate limiting exists. Test whether it is per-IP or per-account. |
| `500` | Server error | Verbose bodies leak stack traces, paths, and query text. |

A subtle but important asymmetry: a `404` for *your* object and `200` for *someone else's* proves an IDOR even
though nothing said "forbidden". Compare responses for two objects you do not have equal rights to — that is
[WSTG-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References).

### 3. State: sessions, cookies and tokens

HTTP has no memory. To recognise you across requests the server needs something it issued, sent back by the
client, that it can verify. There are exactly two families:

**Server-side sessions.** The cookie holds an opaque identifier. The server looks it up in a store (memory,
Redis, a database) and finds the user, roles, and expiry. The client cannot read or meaningfully alter it, and
revocation is a single delete. Most traditional applications work this way.

**Stateless tokens.** The cookie or `Authorization` header holds a signed structure — usually a JWT — containing
claims such as `sub`, `role`, and `exp`. The server verifies the signature and trusts the claims. Nothing is
stored server-side, which scales well and revokes badly: a token is valid until it expires unless you build a
denylist, which returns you to a server-side store with extra steps.

Neither is inherently secure. What matters for review:

1. **Where is it validated?** A signed token that is decoded but not verified, or verified without checking
   `alg` and `exp`, is just user input in a costume. That is [A07:2025 Authentication Failures](https://owasp.org/Top10/2025/).
2. **Can it be stolen?** `HttpOnly` stops JavaScript reading it; `Secure` stops it crossing plaintext HTTP;
   `SameSite` limits cross-site sending.
3. **Can it be fixed?** If the identifier does not change at login, an attacker who plants one before login
   inherits the authenticated session — session fixation, [WSTG-SESS-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation).

### 4. Cookie attributes, one at a time

`Set-Cookie` is a small policy document. Each attribute answers a different question, and each is defeated by a
different attack when missing.

```http
Set-Cookie: session=8f14e45fceea167a5a36dedd4bea2543; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=3600
```

| Attribute | Question it answers | If missing or wrong | Typical attack |
| --- | --- | --- | --- |
| `Secure` | May this travel over plaintext? | Cookie sent over `http://` | Network interception, mixed-content leak |
| `HttpOnly` | May JavaScript read it? | `document.cookie` exposes it | Any XSS escalates to session theft |
| `SameSite=Strict\|Lax\|None` | May another site cause it to be sent? | Cross-site sends allowed | CSRF |
| `Domain` | Which hosts receive it? | Defaults to exact host (safer); a parent domain widens exposure | Subdomain takeover, sibling-host XSS |
| `Path` | Which paths receive it? | Defaults to the setting path | Over-broad sending — a *scope* control, never an authorization control |
| `Max-Age` / `Expires` | When does the browser forget it? | Session cookie: lives until the browser closes | Long-lived stolen credentials |
| `__Host-` prefix | Enforces `Secure`, `Path=/`, no `Domain` | Prefix rejected by browser if violated | Downgrade and domain-scoping mistakes |

Two traps worth stating plainly, because both appear in real reports as false positives:

- **`Path` is not authorization.** A cookie scoped to `/app` is still sent by any script on the same host if it
  can navigate there. Never accept "the cookie is path-scoped" as a control.
- **`SameSite=Lax` is a strong default, not a CSRF fix.** It permits top-level `GET` navigation, so any
  state-changing `GET` remains exploitable. CSRF tokens are the control (CYB-303).

`SameSite=None` is only legitimate for genuinely cross-site embeds (payment widgets, SSO callbacks) and
**requires** `Secure`; browsers reject the combination otherwise. If you see `SameSite=None` on a first-party
session cookie, ask what the cross-site use case is — often there isn't one, and the attribute was added to
silence a console warning.

### 5. The same-origin policy

The single most misunderstood control in web security, and the one that decides what an XSS is worth.

An **origin** is the triple `(scheme, host, port)`. All three must match exactly.

| Page origin | Requested URL | Same origin? | Why |
| --- | --- | --- | --- |
| `https://app.test` | `https://app.test/admin` | Yes | Identical triple |
| `https://app.test` | `http://app.test/admin` | No | Scheme differs |
| `https://app.test` | `https://api.app.test/x` | No | Host differs (subdomain ≠ same host) |
| `https://app.test` | `https://app.test:8443/x` | No | Port differs |
| `http://192.0.2.30:3000` | `http://192.0.2.31:3000` | No | Host differs |

The policy is enforced by the **browser**, on **reads**, per **origin**. It does not prevent requests from being
*sent* — a form post or an `<img>` tag crosses origins freely. It prevents the *response* from being read by
script from another origin. That distinction is the whole basis of CSRF: the attacker does not need to read the
response, only to cause the request.

Three consequences you will use constantly:

1. **XSS defeats the SOP from inside.** Injected script runs in the victim origin, so it can read that origin's
   data and cookies (unless `HttpOnly`) and issue authenticated requests. This is why XSS is rated as it is.
2. **`document.domain` and loose postMessage handlers** re-open the boundary between subdomains. Audit both.
3. **CORS is a deliberate, server-controlled hole in the SOP.** It is not a vulnerability by itself; a
   misconfigured one is.

### 6. CORS: what it actually permits

By default, a cross-origin `fetch` is sent but the response is withheld from JavaScript. CORS lets the *server*
grant read access.

A **simple** request (a `GET` with no custom headers, or a form-encoded `POST`) is sent directly; the browser
checks the response for `Access-Control-Allow-Origin` before releasing it to script.

Anything else triggers a **preflight**: an `OPTIONS` request asking permission before the real one is sent.

```http
OPTIONS /api/profile HTTP/1.1
Origin: https://evil.test
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: content-type, authorization
```

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://evil.test
Access-Control-Allow-Methods: GET, PUT, DELETE
Access-Control-Allow-Headers: content-type, authorization
Access-Control-Allow-Credentials: true
```

That response is a finding, and the reason is specific: any site can now read this API **with the victim's
cookies**, because `Allow-Credentials: true` is combined with a reflected `Origin`. The correct fix is an
exact allowlist of first-party origins, and — for sensitive APIs — no CORS at all.

The rules that matter when you assess:

| Pattern | Verdict |
| --- | --- |
| `Access-Control-Allow-Origin: *` with no credentials | Readable by anyone. Acceptable only for genuinely public data. |
| `*` plus `Access-Control-Allow-Credentials: true` | Ignored by browsers — wildcard is illegal with credentials. Not exploitable, still a smell. |
| Origin reflected from the request | Cross-origin read for any site. **High severity** with credentials. |
| `null` origin allowed | Exploitable from sandboxed iframes and `file://` documents. |
| Allowlist checked with `endsWith(".app.test")` | Bypassed by `evil-app.test`. Check with a parser, compare full origins. |

### 7. Security headers that carry weight

Headers do not replace correct code. They reduce the impact of the mistakes you will inevitably ship, and their
absence is legitimate evidence in a report.

| Header | Effect | Notes for assessment |
| --- | --- | --- |
| `Content-Security-Policy` | Restricts sources for script, style, frame, connection | `unsafe-inline` and `unsafe-eval` largely negate it; nonces or hashes are the modern approach |
| `Strict-Transport-Security` | Forces HTTPS for `max-age` seconds | Only honoured over HTTPS; `includeSubDomains` widens blast radius if a subdomain is HTTP-only |
| `X-Content-Type-Options: nosniff` | Stops MIME sniffing | Cheap, always appropriate |
| `X-Frame-Options: DENY` / `frame-ancestors 'none'` | Blocks framing | Clickjacking control; CSP's `frame-ancestors` is the current mechanism |
| `Referrer-Policy: no-referrer` or `strict-origin-when-cross-origin` | Controls URL leakage | Tokens in URLs leak through `Referer` to third parties |
| `Permissions-Policy` | Disables browser features (camera, geolocation) | Reduces impact of injected script |
| `Cache-Control: no-store` | Prevents caching of sensitive responses | Auth pages and API responses carrying personal data |

CSP deserves one paragraph of honesty. A policy of `default-src *; script-src 'unsafe-inline'` is decoration;
report it as such rather than as a control. A policy with `script-src 'nonce-<random>' 'strict-dynamic'` genuinely
blocks injected inline script. When you test, the question is not "is CSP present" but "would this policy have
blocked the payload I just executed". That comparison is the evidence.

### 8. Seeing it: devtools, proxy, and `curl`

Three views of the same traffic, each with a different purpose:

- **DevTools → Network** — what the browser did, including redirects, timing, and the exact headers sent.
  Enable *Preserve log* before a login flow, or the navigation wipes the evidence.
- **A proxy (Burp or ZAP)** — what you can *change*. Interception lets you alter a request after the browser
  built it and before the server sees it, which is how you test server-side validation rather than client-side.
- **`curl`** — what is reproducible. A finding is not confirmed until you can replay it without a GUI, because
  that replay is what goes in the report appendix.

The professional habit is to confirm every finding with at least two of the three. If devtools shows a
restriction, `curl` proves whether it was client-side only. If Burp shows a `403`, `curl` shows whether the
`403` depended on a header you can simply omit.

---

## Worked example: reading a login as a trust exercise

Start with the raw exchange, unauthenticated, against the lab's Juice Shop instance.

```bash
curl -sS -i -X POST 'http://192.0.2.30:3000/rest/user/login' \
  -H 'Content-Type: application/json' \
  --data '{"email":"learner@lab.test","password":"not-the-real-one"}'
```

Expected shape (values vary; the structure does not):

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json; charset=utf-8
X-Content-Type-Options: nosniff

{"status":"error","message":"Invalid email or password."}
```

Three observations, each a separate hypothesis:

1. `401` with a generic message — no user enumeration *in the message*. Test the timing next, because a
   lookup-then-compare path is often slower for unknown users.
2. `X-Content-Type-Options` present — the framework is doing something right; note it, do not over-credit it.
3. No `Set-Cookie` — expected on failure. Success is where the session policy appears.

Now the success path. Create an account first (Juice Shop's registration is at `/register`), then:

```bash
curl -sS -i -c /tmp/lab301.cookies -X POST 'http://192.0.2.30:3000/rest/user/login' \
  -H 'Content-Type: application/json' \
  --data '{"email":"learner@lab.test","password":"Lab-Passw0rd-301"}'
```

Expected shape:

```http
HTTP/1.1 200 OK
Set-Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; Path=/
```

Read that `Set-Cookie` the way you would read a policy:

- It is a **JWT**, not an opaque identifier — so the server is likely trusting claims, not a store. Check whether
  the payload is readable. A JWT is signed, not encrypted: `sub`, `email`, and `role` are plain base64url.
- There is **no `HttpOnly`** in this instance. That single omission converts any XSS into account takeover; it
  belongs in the report with that sentence attached, not as "cookie missing HttpOnly".
- There is **no `SameSite`** and no `Secure`, which is consistent with an app served over plain HTTP for
  training. In a production deployment over TLS, both absences would be findings.

Decoding the payload is a one-liner and requires no secret — which is the point:

```bash
# Split, decode, and read the claims (no verification: we are inspecting, not trusting)
cut -d. -f2 <<< "$TOKEN" | tr '_-' '/+' | base64 -d 2>/dev/null | jq .
```

**Why this matters:** you have now moved from "there is a cookie" to a specific, defensible statement about
what an attacker gains from one XSS. That is the level of analysis the Level 3 report expects.

---

## Defender's view

| Signal | Where it appears | Why a defender cares |
| --- | --- | --- |
| Cookie without `HttpOnly` | Response headers, or a scanner finding | Any XSS becomes session theft |
| Reflected `Origin` in CORS | Response headers on `OPTIONS` | Cross-origin read with victim credentials |
| Missing `Content-Security-Policy` | Response headers | Injected script executes unfettered |
| Login `401` counts per IP and per account | Reverse-proxy logs, WAF | Distinguishes credential stuffing from a user typo |
| Session ID unchanged after login | Application logs, cookie history | Session fixation |
| `Set-Cookie` on every response | Response headers | Session churn; can indicate a misconfigured store |

Defensive defaults worth memorising, because they are what you recommend in reports: TLS everywhere with HSTS;
`Secure; HttpOnly; SameSite=Lax` (or `Strict`) on session cookies; `__Host-` prefix where possible; an exact
CORS allowlist; a nonce-based CSP; `Cache-Control: no-store` on authenticated responses; and session identifiers
regenerated at every privilege change.

---

## Common mistakes

1. **Treating `403` on the page as `403` on the API.** Single-page apps often hide the button while the endpoint
   happily serves the data. Test the endpoint, not the UI.
2. **Calling every missing header a vulnerability.** A missing `X-Frame-Options` on a JSON API that cannot be
   framed is noise. Tie each header finding to an attack path that exists.
3. **Assuming `Secure` means encrypted storage.** It governs transport only. Cookies sit in a local database,
   often readable by anyone with the profile.
4. **Believing `HttpOnly` prevents CSRF.** It does not; the browser still sends the cookie. `SameSite` and tokens
   address CSRF.
5. **Reading a JWT as if it were trusted evidence.** Decoding tells you what the server *claims*. Only a
   verification failure test tells you whether claims are checked.
6. **Proxying your normal browser.** Use a separate browser profile with the proxy CA installed only there, or
   you will eventually send personal traffic through a tool designed to log everything.

---

## Practice

Complete, in order:

1. [LAB-301-01 · Build the Web Lab](lab-01-web-lab-setup.md) — containers, loopback/lab binding, isolation proof.
2. [LAB-301-02 · Intercept and Annotate a Session](lab-02-intercept-a-session.md) — proxy setup, full-flow capture.
3. [LAB-301-03 · Evaluate Cookie and Session Attributes](lab-03-cookie-and-session-attributes.md) — the attribute
   table and the header review that feeds your report.

**Stretch task.** Write a five-line `curl`-only script that logs in, stores the cookie jar, and requests a
protected endpoint with and without the cookie, printing both status codes. You will reuse it in CYB-303 and
CYB-308; make it a file, not a shell history entry.

## Knowledge check

1. A cookie is set with `Domain=.app.test`. Which hosts receive it, and what new risk does that create?
2. `Access-Control-Allow-Origin: *` is returned on an endpoint that requires no credentials. Is this a
   vulnerability? Justify your answer in one sentence.
3. A response includes `Access-Control-Allow-Credentials: true` and reflects the request's `Origin`. What can an
   attacker do, and what exactly must the fix compare?
4. Why does `SameSite=Lax` not eliminate CSRF on an application that changes state with `GET`?
5. You see `Set-Cookie: session=...; Path=/admin`. Does that prevent an XSS on `/` from reading it? Why not?
6. The login endpoint returns `401` for a wrong password and `200` with an empty body for an unknown user. Name
   the flaw and the two observations that prove it.
7. What is the difference between a JWT being *signed* and being *verified*, and which one causes
   authentication bypass when it is missing?
8. Which single header most directly reduces the impact of an XSS, and what makes a policy ineffective?

## Summary

- HTTP is stateless; every request must re-prove identity, and each mechanism doing so is auditable.
- An origin is `(scheme, host, port)`; the SOP restricts *reads*, not requests, which is why CSRF works.
- CORS is a server-granted exception to the SOP; reflected origins with credentials are high severity.
- Cookies are policy documents: `Secure` (transport), `HttpOnly` (script), `SameSite` (cross-site), `Domain`
  and `Path` (scope), `Max-Age` (lifetime).
- Missing headers are evidence only when tied to an attack path; CSP is a control only when it would have blocked
  your payload.

## References

1. RFC 9110 — HTTP Semantics. IETF, June 2022. <https://www.rfc-editor.org/rfc/rfc9110>
2. RFC 6265 — HTTP State Management Mechanism. IETF, 2011; and RFC 6265bis draft.
3. OWASP Top 10:2025 — A01 Broken Access Control, A07 Authentication Failures. <https://owasp.org/Top10/2025/>
4. OWASP WSTG v4.2 — WSTG-SESS-02, WSTG-SESS-03, WSTG-CONF-07. Accessed 2026-10-29.
5. MDN — Same-origin policy. <https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy> Accessed 2026-10-29.
6. PortSwigger Web Security Academy — CORS and same-origin policy. Accessed 2026-10-29.

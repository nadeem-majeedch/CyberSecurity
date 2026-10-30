---
title: "Authorization, Tokens and Resource Limits"
description: "Object, function and property authorization in APIs, JWT validation requirements, and rate limiting that actually limits."
module_code: CYB-308
level: 3
kind: lesson
prerequisites: [CYB-303]
estimated_minutes: 210
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-308-01, LAB-308-02]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [api-security, bola, bfla, mass-assignment, jwt, rate-limiting]
---

# Authorization, Tokens and Resource Limits

**Level 3** · 210 minutes · **Prerequisites:** CYB-303 · **Labs:**
[API Authorization](lab-01-api-authorization.md) ·
[Mass Assignment and Rate Limiting](lab-02-mass-assignment-and-rate-limiting.md)

## Why this matters

A web page hides what you cannot do. An API does not. Every object it can return and every operation it can
perform is one well-formed request away, and the only control is the check the server makes when that request
arrives. When the check is missing, the finding is a single line — `GET /api/orders/1041` — and the impact is
whatever that endpoint could have done for its rightful owner.

The same applies to tokens and limits. A token that is decoded but not verified is an identity claim written by
the client. A rate limit keyed on the wrong thing is a rate limit that stops nobody.

## Learning outcomes

By the end of this lesson you will be able to:

- Build an endpoint matrix from an API's routes, methods, and object references.
- Test and distinguish object-level, function-level, and property-level authorization failures.
- Identify mass assignment from field behaviour rather than guesswork.
- List the validation steps a JWT must pass, and the specific bypass each omission enables.
- Specify rate limiting with the correct key, scope, and response, and test whether it exists.

## Prerequisites and setup

- Juice Shop running; two accounts you created.
- `curl`, `jq`; a proxy for the requests that need editing.
- The access-control vocabulary from [CYB-303](../03-access-control-and-authentication/index.md).

---

## Core concepts

### 1. What changes with an API, and what does not

Nothing about the underlying flaw classes changes. Injection is still injection, IDOR is still IDOR. What changes
is **reachability and visibility**:

| Web application | API |
| --- | --- |
| Routes discovered by crawling links | Routes discovered from JavaScript bundles, OpenAPI documents, and mobile clients |
| Controls partly in the UI | No UI; the server is the only control |
| Responses are HTML for humans | Responses are structured data, often including fields the UI never shows |
| One origin, cookie-based session | Multiple clients, tokens in headers, CORS decisions |
| Rate limiting often at the page level | Per-operation, per-token, per-tenant |

The practical consequence: **an API assessment is mostly an inventory exercise followed by an authorization
exercise.** Find the routes, then ask who may do what to which object, for each one.

### 2. Build the matrix before you test

From the sitemap, the JavaScript bundle, or an OpenAPI/Swagger document, list every endpoint. For each, record:

| Method | Path | Identity required | Object reference | Role required | Notes |
| --- | --- | --- | --- | --- | --- |
| `GET` | `/rest/basket/{id}` | yes | `id` (numeric) | user | Returns basket contents |
| `GET` | `/api/Users` | yes | none | **admin?** | Returns all users |
| `POST` | `/api/Feedbacks` | no | none | anonymous | Accepts `UserId` in body |
| `GET` | `/rest/products/search?q=` | no | none | anonymous | Text search |

The "role required" column is the hypothesis to test, not a fact from documentation. Documentation describes what
the developers intended; the deployment is what you test.

**Why the inventory matters more than the tooling:** a scanner tests the requests it can construct. The endpoints
nobody documented — the `/v1` that still works, the admin route the mobile app calls, the debug endpoint — are
exactly where the findings are. That is [API9:2023 Improper Inventory
Management](https://owasp.org/API-Security/editions/2023/en/0x11-t10/).

### 3. Three authorization levels, three different bugs

| Level | Question | Failure name | Example | Test |
| --- | --- | --- | --- | --- |
| Object | May this user act on *this* record? | BOLA / IDOR | `/orders/1041` returns another customer's order | Two identities, swap the id |
| Function | May this user perform this *operation*? | BFLA | `/api/Users` (list all) reachable by a normal user | Call an admin route with a user token |
| Property | May this user read or write *these fields*? | Mass assignment / excessive exposure | `PATCH /me` accepts `role: "admin"`; `GET /me` returns `password_hash` | Send extra fields; inspect every response field |

**BOLA is first for a reason.** It is trivially testable, extremely common, and every object-bearing endpoint is a
candidate. It also survives frameworks: an ORM makes it easy to write `find_by(id:)` and forget the owner.

**Property-level flaws are the ones clients dispute.** "We don't show the role field in the app" is not an
authorization control when the API returns it, and "the form doesn't have a role input" is not a control when the
API accepts one.

### 4. Mass assignment, precisely

Mass assignment happens when the server binds request fields directly onto a model or object without an allowlist.

```python
# VULNERABLE — every key in the body is written to the record
@app.patch("/api/users/<int:uid>")
def update_user(uid):
    data = request.get_json()
    for key, value in data.items():
        setattr(user, key, value)          # includes "role", "is_admin", "owner_id"
    db.commit()
    return jsonify(user.to_dict())
```

```python
# SAFE — an explicit allowlist of client-writable fields
WRITABLE = {"display_name", "timezone", "avatar_url"}

@app.patch("/api/users/<int:uid>")
def update_user(uid):
    data = request.get_json() or {}
    unknown = set(data) - WRITABLE
    if unknown:
        return jsonify(error="unknown fields", fields=sorted(unknown)), 400
    for key in WRITABLE & set(data):
        setattr(user, key, data[key])
    db.commit()
    return jsonify(user.to_public_dict())     # explicit output shape, too
```

**How to test for it without guessing field names:**

1. Send an unknown field such as `{"zz_probe": "x"}`. A `200` that ignores it suggests permissive binding; a `400`
   naming the field suggests an allowlist. Neither proves it, but each narrows the hypothesis.
2. Send a field you saw in a *response* but that no form offers — `role`, `is_admin`, `credits`, `owner_id`.
3. Compare the response to the request. If the response echoes fields you did not send, the object is being
   serialised wholesale, which is also how excessive data exposure happens.
4. Check the effect, not just the status: re-read the object with a `GET` and see whether the value persisted.

### 5. Tokens: opaque versus self-contained

| | Opaque token | JWT (self-contained) |
| --- | --- | --- |
| Contents | Random identifier | Base64url header, payload, signature |
| Server lookup | Required on every request | None for validation |
| Revocation | Delete the row — immediate | Hard: needs short expiry, denylist, or token version |
| Client can read claims | No | **Yes — a JWT is signed, not encrypted** |
| Typical mistake | Predictable identifiers | Skipping a validation step |

**The validation checklist for a JWT**, each item with the bug it prevents:

| Check | Omission enables |
| --- | --- |
| Signature verified with the expected algorithm | Anyone can mint tokens |
| Algorithm taken from an **allowlist**, not the token header | `alg: none`, or RS256→HS256 confusion using the public key as an HMAC secret |
| `exp` and `nbf` validated with small leeway | Expired tokens accepted forever |
| `iss` and `aud` validated | A token from another service or tenant is accepted |
| `kid` resolved from a trusted set, never used as a path or query | Path traversal or SQL injection through the key id |
| JWKS URL from configuration, not from the token | Attacker supplies their own keys |
| Sensitive data kept out of the payload | Email, roles, and internal ids readable by anyone holding the token |
| Revocation story defined | A stolen token survives logout for its whole lifetime |

```python
# Correct verification shape (PyJWT): explicit algorithm, audience and issuer checked
import jwt

claims = jwt.decode(
    token,
    key=public_key,
    algorithms=["RS256"],          # allowlist, not header-driven
    audience="api.lab.test",
    issuer="https://auth.lab.test",
    options={"require": ["exp", "iat", "iss", "aud"]},
)
```

```python
# The bug, in one line: decode without verification
claims = jwt.decode(token, options={"verify_signature": False})   # claims are just client input
```

**API keys are not sessions.** They identify a client, not a user; they belong in a header, never in a query string
(where they land in logs and `Referer` headers); they must be scoped to specific operations; and they must be
rotatable without redeploying every client. If an API key grants access to user data, that is a finding about the
key's scope, not a convenience.

### 6. Rate limiting and resource consumption

A limit exists to bound the cost one actor can impose. That definition tells you what to key it on: the thing whose
abuse you are bounding.

| Limit | Key | Stops | Does not stop |
| --- | --- | --- | --- |
| Per IP | Source address | Single-source scripted abuse | Distributed abuse; shared NAT false positives |
| Per account | Authenticated subject | Credential stuffing on one account | Many-account spraying from one IP |
| Per token / client | API key or token id | One integration exhausting capacity | A compromised key rotating accounts |
| Per tenant | Tenant id | One customer degrading others | Abuse within the tenant |
| Per operation cost | Weighted units | Expensive endpoints (export, search) | Cheap-but-frequent calls |

Implementation choices that matter: a **sliding window** or **token bucket** rather than a fixed window (which
permits double bursts at the boundary); `429` with `Retry-After`; limits applied **before** expensive work, not
after; and separate limits for authentication endpoints, which need stricter ones.

```python
# A minimal token bucket for a lab service
import time

class Bucket:
    def __init__(self, capacity: int, refill_per_sec: float):
        self.capacity, self.refill = capacity, refill_per_sec
        self.state = {}                                  # key -> (tokens, last_ts)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        tokens, last = self.state.get(key, (self.capacity, now))
        tokens = min(self.capacity, tokens + (now - last) * self.refill)
        if tokens < 1:
            self.state[key] = (tokens, now)
            return False
        self.state[key] = (tokens - 1, now)
        return True
```

**Test it without abusing it.** Twenty requests establish whether a limit exists. Record the first `429`, the
`Retry-After` value if present, and whether the limit is per IP or per account by switching identity while keeping
the same source address. A thousand requests teaches nothing new and is an attack.

### 7. GraphQL, briefly

GraphQL changes the shape of the same problems:

- **Introspection** can disclose the entire schema. On a public API that is a design choice; on an internal one it
  is a finding.
- **Field-level authorization** is required, because the client chooses which fields to return. A resolver that
  authorizes the query but not each field leaks data.
- **Depth and complexity limits** replace simple request-count limits; a nested query can be enormously expensive.
- **Batching and aliases** let one request perform many operations, so per-request rate limiting is weak.

### 8. Inventory, versions and errors

Three recurring findings that are not about a single endpoint:

- **Shadow and deprecated APIs.** `/v1` still running with the old, unfixed code; a staging hostname resolving
  publicly; an admin API on another port. Inventory is the control.
- **Error verbosity.** A stack trace in a JSON error is a map of the internals: framework, versions, file paths,
  sometimes query text.
- **CORS on APIs.** A permissive policy turns any website into a client for your API, with the victim's cookies.
  Same rules as CYB-301; the impact is larger because APIs return data rather than pages.

---

## Worked example: one endpoint, three questions

`GET /rest/basket/{id}` in the lab application returns a shopping basket. Apply the three levels.

**Object level.** As user B, request basket 1 (owned by A). A `200` containing A's items is BOLA. Evidence: the
response's `UserId` field, plus A's own request for the same path.

**Function level.** Ask whether the route is meant to be reachable by any authenticated user at all. Here it is —
baskets belong to users. Now ask the same of `GET /api/Users`: a normal user receiving a list of every account is
BFLA, and the `role` field in the response tells an attacker whom to target.

**Property level.** Compare the fields returned against the fields a UI needs. A basket response that includes an
internal `couponCode` or another user's email is excessive data exposure, even when the object itself is yours.

**Write it as three findings, not one.** They have different fixes: a `WHERE owner_id = ?`, a role check on the
route, and a response serialiser with an explicit field list. Bundling them into "broken access control" makes the
fix ambiguous, and ambiguous fixes do not happen.

---

## Defender's view

| Signal | Source | Meaning |
| --- | --- | --- |
| Sequential id enumeration by one token | API gateway logs | BOLA probing |
| `401`/`403` spikes per token | Gateway, WAF | Authorization boundary mapping |
| Requests with unexpected JSON fields | Request logs, schema validation metrics | Mass assignment attempts |
| Admin routes called by non-admin tokens | Application audit log | BFLA, or a broken client |
| Many `429`s from one account | Gateway | Either abuse or a broken client retry loop |
| Same key used from many countries | Auth logs | Key leakage or credential sharing |
| Deprecated API versions still receiving traffic | Gateway | Inventory gap; unfixed code in use |

Design-side controls that hold up: authorize inside the query; require an explicit role for every non-user route;
serialise output through an explicit schema; allowlist writable fields and reject unknown ones; keep tokens short-
lived with a revocation story; and rate limit on the identity that would abuse you.

---

## Common mistakes

1. **Testing authorization only through the UI.** The mobile client's routes are in the JavaScript bundle or the
   APK, and they are tested by nobody.
2. **One account.** Without a second identity, a `200` proves nothing about authorization.
3. **Guessing field names for mass assignment.** Read the responses first; the extra fields tell you what exists.
4. **Accepting "the token is signed" as validation.** Signed with what, verified against which key, with which
   algorithm, and is it expired?
5. **Treating `429` as proof of adequate limiting.** Check the key: per IP is not per account, and per request is
   not per cost.
6. **Reporting every undocumented endpoint as a vulnerability.** Shadow APIs matter when they are reachable and
   carry data or operations; inventory noise hides real findings.

---

## Practice

1. [LAB-308-01 · API Authorization Failures](lab-01-api-authorization.md) — matrix, BOLA, BFLA, property exposure.
2. [LAB-308-02 · Mass Assignment and Rate Limiting](lab-02-mass-assignment-and-rate-limiting.md) — a local API, both
   flaws, both fixes, with tests.

**Stretch task.** Take the endpoint matrix from LAB-308-01 and mark each row with the API Top 10 category it would
fall under if the check were missing. Then pick the row where you are least certain and design the test that would
settle it.

## Knowledge check

1. Distinguish BOLA, BFLA, and mass assignment by the question each one answers.
2. Why is a UUID not an authorization control for an object reference?
3. A `PATCH` returns `200` and ignores an unknown field. What does that tell you, and what does it not tell you?
4. Name four JWT checks and the bypass each omission enables.
5. Why is `alg: none` still worth testing on a modern framework?
6. A rate limit is per IP. Describe the abuse it does not stop and the second limit you would add.
7. Why does field-level authorization matter specifically in GraphQL?
8. What is a shadow API, and which control addresses the class rather than one instance?

## Summary

- An API has no UI to hide operations; the server check is the only control.
- Inventory first, then test object, function, and property authorization separately.
- Mass assignment is found from responses and behaviour, then fixed with an allowlist and a strict error.
- JWTs must be verified with an expected algorithm, audience, issuer, and expiry — and revoked by design.
- Rate limits are only meaningful when keyed on the identity that would abuse the service.

## References

1. OWASP API Security Top 10 — 2023 edition. <https://owasp.org/API-Security/> Accessed 2026-10-29.
2. OWASP Top 10:2025 — A01 Broken Access Control. <https://owasp.org/Top10/2025/>
3. OWASP ASVS 5.0 — V4 API and Web Service, V9 Self-contained Tokens. <https://asvs.owasp.org/>
4. OWASP WSTG v4.2 — WSTG-ATHZ-04 (IDOR), WSTG-BUSL (business logic).
5. RFC 7519 — JSON Web Token (JWT). IETF, 2015.

---
title: "LAB-308-01 · API Authorization Failures"
description: "Map an API, then test object, function and property authorization with two identities and record what each response proves."
module_code: CYB-308
level: 3
kind: lab
prerequisites: [CYB-308]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-308-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [api-security, bola, bfla, inventory, authorization]
---

# LAB-308-01 · API Authorization Failures

## Scenario and background

The application is a single-page shop. There is no server-rendered admin area, no links to crawl, and no form
action to inspect — everything happens through `/rest/` and `/api/` calls made by JavaScript. This is the normal
shape of a modern target, and it means your assessment starts with an inventory rather than a browser.

You will build an endpoint matrix, then test three authorization levels separately, because they have three
different fixes and one combined finding helps nobody.

## Learning objectives

By the end of this lab you can:

1. Build an endpoint matrix from observed traffic and client-side JavaScript.
2. Prove BOLA by comparing two identities' access to the same object.
3. Prove BFLA by calling an administrative route with a non-administrative token.
4. Identify excessive data exposure by classifying every field in a response.
5. Map findings to API Top 10 categories and specify the check each endpoint needs.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Juice Shop | 20.3.0 | `http://192.0.2.30:3000` |
| Two accounts | yours | `learner303a@lab.test`, `learner303b@lab.test` |
| `curl`, `jq` | 7.81+, 1.6+ | Requests and field inspection |
| Burp Suite Community | 2026.10.1 | Optional; sitemap and Repeater |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `http://192.0.2.30:3000` only, with accounts you created.
    **Targets you must not use:** any public API, any third-party service, and any other user's account.

    **Read-only across accounts.** You may create and read your own objects, and read other users' objects as
    evidence. Do **not** modify or delete another user's data, and do not change any account's role. A `GET` that
    returns someone else's basket is a finding; a `DELETE` is an incident.

    **No brute force.** Authentication limit testing is bounded to 10 requests in this lab.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary is an ordinary registered customer with a valid token. They have no administrative rights and no
insider knowledge. Their capability is limited to changing identifiers, calling routes they discovered in the
client bundle, and reading whatever comes back.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Requests, notes | 192.0.2.10 |
| `lab-web` | Juice Shop | 192.0.2.30:3000 |

**Network view**

```text
lab-analyst 192.0.2.10                  lab-web 192.0.2.30
  token A / token B ───────────────▶ :3000 /rest/... and /api/...
                                     (same session, different subjects)
```

## Before you start

1. Snapshot `pre-lab-308-01`.
2. Log in as both accounts and store the tokens:

   ```bash
   mkdir -p ~/lab/level-3/lab-308-01/evidence && cd ~/lab/level-3/lab-308-01
   J='http://192.0.2.30:3000/rest/user/login'
   curl -sS -X POST "$J" -H 'Content-Type: application/json' \
     --data '{"email":"learner303a@lab.test","password":"Lab-Passw0rd-303"}' \
     | jq -r '.authentication.token' > evidence/token-a.txt
   curl -sS -X POST "$J" -H 'Content-Type: application/json' \
     --data '{"email":"learner303b@lab.test","password":"Lab-Passw0rd-303"}' \
     | jq -r '.authentication.token' > evidence/token-b.txt
   wc -c evidence/token-*.txt
   ```

   **Expected:** two tokens, each a few hundred bytes. If a file is empty, the login failed — check the credentials
   before continuing.

3. Confirm a token works:

   ```bash
   curl -sS -H "Authorization: Bearer $(cat evidence/token-a.txt)" \
     http://192.0.2.30:3000/rest/user/whoami | jq .
   ```

## Procedure

### 1. Build the endpoint matrix

You cannot crawl a SPA, so collect routes from three sources: the sitemap in your proxy, the JavaScript bundle, and
the calls you observe.

```bash
# Routes referenced in the client bundle
curl -sS http://192.0.2.30:3000/main.js -o evidence/main.js
grep -oE '"/?(rest|api)/[A-Za-z0-9/_{}.-]+"' evidence/main.js | sort -u | head -40 \
  | tee evidence/routes-from-bundle.txt
```

Also record what the running client actually calls: with the proxy configured, perform a login, a search, a basket
view, and a feedback submission, then export the sitemap paths.

Fill `evidence/endpoint-matrix.md`:

| Method | Path | Auth required | Object reference | Suspected role | Observed status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/rest/products/search` | no | `q` | anonymous | 200 | Public search |
| GET | `/rest/basket/{id}` | yes | numeric `id` | user | | |
| GET | `/api/Users` | yes | none | admin? | | |
| GET | `/api/Feedbacks` | ? | none | ? | | |
| GET | `/rest/admin/application-configuration` | ? | none | ? | | |

**Why the "suspected role" column is a hypothesis:** nothing in the client says who *should* be allowed. You infer
it from the route's name and function, then test whether the server enforces it. That gap between intent and
enforcement is the whole assessment.

### 2. Test object-level authorization (BOLA)

As A, create an object and note its identifier. As B, request it.

```bash
T_A=$(cat evidence/token-a.txt); T_B=$(cat evidence/token-b.txt); B='http://192.0.2.30:3000'

# A's own basket
curl -sS -H "Authorization: Bearer $T_A" "$B/rest/basket/1" | jq '{id, UserId, items: [.Products[].name]}' \
  | tee evidence/a-basket.json

# B requests the same object
curl -sS -H "Authorization: Bearer $T_B" -o evidence/b-basket-1.json \
  -w 'status=%{http_code}\n' "$B/rest/basket/1"
jq '{id, UserId}' evidence/b-basket-1.json
```

**Expected:** `200`, and a `UserId` that belongs to A rather than B. That is BOLA, proven by the object's own
ownership field rather than by the status code.

**The control that should exist:** `WHERE user_id = :token_subject`, returning `404` when the row does not belong
to the caller. Write that sentence into the finding; it is the difference between an observation and a fix.

### 3. Test function-level authorization (BFLA)

```bash
for path in /api/Users /api/Feedbacks /rest/admin/application-configuration; do
  anon=$(curl -sS -o /dev/null -w '%{http_code}' "$B$path")
  user=$(curl -sS -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $T_B" "$B$path")
  printf '%-42s anon=%s user=%s\n' "$path" "$anon" "$user"
done | tee evidence/bfla.txt
```

**Expected:** `/api/Users` returns `401` anonymously and `200` for an ordinary user. That is BFLA: the route
requires authentication but not the role its function implies.

Then inspect what it returned, because the impact is in the fields:

```bash
curl -sS -H "Authorization: Bearer $T_B" "$B/api/Users" -o evidence/api-users.json
jq 'length' evidence/api-users.json
jq '.[0] | keys' evidence/api-users.json
```

**Expected:** a list of every account, with fields including at least an email and a role. Record the field names,
**redact the values**, and note the count. The finding is not "an endpoint exists" — it is "any customer can
enumerate the customer base and identify administrators".

### 4. Test property-level exposure

For each response you have collected, classify every field:

```bash
jq -r '.[0] | to_entries[] | "\(.key): \(.value | type)"' evidence/api-users.json
jq -r 'to_entries[] | "\(.key): \(.value | type)"' evidence/a-basket.json
```

| Field | Needed by this client? | Classification |
| --- | --- | --- |
| `id` | yes | Necessary |
| `email` | no (it is your own record) | Excessive for a list endpoint |
| `role` | no | Sensitive: identifies targets |
| `password` (if present) | never | **Critical**: hash disclosure |

**Expected:** at least one field that the client does not need. Note whether any credential material appears — if
it does, do not copy the value into your report; state the field name and that it was present.

**Why this is a separate finding from BFLA:** the route check and the response shape are different controls. Fixing
the role check leaves a well-authorized endpoint returning fields nobody needs; fixing the serialiser leaves the
route open to every user.

### 5. Test for missing rate limiting, within bounds

```bash
for i in $(seq 1 10); do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -X POST "$B/rest/user/login" \
    -H 'Content-Type: application/json' \
    --data "{\"email\":\"learner303b@lab.test\",\"password\":\"wrong-$i\"}")
  printf '%s ' "$code"
done; echo
```

**Expected:** ten consecutive `401`s, no `429`, no lockout. That is the finding: authentication has no throttle, so
password guessing proceeds at network speed.

**Stop at ten.** The control either exists or it does not; more requests add nothing and are indistinguishable from
an attack in the logs.

### 6. Assemble the findings and the fix plan

In `evidence/api-findings.md`, one row per finding:

| ID | Finding | Endpoint | API Top 10 | Fix |
| --- | --- | --- | --- | --- |
| A-01 | BOLA on basket read | `GET /rest/basket/{id}` | API1:2023 | Scope query by token subject; `404` on mismatch |
| A-02 | BFLA on user list | `GET /api/Users` | API5:2023 | Require an admin role; deny by default |
| A-03 | Excessive fields in user list | `GET /api/Users` | API3:2023 | Explicit response schema |
| A-04 | No login throttle | `POST /rest/user/login` | API2:2023 / API4:2023 | Per-account and per-IP limits, `429` + `Retry-After` |

Add one sentence per row describing the **impact to a customer**, not to the scanner. "Any customer can read any
other customer's basket contents" beats "IDOR found".

## Evidence to collect

- `evidence/endpoint-matrix.md` — at least eight endpoints, with observed statuses.
- `evidence/routes-from-bundle.txt` — routes discovered client-side.
- `evidence/a-basket.json`, `evidence/b-basket-1.json` — the BOLA comparison.
- `evidence/bfla.txt` — anonymous versus user status per route.
- `evidence/api-users.json` — with values redacted, field names retained.
- `evidence/rate-limit.txt` — the ten attempts.
- `evidence/api-findings.md` — the table with fixes.

## Verification

- [ ] Matrix covers at least eight endpoints from at least two discovery sources.
- [ ] BOLA proven by `UserId` comparison, not by status alone.
- [ ] BFLA proven with an ordinary user's token on an administrative route.
- [ ] Every field of two responses classified.
- [ ] Rate limiting tested with exactly ten requests or fewer.
- [ ] Four findings mapped to API Top 10 with a specific fix each.
- [ ] No data belonging to another user was modified or deleted.

## Teardown and reset

```bash
rm -f evidence/token-a.txt evidence/token-b.txt    # remove live tokens
```

Tokens remain valid until expiry; deleting the files does not revoke them, which is itself the point from
LAB-301-03. Revert `pre-lab-308-01` to restore the application's database. Keep the findings and the matrix.

## Reflection

1. The bundle revealed routes the UI never calls. Why does that make client-side code a reconnaissance source, and
   what would you ask a development team to do about it?
2. `/api/Users` required authentication. Explain why that is not an authorization check, in one sentence you could
   put in a report.
3. You wrote three separate findings for one endpoint family. Give the argument for that, and the case where
   combining them would be better.
4. Ten login attempts established the absence of a throttle. What would you need to see before concluding that a
   throttle exists but is ineffective?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Inventory | Fewer than five endpoints | Eight endpoints, observed | Eight from multiple sources, including bundle-only routes |
| BOLA proof | Status code only | Ownership field compared | Compared, with the intended query-level fix named |
| BFLA proof | Assumed from the name | Called with a user token | Called, and the returned fields analysed for impact |
| Fix plan | "Add authorization" | Per-endpoint checks | Per-endpoint checks distinguishing route, object and field controls |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Empty token file | Login failed; `jq` found no token | Run the login without `jq` and read the error |
| `401` with a token | Header format wrong | `Authorization: Bearer <token>` with one space |
| `/main.js` returns 404 | Bundle filename differs by build | Use the devtools Network tab to find the actual bundle |
| `/api/Users` returns `403` | Different Juice Shop version or configuration | Record it — the control is present, which is a valid result |
| `jq` prints `null` for `UserId` | Response shape differs | `jq 'keys'` and use the actual field name |
| Password field absent from user list | Build-dependent | Note its absence; the exposure finding may then be about email and role only |

## References

1. OWASP API Security Top 10 — 2023 edition, API1, API2, API3, API5. <https://owasp.org/API-Security/> Accessed 2026-10-29.
2. OWASP WSTG v4.2 — WSTG-ATHZ-04 Testing for Insecure Direct Object References.
3. OWASP ASVS 5.0 — V4 API and Web Service, V8 Authorization. <https://asvs.owasp.org/>
4. OWASP Top 10:2025 — A01 Broken Access Control. <https://owasp.org/Top10/2025/>

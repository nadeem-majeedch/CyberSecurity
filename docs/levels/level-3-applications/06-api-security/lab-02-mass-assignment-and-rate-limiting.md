---
title: "LAB-308-02 · Mass Assignment and Rate Limiting"
description: "Escalate your own role through a PATCH body, exhaust an unlimited endpoint, then fix both with allowlists and a token bucket."
module_code: CYB-308
level: 3
kind: lab
prerequisites: [CYB-308]
estimated_minutes: 105
difficulty: advanced
safety: local-only
lab_ids: [LAB-308-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [mass-assignment, rate-limiting, api-security, serialization]
---

# LAB-308-02 · Mass Assignment and Rate Limiting

## Scenario and background

A small API lets customers update their profile. It also lets them become administrators, because the update
handler copies every key it receives onto the user record. And it lets them make as many requests as they like,
because nobody set a limit.

You will build that API, exploit both flaws, then fix them — and the fix for the first one is a design decision
about **explicitly shaping input and output**, not a validation regex.

## Learning objectives

By the end of this lab you can:

1. Identify mass assignment from observed field behaviour rather than guessed field names.
2. Demonstrate privilege escalation through a writable `role` field, and the chain to an admin endpoint.
3. Measure the absence of rate limiting with a bounded request sequence.
4. Implement a write allowlist, an explicit response schema, and a token-bucket limiter.
5. Test each control, including the 429 response and its headers.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python 3 + Flask | 3.10+, Flask 3.x | Both API versions |
| `pytest` | 7.x | Regression tests |
| `curl`, `jq` | 7.81+, 1.6+ | Manual verification |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** the API on `http://127.0.0.1:5080`, created by you in this lab.
    **Targets you must not use:** any other service. Bind to loopback only — you are about to build an API with
    a privilege-escalation flaw, and it must not be reachable from your network.

    **No brute force.** The rate-limit test sends at most 12 requests. The point is to establish whether a limit
    exists, not to exhaust anything.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary is an authenticated ordinary customer. They can send any JSON body to their own profile endpoint.
Their goal is to gain the `admin` role or exhaust the service. Both are reachable with a single well-formed
request — no injection, no tool, no payload syntax.

## Environment

| Component | Detail |
| --- | --- |
| `api_vulnerable.py` | The flawed version |
| `api_fixed.py` | Your repaired version |
| Address | `127.0.0.1:5080` (vulnerable), `127.0.0.1:5081` (fixed) |
| Data | In-memory, seeded: admin, alice, bob |

## Before you start

```bash
mkdir -p ~/lab/level-3/lab-308-02/{api/tests,evidence}
cd ~/lab/level-3/lab-308-02/api
```

Create the vulnerable API:

```python
"""LAB-308-02 vulnerable API. Deliberately flawed. Lab use only."""
import secrets
from flask import Flask, request, jsonify

app = Flask(__name__)

USERS = {
    "admin@lab.test": {"email": "admin@lab.test", "password": "Lab-Passw0rd-308",
                       "role": "admin", "credits": 100, "timezone": "UTC",
                       "display_name": "Admin"},
    "alice@lab.test": {"email": "alice@lab.test", "password": "Lab-Passw0rd-308",
                       "role": "user", "credits": 10, "timezone": "UTC",
                       "display_name": "Alice"},
    "bob@lab.test": {"email": "bob@lab.test", "password": "Lab-Passw0rd-308",
                     "role": "user", "credits": 5, "timezone": "UTC",
                     "display_name": "Bob"},
}
TOKENS = {}
NOTES = {}
NEXT_ID = [1]


def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return USERS.get(TOKENS.get(auth[7:], ""))


@app.post("/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "")
    if not email or email in USERS:
        return jsonify(error="bad request"), 400
    USERS[email] = {"email": email, "password": data.get("password", ""),
                    "role": "user", "credits": 0, "timezone": "UTC",
                    "display_name": email.split("@")[0]}
    return jsonify(USERS[email]), 201          # returns the password too


@app.post("/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    user = USERS.get(data.get("email", ""))
    if not user or user["password"] != data.get("password", ""):
        return jsonify(error="denied"), 401
    token = secrets.token_urlsafe(24)
    TOKENS[token] = user["email"]
    return jsonify(token=token)


@app.get("/me")
def me():
    user = current_user()
    if not user:
        return jsonify(error="auth required"), 401
    return jsonify(user)                        # entire record, including password


@app.patch("/me")
def update_me():
    user = current_user()
    if not user:
        return jsonify(error="auth required"), 401
    data = request.get_json(force=True, silent=True) or {}
    user.update(data)                           # every key, including "role"
    return jsonify(user)


@app.get("/admin/users")
def admin_users():
    user = current_user()
    if not user:
        return jsonify(error="auth required"), 401
    if user["role"] != "admin":
        return jsonify(error="forbidden"), 403
    return jsonify(list(USERS.values()))


@app.post("/notes")
def create_note():
    user = current_user()
    if not user:
        return jsonify(error="auth required"), 401
    data = request.get_json(force=True, silent=True) or {}
    note_id = NEXT_ID[0]
    NEXT_ID[0] += 1
    NOTES[note_id] = {"id": note_id,
                      "owner": data.get("owner", user["email"]),   # client-chosen owner
                      "title": data.get("title", ""),
                      "body": data.get("body", ""),
                      "internal_note": "internal only — not for clients"}
    return jsonify(NOTES[note_id]), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    user = current_user()
    if not user:
        return jsonify(error="auth required"), 401
    note = NOTES.get(note_id)
    if not note:
        return jsonify(error="not found"), 404
    return jsonify(note)                        # no ownership check


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5080, debug=False)
```

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install flask pytest
python api_vulnerable.py &
sleep 2
curl -sS -o /dev/null -w 'up=%{http_code}\n' http://127.0.0.1:5080/me
```

**Expected:** `up=401` — the service is running and requires a token.

## Procedure

### 1. Authenticate as alice

```bash
B='http://127.0.0.1:5080'
T=$(curl -sS -X POST "$B/login" -H 'Content-Type: application/json' \
  --data '{"email":"alice@lab.test","password":"Lab-Passw0rd-308"}' | jq -r .token)
echo "$T" > ../evidence/token-alice.txt
curl -sS -H "Authorization: Bearer $T" "$B/me" | jq . | tee ../evidence/me-before.json
```

**Expected:** alice's full record, including `"role": "user"`, `"credits": 10`, and her password in plaintext. Two
findings already, before any attack: the response leaks credentials and internal fields.

### 2. Establish the admin boundary

```bash
curl -sS -o /dev/null -w 'admin-before=%{http_code}\n' -H "Authorization: Bearer $T" "$B/admin/users"
```

**Expected:** `403`. This is the control that must hold — and the baseline for the next step.

### 3. Probe for mass assignment

Two probes, in order. First, does the API reject unknown fields?

```bash
curl -sS -X PATCH "$B/me" -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
  --data '{"zz_probe":"x"}' -w '\nstatus=%{http_code}\n'
```

**Expected:** `200`, and `zz_probe` now appears in the record — the handler copies whatever it is given. That is
strong evidence for permissive binding.

Second, does it accept a field that exists but is not client-writable?

```bash
curl -sS -X PATCH "$B/me" -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
  --data '{"role":"admin"}' | jq '{email, role}'
curl -sS -H "Authorization: Bearer $T" "$B/me" | jq '{role, credits}'
```

**Expected:** `"role": "admin"` in both responses — the change persisted.

**Why this is not a "guessed parameter"**: `role` was visible in the `GET /me` response from step 1. The response
told you which fields exist; the `PATCH` told you which ones it honours. Read the output before choosing the
payload.

### 4. Complete the chain

```bash
curl -sS -o /dev/null -w 'admin-after=%{http_code}\n' -H "Authorization: Bearer $T" "$B/admin/users"
curl -sS -H "Authorization: Bearer $T" "$B/admin/users" | jq 'length'
```

**Expected:** `200` and a list of every account. That is the impact: a profile update became full administrative
read access. Record the before/after pair — `403` then `200` — because that contrast is the finding.

Also worth recording, still as alice:

```bash
curl -sS -X PATCH "$B/me" -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
  --data '{"credits":9999}' | jq '{credits}'
```

**Expected:** `9999`. Any writable business value is the same class of flaw, and it is usually worth more money than
the role field.

### 5. Test the other two API flaws in the same service

```bash
# Client-chosen note owner
curl -sS -X POST "$B/notes" -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
  --data '{"title":"forged","owner":"bob@lab.test"}' | jq '{id, owner, internal_note}'

# Read a note you do not own
curl -sS -H "Authorization: Bearer $T" "$B/notes/1" | jq .
```

**Expected:** the note is stored under `bob@lab.test` because the client asked, and the response includes
`internal_note`, a field the client was never meant to see.

### 6. Measure the absence of rate limiting

```bash
for i in $(seq 1 10); do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -X POST "$B/notes" \
    -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
    --data "{\"title\":\"bulk-$i\",\"body\":\"x\"}")
  printf '%s ' "$code"
done; echo
```

**Expected:** ten `201`s. No `429`, no limit, no cost. For a note-taking service that is a storage bill; for a
password-reset or SMS endpoint it is a financial and reputational incident.

**Stop at ten.** You are measuring the presence of a control, not stress-testing a service.

### 7. Build the fixed version

```bash
cp api_vulnerable.py api_fixed.py
```

Apply these changes to `api_fixed.py`:

```python
# 1. Explicit output shape — what a client may see, and nothing else.
from werkzeug.security import generate_password_hash, check_password_hash

def public_user(user, include_role=False):
    out = {"email": user["email"], "display_name": user["display_name"],
           "timezone": user["timezone"], "credits": user["credits"]}
    if include_role:
        out["role"] = user["role"]
    return out

# 2. Passwords stored as hashes, never returned.
#    In register: user["password"] = generate_password_hash(pw)
#    In login:    if not check_password_hash(user["password"], pw): deny

# 3. Write allowlist with an explicit rejection.
WRITABLE = {"display_name", "timezone"}

@app.patch("/me")
def update_me():
    user = current_user()
    if not user:
        return jsonify(error="auth required"), 401
    data = request.get_json(force=True, silent=True) or {}
    unknown = set(data) - WRITABLE
    if unknown:
        return jsonify(error="unknown fields", fields=sorted(unknown)), 400
    for key in WRITABLE & set(data):
        user[key] = data[key]
    return jsonify(public_user(user))

# 4. Server-chosen ownership, and an ownership check on read.
#    owner is always user["email"]; get_note compares before returning.
#    The internal field is never serialised: return an explicit dict.

# 5. A token bucket for write endpoints and login.
import time
from collections import defaultdict

class Bucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity, self.refill = capacity, refill_per_sec
        self.state = {}

    def allow(self, key):
        now = time.monotonic()
        tokens, last = self.state.get(key, (self.capacity, now))
        tokens = min(self.capacity, tokens + (now - last) * self.refill)
        if tokens < 1:
            self.state[key] = (tokens, now)
            return False
        self.state[key] = (tokens - 1, now)
        return True

NOTE_LIMIT = Bucket(capacity=5, refill_per_sec=0.05)    # 5 burst, then 1 per 20 s
LOGIN_LIMIT = Bucket(capacity=5, refill_per_sec=0.02)

def limited(bucket, key):
    if bucket.allow(key):
        return None
    resp = jsonify(error="too many requests")
    resp.status_code = 429
    resp.headers["Retry-After"] = "20"
    return resp
```

In `create_note`, call `limited(NOTE_LIMIT, user["email"])` before doing work, and in `login` call
`limited(LOGIN_LIMIT, request.remote_addr)` first.

**Why the limiter runs first:** a limit enforced after the expensive work bounds nothing. The order is the control.

### 8. Tests

```bash
cat > tests/test_api.py <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
import api_fixed as api

@pytest.fixture(autouse=True)
def reset_limits():
    api.NOTE_LIMIT.state.clear(); api.LOGIN_LIMIT.state.clear()
    yield

@pytest.fixture()
def client():
    api.app.config.update(TESTING=True)
    with api.app.test_client() as c:
        yield c

@pytest.fixture()
def alice(client):
    r = client.post("/login", json={"email": "alice@lab.test", "password": "Lab-Passw0rd-308"})
    return {"Authorization": f"Bearer {r.get_json()['token']}"}

def test_me_does_not_return_credentials(client, alice):
    body = client.get("/me", headers=alice).get_json()
    assert "password" not in body and "password_hash" not in body

def test_role_cannot_be_written(client, alice):
    r = client.patch("/me", headers=alice, json={"role": "admin"})
    assert r.status_code == 400 and "role" in r.get_json()["fields"]
    assert client.get("/admin/users", headers=alice).status_code == 403

def test_credits_cannot_be_written(client, alice):
    client.patch("/me", headers=alice, json={"credits": 9999})
    assert client.get("/me", headers=alice).get_json()["credits"] == 10

def test_legitimate_update_still_works(client, alice):
    r = client.patch("/me", headers=alice, json={"display_name": "Alice L."})
    assert r.status_code == 200 and r.get_json()["display_name"] == "Alice L."

def test_note_owner_is_server_chosen(client, alice):
    r = client.post("/notes", headers=alice,
                    json={"title": "t", "owner": "bob@lab.test"})
    assert r.status_code == 201
    assert r.get_json()["owner"] == "alice@lab.test"

def test_internal_field_not_returned(client, alice):
    r = client.post("/notes", headers=alice, json={"title": "t"})
    assert "internal_note" not in r.get_json()

def test_foreign_note_is_404(client, alice):
    other = client.post("/login", json={"email": "bob@lab.test", "password": "Lab-Passw0rd-308"})
    hb = {"Authorization": f"Bearer {other.get_json()['token']}"}
    nid = client.post("/notes", headers=alice, json={"title": "mine"}).get_json()["id"]
    assert client.get(f"/notes/{nid}", headers=hb).status_code == 404

def test_note_creation_is_rate_limited(client, alice):
    codes = [client.post("/notes", headers=alice, json={"title": "x"}).status_code
             for _ in range(6)]
    assert codes[:5] == [201] * 5
    assert codes[5] == 429

def test_login_is_rate_limited(client):
    codes = [client.post("/login", json={"email": "alice@lab.test",
                                         "password": "wrong"}).status_code
             for _ in range(6)]
    assert codes[5] == 429
PY

python -m pytest -q
```

**Expected:** nine passing tests.

Then confirm the limiter's headers on a live response, and the test's teeth:

```bash
sed 's/import api_fixed as api/import api_vulnerable as api/' tests/test_api.py > tests/test_vulnerable.py
python -m pytest tests/test_vulnerable.py -q; echo "exit=$?"
rm tests/test_vulnerable.py
```

**Expected:** multiple failures — mass assignment accepted, credentials returned, no `429`.

### 9. Verify live

```bash
python api_fixed.py &   # port 5081 in the fixed file
sleep 2
F='http://127.0.0.1:5081'
T=$(curl -sS -X POST "$F/login" -H 'Content-Type: application/json' \
  --data '{"email":"alice@lab.test","password":"Lab-Passw0rd-308"}' | jq -r .token)
curl -sS -o /dev/null -w 'mass-assignment=%{http_code}\n' -X PATCH "$F/me" \
  -H "Authorization: Bearer $T" -H 'Content-Type: application/json' --data '{"role":"admin"}'

for i in 1 2 3 4 5 6; do
  curl -sS -D /tmp/h.txt -o /dev/null -w '%{http_code} ' -X POST "$F/notes" \
    -H "Authorization: Bearer $T" -H 'Content-Type: application/json' --data '{"title":"x"}'
done; echo
grep -i '^retry-after' /tmp/h.txt
kill %1
```

**Expected:** `mass-assignment=400`, then `201 201 201 201 201 429`, with `Retry-After: 20` on the last response.

### 10. Write the remediation table

`evidence/remediation.md`:

| Finding | Fix | Disposition | Test | Status |
| --- | --- | --- | --- | --- |
| `role` writable via `PATCH /me` | Write allowlist + 400 on unknown fields | Fix | `test_role_cannot_be_written` | Closed |
| `credits` writable | Same allowlist | Fix | `test_credits_cannot_be_written` | Closed |
| Credentials in responses | Explicit output schema, hashed storage | Fix | `test_me_does_not_return_credentials` | Closed |
| Client-chosen note owner | Server-side owner assignment | Fix | `test_note_owner_is_server_chosen` | Closed |
| Internal field exposed | Explicit output schema | Fix | `test_internal_field_not_returned` | Closed |
| No rate limit | Token bucket, 429 + `Retry-After` | Fix | `test_note_creation_is_rate_limited` | Closed |

Add a residual-risk note: the bucket is in-process, so a multi-instance deployment needs a shared store; and the
limit is per account, so a distributed attack across many accounts is only bounded by the per-IP login limit.

## Evidence to collect

- `api/api_vulnerable.py`, `api/api_fixed.py`.
- `evidence/me-before.json`, `evidence/escalation.txt` — the `403`→`200` pair and the role change.
- `evidence/rate-limit-before.txt`, `evidence/rate-limit-after.txt` — with the `429` and `Retry-After`.
- `api/tests/test_api.py`; `evidence/pytest-fixed.txt`; `evidence/tests-against-vulnerable.txt`.
- `evidence/remediation.md`.

## Verification

- [ ] `PATCH /me` accepted an unknown field on the vulnerable version.
- [ ] `role` changed and `/admin/users` went from `403` to `200`.
- [ ] `credits` change persisted.
- [ ] Note owner was client-controlled, and `internal_note` was returned.
- [ ] Ten note creations all succeeded with no `429`.
- [ ] Nine tests pass on the fixed version; several fail on the vulnerable one.
- [ ] Live check returns `400`, then five `201`s and one `429` with `Retry-After`.

## Teardown and reset

```bash
pkill -f 'python api_'
deactivate 2>/dev/null
rm -f /tmp/h.txt
```

Both services are in-memory and loopback-only; nothing persists. Keep the directory as evidence.

## Reflection

1. The `role` field was visible in a response before you tried to write it. Explain how output shape and input
   binding are two halves of the same control problem.
2. Rejecting unknown fields with `400` breaks clients that send extra fields. Argue for the strict behaviour and
   name the cost.
3. Your limiter is per account. Describe the attack it misses and the second bucket you would add.
4. `Retry-After` is part of the control. What goes wrong for a well-behaved client when a `429` omits it?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Escalation proof | Field changed | `role` changed and admin route opened | Full chain recorded, plus a business-value field (`credits`) |
| Diagnosis | "Mass assignment" | Handler and line identified | Handler, output-shape cause, and the design fix named |
| Limiting | No `429` observed | Bucket implemented | Bucket implemented with `Retry-After` and a test for both endpoints |
| Testing | Manual only | Tests pass | Tests fail on the vulnerable version and cover legitimate updates |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `401` on every call | Token not captured; `jq` returned `null` | Print the login response and read it |
| `PATCH` returns `400` on the vulnerable app | You edited `api_vulnerable.py` by mistake | Recreate it from the lab text |
| `429` never appears | Bucket state cleared per test, or limit too high | Use capacity 5 and six requests |
| Tests import the wrong module | `test_vulnerable.py` left behind | Delete it; the fixture imports `api_fixed` |
| `werkzeug.security` import error | Old Werkzeug version | Upgrade Flask; the module ships with Werkzeug |
| Fixed app runs on the wrong port | Copied file still binds 5080 | Change to 5081 in `api_fixed.py` |

## References

1. OWASP API Security Top 10 — API3:2023 Broken Object Property Level Authorization, API4:2023 Unrestricted
   Resource Consumption, API6:2023 Unrestricted Access to Sensitive Business Flows.
   <https://owasp.org/API-Security/> Accessed 2026-10-29.
2. OWASP Mass Assignment Cheat Sheet. Accessed 2026-10-29.
3. OWASP ASVS 5.0 — V4 API and Web Service, V2 Validation and Business Logic. <https://asvs.owasp.org/>
4. Werkzeug — `generate_password_hash`, `check_password_hash`. Accessed 2026-10-29.

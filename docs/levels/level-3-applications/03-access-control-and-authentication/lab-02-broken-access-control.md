---
title: "LAB-303-02 · Broken Access Control and IDOR"
description: "Use two real identities to prove object-level and function-level authorization failures, then fix them in code with tests."
module_code: CYB-303
level: 3
kind: lab
prerequisites: [CYB-303]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-303-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [idor, access-control, bola, forced-browsing, authorization]
---

# LAB-303-02 · Broken Access Control and IDOR

## Scenario and background

This is the lab that most resembles paid work. There is no payload, no encoder, and no clever syntax. There are
two accounts you own, one identifier that belongs to the other account, and a question the server should have
asked and did not: *may this user read this object?*

You will test Juice Shop's object-level authorization (a basket), its function-level authorization (an
administrative API), and its unlinked paths (forced browsing). Then you will implement the fix in a small local
service and prove it with tests — because "add an authorization check" is not a deliverable.

## Learning objectives

By the end of this lab you can:

1. Distinguish object-level (IDOR/BOLA) from function-level authorization failures with evidence.
2. Prove an IDOR by showing one identity receiving another identity's object.
3. Enumerate unlinked endpoints and classify each response.
4. Explain why a `404` is often the correct response to an unauthorized object request.
5. Implement object-scoped authorization in a data query and guard it with regression tests.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Juice Shop | 20.3.0 | `http://192.0.2.30:3000` |
| Two accounts | yours | `learner303a@lab.test`, `learner303b@lab.test` |
| `curl`, `jq` | 7.81+, 1.6+ | Request/response evidence |
| Burp Suite Community | 2026.10.1 | Optional; sitemap helps find routes |
| Python 3 + Flask + pytest | 3.10+ | Repair exercise |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `http://192.0.2.30:3000` (Juice Shop) and a local Flask service on
    `127.0.0.1:5002`. Both accounts are yours.
    **Targets you must not use:** any other host. Do not create accounts with other people's addresses, and do not
    modify or delete another user's objects — **reading is sufficient evidence** and mutation is both unnecessary
    and, in a real engagement, a scope violation you would have to disclose.

    Use `GET` and read-only requests for the cross-account tests. Where a `POST` is needed (login, adding to your
    own basket), it acts only on your own data.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary is an ordinary registered user with a valid session. They have no special privileges and no
insider knowledge. Their entire capability is: change a number, request a path they saw in a JavaScript file, and
keep their own cookie. Any data they obtain is obtained through a request the application answered.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Requests, local repair service | 127.0.0.1:5002 |
| `lab-web` | Juice Shop | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                lab-web 192.0.2.30
  token A ──┐                        :3000 Juice Shop
  token B ──┴──────────────────────▶ /rest/basket/{id}, /api/Users
  repair/ 127.0.0.1:5002  local only
```

## Before you start

1. Snapshot `pre-lab-303-02`.
2. Log in as both accounts and keep two cookie jars:

   ```bash
   mkdir -p ~/lab/level-3/lab-303-02/evidence && cd ~/lab/level-3/lab-303-02
   J='http://192.0.2.30:3000/rest/user/login'
   curl -sS -c evidence/a.jar -X POST "$J" -H 'Content-Type: application/json' \
     --data '{"email":"learner303a@lab.test","password":"Lab-Passw0rd-303"}' > /dev/null
   curl -sS -c evidence/b.jar -X POST "$J" -H 'Content-Type: application/json' \
     --data '{"email":"learner303b@lab.test","password":"Lab-Passw0rd-303"}' > /dev/null
   wc -l evidence/a.jar evidence/b.jar
   ```

   **Expected:** two non-empty Netscape cookie files.

3. As A, add one product to the basket so there is something to protect.

## Procedure

### 1. Establish A's baseline

```bash
J='http://192.0.2.30:3000'
curl -sS -b evidence/a.jar "$J/rest/basket/1" | tee evidence/a-basket.json | jq '{id, UserId, items: [.Products[].name]}'
```

**Expected:** a basket object with your `UserId`, containing the product you added. Note the numeric `id` and the
`UserId` field — those two values are all you need for the whole lab.

Determine A's numeric user id, which you will need to interpret the comparison:

```bash
curl -sS -b evidence/a.jar "$J/rest/user/whoami" | jq .
```

### 2. Test object-level authorization

Request the same path as B, and also sweep a small range of neighbouring identifiers.

```bash
for id in 1 2 3 4 5; do
  code=$(curl -sS -o "evidence/b-basket-$id.json" -w '%{http_code}' -b evidence/b.jar "$J/rest/basket/$id")
  uid=$(jq -r '.UserId // "none"' "evidence/b-basket-$id.json" 2>/dev/null)
  printf 'basket=%s status=%s owner=%s\n' "$id" "$code" "$uid"
done
```

**Expected:** `200` for several baskets, with `owner` values that are **not** B's user id. That is a confirmed
IDOR: B is authenticated, the request was well-formed, and the server returned another user's object.

**The critical comparison** — this is what makes the finding, not the status code:

```bash
echo "B's own user id: $(curl -sS -b evidence/b.jar "$J/rest/user/whoami" | jq -r '.user.id')"
jq '{id, UserId}' evidence/a-basket.json
```

If the object B received has A's `UserId`, the finding is proven. Record both.

**What a control would look like:** `403` for another user's object, or `404` if the application prefers not to
confirm existence. Both are acceptable; `200` is not.

### 3. Test function-level authorization

Object-level flaws are about *which* record. Function-level flaws are about *which operation*. An
administration API reachable by a normal user is the second.

```bash
# Unauthenticated: expect 401
curl -sS -o /dev/null -w 'anon /api/Users -> %{http_code}\n' "$J/api/Users"

# Authenticated as an ordinary user: what does it return?
curl -sS -b evidence/a.jar -o evidence/api-users.json -w 'user /api/Users -> %{http_code}\n' "$J/api/Users"
jq 'length' evidence/api-users.json 2>/dev/null
jq '.[0] | keys' evidence/api-users.json 2>/dev/null
```

**Expected:** `401` unauthenticated, then `200` with a **list of every user** when authenticated as a normal
account — including fields such as email and role. That is a broken function-level authorization check: the
endpoint answers to any valid session instead of to an administrator.

**Why this matters more than the IDOR:** the IDOR leaks one object at a time. A list endpoint that returns all
users leaks the entire population in one request, and the role field tells an attacker whom to target.

### 4. Forced browsing

Endpoints that the UI never links are still endpoints. Request a small, fixed set and classify each response.
This is reconnaissance of your own target, not discovery of someone else's.

```bash
paths=(
  "/ftp"
  "/api/Feedbacks"
  "/rest/admin/application-configuration"
  "/api/Users"
  "/metrics"
  "/.git/config"
  "/backup.zip"
  "/administration"
)
for p in ${paths[@]}; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -b evidence/a.jar "$J$p")
  printf '%-42s %s\n' "$p" "$code"
done | tee evidence/forced-browsing.txt
```

**Expected:** a mix. `200` on `/ftp` indicates a browsable directory of files. `200` on
`/rest/admin/application-configuration` indicates configuration served to any client. `404` on `/.git/config` is
the correct answer. Record what you actually observe — this list is a prompt, not a prediction.

For anything that returns `200`, retrieve it and decide what it discloses:

```bash
curl -sS -b evidence/a.jar "$J/ftp" | head -40
```

**Classification for your table:** public by design, requires authentication, requires a role, or should not
exist. Only the last two are findings, and "should not exist" needs a sentence about why.

### 5. Repeat the discipline on a second surface

Pick one more object-bearing endpoint you saw in your LAB-301-02 sitemap (feedback, orders, addresses) and run the
same three questions:

1. As A, read your own object.
2. As B, request A's reference.
3. Compare the bodies.

Append the result to `evidence/idor-matrix.md`. Two independent confirmations are worth far more than one, and
they let you say "systemic pattern" rather than "single endpoint".

### 6. Build the repair

A minimal service with the same flaw, then the fix:

```bash
mkdir -p ~/lab/level-3/lab-303-02/repair/tests && cd ~/lab/level-3/lab-303-02/repair
cat > invoices_vulnerable.py <<'PY'
"""Vulnerable: resolves the invoice by path parameter only."""
from flask import Flask, request, jsonify
app = Flask(__name__)
INVOICES = {1: {"id": 1, "owner": "alice", "total": 1200},
            2: {"id": 2, "owner": "bob", "total": 980}}

@app.get("/invoices/<int:invoice_id>")
def get_invoice(invoice_id):
    # X-Lab-User stands in for session['user_id']; in a real app it is never a client header.
    user = request.headers.get("X-Lab-User", "")
    inv = INVOICES.get(invoice_id)
    if inv is None:
        return jsonify(error="not found"), 404
    return jsonify(inv)
PY

cat > invoices_fixed.py <<'PY'
"""Fixed: the lookup is scoped by the authenticated subject."""
from flask import Flask, request, jsonify
app = Flask(__name__)
INVOICES = {1: {"id": 1, "owner": "alice", "total": 1200},
            2: {"id": 2, "owner": "bob", "total": 980}}

@app.get("/invoices/<int:invoice_id>")
def get_invoice(invoice_id):
    user = request.headers.get("X-Lab-User", "")
    inv = INVOICES.get(invoice_id)
    # Same response for "does not exist" and "not yours": no existence oracle.
    if inv is None or inv["owner"] != user:
        return jsonify(error="not found"), 404
    return jsonify(inv)
PY
```

Now the tests, which must pass on the fixed version **and fail on the vulnerable one**:

```bash
cat > tests/test_authorization.py <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from invoices_fixed import app

@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

def get(client, invoice_id, user):
    return client.get(f"/invoices/{invoice_id}", headers={"X-Lab-User": user})

def test_owner_can_read_own_invoice(client):
    r = get(client, 1, "alice")
    assert r.status_code == 200 and r.get_json()["total"] == 1200

def test_other_user_cannot_read_invoice(client):
    assert get(client, 1, "bob").status_code == 404

def test_missing_and_forbidden_are_indistinguishable(client):
    a = get(client, 1, "bob").get_json()
    b = get(client, 999, "bob").get_json()
    assert a == b

def test_anonymous_cannot_read_invoice(client):
    assert get(client, 1, "").status_code == 404
PY

python3 -m venv .venv && . .venv/bin/activate
pip install flask pytest
python -m pytest -q
```

**Expected:** four passing tests. Then prove the tests detect the bug:

```bash
cp tests/test_authorization.py tests/test_vulnerable.py
sed -i 's/from invoices_fixed import app/from invoices_vulnerable import app/' tests/test_vulnerable.py
python -m pytest tests/test_vulnerable.py -q || echo "expected failures on the vulnerable version"
rm tests/test_vulnerable.py
```

**Expected:** `test_other_user_cannot_read_invoice` and its companions **fail**. A regression test that passes
against vulnerable code is not testing authorization.

### 7. Write the finding

In `evidence/finding-idor.md`, structure it as: title, affected endpoint, two identities, request as B, response
proving A's data, mechanism (handler resolves by path parameter without comparing to the session subject),
impact, and remediation with the code change. Under 400 words. The Level 3 report will reuse it verbatim.

## Evidence to collect

- `evidence/a-basket.json`, `evidence/b-basket-*.json` — the cross-account proof.
- `evidence/api-users.json` with the record count (redact other users' emails).
- `evidence/forced-browsing.txt` — the eight-path table with status codes.
- `evidence/idor-matrix.md` — two surfaces, each with the three-question result.
- `repair/` with both versions and `tests/`; `evidence/pytest.txt`,
  `evidence/pytest-vulnerable.txt`.
- `evidence/finding-idor.md`.

## Verification

- [ ] Two distinct accounts exist and both sessions work.
- [ ] B received an object whose `UserId` is A's, and both values are recorded.
- [ ] `/api/Users` behaves differently for anonymous and authenticated callers, and the returned fields are
      documented.
- [ ] Eight forced-browsing paths tested and each classified.
- [ ] A second object-bearing endpoint tested the same way.
- [ ] Fixed service returns `404` for another user's invoice; tests pass on the fix and fail on the vulnerable
      version.
- [ ] No object belonging to another user was modified or deleted.

## Teardown and reset

```bash
deactivate 2>/dev/null
```

Remove the items you added to your own baskets, or revert `pre-lab-303-02` to restore Juice Shop's database.
Keep `repair/` and `evidence/`. If you created extra accounts beyond the two, delete them through your own
profile settings.

## Reflection

1. The fixed service returns `404` rather than `403` for another user's invoice. Give one argument for each
   choice, and say which you would recommend for a financial API.
2. `/api/Users` required authentication but not a role. Why is "requires login" a weak authorization statement?
3. Your IDOR test used two accounts with equal privileges. Describe the finding you would miss if you only had
   one.
4. The tests fail on the vulnerable version. Explain why that matters more than the tests passing on the fixed
   one.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Proof | Single account, status codes only | Two accounts, B sees A's object | Two accounts plus `UserId` comparison and a second surface |
| Function-level testing | Not attempted | `/api/Users` tested | Tested, fields documented, and role requirement discussed |
| Forced browsing | Fewer than four paths | Eight paths classified | Classified, with a disclosure argument for the `200`s |
| Repair | Advice only | Fixed handler | Fixed handler plus tests that fail on the vulnerable version |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Both cookie jars are identical | Second login reused the first jar path | Log in again with `-c evidence/b.jar` |
| `whoami` returns `401` | Token cookie not sent | Use `-b` with the jar; check the file contains a `token` line |
| `jq` errors on an empty basket | No items added | Add a product as A first |
| `/api/Users` returns `401` for a valid session | Endpoint requires a different header | Compare with the browser's request in devtools |
| Fixed tests pass but vulnerable tests also pass | `sed` did not change the import | Check the first line of the generated test file |
| `404` for A's own invoice in the fixed app | Header missing | Send `X-Lab-User: alice` |

## References

1. OWASP WSTG v4.2 — WSTG-ATHZ-02 (Bypassing Authorization Schema), WSTG-ATHZ-03 (Privilege Escalation),
   WSTG-ATHZ-04 (IDOR).
2. OWASP Top 10:2025 — A01 Broken Access Control. <https://owasp.org/Top10/2025/>
3. OWASP ASVS 5.0 — V8 Authorization. <https://asvs.owasp.org/>
4. OWASP API Security Top 10 — API1:2023 Broken Object Level Authorization (the same flaw at API scale).

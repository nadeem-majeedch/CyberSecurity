---
title: "LAB-307-03 · Fix, Test and Verify"
description: "Repair every finding from LAB-307-01 and prove each fix with tests that fail on the vulnerable version."
module_code: CYB-307
level: 3
kind: lab
prerequisites: [LAB-307-01, LAB-307-02]
estimated_minutes: 150
difficulty: advanced
safety: local-only
lab_ids: [LAB-307-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [remediation, regression-testing, verification, secure-coding]
---

# LAB-307-03 · Fix, Test and Verify

## Scenario and background

You reviewed the application in LAB-307-01 and produced six findings with file-and-line citations. Now you have to
close them — not in a ticket, in code, with proof.

The rule for this lab is simple and unforgiving: **every finding gets a test that fails on the old code and passes
on the new code.** If a test passes on both, it is not testing the fix. At the end you have a remediation table in
which each row is backed by a command and an output, which is the artefact a client accepts.

## Learning objectives

By the end of this lab you can:

1. Fix injection, authorization, path, template, and storage flaws in a small application.
2. Write regression tests that fail on the vulnerable version and pass on the fixed one.
3. Preserve legitimate functionality while removing the vulnerability.
4. Distinguish a fix from a mitigation and record which applies to each finding.
5. Produce a remediation table with evidence for every row.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python 3 + Flask | 3.10+, Flask 3.x | Fixed application |
| `bcrypt` | 4.x | Password storage |
| `pytest` | 7.x | Regression suite |
| `git` | 2.x | Baseline comparison |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** the application on `127.0.0.1:5071` and files under `~/lab/level-3/lab-307-03`.
    **Targets you must not use:** any network service. Keep the binding on loopback; the fixed version still
    shells out, and a fixed bug is not a licence to expose it.

    **Command-injection tests use `id` and `echo` only.** No reverse shells and no downloads, exactly as in
    LAB-307-01.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

Same adversary as LAB-307-01: an authenticated low-privilege user, plus an anonymous visitor for the routes that
should require login. Data remains synthetic. The change is that the application is now expected to refuse.

**Impact if not verified.** The six findings from LAB-307-01 are still exploitable until a test proves otherwise,
and an unverified fix is the most expensive kind: it closes the ticket, removes the urgency, and leaves the flaw in
place for the next assessment to find again.

## Environment

| Component | Detail |
| --- | --- |
| `notesapp.py` | The vulnerable baseline from LAB-307-01 |
| `app.py` | The fixed version you build here |
| Address | `127.0.0.1:5071` |
| Data | `notes.db` copied from LAB-307-01 (synthetic) |

## Before you start

```bash
mkdir -p ~/lab/level-3/lab-307-03 && cd ~/lab/level-3/lab-307-03
cp ~/lab/level-3/lab-307-01/app/notesapp.py .
cp -r ~/lab/level-3/lab-307-01/app/files .
cp ~/lab/level-3/lab-307-01/app/notes.db .
mkdir -p tests evidence

git init -q
git add notesapp.py files notes.db
git -c user.email=lab@test -c user.name=lab commit -qm "vulnerable baseline (LAB-307-01)"
git log --oneline
```

**Expected:** one commit. That commit is your baseline — the code your tests must fail against.

## Procedure

### 1. Copy and rename

```bash
cp notesapp.py app.py
```

Keep `notesapp.py` untouched. It is the control in your experiment.

### 2. Fix the secret and the debug flag

Findings: hardcoded `secret_key` and `debug=True`.

```python
# app.py — replace the hardcoded key
import os, secrets

key = os.environ.get("NOTES_SECRET_KEY")
if not key:
    raise RuntimeError("NOTES_SECRET_KEY must be set; refusing to start with a default key")
app.secret_key = key
```

```python
# app.py — at the bottom
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5071, debug=False)
```

**Why fail closed:** a missing key must stop the process, not silently fall back. A default key is worse than no
key, because it looks configured.

**Generation for the lab:**

```bash
export NOTES_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
echo "key length: ${#NOTES_SECRET_KEY}"
```

### 3. Fix password storage and the SQL in registration

Findings: unsalted MD5, and string-concatenated SQL in `register` and `login`.

```python
# app.py — replaces md5() and the two query sites
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), stored.encode())
    except ValueError:
        return False

@app.post("/register")
def register():
    user = request.form["user"]
    password = request.form["pass"]
    if len(user) > 64 or len(password) < 12:
        return "invalid registration", 400
    with db() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE user = ?", (user,)).fetchone()
        if exists:
            return "registration failed", 400
        conn.execute("INSERT INTO users VALUES (?, ?)", (user, hash_password(password)))
    return "registered"

@app.post("/login")
def login():
    user = request.form["user"]
    password = request.form["pass"]
    row = db().execute("SELECT user, pass FROM users WHERE user = ?", (user,)).fetchone()
    if row and verify_password(password, row[1]):
        session.clear()
        session["user"] = row[0]
        return "logged in"
    return "denied", 401
```

**Two details that matter:** `session.clear()` before setting the user defeats session fixation (CYB-303), and the
same generic `"denied"` is returned for unknown users and wrong passwords, so the response cannot be used to
enumerate accounts.

**Migration note for the report:** existing MD5 hashes cannot be converted without the plaintext. The standard
approach is to verify against the old hash once, then re-hash with bcrypt on the next successful login. Write that
down; it is the part that turns a code fix into a deployable plan.

### 4. Fix the command injection

```python
# app.py — no shell, validated shape, bounded time
import ipaddress, re, subprocess

HOST_RE = re.compile(r"^[A-Za-z0-9.-]{1,253}$")

@app.get("/lookup")
def lookup():
    host = request.args.get("host", "")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        if not HOST_RE.fullmatch(host):
            return "invalid host", 400
    result = subprocess.run(
        ["getent", "hosts", host],
        capture_output=True, text=True, timeout=5, check=False,
    )
    return result.stdout
```

**Why both controls:** the argument list removes the shell, so `;` cannot start a second command. The shape check
removes inputs that are not addresses at all. Either alone would be a partial fix; together they are defensible.

### 5. Fix path traversal

```python
# app.py — canonicalise, then require containment
import pathlib

FILES = (pathlib.Path(__file__).parent / "files").resolve()

@app.get("/file")
def read_file():
    name = request.args.get("name", "")
    target = (FILES / name).resolve()
    if not target.is_relative_to(FILES) or not target.is_file():
        return "not found", 404
    return target.read_text()
```

### 6. Fix the template injection and the authorization flaw

```python
# app.py — user input becomes data, never template source
@app.get("/render")
def render():
    text = request.args.get("t", "hello")
    return render_template_string("Hello, {{ name }}", name=text)

# app.py — authentication and ownership, both enforced server-side
@app.get("/notes/<int:note_id>")
def get_note(note_id):
    user = session.get("user")
    if not user:
        return "authentication required", 401
    row = db().execute(
        "SELECT id, owner, body FROM notes WHERE id = ? AND owner = ?",
        (note_id, user),
    ).fetchone()
    if row is None:
        return "not found", 404
    return jsonify(row)
```

**Why the `owner = ?` clause rather than a check afterwards:** the query cannot return a foreign row, so there is
no window in which a forgotten `if` re-opens the flaw. And `404` rather than `403` avoids confirming that another
user's note exists.

### 7. Write the regression suite

```bash
cat > tests/test_remediation.py <<'PY'
"""Each test asserts a fixed behaviour. All must fail against notesapp.py."""
import importlib, os, shutil, subprocess, sys, pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("NOTES_SECRET_KEY", "test-key-not-for-deployment-0123456789")

import app as app_module

@pytest.fixture()
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as c:
        yield c

def q(sql, params=()):
    """Query helper: Flask's g needs an app context outside a request."""
    with app_module.app.app_context():
        return app_module.db().execute(sql, params).fetchall()

@pytest.fixture()
def as_alice(client):
    with client.session_transaction() as s:
        s["user"] = "alice"
    return client

# F-01 SQL injection
def test_login_sql_injection_does_not_bypass(client):
    r = client.post("/login", data={"user": "alice' OR '1'='1' -- ", "pass": "wrong"})
    assert r.status_code == 401

def test_registration_payload_is_stored_literally(client):
    payload = "mallory'); DROP TABLE users;--"
    client.post("/register", data={"user": payload, "pass": "Lab-Passw0rd-307"})
    rows = q("SELECT count(*) FROM users")[0][0]
    assert rows >= 3   # table survived; no injection executed

# F-02 command injection
def test_command_injection_does_not_execute(client):
    r = client.get("/lookup", query_string={"host": "127.0.0.1; id"})
    assert r.status_code == 400 or "uid=" not in r.get_data(as_text=True)

@pytest.mark.skipif(shutil.which("getent") is None, reason="getent is Linux-only")
def test_legitimate_lookup_still_works(client):
    r = client.get("/lookup", query_string={"host": "127.0.0.1"})
    assert r.status_code == 200

# F-03 path traversal
def test_traversal_is_refused(client):
    assert client.get("/file", query_string={"name": "../notesapp.py"}).status_code == 404

def test_legitimate_file_still_reads(client):
    assert client.get("/file", query_string={"name": "a.txt"}).status_code == 200

# F-04 template injection
def test_template_expression_is_not_evaluated(client):
    body = client.get("/render", query_string={"t": "{{7*7}}"}).get_data(as_text=True)
    assert "49" not in body and "{{7*7}}" in body

# F-05 authorization
def test_anonymous_cannot_read_notes(client):
    assert client.get("/notes/1").status_code == 401

def test_user_cannot_read_another_users_note(as_alice):
    foreign = q("SELECT id FROM notes WHERE owner != 'alice' LIMIT 1")[0][0]
    assert as_alice.get(f"/notes/{foreign}").status_code == 404

def test_user_can_read_own_note(as_alice):
    own = q("SELECT id FROM notes WHERE owner = 'alice' LIMIT 1")[0][0]
    r = as_alice.get(f"/notes/{own}")
    assert r.status_code == 200 and r.get_json()[1] == "alice"

# F-06 password storage
def test_password_is_not_stored_as_md5(client):
    client.post("/register", data={"user": "hashcheck", "pass": "Lab-Passw0rd-307"})
    stored = q("SELECT pass FROM users WHERE user = 'hashcheck'")[0][0]
    assert not (len(stored) == 32 and all(c in "0123456789abcdef" for c in stored))
    assert stored.startswith("$2")

# F-07 secret key
def test_app_refuses_to_start_without_a_secret():
    env = {k: v for k, v in os.environ.items() if k != "NOTES_SECRET_KEY"}
    r = subprocess.run([sys.executable, "-c", "import app"],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "NOTES_SECRET_KEY" in (r.stderr + r.stdout)
PY

python -m pytest -q
```

**Expected:** all tests pass. On a Linux lab host that is twelve; on macOS or Windows the `getent` test skips, so
you will see eleven passed and one skipped. Both are correct — record which you saw.

**Then the essential step** — prove they are testing the fix:

```bash
sed 's/^import app as app_module/import notesapp as app_module/' tests/test_remediation.py > tests/test_vulnerable.py
python -m pytest tests/test_vulnerable.py -q; echo "exit=$?"
```

**Expected:** at least six failures, and a non-zero exit. Record the output verbatim in
`evidence/tests-against-vulnerable.txt`. If everything passes, your tests are not exercising the vulnerability —
stop and fix them before writing the report.

Delete the temporary file afterwards:

```bash
rm tests/test_vulnerable.py
```

### 8. Verify by hand, then write the remediation table

```bash
python app.py &
sleep 2
B='http://127.0.0.1:5071'
curl -sS -o /dev/null -w 'ssti=%{http_code} ' -G "$B/render" --data-urlencode 't={{7*7}}'
curl -sS -G "$B/render" --data-urlencode 't={{7*7}}'; echo
curl -sS -o /dev/null -w 'traversal=%{http_code}\n' -G "$B/file" --data-urlencode 'name=../notesapp.py'
curl -sS -o /dev/null -w 'anon-note=%{http_code}\n' "$B/notes/1"
kill %1
```

**Expected:** `ssti=200` with the literal `{{7*7}}`, `traversal=404`, `anon-note=401`.

Now `evidence/remediation.md`:

| ID | Finding | Fix applied | Disposition | Test | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F-01 | SQL injection in login/register | Parameterised queries | Fix | `test_login_sql_injection_does_not_bypass` | pytest output | Closed |
| F-02 | Command injection | Arg list, no shell, shape check | Fix | `test_command_injection_does_not_execute` | pytest output | Closed |
| … | … | … | … | … | … | … |

For any row where you used a mitigation rather than a fix, say so and explain why. Then add a short
**residual risk** section: no rate limiting on login, no lockfile in the project, `getent` still shelling out to a
binary, and anything else you noticed and deliberately did not change.

## Evidence to collect

- `app.py` — the fixed application.
- `tests/test_remediation.py` — twelve tests.
- `evidence/pytest-fixed.txt` — passing run.
- `evidence/tests-against-vulnerable.txt` — failing run against `notesapp.py`.
- `evidence/remediation.md` — the table plus residual risks.
- `evidence/manual-verification.txt` — the three `curl` results.
- `git log --oneline` showing the vulnerable baseline commit.

## Verification

- [ ] Every finding from LAB-307-01 has a row in the remediation table.
- [ ] All tests pass on `app.py` (twelve on Linux; eleven plus one skip where `getent` is absent).
- [ ] At least six of those tests fail on `notesapp.py`, with output saved.
- [ ] Legitimate functions still work: file read, lookup, own-note read, login.
- [ ] Anonymous access to notes returns `401`; foreign note returns `404`.
- [ ] Stored password begins `$2` (bcrypt) and is not a 32-character hex digest.
- [ ] The app refuses to start without `NOTES_SECRET_KEY`.
- [ ] Residual risks listed.

## Teardown and reset

```bash
pkill -f 'python app.py'
deactivate 2>/dev/null
```

The application is loopback-only and disposable. Keep the directory: the remediation table and the two test runs
are the Level 3 evidence of remediation capability.

## Reflection

1. `test_registration_payload_is_stored_literally` asserts that the `users` table still exists. Why is that a
   better test than asserting the response contains no error?
2. You fixed the authorization flaw by changing the query, not by adding an `if`. Give two reasons that is more
   robust over time.
3. The old MD5 hashes could not be converted. Describe the migration you would implement and the risk it carries
   during the transition.
4. Which finding did you mitigate rather than fix, and what would a real fix require?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Fix coverage | Fewer than four findings | All six fixed | All six fixed, with the migration path noted |
| Test quality | Tests pass on both versions | Tests fail on vulnerable code | Failures are specific, and legitimate-function tests guard against over-restriction |
| Verification evidence | Output pasted without context | Commands and outputs recorded | Reproducible commands, version, and a before/after comparison |
| Reporting | List of changes | Remediation table | Table plus dispositions and a residual-risk section |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `RuntimeError: NOTES_SECRET_KEY must be set` | Env var not exported in this shell | `export NOTES_SECRET_KEY=...`; tests set a default |
| Tests import the wrong module | `tests/test_vulnerable.py` left in place | Delete it; the fixture imports `app` |
| `notes.db` missing tables | Copied without data, or wrong path | Re-seed using LAB-307-01's script |
| bcrypt hash does not start `$2` | `hash_password` not used in `register` | Check the insert uses the function |
| `404` for your own note | `as_alice` fixture not applied | Add the fixture parameter to the test |
| Subprocess test passes when it should fail | `NOTES_SECRET_KEY` still in the environment | Remove it in the test's `env` dict, as shown |
| `test_legitimate_lookup_still_works` errors with `FileNotFoundError` | `getent` is not present (macOS, Windows, minimal container) | Expected: the test skips when `getent` is missing. Run the lab on the Linux VM for the full set |

## References

1. OWASP Top 10:2025 — A05 Injection, A01 Broken Access Control, A07 Authentication Failures.
   <https://owasp.org/Top10/2025/>
2. OWASP Application Security Verification Standard 5.0 — V1, V6, V8. <https://asvs.owasp.org/>
3. OWASP Password Storage Cheat Sheet. Accessed 2026-10-29.
4. Python `subprocess` documentation — `shell=False` and argument lists. Accessed 2026-10-29.

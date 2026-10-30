---
title: "LAB-303-01 · Insecure Login Workflow"
description: "Measure an authentication flow for enumeration, rate limiting, policy and storage, then build the version that resists all four."
module_code: CYB-303
level: 3
kind: lab
prerequisites: [CYB-303]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-303-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [authentication, enumeration, rate-limiting, password-storage, bcrypt]
---

# LAB-303-01 · Insecure Login Workflow

## Scenario and background

A login page is a small distributed system pretending to be a form. It must decide, for each attempt, whether to
reveal that an account exists, how many attempts to permit, what to accept as a password, and how to store it.
Get any of those wrong and the strongest password policy in the world does not help.

You will assess two applications — DVWA's brute-force module and Juice Shop's registration and login — then build
the corrected login yourself and prove each fix with a test. The corrected version is the artefact; the findings
are the argument.

## Learning objectives

By the end of this lab you can:

1. Determine whether a login reveals account existence through message, status, or timing.
2. Demonstrate the absence of rate limiting with a bounded, ethical attempt sequence.
3. Test whether a password policy is enforced server-side or only in the browser.
4. Identify a fast, unsalted password hash and explain its consequences quantitatively.
5. Implement a login with generic errors, per-account throttling, bcrypt storage, and constant-time comparison.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| DVWA | current `master` | `http://192.0.2.30:4280`, **Low** |
| Juice Shop | 20.3.0 | `http://192.0.2.30:3000` |
| `curl` | 7.81+ | `-w '%{time_total}'` for timing |
| Python 3 + `bcrypt`, `flask`, `pytest` | 3.10+ | Fixed implementation |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `192.0.2.30:4280` (DVWA), `192.0.2.30:3000` (Juice Shop), and a Flask app you run
    on `127.0.0.1:5001`.
    **Targets you must not use:** any real login form, any account you do not own, and any service outside the
    lab.

    **Bounded attempts only.** This lab uses a maximum of 30 requests per test. Do not run a wordlist, do not use
    a cracking tool, and do not attempt to recover any password. You are measuring whether a control exists, not
    defeating it — the difference is 30 requests versus 30 million.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary has a list of email addresses (from a breach, a leak, or a guess) and no passwords. Their goal is to
convert the list into valid accounts. Enumeration tells them which addresses are real; absent rate limiting lets
them try common passwords; weak storage means a future database leak converts instantly into credentials.

The DVWA database holds synthetic users. The Juice Shop accounts are yours. No real credential is involved
anywhere in this lab.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Requests, fixed implementation | 127.0.0.1:5001 |
| `lab-web` | DVWA, Juice Shop | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                      lab-web 192.0.2.30
  curl ───────────────────────────────▶ :4280 DVWA (brute force module)
  curl ───────────────────────────────▶ :3000 Juice Shop (login, /api/Users)
  fixlogin/ 127.0.0.1:5000  local only
```

## Before you start

1. Snapshot `pre-lab-303-01`.
2. Log in to DVWA and save a cookie jar (see LAB-302-01 if you need the command).
3. Create `~/lab/level-3/lab-303-01/{evidence,fixlogin/tests}`.
4. Register two Juice Shop accounts you own: `learner303a@lab.test`, `learner303b@lab.test`.

## Procedure

### 1. Test for account enumeration

Send a login for an account you know exists and one that certainly does not, and compare everything: status,
body, headers, and time.

```bash
J='http://192.0.2.30:3000/rest/user/login'
for email in learner303a@lab.test definitely-not-a-user-303@lab.test; do
  echo "--- $email"
  curl -sS -o /tmp/body.txt -w 'status=%{http_code} time=%{time_total}\n' \
    -X POST "$J" -H 'Content-Type: application/json' \
    --data "{\"email\":\"$email\",\"password\":\"wrong-on-purpose\"}"
  head -c 200 /tmp/body.txt; echo
done
```

**Expected:** the same status and message for both. That is a **correct** design — the login endpoint does not
confirm existence.

Now test the registration endpoint, which is where enumeration usually survives:

```bash
J2='http://192.0.2.30:3000/api/Users'
for email in learner303a@lab.test brand-new-303@lab.test; do
  echo "--- $email"
  curl -sS -o /tmp/reg.txt -w 'status=%{http_code}\n' -X POST "$J2" \
    -H 'Content-Type: application/json' \
    --data "{\"email\":\"$email\",\"password\":\"Lab-Passw0rd-303\",\"passwordRepeat\":\"Lab-Passw0rd-303\"}"
  head -c 200 /tmp/reg.txt; echo
done
```

**Expected:** a different status or message for the existing address (`409`-style "already exists") versus the
new one (`201`). That difference is enumeration: an attacker can test a million addresses and learn which are
registered.

**Is that always a finding?** Not automatically — registration must tell a user their address is taken. The
reportable point is whether the response is *cheap to enumerate at scale* (no rate limit, no CAPTCHA) and
whether login or reset leaks the same fact. State the reasoning; do not simply flag the word "exists".

**Timing, handled honestly:** a lookup-then-compare implementation is often measurably slower for known users.
Measuring this requires many samples and a quiet network. Take 10 samples per case, report the median and the
spread, and if the distributions overlap, say the test was inconclusive. Do not report a single-request timing
difference as a finding.

### 2. Test for rate limiting and lockout

DVWA's brute-force module is the cleanest demonstration: it accepts unlimited attempts and reports nothing.

```bash
DV='http://192.0.2.30:4280/vulnerabilities/brute/'
start=$(date +%s)
for i in $(seq 1 25); do
  code=$(curl -sS -o /tmp/bf.html -w '%{http_code}' -b evidence/dvwa.jar -G "$DV" \
    --data-urlencode 'username=admin' \
    --data-urlencode "password=wrong-$i" \
    --data-urlencode 'Login=Login')
  printf '%s:%s ' "$i" "$code"
done
echo; echo "elapsed=$(( $(date +%s) - start ))s"
grep -o 'Username and/or password incorrect' /tmp/bf.html | head -1
```

**Expected:** 25 consecutive `200` responses with the generic failure message, no `429`, and no lockout. Now
confirm the account is still usable — which proves there is no lockout rather than merely no visible one:

```bash
curl -sS -b evidence/dvwa.jar -G "$DV" \
  --data-urlencode 'username=admin' --data-urlencode 'password=password' \
  --data-urlencode 'Login=Login' | grep -o 'Welcome to the password protected area' | head -1
```

**Expected:** the success string appears. **Interpretation:** an attacker with a wordlist has unlimited attempts at
network speed. The finding is "no rate limiting or account lockout on the authentication endpoint", and the
impact is offline-speed guessing against an online service.

**Why only 25:** the control either exists or it does not; 25 requests establish that. A thousand would be an
attack on a service, and the marginal evidence is zero.

### 3. Test whether the password policy is server-side

The browser rejects short passwords. Test the server directly:

```bash
for pw in a Lab-Passw0rd-303; do
  echo "--- password length ${#pw}"
  curl -sS -o /tmp/pw.txt -w 'status=%{http_code}\n' -X POST 'http://192.0.2.30:3000/api/Users' \
    -H 'Content-Type: application/json' \
    --data "{\"email\":\"policy-${#pw}-303@lab.test\",\"password\":\"$pw\",\"passwordRepeat\":\"$pw\"}"
  head -c 160 /tmp/pw.txt; echo
done
```

**Expected:** record what your instance does. A `201` for the one-character password means the policy is
client-side only — the single most common form of this finding. A `400` with a policy message means the server
enforces it; note the minimum length and whether complexity is required.

**Why it matters:** client-side validation protects the user experience, not the data. Anything the browser
enforces can be removed with devtools or bypassed with `curl`.

### 4. Identify the password storage

You already extracted DVWA's `users` table in [LAB-302-01](../02-injection-and-xss/lab-01-sql-injection.md).
Look at the hashes again:

```bash
grep -oE '\b[0-9a-f]{32}\b' ~/lab/level-3/lab-302-01/evidence/union-users.html | head -3
```

**Expected:** 32 hexadecimal characters — the length and charset of an unsalted MD5 digest. That is a hypothesis;
test it without cracking anything, by hashing a value you already know. DVWA's documented default password for
`admin` is `password`, which is public knowledge and not a secret you are recovering:

```bash
printf 'password' | md5sum
```

**Expected:** `5f4dcc3b5aa765d61d8327deb882cf99`. If that string appears in the extracted table, you have
confirmed: **MD5, unsalted, no work factor**.

**Now quantify it.** The argument is not "MD5 is old"; it is "this hash can be tested at this rate":

```bash
python3 - <<'PY'
import hashlib, time, bcrypt

N = 200_000
candidates = [f"candidate-{i}".encode() for i in range(N)]

t0 = time.perf_counter()
for c in candidates:
    hashlib.md5(c).hexdigest()
md5_rate = N / (time.perf_counter() - t0)

t0 = time.perf_counter()
for c in candidates[:50]:
    bcrypt.hashpw(c, bcrypt.gensalt(rounds=12))
bc_rate = 50 / (time.perf_counter() - t0)

print(f"md5:    {md5_rate:,.0f} hashes/sec")
print(f"bcrypt: {bc_rate:,.1f} hashes/sec  (cost 12)")
print(f"ratio:  {md5_rate / bc_rate:,.0f}x")
PY
```

**Expected:** MD5 in the millions per second on one CPU core; bcrypt cost 12 in the tens. The ratio is the
finding, expressed as a number you measured rather than a claim you copied.

State your assumptions in the report: single core, CPU only, this machine. A GPU changes the MD5 figure by orders
of magnitude and the bcrypt figure far less — which is the entire reason memory-hard functions are recommended.

### 5. Build the fixed login

```bash
cd ~/lab/level-3/lab-303-01/fixlogin
cat > app.py <<'PY'
"""Login with the four controls: generic errors, throttling, bcrypt, constant-time compare."""
import time
import bcrypt
from flask import Flask, request, jsonify

app = Flask(__name__)

USERS = {}                 # email -> bcrypt hash (in-memory lab store)
ATTEMPTS = {}              # email -> [timestamps]
MAX_ATTEMPTS = 5
WINDOW = 300               # seconds

GENERIC = "Invalid email or password."

def hash_password(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=12))

def verify(pw: str, stored: bytes) -> bool:
    return bcrypt.checkpw(pw.encode(), stored)

def throttled(email: str) -> bool:
    now = time.time()
    recent = [t for t in ATTEMPTS.get(email, []) if now - t < WINDOW]
    ATTEMPTS[email] = recent
    return len(recent) >= MAX_ATTEMPTS

@app.post("/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    email, pw = data.get("email", ""), data.get("password", "")
    if not email or len(pw) < 12:
        return jsonify(error="Email required; password must be at least 12 characters."), 400
    if email in USERS:
        return jsonify(error="Registration could not be completed."), 400
    USERS[email] = hash_password(pw)
    return jsonify(status="created"), 201

@app.post("/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    email, pw = data.get("email", ""), data.get("password", "")

    if throttled(email):
        return jsonify(error="Too many attempts. Try again later."), 429

    stored = USERS.get(email)
    if stored is None:
        # Equalise timing: hash something so the unknown-user path costs the same.
        bcrypt.checkpw(pw.encode(), bcrypt.hashpw(b"dummy", bcrypt.gensalt(rounds=12)))
        ATTEMPTS.setdefault(email, []).append(time.time())
        return jsonify(error=GENERIC), 401

    if not verify(pw, stored):
        ATTEMPTS.setdefault(email, []).append(time.time())
        return jsonify(error=GENERIC), 401

    ATTEMPTS.pop(email, None)
    return jsonify(status="ok"), 200
PY
```

Then the tests that prove each control:

```bash
cat > tests/test_login.py <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from app import app, USERS, ATTEMPTS, MAX_ATTEMPTS

@pytest.fixture(autouse=True)
def clean():
    USERS.clear(); ATTEMPTS.clear()
    yield

@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

def register(client, email="a@lab.test", pw="Lab-Passw0rd-303"):
    return client.post("/register", json={"email": email, "password": pw})

def test_short_password_rejected_by_server(client):
    assert register(client, pw="abc").status_code == 400

def test_duplicate_registration_does_not_confirm_existence(client):
    register(client)
    r = register(client)
    assert r.status_code == 400
    assert "already" not in r.get_json()["error"].lower()

def test_wrong_password_and_unknown_user_are_indistinguishable(client):
    register(client)
    a = client.post("/login", json={"email": "a@lab.test", "password": "wrong"})
    b = client.post("/login", json={"email": "nobody@lab.test", "password": "wrong"})
    assert a.status_code == b.status_code == 401
    assert a.get_json() == b.get_json()

def test_throttle_after_max_attempts(client):
    register(client)
    codes = [client.post("/login", json={"email": "a@lab.test", "password": "wrong"}).status_code
             for _ in range(MAX_ATTEMPTS + 1)]
    assert codes[-1] == 429

def test_correct_password_still_works(client):
    register(client)
    assert client.post("/login", json={"email": "a@lab.test",
                                       "password": "Lab-Passw0rd-303"}).status_code == 200
PY

python3 -m venv .venv && . .venv/bin/activate
pip install flask bcrypt pytest
python -m pytest -q
```

**Expected:** five passing tests.

**Why the duplicate-registration message is deliberately vague:** a truthful "this email is registered" is
useful to a user and expensive in enumeration. The compromise is a generic failure plus an email to the address
if it already exists — which is what production systems should do, and worth a sentence in your report.

### 6. Verify against the live app, not only the tests

```bash
python app.py &                     # 127.0.0.1:5000 by default; stop after this step
sleep 2
curl -sS -o /dev/null -w 'register=%{http_code}\n' -X POST http://127.0.0.1:5000/register \
  -H 'Content-Type: application/json' \
  --data '{"email":"fixed@lab.test","password":"Lab-Passw0rd-303"}'
for i in 1 2 3 4 5 6; do
  curl -sS -o /dev/null -w "$i=%{http_code} " -X POST http://127.0.0.1:5000/login \
    -H 'Content-Type: application/json' \
    --data '{"email":"fixed@lab.test","password":"wrong"}'
done; echo
kill %1
```

**Expected:** `register=201`, then `401 401 401 401 401 429`. The throttle is real, not just asserted.

## Evidence to collect

- `evidence/enumeration.txt` — both login responses and both registration responses.
- `evidence/ratelimit.txt` — the 25 attempts with codes, elapsed time, and the post-test successful login.
- `evidence/policy.txt` — the one-character password result.
- `evidence/hash-analysis.txt` — the extracted hashes, the `md5sum` confirmation, and the benchmark output.
- `fixlogin/` — `app.py` and `tests/`, plus `evidence/pytest.txt` and `evidence/live-throttle.txt`.
- `evidence/login-assessment.md` — a four-row table: control, observed, expected, recommendation.

## Verification

- [ ] Login and registration responses compared for both a known and an unknown address.
- [ ] At most 30 authentication requests were sent to any endpoint; the count is recorded.
- [ ] No rate limit or lockout observed on DVWA, and the account still worked afterwards.
- [ ] Password policy tested with a one-character password via `curl`.
- [ ] Hash identified, confirmed by hashing a documented default, and benchmarked.
- [ ] All five tests pass, and the live throttle returns `429` on the sixth attempt.

## Teardown and reset

```bash
deactivate 2>/dev/null
pkill -f 'python app.py' 2>/dev/null || true
```

Delete the Juice Shop accounts created for the policy test if they exist. Revert `pre-lab-303-01` to clear DVWA
state. Keep `evidence/` and `fixlogin/` — the fixed implementation is reused in the Level 3 report as evidence of
remediation capability.

## Reflection

1. Registration must tell a user their address is taken. Explain how you would do that without enabling cheap
   enumeration, and what the trade-off costs the user.
2. Your throttle is per email address. Describe the attack it does not stop, and the second control that does.
3. The benchmark measured one core. Explain why the MD5:bcrypt ratio grows on a GPU and what that means for the
   choice of algorithm rather than work factor.
4. The unknown-user path in your fixed code performs a dummy hash. What would an attacker learn without it?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Enumeration analysis | "Login is generic, so fine" | Login and registration both tested | Both tested, with the registration trade-off argued |
| Rate limiting | Claims absent | 25 attempts recorded | Recorded, plus post-test login proving no lockout, plus the per-account limitation named |
| Storage analysis | "MD5 is weak" | Hash identified and confirmed | Confirmed and quantified with a measured benchmark and stated assumptions |
| Remediation | Advice only | Working fixed login | Working login with tests for each control and a live `429` |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| DVWA requests return the login page | Cookie jar stale | Re-run the login `curl` with `-c` |
| All registration attempts return `400` | Missing field the API requires | Inspect the real browser request in devtools and copy the field names |
| `bcrypt` install fails | Build tools missing | `sudo apt install build-essential python3-dev`, or use `argon2-cffi` |
| Benchmark takes too long | bcrypt cost 12 is intentionally slow | Reduce sample count, not the cost — the cost is the point |
| `pytest` cannot import `app` | Wrong working directory | Run from `fixlogin/`; keep the `sys.path` line |
| Live throttle does not return `429` | Server restarted between attempts | Keep one process; the attempt store is in memory |

## References

1. OWASP WSTG v4.2 — WSTG-ATHN-03 (Weak Lock Out), WSTG-ATHN-07 (Password Policy), WSTG-IDNT-04 (Account Enumeration).
2. OWASP Password Storage Cheat Sheet. Accessed 2026-10-29.
3. OWASP Authentication Cheat Sheet. Accessed 2026-10-29.
4. OWASP Top 10:2025 — A07 Authentication Failures. <https://owasp.org/Top10/2025/>
5. Python `bcrypt` documentation. Accessed 2026-10-29.

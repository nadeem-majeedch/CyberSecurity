---
title: "LAB-304-02 · Path Traversal and File Inclusion"
description: "Read files outside the intended directory, bypass a naive filter, then fix it with canonicalisation and containment."
module_code: CYB-304
level: 3
kind: lab
prerequisites: [CYB-304]
estimated_minutes: 75
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-304-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [path-traversal, lfi, file-inclusion, canonicalisation]
---

# LAB-304-02 · Path Traversal and File Inclusion

## Scenario and background

DVWA's file-inclusion module takes a page name and includes it. At Low there is no filtering at all, so
`../../../../etc/passwd` is enough. At Medium, the developer has added a filter that removes `../` — which is
exactly the kind of fix that feels like a fix and is not.

You will demonstrate both, then write the containment check that cannot be bypassed by encoding, because it
compares the final resolved path rather than the input string.

## Learning objectives

By the end of this lab you can:

1. Read a file outside the intended directory through a path parameter.
2. Bypass a filter that removes `../` using a nested sequence, and explain why the filter failed.
3. Distinguish traversal from local file inclusion and state when inclusion becomes code execution.
4. Implement canonicalisation plus containment and prove it against five bypass attempts.
5. Explain why a symlink inside the base directory is still a traversal.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| DVWA | current `master` | `http://192.0.2.30:4280`; Low then Medium |
| `curl`, `jq` | 7.81+, 1.6+ | Requests and evidence |
| Python 3 + Flask + pytest | 3.10+ | Repair exercise |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `http://192.0.2.30:4280` (DVWA) and a local Flask service on `127.0.0.1:5005`.
    **Targets you must not use:** any other host.

    **Read only, and only lab files.** `/etc/passwd` on your own lab VM is a safe, standard demonstration file —
    it contains no secrets on a default install. Do **not** target `/etc/shadow`, SSH private keys, application
    configuration with credentials, or anything belonging to a real system. If you find a file that looks like it
    contains a secret, stop and record the path only; do not open it.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary is an authenticated low-privilege user able to influence a filename parameter. Their capability is
whatever the web-server process can read. On a real host that includes application configuration, source code,
and sometimes credentials — which is why traversal is usually rated by what it exposes, not by the traversal
itself.

**Impact if exploited.** Disclosure of any file the web process can read — configuration, source, keys — and,
because this module *includes* rather than reads, execution of any PHP file the attacker can place on the host.
The severity follows the worst file reachable, not the traversal itself.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Requests, repair service | 127.0.0.1:5005 |
| `lab-web` | DVWA | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                    lab-web 192.0.2.30
  curl ?page= ─────────────────────▶ :4280 DVWA (/vulnerabilities/fi/)
  traversalfix/ 127.0.0.1:5005  local only
```

## Before you start

1. Snapshot `pre-lab-304-02`.
2. Log in to DVWA, save `evidence/dvwa.jar`, confirm **Low**.
3. Create `~/lab/level-3/lab-304-02/{evidence,traversalfix/tests}`.

## Procedure

### 1. Baseline: a legitimate include

```bash
DV='http://192.0.2.30:4280'
curl -sS -b evidence/dvwa.jar -G "$DV/vulnerabilities/fi/" \
  --data-urlencode 'page=file1.php' -o evidence/legit.html
grep -oE 'include|File 1|Hello' evidence/legit.html | sort -u | head
```

**Expected:** the module renders one of its included files. You now know the parameter's name and its normal
shape.

### 2. Traverse to a file outside the web root

```bash
curl -sS -b evidence/dvwa.jar -G "$DV/vulnerabilities/fi/" \
  --data-urlencode 'page=../../../../etc/passwd' -o evidence/traversal.html
head -3 evidence/traversal.html
```

**Expected:** the first lines of `/etc/passwd`, starting `root:x:0:0:`. The page was told to include a file, and it
included one four directories up.

**Why `../../../../` four times:** the working directory is around `/var/www/html/vulnerabilities/fi/`. Four
levels reach `/`, and `/etc/passwd` is then absolute from there. A count that is too small fails; try more levels
if needed, and record how many your build required.

### 3. Add a filter, then bypass it

Switch DVWA to Medium, which strips `../`:

```bash
curl -sS -b evidence/dvwa.jar -c evidence/dvwa.jar -X POST "$DV/security.php" \
  --data 'security=medium&seclev_submit=Submit'

# Confirm the filter is active: the plain payload should now fail
curl -sS -b evidence/dvwa.jar -G "$DV/vulnerabilities/fi/" \
  --data-urlencode 'page=../../../../etc/passwd' | head -3
```

**Expected:** an error or a missing file — the filter removed the sequences.

Now the bypass. The filter removes `../` **once** per occurrence, and `....//` contains `../` starting at the
second character, so removing it leaves `../` behind:

```bash
curl -sS -b evidence/dvwa.jar -G "$DV/vulnerabilities/fi/" \
  --data-urlencode 'page=....//....//....//....//etc/passwd' -o evidence/bypass.html
head -3 evidence/bypass.html
```

**Expected:** `/etc/passwd` again. **This is the lesson of the lab:** a string filter operates on the input, and
the filesystem operates on the decoded result. Any gap between those two views is a bypass.

Other variants that defeat the same filter class, worth noting in your report even if you do not run them all:
`..%2f` (decoded after the filter), `..%252f` (double-encoded), backslashes on Windows, and absolute paths.

**Return DVWA to Low** before the next lab:

```bash
curl -sS -b evidence/dvwa.jar -X POST "$DV/security.php" --data 'security=low&seclev_submit=Submit'
```

### 4. Classify the flaw

Answer in your notes: is this traversal, LFI, or both? The module *includes* the file, so a file containing PHP
would execute — which makes it LFI, and the traversal is the mechanism. Record that distinction, and note that
this is why LFI is more severe than a file-read primitive: inclusion is execution.

**Do not** attempt to turn LFI into code execution by poisoning logs or uploading a file. It is a well-documented
technique, it is not needed to prove this finding, and it would put a working execution path in your lab.

### 5. Build the repair

```bash
cd ~/lab/level-3/lab-304-02/traversalfix
mkdir -p files tests
echo "quarterly report (synthetic)" > files/report.txt
echo "internal note (synthetic)" > files/note.txt

cat > vulnerable_app.py <<'PY'
"""Vulnerable: concatenates the name onto the base directory."""
import pathlib
from flask import Flask, request, abort
app = Flask(__name__)
BASE = pathlib.Path(__file__).parent / "files"

@app.get("/read")
def read():
    name = request.args.get("name", "")
    return (BASE / name).read_bytes(), 200, {"Content-Type": "text/plain"}
PY

cat > app.py <<'PY'
"""Fixed: resolve first, then require containment inside BASE."""
import pathlib
from flask import Flask, request, abort
app = Flask(__name__)
BASE = (pathlib.Path(__file__).parent / "files").resolve()

@app.get("/read")
def read():
    name = request.args.get("name", "")
    target = (BASE / name).resolve()
    if not target.is_relative_to(BASE) or not target.is_file():
        abort(404)
    return target.read_bytes(), 200, {"Content-Type": "text/plain"}
PY
```

Tests for five bypass attempts plus the legitimate case:

```bash
cat > tests/test_traversal.py <<'PY'
import os, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from app import app, BASE

@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

def get(client, name):
    return client.get("/read", query_string={"name": name})

def test_legitimate_file_reads(client):
    r = get(client, "report.txt")
    assert r.status_code == 200 and b"synthetic" in r.data

@pytest.mark.parametrize("payload", [
    "../report.txt",              # sibling escape
    "../../../../etc/passwd",     # classic
    "....//....//etc/passwd",     # filter-bypass shape
    "/etc/passwd",                # absolute path overrides the base
    "..%2f..%2fetc%2fpasswd",     # encoded (Flask decodes before we see it)
])
def test_traversal_is_refused(client, payload):
    assert get(client, payload).status_code == 404

def test_symlink_inside_base_is_refused(client):
    link = BASE / "innocent.txt"
    if not link.exists():
        os.symlink("/etc/passwd", link)
    try:
        assert get(client, "innocent.txt").status_code == 404
    finally:
        link.unlink(missing_ok=True)

def test_missing_file_is_404(client):
    assert get(client, "nope.txt").status_code == 404
PY

python3 -m venv .venv && . .venv/bin/activate
pip install flask pytest
python -m pytest -q
```

**Expected:** eight passing tests (five parametrised traversal cases plus three others).

Then point the tests at `vulnerable_app` and confirm they fail — that is what proves they test the control:

```bash
sed 's/from app import app, BASE/from vulnerable_app import app, BASE/' tests/test_traversal.py > tests/test_vulnerable.py
python -m pytest tests/test_vulnerable.py -q || echo "expected failures"
rm tests/test_vulnerable.py
```

### 6. Verify live

```bash
python app.py &      # 127.0.0.1:5000
sleep 2
for p in 'report.txt' '../report.txt' '../../../../etc/passwd' '/etc/passwd'; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -G http://127.0.0.1:5000/read --data-urlencode "name=$p")
  printf '%-28s %s\n' "$p" "$code"
done
kill %1
```

**Expected:** `200 404 404 404`.

### 7. Write the finding

In `evidence/traversal-finding.md`: the module, the parameter, the successful request and its output (three lines
maximum — do not paste a whole system file), the filter that was bypassed and why, whether inclusion makes it code
execution, and the fix with the containment code.

## Evidence to collect

- `evidence/traversal.html` — first three lines only.
- `evidence/bypass.html` — the Medium-level bypass, first three lines.
- `evidence/dvwa-security.txt` — output proving the level before and after.
- `traversalfix/` with both versions and `tests/`; `evidence/pytest.txt`,
  `evidence/pytest-vulnerable.txt`.
- `evidence/traversal-finding.md`.

## Verification

- [ ] Traversal worked at Low and the output is captured (three lines, no secrets).
- [ ] DVWA was set to Medium, the plain payload failed, and `....//` succeeded.
- [ ] DVWA returned to Low afterwards.
- [ ] Eight tests pass; the same tests fail against the vulnerable version.
- [ ] Absolute path, encoded sequence, sibling escape, and symlink are all refused.
- [ ] The finding states whether the flaw is read-only or executable.

## Teardown and reset

```bash
deactivate 2>/dev/null
rm -f traversalfix/files/innocent.txt
```

Confirm DVWA is back at **Low**. Revert `pre-lab-304-02` to clear any state you changed. Keep
`traversalfix/` and `evidence/`.

## Reflection

1. The filter removed `../` and the bypass still worked. Explain the general principle in one sentence, without
   using the word "filter".
2. `(BASE / "/etc/passwd")` ignores `BASE` entirely. Why is that a language behaviour rather than a bug, and what
   does it mean for any concatenation-based path check?
3. The fixed code calls `.resolve()` before comparing. What does that do to a symlink, and why does the check
   without it pass a malicious link?
4. LFI is rated higher than arbitrary file read. Give the one-word reason and one example file that makes the
   difference concrete.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Demonstration | Payload shown, not run | Traversal executed at Low | Low and Medium, with the bypass explained |
| Classification | "Traversal" | Traversal and inclusion distinguished | Distinguished, with the execution implication stated |
| Fix | Filter suggested | Containment implemented | Containment plus `resolve()`, with the symlink case tested |
| Testing | Manual only | Tests pass | Tests fail on the vulnerable version and cover five bypass shapes |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Traversal returns the module's own page | Too few `../` levels | Add levels until the read succeeds; record the count |
| Medium bypass returns an error | `....//` count insufficient | Repeat the pattern; each pair consumes one level after filtering |
| `security.php` POST has no effect | Missing session or wrong field name | Inspect the form in devtools; include `seclev_submit=Submit` |
| `is_relative_to` missing | Python < 3.9 | Upgrade Python; the check is not equivalent to a string prefix |
| Symlink test skipped | Link already existed | Remove `files/innocent.txt` and rerun |
| `404` for `report.txt` | Wrong base directory | `BASE` is relative to `app.py`; print it once |

## References

1. OWASP WSTG v4.2 — WSTG-ATHZ-01 Testing Directory Traversal and File Include.
2. OWASP Top 10:2025 — A01 Broken Access Control. <https://owasp.org/Top10/2025/>
3. Python `pathlib` — `resolve`, `is_relative_to`. Accessed 2026-10-29.
4. OWASP ASVS 5.0 — V5 File Handling. <https://asvs.owasp.org/>

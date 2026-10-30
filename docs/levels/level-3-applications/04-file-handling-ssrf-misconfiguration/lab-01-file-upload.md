---
title: "LAB-304-01 · File Upload Validation"
description: "Demonstrate how an upload endpoint becomes code execution, then build a handler that validates content, name, location and size."
module_code: CYB-304
level: 3
kind: lab
prerequisites: [CYB-304]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-304-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [file-upload, webshell, validation, flask, hardening]
---

# LAB-304-01 · File Upload Validation

## Scenario and background

DVWA's upload module performs exactly one check: it looks at the MIME type the client claimed. That single
mistake turns an image upload into an execution primitive, because the file lands in a served directory under a
name the client chose.

You will prove that with a file that prints a fixed string — not a shell, not a backdoor, just a demonstration
that the server executed your code. Then you will build the handler that would have stopped it, and test each
defence separately.

## Learning objectives

By the end of this lab you can:

1. Explain why a client-declared MIME type is not a validation control.
2. Demonstrate server-side execution of an uploaded file in a deliberately vulnerable application.
3. Implement content sniffing, generated names, non-executable storage, and a size limit.
4. Verify each control with a request that should fail and one that should succeed.
5. Write regression tests that fail if a control is removed.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| DVWA | current `master` | `http://192.0.2.30:4280`, **Low** |
| `curl` | 7.81+ | `-F` multipart uploads |
| Python 3 + Flask + Pillow | 3.10+, Flask 3.x, Pillow 10+ | Fixed handler |
| `pytest` | 7.x | Regression tests |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `http://192.0.2.30:4280` (DVWA) and a Flask service on `127.0.0.1:5004`.
    **Targets you must not use:** any other host.

    **The uploaded file is harmless by design.** It contains one `echo` statement printing a fixed string. Do not
    upload a shell, a reverse shell, or anything that accepts commands — the demonstration is complete without
    them, and a working backdoor in a lab is an incident waiting for a misconfigured adapter.

    **Delete your uploads in teardown.** DVWA's `hackable/uploads/` directory is web-accessible.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary has an account on the application (or, for a public upload form, no account at all). They can send a
multipart request with any filename, any declared type, and any bytes. The application stores the file in a
directory the web server serves and executes `.php` from. The consequence is code execution as the web-server
user, which is a foothold rather than a data leak.

**Impact if exploited.** Remote code execution as the web-server user. From there an attacker reads application
configuration, reaches internal services from the host's network position, and persists. This is a foothold, not a
data leak — which is why it outranks almost every other finding in this level.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Uploads, fixed handler | 127.0.0.1:5004 |
| `lab-web` | DVWA | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                    lab-web 192.0.2.30
  curl -F upload ──────────────────▶ :4280 DVWA (/vulnerabilities/upload/)
  curl proof ──────────────────────▶ :4280 /hackable/uploads/probe.php
  uploadfix/ 127.0.0.1:5004  local only
```

## Before you start

1. Snapshot `pre-lab-304-01`.
2. Log in to DVWA and save `evidence/dvwa.jar` (see LAB-302-01).
3. Create `~/lab/level-3/lab-304-01/{evidence,uploadfix/tests}`.

## Procedure

### 1. Create the harmless payload and a real image

```bash
cd ~/lab/level-3/lab-304-01
printf '<?php echo "LAB-304-01-upload-accepted"; ?>\n' > probe.php

python3 - <<'PY'
from PIL import Image
Image.new("RGB", (32, 32), (240, 240, 240)).save("ok.png")
PY
file ok.png probe.php
```

**Expected:** `ok.png` is reported as PNG image data; `probe.php` is ASCII text.

### 2. Upload the PHP file with a lying content type

DVWA's check trusts the client. Claim an image type while sending PHP:

```bash
curl -sS -b evidence/dvwa.jar -c evidence/dvwa.jar \
  -F 'uploaded=@probe.php;filename=probe.php;type=image/png' \
  -F 'Upload=Upload' \
  http://192.0.2.30:4280/vulnerabilities/upload/ \
  -o evidence/upload-response.html

grep -oE '(succesfully|Successfully|uploaded)[^<]*' evidence/upload-response.html | head -3
grep -oE 'hackable/uploads/[A-Za-z0-9._-]+' evidence/upload-response.html | head -3
```

**Expected:** a success message naming a path under `hackable/uploads/`. Record the exact filename.

**Why this worked:** the server checked `$_FILES['uploaded']['type']`, which is whatever the client put in the
multipart part header. Nothing looked at the bytes, the extension, or the storage location.

### 3. Request the uploaded file and observe execution

```bash
UP='http://192.0.2.30:4280/hackable/uploads/probe.php'
curl -sS -i "$UP" | head -20
```

**Expected:** a `200` whose body is `LAB-304-01-upload-accepted` — the PHP was executed by the web server, not
served as text. That single line of output is the whole finding: **arbitrary code execution as the web user**.

**Why the string and not a shell:** the proof is that the interpreter ran your code. A shell would add nothing to
the evidence and a great deal to the risk.

### 4. Note the second flaw: the name is yours

The filename in the URL is the one you sent. Nothing prevented `../../` or an overwrite of an existing file.
Record that as a separate defect from the type check — they have different fixes.

### 5. Build the hardened handler

```bash
cd uploadfix
cat > app.py <<'PY'
"""Hardened upload: content sniffing, re-encode, generated name, no execution, size limit."""
import io, uuid, pathlib
from flask import Flask, request, abort, send_from_directory
from PIL import Image

app = Flask(__name__)
STORE = pathlib.Path(__file__).parent / "uploads"
STORE.mkdir(exist_ok=True)
ALLOWED = {"image/png": "png", "image/jpeg": "jpg"}
MAX_BYTES = 1 * 1024 * 1024

def sniff(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None

@app.post("/avatar")
def avatar():
    f = request.files.get("file")
    if f is None:
        abort(400)
    data = f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        abort(413)
    claimed = sniff(data)
    if claimed not in ALLOWED:
        abort(415)
    try:
        img = Image.open(io.BytesIO(data)); img.verify()
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        abort(415)
    name = f"{uuid.uuid4().hex}.{ALLOWED[claimed]}"
    img.save(STORE / name)
    return {"stored_as": name}, 201

@app.get("/files/<name>")
def serve(name):
    return send_from_directory(STORE, name, as_attachment=True)
PY
```

Then the tests, one per control:

```bash
cat > tests/test_upload.py <<'PY'
import io, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from PIL import Image
from app import app, STORE

@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

def png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (10, 10, 10)).save(buf, format="PNG")
    buf.seek(0)
    return buf

def post(client, data, filename="x.png", content_type="image/png"):
    return client.post("/avatar",
                       data={"file": (data, filename, content_type)},
                       content_type="multipart/form-data")

def test_real_png_is_accepted(client):
    assert post(client, png_bytes()).status_code == 201

def test_php_with_image_content_type_is_rejected(client):
    r = post(client, io.BytesIO(b'<?php echo "x"; ?>'), filename="x.php", content_type="image/png")
    assert r.status_code == 415

def test_traversal_filename_is_not_used(client):
    r = post(client, png_bytes(), filename="../../evil.png")
    assert r.status_code == 201
    stored = r.get_json()["stored_as"]
    assert ".." not in stored and "/" not in stored

def test_oversize_is_rejected(client):
    big = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"A" * (1024 * 1024 + 10))
    assert post(client, big).status_code == 413

def test_svg_is_rejected(client):
    svg = io.BytesIO(b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')
    assert post(client, svg, filename="x.svg", content_type="image/svg+xml").status_code == 415

def test_files_are_served_as_attachments(client):
    name = post(client, png_bytes()).get_json()["stored_as"]
    r = client.get(f"/files/{name}")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("Content-Disposition", "")
PY

python3 -m venv .venv && . .venv/bin/activate
pip install flask pillow pytest
python -m pytest -q
```

**Expected:** six passing tests.

**Then break it deliberately** — this is the step that shows the tests have teeth. Comment out the `sniff()`
check and rerun: `test_php_with_image_content_type_is_rejected` and `test_svg_is_rejected` must fail. Restore it.

### 6. Verify with real requests

```bash
python app.py &          # 127.0.0.1:5000 — adjust if your app uses another port
sleep 2
curl -sS -o /dev/null -w 'png=%{http_code}\n'       -F 'file=@ok.png' http://127.0.0.1:5000/avatar
curl -sS -o /dev/null -w 'php=%{http_code}\n'       -F 'file=@probe.php;type=image/png' http://127.0.0.1:5000/avatar
curl -sS -o /dev/null -w 'traversal=%{http_code}\n' -F 'file=@ok.png;filename=../../evil.png' http://127.0.0.1:5000/avatar
kill %1
```

**Expected:** `201`, `415`, `201`. The traversal upload succeeding is the correct outcome: the name you sent was
discarded, so there was nothing to traverse.

### 7. Write the finding and the fix

In `evidence/upload-finding.md`: the request, the response path, the executed output, why the MIME check failed,
and the five layers with the code that implements them. Name the separate filename flaw explicitly.

## Evidence to collect

- `probe.php`, `ok.png` — the harmless payload and a valid image.
- `evidence/upload-response.html` — the vulnerable application's success response.
- `evidence/execution.txt` — `curl -i` of the uploaded file showing the executed string.
- `uploadfix/` with `app.py` and `tests/`; `evidence/pytest.txt`; `evidence/broken-check.txt` showing the tests
  failing when `sniff()` is removed.
- `evidence/upload-finding.md`.

## Verification

- [ ] PHP uploaded with a lying `type=image/png` and executed by the server.
- [ ] The executed output is captured verbatim, with the response headers.
- [ ] Six tests pass; removing the content check makes two of them fail.
- [ ] Live requests return `201`, `415`, `201`.
- [ ] Stored filenames are generated and contain no client-supplied path components.
- [ ] Uploaded files are served with `Content-Disposition: attachment`.

## Teardown and reset

**Remove the uploaded file from DVWA immediately** — it is web-accessible:

```bash
docker exec -u 0 -it $(docker ps --filter name=dvwa -q) \
  rm -f /var/www/html/hackable/uploads/probe.php
```

If the container name differs, list with `docker ps` and verify with
`curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.30:4280/hackable/uploads/probe.php` — it must return
`404`.

```bash
deactivate 2>/dev/null
rm -rf uploadfix/uploads/*
```

Then revert `pre-lab-304-01` for a clean DVWA state.

## Reflection

1. The upload succeeded in the traversal case. Explain why that is the correct behaviour, and what the alternative
   would cost legitimate users.
2. `sniff()` checks the first bytes. Describe a file that passes `sniff()` and `Pillow.verify()` but is still
   dangerous, and the control that addresses it.
3. Why is storing uploads outside the web root more robust than blocking `.php`?
4. Your handler re-encodes the image. Name two distinct attacks that re-encoding mitigates.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Demonstration | Described only | Upload executed, output captured | Executed, with headers and the exact request |
| Analysis | "No validation" | MIME check named as the flaw | MIME and filename flaws separated, with different fixes |
| Implementation | Partial checks | All five layers present | All five, with generated names verified and attachment serving |
| Testing | Manual only | Tests pass | Tests shown to fail when a control is removed |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| DVWA says the file type is not supported | Server checks the actual upload, or security level is not Low | Confirm `security=low` in the DVWA session |
| Upload succeeds but requesting it downloads the source | PHP handler not routed for that path | Check the URL; DVWA serves `.php` from `hackable/uploads/` at Low |
| `415` for a real PNG | `sniff()` signature mismatch | Confirm the file is a PNG with `file ok.png` |
| `413` never triggered | Test file smaller than the limit | Build the oversized buffer with the PNG signature plus padding |
| `send_from_directory` raises `NotFound` | Wrong `STORE` path | `STORE` is relative to `app.py`; print it once |
| Pillow `verify()` rejects a valid image | Image truncated during upload | Regenerate with Pillow and retry |

## References

1. OWASP File Upload Cheat Sheet. Accessed 2026-10-29.
2. OWASP WSTG v4.2 — WSTG-BUSL-09 Testing for Upload of Malicious Files.
3. OWASP Top 10:2025 — A05 Injection, A02 Security Misconfiguration. <https://owasp.org/Top10/2025/>
4. Flask — `send_from_directory` and `Content-Disposition`. Accessed 2026-10-29.

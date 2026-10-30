---
title: "LAB-302-02 · Reflected and Stored XSS"
description: "Execute proof-of-concept script in four different contexts, then fix each with the correct encoding and verify with tests."
module_code: CYB-302
level: 3
kind: lab
prerequisites: [CYB-302]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-302-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [xss, reflected, stored, dom, csp, output-encoding]
---

# LAB-302-02 · Reflected and Stored XSS

## Scenario and background

"XSS" is not one bug, and `<script>alert(1)</script>` is not one test. The payload that works in an HTML body
fails in an attribute; the payload that works in an attribute fails inside a JavaScript string; and DOM-based XSS
never reaches the server at all, so no filter can see it.

You will demonstrate XSS in DVWA's deliberately vulnerable modules, then work through a four-context application
you build yourself — one endpoint per context — so that each failure and each fix is isolated and visible. The
proof-of-concept is deliberately harmless: it changes the page title. Nothing exfiltrates data, and nothing
touches a cookie.

## Learning objectives

By the end of this lab you can:

1. Demonstrate reflected and stored XSS in a local vulnerable application and explain the difference in impact.
2. Identify the injection context of a reflection from the surrounding markup.
3. Select and apply the correct encoding for HTML body, attribute, JavaScript string, and DOM sink contexts.
4. Add a nonce-based CSP and show which payloads it blocks and which it does not.
5. Write regression tests that fail if a payload is ever reflected unencoded.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| DVWA | current `master` | `http://192.0.2.30:4280`, level **Low** |
| Firefox or Chromium | current | Devtools console |
| Python 3 + Flask | 3.10+, Flask 3.x | `pip install flask markupsafe pytest` |
| Burp Suite Community | 2026.10.1 | Optional |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `http://192.0.2.30:4280` (DVWA), `http://192.0.2.30:3000` (Juice Shop), and the
    Flask application you run on `http://127.0.0.1:5000` of `lab-analyst`.
    **Targets you must not use:** any public site, any real user's browser, and any page you do not control.

    **Cookie theft is out of scope.** Do not build a payload that sends cookies or tokens anywhere, even to
    yourself. The lab's purpose is to prove execution; a working exfiltration payload adds nothing to the
    learning and creates a habit that is indefensible in a report.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary can get a string of their choosing into a page another user views. Reflected XSS requires the
victim to follow a crafted link; stored XSS requires only that they open the affected page. In both cases the
script runs with the origin's privileges: it can read the DOM, make authenticated requests, and (if the session
cookie lacks `HttpOnly`) read `document.cookie`.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Browser, Flask context lab | 127.0.0.1:5000 |
| `lab-web` | DVWA, Juice Shop | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                        lab-web 192.0.2.30
  127.0.0.1:5000 four-context app      :4280 DVWA (xss_r, xss_s)
```

## Before you start

1. Snapshot `pre-lab-302-02`.
2. Log in to DVWA; confirm **DVWA Security → Low**.
3. Create `~/lab/level-3/lab-302-02/{evidence,contextlab/tests}`.

**A note on `alert()`:** many browsers and extensions suppress or de-emphasise `alert` dialogs, and a blocked
dialog looks identical to a failed injection. Use `document.title` as the observable instead — it is visible in
the tab, survives dialogs being blocked, and is trivially recorded in a screenshot.

## Procedure

### 1. Reflected XSS in DVWA

The module reflects a `name` parameter into the page body.

```text
http://192.0.2.30:4280/vulnerabilities/xss_r/?name=<script>document.title='XSS-302-reflected'</script>
```

Open it in the browser, then check the tab title and the page source. The payload appears **unescaped** in the
HTML, and the script executes.

**Expected:** the tab title becomes `XSS-302-reflected`. In devtools → Elements, the injected `<script>` is a
real node, not text.

Now the same request without a browser, which is how you will document it:

```bash
curl -sS -G 'http://192.0.2.30:4280/vulnerabilities/xss_r/' \
  --data-urlencode "name=<script>document.title='XSS-302-reflected'</script>" \
  -b evidence/dvwa.jar -o evidence/reflected.html
grep -o 'document.title[^<]*' evidence/reflected.html | head -3
```

**Why this proves the finding:** the string is present verbatim in the server's response. Whether it executes is
the browser's decision, and the browser's decision is "yes" because it is outside any text node.

### 2. Stored XSS in DVWA

The guestbook module saves a name and a message, then renders them to every visitor.

1. Open `/vulnerabilities/xss_s/`.
2. Submit name `XSS-302` and message
   `<script>document.title='XSS-302-stored'</script>`.
3. Reload the page.
4. Log out, log back in, reload again.

**Expected:** the payload executes on every load, for every session — and it still fires after you log out and
back in, because it lives in the database.

**Why stored XSS is rated higher than reflected:** the attacker does not need to deliver a link. One submission
reaches every user who opens the page, including an administrator reviewing guestbook entries — which is how
stored XSS becomes privilege escalation. Record that chain in your notes; it is the impact statement.

### 3. Build the four-context lab

Each endpoint reflects input in exactly one context, with no encoding.

```bash
cd ~/lab/level-3/lab-302-02/contextlab
cat > app.py <<'PY'
"""Deliberately vulnerable: one endpoint per injection context. Lab use only."""
from flask import Flask, request, Response

app = Flask(__name__)

@app.get("/body")
def body():
    q = request.args.get("q", "")
    return f"<p>You searched for: {q}</p>"

@app.get("/attr")
def attr():
    q = request.args.get("q", "")
    return f'<input type="text" value="{q}"><p>Attribute context</p>'

@app.get("/script")
def script():
    q = request.args.get("q", "")
    return f"<script>const q = '{q}'; document.title = 'q=' + q;</script>"

@app.get("/dom")
def dom():
    return """<!doctype html><div id="out"></div><script>
const frag = decodeURIComponent(location.hash.slice(1));
document.getElementById('out').innerHTML = frag;
</script>"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
PY

python3 -m venv .venv && . .venv/bin/activate
pip install flask markupsafe pytest
python app.py
```

Note `host="127.0.0.1"`: the context lab is loopback-only. It is a deliberately vulnerable application; it has no
business listening on any other interface.

### 4. Exploit each context

Open each URL in the browser and record the tab title after load.

| Context | URL | Payload | Observable |
| --- | --- | --- | --- |
| HTML body | `/body?q=` | `<img src=x onerror="document.title='XSS-body'">` | Title changes |
| Attribute | `/attr?q=` | `"><img src=x onerror="document.title='XSS-attr'">` | Title changes |
| JS string | `/script?q=` | `'; document.title='XSS-script'; //` | Title changes |
| DOM sink | `/dom#` | `<img src=x onerror="document.title='XSS-dom'">` | Title changes |

**Expected:** all four execute. Note what each payload needed:

- **Body** — any element with an event handler works; `<script>` also works here.
- **Attribute** — the payload must first *close* the attribute (`"`), then open a new element. A `<script>` tag
  alone would do nothing, because it is inside an attribute value.
- **JS string** — the payload must close the quote and neutralise the rest of the statement (`//` comments out
  the trailing `;`). HTML tags are inert here; `<script>` would be a syntax error.
- **DOM** — the server never sees the payload. View the page source: it contains only the vulnerable script.
  This is why server-side filters cannot help.

**Verification for the DOM case:** send the request to the server with the payload in the fragment and confirm
in your proxy or `tcpdump` that the fragment is not transmitted. The browser strips it, and the payload is applied
client-side.

### 5. Fix each context properly

Rewrite `app.py` with context-specific encoding:

```bash
cat > app_fixed.py <<'PY'
"""Fixed: each context receives data encoded for that context."""
import json
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

def js_string(value: str) -> str:
    """JSON-encode for a script block and neutralise the </script> terminator."""
    return json.dumps(value).replace("<", "\\u003c").replace(">", "\\u003e")

@app.get("/body")
def body():
    q = request.args.get("q", "")
    return f"<p>You searched for: {escape(q)}</p>"

@app.get("/attr")
def attr():
    q = request.args.get("q", "")
    # Quoted attribute + entity encoding: quotes cannot break out.
    return f'<input type="text" value="{escape(q)}"><p>Attribute context</p>'

@app.get("/script")
def script():
    q = request.args.get("q", "")
    return f"<script>const q = {js_string(q)}; document.title = 'q=' + q;</script>"

@app.get("/dom")
def dom():
    # No HTML insertion at all: the value is treated as text.
    return """<!doctype html><div id="out"></div><script>
const frag = decodeURIComponent(location.hash.slice(1));
document.getElementById('out').textContent = frag;
</script>"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
PY
```

Restart the server with `python app_fixed.py` and repeat step 4 exactly.

**Expected:** no payload changes the title. The body and attribute pages display the payload as visible text.

**Why each fix is the fix:**

| Context | Control | Why it works |
| --- | --- | --- |
| HTML body | `escape()` → `&lt;img …&gt;` | The browser parses the entities as text characters, not as markup |
| Attribute | `escape()` inside a **quoted** attribute | Quotes become `&quot;`, so the value cannot terminate the attribute |
| JS string | JSON encoding, `<`/`>` escaped | The value is a string literal; no quote or `</script>` can escape it |
| DOM | `textContent` instead of `innerHTML` | The value is never parsed as HTML |

**What would not work:** stripping `<` on input. It breaks legitimate text, and the database then holds a
mangled value that any JSON consumer renders literally as `&lt;`. It also does nothing for the DOM case.

### 6. Add a CSP that actually blocks something

Serve a nonce-based policy from the fixed application. Add this to `app_fixed.py`:

```python
import secrets
from flask import g

@app.before_request
def make_nonce():
    g.nonce = secrets.token_urlsafe(16)

@app.after_request
def add_csp(resp):
    resp.headers["Content-Security-Policy"] = (
        f"default-src 'self'; script-src 'nonce-{g.nonce}' 'strict-dynamic'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    return resp
```

The app's own `<script>` blocks need the nonce to keep running. Add
`<script nonce="{{ nonce }}">` where a template is used, or interpolate `g.nonce` into the inline script tag in
the `/dom` and `/script` responses.

Then repeat step 4 against the *vulnerable* application with the same policy applied, and watch the console.

**Expected:** the injected payload is refused, and the console reports a CSP violation naming the blocked inline
script. The page's own nonce-carrying script still runs.

**What CSP did not fix:** the injection still happened. The payload is still in the HTML; the browser declined to
execute it. If `script-src` allowed `'unsafe-inline'`, or if the payload could reach an already-allowed script via
a gadget, it would run. Report CSP as defence in depth, never as the remediation.

### 7. Write the regression tests

```bash
cat > tests/test_encoding.py <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from app_fixed import app

PAYLOADS = [
    "<img src=x onerror=document.title=1>",
    '"><script>document.title=1</script>',
    "'; document.title=1; //",
]

@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

@pytest.mark.parametrize("payload", PAYLOADS)
def test_body_never_reflects_raw_markup(client, payload):
    body = client.get("/body", query_string={"q": payload}).get_data(as_text=True)
    assert "<img" not in body
    assert "onerror=document.title=1>" not in body

@pytest.mark.parametrize("payload", PAYLOADS)
def test_attribute_cannot_be_broken_out_of(client, payload):
    body = client.get("/attr", query_string={"q": payload}).get_data(as_text=True)
    assert 'value="' in body
    assert '"' not in body.split('value="', 1)[1].split('"', 1)[0]

def test_script_context_uses_json_encoding(client):
    body = client.get("/script", query_string={"q": "'; alert(1); //"}).get_data(as_text=True)
    assert "alert(1); //" not in body.split("const q = ", 1)[1].split(";", 1)[0] or "\\u" in body
    assert "</script>" in body
PY

python -m pytest -q
```

**Expected:** all tests pass against `app_fixed.py`. Then temporarily point the imports at the vulnerable `app.py`
and confirm they **fail** — a test that passes against vulnerable code is not a test.

## Evidence to collect

- `evidence/reflected.html` and a screenshot showing the changed tab title.
- `evidence/stored.html` — the guestbook page after reload, payload visible in the source.
- `evidence/context-results.md` — the four-row table with actual outcomes.
- `evidence/fixed-results.md` — the same four payloads after the fix, with outcomes.
- `evidence/csp-violation.txt` — the console message, copied as text.
- `contextlab/` — vulnerable and fixed applications plus `tests/`.
- `evidence/pytest.txt` — passing run, and the failing run against the vulnerable version.

## Verification

- [ ] Reflected payload executes and is present unescaped in the server response.
- [ ] Stored payload persists across logout and reload.
- [ ] All four contexts exploited, with the context-specific reason noted for each.
- [ ] All four payloads blocked after the fix, verified by re-running the same URLs.
- [ ] CSP header present, nonce changes per request, and a violation is observed in the console.
- [ ] Regression tests pass on the fixed app and fail on the vulnerable app.

## Teardown and reset

```bash
# Stop Flask (Ctrl+C), then remove the lab app and its environment
deactivate 2>/dev/null
```

Delete any DVWA guestbook entries you created (the module has a clear option, or reset the database from
`/setup.php`). Revert `pre-lab-302-02` to restore DVWA exactly. Keep `contextlab/` and `evidence/` — they are
the deliverable, and `contextlab` is reused in CYB-307.

## Reflection

1. The DOM payload never reached the server. What does that imply about the value of a server-side XSS filter,
   and what does it imply about where to put the fix?
2. Stored XSS in a guestbook is often rated higher than reflected XSS in a search page. Give the two-part
   argument, in terms of who must act and who is affected.
3. Your CSP blocks inline script. Name one payload class it still would not stop, and the second control that
   would.
4. The regression tests assert on the response body. What kind of regression would they miss, and what would you
   add?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Context analysis | One payload applied everywhere | Correct payload per context | Correct payload per context, with the parsing reason stated |
| Fix correctness | Input filtering proposed | Correct encoding per context | Correct encoding, plus CSP with an observed violation |
| Verification | Payload "looked blocked" | All four re-tested | Re-tested plus tests that fail on vulnerable code |
| Impact reasoning | "XSS is High" | Reflected vs stored distinguished | Chain to privilege escalation described, with the precondition |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Payload appears as text in the page | It was encoded — wrong context or app already fixed | Confirm you are hitting the vulnerable app and the right endpoint |
| `alert()` does nothing | Dialog blocked by browser or extension | Use `document.title` as the observable |
| DOM payload does nothing | `#` fragment not included, or cached page | Hard-reload; confirm the hash is in the address bar |
| Attribute payload needs a click | Used `onmouseover` | Use `onerror` on a broken image, or click the element |
| CSP blocks the app's own script | Nonce missing from the inline tag | Add `nonce="…"` to every legitimate inline script |
| `python app.py` port already in use | Previous run still alive | `ss -tlnp \| grep 5000`, then stop that PID |

## References

1. OWASP WSTG v4.2 — WSTG-INPV-01 (Reflected XSS), WSTG-INPV-02 (Stored XSS), WSTG-CLNT-01 (DOM XSS).
2. OWASP Cross Site Scripting Prevention Cheat Sheet. Accessed 2026-10-29.
3. OWASP Content Security Policy Cheat Sheet. Accessed 2026-10-29.
4. MDN — `textContent`, `innerHTML`, and CSP `script-src`. Accessed 2026-10-29.
5. OWASP Top 10:2025 — A05 Injection. <https://owasp.org/Top10/2025/>

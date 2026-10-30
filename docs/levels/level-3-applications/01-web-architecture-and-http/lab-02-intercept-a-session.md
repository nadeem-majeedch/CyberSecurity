---
title: "LAB-301-02 · Intercept and Annotate a Session"
description: "Capture a full browse, login and cart flow with devtools, a proxy and curl, then annotate every trust decision."
module_code: CYB-301
level: 3
kind: lab
prerequisites: [CYB-301]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-301-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [burp, devtools, curl, http, repeater]
---

# LAB-301-02 · Intercept and Annotate a Session

## Scenario and background

You are the tester on a small engagement against a training application. Before you look for vulnerabilities,
you produce the thing every report needs and almost no junior tester writes: **a map of the traffic**. Which
requests carry identity, where they go, what the server accepts, and which decisions are made in the browser.

The deliverable is an annotated exchange table plus a short narrative a non-technical reader could follow. This
is the foundation for CYB-302 through CYB-308: every finding you later write will cite a row from this table.

## Learning objectives

By the end of this lab you can:

1. Capture a multi-step session with devtools, a proxy, and `curl`, and explain when each view is appropriate.
2. Intercept and modify a request in flight, then replay it unchanged in Repeater.
3. Reproduce a browser request as a `curl` command that returns the same result without any GUI.
4. Distinguish a client-side restriction from a server-side control using evidence you collected.
5. Write an annotated exchange table that names the trust decision in each request.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Firefox ESR or Chromium | current | **Dedicated profile** for proxying |
| Burp Suite Community | 2026.10.1 | Or OWASP ZAP 2.17.0 |
| `curl` | 7.81+ | Replay and evidence |
| `jq` | 1.6+ | Read JSON responses |
| Juice Shop | 20.3.0 | `http://192.0.2.30:3000` |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `http://192.0.2.30:3000` (Juice Shop) and `http://192.0.2.30:4280` (DVWA) in your
    host-only lab; `127.0.0.1:8080` (your proxy).
    **Targets you must not use:** any public website. Do not enable the proxy in your everyday browser profile —
    every request, including personal ones, would be logged by your tool.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

No exploitation in this lab. You are recording behaviour to establish a baseline. The risk being managed is
**operational**: a proxy left on, or installed in the wrong browser profile, leaks credentials and session
tokens into a tool's history file.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Browser, proxy, curl | 192.0.2.10 |
| `lab-web` | Juice Shop, DVWA | 192.0.2.30 |

Software: from [LAB-301-01](lab-01-web-lab-setup.md). Snapshot `pre-cyb301` exists; take `pre-lab-301-02` now.

**Network view**

```text
lab-analyst 192.0.2.10                      lab-web 192.0.2.30
  browser ──▶ 127.0.0.1:8080 (proxy) ──▶ http://192.0.2.30:3000
  curl ─────────────────────────────▶ (same target, no proxy)
```

## Before you start

1. Confirm both applications answer: `curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.30:3000/`.
2. Create a lab account in Juice Shop at `/register` using an address you will remember, e.g.
   `learner301@lab.test`, with a password used **only** here.
3. Create `~/lab/level-3/lab-301-02/evidence/` and a file `exchanges.md` for the table you will build.

## Procedure

### 1. Capture the flow in devtools

In your dedicated profile, open devtools (`F12`), go to **Network**, tick **Preserve log** and **Disable cache**,
then perform this flow slowly:

1. Load `/` (home page).
2. Search for a product.
3. Open one product's detail.
4. Log in at `/#/login`.
5. Add the product to the basket.
6. Open the basket.
7. Reload the page (this is where the session is re-proved).

**Why Preserve log:** a login redirects, and a redirect clears the network list by default — the login POST you
most want would vanish.

Right-click any request → **Copy → Copy as cURL**. That is your bridge from GUI to evidence.

### 2. Capture the same flow through the proxy

1. In Burp: **Proxy → Intercept** is **off** for now. Confirm the listener is `127.0.0.1:8080`.
2. In the browser profile, set the HTTP proxy to `127.0.0.1:8080` (both HTTP and HTTPS).
3. Repeat the seven-step flow.
4. Open **Target → Site map**, expand `http://192.0.2.30:3000`, and confirm the endpoints you used appear.

**Expected:** a tree containing `/rest/user/login`, `/rest/products/search`, `/rest/basket/...`, and the static
bundle. What matters is that you can *find* the API calls made by a JavaScript application whose visible URLs
never change.

### 3. Intercept and modify one request

Turn **Intercept on**. In the browser, reload the basket page. When the request is held, read it before changing
anything: method, path, `Cookie`, and any custom headers. Then:

1. Change one query parameter value to something the UI would not produce (for example, a larger quantity, or a
   different basket identifier — you will exploit this properly in CYB-303).
2. Forward the request.
3. Record the status code and whether the server honoured the change.

**Why this matters:** the browser's UI is not the application. Any value it sends can be changed before it
arrives; the only question is whether the server notices.

### 4. Replay in Repeater

Right-click the login request → **Send to Repeater**. Send it unchanged and confirm the response matches what
the browser received. Then change exactly one thing per attempt and record the difference:

| Attempt | Change | Observed status | Interpretation |
| --- | --- | --- | --- |
| 1 | none | 200 | Baseline |
| 2 | remove `Content-Type` | ? | Does the parser still accept it? |
| 3 | wrong password | 401 | Failure path |
| 4 | add an unknown JSON field | ? | Ignored, or rejected? |

Attempt 4 is not idle curiosity: "the server ignores unknown fields" is the precondition for mass assignment
(CYB-308), and "it rejects them" is a control you should credit.

### 5. Reproduce without the GUI

Take the `curl` command from step 1 and make it explicit and readable. Never ship `curl -k` in a report — it
disables certificate validation and hides a real class of finding.

```bash
BASE='http://192.0.2.30:3000'
curl -sS -i -c evidence/jar.txt -X POST "$BASE/rest/user/login" \
  -H 'Content-Type: application/json' \
  --data '{"email":"learner301@lab.test","password":"Lab-Passw0rd-301"}' \
  | tee evidence/login-response.txt
```

```bash
# Authenticated request using the stored cookie jar
curl -sS -i -b evidence/jar.txt "$BASE/rest/basket/1" | tee evidence/basket-response.txt
```

Option by option, because you will be asked:

| Option | Effect | Why it is here |
| --- | --- | --- |
| `-sS` | Silent, but show errors | Keeps output clean without hiding failures |
| `-i` | Include response headers | The headers *are* the evidence |
| `-c FILE` | Write cookies received | Persists the session for later commands |
| `-b FILE` | Send cookies from file | Re-proves identity without a browser |
| `-X POST` | Method override | Explicit; note that `--data` already implies POST |
| `-H` | Add a header | Required for JSON APIs |
| `--data` | Request body | The input you will vary |
| `--max-time 10` | Bound the request | A hanging request means a filtered port, not a slow server |
| `-L` | Follow redirects | Useful for login flows; dangerous when it silently changes method |

**Deliberately absent:** `-k`. If TLS fails, that is a finding about the certificate, not an inconvenience.

### 6. Test client-side versus server-side validation

Juice Shop's registration form validates the password in the browser. Determine whether the *server* does.

1. In devtools, submit a registration with a password the UI accepts.
2. Then submit the same registration with a deliberately weak password using `curl` directly, bypassing the UI.
3. Compare: `201 Created` means the server accepted input the UI forbade — client-side validation only.
   `400`/`422` means the server enforces a policy.

Record both requests and both responses. This is the cleanest demonstration of a principle you will use for the
rest of the course: **validation in the browser is a usability feature; validation on the server is a control.**

### 7. Build the annotated table

For each of at least eight exchanges, complete a row:

| # | Method + path | Identity carried | Decision made | Side effect | Where validated |
| --- | --- | --- | --- | --- | --- |
| 1 | `GET /` | none | public read | none | server |
| 2 | `GET /rest/products/search?q=…` | none | public read | none | server |
| 3 | `POST /rest/user/login` | credentials | issues session token | session created | server |
| 4 | `GET /rest/basket/1` | `token` cookie | object read by ID | none | **unknown — test in CYB-303** |
| … | … | … | … | … | … |

The "where validated" column is where the analysis lives. Write `unknown` honestly and note what test would
resolve it; that note is the start of your Level 3 finding list.

### 8. Write the narrative

One page, no jargon beyond what you define. Answer: what does this application consider proof of identity, how
long does that proof last, what can an unauthenticated visitor do, and what changes after login.

## Evidence to collect

- `evidence/exchanges.md` — the annotated table, eight rows minimum.
- `evidence/login-response.txt`, `evidence/basket-response.txt` — raw `curl` output with headers.
- `evidence/repeater-attempts.md` — the four-attempt table with status codes.
- `evidence/narrative.md` — the one-page explanation.
- Screenshot of the Burp sitemap with the API tree expanded.

## Verification

- [ ] Sitemap contains at least three `/rest/` endpoints you actually triggered.
- [ ] One intercepted request was modified in flight and the outcome recorded.
- [ ] Repeater baseline matches the browser's response byte-for-byte in status and body shape.
- [ ] `curl` login returns `200` and a `Set-Cookie` header; the basket request with `-b` returns `200`.
- [ ] Client-side versus server-side validation test has both requests and both responses.
- [ ] Table has at least eight rows and every "where validated" cell is filled or marked `unknown` with a test.

## Teardown and reset

```bash
# Remove captured credentials and tokens from the workspace
shred -u evidence/jar.txt 2>/dev/null || rm -f evidence/jar.txt
```

In Burp, **Proxy → Intercept → off**, then disable the proxy in your dedicated browser profile. Delete the
Juice Shop account you created if you wish (`/#/privacy-security` → delete). Revert to `pre-lab-301-02` if you
altered application state beyond your own account.

## Reflection

1. You captured the same flow three ways. Name one question only the proxy could answer and one only `curl`
   could answer.
2. Removing `Content-Type` from a JSON request often still succeeds. What does that tell you about how the server
   parses input, and why does it matter for a security review?
3. The basket request carries an object identifier and a token. Which of the two should decide what you may
   read, and what will you test first in CYB-303?
4. Why is `-k` never acceptable in evidence, even on a lab target?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Coverage | Fewer than five exchanges | Eight exchanges across the flow | Full flow plus an authenticated and an unauthenticated variant of the same endpoint |
| Interpretation | Rows list URLs only | Decisions named | Unknowns identified with the specific test that would resolve them |
| Reproduction | GUI only | `curl` reproduces login | `curl` reproduces login *and* an authenticated object read, with headers retained |
| Client/server distinction | Not tested | Tested and recorded | Tested, explained, and generalised into a review question for the report |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Browser cannot load anything through the proxy | Proxy listener not running, or wrong port | Check Burp **Proxy → Proxy settings**; confirm `ss -tlnp \| grep 8080` |
| HTTPS pages fail with certificate errors | CA not installed in this profile | Visit `http://burp`, import the certificate into the profile's authorities |
| Sitemap empty after browsing | Scope excludes the host | Add `192.0.2.30` to target scope |
| `curl` login returns `401` | Account not created, or password mismatch | Register again; confirm with the browser first |
| `curl` basket returns `401` even with `-b` | Cookie jar from a different host or expired | Re-login writing `-c`, then reuse the same file with `-b` |
| Response body truncated in terminal | Long JSON | Pipe to `jq .` or `tee` to a file |

## References

1. PortSwigger — Burp Proxy and Repeater documentation. Accessed 2026-10-29.
2. MDN — Network Monitor: Preserve log. Accessed 2026-10-29.
3. `curl` manual — `--cookie`, `--cookie-jar`, `--max-time`. Accessed 2026-10-29.
4. OWASP WSTG v4.2 — WSTG-INFO-04 (Enumerate Applications on Webserver), WSTG-CONF-06 (HTTP Methods).

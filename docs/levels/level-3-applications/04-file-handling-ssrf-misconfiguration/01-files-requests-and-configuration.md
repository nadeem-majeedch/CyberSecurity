---
title: "Files, Requests and Configuration"
description: "Upload validation, path canonicalisation, SSRF defences, and the misconfigurations that scanners find first."
module_code: CYB-304
level: 3
kind: lesson
prerequisites: [CYB-303]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-304-01, LAB-304-02, LAB-304-03, LAB-304-04]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [file-upload, path-traversal, ssrf, misconfiguration, tls, headers]
---

# Files, Requests and Configuration

**Level 3** · 240 minutes · **Prerequisites:** CYB-303 · **Labs:**
[Upload](lab-01-file-upload.md) · [Traversal](lab-02-path-traversal.md) ·
[SSRF](lab-03-ssrf.md) · [Headers and TLS](lab-04-headers-and-tls.md)

## Why this matters

Three input types deserve their own module because each grants a capability rather than a value. A **filename**
can address any file the process can read. An **uploaded file** can become code that the server executes. A
**URL** lets the server make a request on the attacker's behalf — from a network position the attacker does not
occupy.

Then there is configuration. Most first assessments find more in the deployment than in the code: a directory
listing, a `.git` directory, a debug console, TLS 1.0, a stack trace with a database password. These are cheap to
find, cheap to fix, and embarrassing to miss.

## Learning outcomes

By the end of this lesson you will be able to:

- Explain each layer of upload defence and which attack each layer stops.
- Trace a path traversal through URL decoding to the filesystem call, and fix it with canonicalisation.
- Distinguish SSRF classes and describe why an allowlist must be applied after DNS resolution.
- Recognise the misconfigurations that account for most scanner findings, with a concrete risk for each.
- Verify a TLS configuration and a header set with commands rather than assumptions.

## Prerequisites and setup

- Web lab running; DVWA at **Low**.
- Python 3.10+ with Flask and `requests`; `openssl`, `file`, `xxd`.
- `nginx` installed on `lab-web` or in a container for the last lab.

---

## Core concepts

### 1. Uploads: the file is the payload

An upload endpoint accepts bytes and a name from an unauthenticated or low-privilege user. Everything about that
file is attacker-controlled: its name, its declared type, its actual bytes, its size, and its internal structure.
The threats follow directly:

| Threat | Mechanism | Consequence |
| --- | --- | --- |
| Web shell | `.php`/`.jsp`/`.aspx` file stored under the web root and requested | Remote code execution as the web user |
| Content-type spoofing | `Content-Type: image/png` on a PHP file | Bypasses a check that trusts the header |
| Double extension / trailing tricks | `shell.php.jpg`, `shell.php%00.jpg`, `shell.pHp` | Bypasses a naive extension check |
| Path traversal in the filename | `../../../../var/www/html/x.php` | Writes outside the intended directory |
| Stored XSS via SVG or HTML | `image/svg+xml` containing script | Script execution in the application's origin |
| Polyglot | Valid image that is also valid script | Defeats magic-byte-only checks |
| Zip bomb / decompression bomb | Small archive, enormous expansion | Denial of service |
| Malware hosting | Application serves attacker files | Reputation and legal exposure |

**The five layers, in the order they should be applied.** No single layer is sufficient; the point is that each
one fails independently.

1. **Authenticate and authorize the upload.** Who may upload, and to where? An anonymous upload endpoint is a
   different risk class from an avatar upload for logged-in users.
2. **Validate the type from content, not metadata.** Check the file's magic bytes and, where possible, decode it
   with a real parser (`Pillow` for images). The `Content-Type` header is a claim by the client.
3. **Generate the stored name yourself.** A UUID plus a known extension. Never use the client's filename for
   storage; keep it only as a display label, escaped on output.
4. **Store outside the web root, with no execute permission.** Files are served by an application route that sets
   `Content-Disposition: attachment`, not by the web server executing them.
5. **Bound the size, and strip metadata.** Enforce a maximum in the server, not only in the client, and re-encode
   images to discard embedded payloads.

```python
# A defensible upload handler: allowlist, magic bytes, generated name, no execution
import io, uuid, pathlib
from flask import Flask, request, abort, send_from_directory
from PIL import Image

app = Flask(__name__)
STORE = pathlib.Path("/srv/app/uploads").resolve()      # outside the web root
STORE.mkdir(parents=True, exist_ok=True)
ALLOWED = {"image/png": "png", "image/jpeg": "jpg"}
MAX_BYTES = 2 * 1024 * 1024

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

    # Decode and re-encode: proves the file is an image and drops embedded metadata.
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        abort(415)

    name = f"{uuid.uuid4().hex}.{ALLOWED[claimed]}"
    img.save(STORE / name, format="PNG" if claimed == "image/png" else "JPEG")

    return {"stored_as": name}, 201

@app.get("/files/<name>")
def serve(name):
    # send_from_directory refuses traversal; attachment prevents inline rendering.
    return send_from_directory(STORE, name, as_attachment=True)
```

**What `secure_filename` does and does not do.** Werkzeug's helper strips path separators and dangerous
characters. It is useful for producing a *display* name. It is not a type check, and it does not stop a file with
an executable extension being stored in an executable location. Use it, and do not rely on it.

### 2. Path traversal: follow the string through every layer

A traversal flaw is any code that builds a filesystem path from user input without proving the result stays
inside the intended directory. The subtlety is that the input is decoded **more than once** on the way in:

```text
Client sends:        ..%2f..%2fetc%2fpasswd
URL-decoded once:    ../../etc/passwd
Framework normalises: maybe, maybe not
Filesystem call:     open(base + user_input)   ← traversal happens here
```

Variants you will meet: `..%252f` (double-encoded), `....//` (filter removes `../` once, leaving `../`), UTF-8
overlong encodings (mostly historical), backslashes on Windows, and absolute paths (`/etc/passwd`) which ignore
the base entirely if concatenated carelessly.

**The fix is canonicalisation plus a containment check**, not a filter:

```python
import pathlib
from flask import abort

BASE = pathlib.Path("/srv/app/files").resolve()

def read_report(user_path: str) -> bytes:
    # Resolve symlinks and '..' first, then compare against the base.
    target = (BASE / user_path).resolve()
    if not target.is_relative_to(BASE):        # Python 3.9+
        abort(404)
    if not target.is_file():
        abort(404)
    return target.read_bytes()
```

**Why this works when filtering does not:** the check happens on the *resolved* path — the one the operating
system will actually open. Symlinks, `..`, encoded separators, and absolute paths all collapse to a concrete path,
and that path is either inside `BASE` or it is not. A blacklist of `"../"` strings is defeated by any encoding the
server decodes later; a containment check is not.

Two related flaws worth naming separately:

- **Local File Inclusion (LFI)** — the input selects a *template* or *include* rather than a data file. In PHP this
  is `include($_GET['page'])`, which traverses and can execute. The fix is an allowlist mapping keys to fixed
  paths, never a path from the client.
- **Remote File Inclusion (RFI)** — the include accepts a URL. This is code execution from an attacker-controlled
  server. Disable remote includes; if the feature is genuinely needed, that is a redesign.

### 3. SSRF: the server as proxy

SSRF occurs when the application fetches a URL supplied by the user. The server sits inside a network position the
attacker does not: it can reach `127.0.0.1`, internal services, and — in cloud environments — a metadata endpoint
that issues credentials.

| Class | Behaviour | Detection difficulty |
| --- | --- | --- |
| Basic (in-band) | The response body is returned to the attacker | Easy: read the response |
| Semi-blind | Errors or timing differ, body is not returned | Medium: infer from error text |
| Blind | No output, no error difference | Hard: requires an out-of-band listener you control |

Common sources: image importers ("fetch this URL"), PDF and screenshot generators, webhook testers, URL previews,
RSS/feed readers, SSO metadata fetchers, and document converters.

**Why `169.254.169.254` appears in every SSRF write-up:** it is the link-local address used by cloud instance
metadata services. Reaching it can yield temporary credentials. **This course never tests it.** The lab's internal
service is one you start on `127.0.0.1`, holding fake data — the same lesson without touching a real control plane.

**Defences, in order of reliability:**

1. **Do not fetch arbitrary URLs.** If the feature only needs one host, hard-code it. Most "SSRF fixes" are really
   this.
2. **Allowlist hostnames exactly**, then resolve them yourself. An allowlist checked against the *string* is
   bypassed by `allowed.test@evil.test`, `evil.test#allowed.test`, decimal IP encodings (`2130706433`), and DNS
   names that resolve to loopback.
3. **Reject the resolved address if it is private, loopback, link-local, or reserved** — unless it is explicitly
   the allowlisted internal service.
4. **Disable redirects** and re-validate each hop if you must follow them.
5. **Restrict schemes** to `https` (and `http` only if required); block `file:`, `gopher:`, `dict:`, `ftp:`.
6. **Pin the connection** to the IP you validated, or route outbound requests through a proxy with an egress
   policy. This closes the DNS-rebinding window between check and connect.

```python
import ipaddress, socket
from urllib.parse import urlparse
import requests

ALLOWED_HOSTS = {"status.lab.internal"}
ALLOWED_PORTS = {443}

def safe_fetch(url: str) -> requests.Response:
    p = urlparse(url)
    if p.scheme != "https" or p.port not in ALLOWED_PORTS:
        raise ValueError("scheme or port not permitted")
    if p.hostname not in ALLOWED_HOSTS:
        raise ValueError("host not permitted")

    infos = socket.getaddrinfo(p.hostname, p.port, proto=socket.IPPROTO_TCP)
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValueError("resolved address not permitted")

    # Redirects off: each hop would need re-validation.
    return requests.get(url, timeout=5, allow_redirects=False, stream=True)
```

**What this still misses:** between `getaddrinfo` and the connection, DNS can change (rebinding). Closing that
requires connecting to the validated IP directly with the `Host` header set, or an egress proxy. Say so in a
report rather than claiming the allowlist is complete.

### 4. Deserialisation and integrity

If an application accepts a serialised object from a client and reconstructs it, the client can often choose the
class that gets instantiated. Python `pickle`, Java `ObjectInputStream`, PHP `unserialize`, and YAML's unsafe
loader are the usual suspects; the outcome ranges from data tampering to remote code execution.

The rules are short: never deserialise untrusted input with a format that can express objects; prefer JSON with an
explicit schema; if you must use YAML, use `safe_load`; and verify signatures on any artefact you do accept
(updates, plugins, tokens) — that is [A08:2025 Software or Data Integrity Failures](https://owasp.org/Top10/2025/).

### 5. Misconfiguration: the catalogue

| Misconfiguration | How to spot it | Risk |
| --- | --- | --- |
| Default credentials | Vendor docs; `admin`/`admin` | Full administrative access |
| Debug mode in production | Werkzeug console, Django debug page | Interactive console → RCE |
| Verbose errors | Stack traces, SQL in responses | Schema and path disclosure; aids every other attack |
| Directory listing | `Index of /` | Source, backups, and secrets |
| Exposed VCS or backups | `/.git/`, `/.env`, `/backup.zip` | Credentials, full source |
| Unnecessary methods | `OPTIONS`, then `TRACE`/`PUT` | Cross-site tracing, file write |
| Admin interface reachable | `/admin`, `/manager/html` | Brute force, default creds |
| Missing security headers | `curl -I` | XSS impact, clickjacking, MIME sniffing |
| Weak TLS | Protocol version, cipher list | Interception, compliance failure |
| Over-permissive CORS | Reflected `Origin` | Cross-origin data theft (CYB-301) |

**Headers worth checking on every response**, with the risk of each absence: `Content-Security-Policy` (XSS impact),
`Strict-Transport-Security` (downgrade), `X-Content-Type-Options: nosniff` (MIME confusion), `Referrer-Policy`
(URL leakage), `frame-ancestors`/`X-Frame-Options` (clickjacking), `Permissions-Policy` (feature abuse), and
`Cache-Control: no-store` on authenticated responses.

**TLS, verified rather than assumed.** `openssl s_client` is enough:

```bash
# Which protocol and cipher did we actually negotiate?
openssl s_client -connect 192.0.2.30:443 -servername lab.test </dev/null 2>/dev/null \
  | grep -E 'Protocol|Cipher'

# Is an obsolete protocol still accepted? (should fail)
openssl s_client -connect 192.0.2.30:443 -tls1_1 </dev/null 2>&1 | head -3

# Certificate subject, issuer, and validity
openssl s_client -connect 192.0.2.30:443 -servername lab.test </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

**Expected:** TLS 1.2 or 1.3 negotiated, TLS 1.0/1.1 refused, and a certificate whose dates and name match the
host. TLS 1.0 and 1.1 were deprecated by RFC 8996 in 2021; a server still offering them is a finding regardless of
cipher strength.

---

## Worked example: one upload, three defences

A support portal lets users attach screenshots. The naive handler:

```python
f = request.files["screenshot"]
f.save(os.path.join("static/uploads", f.filename))     # three flaws in one line
```

| Flaw | Exploit | Defence |
| --- | --- | --- |
| Client-controlled name | `../../app.py` overwrites code | Generated name |
| Client-controlled type | `shell.php` stored under a served path | Content sniffing + extension from allowlist |
| Served from an executable location | Request the uploaded file, get code execution | Store outside web root, serve as attachment |

The corrected handler is the one in section 1. The evidence that it works is not "the code looks right" — it is
that four malicious uploads are rejected and one legitimate image is accepted, each with a status code recorded:

```bash
# Rejected: executable type
curl -sS -o /dev/null -w 'php=%{http_code}\n' -F 'file=@shell.php;type=image/png' \
  http://127.0.0.1:5004/avatar

# Rejected: traversal in the name
curl -sS -o /dev/null -w 'traversal=%{http_code}\n' -F 'file=@ok.png;filename=../../evil.png' \
  http://127.0.0.1:5004/avatar

# Accepted: a real PNG
curl -sS -o /dev/null -w 'png=%{http_code}\n' -F 'file=@ok.png' http://127.0.0.1:5004/avatar
```

**Expected:** `415`, `201` (with the traversal neutralised into a generated name), `201`. The middle case is the
interesting one: the upload *succeeds*, and that is correct — the filename was never trusted, so there was nothing
to exploit.

---

## Defender's view

| Signal | Source | Meaning |
| --- | --- | --- |
| Uploads whose extension contradicts their magic bytes | Upload handler logs | Type-spoofing attempt |
| Filenames containing `..`, `/`, or null bytes | Application log, WAF | Traversal attempt |
| Requests for `/etc/passwd`-style paths | Access logs (404s) | LFI probing |
| Outbound requests to loopback or link-local from the app | Egress firewall, proxy logs | SSRF |
| DNS lookups for unusual names from the app server | DNS logs | SSRF with hostname indirection |
| `OPTIONS`/`TRACE` bursts, or `PUT` to static paths | Web server logs | Method probing |
| Requests for `/.git/`, `/.env`, `*.bak` | Access logs | Source and secret harvesting |
| 5xx with stack traces in the body | Response inspection | Debug mode left on |

Controls that remove categories rather than instances: files stored outside the document root and served by a
handler; a single `safe_join`-style helper used everywhere; outbound egress restricted by policy at the network
layer so an SSRF bug cannot reach metadata services; and a deployment checklist that a second person signs.

---

## Common mistakes

1. **Trusting `Content-Type`.** It is a client claim. Sniff the bytes and decode with a real parser.
2. **Using the client's filename for storage.** Even "sanitised" names can collide, overwrite, or surprise you.
   Generate the name; display the original only as escaped text.
3. **Filtering `../` instead of canonicalising.** Encodings and symlinks defeat string filters. Resolve, then
   compare.
4. **Blocklisting IP ranges for SSRF.** IPv4-mapped IPv6, decimal encodings, and redirects bypass naive checks.
   Allowlist hosts, validate after resolution, and disable redirects.
5. **Reporting TLS 1.0 as Critical on an internal-only service.** Severity depends on exposure and data. Say what
   you measured and let the rating follow.
6. **Calling a missing header a vulnerability.** Tie it to an attack path, or report it as hardening.

---

## Practice

1. [LAB-304-01 · File Upload Validation](lab-01-file-upload.md)
2. [LAB-304-02 · Path Traversal and File Inclusion](lab-02-path-traversal.md)
3. [LAB-304-03 · Server-Side Request Forgery](lab-03-ssrf.md)
4. [LAB-304-04 · Security Headers, TLS and Misconfiguration](lab-04-headers-and-tls.md)

**Stretch task.** Extend the fixed upload handler to accept PDFs safely. Decide what "safely" means for a format
that can contain JavaScript, embedded files, and launch actions, and write down the three controls you would need
before accepting one.

## Knowledge check

1. Name the five layers of upload defence and the attack each one stops.
2. Why does checking a file's `Content-Type` header not constitute validation?
3. A developer filters `"../"` from a path parameter. Give two ways to bypass the filter.
4. Why must an SSRF allowlist be applied to the resolved address rather than the URL string?
5. What is the difference between LFI and RFI, and which is more severe?
6. Which misconfiguration turns a stack trace into remote code execution?
7. You see TLS 1.2 negotiated but TLS 1.1 also accepted. What is the finding, and how do you verify it?
8. Why is `as_attachment=True` used when serving user-uploaded files?

## Summary

- Uploaded files are attacker-controlled code; validate content, generate names, store outside the web root, and
  never execute.
- Traversal is fixed by canonicalising and checking containment, not by filtering strings.
- SSRF gives the server's network position to the attacker; allowlist hosts, validate resolved IPs, disable
  redirects, restrict schemes.
- Deserialising untrusted input is code execution waiting for a gadget chain; prefer schemas and signatures.
- Misconfiguration is the most common finding and the cheapest to fix; verify with requests, not assumptions.

## References

1. OWASP Top 10:2025 — A02 Security Misconfiguration, A01 Broken Access Control. <https://owasp.org/Top10/2025/>
2. OWASP File Upload Cheat Sheet. Accessed 2026-10-29.
3. OWASP Server-Side Request Forgery Prevention Cheat Sheet. Accessed 2026-10-29.
4. OWASP WSTG v4.2 — WSTG-BUSL-09, WSTG-ATHZ-01, WSTG-CONF-06, WSTG-CRYP-01.
5. RFC 8996 — Deprecating TLS 1.0 and TLS 1.1. IETF, 2021.
6. OWASP ASVS 5.0 — V5 File Handling, V12 Secure Communication, V13 Configuration. <https://asvs.owasp.org/>

---
title: "LAB-304-04 · Security Headers, TLS and Misconfiguration"
description: "Audit a live service for missing headers, obsolete TLS and exposed paths, then harden it and prove each change with a request."
module_code: CYB-304
level: 3
kind: lab
prerequisites: [CYB-304]
estimated_minutes: 75
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-304-04]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [security-headers, tls, nginx, misconfiguration, hardening]
---

# LAB-304-04 · Security Headers, TLS and Misconfiguration

## Scenario and background

A service can be correctly written and badly deployed. The code is fine; the web server advertises its version,
serves directory listings, allows `TRACE`, negotiates TLS 1.1, and returns no security headers at all. None of
these is a clever exploit, and together they are what most first assessments actually report.

You will audit two running applications and one nginx instance you configure, then harden the nginx instance and
prove every change with a request. The deliverable is a before/after table — the format a client reads.

## Learning objectives

By the end of this lab you can:

1. Audit response headers and classify each absence by the risk it leaves open.
2. Test supported HTTP methods and exposed paths systematically.
3. Determine the negotiated TLS version and whether obsolete protocols are accepted.
4. Write a hardened nginx configuration covering headers, TLS, version disclosure and directory listing.
5. Verify each control with a command, and distinguish a compensating control from a fix.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| nginx | 1.18+ | On `lab-web` |
| `curl` | 7.81+ | `-I`, `-k`, `-X` |
| `openssl` | 3.0+ | `s_client` |
| Juice Shop / DVWA | 20.3.0 / current | Existing targets |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `192.0.2.30:3000`, `:4280`, and the nginx instance you configure on `:8443` of the
    same host. All are yours.
    **Targets you must not use:** any public site, and any TLS endpoint you do not operate. Scanning TLS
    configuration of third parties is not a victimless exercise and is out of scope for this course.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

No adversary is simulated here. The subject is **exposure**: what a service tells an unauthenticated client about
itself, and what it permits. The relevant risk is an attacker using version disclosure, weak TLS, or an exposed
path to shorten the next step — not a single exploit.

**Impact if exploited.** No single item here is remotely exploitable on its own. Together they shorten every
other attack: version disclosure selects the exploit, obsolete TLS permits interception, directory listing finds
the backup, and missing headers remove the browser's last line of defence.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-analyst` | Audit client | 192.0.2.10 |
| `lab-web` | Juice Shop, DVWA, nginx (new) | 192.0.2.30 |

**Network view**

```text
lab-analyst 192.0.2.10                     lab-web 192.0.2.30
  curl -I ────────────────────────────▶ :3000 Juice Shop
  curl -I ────────────────────────────▶ :4280 DVWA
  curl -k / openssl s_client ─────────▶ :8443 nginx (lab site)
```

## Before you start

1. Snapshot `pre-lab-304-04`.
2. On `lab-web`, attach NAT and install nginx:

   ```bash
   sudo apt update && sudo apt install -y nginx openssl
   nginx -v
   ```

   Detach NAT afterwards.
3. Create `evidence/` on `lab-analyst` and a document `evidence/header-audit.md` for the tables.

## Procedure

### 1. Audit the headers of the two applications

```bash
for target in 'http://192.0.2.30:3000/' 'http://192.0.2.30:4280/login.php'; do
  echo "=== $target"
  curl -sS -D - -o /dev/null "$target" | sed -n '1,25p'
done | tee evidence/headers-before.txt
```

Build the table. For each header, record present/absent and the risk of absence:

| Header | Juice Shop | DVWA | Risk if absent |
| --- | --- | --- | --- |
| `Content-Security-Policy` | ? | ? | Injected script runs with no restriction |
| `Strict-Transport-Security` | ? | ? | Downgrade to HTTP on later visits |
| `X-Content-Type-Options` | ? | ? | MIME sniffing turns an upload into script |
| `Referrer-Policy` | ? | ? | URLs leak to third parties |
| `X-Frame-Options` / `frame-ancestors` | ? | ? | Clickjacking |
| `Permissions-Policy` | ? | ? | Injected script can use device features |
| `Cache-Control` on authenticated pages | ? | ? | Shared-cache disclosure |
| `Server` / `X-Powered-By` | ? | ? | Version disclosure aids targeted exploitation |

**Expected:** most rows empty on both. That is normal for lab builds and is the point — these are defaults, not
decisions.

**Important:** an absent header is a *hardening* finding unless there is an attack path. `X-Frame-Options` on a
JSON API that cannot be framed is noise. Say which of these rows could actually be exploited against a page a user
visits, and which cannot.

### 2. Test methods and exposed paths

```bash
echo "--- methods"
for m in GET OPTIONS TRACE PUT DELETE; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -X "$m" 'http://192.0.2.30:4280/login.php')
  printf '%-8s %s\n' "$m" "$code"
done

echo "--- paths"
for p in /.git/config /.env /server-status /phpinfo.php /backup.zip /ftp /api/Users; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "http://192.0.2.30:3000$p")
  printf '%-16s %s\n' "$p" "$code"
done | tee evidence/paths.txt
```

**Expected:** `TRACE` and `PUT` refused or ignored; a mix of statuses for the paths. A `200` on `/ftp` or
`/.git/config` is a finding; a `404` is the correct answer. Record what you see, and note that `405` on `PUT` is
the server doing its job.

### 3. Build an intentionally weak TLS service

Create a self-signed certificate and a minimal nginx site that accepts obsolete protocols:

```bash
sudo mkdir -p /etc/nginx/lab304 /var/www/lab304
sudo openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout /etc/nginx/lab304/lab.key -out /etc/nginx/lab304/lab.crt \
  -subj '/CN=lab.test/O=CyberSecurity Lab/C=PK'
sudo chmod 600 /etc/nginx/lab304/lab.key

sudo tee /var/www/lab304/index.html >/dev/null <<'HTML'
<!doctype html><meta charset="utf-8"><title>Lab 304</title><h1>lab304</h1>
HTML
sudo mkdir -p /var/www/lab304/private && echo "synthetic" | sudo tee /var/www/lab304/private/a.txt >/dev/null

sudo tee /etc/nginx/sites-available/lab304 >/dev/null <<'CONF'
server {
    listen 8443 ssl;
    server_name lab.test;
    ssl_certificate     /etc/nginx/lab304/lab.crt;
    ssl_certificate_key /etc/nginx/lab304/lab.key;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    autoindex on;
    root /var/www/lab304;
    location / { try_files $uri $uri/ =404; }
}
CONF

sudo ln -sf /etc/nginx/sites-available/lab304 /etc/nginx/sites-enabled/lab304
sudo nginx -t && sudo systemctl reload nginx
```

Note: some distributions disable TLS 1.0/1.1 at the library level. If nginx refuses to start with those protocols,
record that as an environment limitation and continue — the hardening steps are unaffected.

### 4. Audit the weak service

```bash
# Headers and directory listing
curl -sk -D - -o /dev/null https://192.0.2.30:8443/ | head -12
curl -sk https://192.0.2.30:8443/private/ | head -20

# Protocol: what is negotiated, and is an obsolete version accepted?
openssl s_client -connect 192.0.2.30:8443 -servername lab.test </dev/null 2>/dev/null \
  | grep -E 'Protocol|Cipher'
openssl s_client -connect 192.0.2.30:8443 -tls1_1 </dev/null 2>&1 | grep -E 'Protocol|error|alert' | head -3
```

**Expected:** a `Server: nginx/1.x` header, no security headers, a browsable `/private/` listing, and TLS 1.1
accepted. Each is a row in your before table.

**On `-k`:** here it is legitimate, and the reason matters. `-k` disables certificate validation, which is exactly
what you want when the *subject* of the test is the header set of a self-signed lab service. It is never
legitimate when the subject is certificate trust — for that, use `openssl s_client` and read the verification
result. In LAB-301-02 `-k` was forbidden because the finding there concerned the exchange itself; context decides,
and you should be able to say which context you are in.

### 5. Harden the service

```bash
sudo tee /etc/nginx/sites-available/lab304 >/dev/null <<'CONF'
server {
    listen 8443 ssl;
    server_name lab.test;

    ssl_certificate     /etc/nginx/lab304/lab.crt;
    ssl_certificate_key /etc/nginx/lab304/lab.key;

    # Modern protocols only; TLS 1.0/1.1 were deprecated by RFC 8996.
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;

    # Do not advertise the version.
    server_tokens off;

    # Directory listing off by default.
    autoindex off;

    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'" always;
    add_header Permissions-Policy "geolocation=(), camera=(), microphone=()" always;

    root /var/www/lab304;
    location / { try_files $uri $uri/ =404; }

    # Refuse methods this static site does not need.
    if ($request_method !~ ^(GET|HEAD)$) { return 405; }
}
CONF

sudo nginx -t && sudo systemctl reload nginx
```

**Why `always` on `add_header`:** without it, nginx omits the header on error responses — precisely the responses
where a browser might still render content.

**Why `autoindex off`:** `on` turns any directory without an index into a file listing, which is how backup files
and drafts get discovered. Off is the default; the weak config turned it on deliberately.

### 6. Verify every change

```bash
echo "=== headers"
curl -sk -D - -o /dev/null https://192.0.2.30:8443/ | sed -n '1,15p'

echo "=== listing"
curl -sk -o /dev/null -w 'private=%{http_code}\n' https://192.0.2.30:8443/private/

echo "=== protocols"
openssl s_client -connect 192.0.2.30:8443 -servername lab.test </dev/null 2>/dev/null \
  | grep -E 'Protocol|Cipher'
openssl s_client -connect 192.0.2.30:8443 -tls1_1 </dev/null 2>&1 | grep -E 'error|alert|no protocols' | head -2

echo "=== methods"
curl -sk -o /dev/null -w 'PUT=%{http_code}\n' -X PUT https://192.0.2.30:8443/ -d 'x'
```

**Expected:** the six headers present; `private=403`; `Protocol: TLSv1.3` (or 1.2); TLS 1.1 refused; `PUT=405`.

Populate the after table in `evidence/header-audit.md`. Every row needs the command and the observed value — a
hardening claim without a verification command is a claim you cannot defend.

### 7. Separate what you fixed from what you did not

In `evidence/residual.md`, list honestly:

- The certificate is self-signed. On a real service, use a certificate from a trusted CA and monitor expiry.
- TLS 1.2 is still enabled, which is correct; note the cipher suites you would restrict in a stricter profile.
- The CSP here is basic and would not block an inline script on a page that needs one without a nonce.
- nginx headers apply to this site only; the applications on :3000 and :4280 still lack them.

That last point is the one most reports miss: hardening the proxy does not harden the application behind it.

## Evidence to collect

- `evidence/headers-before.txt` and the after capture — raw headers, not descriptions.
- `evidence/paths.txt` — path and method results.
- `evidence/tls-before.txt`, `evidence/tls-after.txt` — negotiated protocol and the obsolete-protocol attempt.
- `/etc/nginx/sites-available/lab304` (copy it into `evidence/lab304.conf`).
- `evidence/header-audit.md` — before/after table with the command for each row.
- `evidence/residual.md`.

## Verification

- [ ] Both applications audited; eight header rows filled with observed values.
- [ ] At least six paths and five methods tested, with status codes recorded.
- [ ] Weak service negotiated an obsolete protocol and listed a directory.
- [ ] Hardened service returns all six headers, `403` on the directory, `405` on `PUT`.
- [ ] TLS 1.1 refused after hardening.
- [ ] Residual risks listed, including that the two applications remain unchanged.

## Teardown and reset

```bash
sudo rm -f /etc/nginx/sites-enabled/lab304 /etc/nginx/sites-available/lab304
sudo nginx -t && sudo systemctl reload nginx
```

Remove `/etc/nginx/lab304` and `/var/www/lab304` if you do not need them, then revert `pre-lab-304-04`. Leaving a
site enabled is untidy rather than dangerous, but an unexplained listener on `:8443` will confuse you in Level 4
when you baseline the host.

## Reflection

1. `server_tokens off` removes the version but not the product name. What does that buy, and why is it still worth
   doing?
2. An absent `X-Frame-Options` on a static marketing page versus on an authenticated settings page — argue for
   different severities.
3. HSTS was set to one year with no `includeSubDomains`. Give one reason to add it and one reason to be cautious.
4. Your hardening is at the proxy. Explain what a request to `:3000` still gets, and where the corresponding fix
   belongs.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Audit coverage | Fewer than four headers | Eight headers plus paths and methods | Full audit with risk stated per row, including rows that are not exploitable |
| TLS analysis | Version quoted from memory | Negotiated version shown | Negotiated version plus an obsolete-protocol attempt, before and after |
| Hardening | Advice only | Config applied | Config applied with `always`, method restriction, and token suppression |
| Verification | Assumed from config | Headers captured | Every row has a command and observed output; residual risks listed |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `nginx -t` fails on `ssl_protocols TLSv1` | Library disables obsolete protocols | Remove them, note the limitation, continue |
| `curl` to `:8443` refused | Site not enabled or nginx not reloaded | `ls /etc/nginx/sites-enabled/`, then `systemctl reload nginx` |
| Headers missing on error pages | `add_header` without `always` | Add `always` to each directive |
| `403` on `/` after hardening | `try_files` and index mismatch | Ensure `index.html` exists and `index` is configured |
| `PUT` returns `405` from nginx but `200` before | The `if` block is doing its job | Expected |
| `openssl s_client` hangs | Waiting on stdin | Redirect `</dev/null` |

## References

1. OWASP Secure Headers Project. Accessed 2026-10-29.
2. OWASP WSTG v4.2 — WSTG-CONF-07 (HSTS), WSTG-CONF-06 (HTTP Methods), WSTG-CRYP-01 (Weak TLS).
3. RFC 8996 — Deprecating TLS 1.0 and TLS 1.1. IETF, 2021.
4. nginx documentation — `ssl_protocols`, `add_header`, `server_tokens`, `autoindex`. Accessed 2026-10-29.
5. OWASP ASVS 5.0 — V12 Secure Communication, V13 Configuration. <https://asvs.owasp.org/>

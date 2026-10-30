---
title: "TCP, UDP, HTTP, HTTPS and TLS"
description: "Transport behaviour, common ports, HTTP message anatomy, and what TLS protects — with a local handshake you can inspect."
module_code: CYB-108
level: 1
kind: lesson
prerequisites: [CYB-107]
estimated_minutes: 90
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, tcp, udp, http, tls]
---

# TCP, UDP, HTTP, HTTPS and TLS

## Learning objectives

By the end of this lesson you can:

1. Compare TCP and UDP, and choose which a service needs.
2. Read TCP flags and explain the three-way handshake and connection teardown.
3. Place at least ten common services on their default ports.
4. Describe an HTTP request and response, including status codes and the headers that matter for security.
5. Explain what TLS provides, what it does not, and how certificate validation fails.
6. Inspect a local TLS handshake with `openssl s_client`.

## Prerequisites

[CYB-107](../07-networking-fundamentals/index.md) and the first lesson of this module. `openssl` and
`curl` installed (default on Ubuntu Server).

---

## 1. TCP versus UDP

| | TCP | UDP |
| --- | --- | --- |
| Connection | Established (handshake) | Connectionless |
| Reliability | Retransmits lost data | Best effort |
| Ordering | Guaranteed | Not guaranteed |
| Overhead | Higher | Lower |
| Typical use | HTTP, SSH, SMTP, file transfer | DNS, DHCP, NTP, streaming, VPNs |

Security implications:

- TCP's handshake makes connection tracking, scanning, and rate limiting meaningful.
- UDP services are easier to spoof (no handshake) and often forgotten in firewall rules.
- A "connection refused" (TCP RST) tells you the host is reachable but nothing is listening. A timeout
  suggests filtering or a dropped packet. Those are different findings.

### Flags you will see in captures

| Flag | Meaning |
| --- | --- |
| `S` | SYN — open a connection |
| `S.` | SYN-ACK — accept |
| `.` | ACK — acknowledge |
| `P.` | PSH-ACK — carries data |
| `F.` | FIN-ACK — orderly close |
| `R` | RST — reset/refuse |

## 2. Common ports worth knowing

| Port | Service | Note |
| --- | --- | --- |
| 22 | SSH | Remote administration; brute-force target |
| 23 | Telnet | Plaintext; should not exist on modern networks |
| 25 / 587 / 465 | SMTP submission | Mail; abuse target |
| 53 | DNS | TCP and UDP |
| 80 | HTTP | Plaintext web |
| 443 | HTTPS | TLS-wrapped HTTP |
| 445 | SMB | File sharing; major lateral-movement path |
| 3306 / 5432 | MySQL / PostgreSQL | Database; should not be internet-facing |
| 3389 | RDP | Remote desktop; heavily attacked |
| 8080 | Alternate HTTP | Proxies, app servers, labs |

Port numbers are conventions, not guarantees: anything can run on any port. That is why "it is on 443, so
it is encrypted" is a dangerous assumption.

## 3. HTTP in one page

```http
GET /login HTTP/1.1
Host: app.example.test
User-Agent: curl/7.81.0
Accept: */*
Cookie: session=abc123
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Set-Cookie: session=def456; HttpOnly; Secure; SameSite=Lax
Content-Length: 1234

<!doctype html>...
```

What matters for security:

| Element | Why |
| --- | --- |
| Method (`GET`, `POST`, …) | Safe methods should not change state; `GET` with side effects is a finding |
| Path and query | Input surface; injection and traversal live here |
| `Host` header | Virtual hosting, and a source of cache/poisoning issues |
| `Cookie` / `Set-Cookie` | Session transport; `HttpOnly`, `Secure`, `SameSite` are the controls |
| `Authorization` | Bearer tokens and basic auth; must travel over TLS |
| Status codes | `2xx` success, `3xx` redirect, `4xx` client error, `5xx` server error |

Try it locally (server from LAB-107-01):

```bash
python3 -m http.server 8000 --bind 127.0.0.1 &
curl -sv http://127.0.0.1:8000/ 2>&1 | head -20
```

**Expected output** includes the request line, headers, a `200 OK` status, and `Server: SimpleHTTP/...`.
Stop the server afterwards with `kill %1`.

## 4. HTTPS and TLS

TLS sits between TCP and HTTP. It provides:

- **Confidentiality** — traffic is encrypted in transit.
- **Integrity** — tampering is detectable.
- **Server authentication** — the certificate proves the server's identity, *if* the client validates it.

TLS does **not** provide: protection at the endpoints, protection from a compromised server, user
authentication, or anonymity. HTTPS protects the pipe, not the contents after arrival.

### Certificate validation is the security control

A client checks that the certificate chains to a trusted authority, matches the hostname, and is within its
validity dates. Disable validation (`curl -k`, browser "proceed anyway") and the authentication guarantee
is gone — leaving encryption to whoever is in the middle.

Build a local demonstration with a self-signed certificate:

```bash
cd /tmp && mkdir -p tlsdemo && cd tlsdemo
openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -keyout key.pem -out cert.pem -subj "/CN=localhost" 2>/dev/null
openssl s_server -accept 8443 -cert cert.pem -key key.pem -www 2>/dev/null &
```

Inspect the handshake:

```bash
openssl s_client -connect 127.0.0.1:8443 -servername localhost </dev/null 2>/dev/null | head -20
```

**Expected output** includes the protocol version, cipher suite, and a certificate chain with
`verify error: self-signed certificate`. Now compare clients:

```bash
curl -s https://127.0.0.1:8443/ -o /dev/null; echo "without -k exit: $?"
curl -sk https://127.0.0.1:8443/ -o /dev/null; echo "with -k exit: $?"
```

**Expected:**

```text
without -k exit: 60
with -k exit: 0
```

Exit code 60 is "SSL certificate problem". That single number is the difference between authenticated
encryption and encryption to an unknown party.

Cleanup:

```bash
kill %1 2>/dev/null; rm -rf /tmp/tlsdemo
```

## 5. What this means in practice

| Claim | Reality check |
| --- | --- |
| "It uses HTTPS, so it is safe" | Only if certificates are validated and the server is not compromised |
| "Traffic is encrypted, so monitoring is pointless" | Metadata remains: SNI, DNS, IPs, timing, volumes |
| "Port 443 means HTTPS" | Ports are conventions; verify the protocol |
| "TLS protects the database" | TLS protects data in transit; data at rest needs its own controls |
| "Certificate warnings are fine to click through" | That click trains users to defeat the only authentication control |

---

## Practical exercises

### Exercise 1 — Read a real exchange (15 minutes)

With the local server running, capture and inspect one request/response pair:

```bash
curl -sv http://127.0.0.1:8000/ 2>&1 | sed -n '1,12p'
```

In your notes, list: method, path, `Host`, one request header you recognise, status code, and one response
header that exists for security reasons.

### Exercise 2 — Port reasoning (10 minutes)

For each service, state TCP or UDP (or both) and one security concern:

1. DNS
2. SSH
3. SMB
4. NTP
5. RDP

### Exercise 3 — Break and fix certificate validation (20 minutes)

Run the TLS demonstration above. Record:

- The exact `verify error` line.
- The exit code without `-k` and with `-k`.
- One sentence on what an attacker gains if users habitually ignore that error.

### Exercise 4 — Status code interpretation (10 minutes)

For each response, state what happened and whether it suggests a security issue:

1. `200 OK` on `/admin` for a normal user
2. `302` to `/login` when requesting `/dashboard`
3. `403 Forbidden` on `/api/users/42`
4. `500 Internal Server Error` with a stack trace in the body

## Expected observations and verification

- You can identify TCP flags in a capture from LAB-107-01.
- You produced a TLS handshake locally and saw a self-signed verification failure.
- You can explain the difference between encryption and authentication.
- You can name one thing HTTPS does not protect.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| `curl: (60) certificate problem` treated as an error to bypass | Impatience | That is the control working; use `-k` only in a lab, and say why |
| `s_server` fails with "address in use" | Port 8443 busy | Choose another port, or stop the previous process |
| Believing `-k` is acceptable in production tooling | Convenience | Never ship scripts that disable validation |
| Thinking TLS hides everything from monitoring | Marketing | Metadata (SNI, DNS, timing) remains visible |
| Assuming a 403 means "secure" | It is just an authorization response | Test with different roles before concluding |
| Forgetting to stop background servers | They linger | `kill %1`; check with `ss -tlnp` |

## Review questions

1. Give one reason a service would choose UDP despite losing reliability.
2. What does a TCP RST tell you that a timeout does not?
3. Which HTTP headers carry session state, and which attributes protect it?
4. What three guarantees does TLS provide, and what does it not?
5. Why is certificate validation the security-relevant part of HTTPS?
6. Why can "it is on port 443" be misleading?

## Knowledge check

1. Which flag combination accepts a TCP connection?
2. Name the port for HTTPS and one for SMB.
3. `curl` exit code 60 means what?
4. Does TLS protect data at rest? Why or why not?
5. A `302` to `/login` when requesting a protected page suggests what?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 1, 3 and 4 if 1, 3 and 5 are uncertain.)*

## Summary

- TCP is reliable and connection-oriented; UDP is cheap and unreliable, and both have security
  consequences.
- Ports are conventions; protocol behaviour is what you verify.
- HTTP headers carry the trust decisions — cookies, host, authorization.
- TLS gives confidentiality, integrity, and server authentication *only when certificates are validated*.
- Monitoring still works on metadata even when payloads are encrypted.

## Next lesson

[CYB-109 · Linux Command-Line Fundamentals](../09-linux-command-line/index.md) — where you start doing all of
this fluently, without a GUI.

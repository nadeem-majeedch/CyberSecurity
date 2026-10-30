---
title: "IPv4 Addressing, Subnets, ARP, DNS and DHCP"
description: "Address structure and prefix lengths, subnet arithmetic, address ranges, and the three protocols that make a network usable."
module_code: CYB-108
level: 1
kind: lesson
prerequisites: [CYB-107]
estimated_minutes: 120
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, ipv4, subnetting, dns, dhcp, arp]
---

# IPv4 Addressing, Subnets, ARP, DNS and DHCP

## Learning objectives

By the end of this lesson you can:

1. Convert an IPv4 address and prefix into network, broadcast, and usable host ranges.
2. Recognise private, loopback, link-local, and documentation ranges immediately.
3. Explain ARP, DNS, and DHCP, and what symptom appears when each fails.
4. Read `ipcalc`, `ip route get`, and `dig` output.
5. Diagnose a name-resolution failure versus a routing failure versus a service failure.

## Prerequisites

[CYB-107](../07-networking-fundamentals/index.md). Optional: `sudo apt install -y ipcalc` in your VM.

---

## 1. IPv4 anatomy

An IPv4 address is 32 bits, written as four decimal octets: `192.0.2.20` is
`11000000.00000000.00000010.00010100`.

The **prefix** (or netmask) says how many leading bits identify the network:

| Notation | Netmask | Network bits | Host bits |
| --- | --- | --- | --- |
| `/24` | `255.255.255.0` | 24 | 8 |
| `/25` | `255.255.255.128` | 25 | 7 |
| `/26` | `255.255.255.192` | 26 | 6 |
| `/27` | `255.255.255.224` | 27 | 5 |
| `/28` | `255.255.255.240` | 28 | 4 |

**Usable hosts = 2^(host bits) − 2** (network and broadcast addresses are not assignable).

| Prefix | Addresses | Usable hosts |
| --- | --- | --- |
| /24 | 256 | 254 |
| /25 | 128 | 126 |
| /26 | 64 | 62 |
| /27 | 32 | 30 |
| /28 | 16 | 14 |
| /30 | 4 | 2 |

### Worked example

`192.0.2.20/26`:

- Block size 64 → networks start at 0, 64, 128, 192.
- 20 falls in the 0–63 block, so **network = 192.0.2.0**, **broadcast = 192.0.2.63**,
  **usable = 192.0.2.1–192.0.2.62**.

Verify:

```bash
ipcalc 192.0.2.20/26
```

**Expected output** (format varies slightly by version):

```text
Address:   192.0.2.20          11000000.00000000.00000010.00010100
Netmask:   255.255.255.192 = 26 11111111.11111111.11111111.11000000
Wildcard:  0.0.0.63            00000000.00000000.00000000.00111111
Network:   192.0.2.0/26        11000000.00000000.00000010.00000000
HostMin:   192.0.2.1           11000000.00000000.00000010.00000001
HostMax:   192.0.2.62          11000000.00000000.00000010.00111110
Broadcast: 192.0.2.63          11000000.00000000.00000010.00111111
Hosts/Net: 62
```

## 2. Ranges you must recognise

| Range | Purpose | Why it matters in security work |
| --- | --- | --- |
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | Private (RFC 1918) | Internal traffic; never routable on the internet |
| `127.0.0.0/8` | Loopback | Local only; a "connection from 127.0.0.1" is this machine |
| `169.254.0.0/16` | Link-local | Usually a DHCP failure — a very common symptom |
| `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | Documentation (RFC 5737) | Safe addresses for labs and examples, never real hosts |
| `224.0.0.0/4` | Multicast | Discovery protocols; unexpected multicast can be interesting |
| `0.0.0.0` | "Any address" in binds | Binding a service to `0.0.0.0` exposes it on all interfaces |

**IPv6, briefly:** 128-bit addresses written in hexadecimal, with `::` collapsing zero groups.
`::1` is loopback, `fe80::/10` is link-local, and `2000::/3` is global unicast. You will meet IPv6 properly
at Level 2; for now, know that `::1` behaves like `127.0.0.1`.

## 3. ARP: address resolution on the local link

A host knows an IP but must put a frame on the wire, which needs a MAC address. **ARP** asks: "who has
`192.0.2.20`?" and the owner replies with its MAC.

```bash
ip neigh show
```

**Expected output** (entries depend on recent traffic):

```text
192.0.2.1 dev enp0s3 lladdr 52:54:00:12:34:56 REACHABLE
192.0.2.20 dev enp0s3 lladdr 08:00:27:1a:2b:3c STALE
```

Security relevance: ARP has no authentication, so an attacker on the same segment can claim an IP and
intercept traffic (**ARP spoofing**). That is why local network trust is fragile and why segmentation
matters. You will not perform ARP spoofing in this course; you will learn to recognise it in captures.

## 4. DNS: names to addresses

DNS is a distributed hierarchy: root servers → top-level domains → authoritative servers for a domain.
A resolver walks that chain (or serves from cache) and returns records.

| Record | Meaning | Example use |
| --- | --- | --- |
| `A` | Name → IPv4 | `www.example.com → 203.0.113.10` |
| `AAAA` | Name → IPv6 | |
| `CNAME` | Alias to another name | `shop → store.example.net` |
| `MX` | Mail exchanger | Mail routing, and a phishing investigation clue |
| `TXT` | Arbitrary text | SPF/DKIM/DMARC, domain verification |
| `NS` | Authoritative name servers | Delegation |
| `PTR` | Reverse lookup (IP → name) | Log enrichment; often missing or stale |

```bash
dig +short example.com A
dig example.com MX +noall +answer
```

**Expected output** (addresses change; this is a real public domain and requires internet access):

```text
93.184.216.34
```

```text
example.com.  3600  IN  MX  0 .
```

If your lab VM is isolated, these commands fail with a timeout — that is correct behaviour, not a broken
lesson. Use the `/etc/hosts` exercise below, and run `dig` on a machine with internet access.

### Local name resolution

Before DNS, the system consults `/etc/hosts` (Linux) or `C:\Windows\System32\drivers\etc\hosts` (Windows).
Hosts-file overrides are a classic persistence and testing technique — and a common cause of "it resolves
for me but not for you".

```bash
echo '127.0.0.1  intra.example.test' | sudo tee -a /etc/hosts
getent hosts intra.example.test
```

**Expected output:**

```text
127.0.0.1       intra.example.test
```

Cleanup:

```bash
sudo sed -i '/intra.example.test/d' /etc/hosts
```

## 5. DHCP: configuration without a human

**DORA** — Discover, Offer, Request, Acknowledge. A client broadcasts a request, a server offers an
address and options (gateway, DNS, lease time), the client requests it, the server confirms.

Symptoms worth memorising:

- An address in `169.254.x.x` means no DHCP response (or a static misconfiguration).
- A lease that changes between boots breaks static assumptions — in labs, prefer static addresses.
- Rogue DHCP on a network can hand out a malicious gateway or DNS server. That is a real attack class,
  and detection relies on knowing what a legitimate lease looks like.

## 6. Diagnosing in order

When "it does not work", test in this order and stop at the first failure:

| Step | Command | Failure means |
| --- | --- | --- |
| 1. Link | `ip -br link` | Interface down |
| 2. Address | `ip -br addr` | No IP, or APIPA `169.254.x.x` |
| 3. Route | `ip route get 192.0.2.20` | No route to destination |
| 4. Local network | `ping -c1 <gateway>` | Layer 2/3 issue on the segment |
| 5. Name resolution | `getent hosts name` | `/etc/hosts` or DNS problem |
| 6. Port reachability | `nc -vz 192.0.2.20 80` | Firewall or service not listening |
| 7. Application | `curl -sv http://192.0.2.20/` | Service up but failing |

Testing in this order prevents the beginner habit of restarting services when the actual problem is a
missing route.

---

## Practical exercises

### Exercise 1 — Subnet drills (20 minutes)

Without `ipcalc` first, then verify:

| Address | Prefix | Network | Broadcast | Usable range | Hosts |
| --- | --- | --- | --- | --- | --- |
| 192.0.2.130 | /26 | | | | |
| 198.51.100.77 | /27 | | | | |
| 203.0.113.200 | /28 | | | | |
| 10.10.10.10 | /25 | | | | |

Check each with `ipcalc <address>/<prefix>` and note any you got wrong.

### Exercise 2 — Route lookup (10 minutes)

```bash
ip route get 192.0.2.20
ip route get 8.8.8.8
```

Answer: which interface would each use, and why does the second one fail in an isolated lab?

### Exercise 3 — Local resolution (10 minutes)

Add and remove a hosts entry as shown in section 4. Then try to resolve a name that does not exist:

```bash
getent hosts nonexistent.example.test; echo "exit: $?"
```

**Expected:** no output, exit code 2. This is what a failed lookup looks like — worth recognising, because
"no output" is often misread as "command broken".

### Exercise 4 — ARP observation (10 minutes)

```bash
ping -c 2 192.0.2.1 >/dev/null 2>&1 || true
ip neigh show
```

Record which entry is `REACHABLE` and which is `STALE`. Explain in one line why a cache entry can be stale
even when the host is up.

## Expected observations and verification

- All four subnet rows correct on a second attempt.
- You can name the interface and gateway for a given destination.
- You saw a failed lookup produce no output and a non-zero exit code.
- You can explain the difference between "no route" and "no DNS".

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Counting network/broadcast as usable | Easy off-by-two | Hosts = 2^hostbits − 2 |
| Assuming `/24` always | Habit | Read the prefix; cloud networks are often `/20` or `/16` |
| Editing `/etc/resolv.conf` on a modern Ubuntu | It is managed by `systemd-resolved` and may be overwritten | Use `resolvectl` or netplan, not the file |
| Confusing DNS failure with network failure | Both look like "cannot connect" | Resolve by IP first: if that works, it is DNS |
| Leaving test entries in `/etc/hosts` | Forgot cleanup | Remove after each exercise; verify with `getent` |
| Treating `169.254.x.x` as a valid lab address | It appears automatically | It signals DHCP failure; fix the adapter |

## Review questions

1. How many usable hosts does a `/27` provide, and why not 32?
2. Why are documentation ranges used in course labs rather than `192.168.x.x`?
3. What does ARP resolve, and on which scope does it operate?
4. Name four DNS record types and one security use for each.
5. What are the four DHCP messages, in order?
6. Why test name resolution *after* route and reachability, not before?

## Knowledge check

1. `203.0.113.200/28` — what is the broadcast address?
2. Which range indicates a DHCP failure?
3. `ip neigh` shows what kind of mapping?
4. Which record type would you check to understand a domain's mail handling?
5. A host can reach `192.0.2.20` by IP but not by name. Which layer of diagnosis failed?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 1, 3 and 6 if 1, 2 and 5 are uncertain.)*

## Summary

- Prefix length determines network size; usable hosts = 2^hostbits − 2.
- Recognise private, loopback, link-local, and documentation ranges instantly.
- ARP resolves local MAC addresses, DNS resolves names, DHCP assigns configuration — different failures,
  different symptoms.
- `/etc/hosts` overrides DNS and is a common source of confusion (and of persistence).
- Diagnose link → address → route → reachability → name → port → application, and stop at the first
  failure.

## Next lesson

[CYB-108 · TCP, UDP, HTTP, HTTPS and TLS](02-tcp-udp-http-tls.md) — what actually travels over those
addresses.

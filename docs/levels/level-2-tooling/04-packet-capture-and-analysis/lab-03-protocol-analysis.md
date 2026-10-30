---
title: "LAB-204-03 · Protocol Analysis: DNS, TCP, HTTP, TLS"
description: "Prove four protocol behaviours from your own captures and write the analysis note the assessment report will cite."
module_code: CYB-204
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-204-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [dns, tcp, http, tls, analysis]
---

# LAB-204-03 · Protocol Analysis: DNS, TCP, HTTP, TLS

| | |
| --- | --- |
| **Level** | 2 |
| **Time** | 4 hours |
| **Prerequisites** | [CYB-203](../03-host-discovery-and-enumeration/index.md), LAB-204-01, LAB-204-02 |
| **Lab hosts** | `lab-kali`, `lab-ubuntu` |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

You have been asked to produce the protocol evidence section of a security assessment. Four claims must be
demonstrated from captures rather than asserted:

1. Name resolution happens before the connection, and is visible in the clear.
2. TCP connection setup is observable, and refusal looks different from silence.
3. HTTP exposes content; HTTPS exposes metadata only.
4. TLS identity is checkable from the handshake without decryption.

Each claim gets a capture, an observation, and a limitation. This is the lab that teaches you to write findings
that survive review.

## Learning objectives

1. Capture and interpret DNS query/response pairs.
2. Distinguish open, refused and filtered TCP behaviour from flags and timing.
3. Demonstrate the visibility difference between HTTP and HTTPS.
4. Extract TLS certificate and SNI metadata from a handshake.
5. Write four findings in a form another analyst can verify.

## Required tools and versions

| Tool | Version | Install |
| --- | --- | --- |
| `tcpdump`, `tshark` | 4.99+, 4.0+ | `sudo apt install tcpdump tshark` |
| `dig` | 9.18+ | `sudo apt install dnsutils` |
| `curl`, `openssl` | any | present |
| `dnsmasq` (optional) | 2.89+ | `sudo apt install dnsmasq` — only if you want local DNS |

## Setup

```bash
mkdir -p ~/lab204/protocols && cd ~/lab204/protocols
```

Optional local DNS, so the lab works fully offline:

```bash
# on lab-ubuntu
sudo apt install -y dnsmasq
echo 'address=/lab.internal/192.0.2.20' | sudo tee /etc/dnsmasq.d/lab.conf
sudo systemctl restart dnsmasq
```

Then point `lab-kali` at it: `echo 'nameserver 192.0.2.20' | sudo tee /etc/resolv.conf` (temporary; restore after).

## Target addresses and lab topology

```
lab-kali 192.0.2.10  --- host-only lab-only-192.0.2.0 ---  lab-ubuntu 192.0.2.20
                                                          udp/53   dnsmasq (optional, resolvable names only in the lab)
                                                          tcp/8000 HTTP
                                                          tcp/8443 HTTPS via openssl s_server
```

DNS is served from the lab host, so no public resolver is needed. Every endpoint is on `192.0.2.0/24` or loopback.

## Numbered commands and actions

### Part A — DNS

**Step A1.** Capture only DNS:

```bash
sudo tcpdump -i eth0 -nn -s 0 -c 10 -w dns.pcap 'udp port 53'
```

**Step A2.** In a second terminal:

```bash
dig lab.internal
dig nonexistent.lab.internal
```

**Step A3.** Read the exchange:

```bash
tshark -r dns.pcap -Y 'dns' -T fields \
  -e dns.id -e dns.flags.response -e dns.qry.name -e dns.a
```

**Expected:** paired rows sharing a transaction ID; `flags.response` 0 then 1; the first name resolves to
`192.0.2.20`; the second returns no answer and `dns.flags.rcode == 3` (NXDOMAIN).

| Observation | Where |
| --- | --- |
| Query and response share an ID | `dns.id` |
| Query is before the TCP connection | frame numbers |
| NXDOMAIN | `dns.flags.rcode == 3` |

!!! note "No local DNS?"
    If you skipped `dnsmasq`, resolve a name that your lab can reach (for example `localhost` via `/etc/hosts`
    produces no packet — which is itself a useful observation: `/etc/hosts` lookups never leave the host).

### Part B — TCP setup, refusal and silence

**Step B1.** Start a capture covering three ports:

```bash
sudo tcpdump -i eth0 -nn -s 0 -c 30 -w tcp.pcap 'host 192.0.2.20 and tcp'
```

**Step B2.** Generate three behaviours:

```bash
curl -s -m 5 -o /dev/null http://192.0.2.20:8000/     # open (start the server first)
curl -s -m 5 -o /dev/null http://192.0.2.20:8123/     # closed → RST
curl -s -m 5 -o /dev/null http://192.0.2.20:9/        # filtered → timeout, no reply
```

**Step B3.** Compare:

```bash
tshark -r tcp.pcap -Y 'tcp.flags.syn == 1 || tcp.flags.reset == 1' -T fields \
  -e frame.number -e ip.src -e tcp.srcport -e tcp.dstport -e tcp.flags.str
```

**Expected:** for the open port, `SYN` → `SYN, ACK` → `ACK`. For the closed port, `SYN` → `RST, ACK`. For the
filtered port, repeated `SYN` with retransmission delays and no reply.

**Step B4.** Record the timing difference between the three (Wireshark: **Statistics → Flow Graph**, or
`-z io,stat,0.1`).

| Behaviour | Signature | Client experience |
| --- | --- | --- |
| Open | SYN, SYN/ACK, ACK | Fast connect |
| Closed (host up) | SYN → RST | Immediate refusal |
| Filtered (dropped) | SYN retransmissions, no reply | Timeout after seconds |

### Part C — HTTP vs HTTPS visibility

**Step C1.** Start a TLS server on `lab-ubuntu`:

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout key.pem -out cert.pem -subj "/CN=lab.internal/O=Training Lab"
openssl s_server -accept 8443 -cert cert.pem -key key.pem -www
```

**Step C2.** Capture both protocols:

```bash
sudo tcpdump -i eth0 -nn -s 0 -c 200 -w web.pcap 'host 192.0.2.20 and (tcp port 8000 or tcp port 8443)'
```

```bash
curl -s -o /dev/null http://192.0.2.20:8000/
curl -sk -o /dev/null https://192.0.2.20:8443/
```

**Step C3.** Compare payload visibility:

```bash
echo "=== HTTP ==="; tshark -r web.pcap -Y 'http.request' -T fields -e http.request.method -e http.request.uri -e http.user_agent
echo "=== TLS ==="; tshark -r web.pcap -Y 'tls.handshake.type == 1' -T fields -e ip.dst -e tls.handshake.extensions_server_name
```

**Expected:** the HTTP row contains method, URI and user agent. The TLS row contains only the destination and
SNI — which is empty here because you connected by IP address.

### Part D — TLS identity metadata

**Step D1.** Extract the certificate details:

```bash
tshark -r web.pcap -Y 'tls.handshake.type == 11' -T fields \
  -e x509sat.printableString -e x509af.utcTime
```

Or inspect live:

```bash
echo | openssl s_client -connect 192.0.2.20:8443 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

**Expected:** subject `CN = lab.internal, O = Training Lab`, issuer identical (self-signed), validity 30 days from
creation.

**Step D2.** Explain the difference between *identity claimed* and *identity verified*: a self-signed certificate
proves the server holds the key, not that it is who it claims to be. `curl` needed `-k` for exactly that reason.

## Evidence to collect

| File | Contents |
| --- | --- |
| `dns.pcap` | Query/response pair, NXDOMAIN |
| `tcp.pcap` | Open, refused, filtered |
| `web.pcap` | HTTP request text; TLS handshake metadata |
| `protocol-findings.md` | Four findings, each with capture reference and limitation |

Each finding follows: **Claim → Evidence (file + filter) → Observation → Limitation.**

## Verification criteria

- [ ] DNS query/response pair identified by shared transaction ID.
- [ ] NXDOMAIN explained with `rcode == 3`.
- [ ] Three TCP behaviours distinguished by flags and timing, not assumption.
- [ ] HTTP content shown to be readable; HTTPS shown to be metadata-only.
- [ ] Certificate subject, issuer and validity extracted.
- [ ] Each finding states what the capture cannot prove.
- [ ] PCAPs are hashed and named per the CYB-204 convention.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| No DNS packets | Name in `/etc/hosts`, or resolver not the lab host | Use a name only the lab DNS knows |
| All three ports time out | Host firewall drops everything | `sudo iptables -L -n` on lab-ubuntu; temporarily allow 8000 |
| No SNI in handshake | Connected by IP | Use a hostname that resolves, and `curl --resolve` |
| Certificate fields missing | Wireshark version lacks the x509 field names | Use the `openssl s_client` alternative |
| `s_server` will not start | Port already in use | Choose another port above 1024 |

## Cleanup and restoration

```bash
# Stop s_server, http.server and nc (Ctrl-C each)
# Remove the temporary resolver change
sudo rm -f /etc/resolv.conf.bak
# If you installed dnsmasq for the lab:
sudo systemctl disable --now dnsmasq && sudo apt remove --purge -y dnsmasq

pgrep -a tcpdump || echo "no capture running"
chmod 600 ~/lab204/protocols/web.pcap    # may contain request metadata
```

## Questions and extension challenges

1. Why does an IP-address connection produce no SNI, and why does that matter for detection?
2. A host answers SYN with RST for every port. What can and cannot you conclude?
3. Retransmission timing differences: what do they reveal about a firewall's behaviour?
4. Add `--resolve` to `curl` so a hostname is sent without changing DNS, and capture the resulting SNI.
5. Write the four findings again for a reader who has never used Wireshark — same evidence, no jargon.

---
title: "Layered Networking and Encapsulation"
description: "The OSI and TCP/IP models, protocol data units, devices at each layer, and a walked-through encapsulation example."
module_code: CYB-107
level: 1
kind: lesson
prerequisites: [CYB-106]
estimated_minutes: 120
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, osi, encapsulation, tcp-ip]
---

# Layered Networking and Encapsulation

## Learning objectives

By the end of this lesson you can:

1. Name the seven OSI layers and the four TCP/IP layers, in order, with one protocol example each.
2. Map any OSI layer to its TCP/IP equivalent.
3. Explain encapsulation and name the PDU at each layer.
4. Identify which layer a device or control operates at, and why that limits what it can see.
5. Distinguish MAC address, IP address, and port number.
6. Read the output of `ip link`, `ip addr`, and `ping`, and say what each proves.

## Prerequisites

[CYB-106](../06-computer-hardware-os-fundamentals/index.md). A Linux environment with `sudo`.

---

## 1. Why layering exists

Networks are built in layers so that each layer can solve one problem and ignore the rest. A browser does
not need to know whether the connection is Ethernet or Wi-Fi; Wi-Fi does not need to know whether the bytes
are HTTP or SSH.

For security, layering answers a practical question: **what can this control actually see?**

- A switch sees frames and MAC addresses.
- A router sees IP packets and IP addresses.
- A firewall may see packets, or connections, or application data, depending on its type.
- A web application firewall sees HTTP requests — and nothing about the TCP handshake underneath.

If you deploy a control at the wrong layer, it cannot help you. That is the most common architecture
mistake in small networks.

## 2. The two models

| OSI (7) | TCP/IP (4) | What it handles | Example protocols |
| --- | --- | --- | --- |
| 7 Application | Application | The meaning of the data | HTTP, DNS, SMTP, SSH |
| 6 Presentation | Application | Encoding, encryption, compression | TLS, character encoding |
| 5 Session | Application | Conversation state | Session cookies, RPC |
| 4 Transport | Transport | End-to-end delivery, ports, reliability | TCP, UDP |
| 3 Network | Internet | Addressing and routing across networks | IP (v4/v6), ICMP |
| 2 Data link | Network access | Local delivery, hardware addressing | Ethernet, Wi-Fi, ARP |
| 1 Physical | Network access | Bits on a medium | Copper, fibre, radio |

The OSI model is a teaching and reference tool; the TCP/IP model is what the internet runs on. Use OSI to
talk precisely ("that is a layer 2 problem") and TCP/IP to describe what actually happens.

### PDUs: what the unit is called

| Layer | PDU | Contains |
| --- | --- | --- |
| Application | Data / message | HTTP request, DNS query |
| Transport | Segment (TCP) / datagram (UDP) | Ports, sequence numbers, payload |
| Network | Packet | Source and destination IP, TTL, payload |
| Data link | Frame | MAC addresses, EtherType, payload |
| Physical | Bits | Signals |

## 3. Encapsulation, walked through

You type a URL. Here is what happens, top down:

```text
HTTP GET /index.html                     ← application data
  └─ TCP header: src port 51234, dst port 80, seq/ack, flags   ← segment
       └─ IP header: src 192.0.2.20, dst 192.0.2.10, TTL 64    ← packet
            └─ Ethernet header: src MAC, dst MAC, 0x0800       ← frame
                 └─ bits on the wire                            ← physical
```

At the receiver, each layer strips its own header and passes the payload upward. A **packet capture** gives
you all of these headers at once, which is why the lab has you capture one exchange and identify each part.

## 4. Three identifiers that are not interchangeable

| Identifier | Scope | Changes when… | Example |
| --- | --- | --- | --- |
| **MAC address** | Local link only | The frame crosses a router | `08:00:27:1a:2b:3c` |
| **IP address** | Across networks | Reassigned by DHCP or moved | `192.0.2.20` |
| **Port** | One host, one service | A different service is contacted | `22` (SSH), `443` (HTTPS) |

A connection is identified by the **four-tuple**: source IP, source port, destination IP, destination port.
That tuple is what firewalls, logs, and `ss` output show you.

## 5. Seeing your own interfaces

```bash
ip link show
ip -br addr show
ip route show
```

**Expected output** (names and addresses vary):

```text
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT
lo               UNKNOWN        127.0.0.1/8 ::1/128
enp0s3           UP             192.0.2.20/24
default via 192.0.2.1 dev enp0s3 proto static
```

Read it as: `lo` is the loopback (traffic to yourself, never leaves the machine), `enp0s3` is your lab
interface with `192.0.2.20/24`, and there is a default route via `192.0.2.1` — which in a well-isolated lab
should point at nothing useful, or not exist at all.

`lo` matters for this course: **capturing on loopback is how you practise safely**, with no traffic leaving
the machine.

## 6. Reachability versus service availability

```bash
ping -c 3 192.0.2.1
```

ICMP echo proves the host responded to ICMP. It does **not** prove:

- that a service is running (ping says nothing about ports),
- that the service is healthy (it may accept connections and return errors),
- that you have permission to test anything else.

That distinction is the difference between "the host is up" and "the application is exploitable". Beginners
conflate them constantly; professionals keep them separate in findings.

## 7. Where controls live

| Control | Layer | Sees | Blind to |
| --- | --- | --- | --- |
| Switch port security | 2 | MAC addresses, frames | Anything above Ethernet |
| Router ACL | 3 | IP addresses, ports | Application content |
| Stateful firewall | 3–4 | Connections, ports | Encrypted payload |
| IDS/IPS (network) | 3–7 | Packets, some application parsing | Encrypted content, host-internal activity |
| Reverse proxy / WAF | 7 | HTTP requests and responses | Non-HTTP traffic |
| Host firewall | 3–4 on the host | Its own traffic | Other hosts |

A control that cannot see the traffic cannot protect it. This is why "we have a firewall" is not an answer
to "how do you detect lateral movement inside the network".

---

## Practical exercises

### Exercise 1 — Layer mapping (15 minutes)

For each item, name the highest OSI layer involved and justify it in a few words:

1. A switch forwarding a frame to a MAC address.
2. A router choosing a next hop for `203.0.113.9`.
3. `ping` receiving a reply.
4. A TLS handshake completing.
5. A web server returning `403 Forbidden`.

### Exercise 2 — Read your interfaces (10 minutes)

Run `ip -br addr` and `ip route`. In your notes, record: interface names, your address and prefix,
the default gateway (if any), and whether your lab VM can reach `8.8.8.8` (it should **not**, if isolated).

### Exercise 3 — Watch encapsulation (20 minutes)

```bash
python3 -m http.server 8000 --bind 127.0.0.1 &
sudo tcpdump -i lo -nn -c 6 port 8000
```

In a second terminal:

```bash
curl -s -o /dev/null http://127.0.0.1:8000/
```

**Expected tcpdump output** (sequence numbers and timing vary):

```text
IP 127.0.0.1.54321 > 127.0.0.1.8000: Flags [S], seq 123456789, win 65495, options [...], length 0
IP 127.0.0.1.8000 > 127.0.0.1.54321: Flags [S.], seq 987654321, ack 123456790, ...
IP 127.0.0.1.54321 > 127.0.0.1.8000: Flags [.], ack 1, ...
IP 127.0.0.1.54321 > 127.0.0.1.8000: Flags [P.], seq 1:78, ack 1, ... length 77
```

Identify: the three-way handshake (`S`, `S.`, `.`), then the data (`P.`). Clean up:

```bash
kill %1
```

If `tcpdump` reports "no suitable device", you likely need `sudo` (capture requires privileges).

### Exercise 4 — Prove reachability is not availability (10 minutes)

Stop the web server, then:

```bash
curl -s -m 2 http://127.0.0.1:8000/ ; echo "curl exit: $?"
ping -c 1 127.0.0.1 >/dev/null && echo "host responds"
```

**Expected:** `curl` fails (exit code 7, connection refused) while the host still responds to `ping`. Two
different questions, two different answers.

## Expected observations and verification

- You can list the four TCP/IP layers and place TCP, IP, Ethernet, and HTTP correctly.
- You saw SYN, SYN-ACK, ACK, then data in your own capture.
- You can explain why loopback capture is safe and sufficient for beginner practice.
- You can state one control that is blind to encrypted traffic.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Interchanging layer 2 and layer 3 | Both "addresses" | MAC is local-link; IP is routed |
| Believing `ping` failure means host is down | ICMP is often blocked | Test the service on its port; note both results |
| Capturing on the wrong interface | Default interface is not the one carrying traffic | Check `ip -br addr`; loopback traffic needs `-i lo` |
| `tcpdump: permission denied` | Raw capture needs privileges | `sudo`, or add capabilities deliberately |
| Forgetting to stop the test server | Left running | `kill %1` or `pkill -f "http.server 8000"` |
| Thinking a WAF protects non-HTTP services | Tool scope confusion | Match the control to the protocol |

## Review questions

1. Why does layering make controls layer-specific?
2. What is the PDU at the transport layer, and what does its header contain?
3. Which identifiers change when a packet crosses a router, and which do not?
4. Why can a network IDS not inspect encrypted payloads?
5. What does `ping` prove, and what does it not prove?
6. Why is loopback capture useful for learning?

## Knowledge check

1. At which OSI layer does a switch operate?
2. What are the three packets that open a TCP connection, in order?
3. Name the four-tuple that identifies a connection.
4. True or false: an open port proves the application is working correctly.
5. Which layer would a reverse proxy inspect: 3, 4, or 7?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 2–3 and 6 if 2 and 5 are uncertain.)*

## Summary

- Layering exists so each layer can ignore the others — and so controls can be placed where they see
  relevant data.
- OSI is the reference model; TCP/IP is what runs.
- Encapsulation wraps data in headers, and a capture shows them all at once.
- MAC, IP, and port are different identifiers with different scopes.
- Reachability, listening state, and application health are three separate facts.

## Next lesson

[CYB-108 · IP Addressing, Subnets and Core Protocols](../08-addressing-and-protocols/index.md) — the
detail behind the addresses you just read.

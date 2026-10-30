---
title: "Capture and Read Traffic"
description: "Capture mechanics, BPF filters, tcpdump and Wireshark workflows, TLS metadata, and capture evidence handling."
module_code: CYB-204
level: 2
kind: lesson
prerequisites: [CYB-203]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [tcpdump, wireshark, bpf, pcap, tls]
---

# Capture and Read Traffic

## Learning objectives

By the end of this lesson you can:

1. Explain what a capture point can and cannot see.
2. Write BPF capture filters and distinguish them from display filters.
3. Capture with `tcpdump` and analyse with `tshark` or Wireshark.
4. Read DNS, TCP handshake, HTTP and TLS exchanges from a pcap.
5. Handle capture files as evidence: naming, hashing, retention, sanitisation.
6. State the limits of a capture in a report.

## Prerequisites

[CYB-203](../03-host-discovery-and-enumeration/index.md) and a working lab network.

---

## 1. Where to capture, and what that decides

| Capture point | Sees | Misses |
| --- | --- | --- |
| On the host, `-i lo` | Traffic to itself | Everything else |
| On the host, `-i eth0` | That host's traffic | Other hosts' traffic (unless promiscuous bridging applies) |
| On a virtual switch / port mirror | All traffic on that segment | Traffic on other segments, encrypted payloads |
| On the router/firewall | Traffic crossing it | Host-local traffic |

A capture is only as good as its position. "The traffic is not there" usually means "you captured in the wrong
place", not "it did not happen".

**Promiscuous mode** lets an interface accept frames not addressed to it — useful on a mirror port, useless on a
switched segment where the frames never arrive.

## 2. BPF: filters that decide what is recorded

Capture filters run in the kernel and reduce what is written to disk. Display filters run later, in Wireshark,
against what you already captured. Mixing them up produces empty files and confusing advice.

| Goal | Capture filter (BPF) | Display filter (Wireshark) |
| --- | --- | --- |
| One host | `host 192.0.2.20` | `ip.addr == 192.0.2.20` |
| One port | `tcp port 8000` | `tcp.port == 8000` |
| Subnet | `net 192.0.2.0/24` | `ip.addr == 192.0.2.0/24` |
| DNS only | `udp port 53` | `dns` |
| Exclude SSH | `not tcp port 22` | `!tcp.port == 22` |
| HTTP methods | not expressible | `http.request.method == "POST"` |
| TCP problems | not expressible | `tcp.analysis.retransmission` |

Rule of thumb: **capture narrowly, analyse broadly** — keep the capture small enough to handle, but wide enough
to contain the context you will want later.

## 3. tcpdump essentials

```bash
# List interfaces
sudo tcpdump -D

# Capture 50 packets on the lab interface, no name resolution, full packets
sudo tcpdump -i eth0 -nn -s 0 -c 50 -w lab.pcap 'host 192.0.2.20'

# Read it back, as text
sudo tcpdump -nn -r lab.pcap | head -20

# Read with ASCII payload (useful for HTTP)
sudo tcpdump -nn -A -r lab.pcap 'tcp port 8000' | head -40

# Rotate: 10 files of 10 MB
sudo tcpdump -i eth0 -w lab-%Y%m%d-%H%M%S.pcap -C 10 -W 10 'host 192.0.2.20'
```

| Option | Meaning | Why it matters |
| --- | --- | --- |
| `-i IFACE` | Interface (`any` for all) | Wrong interface is the most common empty capture |
| `-nn` | No DNS/service name resolution | Prevents capture-time lookups and delays |
| `-s 0` | Full packet, no truncation | Truncated packets hide payload |
| `-c N` | Stop after N packets | Bounded evidence, bounded disk |
| `-w FILE` | Write pcap | Reusable evidence, analysable later |
| `-A` | ASCII payload | Readable HTTP in the terminal |
| `-X` | Hex + ASCII | Headers and binary inspection |
| `-C MB`, `-W N` | Rotate by size, keep N files | Long captures without filling the disk |

**Always bound a capture.** An unbounded `-i any` capture on a busy host can fill a disk in minutes and take the
system down — an incident you caused.

## 4. Wireshark and tshark

The GUI is convenient; `tshark` is scriptable and works over SSH. Learn both.

```bash
# Summarise a capture without opening a GUI
tshark -r lab.pcap -q -z io,phs

# HTTP requests only
tshark -r lab.pcap -Y 'http.request' -T fields -e frame.time -e ip.src -e http.host -e http.request.uri

# DNS queries
tshark -r lab.pcap -Y 'dns.flags.response == 0' -T fields -e dns.qry.name

# TLS server name (SNI) — metadata, not decryption
tshark -r lab.pcap -Y 'tls.handshake.extensions_server_name' \
  -T fields -e ip.dst -e tls.handshake.extensions_server_name
```

Wireshark workflows worth knowing: **Statistics → Protocol Hierarchy** (what is in this capture), **Follow → TCP
Stream** (one conversation, both directions), **Expert Information** (retransmissions, resets, malformed
packets), and colourising by display filter.

## 5. Reading the protocols

### DNS

A query (`dns.flags.response == 0`) and its response share a transaction ID. Look at the queried name, type, and
the answer addresses. NXDOMAIN responses in bulk suggest enumeration or a typo storm.

### TCP handshake

```
SYN → SYN, ACK → ACK  (connection open)
FIN, ACK → ACK → FIN, ACK → ACK  (orderly close)
RST  (refusal or abort)
```

Relative sequence numbers (Wireshark default) make this readable. Retransmissions and duplicate ACKs explain most
"slow application" complaints that logs cannot.

### HTTP

Plaintext HTTP is fully visible: method, host, URI, headers, cookies, body. This is why HTTP on a network is a
finding, and why `Authorization: Basic` over HTTP is a serious one.

### TLS metadata

Without decryption you can still see:

| Field | Where | What it reveals |
| --- | --- | --- |
| SNI | ClientHello extension | Destination hostname |
| Certificate subject/SAN | ServerHello → Certificate | Identity claimed by the server |
| Validity dates | Certificate | Expiry, and sometimes misconfiguration |
| TLS version, cipher suite | Handshake | Weak configuration (e.g. TLS 1.0) |
| Certificate issuer | Certificate | Self-signed vs public CA |

That metadata is enough for a lot of detection work — and it is exactly why "encrypted" does not mean "invisible".

## 6. Captures as evidence

| Practice | Why |
| --- | --- |
| Name files `YYYYMMDD-HHMMSS-host-purpose.pcap` | Sortable, self-describing |
| Record the filter and interface in your notes | Reproducibility |
| Hash the file (`sha256sum`) at capture time | Integrity |
| Keep captures out of Git | Size and sensitivity |
| Sanitise before sharing: strip payloads, keep headers | Avoid leaking credentials or personal data |
| State the capture point in any finding | A capture without position is ambiguous |
| Delete when the module ends unless the assessment needs it | Retention discipline |

```bash
sha256sum lab.pcap | tee lab.pcap.sha256
```

## 7. What a capture cannot tell you

- What happened inside the host (file writes, memory, local logs).
- What was dropped before it reached the capture point.
- The contents of encrypted traffic without keys.
- Whether the same bytes were also sent somewhere you were not capturing.
- Intent, or who was at the keyboard.

Write those limits down. A finding that overstates its evidence is worse than no finding.

---

## Practical exercises

### Exercise 1 — Filter translation (10 minutes)

Convert each capture filter to a display filter, and explain why one of them cannot be expressed the other way:

1. `host 192.0.2.20 and tcp port 443`
2. `udp port 53`
3. `not tcp port 22`
4. `http.request.method == "POST"` (display-only)

### Exercise 2 — Bounded capture (15 minutes)

Capture exactly 30 packets of DNS traffic on your lab interface, write to a file, then read it back with
`tcpdump -nn -r`. Confirm the file is small and the filter is correct.

### Exercise 3 — TLS metadata (15 minutes)

Query any HTTPS endpoint from your lab VM (if internet is available) while capturing, then run the `tshark` SNI
command. If the lab is isolated, generate TLS locally with `openssl s_server` as in CYB-108 and capture that.

### Exercise 4 — Sanitise a capture (15 minutes)

Take a capture containing an HTTP request with a cookie. Produce a sanitised version suitable for sharing:
remove payload bytes but keep headers.

*Hint:* `tcpdump -nn -r in.pcap -w out.pcap 'tcp port 80'` keeps packets; to strip payload entirely, `-s 96`
truncates to headers, which is often enough for a protocol finding.

## Expected observations and verification

- Your captures are bounded and named consistently.
- You can state the capture point for each file.
- You translated filters in both directions and know which are capture-only.
- You extracted SNI from a TLS handshake without decrypting anything.
- You can list three things a capture cannot show.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Empty capture | Wrong interface, or filter too narrow | `tcpdump -D`; try `-i any` briefly |
| Capture fills the disk | No `-c`, `-C`, or time bound | Always bound; monitor with `df -h` |
| Confusing capture and display filter syntax | Similar names | BPF at capture, Wireshark syntax afterwards |
| Truncated packets hide the payload | Default snap length in some tools | `-s 0` |
| `permission denied` | Raw capture requires privileges | `sudo`; consider capabilities for repeated use |
| Sharing a pcap with credentials in it | Convenience | Sanitise; strip payloads |

## Review questions

1. Why does the capture point determine what you can conclude?
2. What is the difference between a capture filter and a display filter?
3. Why should every capture be bounded?
4. What TLS fields remain visible without decryption?
5. Why hash a capture file at creation time?
6. Name three things a capture cannot prove.

## Knowledge check

1. Which `tcpdump` flag writes to a file?
2. Which filter syntax does `tcpdump -w` accept?
3. What does the SNI extension reveal?
4. Why is `-s 0` important when writing a pcap?
5. What does a retransmission in Wireshark's expert information suggest?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 2–4 if 2, 3 and 5 are uncertain.)*

## Summary

- Capture position defines your conclusions; state it with every finding.
- Capture narrowly with BPF; analyse broadly with display filters.
- `tcpdump` and `tshark` give you the same power without a GUI.
- DNS, handshakes, HTTP and TLS metadata tell most of the story.
- Captures are evidence: named, hashed, bounded, sanitised, and honestly limited.

## Next lesson

[CYB-205 · OpenSSH and Secure Remote Administration](../05-ssh-secure-administration/index.md) — managing the
hosts you have been analysing.

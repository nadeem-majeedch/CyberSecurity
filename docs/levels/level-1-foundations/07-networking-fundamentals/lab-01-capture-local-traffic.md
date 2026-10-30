---
title: "LAB-107-01 · Capture a Local Exchange"
description: "Capture loopback traffic and explain a full HTTP exchange layer by layer, without any traffic leaving the machine."
module_code: CYB-107
level: 1
kind: lab
prerequisites: [CYB-107]
estimated_minutes: 60
difficulty: beginner
safety: local-only
lab_ids: [LAB-107-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, tcpdump, packet-analysis]
---

# LAB-107-01 · Capture a Local Exchange

**Module:** CYB-107 · **Time:** 60 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-107-01`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `127.0.0.1` (loopback) and the HTTP server you start yourself on port 8000.
    **Targets you must not use:** any other host, any address on your home network, your university or
    employer network, or any public system.

    Capture on loopback only (`-i lo`). Nothing in this lab leaves the virtual machine.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Objective

Produce a packet capture of one HTTP request to a local server, identify the TCP handshake and the data
exchange, and write a five-line narrative that names what each packet is doing.

## Threat model

None. This lab generates synthetic traffic between two processes on one machine. You are learning to read
evidence, not to attack anything.

## Environment

| Host | Role | Address | Notes |
| --- | --- | --- | --- |
| `lab-ubuntu` | Client and server, same machine | `127.0.0.1` | Loopback interface `lo` |

Software: Ubuntu Server 22.04.x, `tcpdump` 4.99+, `curl` 7.81+, Python 3.10+ (`http.server`).
Wireshark is optional; this lab uses `tcpdump` so it works over SSH and without a desktop.

## Before you start

1. Take a snapshot named `pre-lab-107-01`.
2. Confirm you are in the lab VM, not on your host:

   ```bash
   hostname
   ip -br addr show lo
   ```

   Expected: your VM hostname, and `lo ... 127.0.0.1/8`.

## Procedure

### Step 1 — Create the evidence folder

```bash
mkdir -p ~/cyber/level-1/lab-107-01/evidence
cd ~/cyber/level-1/lab-107-01
```

### Step 2 — Start a local web server

```bash
cd /tmp && mkdir -p lab107site && cd lab107site
printf '<html><body><h1>Lab 107</h1></body></html>\n' > index.html
python3 -m http.server 8000 --bind 127.0.0.1 &
```

Expected output:

```text
Serving HTTP on 127.0.0.1 port 8000 (http://127.0.0.1:8000/) ...
```

`--bind 127.0.0.1` is deliberate: the server is unreachable from any other machine, which is exactly what a
beginner lab should be.

### Step 3 — Start the capture

In a second terminal (or use `tmux`):

```bash
cd ~/cyber/level-1/lab-107-01/evidence
sudo tcpdump -i lo -nn -s 0 -c 12 -w lab107.pcap 'tcp port 8000'
```

`-i lo` loopback · `-nn` no name/port resolution · `-s 0` full packets · `-c 12` stop after 12 ·
`-w` write to file.

### Step 4 — Generate the traffic

In a third terminal:

```bash
curl -sv http://127.0.0.1:8000/ -o /dev/null
```

Expected `curl` output includes a connection line, request headers, a `200 OK` status, and the response
headers. The capture stops itself after 12 packets.

### Step 5 — Read the capture

```bash
sudo tcpdump -nn -r lab107.pcap | head -20
```

**Expected output** (ports, sequence numbers, and timing vary; your ephemeral source port will be
different):

```text
IP 127.0.0.1.54321 > 127.0.0.1.8000: Flags [S], seq 2517304939, win 65495, options [mss 65495,sackOK,TS val ...], length 0
IP 127.0.0.1.8000 > 127.0.0.1.54321: Flags [S.], seq 3299481221, ack 2517304940, win 65483, options [...], length 0
IP 127.0.0.1.54321 > 127.0.0.1.8000: Flags [.], ack 1, win 512, length 0
IP 127.0.0.1.54321 > 127.0.0.1.8000: Flags [P.], seq 1:86, ack 1, length 85
IP 127.0.0.1.8000 > 127.0.0.1.54321: Flags [.], ack 86, length 0
IP 127.0.0.1.8000 > 127.0.0.1.54321: Flags [P.], seq 1:238, ack 86, length 237
```

If you want to see the HTTP text itself:

```bash
sudo tcpdump -nn -A -r lab107.pcap 'tcp port 8000' | grep -A6 'GET /'
```

### Step 6 — Write the narrative

In `narrative.md`, answer in five numbered lines:

1. Which packet opens the connection, and what does `[S]` mean?
2. Which packet acknowledges it from the server side?
3. Which packet carries the HTTP request, and how do you know?
4. Which packet carries the response?
5. What would you expect to see if the server were not running?

## Evidence to collect

- `lab107.pcap` (the capture).
- `narrative.md` (your five-line explanation).
- The `curl -sv` output, pasted as text.
- Your `hostname` and `ip -br addr show lo` output, proving the lab environment.

## Verification

- [ ] The capture contains at least 6 packets on port 8000.
- [ ] You identified SYN, SYN-ACK, ACK, and at least one data packet.
- [ ] Your narrative explains each of the five questions without copying the lesson text.
- [ ] The HTTP request line is visible in the `-A` output.
- [ ] Evidence is stored under `~/cyber/level-1/lab-107-01/evidence/`.

## Teardown and reset

```bash
# Stop the web server (the job started with & in this shell)
kill %1 2>/dev/null || pkill -f "http.server 8000"
# Remove the test site
rm -rf /tmp/lab107site
# Confirm nothing is left listening on 8000
ss -tlnp | grep 8000 || echo "port 8000 free"
```

Revert to snapshot `pre-lab-107-01` if you changed any interface or service configuration.

## Reflection

1. Why does capturing on `lo` produce the same TCP behaviour as capturing on a real network?
2. The capture shows only 12 packets for one request. Where did the TLS packets go, and why are there none?
3. If you captured on `enp0s3` instead of `lo`, would you have seen this traffic? Why?
4. What does `-c 12` protect you from in a lab with other traffic?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Fewer than 6 packets; handshake not identified | Handshake and data identified | Handshake, data, and expected failure behaviour explained |
| Methodology | Captured without understanding flags | Chose interface and filter deliberately | Justifies filter and count; explains what was excluded |
| Evidence | Capture missing or untimestamped | Capture plus narrative present | Reproducible steps, raw output, annotated narrative |
| Safety | Captured on a non-loopback interface | Loopback only | Loopback only, plus a note on why it is sufficient |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `tcpdump: permission denied` | Raw capture needs privileges | Run with `sudo` |
| `tcpdump: no suitable device found` | Wrong interface name | `tcpdump -D` lists devices; use `lo` |
| Capture stops immediately | Another process matched and filled `-c 12` | Use a narrower filter, or raise the count |
| `curl: (7) Failed to connect` | Server not running, or bound elsewhere | Check the server terminal; `ss -tlnp | grep 8000` |
| No packets shown by `-r` | File written to a different directory | Use the absolute path; check `pwd` |
| Empty HTTP text with `-A` | Packets truncated at capture time | Re-capture with `-s 0` |

## Related

- [Layered Networking and Encapsulation](01-osi-tcpip.md)
- [IP Addressing, Subnets and Core Protocols](../08-addressing-and-protocols/index.md)
- [Lab Safety Guide](../../../start-here/lab-safety.md)

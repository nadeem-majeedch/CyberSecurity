---
title: "LAB-204-01 · Capture with tcpdump and Inspect a pcap"
description: "Bound a capture on a lab interface, write a pcap, hash it, and read it back from the terminal."
module_code: CYB-204
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-204-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [tcpdump, pcap, evidence]
---

# LAB-204-01 · Capture with tcpdump and Inspect a pcap

| | |
| --- | --- |
| **Level** | 2 |
| **Time** | 4 hours |
| **Prerequisites** | [CYB-203](../03-host-discovery-and-enumeration/index.md) |
| **Lab hosts** | `lab-kali` 192.0.2.10, `lab-ubuntu` 192.0.2.20 |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

A colleague reports that a service on `lab-ubuntu` "sometimes takes ten seconds". No log shows anything unusual.
You are asked to capture the interaction and produce a pcap that another analyst could re-examine without you.

You will capture on the client, bound the capture, name it consistently, hash it at creation, and read it back
entirely from the terminal — because the first place you will ever need this is an SSH session with no GUI.

## Learning objectives

1. Capture on a specific interface with a deliberate filter.
2. Bound a capture by packet count and by rotation.
3. Name, hash, and store a capture as evidence.
4. Read a pcap with `tcpdump -r` in summary, ASCII and hex modes.
5. Verify that a capture contains what you claim it contains.

## Required tools and versions

| Tool | Version | Install |
| --- | --- | --- |
| `tcpdump` | 4.99+ | `sudo apt install tcpdump` (present in Kali) |
| `python3` | 3.11+ | present |
| `curl`, `nc` | any | `sudo apt install curl netcat-openbsd` |

## Setup

```bash
mkdir -p ~/lab204/pcap
cd ~/lab204
ip -brief addr            # confirm 192.0.2.10/24 on eth0
ping -c 2 192.0.2.20      # confirm the target is up
```

On `lab-ubuntu`, start a listener you control:

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

## Target addresses and lab topology

```
lab-kali 192.0.2.10  --- host-only lab-only-192.0.2.0 ---  lab-ubuntu 192.0.2.20
        (capture point: eth0)                            (service: tcp/8000)
```

You capture on `lab-kali`'s `eth0`; the only traffic in scope is between these two addresses on `192.0.2.0/24`.

## Numbered commands and actions

### Step 1 — Know your interfaces

```bash
sudo tcpdump -D
```

**Expected:** a numbered list including `eth0` and `lo`.

### Step 2 — Capture with a bounded filter

In terminal 1 on `lab-kali`:

```bash
sudo tcpdump -i eth0 -nn -s 0 -c 20 \
  -w ~/lab204/pcap/01-http-basic.pcap 'host 192.0.2.20 and tcp port 8000'
```

**Expected:** `listening on eth0, link-type EN10MB` then `20 packets captured` once the count is reached.

| Option | Meaning |
| --- | --- |
| `-i eth0` | Capture on the lab interface only |
| `-nn` | No name resolution (faster, no DNS noise) |
| `-s 0` | Whole packet, no truncation |
| `-c 20` | Stop after 20 packets |
| `-w FILE` | Write binary pcap rather than printing |
| `'...'` | BPF filter, evaluated in the kernel |

### Step 3 — Generate the traffic

In terminal 2:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.20:8000/
curl -s -o /dev/null http://192.0.2.20:8000/nonexistent
```

**Expected:** `200` then a 404 in the second request. Terminal 1 reaches 20 packets and returns to the prompt.

!!! warning "If the capture does not complete"
    If traffic is too light to reach 20 packets, the capture waits. Send more requests, or add `-G 30` style
    time bounds and re-run. Never leave an unbounded capture running in an exam lab.

### Step 4 — Hash and record provenance

```bash
cd ~/lab204/pcap
sha256sum 01-http-basic.pcap | tee 01-http-basic.pcap.sha256
cat > 01-http-basic.notes.md <<'EOF'
# Capture record
- Host: lab-kali (192.0.2.10)
- Interface: eth0
- Capture point: client NIC, host-only lab network
- Filter: host 192.0.2.20 and tcp port 8000
- Bound: -c 20
- Purpose: reproduce intermittent delay on HTTP service
- Timestamp (UTC): SEE FILE MTIME
EOF
ls -l
```

**Expected:** three files — `.pcap`, `.pcap.sha256`, `.notes.md`. Record the UTC timestamp with `date -u`.

### Step 5 — Read it back without a GUI

```bash
sudo tcpdump -nn -r 01-http-basic.pcap
```

**Expected:** lines like

```
IP 192.0.2.10.41234 > 192.0.2.20.8000: Flags [S], seq 123456789, win 64240, length 0
IP 192.0.2.20.8000 > 192.0.2.10.41234: Flags [S.], seq 987654321, ack 123456790, win 65160, length 0
```

Identify the handshake by the `[S]` and `[S.]` flags. Then:

```bash
sudo tcpdump -nn -A -r 01-http-basic.pcap 'tcp port 8000' | head -40
sudo tcpdump -nn -X -r 01-http-basic.pcap | head -30
```

**Expected:** `-A` shows `GET / HTTP/1.1`, `Host:`, and `User-Agent:`; `-X` adds a hex column.

### Step 6 — Verify the claim, then extend the bound

```bash
# How many packets, really?
sudo tcpdump -nn -r 01-http-basic.pcap | wc -l

# Rotating capture: 2 files of ~1 MB each
sudo timeout 60 tcpdump -i eth0 -nn -s 0 -C 1 -W 2 -w ~/lab204/pcap/rot.pcap 'host 192.0.2.20'
ls -l ~/lab204/pcap/rot*
```

**Expected:** the packet count matches your `-c 20` (20, or 20 plus a partial line). Rotation produces
`rot.pcap0` and `rot.pcap1`.

### Step 7 — Confirm the integrity hash

```bash
sha256sum -c 01-http-basic.pcap.sha256
```

**Expected:** `01-http-basic.pcap: OK`.

## Evidence to collect

- The `.pcap`, `.sha256`, and `.notes.md` triple.
- Output of Step 5 showing the handshake and the HTTP request line.
- The packet count from Step 6.
- `sha256sum -c` result.

## Verification criteria

- [ ] Capture was bound and terminated on its own.
- [ ] Filter restricted traffic to the lab host and port.
- [ ] Provenance notes name the host, interface, capture point, filter and purpose.
- [ ] You identified SYN / SYN-ACK / ACK from `tcpdump` output.
- [ ] `-A` revealed the HTTP request line.
- [ ] Hash verifies.
- [ ] You can explain why GUI tools were not required.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `tcpdump: eth0: No such device` | Interface renamed | `tcpdump -D` and use the actual name |
| Capture never finishes | Traffic below `-c` count | Send more requests, or bound by time |
| `Permission denied` | Raw sockets need privilege | `sudo` |
| Read-back shows only `length 0` | Filter excluded payload packets | Widen the filter, keep `-s 0` |
| Huge pcap | No bound, or `any` interface | Bound with `-c`/`-C`, target one interface |

## Cleanup and restoration

```bash
# Stop any listener you started on lab-ubuntu
# (Ctrl-C in its terminal)

# Keep assessment artefacts; remove throwaway captures
rm -f ~/lab204/pcap/rot.pcap*

# Verify no capture is still running
pgrep -a tcpdump || echo "no capture running"

# Restore the VM to its post-CYB-203 snapshot
```

## Questions and extension challenges

1. Why does `-nn` matter when capturing on a host whose DNS is unreachable?
2. What does `-s 96` change about the evidence you can present later?
3. Re-capture with `-i any` and compare the packet count. Explain the difference.
4. Add a filter that excludes your own SSH session, and explain why that is often necessary.
5. Write a one-paragraph provenance statement a second analyst could follow to reproduce this capture.

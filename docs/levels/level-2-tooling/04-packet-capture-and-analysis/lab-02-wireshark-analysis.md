---
title: "LAB-204-02 · Capture and Analyse with Wireshark"
description: "Use Wireshark's protocol hierarchy, TCP stream following and expert information to explain a conversation."
module_code: CYB-204
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-204-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [wireshark, tshark, analysis]
---

# LAB-204-02 · Capture and Analyse with Wireshark

| | |
| --- | --- |
| **Level** | 2 |
| **Time** | 4 hours |
| **Prerequisites** | [CYB-203](../03-host-discovery-and-enumeration/index.md), LAB-204-01 |
| **Lab hosts** | `lab-kali`, `lab-ubuntu` |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

You have a pcap from a colleague and no explanation of what is in it. Your job is to characterise the capture
before reading a single payload byte: what protocols, which hosts, how many conversations, and whether anything
looks malformed. This "orient before you dive" habit is what separates analysis from scrolling.

## Learning objectives

1. Characterise a capture using Protocol Hierarchy and Conversations.
2. Use display filters, colourisation, and Follow TCP Stream deliberately.
3. Read Wireshark's Expert Information and explain each warning class.
4. Produce the same analysis with `tshark` for a headless environment.
5. Write a short, evidence-based narrative of one conversation.

## Required tools and versions

| Tool | Version | Install |
| --- | --- | --- |
| Wireshark GUI | 4.0+ | `sudo apt install wireshark` |
| `tshark` | 4.0+ | installed with Wireshark |
| `tcpdump` | 4.99+ | `sudo apt install tcpdump` |

If the GUI is unavailable, `tshark` covers every step. Note which you used.

## Setup

```bash
mkdir -p ~/lab204/analysis && cd ~/lab204/analysis
```

On `lab-ubuntu`, start a service and a second listener so the capture has variety:

```bash
python3 -m http.server 8000 --bind 0.0.0.0 &
nc -l -k 9999 &
```

On `lab-kali`, capture a mixed session:

```bash
sudo tcpdump -i eth0 -nn -s 0 -c 120 -w mixed.pcap 'host 192.0.2.20'
```

Then, in a second terminal, generate traffic while it runs:

```bash
curl -s -o /dev/null http://192.0.2.20:8000/
curl -s -o /dev/null http://192.0.2.20:8000/index.html
dig +short @192.0.2.20 example.test 2>/dev/null || true
printf 'hello\n' | nc -w 2 192.0.2.20 9999
```

## Target addresses and lab topology

```
lab-kali 192.0.2.10  --- host-only lab-only-192.0.2.0 ---  lab-ubuntu 192.0.2.20
                                                          tcp/8000 (HTTP), tcp/9999 (netcat)
```

All captures are filtered to `host 192.0.2.20`. Nothing outside `192.0.2.0/24` is captured or analysed.

## Numbered commands and actions

### Step 1 — Protocol hierarchy first

```bash
tshark -r mixed.pcap -q -z io,phs
```

**Expected:** a tree showing Ethernet → IPv4 → TCP → HTTP with packet counts, plus your netcat stream.

Open the same file in Wireshark: **Statistics → Protocol Hierarchy**.

Record: total packets, top three protocols by packet count, and any protocol you did not expect.

### Step 2 — Conversations

```bash
tshark -r mixed.pcap -q -z conv,tcp
```

**Expected:** one row per TCP conversation with address:port pairs, packet counts and byte counts. Identify which
conversation carried the most bytes and why.

### Step 3 — Display filters

Apply each in Wireshark's filter bar (and the `tshark -Y` equivalent), recording what each returns:

| Filter | Question it answers |
| --- | --- |
| `ip.addr == 192.0.2.20 && tcp.port == 8000` | The HTTP conversation only |
| `http.request` | Requests, not responses |
| `tcp.flags.syn == 1 && tcp.flags.ack == 0` | Connection attempts |
| `tcp.flags.reset == 1` | Refusals or aborts |
| `tcp.analysis.retransmission` | Retransmitted segments |
| `tcp.stream eq 0` | One conversation in isolation |

### Step 4 — Follow the stream

Right-click an HTTP packet → **Follow → TCP Stream**. 

**Expected:** the full request and response in one window, with client and server coloured differently.

In `tshark`:

```bash
tshark -r mixed.pcap -q -z follow,tcp,ascii,0 | head -40
```

Record the request line, the `Host` header, the response status, and the `Content-Type`.

!!! note "This is why HTTP is a finding"
    Everything above was readable without any special tooling. Note in your write-up that the same conversation
    over TLS would have exposed metadata only.

### Step 5 — Expert information

**Analyze → Expert Information**, or:

```bash
tshark -r mixed.pcap -q -z expert
```

**Expected:** warnings such as *Connection reset*, *Retransmission*, or *Duplicate ACK* — some caused by the
`nc -w 2` timeout, which closes abruptly.

For each warning class, write one sentence: what it means mechanically, and whether it is benign here.

### Step 6 — Colourise and label

Create a colour rule for `tcp.analysis.flags` and one for `http.request.method == "POST"`. Save the profile.
Explain in your notes why colour rules are a communication tool, not just a convenience.

### Step 7 — Write the narrative

Produce `analysis-note.md` (200–300 words) covering:

- Capture point and bound.
- Protocol mix.
- Each conversation, in one line.
- Expert warnings and their cause.
- What the capture does **not** show.

## Evidence to collect

`mixed.pcap` (hashed), the `-z io,phs`, `-z conv,tcp` and `-z expert` outputs, and `analysis-note.md`.

## Verification criteria

- [ ] Protocol hierarchy summarised before payload inspection.
- [ ] Every conversation accounted for.
- [ ] At least four display filters applied with recorded results.
- [ ] Follow TCP Stream used and the request/response summarised.
- [ ] Each expert warning explained mechanically.
- [ ] Narrative states the capture point and three limitations.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Wireshark cannot open the interface | User lacks capture privileges | `sudo dpkg-reconfigure wireshark-common`, add user to `wireshark` |
| Empty protocol hierarchy | Wrong file or truncated capture | `capinfos mixed.pcap` |
| No HTTP in the capture | Traffic used HTTPS or a different port | Check `tcp.port` values in conversations |
| `tshark: command not found` | GUI not installed | `sudo apt install tshark` |
| Follow Stream is unreadable | Binary payload | Use **Show data as → Hex Dump** |

## Cleanup and restoration

```bash
# Stop listeners on lab-ubuntu
# Ctrl-C the python server and nc

pgrep -a tcpdump || echo "no capture running"
rm -f ~/lab204/analysis/mixed.pcap   # only after submitting the note
```

## Questions and extension challenges

1. Which protocol dominates your capture, and does that match what you generated?
2. Why can `tcp.analysis.retransmission` be benign in a lab but significant in production?
3. Re-capture the same actions over HTTPS to a local `openssl s_server`. What remains visible?
4. Write a `tshark` one-liner that lists every distinct destination hostname seen via SNI.
5. Explain to a non-technical reader why "we captured the traffic" is not the same as "we know what was said".

---
title: "LAB-203-03 · Compare TCP and UDP Behaviour"
description: "Observe open, closed, and filtered behaviour for TCP and UDP on a lab host, and capture the packets that explain the difference."
module_code: CYB-203
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-203-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [tcp, udp, nmap, netcat, capture]
---

# LAB-203-03 · Compare TCP and UDP Behaviour

## Prerequisites

LAB-203-01 and LAB-203-02 complete: hosts discovered and services enumerated, with both VMs still on
`192.0.2.0/24` and a capture point available (`lab-kali` or a span port you control).

## Scenario and background

TCP and UDP report their states very differently, and that difference is the source of most confusion about
"filtered" ports. Rather than memorise the table, you will produce it: start listeners, scan them, capture the
packets, and explain each state from what you can see on the wire.

Everything stays on `192.0.2.0/24`.

## Learning objectives

By the end of this lab you can:

1. Explain why TCP gives definitive open/closed answers and UDP often does not.
2. Produce and interpret `open`, `closed`, and `open|filtered` results for both protocols.
3. Capture the packets that justify each conclusion.
4. Explain what an ICMP port-unreachable message contributes.
5. Report UDP findings honestly rather than overstating them.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| `nmap` | 7.94+ | `-sT`, `-sU` |
| `nc` | netcat | TCP and UDP listeners |
| `tcpdump` | 4.99+ | Capture on the analyst or target |
| `ss` | iproute2 | Confirm listeners, including UDP (`-u`) |

## Setup

On **`lab-ubuntu`**:

```bash
# TCP listener
nohup nc -lvnp 4444 >/tmp/lab203/tcp4444.log 2>&1 &

# UDP listener
nohup nc -u -lvnp 5353 >/tmp/lab203/udp5353.log 2>&1 &

ss -tlnp | grep 4444
ss -ulnp | grep 5353
```

**Why two listeners:** one gives a definitive "open" for each protocol, so you can contrast it with a port that
is closed and one that is filtered.

On **`lab-kali`**:

```bash
mkdir -p ~/lab/level-2/lab-203/evidence
```

## Target addresses and lab topology

```
lab-kali 192.0.2.10 ──► lab-ubuntu 192.0.2.20
                          TCP 4444  open     (nc listener)
                          TCP 4455  closed   (nothing bound)
                          UDP 5353  open     (nc listener)
                          UDP 5354  closed   (nothing bound, ICMP unreachable expected)
```

## Numbered commands and actions

### 1. Confirm the listeners from the target side

```bash
ss -tlnp | grep 4444
ss -ulnp | grep 5353
```

**Why:** the scan tells you what a remote observer sees; `ss` tells you what is actually bound. When they
disagree, the disagreement is the finding.

### 2. TCP: open, closed, and timing

```bash
time sudo nmap -sS -p 4444,4455 --reason 192.0.2.20 -oN evidence/tcp-states.txt
cat evidence/tcp-states.txt
```

**Expected** (state lines only):

```text
4444/tcp open  unknown
4455/tcp closed unknown
```

The `--reason` line reports `syn-ack` for open and `reset` for closed. **Interpretation:** closed is a definitive
answer, because the host replied.

### 3. UDP: open, closed, and ambiguity

```bash
sudo nmap -sU -p 5353,5354 --reason --max-retries 1 192.0.2.20 -oN evidence/udp-states.txt
cat evidence/udp-states.txt
```

**Expected:**

```text
5353/udp open  unknown
5354/udp closed unknown
```

or, frequently, `open|filtered` for one of them. **Interpretation:** if you see `closed`, the host sent ICMP
port-unreachable; if you see `open|filtered`, no answer came back and the scan cannot distinguish.

### 4. Capture the difference

On **`lab-kali`**, start a capture in one terminal:

```bash
sudo tcpdump -ni any -c 40 'host 192.0.2.20 and (port 4444 or port 4455 or port 5353 or port 5354)' \
  -w ~/lab/level-2/lab-203/evidence/tcp-udp.pcap
```

In a second terminal, run both scans again:

```bash
sudo nmap -sS -p 4444,4455 192.0.2.20
sudo nmap -sU -p 5353,5354 --max-retries 1 192.0.2.20
```

Then read the capture:

```bash
sudo tcpdump -nn -r ~/lab/level-2/lab-203/evidence/tcp-udp.pcap 'tcp port 4444 or tcp port 4455' | head
sudo tcpdump -nn -r ~/lab/level-2/lab-203/evidence/tcp-udp.pcap 'udp or icmp' | head
```

**Expected observations:**

- Port 4444: SYN → SYN-ACK → RST (the scan closes cleanly).
- Port 4455: SYN → RST (immediate refusal).
- Port 5353: a UDP datagram, then no reply, or a reply from your listener.
- Port 5354: a UDP datagram, then `ICMP port unreachable` from the host.

### 5. Explain the states in your own words

Add a table to `evidence/tcp-udp-comparison.md`:

| Probe | Response observed | Reported state | Confidence |
| --- | --- | --- | --- |
| TCP 4444 | SYN-ACK | open | Definitive |
| TCP 4455 | RST | closed | Definitive |
| UDP 5353 | no reply | open\|filtered | Ambiguous |
| UDP 5354 | ICMP unreachable | closed | Definitive |

Then answer: **why can a firewall make a UDP scan take much longer than a TCP scan?** (Because silence must be
waited out; there is no handshake to fail fast.)

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `-sU` | UDP scan | Requires ICMP or a reply to decide |
| `--max-retries 1` | Fewer retransmissions | Keeps a slow scan bounded |
| `--reason` | Justification per port | The evidence column |
| `-c 40` in tcpdump | Stop after 40 packets | Keeps the capture small |
| `-w file` | Write pcap | Reusable evidence |
| `ss -ulnp` | UDP listeners | Confirms the target's true state |

## Expected observations

- TCP produces definitive states because every probe gets a response.
- UDP produces `open|filtered` whenever nothing answers.
- ICMP port-unreachable is what converts a UDP port to `closed`.
- The capture shows exactly those packets, in order.
- Scan duration for UDP is longer, even with reduced retries.

## Verification criteria

- [ ] Both listeners confirmed with `ss` (TCP and UDP).
- [ ] TCP scan shows open and closed with `--reason` evidence.
- [ ] UDP scan recorded, including any `open|filtered` result.
- [ ] Capture saved and inspected for both protocols.
- [ ] Comparison table completed with a confidence column.
- [ ] Explanation of the UDP timing difference written.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| UDP port always `open|filtered` | Listener not running, or bound to loopback | `ss -ulnp`; rebind to `192.0.2.20` |
| `nc: Address already in use` | Previous listener still running | `pkill -f "nc -"`, then retry |
| No ICMP visible in capture | Firewall suppressing ICMP | Note it; the state will stay ambiguous |
| `tcpdump` writes nothing | Filter too narrow or wrong interface | Use `-i any` for a quick check |
| TCP closed port shows `filtered` | A local firewall is dropping RSTs | Check `iptables`/`nft` state on both hosts |
| Scan takes minutes | UDP retries | `--max-retries 1 --host-timeout 60s` |

## Cleanup and restoration

```bash
pkill -f "nc -lvnp 4444" 2>/dev/null
pkill -f "nc -u -lvnp 5353" 2>/dev/null
rm -f /tmp/lab203/tcp4444.log /tmp/lab203/udp5353.log
ss -tlnp | grep 4444 || echo "tcp listener stopped"
ss -ulnp | grep 5353 || echo "udp listener stopped"
```

Keep the pcap and comparison table for LAB-204.

## Questions and extension challenges

1. Why does a closed TCP port give a definitive answer while a closed UDP port may not?
2. What role does ICMP play in UDP scanning, and what happens if it is filtered?
3. Why is `--max-retries 1` acceptable in a lab but risky on a lossy network?
4. **Extension:** add a firewall rule dropping UDP 5354 and re-scan. Explain the new state and why it changed.
5. **Extension:** repeat the UDP scan with `-sV` and explain why UDP version detection is slower and less
   reliable than TCP.

## Related

- [Scanning Your Own Lab](01-scanning-your-lab.md)
- [LAB-203-04 · Netcat for Controlled Demonstrations](lab-04-netcat-local.md)
- [Packet Capture and Traffic Analysis](../04-packet-capture-and-analysis/index.md)

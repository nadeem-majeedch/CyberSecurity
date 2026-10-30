---
title: "Scanning Your Own Lab"
description: "nmap scan types and options, interpreting open/closed/filtered states, netcat basics, and a verification workflow."
module_code: CYB-203
level: 2
kind: lesson
prerequisites: [CYB-202]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [nmap, netcat, scanning, tcp, udp]
---

# Scanning Your Own Lab

## Learning objectives

By the end of this lesson you can:

1. Choose a discovery method and explain what response it depends on.
2. Distinguish open, closed, and filtered states from timing and flags.
3. Select scan options deliberately instead of copying `-A -T4`.
4. Verify a scanner's service guess with an independent tool.
5. Use `netcat` for a listener, a connection test, and a small transfer.
6. Explain why a scan result is a hypothesis until it is verified.

## Prerequisites

[CYB-202](../02-bash-python-git/index.md), a working lab from CYB-201, and the
[Safety Policy](../../../policies/safety-policy.md) read this week.

---

## 1. Discovery: who is there?

```bash
# ICMP echo discovery (may be blocked; that is information, not failure)
nmap -sn 192.0.2.0/24

# ARP discovery works only on the local segment, and is very reliable there
sudo nmap -sn -PR 192.0.2.0/24

# Show why each host was considered up
nmap -sn --reason 192.0.2.0/24
```

| Method | Depends on | Notes |
| --- | --- | --- |
| `-PR` (ARP) | Same broadcast domain | Best on a host-only segment; cannot cross a router |
| `-PE` (ICMP echo) | Host replying to ping | Often blocked in real networks |
| `-PS<port>` (TCP SYN) | A port answering or refusing | Answers even when ICMP is blocked |
| `-PU<port>` (UDP) | ICMP port-unreachable | Slow and unreliable, but sometimes the only answer |

**Interpretation matters more than the technique.** "No hosts found" on a segment where you know two hosts exist
means your discovery method is blocked, not that the hosts are gone. Cross-check with `ip neigh` (ARP cache) and
a direct `ping`.

## 2. Port states

| State | What happened | What it means |
| --- | --- | --- |
| **open** | Service accepted a connection (SYN-ACK) | Something is listening |
| **closed** | Host replied with RST | Host is up; nothing on that port |
| **filtered** | No reply, or an ICMP admin-prohibited | A firewall or filter is dropping it |
| **unfiltered** | Reachable, state unknown | Needs a different probe to classify |
| **open\|filtered** | Ambiguous (common with UDP) | No response either way — cannot distinguish |

"Filtered" is the most misread state in beginner reports. It does not mean "secure"; it means "the scan got no
answer", which may be a firewall, a rate limit, or a host that silently drops packets.

## 3. Choosing options deliberately

| Option | Effect | Use when | Cost |
| --- | --- | --- | --- |
| `-sT` | Full TCP connect via the OS | Unprivileged scanning, or through a proxy | More noise, slower |
| `-sS` | SYN scan (half-open) | Root available; speed matters | Requires privileges; some stacks log differently |
| `-sU` | UDP scan | DNS, DHCP, SNMP, NTP | Very slow; results ambiguous |
| `-p-` | All 65,535 ports | Completeness required | Time |
| `-p 22,80,443` | Named ports | Targeted check | Misses surprises |
| `--top-ports 100` | Common ports only | Fast first pass | Not an inventory |
| `-sV` | Service/version detection | Confirming what is listening | Extra traffic; can be inaccurate |
| `-O` | OS fingerprint | Rarely needed; often wrong in VMs | Noisy |
| `-T4` | Aggressive timing | Fast, reliable LAN | Can drop results; may trigger rate limits |
| `--reason` | Explain each state | Learning and reporting | Longer output |
| `-oA base` | Save normal, XML, grepable | Always, for evidence | Disk |

A defensible default for a lab:

```bash
sudo nmap -sT -p 1-1000 -sV --reason -oA ~/lab/level-2/lab-203/evidence/scan-initial 192.0.2.20
```

Read it as: full connect scan of the first thousand ports, version detection, reasons shown, all output formats
saved. Every flag has a justification you could say out loud.

## 4. netcat: the smallest useful tool

`netcat` (`nc`) moves bytes over TCP or UDP. It has no idea what the bytes mean, which is both its power and its
limitation.

```bash
# Listener on the lab address (target host)
nc -lvnp 4444

# Connect from the analyst host (on the lab network only)
nc -vz 192.0.2.20 4444
printf 'hello from kali\n' | nc -N 192.0.2.20 4444

# Small file transfer inside the lab
# receiver: nc -l 5555 > received.txt
# sender:   nc -N 192.0.2.20 5555 < send.txt
```

| Option | Meaning |
| --- | --- |
| `-l` | Listen |
| `-v` | Verbose |
| `-n` | No DNS lookups |
| `-p PORT` | Port (with `-l` on most variants) |
| `-z` | Zero-I/O scan (test only) |
| `-N` | Close after EOF (GNU netcat) |
| `-w N` | Timeout |

**Limitations to state in any report:** `nc` speaks raw bytes, cannot negotiate TLS, has no authentication, and
variant differences (`netcat-traditional` vs `netcat-openbsd` vs `ncat`) change flags. "It worked with `nc`" is
not a service inventory.

## 5. Verify, then document

The workflow that produces defensible findings:

```
discover → scan → detect version → verify by hand → classify → document
```

Verification examples:

```bash
# A web service
curl -sI http://192.0.2.20:8000/ | head -5

# An SSH service
nc -v 192.0.2.20 22 </dev/null | head -1

# Confirm what is actually listening
ssh learner@192.0.2.20 'ss -tlnp'
```

Then write the inventory as facts you verified, with the scanner's guess as an annotation:

| Port | Scanner guess | Verified? | Evidence | Notes |
| --- | --- | --- | --- | --- |
| 22 | OpenSSH 8.9 | Yes | banner via `nc`, `ss` on host | Key auth only |
| 8000 | http-alt | Yes | `curl -I` returned 200 | Python test server, lab only |

That table is the difference between an inventory and a screenshot.

---

## Practical exercises

### Exercise 1 — Discovery methods (15 minutes)

Run `nmap -sn --reason 192.0.2.0/24`, then `sudo nmap -sn -PR 192.0.2.0/24`. Compare which hosts appear and why.
Check `ip neigh` afterwards and explain the overlap.

### Exercise 2 — State interpretation (15 minutes)

Scan one host for a port you know is closed, one you know is open, and one filtered by a deliberate rule (if you
have one). Record the exact output line for each and the state it reported.

### Exercise 3 — Option justification (10 minutes)

Take `sudo nmap -A -T4 192.0.2.20`. List what `-A` enables, then rewrite the command using only the options you
can justify for a lab inventory. Compare run times and outputs.

### Exercise 4 — Verification loop (20 minutes)

Start a service on the target, scan it, and verify with `curl` and `ss`. Then stop the service and re-scan: note
how quickly the state changes, and what that implies about scan results as evidence of a point in time.

## Expected observations and verification

- ARP discovery finds every lab host; ICMP discovery may not.
- You can quote one line of output for open, closed, and filtered.
- Your scan command has a written justification for each flag.
- A service you started appears as open, and disappears after you stop it.
- Your inventory separates verified facts from scanner guesses.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| `-A -T4` by default | Copy-paste | Choose flags per question; record why |
| Treating "filtered" as "closed" | Both look like nothing | Read `--reason`; filtered means no answer |
| Trusting `-sV` absolutely | It guesses from banners | Verify with the service's own output |
| Scanning a public address "to test" | Curiosity | Never; the lab range exists for this |
| UDP results read as definitive | Silence is ambiguous | Report `open|filtered` honestly |
| Forgetting to save output | Terminal scrollback | `-oA` every time |
| Running `-sS` without root | Half-open needs privileges | Use `-sT`, or `sudo` deliberately |

## Review questions

1. Why is ARP discovery more reliable than ICMP on a local segment?
2. What does "filtered" actually tell you, and what does it not?
3. Why save results with `-oA` rather than copying terminal text?
4. What are two limitations of `netcat` as an enumeration tool?
5. Why must a scanner's version guess be verified independently?
6. What is the difference between a host being up and a service being available?

## Knowledge check

1. Which flag performs a TCP connect scan without raw sockets?
2. What does `open|filtered` mean for a UDP port?
3. Which command saves normal, XML, and grepable output?
4. Why does `-sV` sometimes report the wrong service?
5. What is the first verification step after a scanner reports an open port?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 2–4 if 2, 4 and 5 are uncertain.)*

## Summary

- Discovery method determines what you can see; blocked ICMP is not an absent host.
- Open, closed, and filtered mean different things, and `--reason` explains which you have.
- Choose scan options per question, and be able to justify every flag.
- `netcat` proves reachability and moves bytes; it is not an inventory tool.
- Verify every finding independently, then document facts and guesses separately.

## Next lesson

[CYB-204 · Packet Capture and Traffic Analysis](../04-packet-capture-and-analysis/index.md) — watching the
traffic your scans produce.

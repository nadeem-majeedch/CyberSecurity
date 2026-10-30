---
title: "LAB-203-02 · Port and Service Enumeration of a Local Target"
description: "Create known services on your own target host, enumerate them with nmap, and verify every finding independently."
module_code: CYB-203
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-203-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [nmap, enumeration, services, verification]
---

# LAB-203-02 · Port and Service Enumeration of a Local Target

## Prerequisites

The CYB-203 lesson and LAB-203-01's host inventory. `lab-ubuntu` reachable from `lab-kali` with SSH access,
because you start and stop the target services on that host yourself.

## Scenario and background

You control both ends of this exercise. On `lab-ubuntu` you will deliberately start a small, known set of
services, then enumerate them from `lab-kali` and compare what the scanner reports with what you actually
configured. This is the fastest way to learn a tool's blind spots: you know the ground truth.

The deliverable is a verified service inventory, not a scan dump.

## Learning objectives

By the end of this lab you can:

1. Start known services on a target and bind them to the lab address only.
2. Perform a TCP port scan with a defensible option set.
3. Identify service versions and verify each with an independent tool.
4. Classify findings as confirmed, probable, or unverified.
5. Document an inventory with evidence for every row.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| `nmap` | 7.94+ | On the analyst host |
| `python3` | 3.10+ | Test HTTP servers on the target |
| `ss`, `curl`, `nc` | standard | Verification |
| OpenSSH server | 8.9+ | Optional but recommended |

## Setup

On **`lab-ubuntu`** (target), start the services:

```bash
# A static HTTP service on a non-standard port, bound to the lab address
mkdir -p /tmp/lab203 && printf 'lab203 target\n' > /tmp/lab203/index.html
cd /tmp/lab203 && nohup python3 -m http.server 8000 --bind 192.0.2.20 >/tmp/lab203/http8000.log 2>&1 &

# A second service on 8080
cd /tmp/lab203 && nohup python3 -m http.server 8080 --bind 192.0.2.20 >/tmp/lab203/http8080.log 2>&1 &

# Confirm what is listening
ss -tlnp | grep -E '8000|8080'
```

**Why bind to `192.0.2.20`:** the services must be reachable from the analyst host on the lab segment, and must
not be exposed on any other interface. Binding to `0.0.0.0` would expose them everywhere, which is a mistake you
should see once and never repeat.

On **`lab-kali`**:

```bash
mkdir -p ~/lab/level-2/lab-203/evidence
cd ~/lab/level-2/lab-203
```

## Target addresses and lab topology

```
lab-kali 192.0.2.10  ──►  lab-ubuntu 192.0.2.20
                            :22   sshd (if installed)
                            :8000 python http.server
                            :8080 python http.server
                            :9    deliberately closed
```

## Numbered commands and actions

### 1. Fast pass: common ports

```bash
nmap -sT --top-ports 100 192.0.2.20 -oN evidence/scan-top100.txt
grep -E '^[0-9]+/' evidence/scan-top100.txt
```

**Expected:** `22/tcp open ssh` (if installed), `8000/tcp open http-alt`, `8080/tcp open http-proxy`.
**Note:** 8000 and 8080 may not be in the top-100 set; if they are missing, that is a lesson about "top ports"
being a popularity list, not a guarantee.

### 2. Full TCP sweep with reasons

```bash
sudo nmap -sS -p- --reason --min-rate 1000 192.0.2.20 \
  -oA evidence/scan-allports 2>/dev/null || nmap -sT -p- --reason 192.0.2.20 -oA evidence/scan-allports
grep -E '^[0-9]+/tcp' evidence/scan-allports.nmap
```

**Why `-p-`:** a deliberate inventory should not rely on a popularity list. On a lab host the scan takes seconds
to a minute; on a real network it would be planned differently.

**Why `--min-rate`:** bounded speed for a local scan. On a real engagement you would consider detection and
stability, not just speed.

### 3. Service and version detection

```bash
nmap -sV -sC -p 22,8000,8080 192.0.2.20 -oN evidence/scan-versions.txt
cat evidence/scan-versions.txt
```

**Expected** (versions vary):

```text
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
8000/tcp open  http    SimpleHTTPServer 0.6 (Python 3.10.12)
8080/tcp open  http    SimpleHTTPServer 0.6 (Python 3.10.12)
```

`-sC` runs the default script set. Read the script output; do not paste it into a report unread.

### 4. Verify each finding independently

```bash
curl -sI http://192.0.2.20:8000/ | head -3
printf 'HEAD / HTTP/1.0\r\n\r\n' | nc -w2 192.0.2.20 8080 | head -3
nc -vz -w2 192.0.2.20 9; echo "port 9 exit: $?"
ssh -o BatchMode=yes -o ConnectTimeout=2 learner@192.0.2.20 true 2>&1 | head -2
```

**Expected:** `curl` returns `200 OK`; `nc` returns an HTTP response from 8080; port 9 is refused or closed;
SSH either offers a banner or reports connection refused if not installed.

### 5. Classify and document

Create `evidence/service-inventory.md`:

| Port | State | Scanner says | Verified how | Classification | Notes |
| --- | --- | --- | --- | --- | --- |
| 22 | open | OpenSSH 8.9 | `nc` banner | Confirmed | Key auth recommended |
| 8000 | open | SimpleHTTPServer | `curl -I` 200 | Confirmed | Lab test server, no auth |
| 8080 | open | SimpleHTTPServer | `HEAD` via `nc` | Confirmed | Duplicate lab service |
| 9 | closed | — | `nc` refused | Confirmed closed | — |

Add a paragraph: **which scanner claim in this lab was a guess rather than a fact?** (Version strings are
banner-derived guesses; confirm with the service's own documentation or `ss -p` on the host.)

### 6. Re-scan after a change

```bash
# On the target
kill %1 2>/dev/null || pkill -f "http.server 8000"
# On the analyst
nmap -sT -p 8000 192.0.2.20 -oN evidence/scan-after-stop.txt
cat evidence/scan-after-stop.txt | grep 8000
```

**Expected:** the port is now closed. Record in the inventory that scan results describe a moment, not a system.

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `-sS` | SYN scan | Fast, requires root |
| `-sT` | Connect scan | Works unprivileged, noisier |
| `-p-` | All ports | Complete inventory |
| `--min-rate 1000` | Minimum packets per second | Bounded, predictable speed |
| `-sV` | Version detection | Service identification |
| `-sC` | Default scripts | Safe, non-destructive checks |
| `-oA` | All output formats | Evidence and later parsing |

## Expected observations

- The top-100 scan may miss the non-standard ports; the full sweep finds them.
- Version detection reports plausible banners, not ground truth.
- Independent verification confirms each service.
- Stopping a service changes the result on the next scan.
- `-sV` output includes an OS hint that may be wrong inside a VM — note it.

## Verification criteria

- [ ] Both target services confirmed listening on `192.0.2.20` only (`ss -tlnp`).
- [ ] Top-100 and full-sweep scans saved.
- [ ] Version scan saved and read.
- [ ] Every inventory row has an independent verification method.
- [ ] Post-change scan recorded.
- [ ] No target outside `192.0.2.0/24` scanned.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Ports show `closed` from analyst | Service bound to `127.0.0.1` | Rebind to `192.0.2.20` |
| `-sS` fails | No privileges | Use `sudo`, or fall back to `-sT` |
| Version detection times out | Server slow to respond, or `--min-rate` too high | Lower rate, increase `--host-timeout` |
| `nmap` reports "host seems down" | ICMP blocked and no port responded | Add `-Pn` **only** when you know the host is up |
| Scan takes minutes | `-p-` on a slow VM | Accept it, or scan a defined range and document the choice |
| `curl` succeeds but scan says closed | Scanned the wrong address | Check the target IP in both commands |

## Cleanup and restoration

```bash
# On the target: stop test services and remove data
pkill -f "http.server 8080" 2>/dev/null
pkill -f "http.server 8000" 2>/dev/null
rm -rf /tmp/lab203
ss -tlnp | grep -E '8000|8080' || echo "test services stopped"
```

Keep all evidence in `~/lab/level-2/lab-203/evidence/`.

## Questions and extension challenges

1. Why is "--top-ports" unsuitable as an inventory method?
2. Which inventory row is a guess rather than a verified fact, and how could you confirm it on the host?
3. What does the post-change scan demonstrate about the reliability of a scan report over time?
4. **Extension:** add SSH to the target, re-scan, and compare the banner your scan reports with
   `ssh -V` on the host. Explain any difference.
5. **Extension:** run the same scan with `-T2` and `-T4` and compare accuracy and duration.

## Related

- [Scanning Your Own Lab](01-scanning-your-lab.md)
- [LAB-203-03 · TCP and UDP Behaviour](lab-03-tcp-udp-behaviour.md)
- [System Inspection, Hardening and Reporting](../06-host-inspection-and-hardening/index.md)

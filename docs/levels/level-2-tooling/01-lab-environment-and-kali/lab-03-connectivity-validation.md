---
title: "LAB-201-03 · Validate Connectivity Between Lab Hosts"
description: "Produce a connectivity matrix proving the lab segment works between guests and is isolated from the internet."
module_code: CYB-201
level: 2
kind: lab
prerequisites: [CYB-201]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-201-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, connectivity, troubleshooting, evidence]
---

# LAB-201-03 · Validate Connectivity Between Lab Hosts

## Prerequisites

LAB-201-01 and LAB-201-02 complete: both hosts built, statically addressed on the same host-only network,
and snapshotted, so a failed row in the matrix can be undone in minutes.

## Scenario and background

Two hosts have addresses. Before you trust a scan or a capture, you must know exactly what can reach what.
This lab produces a connectivity matrix — a small table of deliberate tests with recorded outcomes — that
becomes the baseline for every later lab in the level.

The matrix is also the first piece of evidence you will keep in a lab notebook, so treat it as a deliverable,
not a warm-up.

## Learning objectives

By the end of this lab you can:

1. Run a fixed set of connectivity checks between two lab hosts.
2. Interpret exit codes and error messages for ICMP, TCP, and DNS.
3. Distinguish "unreachable", "filtered", "refused", and "resolved but no service".
4. Record results in a reproducible matrix with timestamps.
5. Recognise the three most common causes of a failed matrix row.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| `ip` | iproute2 5.15+ | Address and route inspection |
| `ping` | iputils | ICMP echo |
| `traceroute` | traceroute 2.1+ | Path visibility (may be a single hop) |
| `dig` | dnsutils | Name resolution |
| `nc` | netcat | TCP port probe |
| `ss` | iproute2 | Listening sockets on the target |

## Setup

- `lab-kali` at `192.0.2.10/24`, `lab-ubuntu` at `192.0.2.20/24`, both on the same host-only network.
- An evidence folder: `mkdir -p ~/lab/level-2/lab-201/evidence`.
- On `lab-ubuntu`, start a temporary listener for the TCP test:

```bash
python3 -m http.server 8080 --bind 192.0.2.20
```

Use `--bind 192.0.2.20` (the lab address), not `127.0.0.1`, so the analyst host can reach it. **Do not** bind
to `0.0.0.0` on any interface that is not the isolated lab adapter.

## Target addresses and lab topology

```
lab-kali 192.0.2.10/24  ──────►  lab-ubuntu 192.0.2.20:8080   (allowed)
lab-kali 192.0.2.10/24  ──────✕  8.8.8.8                       (must fail)
```

## Numbered commands and actions

Run the following on `lab-kali`. Save everything with `tee`.

### 1. Layer 1–2: interface and link

```bash
ip -br link
ip -br addr
```

### 2. Layer 3: route selection

```bash
ip route
ip route get 192.0.2.20
ip route get 8.8.8.8
```

**Interpretation:** the first should select your lab interface; the second should fail with "Network is
unreachable" if there is genuinely no default route.

### 3. ICMP reachability

```bash
ping -c 2 -W 2 192.0.2.20; echo "peer exit: $?"
ping -c 1 -W 2 8.8.8.8; echo "internet exit: $?"
```

### 4. Path (single hop expected)

```bash
traceroute -n -m 3 192.0.2.20
```

On a host-only segment you will usually see one hop, or `!H`. That is correct: there is no router.

### 5. TCP service test

```bash
nc -vz -w 2 192.0.2.20 8080; echo "tcp 8080 exit: $?"
nc -vz -w 2 192.0.2.20 22;   echo "tcp 22 exit: $?"
```

**Interpretation:** `succeeded` means something is listening; `Connection refused` means the host is reachable
and nothing is bound; a timeout means filtering or a wrong address.

### 6. DNS behaviour

```bash
dig +short 192.0.2.20        # reverse lookup, may be empty
getent hosts lab-ubuntu      # local name resolution, may be empty
dig +short example.com       # must fail or time out in an isolated lab
```

### 7. Full matrix with timestamps

```bash
{
  echo "== connectivity matrix =="
  echo "date: $(date -Is)  host: $(hostname)"
  echo "peer=$(ping -c2 -W2 192.0.2.20 >/dev/null 2>&1 && echo OK || echo FAIL)"
  echo "tcp8080=$(nc -z -w2 192.0.2.20 8080 >/dev/null 2>&1 && echo OK || echo FAIL)"
  echo "tcp22=$(nc -z -w2 192.0.2.20 22 >/dev/null 2>&1 && echo OK || echo FAIL)"
  echo "dns=$(dig +short example.com >/dev/null 2>&1 && echo RESOLVED || echo BLOCKED)"
  echo "internet=$(ping -c1 -W2 8.8.8.8 >/dev/null 2>&1 && echo REACHABLE || echo BLOCKED)"
} | tee ~/lab/level-2/lab-201/evidence/connectivity-matrix.txt
```

**Expected:**

```text
peer=OK
tcp8080=OK
tcp22=FAIL
dns=BLOCKED
internet=BLOCKED
```

`tcp22=FAIL` is expected if you have not started SSH on the target; do not "fix" it by installing something.

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `ping -c 2 -W 2` | Two attempts, 2-second wait | Bounded, scriptable |
| `nc -vz -w 2 HOST PORT` | Verbose, zero-I/O scan, 2s timeout | Tests reachability of one port without sending data |
| `traceroute -n -m 3` | Numeric output, max 3 hops | Avoids DNS delays; a lab has no long path |
| `dig +short` | Answer only | Readable output for a matrix |
| `ip route get ADDR` | Show the route decision | Proves which interface would be used |

## Expected observations

- `ip route get 8.8.8.8` reports `Network is unreachable`.
- Peer ICMP succeeds; internet ICMP fails.
- The TCP test to 8080 succeeds while SSH fails or is refused.
- Reverse DNS for a lab address is empty — normal on an isolated segment.
- The matrix file contains five named results with a timestamp.

## Verification criteria

- [ ] Matrix file saved with date and hostname.
- [ ] Peer reachability is `OK`.
- [ ] Internet is `BLOCKED` (or `FAIL`), and you can quote the exit code.
- [ ] You explained the difference between "refused" and "timeout" using your own output.
- [ ] No scan was run against any address outside `192.0.2.0/24`.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| All rows fail | Wrong adapter or subnet | Re-check `ip -br addr` on both hosts |
| `ping` works, TCP times out | Listener bound to `127.0.0.1`, or firewall | Rebind to `192.0.2.20`; check `ss -tlnp` |
| `traceroute` hangs | It is waiting for DNS on a blocked resolver | Use `-n` |
| `internet=REACHABLE` | NAT adapter still attached | Remove it; this invalidates the lab |
| `nc: command not found` | Netcat not installed | `sudo apt install -y netcat-traditional` |
| Matrix shows `dns=RESOLVED` | A resolver is reachable (NAT or host DNS proxy) | Investigate before continuing: the lab should be isolated |

## Cleanup and restoration

```bash
# On lab-ubuntu: stop the temporary listener
kill %1 2>/dev/null || pkill -f "http.server 8080"
```

Keep `connectivity-matrix.txt` — later labs compare against it when results look wrong. Revert either VM to its
baseline only if you changed network configuration during troubleshooting.

## Questions and extension challenges

1. Why is `tcp22=FAIL` not a problem for this lab, and what would it mean in a real assessment?
2. What is the practical difference between a timeout and a refused connection when you are diagnosing?
3. **Extension:** enable SSH on the target, re-run the matrix, and explain which row changed and why.
4. **Extension:** add a row testing UDP (`nc -u -z -w2`) and explain why UDP results are less conclusive than
   TCP results.

## Related

- [Preparing the Analyst Environment](01-lab-environment.md)
- [LAB-201-02 · Configure Host-Only Networking](lab-02-host-only-network.md)
- [Host Discovery and Service Enumeration](../03-host-discovery-and-enumeration/index.md)

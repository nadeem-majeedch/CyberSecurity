---
title: "LAB-203-04 · Netcat for Controlled Local Demonstrations"
description: "Use netcat as a listener, a client, a banner reader, and a file transfer tool — inside your own lab only."
module_code: CYB-203
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-203-04]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [netcat, tcp, udp, transfer]
---

# LAB-203-04 · Netcat for Controlled Local Demonstrations

## Scenario and background

`netcat` is the smallest useful network tool: it moves bytes between two endpoints and understands nothing about
their meaning. That makes it ideal for demonstrating what a connection actually is — and dangerous in the wrong
hands, because it can also be used to move data out of a network or to open a shell.

This lab uses it the way a professional does in a lab: to prove reachability, read a banner, transfer a file, and
understand what a raw TCP session looks like. Every action is confined to `192.0.2.0/24`.

!!! warning "Scope and intent"
    You will not use `netcat` to obtain a shell on any host, and you will not connect to any address outside
    your lab. If you are asked to demonstrate a "reverse shell" in a job interview, the correct answer is a
    discussion of detection and prevention, not a live demo against someone else's machine.

## Learning objectives

By the end of this lab you can:

1. Start and connect to a TCP listener inside the lab.
2. Read a service banner and explain what it reveals and conceals.
3. Transfer a small file with `netcat` and verify integrity with a hash.
4. Test a port without sending application data.
5. Explain `netcat`'s limitations and when a purpose-built tool is the better choice.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| `nc` | netcat-traditional or openbsd | Flags differ; check `nc -h` |
| `sha256sum` | coreutils | Integrity check |
| `tcpdump` | 4.99+ | Optional: watch the session |

## Setup

```bash
mkdir -p ~/lab/level-2/lab-203/evidence
# Both hosts, same path for convenience
```

Check which variant you have, and note it — this is a real source of "it does not work" reports:

```bash
nc -h 2>&1 | head -3
update-alternatives --display nc 2>/dev/null | head -5 || echo "single variant installed"
```

## Target addresses and lab topology

```
lab-ubuntu 192.0.2.20  ── listener on :4444 (TCP)
lab-kali   192.0.2.10  ── client
```

## Numbered commands and actions

### 1. Listener and client

On **`lab-ubuntu`**:

```bash
nc -lvnp 4444
```

On **`lab-kali`**:

```bash
printf 'hello from the analyst host\n' | nc -N 192.0.2.20 4444
```

**Expected:** the text appears in the listener terminal, and the client exits. On `netcat-traditional` you may
need `-q 1` instead of `-N`; the effect is the same (close after sending).

### 2. Port test without sending data

```bash
nc -vz -w 2 192.0.2.20 4444; echo "exit: $?"
nc -vz -w 2 192.0.2.20 4445; echo "exit: $?"
```

**Expected:** `succeeded!`/`open` and exit 0 for 4444; `Connection refused` and a non-zero exit for 4445. This is
the same check you ran in LAB-201-03, now with a listener you control.

### 3. Banner reading

On **`lab-ubuntu`**, if OpenSSH is installed:

```bash
sudo systemctl status ssh --no-pager | head -3
```

On **`lab-kali`**:

```bash
printf '\n' | nc -w2 192.0.2.20 22 | head -1
```

**Expected:** something like `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.10`. **Interpretation:** the banner reveals
protocol version and distribution — useful for inventory, insufficient for a vulnerability conclusion. Version
strings can be changed, and distributions backport fixes without changing the banner.

### 4. File transfer with integrity check

On **`lab-ubuntu`**:

```bash
dd if=/dev/urandom of=/tmp/transfer.bin bs=1k count=64 2>/dev/null
sha256sum /tmp/transfer.bin | tee /tmp/transfer.sha256
nc -lvnp 5555 > /tmp/received.bin
```

On **`lab-kali`**:

```bash
nc -N 192.0.2.20 5555 < /tmp/kali-transfer.bin    # create a file first (see below)
```

Create the file on the analyst host, then compare:

```bash
dd if=/dev/urandom of=/tmp/kali-transfer.bin bs=1k count=64 2>/dev/null
sha256sum /tmp/kali-transfer.bin
```

**Expected:** after the listener closes, `sha256sum /tmp/received.bin` on the target matches the value from the
analyst host. Any difference means truncation — `netcat` gives you no delivery guarantee beyond TCP's, and
process timing can cut a transfer short.

### 5. Two-way session (chat)

Terminal 1 on the target: `nc -lvnp 6666`
Terminal 2 on the analyst: `nc 192.0.2.20 6666`
Type in either terminal; text appears in the other. Exit with `Ctrl-C` on both.

**Why this matters:** it is the clearest demonstration that a TCP connection is just two byte streams. It is also
the mechanism behind "reverse shell" tooling — which is exactly why defenders monitor for it.

### 6. Watch it on the wire (optional)

On the analyst host, in a third terminal:

```bash
sudo tcpdump -ni any -c 20 'host 192.0.2.20 and port 6666'
```

Repeat the chat. You will see the handshake, then data packets, then FIN/RST on exit.

### 7. Document the limitations

Create `evidence/netcat-limitations.md`:

| Limitation | Consequence |
| --- | --- |
| No encryption | Anything sent is readable on the wire |

Add at least four more rows (no authentication, no framing, variant flag differences, no retry/resume, no
integrity check, easy to misuse).

## Important command options explained

| Option | Meaning | Variant note |
| --- | --- | --- |
| `-l` | Listen | Both variants |
| `-v` | Verbose | Both |
| `-n` | No DNS resolution | Both |
| `-p PORT` | Port with `-l` | Traditional uses `-p`; OpenBSD accepts `PORT` positionally |
| `-z` | Zero-I/O scan | Both |
| `-N` | Shutdown after EOF | OpenBSD/ncat; traditional uses `-q 1` |
| `-w N` | Timeout seconds | Both |

## Expected observations

- A listener accepts one connection and prints what was sent.
- `-z` distinguishes open from refused without application data.
- The SSH banner identifies protocol and distribution, not patch level.
- A 64 KB transfer completes and matches by hash.
- A raw TCP session is symmetric: both sides can send at any time.

## Verification criteria

- [ ] Listener and client demonstration completed and recorded.
- [ ] Open and refused port tests both shown with exit codes.
- [ ] Banner captured and interpreted with its limitation stated.
- [ ] File transferred and hash compared.
- [ ] `netcat-limitations.md` has at least five rows.
- [ ] Nothing outside `192.0.2.0/24` was contacted.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `nc: invalid option -- 'N'` | Traditional variant | Use `-q 1` |
| Listener exits immediately | `-l` missing, or port in use | Check the command; `ss -tlnp` for the port |
| Transfer truncated | Sender closed before receiver flushed | Use `-q 1`, or verify with hashes |
| `Connection refused` on a listener | Listener bound to `127.0.0.1` | Bind to `0.0.0.0` inside the lab, or start without `-s` |
| Banner empty | Service waits for client input first | Send a newline, or use `ssh -o BatchMode=yes` |
| `tcpdump` sees nothing | Wrong interface | `-i any` |

## Cleanup and restoration

```bash
pkill -f "nc -lvnp 4444" 2>/dev/null
pkill -f "nc -lvnp 5555" 2>/dev/null
pkill -f "nc -lvnp 6666" 2>/dev/null
rm -f /tmp/transfer.bin /tmp/received.bin /tmp/kali-transfer.bin /tmp/transfer.sha256
ss -tlnp | grep -E '4444|5555|6666' || echo "listeners stopped"
```

If you started a listener on `0.0.0.0` for the lab, confirm it is gone — a forgotten listener is exactly the
kind of unintended exposure this course keeps warning about.

## Questions and extension challenges

1. Why does `netcat` not guarantee a complete file transfer even though TCP does?
2. What does the SSH banner tell you, and what does it not tell you?
3. Why is "reverse shell" tooling detectable, and what would you monitor for?
4. **Extension:** replace `netcat` with `socat` for the file transfer and note which problems it solves.
5. **Extension:** write a Bash loop that tests a list of ports on the lab host and prints a clean table, with a
   scope guard rejecting anything outside `192.0.2.0/24`.

## Related

- [Scanning Your Own Lab](01-scanning-your-lab.md)
- [LAB-203-03 · TCP and UDP Behaviour](lab-03-tcp-udp-behaviour.md)
- [OpenSSH and Secure Remote Administration](../05-ssh-secure-administration/index.md)

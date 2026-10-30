---
title: "Level 2 Module Quizzes — Tooling and Lab Craft"
description: "Thirty self-check items across CYB-201 to CYB-206: lab build, scripting, enumeration, packet capture, SSH and host assessment."
module_code: ASM-L2
level: 2
kind: assessment
prerequisites: [CYB-201]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, quiz, level-2, enumeration, packet-capture]
---

# Level 2 Module Quizzes

Five items per module, six modules, thirty items. Everything here assumes the lab built in
[CYB-201](../levels/level-2-tooling/01-lab-environment-and-kali/index.md): an analyst host and at least one
target, on an isolated network.

**Protocol.** Attempt on paper with nothing open. Then mark against the [Level 2 answer key](level-2-key.md),
record right / wrong / right-for-the-wrong-reason, and read every explanation. Target 4 of 5 per module.

A note on scope for every item below: **the only permitted target is your own lab.** If a question describes a
target you do not own, the correct answer always begins with "I would not test that".

---

## CYB-201 · Lab Environment, Kali and Network Foundations

**Q201.1** (MCQ) You have configured static addresses on both VMs, but the analyst host cannot reach the
target. Which check comes first?

- A. Reinstall the target's network service
- B. Confirm both interfaces are attached to the same virtual network and are up, with addresses in the same
  subnet
- C. Disable the host firewall on your workstation
- D. Change the target's port to 8080

**Q201.2** (MCQ) Which command shows the IP addresses currently assigned to each interface?

- A. `ip route`
- B. `ip addr`
- C. `ss -ltnp`
- D. `arp -a`

**Q201.3** (MCQ) A service is running on the target, but a connection from the analyst host is refused. `ss
-ltnp` on the target shows `127.0.0.1:8080`. What is the most likely cause?

- A. The service is bound to loopback only
- B. The analyst host has the wrong default gateway
- C. The target's disk is full
- D. The service needs a DNS name

**Q201.4** (Short) Name the three connectivity failures this module says to diagnose first, and one check for
each.

**Q201.5** (Scenario) Your lab address register says the target is `10.10.10.20`. `ping` succeeds, but `nmap -p
22,80,443 10.10.10.20` reports all ports filtered. The target's `ss -ltn` shows 22 and 80 listening on
`0.0.0.0`. Give two explanations and the check that distinguishes them.

---

## CYB-202 · Bash, Python and Git for Lab Work

**Q202.1** (MCQ) What does `set -euo pipefail` change in a Bash script?

- A. It enables verbose output and logging to a file
- B. It exits on error, errors on unset variables, and makes a failing command in a pipeline fail the pipeline
- C. It runs the script as root
- D. It quotes all variables automatically

**Q202.2** (MCQ) Why should a script that changes system state default to a dry-run mode?

- A. Dry-run is faster than the real operation
- B. It lets the operator see the intended actions and targets before anything is changed
- C. It satisfies the package manager's requirements
- D. It avoids the need for input validation

**Q202.3** (MCQ) A developer commits an API key, then deletes the line in a later commit. What is required?

- A. Nothing: the key is no longer in the current file
- B. Rotate the key, because it remains in Git history, and remove the history from any shared copy
- C. Add the file to `.gitignore` and continue
- D. Change the key's variable name

**Q202.4** (Short) A script deletes files matching a user-supplied pattern. List three validations it needs
before it deletes anything.

**Q202.5** (Scenario) Your Python parser crashes with `KeyError: 'src_ip'` on one line of a 5,000-line log, and
the run produces no output. State the design change and what the script should report at the end.

---

## CYB-203 · Host Discovery and Service Enumeration

**Q203.1** (MCQ) Which Nmap option performs host discovery without a port scan?

- A. `-sV`
- B. `-sn`
- C. `-sU`
- D. `-O`

**Q203.2** (MCQ) A scan reports a port as `filtered`. What does that mean?

- A. The port is open but the service is not responding
- B. No response was received, consistent with a packet filter dropping the probe
- C. The host is down
- D. The service rejected the connection with a reset

**Q203.3** (MCQ) A scan reports `22/tcp open ssh OpenSSH 9.6`. What is still required before recording "SSH
9.6" in an inventory?

- A. Nothing; Nmap's version detection is authoritative
- B. Independent confirmation, such as a banner grab or the service's own version output
- C. A second scan with `-O`
- D. Root privileges

**Q203.4** (Short) Why does "open" from a scanner need verification before it becomes a finding?

**Q203.5** (Scenario) `nmap -sU -p 53,123,161 10.10.10.20` reports all three as `open|filtered`. Explain the
ambiguity, why UDP produces it, and how you would narrow it down.

---

## CYB-204 · Packet Capture and Traffic Analysis

**Q204.1** (MCQ) What is the difference between a capture filter and a display filter?

- A. Capture filters are for Wireshark and display filters are for tcpdump
- B. A capture filter decides what is recorded; a display filter decides what is shown from what was recorded
- C. They are interchangeable
- D. Capture filters can only match IP addresses

**Q204.2** (MCQ) Which BPF expression captures traffic to or from `10.10.10.20` on port 443?

- A. `tcp.port == 443 and ip.addr == 10.10.10.20`
- B. `host 10.10.10.20 and port 443`
- C. `-f "443"`
- D. `port 443 or host 10.10.10.20`

**Q204.3** (MCQ) Which information remains visible in a capture of a TLS 1.3 connection?

- A. The full HTTP request and response
- B. The server name in the ClientHello, IP addresses, ports, and timing
- C. The session keys
- D. Nothing at all

**Q204.4** (Short) State four things you must record when a capture is evidence.

**Q204.5** (Scenario) A capture shows `SYN`, `SYN/ACK`, `ACK`, then an immediate `RST` from the server before
any application data. What happened, and which two alternative explanations would you rule out with what
evidence?

---

## CYB-205 · OpenSSH and Secure Remote Administration

**Q205.1** (MCQ) What permissions should a private key file have, and why?

- A. `644`, so the SSH client can read it
- B. `600`, so only the owner can read it, since the key is the credential
- C. `777`, so any tool can use it
- D. `400` and owned by root, always

**Q205.2** (MCQ) What is the difference between `authorized_keys` and `known_hosts`?

- A. `authorized_keys` holds keys allowed to log in to this account; `known_hosts` holds host keys this client
  has seen
- B. They are the same file in different locations
- C. `authorized_keys` is on the client; `known_hosts` is on the server
- D. `known_hosts` stores passwords

**Q205.3** (MCQ) Before reloading `sshd` with a hardened configuration, what should you do?

- A. Reboot the server
- B. Validate with `sshd -t`, and keep an existing session open as a fallback
- C. Delete `authorized_keys` to test password login
- D. Change the port to 22

**Q205.4** (Short) Why are `PermitRootLogin no` and `PasswordAuthentication no` worth more together than
either alone?

**Q205.5** (Scenario) After a configuration change, SSH connections are refused and you have no session. You
have console access to the VM. State your recovery steps and the two practices that would have prevented the
outage.

---

## CYB-206 · Host Inspection and Hardening Assessment

**Q206.1** (MCQ) Lynis reports a hardening index of 62 and 40 suggestions. How should that be interpreted?

- A. The host is 62% secure
- B. The index is a rough comparative score; the suggestions must be triaged by risk, and many will not apply
- C. All 40 suggestions must be implemented
- D. The host has 40 vulnerabilities

**Q206.2** (MCQ) Which observation is a defensible finding rather than scanner noise?

- A. "Lynis suggests installing a file-integrity tool"
- B. "`/etc/shadow` is world-readable"
- C. "The kernel is not the newest available"
- D. "The host has no intrusion detection system"

**Q206.3** (MCQ) A service listens on `0.0.0.0:3306`. What does this mean?

- A. It accepts connections on every interface and address, not only loopback
- B. It is bound to IPv6 only
- C. It is limited to the local host
- D. It is firewalled by default

**Q206.4** (Short) You have two findings: an unused FTP service running as root, and world-readable log files
containing usernames. Rank them and justify the order in one sentence each.

**Q206.5** (Scenario) A colleague's report lists "critical: outdated PHP" with no version, no evidence and no
remediation. Rewrite it as a finding that would survive review: state the four fields it must contain.

---

## Troubleshooting exercises

**T206.1** Nmap reports port 80 open on the target, `curl` returns `Connection reset by peer`, and the target's
`ss -ltnp` shows nothing on port 80. Explain how all three observations can be true.

**T206.2** A capture file is 4 GB and Wireshark takes minutes to open it. Describe two changes to the capture
approach, and one thing you must not do to the original file.

**T206.3** You are asked to harden a host you did not build, with no snapshot and no console access. State the
first three actions, and why the usual "change it and reload" advice is unsafe here.

---

## Practical challenges

| Module | Challenge | Where |
| --- | --- | --- |
| CYB-201 | Record a lab register and connectivity matrix that a peer could reproduce | [LAB-201-03](../levels/level-2-tooling/01-lab-environment-and-kali/lab-03-connectivity-validation.md) |
| CYB-202 | Write a Bash check with strict mode and a non-zero exit on failure | [LAB-202-01](../levels/level-2-tooling/02-bash-python-git/lab-01-bash-security-check.md) |
| CYB-203 | Produce an inventory that separates confirmed services from scanner guesses | [LAB-203-02](../levels/level-2-tooling/03-host-discovery-and-enumeration/lab-02-service-enumeration.md) |
| CYB-204 | Extract DNS, handshake, HTTP and TLS metadata from one capture, then hash and name it as evidence | [LAB-204-03](../levels/level-2-tooling/04-packet-capture-and-analysis/lab-03-protocol-analysis.md) |
| CYB-205 | Harden `sshd` and prove you can still authenticate, without locking yourself out | [LAB-205-02](../levels/level-2-tooling/05-ssh-secure-administration/lab-02-harden-sshd.md) |
| CYB-206 | Turn a Lynis run into three prioritised, evidenced findings | [LAB-206-02](../levels/level-2-tooling/06-host-inspection-and-hardening/lab-02-lynis-assessment.md) |

---

## Next

- [Level 2 answer key](level-2-key.md)
- [Level 2 integrated assessment](level-2-assessment.md) — enumerate and assess a lab host under time pressure
- [Level 2 overview](../levels/level-2.md)

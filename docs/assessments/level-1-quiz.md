---
title: "Level 1 Module Quizzes — Foundations"
description: "Seventy-five self-check items across CYB-101 to CYB-115: multiple choice, short answer, scenarios and troubleshooting, with answers on a separate key page."
module_code: ASM-L1
level: 1
kind: assessment
prerequisites: [CYB-101]
estimated_minutes: 180
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, quiz, level-1, foundations]
---

# Level 1 Module Quizzes

Five items per module: three multiple-choice, one short answer, one scenario. Fifteen modules, seventy-five
items, roughly three hours if you write full sentences.

**Protocol.** Attempt all five items for a module on paper with nothing open. Then open the
[Level 1 answer key](level-1-key.md), mark each as correct, wrong, or *right for the wrong reason*, and
read every explanation. Target **4 of 5 with no right-for-the-wrong-reason answers**. Retake at seven days.

A quiz is a sample, not a measurement. The labs are where the level is actually earned.

---

## CYB-101 · Introduction to Cybersecurity

**Q101.1** (MCQ) Which statement best explains why defenders talk about asymmetry?

- A. Attackers have better tools than defenders can buy.
- B. An attacker needs one unmitigated path in; a defender must cover every path, every time.
- C. Defenders must patch faster than vendors release advisories.
- D. Attackers only target high-value organisations, so most defenders are safe.

**Q101.2** (MCQ) Which set names the four broad activities of security practice?

- A. Predict, prevent, detect, respond
- B. Scan, exploit, report, remediate
- C. Identify, purchase, deploy, audit
- D. Encrypt, hash, sign, verify

**Q101.3** (MCQ) A team writes the access-control policy, decides which risks the organisation will accept,
and commissions an audit. Which category of work is this?

- A. Offensive security
- B. Security engineering
- C. Governance, risk and compliance
- D. Incident response

**Q101.4** (Short) State the authorization rule this course requires in one sentence, and name the two
properties that make permission adequate rather than merely friendly.

**Q101.5** (Scenario) A friend who runs a small business asks you to "have a quick look at whether the website
is hackable" over the weekend. You have known him for years. In two or three sentences, say what must exist
before you test anything, and what you would do with a serious finding.

---

## CYB-102 · CIA Triad, Security Principles and Risk

**Q102.1** (MCQ) A payroll clerk can edit their own salary record through the staff portal. Which property is
primarily violated?

- A. Confidentiality
- B. Integrity
- C. Availability
- D. Non-repudiation

**Q102.2** (MCQ) An intern's account can read only the shared drive for their own team, and nothing else on the
file server. Which design principle does this most directly apply?

- A. Defence in depth
- B. Fail-safe defaults
- C. Least privilege
- D. Separation of duties

**Q102.3** (MCQ) A legacy stock system cannot be patched. The business keeps it running behind a firewall,
isolated from the internet, and records the decision with its reasoning. Which risk treatment is this?

- A. Avoidance
- B. Mitigation with a compensating control, with the residual risk formally accepted
- C. Transference
- D. Elimination

**Q102.4** (Short) Distinguish a *threat* from a *vulnerability* in two sentences, using one concrete example
that contains both.

**Q102.5** (Scenario) You have two findings on a small network: an unpatched internet-facing server with a
known remote code execution flaw, and a laptop without disk encryption. Rank them by risk and justify the
order using likelihood and impact. State one assumption you made.

---

## CYB-103 · Threats, Vulnerabilities, Exploits and Controls

**Q103.1** (MCQ) A weakness exists in the design of a protocol itself, so no vendor patch can remove it
without changing the protocol. Which category is this?

- A. Implementation vulnerability
- B. Configuration vulnerability
- C. Design vulnerability
- D. Operational vulnerability

**Q103.2** (MCQ) What makes a vulnerability a *zero-day*?

- A. It affects software from a vendor that does not publish advisories.
- B. It is exploited before a fix is generally available.
- C. It was discovered by a researcher rather than a criminal.
- D. It requires no user interaction to exploit.

**Q103.3** (MCQ) A badge-controlled door and a receptionist who checks visitors against a list are best
described as which control types?

- A. Physical preventive, and administrative preventive
- B. Technical detective, and physical deterrent
- C. Physical deterrent, and technical corrective
- D. Administrative detective, and technical preventive

**Q103.4** (Short) Give two reasons why "patch everything immediately" is not a workable vulnerability
management strategy, even where patching is possible.

**Q103.5** (Scenario) A small clinic is losing credentials to phishing. Propose three controls that work at
different points, and label each as preventive, detective, or corrective.

---

## CYB-104 · Threat Modeling and Attack Surfaces

**Q104.1** (MCQ) An attacker edits the hidden `price` field in a checkout form before submitting it. Which
STRIDE category does this represent?

- A. Spoofing
- B. Tampering
- C. Repudiation
- D. Information disclosure

**Q104.2** (MCQ) What is a trust boundary in a data-flow diagram?

- A. The firewall rule that blocks incoming traffic
- B. Any point where data or control passes between components with different levels of trust or privilege
- C. The line between production and test environments
- D. The outer edge of the network diagram

**Q104.3** (MCQ) Which change genuinely *reduces* attack surface, rather than adding a control in front of it?

- A. Adding a web application firewall in blocking mode
- B. Disabling an unused administrative interface and removing its package
- C. Increasing the password minimum length to 16
- D. Enabling verbose error logging

**Q104.4** (Short) Name the four questions of the threat-modelling framework used in this course.

**Q104.5** (Scenario) A diagram shows a browser, an API, and a database. Name the two trust boundaries and
state one realistic threat at each, with the STRIDE letter you would assign.

---

## CYB-105 · Ethics, Authorization, Responsible Disclosure and Cyber Law

**Q105.1** (MCQ) Which of these is adequate authorization to test a system?

- A. A verbal "sure, go ahead" from the IT manager
- B. An email from a marketing colleague who uses the system daily
- C. A signed scope from the system owner naming the targets, the window, the permitted techniques, and the contact
- D. A public bug-bounty page that lists the vendor's name

**Q105.2** (MCQ) You find a vulnerability in a vendor product during authorized lab work. What is the first
correct action?

- A. Publish a proof of concept so users can defend themselves
- B. Report it privately to the vendor with reproduction steps and agree a disclosure timeline
- C. Post it in a community forum to check whether others can reproduce it
- D. Nothing, because it is not your system

**Q105.3** (MCQ) Which statement about authorization and intent is correct?

- A. Good intentions make unauthorized access lawful if no damage occurs.
- B. Authorization comes from the asset owner, and intent does not create it.
- C. Authorization is implied by finding a vulnerability.
- D. Testing from outside the country changes the legal position.

**Q105.4** (Short) List three elements that every scope statement must contain, and explain why an exclusion
list matters as much as an inclusion list.

**Q105.5** (Scenario) A bug-bounty programme scopes `app.example.com` and explicitly excludes
`staging.example.com`. While testing the in-scope host, you notice a staging subdomain leaking session tokens.
What do you do, in order?

---

## CYB-106 · Hardware, Operating Systems, Files, Processes and Permissions

**Q106.1** (MCQ) Why is the boundary between kernel space and user space a security boundary?

- A. Because kernel code is written by more experienced programmers
- B. Because the kernel mediates access to memory, devices and other processes, so a bug there defeats every
  in-process protection
- C. Because user-space programs run more slowly
- D. Because the kernel is always digitally signed

**Q106.2** (MCQ) A file has mode `-rw-r-----`, owner `alice`, group `auditors`. Who can read it?

- A. Everyone
- B. Only alice
- C. alice and members of `auditors`
- D. alice, `auditors`, and root only after changing ownership

**Q106.3** (MCQ) Which permission mistake most directly creates remote-code-execution risk on a web server?

- A. A log directory that is group-readable
- B. An upload directory that is writable by the web user and also permits script execution
- C. A configuration file owned by root and readable only by root
- D. A home directory with mode `700`

**Q106.4** (Short) Explain what the setuid bit does and give one reason it is a security risk.

**Q106.5** (Scenario) `ps aux` shows a process owned by `www-data` running `/bin/sh -c ...`. List three
questions you would ask about that process before deciding whether it is suspicious.

---

## CYB-107 · Networking Fundamentals and the OSI/TCP-IP Models

**Q107.1** (MCQ) A switch forwards frames using MAC addresses. At which OSI layer does it primarily operate?

- A. Layer 1
- B. Layer 2
- C. Layer 3
- D. Layer 4

**Q107.2** (MCQ) What is the protocol data unit at the transport layer?

- A. Frame
- B. Packet
- C. Segment (TCP) or datagram (UDP)
- D. Bit

**Q107.3** (MCQ) Which identifier selects the service or application on a host?

- A. MAC address
- B. IP address
- C. Port number
- D. Subnet mask

**Q107.4** (Short) Explain encapsulation in three sentences, naming the PDU at each step from application data to
frame.

**Q107.5** (Scenario) `nc -vz 10.10.10.20 443` reports the port is open, but the browser fails to load the
site. Give two plausible explanations that are consistent with an open port.

---

## CYB-108 · IP Addressing, Subnets and Core Protocols

**Q108.1** (MCQ) What is the broadcast address of `192.168.1.0/26`?

- A. `192.168.1.0`
- B. `192.168.1.63`
- C. `192.168.1.64`
- D. `192.168.1.255`

**Q108.2** (MCQ) A Windows host reports the address `169.254.37.12`. What does this most likely indicate?

- A. A static address on the corporate VLAN
- B. A link-local address assigned because DHCP did not answer
- C. A public address allocated by the ISP
- D. A loopback alias

**Q108.3** (MCQ) Which statement about TLS is accurate?

- A. TLS hides the destination IP address from the network
- B. TLS provides confidentiality and integrity in transit, and authenticates the server, but does not protect
  data at rest
- C. TLS prevents an attacker with the session key from reading the traffic
- D. TLS replaces the need for application-level authorization

**Q108.4** (Short) For each symptom, name the evidence that distinguishes it: "the name does not resolve",
"the port is closed", "the service is broken".

**Q108.5** (Scenario) `ping 10.10.10.5` succeeds; `ping db.lab.local` fails; `dig db.lab.local` returns
NXDOMAIN. State the fault domain and the next two commands you would run.

---

## CYB-109 · Linux Command-Line Fundamentals

**Q109.1** (MCQ) What does `chmod 640 report.txt` grant?

- A. Owner read/write, group read, others none
- B. Owner read/write/execute, group read, others none
- C. Owner read/write, group read/write, others read
- D. Owner read only, group read, others none

**Q109.2** (MCQ) With `umask 027`, what permissions will a newly created regular file normally receive?

- A. `640`
- B. `660`
- C. `750`
- D. `600`

**Q109.3** (MCQ) Which command maps a listening TCP port to the process that owns it?

- A. `ss -ltnp`
- B. `ip addr show`
- C. `ps aux | grep tcp`
- D. `netstat -rn`

**Q109.4** (Short) Explain the difference between an absolute and a relative path, give one example of each, and
say when the absolute form is safer.

**Q109.5** (Scenario) You delete the wrong file with `rm` and there is no recycle bin. State what actually
happened to the data, what recovery options exist, and two preventive habits you would adopt.

---

## CYB-110 · Windows Fundamentals and PowerShell Basics

**Q110.1** (MCQ) What does a Windows access token contain?

- A. The user's password hash
- B. The user's security identifier, the groups they belong to, and the privileges granted
- C. The list of files the user opened this session
- D. The BitLocker recovery key

**Q110.2** (MCQ) A folder's ACL contains `Allow Modify` for `LAB\Finance` and `Deny Full control` for
`LAB\Contractors`. A contractor who is also in Finance tries to edit a file. What happens, and why?

- A. They can edit, because Allow entries take precedence
- B. They are denied, because an explicit Deny entry takes precedence over Allow
- C. They can edit, because group membership overrides Deny
- D. Access depends only on the file owner

**Q110.3** (MCQ) Which Security event ID records a failed logon?

- A. 4624
- B. 4625
- C. 4688
- D. 7045

**Q110.4** (Short) Why is PowerShell used by both defenders and attackers, and name two logging features that
make its use auditable.

**Q110.5** (Scenario) The same text file is copied from Linux to Windows and its SHA-256 changes, although the
content looks identical. Give the most likely explanation and one way to confirm it.

---

## CYB-111 · Virtualization, Snapshots and Isolated Lab Networks

**Q111.1** (MCQ) What does a host-only virtual network adapter allow?

- A. The VM to reach the internet through the host
- B. The VM to communicate with the host and other VMs on that virtual network, with no route to the physical LAN
- C. The VM to appear as a separate physical machine on the office LAN
- D. The VM to share the host's loopback interface

**Q111.2** (MCQ) Which statement distinguishes a snapshot from a clone?

- A. A snapshot is a full independent copy; a clone references the original disk
- B. A snapshot records disk state at a point in time and depends on the original disk; a clone is an
  independent copy
- C. Both are identical in cost and purpose
- D. A clone can only be taken while the VM is running

**Q111.3** (MCQ) Which hypervisor type runs directly on hardware with no host operating system beneath it?

- A. Type 1
- B. Type 2
- C. Container runtime
- D. Emulator

**Q111.4** (Short) Describe two checks that produce evidence of isolation, rather than an assumption of it.

**Q111.5** (Scenario) You discover a lab VM running a deliberately vulnerable application has been left on a
bridged adapter. Explain the risk, the immediate action, and the change that prevents recurrence.

---

## CYB-112 · Introduction to Kali Linux

**Q112.1** (MCQ) Which description of Kali is accurate?

- A. A hardened server distribution intended for production use
- B. A Debian-based distribution that ships a large security toolset, useful when its tools match the task
- C. A penetration-testing framework that replaces the operating system's package manager
- D. A Windows subsystem that runs Linux tools

**Q112.2** (MCQ) You need to edit a configuration file on a production web server you administer. Which host is
the better choice?

- A. The Kali VM, because it has more tools
- B. A standard Linux host or SSH session with the usual administration tools, because the task needs no
  offensive tooling
- C. A Windows workstation running PowerShell remoting
- D. Whichever host has the newest kernel

**Q112.3** (MCQ) What does Kali's rolling-release model imply for maintenance?

- A. Updates are optional because the image is frozen
- B. Updates arrive continuously, so a full upgrade should be run regularly and a snapshot taken first
- C. Only security tools receive updates
- D. Upgrades must be performed once per year at most

**Q112.4** (Short) Why should you check a tool's version before following a tutorial's exact command line?

**Q112.5** (Scenario) A classmate says, "I'll use Kali for everything, because that's what hackers use." Give
two criteria you would use to choose between Kali, a standard Linux host, and a built-in operating-system tool.

---

## CYB-113 · Introduction to Cryptography, Hashing and Digital Signatures

**Q113.1** (MCQ) Which primitive detects modification without using any key and without providing confidentiality?

- A. Symmetric encryption
- B. Asymmetric encryption
- C. A cryptographic hash
- D. A digital signature

**Q113.2** (MCQ) How is a digital signature produced and verified?

- A. Sign with the public key, verify with the private key
- B. Sign with the private key, verify with the public key
- C. Sign with a shared secret, verify with the same secret
- D. Sign with a hash, verify with a certificate

**Q113.3** (MCQ) What does a TLS certificate bind?

- A. A public key to an identity, asserted by a certificate authority
- B. A private key to a password
- C. An IP address to a MAC address
- D. A session cookie to a user account

**Q113.4** (Short) Why are MD5 and SHA-1 no longer acceptable for integrity verification?

**Q113.5** (Scenario) You download an ISO and its published SHA-256 does not match your copy. State what the
mismatch proves, what it does not prove, and your next two actions.

---

## CYB-114 · Password Security, MFA and Phishing Awareness

**Q114.1** (MCQ) What is password spraying?

- A. Trying many passwords against one account
- B. Trying a small set of common passwords across many accounts to stay under lockout thresholds
- C. Reusing a password across many sites
- D. Cracking hashes with a GPU

**Q114.2** (MCQ) Which second factor resists phishing most effectively, and why?

- A. SMS codes, because phones are personal
- B. TOTP codes, because they expire in 30 seconds
- C. A FIDO2/WebAuthn security key, because the credential is bound to the origin that requested it
- D. Security questions, because only the user knows the answers

**Q114.3** (MCQ) Which control most directly limits the damage from password reuse after a third-party breach?

- A. Forcing a 90-day password rotation
- B. Checking logins against known-breached credential lists, plus MFA
- C. Requiring a special character
- D. Hiding the password field

**Q114.4** (Short) Name two attacks that survive MFA and state the precondition each needs.

**Q114.5** (Scenario) An email appears from `accounts@paypa1-support.com`, addresses you by name, warns of a
suspicious login, and links to a login page. List three checks you would perform and name the single check that
settles the question.

---

## CYB-115 · Security Logs and Basic Troubleshooting

**Q115.1** (MCQ) Which command shows failed SSH authentications from the last hour on a systemd host?

- A. `journalctl -u ssh --since "1 hour ago"`
- B. `dmesg | tail`
- C. `systemctl status ssh`
- D. `last -a`

**Q115.2** (MCQ) Which five fields should you extract from any log line before interpreting it?

- A. Timestamp, source, actor, action, outcome
- B. Hostname, kernel version, uptime, load, memory
- C. User, password, session, cookie, token
- D. Severity, facility, PID, UID, GID

**Q115.3** (MCQ) What can the *absence* of an expected log entry indicate?

- A. Nothing; only present entries are evidence
- B. That logging is disabled or misconfigured, that the event never happened, or that the entry was removed —
  and the possibilities must be distinguished
- C. Always that the event did not happen
- D. That the system clock is wrong

**Q115.4** (Short) State a fixed troubleshooting order you can defend, and explain why changing the order
mid-investigation causes problems.

**Q115.5** (Scenario) A user reports "I can't log in". Describe your first four checks in order, and the
evidence you would record at each.

---

## Troubleshooting exercises

These take longer than a quiz item — twenty to thirty minutes each. They are marked against the key's
criteria, not a single answer.

**T115.1** A Linux VM has no internet access but can ping its host at `192.168.56.1`. `ip route` shows no
default gateway. Write the diagnosis in four steps and the command you would run at each.

**T115.2** A Windows host's Security log contains 4625 events for one account every 30 seconds from a single
address, and 4624 events for the same account immediately afterwards. Explain what pattern this is, what
benign explanation must be excluded, and what you would record.

**T115.3** You are given `auth.log` lines from two hosts whose clocks differ by four minutes, and asked when a
session began. Describe how you establish which clock is wrong and how you state the timeline.

---

## Practical challenges

The quiz checks vocabulary; these check that you can act. Each maps to a lab whose final challenge is the
assessment.

| Module | Challenge | Where |
| --- | --- | --- |
| CYB-108 | Prove DHCP failure by producing a link-local address, then fix it | [LAB-108-01](../levels/level-1-foundations/08-addressing-and-protocols/lab-01-network-configuration.md) |
| CYB-109 | Create a file tree, set permissions to a stated policy, and prove it with `ls -l` and `namei` | [LAB-109-01](../levels/level-1-foundations/09-linux-command-line/lab-01-files-permissions.md) |
| CYB-110 | Produce a filtered event-log export for one event ID, with the query recorded | [LAB-110-01](../levels/level-1-foundations/10-windows-powershell-basics/lab-01-windows-inspection.md) |
| CYB-111 | Build an isolated network and prove it with two independent tests | [LAB-111-01](../levels/level-1-foundations/11-virtualization-and-lab-networks/lab-01-isolated-network.md) |
| CYB-113 | Detect a modified file using only hashes, and state what the hash does not prove | [LAB-113-01](../levels/level-1-foundations/13-cryptography-hashing-signatures/lab-01-hashing-integrity.md) |
| CYB-114 | Triage three synthetic phishing emails and justify the one you would report | [LAB-114-01](../levels/level-1-foundations/14-passwords-mfa-phishing/lab-01-phishing-triage.md) |
| CYB-115 | Follow a symptom to a cause across two log sources | [LAB-115-01](../levels/level-1-foundations/15-security-logs-and-troubleshooting/lab-01-evidence-trail.md) |

---

## Next

- [Level 1 answer key](level-1-key.md) — mark your attempt
- [Level 1 integrated assessment](level-1-assessment.md) — the three-hour practical plus written justification
- [Level 1 overview](../levels/level-1.md) — module list and outcomes

---
title: "Level 1 Answer Key"
description: "Answers and explanations for all 75 Level 1 items, with acceptable-reasoning criteria for the open questions."
module_code: ASM-L1K
level: 1
kind: assessment
prerequisites: [CYB-101]
estimated_minutes: 60
difficulty: beginner
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, answer-key, level-1]
---

# Level 1 Answer Key

!!! warning "Attempt first"
    Reading this page before attempting the [Level 1 quiz](level-1-quiz.md) converts a measurement into a
    reading exercise. Attempt on paper first, then come back.

**Marking.** Each module is worth 5: one mark per item. Multiple-choice items are right or wrong. Short
answers earn the mark only if they contain **every required point** listed below — partial credit is what
lets a gap survive. Scenario items earn the mark for the decision **and** the reason; a correct decision
with no reasoning is half a mark.

Record each item as **correct**, **wrong**, or **right for the wrong reason** (you chose the right option but
your justification was not the one below). The third category is the one to re-study.

---

## CYB-101 · Introduction to Cybersecurity

**Q101.1 — B.** An attacker needs one unmitigated path; a defender must cover every path, every time. Tools
are broadly comparable and often free; the asymmetry is structural, not budgetary. Option D is the
dangerous misconception: most incidents are opportunistic and untargeted.

**Q101.2 — A.** Predict, prevent, detect, respond. Scanning and reporting are activities inside those phases,
not peers of them.

**Q101.3 — C.** Policy authorship, risk acceptance and commissioning audits are governance work. Engineering
builds controls; offensive work tests them; response handles incidents.

**Q101.4.** Required points: (1) test only systems you own or have **explicit authorization** to test, and
stay inside the agreed scope; (2) authorization comes **from the asset owner** and is **specific** — targets,
time window, permitted techniques — not a verbal "go ahead" from a colleague.

**Q101.5.** Acceptable: a written scope from the business owner naming the site, the window, and what may be
attempted, plus agreement on how findings are handled. For a serious finding: report it privately to the
owner with reproduction steps, do not publish, do not test further than needed to demonstrate it, and agree a
fix timeline. Full marks require recognising that a friendship of years is not authorization.

---

## CYB-102 · CIA Triad, Security Principles and Risk

**Q102.1 — B.** The clerk changed data they were not entitled to change: integrity, with an authorization
failure behind it. Availability is unaffected, and confidentiality only if they also read records they should
not.

**Q102.2 — C.** Least privilege: the minimum access needed for the role. Defence in depth is about layers;
fail-safe defaults is about the initial state of access.

**Q102.3 — B.** Isolation is a compensating control that lowers likelihood; the decision to keep running the
system and accept what remains is risk acceptance. Calling it "mitigation" alone hides the acceptance, and
calling it "avoidance" is simply wrong.

**Q102.4.** A threat is a potential cause of harm — an actor, event or circumstance; a vulnerability is a
weakness that a threat can exploit. Example: an exposed SSH service with password authentication (vulnerability)
and an internet-wide credential-stuffing campaign (threat). Answers that swap the terms, or that describe an
"exploit" as a threat, do not earn the mark.

**Q102.5.** Internet-facing RCE ranks higher: high likelihood (reachable, automated exploitation) and high
impact (full host compromise). Unencrypted laptop is real but conditional: it needs physical theft, and impact
is limited to data on that device. State an assumption such as "the server holds no regulated data" and say
whether it would change the ranking.

---

## CYB-103 · Threats, Vulnerabilities, Exploits and Controls

**Q103.1 — C.** Design vulnerability. Implementation flaws can be patched; design flaws usually need the
protocol or architecture changed, which is why they persist.

**Q103.2 — B.** A zero-day is exploited before a fix is generally available. Discovery by a researcher, or the
absence of an advisory, is not the definition.

**Q103.3 — A.** A badge door is a physical preventive control; a receptionist checking a list is an
administrative preventive control. Neither detects after the fact.

**Q103.4.** Any two: patching causes downtime and regression risk that must be scheduled; some systems cannot
be patched at all; not every patch fixes an exploitable issue, so triage by exposure and exploitability is
required; supply-chain delays mean the vendor patch is not the end of the chain. Full marks require the idea
of *prioritisation by risk*, not just "patching is hard".

**Q103.5.** Example set: phishing-resistant MFA (preventive), email filtering with DMARC enforcement
(preventive), EDR detection of token theft or impossible travel (detective), forced session revocation and
password reset after a confirmed compromise (corrective). Marks require three controls that are genuinely at
different points, correctly labelled.

---

## CYB-104 · Threat Modeling and Attack Surfaces

**Q104.1 — B.** Tampering with data the client is not trusted to supply. Spoofing is pretending to be another
identity; repudiation is denying an action.

**Q104.2 — B.** A trust boundary is where data or control crosses between components with different trust or
privilege. It is a modelling construct, not a firewall rule, though firewalls often sit on one.

**Q104.3 — B.** Removing the interface and its package deletes the code path. A WAF adds a control in front of
the same surface; longer passwords and more logging change other properties.

**Q104.4.** What are we building? What can go wrong? What are we going to do about it? Did we do a good job?
(Equivalent wording accepted; all four required.)

**Q104.5.** Browser→API boundary: spoofing (S) of a client or tampering (T) with request fields; API→database
boundary: information disclosure (I) through over-broad queries, or elevation of privilege (E) via excessive
database permissions. Marks require the boundary named *and* a threat that is plausible at that boundary.

---

## CYB-105 · Ethics, Authorization and Law

**Q105.1 — C.** A signed scope from the owner with targets, window, techniques and contact. A verbal go-ahead
is unauthorised in practice because it cannot be evidenced; a colleague who uses the system is not its owner;
a bug-bounty page authorises only what its scope says.

**Q105.2 — B.** Private report with reproduction and an agreed timeline. Publishing first removes the vendor's
chance to fix and can expose users; a public forum is disclosure by another name.

**Q105.3 — B.** Authorization comes from the asset owner; intent does not create it. Good intentions are
relevant to sentencing, not to whether an offence occurred.

**Q105.4.** Required: in-scope targets (named, not "the website"), time window, permitted techniques or
constraints, and a contact/escalation path. Exclusions matter because they define what you must *not* touch
when you stumble onto it — and because most scope incidents are accidental, not deliberate.

**Q105.5.** Stop testing the staging host immediately; do not use or retain the tokens; record only what is
needed to describe the issue (no session data); report through the programme's channel, noting that the
finding is on an excluded asset and asking how to proceed; follow their instruction, including "do not
continue". Full marks require *stop first* and *do not retain the data*.

---

## CYB-106 · Hardware, Operating Systems and Permissions

**Q106.1 — B.** The kernel mediates memory, devices and IPC. A kernel bug defeats in-process protections,
which is why kernel exploits are rated so highly.

**Q106.2 — C.** Owner read/write, group read, others none: alice and members of `auditors`.

**Q106.3 — B.** A directory writable by the web user **and** able to execute scripts allows an uploaded file
to run as the server. Group-readable logs are a lesser confidentiality issue; a root-only config is correct.

**Q106.4.** setuid makes the program run with the file owner's effective UID rather than the caller's. Risk:
if the owner is root and the program has a flaw (buffer overflow, unsafe `PATH`, shell escape), any user can
turn it into privilege escalation.

**Q106.5.** Any three: what parent process started it and why; what the full command line is doing; whether
`www-data` is expected to spawn a shell at all; what it has open (`lsof -p`) and where it connects; whether the
binary or script was recently modified; whether the application's own logs explain it. "It's www-data, so it's
the web server" is the answer that misses web-shells.

---

## CYB-107 · Networking Fundamentals

**Q107.1 — B.** Layer 2, by MAC address. A layer-3 switch routes by IP as well, but forwarding frames is its
layer-2 function.

**Q107.2 — C.** Segment for TCP, datagram for UDP. Frame is layer 2, packet is layer 3.

**Q107.3 — C.** The port number selects the service. MAC identifies the interface on the local segment; IP
identifies the host across networks.

**Q107.4.** Application data is passed to the transport layer, which adds a header to form a segment (TCP) or
datagram (UDP); the network layer adds an IP header to form a packet; the link layer adds a frame header and
trailer to form a frame, which is transmitted. Each layer treats the layer above as payload.

**Q107.5.** Two of: the service is listening but the TLS handshake fails (expired or wrong-name certificate);
the service expects HTTP and the client speaks HTTPS (or the reverse); the application is returning an error
(500) so the port accepts but the page fails; the port is open on a different interface/address than the one
being requested. "The port is open" only proves something accepted the connection.

---

## CYB-108 · Addressing and Protocols

**Q108.1 — B.** `192.168.1.0/26` covers `.0`–`.63`; `.0` is the network address, `.63` the broadcast, and
`.1`–`.62` are usable.

**Q108.2 — B.** `169.254.0.0/16` is link-local (APIPA): DHCP did not answer. It is not a valid corporate or
public address, and its presence is itself diagnostic.

**Q108.3 — B.** TLS protects data in transit and authenticates the server. It does not hide the destination
IP (the connection needs it), does not protect data at rest, and does not replace authorization.

**Q108.4.** Name resolution: `dig`/`nslookup` returns NXDOMAIN or SERVFAIL, or times out. Port closed: `nc
-vz` reports connection refused (a TCP RST), and `ss -ltn` on the host shows nothing listening. Service
broken: the port accepts, and the application returns an error status or logs a failure.

**Q108.5.** Fault domain: name resolution (NXDOMAIN is authoritative — the name does not exist as queried).
Next commands: read `/etc/resolv.conf` (or `resolvectl status`) to confirm the resolver and search domains,
then `dig db.lab.local @<resolver>` and `dig db.lab.local` with the fully qualified name including the domain,
to test whether the search suffix is the problem.

---

## CYB-109 · Linux Command Line

**Q109.1 — A.** 6 = read+write for owner, 4 = read for group, 0 for others.

**Q109.2 — A.** `666 & ~027 = 640`. Directories would get `777 & ~027 = 750`.

**Q109.3 — A.** `ss -ltnp`: listening, TCP, numeric, process. Without root you see only your own processes,
which is a common reason the mapping appears to fail.

**Q109.4.** An absolute path starts at `/` and means the same thing from any working directory; a relative
path is resolved from the current directory. Absolute is safer in scripts, cron jobs, systemd units and any
command run by another user, because the working directory is not guaranteed.

**Q109.5.** `rm` unlinks the directory entry; the data blocks remain until overwritten. Recovery: stop writing
to that filesystem, then use a backup or VM snapshot; carving tools (`extundelete`, `testdisk`, `photorec`)
may recover content but not reliably the name. Prevention: backups verified by restore, and a `trash-cli`
alias or `rm -i` habit; quoting globs before running destructive commands.

---

## CYB-110 · Windows Fundamentals

**Q110.1 — B.** SIDs of the user and groups, plus privileges. Hashes live in SAM/NTDS, never in the token.

**Q110.2 — B.** Explicit Deny wins over Allow. This is the opposite of the common "allow always wins"
assumption, and it is how contractors lose access they appear to have been granted.

**Q110.3 — B.** 4625 is a failed logon; 4624 is successful; 4688 is process creation; 7045 is a service
installed.

**Q110.4.** It is installed everywhere, can run in memory, reaches .NET/WMI/COM, and blends with administration
— "living off the land". Logging: Script Block Logging (4104), Module Logging (4103), transcription, and AMSI
for content inspection.

**Q110.5.** Different bytes on disk: usually line endings (CRLF vs LF) or encoding introduced by the transfer
mode. Confirm with `file`, `xxd | head`, and by hashing the same bytes on both sides (e.g. `sha256sum` inside
WSL, or transfer in binary mode). The lesson: a hash covers bytes, not meaning.

---

## CYB-111 · Virtualization and Lab Networks

**Q111.1 — B.** Host-only gives the VM a private virtual network shared with the host and other VMs, with no
route out.

**Q111.2 — B.** A snapshot is a point-in-time delta dependent on the original disk and grows as you work; a
clone is independent. Snapshots are cheap and temporary; clones cost disk and are durable.

**Q111.3 — A.** Type 1 runs on hardware (ESXi, Hyper-V, KVM in some deployments, Proxmox's KVM); Type 2 runs
on a host OS (VirtualBox, VMware Workstation, UTM).

**Q111.4.** Two of: `ip route` shows no default gateway on the lab VM, and a ping to `1.1.1.1` or a name lookup
fails; a host on the physical LAN cannot reach the VM's address and a scan of the LAN from the VM finds nothing
but its own segment; the virtual adapter is confirmed as host-only/internal by reading the hypervisor settings;
the host's physical interface capture shows no traffic from the VM. Evidence, not configuration alone.

**Q111.5.** Risk: the deliberately vulnerable app is reachable from the office LAN and possibly from other
networks via the host's bridge — an unauthenticated compromise path into a machine you control. Immediate:
disconnect the adapter or power off the VM; revert to a clean snapshot if it may have been touched. Prevention:
name lab networks so bridged is never selected by default, and add an isolation check to the pre-lab checklist
that must be recorded before the vulnerable service is started.

---

## CYB-112 · Kali Linux

**Q112.1 — B.** A Debian-based distribution with a large security toolset. It is not hardened for production
and is not a replacement for understanding the tools.

**Q112.2 — B.** Editing a configuration file needs an editor and ordinary administration tools. Bringing an
offensive toolset to a production host increases risk for no benefit.

**Q112.3 — B.** Continuous updates; run a full upgrade regularly, snapshot first, and expect occasional
breakage from a rolling release.

**Q112.4.** Flags, defaults and output formats change between versions, so a tutorial's exact command can
silently do something different — or fail in a way that looks like a finding. Recording versions also makes
your evidence reproducible.

**Q112.5.** Criteria such as: does the task need the specialist toolset at all; what does the target
environment require (Windows-native tool, distribution package availability); what is the smallest capability
that answers the question; reproducibility for a reader. Full marks require the idea that the tool follows the
question, not the reverse.

---

## CYB-113 · Cryptography, Hashing and Signatures

**Q113.1 — C.** A hash needs no key. A signature also provides integrity without confidentiality, which is why
the stem specifies *no key*; a signature requires a private key.

**Q113.2 — B.** Sign with the private key, verify with the public key. Reversing this is the most common
conceptual error in the module.

**Q113.3 — A.** A certificate binds a public key to an identity, asserted by a CA and validated against trust
anchors, names and validity dates.

**Q113.4.** Practical collisions exist: MD5 since 2004 and SHA-1 with the 2017 SHAttered attack (and cheaper
chosen-prefix collisions afterwards). An attacker can produce two different files with the same hash, so a
matching hash no longer proves the file is unmodified in the way you intended.

**Q113.5.** The mismatch proves your bytes differ from the bytes the publisher hashed. It does not prove
malice — corruption in transit, a mirror serving an old build, or the wrong file are all possible. Actions:
re-download from the official source over HTTPS, verify any signature as well as the hash, and do not execute
the file until it verifies.

---

## CYB-114 · Passwords, MFA and Phishing

**Q114.1 — B.** A few common passwords across many accounts, staying under lockout thresholds. Many passwords
against one account is brute force and trips lockouts.

**Q114.2 — C.** FIDO2/WebAuthn binds the credential to the origin, so a proxy at a lookalike domain cannot
replay it. SMS and TOTP codes can be relayed by a real-time phishing proxy.

**Q114.3 — B.** Breached-credential screening blocks the reused password at login, and MFA limits the value of
a password alone. Rotation and composition rules are the controls the evidence has moved away from.

**Q114.4.** Any two with preconditions: real-time phishing proxy / adversary-in-the-middle (user must
authenticate through the proxy); MFA fatigue or push bombing (push-based MFA and a user who approves);
SIM swap (SMS-based factor); session-cookie theft after authentication (malware or XSS, defeating MFA
entirely). "MFA can be bypassed" without the precondition earns nothing.

**Q114.5.** Checks: the sender domain against the display name (`paypa1` with a digit one); where the link
actually points (hover/status bar, not the text); authentication results in the headers (SPF/DKIM/DMARC);
the urgency and the request (credentials, payment, MFA approval). The check that settles it: contact the
organisation through a known, independent channel — type the address yourself or phone the number on your
statement — never through the contact details in the message.

---

## CYB-115 · Logs and Troubleshooting

**Q115.1 — A.** `journalctl -u ssh --since "1 hour ago"`, then filter for failures. `dmesg` is kernel ring
buffer; `last` shows sessions, not auth failures.

**Q115.2 — A.** Timestamp, source, actor, action, outcome. Without all five you cannot say who did what, from
where, and whether it worked.

**Q115.3 — B.** Absence is evidence but ambiguous: logging may be off, the event may not have happened, or the
record may have been deleted. Distinguishing those three is the investigative work.

**Q115.4.** Example order: define the symptom precisely; check the physical/network layer; check the service
state; read the logs for that service; only then inspect configuration and recent changes. Changing order
mid-investigation produces confirmation bias — you start collecting evidence for a theory rather than
eliminating causes.

**Q115.5.** First four: confirm the account is not locked or disabled (and whether the password expired); check
the service is running and reachable; read the authentication log for that user in the reported window (4625 or
`auth.log`); check clock and time source, because an unsynchronised clock makes the log look empty. Record the
command, output and timestamp at each step.

---

## Troubleshooting exercises — marking criteria

**T115.1** (4 marks) — one per step, with the command that tests it:
1. Confirm the fault is routing, not name resolution (`ip route`, `ping 1.1.1.1`).
2. Identify the missing default and the correct gateway for the host-only network (`ip route`, hypervisor
   network settings).
3. Add the route or fix the adapter configuration (`ip route add default via …`, or correct the VM network
   mode), stating whether the change survives reboot.
4. Verify with `ip route`, a ping to the gateway, and one external name lookup, and record before/after.
Award 0 if the answer is "restart the VM" with no diagnosis.

**T115.2** (4 marks) — one each for: pattern identified as repeated failed authentication followed by success
(brute force or a misconfigured service account, depending on the account); the benign explanation to exclude
(a scheduled task, service or backup job using stale credentials, or a user repeatedly mistyping then
succeeding); the account and source identified; the record written with timestamps, count and what would
confirm/refute malice (e.g. source geolocation, logon type, whether the success came from the same host).

**T115.3** (4 marks) — one each for: comparing both hosts to an independent time source (NTP peer, domain
controller, or a capture taken at the same moment); stating which clock is wrong and by how much; converting
one timeline to a single stated timezone and labelling the conversion; expressing the uncertainty ("session
began 14:02:10 ± 4 min, host B clock 4 min fast") rather than presenting a false precision.

---

## Level 1 integrated assessment — model answers

Mark Part A against your own evidence, then against these expectations. Part B is marked for reasoning, so
what follows is a set of *required elements*, not a script.

### Part A expectations

| Task | Expected shape | Common loss of marks |
| --- | --- | --- |
| A1 | A named private range (for example `10.10.10.0/24`), hosts at fixed addresses, adapter type per host, one service, one exclusion with a reason | "Private range" with no range; exclusion named but not justified |
| A2 | Both hosts ping by address and resolve by name; outputs pasted, not summarised | Name resolution skipped; outputs paraphrased |
| A3 | (a) `ip route` shows **no** `default via` line and `ping 1.1.1.1` fails; (b) `curl --max-time 5 http://1.1.1.1` fails with a timeout or unreachable, not a DNS error; (c) from the LAN host, `ping` and a port probe to the target fail or are filtered; (d) a capture on the analyst interface shows only ARP/ICMP/DHCP traffic belonging to the range | Four pings and nothing else; no statement of what failure would have looked like |
| A4 | `ss -ltnp` on the target shows the listener with its PID; a connection from the analyst succeeds; the same port probed from elsewhere is closed or filtered | Claiming a listener without showing the process |
| A5 | NAT adds a `default via` route; outbound check (b) now succeeds, which is the proof the check works; after restoration, A3 output is identical to the original | Change made but no before/after; no re-run after restore |
| A6 | Snapshot names, exact revert commands, what reverting loses, and a README mapping files to tasks | "Revert the snapshot" without names or commands |

**On "a check that cannot fail".** The strongest submissions show the negative case: A5 demonstrates that
check (b) detects a leak because it flips from failure to success. A submission with four passing checks and
no demonstration that any of them can fail earns at most half of A3, however tidy it looks.

### Part B criteria

**B1 (8).** Requires: the range chosen and why it cannot collide with the physical LAN; the adapter type and
what it permits; a named simpler alternative (bridged, or NAT with port forwarding) and the reason it was
rejected — exposure, not difficulty. Deduct for "host-only is more secure" with no mechanism.

**B2 (7).** There is no single correct ranking, but the reasoning must distinguish **observational** evidence
(an outbound attempt failing, a LAN host unable to reach the target) from **configuration** evidence (the
adapter setting). Configuration is the weakest because it describes intent, not behaviour. Accepted leak
paths: a second adapter the learner forgot, host-only networking on a hypervisor that also bridges, IPv6
route discovered by the VM, or the host's own routing/NAT forwarding traffic. Any one, stated concretely,
earns the third mark.

**B3 (6).** Requires: the observed change (default route appears, outbound succeeds), the explanation (NAT
provides translation and a gateway), and the generalisation (the configuration is a claim; the observed
behaviour is the evidence; the two can disagree). Answers that only narrate what they clicked earn 2.

**B4 (5).** Any genuine accepted risk with reasoning, for example: the target runs a service that could be
reached if isolation failed, because the exercise requires a listener; or no host firewall, because the
network boundary is the control and a host firewall would mask a failure. Deduct if the "risk" is trivial or
if the mitigation is claimed without being recorded.

**B5 (4).** Requires: what was verified (four checks, with the failure case demonstrated); what was not (the
hypervisor's own bugs, the host's other interfaces, anything changed after the checks); and a statement that
isolation is maintained, not proven once. "Yes, it is completely safe" earns 0; a refusal to answer earns 0.

---

## Scoring

| Module score | Action |
| --- | --- |
| 5/5 | Move on; retake at seven days to confirm retention |
| 4/5 | Move on; reread the explanation for the missed item |
| 3/5 | Re-read the lesson section the item came from, then retake the module |
| 0–2/5 | Re-do the module's lab before the quiz — the gap is applied, not verbal |

Level total: 75 marks. Below 56 (75%) suggests the level assessment will be difficult; the lab work, not more
quizzes, is the fix.

## Related

- [Level 1 quiz](level-1-quiz.md) · [Level 1 integrated assessment](level-1-assessment.md)
- [Assessment Guide](../start-here/assessment-guide.md) — the protocol behind this page
- [How Assessment Works](../policies/assessment-format.md) — weights and integrity rules

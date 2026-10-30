---
title: "Level 2 Answer Key"
description: "Answers and explanations for all 30 Level 2 items, plus marking criteria for the integrated host assessment."
module_code: ASM-L2K
level: 2
kind: assessment
prerequisites: [CYB-201]
estimated_minutes: 45
difficulty: intermediate
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, answer-key, level-2]
---

# Level 2 Answer Key

!!! warning "Attempt first"
    Attempt the [Level 2 quiz](level-2-quiz.md) before reading this page.

**Marking.** One mark per item, 5 per module. Multiple-choice is right or wrong. Short answers need every
required point. Scenario items need the diagnosis **and** the check that distinguishes the alternatives.

---

## CYB-201 · Lab Environment

**Q201.1 — B.** Check the link and the addressing before anything else: same virtual network, interfaces up,
addresses in one subnet. Reinstalling a service or disabling your workstation firewall are changes that hide
the cause.

**Q201.2 — B.** `ip addr` shows addresses per interface. `ip route` shows routes; `ss -ltnp` shows listeners;
`arp -a` shows the neighbour cache.

**Q201.3 — A.** Bound to `127.0.0.1` means only local connections are accepted, regardless of firewall. This
is one of the three named failures and the most common reason a "running" service appears dead from another
host.

**Q201.4.** (1) Wrong virtual adapter or network — check the hypervisor's adapter setting and `ip link`; (2)
wrong subnet or mask — check `ip addr` and `ip route` on both hosts; (3) service bound to loopback — check
`ss -ltnp` on the target for the bind address. Accept any wording that names the mechanism and a check.

**Q201.5.** Two explanations: a host firewall on the target drops the probes while allowing ICMP (so ping
works and ports look filtered), or a filter exists on the virtual network between the hosts. Distinguish by
capturing on the target (`tcpdump -ni any port 22`) while scanning: if SYNs arrive, the target's firewall or
service is responsible; if nothing arrives, the traffic is being dropped before the host. Checking the
target's firewall rule counters or logs supports the same conclusion.

---

## CYB-202 · Bash, Python and Git

**Q202.1 — B.** `-e` exit on error, `-u` error on unset variable, `-o pipefail` propagate a pipeline failure.
It does not log, elevate or quote.

**Q202.2 — B.** Dry-run exposes the intended actions and their targets for review before state changes. It is
not faster, and it does not remove the need for validation.

**Q202.3 — B.** The key is in history, so it must be rotated; removing it from history matters for shared
copies, but rotation is the control that actually ends the exposure. `.gitignore` prevents recurrence, not the
current exposure.

**Q202.4.** Any three: reject empty or over-broad patterns (`*`, `/`, `.`); resolve matches and confirm they
lie inside a fixed base directory after canonicalisation; refuse to act on paths outside it; require an
explicit confirmation or `--apply`; refuse to run as root on system paths. All three must be *before* the
delete, not warnings after it.

**Q202.5.** Handle input per line: wrap parsing in `try/except`, skip malformed records, record line numbers
and the reason, continue, and exit non-zero only if a stated threshold is exceeded (for example, more than 1%
skipped, or zero records parsed). Final summary: parsed, skipped, first three malformed lines with numbers.
"Crash on the first bad line" is the failure the module is teaching against.

---

## CYB-203 · Discovery and Enumeration

**Q203.1 — B.** `-sn` is ping scan only. `-sV` is version detection, `-sU` UDP, `-O` OS detection.

**Q203.2 — B.** No response: consistent with a drop, which is why UDP and firewalled ports both produce it.
A reset would be `closed`; `open` requires a response proving acceptance.

**Q203.3 — B.** Version detection is a guess from banners and probes. Confirm with an independent method —
`ssh -vv` banner, `curl -I` server header, or the service's own version request — and record the version you
observed, not the one the scanner inferred.

**Q203.4.** A scanner reports an inference from a probe, and inferences fail in both directions: proxies,
load balancers and IDS can answer on behalf of a host, and services can be reachable but not exploitable (or
vice versa). A finding needs observed behaviour plus impact, so the claim has to be reproducible by someone
else.

**Q203.5.** UDP has no handshake, so silence is ambiguous: an open service may ignore an empty or unexpected
datagram, and a filter drops it — both look the same. Narrow it with service-specific probes (`dig` for 53,
`ntpq -p`/`ntpdig` for 123, `snmpwalk` for 161), several payload variants, and a capture on the target to see
whether the datagrams arrived. Record the state as unresolved if it cannot be distinguished.

---

## CYB-204 · Packet Capture

**Q204.1 — B.** Capture filters (BPF) limit what is written; display filters select what is shown. Getting
this backwards is why people capture 4 GB and then cannot find the flow they needed.

**Q204.2 — B.** `host 10.10.10.20 and port 443` is valid BPF. Option A is Wireshark display-filter syntax;
option D changes the logic to *either* condition; option C is not a filter expression.

**Q204.3 — B.** SNI, addresses, ports, sizes and timing remain. HTTP content and keys do not. This is the
metadata that hunting and network monitoring actually use.

**Q204.4.** Any four: capture point/interface; start and stop time in UTC with timezone stated; filter used;
tool and version; SHA-256 of the file; host and network context; who captured it and why (custody). Naming and
retention matter but are not substitutes for the hash.

**Q204.5.** The server completed the TCP handshake and then reset before any application data: the port is
reachable but whatever should answer is not accepting (service down, bound elsewhere, or a proxy/middlebox
resetting). Rule out: (a) wrong service or port — check `ss -ltnp` on the target and try the expected protocol
(`curl -v`, `openssl s_client`); (b) a middlebox or firewall resetting — compare a capture taken at the target
with the one at the client, and test from a second client on the same segment.

---

## CYB-205 · SSH

**Q205.1 — B.** `600`, owner-only. The private key is the credential; group or world readability is a
compromise waiting for a backup.

**Q205.2 — A.** `authorized_keys` on the server lists client public keys permitted to log in; `known_hosts` on
the client records server host keys, which is what detects a changed host key.

**Q205.3 — B.** `sshd -t` validates syntax and key files; an existing session kept open is your way back in if
the new configuration rejects you. Rebooting is the opposite of cautious.

**Q205.4.** Password authentication makes an account brute-forceable from anywhere; root login makes the
highest-privilege account the target and removes accountability. Removing either alone leaves a path: root
with keys only is still a target for key theft, and password auth for normal users still allows spraying.

**Q205.5.** Recovery: log in on the console, inspect the effective configuration (`sshd -T`), revert the last
change (or the drop-in file), validate with `sshd -t`, restart the service, and test a new connection before
closing the console. Prevention: keep an existing session open while changing access controls, validate and
test on a second listener/port or a snapshot first, and record the rollback command before making the change.

---

## CYB-206 · Host Inspection and Assessment

**Q206.1 — B.** The index is comparative and configuration-based; suggestions include items that do not apply
to the host's role. Triage by risk and record why each was accepted or rejected — that record is the
assessment.

**Q206.2 — B.** A world-readable `/etc/shadow` is an observed condition with a clear impact. The others are
suggestions or absences with no demonstrated exposure.

**Q206.3 — A.** `0.0.0.0` is every IPv4 address on the host, so reachability depends on firewall and routing,
not on the bind address alone.

**Q206.4.** FTP as root ranks higher: network-reachable, historically vulnerable service, running with maximum
privilege, and usually unnecessary. Readable logs are a confidentiality issue with a smaller blast radius, but
they expose usernames for later attacks, so they are High rather than Low if the logs are reachable.

**Q206.5.** Four fields: asset and component with the exact version; evidence (command, output, timestamp);
impact and likelihood stated concretely; remediation with a verification step. "Outdated PHP" with no version
cannot be actioned or retested.

---

## Troubleshooting exercises — marking criteria

**T206.1** (3 marks) — one each for: the observations are at different times or through different paths (the
service stopped after the scan, or the scan was answered by something other than the service); a middlebox or
port forward can accept and reset (a proxy or NAT rule); the check that resolves it (repeat `ss -ltnp` and the
scan together, capture on the target, and confirm which process owns the port).

**T206.2** (3 marks) — two of: capture with a BPF filter limited to the relevant hosts/ports; rotate capture
files by size/time (`-C`, `-G`) and merge only what is needed; capture on the correct interface and use
`capinfos` to confirm. Never: edit, trim or re-save the original — work on a copy and keep the hash.

**T206.3** (3 marks) — confirm written authorization and a change window; establish out-of-band access
(console, hypervisor, second management path) and a snapshot/backup; inventory the current configuration and
record the rollback. The usual advice is unsafe because a syntactically valid configuration can still lock you
out (`PasswordAuthentication no` with no key installed), and without console access the only recovery is a
rebuild.

---

## Level 2 integrated assessment — model answers

The assessment asks you to enumerate and assess a lab host, then justify your choices. Full marks do not
require finding every planted issue; they require that everything you claim is evidenced and correctly rated.

### A defensible finding set

A deliberately weakened lab target commonly exposes some of the following. Each entry shows the shape of a
complete finding.

| ID | Finding | Severity | Evidence | Remediation |
| --- | --- | --- | --- | --- |
| F-01 | Anonymous FTP enabled and writable | High | `ftp 10.10.10.20` → `230 Anonymous login ok`; `nmap -sV` banner `vsftpd 3.0.5` | Disable anonymous access, restart, retest with `ftp` |
| F-02 | SSH permits root login with password authentication | High | `sshd -T \| grep -E 'permitrootlogin\|passwordauthentication'` | Drop-in `PermitRootLogin no`, `PasswordAuthentication no`; `sshd -t`; reload; verify |
| F-03 | Database listening on all interfaces | Medium | `ss -ltnp` shows `0.0.0.0:3306`; connection from analyst succeeds | Bind to `127.0.0.1` or restrict with firewall; verify from second host |
| F-04 | World-writable directory in the web root | Medium | `find /var/www -perm -0002 -type d` | Correct ownership and mode; verify with the same command |
| F-05 | Unsupported PHP version | High | `curl -I` `X-Powered-By`; package manager shows version and end-of-life date | Upgrade, or isolate; verify header and version after change |

### Written component criteria

**B1 — Justify scan choices (10 marks).** Requires: why host discovery preceded port scanning; why TCP connect
or SYN scan was chosen (privileges, noise, lab context); why UDP was limited to named ports; how service
detection was verified independently; what was deliberately not run (exploitation, DoS, authenticated testing)
and why.

**B2 — Finding versus false positive (8 marks).** Requires one concrete example of a scanner claim you
rejected, with the check that rejected it (for example, a "vulnerable" version banner that the package manager
showed as backported-patched, or an "open" UDP port that no service-specific probe could confirm). "I trusted
Nmap" loses the marks.

**B3 — Evidence and reproducibility (7 marks).** Requires: exact commands, outputs, timestamps, host and
version context, and enough detail that a peer reproduces each finding without asking.

**B4 — Limits of the evidence (5 marks).** Requires: what the assessment did not cover (authenticated
configuration review, other hosts, application logic), and what the findings therefore cannot claim — for
example, "no exploitation was attempted, so impact beyond reachability is inferred, not demonstrated".

**Safety and scope — a gate, not marks.** The written component is 30 marks: 10 + 8 + 7 + 5. Target named
and inside the lab, no traffic to anything else, data not modified, and any accidental out-of-scope observation
recorded and stopped on. Failing this voids the assessment rather than reducing the score.

---

## Scoring

| Module score | Action |
| --- | --- |
| 5/5 | Retake at seven days; move on |
| 4/5 | Reread the missed explanation, then move on |
| 3/5 | Re-read the lesson section and redo one lab step before retaking |
| 0–2/5 | Return to the module's lab; the gap is practical |

Level total: 30 marks; 24 or above (80%) is a reasonable readiness signal for the integrated assessment.

## Related

- [Level 2 quiz](level-2-quiz.md) · [Level 2 integrated assessment](level-2-assessment.md)
- [Assessment Report Template](../policies/assessment-report-template.md)
- [Level 2 overview](../levels/level-2.md)

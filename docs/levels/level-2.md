# Level 2 — Tooling and Lab Craft

**~90 guided hours · 6 of 8 modules · 18 labs · Prerequisite: Level 1**

!!! success "Status: six modules and eighteen labs published"
    All six published modules and their eighteen labs are written. Every lab carries a scenario, topology,
    numbered commands, expected observations, verification criteria, troubleshooting, cleanup, and extension
    challenges.

    Two modules of the planned eight are **not written**: CYB-207 Vulnerability Assessment Workflow and CYB-208
    Instrumenting Your Own Lab for Defence. Their outcomes are defined in the [roadmap](../curriculum/roadmap.md);
    no pages exist, and nothing below implies otherwise. The level assessment (CYB-209) is published, so the level
    is usable end to end without them.

---

## What this level is about

Level 1 taught you how systems work. Level 2 teaches you how to **investigate** them without guessing, and how to
prove what you found.

The tools here are ordinary: the shell, Python, Git, `nmap`, `tcpdump`, Wireshark, `netcat`, OpenSSH, Lynis. What
makes the level hard — and valuable — is the discipline around them: knowing why a command is the right one,
what its output can and cannot show, and how to record it so somebody else can reproduce it.

Reconnaissance is confined to **your own isolated lab**. Scanning a public system is not an advanced version of
this exercise; it is a different activity with legal consequences.

---

## What you will be able to do

By the end of Level 2 you can:

- Prepare a Kali VM, configure host-only networking, and validate connectivity with evidence.
- Discover hosts and enumerate services inside your own lab, explaining every scan option you chose.
- Explain the difference between TCP and UDP behaviour, and show it in output you produced.
- Capture traffic with `tcpdump` and analyse it in Wireshark, including DNS, TCP handshakes, HTTP and TLS metadata.
- Write a Bash security-check script and a Python log parser, both readable and safe.
- Use Git to version lab artefacts without committing secrets or oversized captures.
- Configure key-based SSH and prove that password authentication is disabled.
- Run a hardening assessment, interpret its output critically, and document findings in a professional report.

---

## Modules

| Code | Module | Focus | Labs | Hours |
| --- | --- | --- | --- | --- |
| [CYB-201](level-2-tooling/01-lab-environment-and-kali/index.md) | Lab Environment, Kali and Network Foundations | Kali preparation, adapter modes, static addressing, connectivity record | 3 | 12 |
| [CYB-202](level-2-tooling/02-bash-python-git/index.md) | Bash, Python and Git for Lab Work | Shell scripting, Python log parsing, Git for artefacts | 3 | 16 |
| [CYB-203](level-2-tooling/03-host-discovery-and-enumeration/index.md) | Host Discovery and Service Enumeration | `nmap` scan types, service detection, `netcat`, TCP vs UDP | 4 | 18 |
| [CYB-204](level-2-tooling/04-packet-capture-and-analysis/index.md) | Packet Capture and Traffic Analysis | `tcpdump`, Wireshark, BPF filters, DNS/TCP/HTTP/TLS analysis | 3 | 16 |
| [CYB-205](level-2-tooling/05-ssh-secure-administration/index.md) | OpenSSH and Secure Remote Administration | Keys, `sshd` hardening, host verification, file transfer | 2 | 12 |
| [CYB-206](level-2-tooling/06-host-inspection-and-hardening/index.md) | Host Inspection, Hardening Assessment and Reporting | Accounts, permissions, services, sockets, Lynis, assessment report | 3 | 16 |

Hours are study time including labs. The level ends with the CYB-209 assessment (~5 hours).

---

## Labs at a glance

| Lab | Module | What you build or prove |
| --- | --- | --- |
| [LAB-201-01](level-2-tooling/01-lab-environment-and-kali/lab-01-prepare-kali-vm.md) | CYB-201 | Prepare and verify a Kali VM |
| [LAB-201-02](level-2-tooling/01-lab-environment-and-kali/lab-02-host-only-network.md) | CYB-201 | Configure host-only networking and record addresses |
| [LAB-201-03](level-2-tooling/01-lab-environment-and-kali/lab-03-connectivity-validation.md) | CYB-201 | Validate connectivity between lab hosts |
| [LAB-202-01](level-2-tooling/02-bash-python-git/lab-01-bash-security-check.md) | CYB-202 | Bash script checking local security settings |
| [LAB-202-02](level-2-tooling/02-bash-python-git/lab-02-python-log-parser.md) | CYB-202 | Python parser for synthetic network logs |
| [LAB-202-03](level-2-tooling/02-bash-python-git/lab-03-git-for-artifacts.md) | CYB-202 | Version lab artefacts with Git, safely |
| [LAB-203-01](level-2-tooling/03-host-discovery-and-enumeration/lab-01-host-discovery.md) | CYB-203 | Host discovery inside the isolated lab |
| [LAB-203-02](level-2-tooling/03-host-discovery-and-enumeration/lab-02-service-enumeration.md) | CYB-203 | Port and service enumeration of a local target |
| [LAB-203-03](level-2-tooling/03-host-discovery-and-enumeration/lab-03-tcp-udp-behaviour.md) | CYB-203 | Compare TCP and UDP behaviour |
| [LAB-203-04](level-2-tooling/03-host-discovery-and-enumeration/lab-04-netcat-local.md) | CYB-203 | Controlled `netcat` demonstrations |
| [LAB-204-01](level-2-tooling/04-packet-capture-and-analysis/lab-01-tcpdump-capture.md) | CYB-204 | Capture and inspect a pcap file |
| [LAB-204-02](level-2-tooling/04-packet-capture-and-analysis/lab-02-wireshark-analysis.md) | CYB-204 | Capture and analyse with Wireshark |
| [LAB-204-03](level-2-tooling/04-packet-capture-and-analysis/lab-03-protocol-analysis.md) | CYB-204 | DNS, TCP handshake, HTTP and TLS metadata |
| [LAB-205-01](level-2-tooling/05-ssh-secure-administration/lab-01-key-based-auth.md) | CYB-205 | Key-based SSH, proven from client and server evidence |
| [LAB-205-02](level-2-tooling/05-ssh-secure-administration/lab-02-harden-sshd.md) | CYB-205 | Audit and harden `sshd` without locking yourself out |
| [LAB-206-01](level-2-tooling/06-host-inspection-and-hardening/lab-01-host-inventory.md) | CYB-206 | Accounts, permissions, processes, sockets |
| [LAB-206-02](level-2-tooling/06-host-inspection-and-hardening/lab-02-lynis-assessment.md) | CYB-206 | Hardening assessment with Lynis, triaged |
| [LAB-206-03](level-2-tooling/06-host-inspection-and-hardening/lab-03-assessment-report.md) | CYB-206 | Report findings with the assessment template |

Eighteen labs, each mapped to one module. LAB-206-03 is the level's capstone assessment.

---

## Lab environment

| Host | Role | Address | Notes |
| --- | --- | --- | --- |
| `lab-kali` | Analyst workstation | `192.0.2.10/24` | Kali, host-only adapter |
| `lab-ubuntu` | Target and reference host | `192.0.2.20/24` | Ubuntu Server, host-only |
| `lab-win` | Secondary host | `192.0.2.30/24` | Optional in this level |

All traffic stays inside `192.0.2.0/24`. NAT is attached only for package installation and removed before any
scanning. See [Labs](../labs/index.md) for the canonical specification and the
[Lab Safety Guide](../start-here/lab-safety.md) for the build and isolation proof.

---

## Level assessment (CYB-209)

The [published Level 2 assessment](../assessments/level-2-assessment.md) is a timed practical (~4 hours) plus a
written justification (~90 minutes). In outline:

- Enumerate a provided lab host inside the range, documenting method and evidence.
- Capture and explain one traffic exchange.
- Produce a findings table that separates real findings from scanner noise.
- Justify your scan choices, and state what your evidence cannot show.

Weighting: reconnaissance 30, analysis 30, reporting 25, safety 15 — see the
[assessment blueprint](../policies/assessment-format.md#5-level-assessment-blueprint).

---

## Before you start

- Level 1 complete, including CYB-111 (isolated networking) and CYB-109 (Linux shell).
- 16 GB RAM preferred; 12 GB workable if you run hosts sequentially.
- Re-read the [Safety Policy](../policies/safety-policy.md). Scope discipline starts to matter in practice here,
  because the tools you are learning are the ones people misuse.

---

## Where learners get stuck

| Sticking point | Why it happens | What helps |
| --- | --- | --- |
| Treating scan output as fact | Scanners report possibilities | Verify a service by hand before writing a finding |
| Copying `nmap -A -T4` | It produces impressive output | Explain each flag in your notes or remove it |
| Reading a capture chronologically | Streams interleave and overwhelm | Follow one conversation; filter by host and port |
| Scripts that "mostly work" | No error handling | `set -euo pipefail`, input validation, explicit failures |
| Committing secrets or huge pcaps | Convenience | `.gitignore`, LAB-202-03, and review before commit |
| Reporting scanner output verbatim | Looks objective | Report weakness, evidence, impact, fix |
| Hardening `sshd` before keys work | Enthusiasm | Prove key access first; keep a session open |

---

## After Level 2

Continue to [Level 3 — Applications, Cryptography and Identity](level-3.md) or
[Level 4 — Defensive Operations](level-4.md). Level 3 first is recommended: detection engineering in Level 4 reads
web and authentication telemetry constantly.

---

## Related

- [Full roadmap](../curriculum/roadmap.md) · [Levels overview](index.md)
- [Labs](../labs/index.md) · [Lab Safety Guide](../start-here/lab-safety.md)
- [Assessment Report Template](../policies/assessment-report-template.md)

# Level 1 — Foundations

**~52 guided hours · 15 modules · 11 labs · Prerequisite: none**

!!! success "Status: published"
    All fifteen modules are written and available, with eleven labs, review questions, and knowledge checks.
    Labs are written for a two-VM isolated lab and have explicit scope, expected output, and teardown steps.

---

## What this level is about

Level 1 turns a competent computer user into someone who can explain what a system is doing and why. There
is no exploitation here and no "hacking tools" section: instead you build the foundations every later module
assumes.

- the vocabulary of risk — assets, threats, vulnerabilities, controls, impact;
- the law and ethics that decide whether an action is professional or criminal;
- how operating systems work: processes, permissions, filesystems, logs;
- how networks work: addressing, protocols, name resolution, transport, TLS;
- how to administer Linux and Windows rather than merely use them;
- how to build an isolated lab, prove it is isolated, and reset it on demand;
- how to read logs and diagnose a failure from evidence.

It is deliberately unglamorous. Learners who skip it spend Level 2 copying commands whose output they cannot
interpret.

---

## What you will be able to do

By the end of Level 1 you can:

- Explain the CIA triad, and distinguish a threat, a vulnerability, and a risk using a concrete system.
- State what makes testing authorised, and name the laws that make unauthorised access a crime.
- Model a small system with a data-flow diagram and STRIDE, and propose reductions to its attack surface.
- Trace an HTTP request from application to server, naming the protocol at each hop.
- Convert between CIDR notation and host ranges, and explain what a subnet contains.
- Administer an Ubuntu Server VM: users, permissions, services, packages, logs, SSH keys.
- Administer a Windows VM: accounts, ACLs, services, event logs, PowerShell inspection.
- Build a two-VM isolated lab, verify isolation with evidence, and reset it in minutes.
- Compute file hashes, detect tampering, and sign and verify a file.
- Triage a phishing email and assess a password policy using evidence rather than instinct.
- Diagnose a failing service from its logs and document the trail.

---

## Modules

| Code | Module | Focus | Hours | Status |
| --- | --- | --- | --- | --- |
| [CYB-101](level-1-foundations/01-introduction-to-cybersecurity/index.md) | Introduction to Cybersecurity | What security work is, the four activities, roles, the authorization rule | 1 | Published |
| [CYB-102](level-1-foundations/02-cia-triad-principles-risk/index.md) | CIA Triad, Security Principles and Risk | CIA, design principles, risk assessment and treatment | 2 | Published |
| [CYB-103](level-1-foundations/03-threats-vulnerabilities-controls/index.md) | Threats, Vulnerabilities, Exploits and Controls | Threat actors, vulnerability classes, CVSS, control types | 2 | Published |
| [CYB-104](level-1-foundations/04-threat-modeling-attack-surfaces/index.md) | Threat Modeling and Attack Surfaces | Data-flow diagrams, trust boundaries, STRIDE, surface reduction | 2 | Published |
| [CYB-105](level-1-foundations/05-ethics-authorization-disclosure-law/index.md) | Ethics, Authorization, Disclosure and Law | Authorization artefacts, disclosure, PECA 2016 and comparative law | 2.5 | Published |
| [CYB-106](level-1-foundations/06-computer-hardware-os-fundamentals/index.md) | Hardware, OS, Files, Processes and Permissions | Boot, kernel/user space, inodes, process states, permission models | 2.5 | Published |
| [CYB-107](level-1-foundations/07-networking-fundamentals/index.md) | Networking Fundamentals and OSI/TCP-IP | Layering, encapsulation, PDUs, where controls see traffic | 3 | Published |
| [CYB-108](level-1-foundations/08-addressing-and-protocols/index.md) | IP Addressing, Subnets and Core Protocols | IPv4/subnets, ARP, DNS, DHCP, TCP/UDP, HTTP, TLS | 4 | Published |
| [CYB-109](level-1-foundations/09-linux-command-line/index.md) | Linux Command-Line Fundamentals | Paths, files, permissions, processes, services, packages, logs | 3.5 | Published |
| [CYB-110](level-1-foundations/10-windows-powershell-basics/index.md) | Windows Fundamentals and PowerShell | Tokens, UAC, ACLs, services, event logs, object pipelines | 3 | Published |
| [CYB-111](level-1-foundations/11-virtualization-and-lab-networks/index.md) | Virtualization, Snapshots and Lab Networks | Hypervisors, adapter modes, snapshots, isolation proof | 3 | Published |
| [CYB-112](level-1-foundations/12-kali-linux/index.md) | Introduction to Kali Linux | What Kali is for, when native tools are better, safe setup | 1.5 | Published |
| [CYB-113](level-1-foundations/13-cryptography-hashing-signatures/index.md) | Cryptography, Hashing and Digital Signatures | Primitives, hashes, signatures, PKI, failure modes | 3 | Published |
| [CYB-114](level-1-foundations/14-passwords-mfa-phishing/index.md) | Password Security, MFA and Phishing Awareness | Credential attacks, storage, policy, MFA, phishing triage | 3 | Published |
| [CYB-115](level-1-foundations/15-security-logs-and-troubleshooting/index.md) | Security Logs and Basic Troubleshooting | Log sources, filtering, correlation, absence as evidence | 2.5 | Published |

Hours shown are lesson time. The eleven labs add roughly nine hours, and the readiness assessment
about four, which is where the level total of ~52 guided hours comes from.

Full descriptions and prerequisites: [roadmap](../curriculum/roadmap.md).

---

## Labs

Eleven labs, each with explicit scope, expected output, verification, teardown, reflection questions, and a
rubric. Full list: [Labs](../labs/index.md).

| Lab | Module | What you practise |
| --- | --- | --- |
| [LAB-107-01](../levels/level-1-foundations/07-networking-fundamentals/lab-01-capture-local-traffic.md) | CYB-107 | Capture a loopback HTTP exchange and read the handshake |
| [LAB-108-01](../levels/level-1-foundations/08-addressing-and-protocols/lab-01-network-configuration.md) | CYB-108 | Inspect and document network configuration |
| [LAB-108-02](../levels/level-1-foundations/08-addressing-and-protocols/lab-02-dns-lookups.md) | CYB-108 | Read DNS results, hosts overrides, negative answers |
| [LAB-109-01](../levels/level-1-foundations/09-linux-command-line/lab-01-files-permissions.md) | CYB-109 | Shared directory, setgid, sticky bit, access proof |
| [LAB-109-02](../levels/level-1-foundations/09-linux-command-line/lab-02-processes-listeners-logs.md) | CYB-109 | Map ports to processes; read access logs |
| [LAB-110-01](../levels/level-1-foundations/10-windows-powershell-basics/lab-01-windows-inspection.md) | CYB-110 | Inventory a Windows host; event 4720; cross-platform hash |
| [LAB-111-01](../levels/level-1-foundations/11-virtualization-and-lab-networks/lab-01-isolated-network.md) | CYB-111 | Build and prove an isolated virtual network |
| [LAB-113-01](../levels/level-1-foundations/13-cryptography-hashing-signatures/lab-01-hashing-integrity.md) | CYB-113 | Detect tampering; sign and verify with OpenSSL |
| [LAB-114-01](../levels/level-1-foundations/14-passwords-mfa-phishing/lab-01-phishing-triage.md) | CYB-114 | Triage three synthetic phishing emails |
| [LAB-114-02](../levels/level-1-foundations/14-passwords-mfa-phishing/lab-02-password-policy.md) | CYB-114 | Assess a fictional password policy and dataset |
| [LAB-115-01](../levels/level-1-foundations/15-security-logs-and-troubleshooting/lab-01-evidence-trail.md) | CYB-115 | Diagnose a broken service from logs alone |

---

## How the level runs

**Lab environment.** Two VMs on a host-only segment: Ubuntu Server and Windows 11 (or 10). Kali is introduced
in CYB-112 but not required for the labs. No vulnerable applications yet — that starts in Level 2.

**Rhythm.** One module per week at the standard pace. CYB-108 and CYB-111 are the heaviest; budget extra
time rather than rushing them, because everything later assumes both.

**Assessment.** Every module has a knowledge check and review questions; eleven modules have labs marked
against the lab rubric. The level ends with the readiness assessment below.

---

## Level assessment

The [published Level 1 assessment](../assessments/level-1-assessment.md) has two parts, and its model answers and
marking criteria are in the [answer key](../assessments/level-1-key.md#level-1-integrated-assessment-model-answers).

**Practical (~3 hours).** From a written brief: build an isolated network with two hosts, apply specified
accounts and permissions, verify isolation, capture one exchange, hash a file, and produce a findings
table — using only your own notes and the tool documentation.

**Written (~90 minutes).** Explain your network and addressing choices; justify one control per risk; state
what is and is not authorised; describe one finding you would escalate and why.

Marking uses the [level assessment blueprint](../policies/assessment-format.md#5-level-assessment-blueprint)
with these domain weights: networking 30, OS administration 30, lab design 25, ethics 15.

**Pass standard:** 60 overall, no component below 50, and a competent rating on safety. If you cannot rebuild
your lab from your own notes, repeat CYB-111 before continuing — that single capability predicts success in
the rest of the course better than anything else.

---

## Before you start

- Hardware: 8 GB RAM minimum, 16 GB recommended; 60–100 GB free disk; virtualization enabled.
- Software: a hypervisor, Ubuntu Server LTS, a Windows evaluation VM; Kali only when you reach CYB-112.
- Reading: [Prerequisites and Setup](../start-here/prerequisites.md), then the
  [Safety Policy](../policies/safety-policy.md).

---

## Where learners get stuck

| Sticking point | Why it happens | What helps |
| --- | --- | --- |
| Subnetting | It is arithmetic until it clicks | `ipcalc` drills in CYB-108; draw the bit boundary once by hand |
| "Why does ethics matter?" | Feels like paperwork | CYB-105's scenarios are real cases in miniature |
| Linux permissions | `rwx` looks arbitrary | LAB-109-01's setgid and sticky-bit demonstrations |
| Snapshot discipline | Feels like wasted time | The first corrupted VM changes your mind |
| Reading logs | Volume overwhelms | Filter by time, then unit, then pattern (CYB-115) |
| Wanting tools immediately | Tools feel like progress | Kali arrives at CYB-112, after the fundamentals |

---

## After Level 1

You are ready for [Level 2 — Tooling and Lab Craft](level-2.md), which assumes your lab works, your notes are
usable, and you can move around Linux and Windows without hesitating.

---

## Related

- [Full roadmap](../curriculum/roadmap.md) · [Levels overview](index.md)
- [Lab Safety Guide](../start-here/lab-safety.md) · [Prerequisites](../start-here/prerequisites.md)
- [Assessment Guide](../start-here/assessment-guide.md) · [Labs](../labs/index.md)

# Course Roadmap — Cyber Security Self-Study Program

**Version:** 1.0 (planning baseline) · **Date:** 28 October 2026
**Owner:** Engr. Dr. Muhammad Nadeem Majeed, Department of Data Science (PUCIT), University of the Punjab
**Status:** Approved structure for phased authoring; no lesson content published yet.

---

## 1. Purpose

This document defines the complete curriculum architecture for a public, self-paced
cybersecurity course: what is taught, in what order, at what depth, with which labs and
assessments, and how long each part should take.

It is the authoritative reference for authoring. Any proposed module, lab, or scope change is
measured against it, and changes are recorded in the changelog at the end of this file.

The course is built for learners who will work in defensive and offensive roles and who must
be able to explain, document, and justify what they do. It is therefore organised around
**understanding and evidence**, not around tool buttons.

---

## 2. Design principles

1. **Prerequisite-gated, not topic-sorted.** Each level unlocks the next. A learner never needs
   a concept that has not been introduced, or is told exactly where to go and get it.
2. **Defender-first framing.** Every offensive technique is paired with how it is detected,
   logged, prevented, and reported. Attack knowledge exists to improve defence.
3. **Lab before lecture-completion.** A module is not finished until a practical artefact exists:
   a capture, a report, a rule, a hardened host, a detection.
4. **Isolation by construction.** All practical work targets localhost, dedicated VMs,
   intentionally vulnerable applications, synthetic data, or an instructor-authorized range.
   The [safety policy](../policies/safety-policy.md) is a hard constraint on every lab design.
5. **Reproducibility.** Pinned versions, dated instructions, explicit expected output, and a
   reset path. "It worked on my machine" is a documentation defect.
6. **Evidence discipline.** Learners keep notes, screenshots, logs, and timestamps from Level 1,
   because reporting is the deliverable in professional security work.
7. **Exit-level competence, not tool familiarity.** Each level ends in an authentic task:
   assessment, investigation, or build — never a multiple-choice test alone.
8. **Public-safe content.** No live malware, no real credentials or personal data, no
   copy-paste exploitation of third-party systems in a public repository. Answer keys are the
   deliberate exception: they are learner-facing by design (see §12), because a self-study course
   with no marker has to let the learner check their own work.
9. **Maintainable by a small team.** Standard templates, a shared component library, and CI
   checks that fail loudly on broken links, broken builds, or leaked secrets.
10. **Accessible and honest.** Plain language, alt text, colour-independent meaning, stated
    limitations, and citations with access dates.

---

## 3. Audience and entry assumptions

| Audience | Starting point | Expected exit |
| --- | --- | --- |
| CS/DS/IT undergraduate | Programming basics, no security | Junior SOC analyst / security engineer intern level |
| Postgraduate or career-changer | Some scripting, some networking | Confident across defence and assessment fundamentals |
| Working IT professional | Sysadmin or developer experience | Security specialisation with documented lab portfolio |

**Assumed entry:** can use a computer fluently, can follow technical instructions, can install
software. **Not assumed:** Linux, networking theory, programming, prior security exposure.

**Hardware baseline for labs:** 16 GB RAM (8 GB workable with patience), 100 GB free disk,
64-bit CPU with virtualization extensions enabled, ability to run two VMs concurrently.
Software stack is specified per level; nothing commercial is required.

---

## 4. Progression model

```
                    CYB-100  Foundations
                        │  (security concepts, ethics, OS, networking, Linux, Windows, VMs)
                        ▼
                    CYB-200  Tooling & Lab Craft
                        │  (CLI, Python, recon, pcap, service analysis, vuln assessment)
                        ▼
        ┌───────────────┴───────────────┐
        ▼                               ▼
 CYB-300  Applications,          CYB-400  Defensive Operations
 Crypto & Identity                 (hardening, logging, SIEM, CTI, forensics, IR)
        │                               │
        └───────────────┬───────────────┘
                        ▼
                    CYB-500  Advanced Practice
                (PT methodology, AD, cloud, hunting,
                 malware analysis in sandbox, automation)
                        ▼
                    CYB-600  Capstone & Portfolio Review
```

CYB-300 and CYB-400 are siblings: a learner may take them in either order after CYB-200,
although CYB-300 → CYB-400 is the recommended sequence because web logs and web attack
telemetry are used heavily in detection engineering. CYB-500 requires both.

---

## 5. Level 1 — CYB-100 Foundations (~52 hours)

Goal: a learner can explain core security concepts, model a design, navigate Linux and Windows, read a
network capture, verify file integrity, and build an isolated lab. No exploitation.

| Code | Module | Focus | Core lab | Hours |
| --- | --- | --- | --- | --- |
| CYB-101 | Introduction to Cybersecurity | What security work is, the four activities, roles, the authorization rule | Personal evidence workspace | 1 |
| CYB-102 | CIA Triad, Security Principles and Risk | CIA, six design principles, qualitative risk, four treatments | Risk register for a chosen system | 2 |
| CYB-103 | Threats, Vulnerabilities, Exploits and Controls | Threat actors, vulnerability classes, CVSS reading, control taxonomy | Control map for one risk | 2 |
| CYB-104 | Threat Modeling and Attack Surfaces | Data-flow diagrams, trust boundaries, STRIDE, surface reduction | One-page threat model | 2 |
| CYB-105 | Ethics, Authorization, Disclosure and Law | Authorization artefacts, scope writing, coordinated disclosure, PECA 2016 | Scope statement plus scenario classification | 2.5 |
| CYB-106 | Hardware, OS, Files, Processes and Permissions | Boot, kernel/user space, inodes, process states, permission models | Permissions ladder and process ownership | 2.5 |
| CYB-107 | Networking Fundamentals and OSI/TCP-IP | Layering, encapsulation, PDUs, control placement | LAB-107-01 capture a local exchange | 3 |
| CYB-108 | IP Addressing, Subnets and Core Protocols | IPv4/subnets, ARP, DNS, DHCP, TCP/UDP, HTTP, HTTPS, TLS | LAB-108-01 network configuration, LAB-108-02 DNS | 4 |
| CYB-109 | Linux Command-Line Fundamentals | Paths, files, permissions, processes, services, packages, logs | LAB-109-01 permissions, LAB-109-02 processes and logs | 3.5 |
| CYB-110 | Windows Fundamentals and PowerShell | Tokens, UAC, ACLs, services, event logs, object pipelines | LAB-110-01 Windows host inventory | 3 |
| CYB-111 | Virtualization, Snapshots and Lab Networks | Hypervisors, adapter modes, snapshots, isolation proof, reset | LAB-111-01 isolated virtual network | 3 |
| CYB-112 | Introduction to Kali Linux | What Kali is for, when native tools are better, safe setup | Kali setup, credentials, snapshot, reset drill | 1.5 |
| CYB-113 | Cryptography, Hashing and Digital Signatures | Primitives, hashes, signatures, PKI, failure modes | LAB-113-01 hashing, integrity, signatures | 3 |
| CYB-114 | Password Security, MFA and Phishing Awareness | Credential attacks, storage, policy, MFA, phishing triage | LAB-114-01 phishing, LAB-114-02 password policy | 3 |
| CYB-115 | Security Logs and Basic Troubleshooting | Log sources, filtering, correlation, absence as evidence | LAB-115-01 evidence trail | 2.5 |

Hours are lesson time. The eleven labs add roughly 9.5 hours, and the level ends with the readiness
assessment (~4 hours), bringing the level to approximately 52 guided hours.

**Exit criteria:** can build and reset an isolated lab with isolation evidence; can explain how a packet
reaches a web server; can administer basic Linux and Windows tasks; can verify file integrity; can state, in
writing, what is and is not authorized; can diagnose a failing service from logs.

## 6. Level 2 — CYB-200 Tooling and Lab Craft (~90 hours)

Goal: operate tools correctly and safely, and document results like a professional. Reconnaissance
is limited to the learner's own lab subnet and localhost.

| Code | Module | Focus | Core lab | Hrs |
| --- | --- | --- | --- | --- |
| CYB-201 | Lab Environment, Kali and Network Foundations | Kali preparation, adapter modes, static addressing, connectivity record, evidence discipline | Prepare the analyst VM, configure host-only networking, validate connectivity | 12 |
| CYB-202 | Bash, Python and Git for Lab Work | Shell semantics, safe scripting habits, Python parsing and error handling, Git for artefacts and `.gitignore` discipline | Bash security check, Python log parser, Git-versioned artefacts | 16 |
| CYB-203 | Host Discovery and Service Enumeration | Host discovery, service/version detection, safe timing, output formats, scanner limitations, `netcat`, TCP vs UDP | Discover and enumerate your own lab; produce an inventory with evidence | 18 |
| CYB-204 | Packet Capture and Traffic Analysis | Capture points, BPF vs display filters, `tcpdump`, Wireshark, TCP streams, TLS metadata without decryption, capture as evidence | Capture, hash and analyse pcaps; write a protocol narrative | 16 |
| CYB-205 | OpenSSH and Secure Remote Administration | Key-based authentication, host verification, `sshd` hardening, safe change discipline, file transfer | Key-based access, then harden `sshd` and prove refusals | 12 |
| CYB-206 | Host Inspection, Hardening Assessment and Reporting | Accounts, permissions, processes, services, sockets, Lynis triage, professional reporting | Inventory a host, assess with Lynis, write the report | 16 |
| CYB-207 | Vulnerability Assessment Workflow *(planned)* | Scanner architecture, credentialed vs uncredentialed scans, false positives, CVSS reading, prioritisation, remediation advice | Run an authenticated scan of a lab VM; deliver a prioritised findings table | 12 |
| CYB-208 | Instrumenting Your Own Lab for Defence *(planned)* | Host logging, centralised log collection, monitoring your own actions, snapshots before/after, detecting your own scans | Enable logging and demonstrate a record of your own enumeration activity | 6 |
| CYB-209 | Level 2 Assessment | Practical exam plus written analysis | Assess a provided lab host, document method and evidence, propose remediation | 5 |

**Delivery note.** CYB-201–206 are published with eighteen labs. The earlier single "Lab Operations and Evidence
Discipline" module was absorbed into CYB-201, and the command-line, Python and service-protocol material was
regrouped into CYB-202 and CYB-203 so that each module ends with a deliverable a marker can inspect. CYB-207 and
CYB-208 remain planned: vulnerability assessment needs the web targets built in Level 3, and self-instrumentation
belongs with the logging work in Level 4.

**Exit criteria:** can explain and justify every command run; can read a capture; can distinguish
a real finding from a scanner artefact; can reproduce another learner's results from their notes.

---

## 7. Level 3 — CYB-300 Applications, Cryptography and Identity (~100 hours; ~68 published)

Goal: understand how applications fail and how to build, review, and test them responsibly.
All targets are intentionally vulnerable applications running locally.

| Code | Module | Focus | Core lab | Hrs |
| --- | --- | --- | --- | --- |
| CYB-301 | Web Architecture and HTTP for Security | Browser/server model, requests and responses, headers, cookies, sessions, same-origin policy, CORS, caching, proxies, devtools | Intercept and annotate a full session against a local app with devtools and a proxy | 8 |
| CYB-302 | Injection and Cross-Site Scripting | SQL injection mechanics and parameterisation, command injection, XSS types and context, output encoding, CSP, safe testing boundaries | Exploit and then fix injection and XSS in a local vulnerable app (DVWA / Juice Shop) | 14 |
| CYB-303 | Broken Access Control, Authentication, and Session Flaws | IDOR, vertical/horizontal privilege issues, auth logic flaws, session fixation, password storage, brute-force protection, MFA design | Reproduce and remediate an IDOR and an authentication bypass locally | 12 |
| CYB-304 | Server-Side Request Forgery, Deserialization, and File Handling | SSRF classes and allow-listing, path traversal, file upload validation, insecure deserialization concepts, template injection overview | Test and mitigate SSRF and path traversal in a local app | 12 |
| CYB-305 | Applied Cryptography | Symmetric/asymmetric primitives, modes and IVs, hashing vs encryption, password KDFs, MACs and AEAD, TLS configuration, PKI and certificate validation, common implementation mistakes | Break weak configurations in a local exercise; verify a hardened TLS setup; crack hashes you generated | 14 |
| CYB-306 | Identity, Access Management and Federation | AuthN vs AuthZ, RBAC/ABAC, least privilege, MFA, OAuth 2.0 and OIDC flows, JWT structure and pitfalls, SAML overview, session lifecycle, directory services basics | Audit a local OIDC flow; find and fix a JWT validation flaw in a provided sample | 12 |
| CYB-307 | Secure Coding and Threat Modeling | Secure SDLC, STRIDE and data-flow threat modeling, secure design patterns, input validation strategy, dependency and secret hygiene, security code review practice | Threat-model a small app and review a seeded vulnerable codebase | 12 |
| CYB-308 | API Security | REST and GraphQL authZ, object-level authorization, rate limiting, mass assignment, API inventory, schema exposure, token handling | Test a local API for BOLA and mass assignment; produce a fix plan | 10 |
| CYB-309 | Level 3 Assessment | Practical plus written defence of remediation decisions | Assess a local app end-to-end and write a client-style report with fixes | 6 |

**Exit criteria:** can name the class of a web flaw, demonstrate it locally, explain the root
cause in code, and prescribe a specific fix; can explain why a crypto choice is unsafe.

**Delivery note (29 October 2026).** Six of the nine rows above are published as modules CYB-301, CYB-302,
CYB-303, CYB-304, CYB-307 and CYB-308, with seventeen labs and approximately 68 guided hours. Module codes were
kept as planned rather than renumbered, so the published sequence reads 301–304 then 307–308 and the gap is
visible to learners.

Two changes were made to the planned shape, both recorded here because they alter the module boundaries:

- **File handling absorbed SSRF and misconfiguration.** The original CYB-304 combined SSRF, deserialisation and
  file handling. In practice SSRF is a request-forgery exercise with its own lab topology (an internal service the
  learner starts themselves), and misconfiguration is a deployment review rather than a code flaw. All three are
  taught, in one module with four labs, because they share the same precondition: a low-privilege foothold.
- **Secure coding absorbed the dependency work.** CYB-307 now covers threat modeling, code review, supply-chain
  analysis with an SBOM, and remediation verification. Splitting dependency scanning into its own module produced
  two thin modules and one weak deliverable; combined, the module ends with a remediation table where each row has
  a test that fails on the vulnerable version.

**Still outstanding:** CYB-305 (applied cryptography), CYB-306 (identity and federation), and CYB-309 (level
assessment). Their hours remain in the ~100-hour total, which is why the published figure is stated separately.
No lab in this level has yet been executed on a real VM pair; expected outputs are written to spec.

---

## 8. Level 4 — CYB-400 Defensive Operations (~86 hours; 7 modules, 22 labs)

Goal: run and improve defence: harden systems, build detections, triage alerts, investigate,
and respond. This level is the professional core of the program.

| Code | Module | Focus | Labs | Hrs |
| --- | --- | --- | --- | --- |
| CYB-401 | SOC Operations, ATT&CK and Threat Intelligence | Alert lifecycle, triage judgement, ATT&CK v20.0 mapping and its limits, indicator confidence and expiry, TLP, intelligence briefs | 3 | 10 |
| CYB-402 | Endpoint Telemetry and Authentication Monitoring | Windows Security log and audit policy, Sysmon 15.x with a community config, `journald` and `auth.log`, brute force vs spraying, telemetry limits | 3 | 12 |
| CYB-403 | Hardening, Baselines and Vulnerability Management | CIS/STIG/vendor/SCAP sources, OpenSCAP 1.4.6 and SSG 0.1.82, Lynis 3.1.7, Windows ASR/LAPS/logging controls, CVSS v4.0, KEV, EPSS v5, patch SLAs and exceptions | 3 | 12 |
| CYB-404 | Detection Engineering and SIEM | Hypothesis-driven rules, Sigma and correlation rules, Wazuh 4.14.9 deployment, normalisation, threshold/sequence/absence correlation, four tests, tuning without blind spots | 3 | 14 |
| CYB-405 | Network Defence and Monitoring | Zones and default deny, `nftables` with a verification matrix, sensor placement, Suricata 8.0.7, Zeek 9.0.1 LTS, what TLS hides, DNS tunnelling and beaconing analysis | 3 | 12 |
| CYB-406 | Digital Forensics | Forensic soundness, evidence register and custody, verified acquisition, The Sleuth Kit 4.12, MACB timelines, Autopsy 4.23.1, YARA 4.6.0, Volatility 3 mapping and limits | 3 | 14 |
| CYB-407 | Incident Response | NIST SP 800-61 Rev. 3 phases, roles, phishing triage and scope, master timeline with clock-skew correction, containment, simulated ransomware recovery, incident report and post-incident review | 4 | 12 |

**Exit criteria:** can harden a host against a documented baseline and prove the change, write a detection
that fires on generated activity and states its false-positive cost, triage an alert queue into a handover,
acquire and analyse evidence with custody intact, and produce a defensible incident report with owned actions.

**Delivery note (29 October 2026).** Seven modules are published, with 22 labs and 36 pages, replacing the ten
rows originally planned. The changes:

- **Linux and Windows hardening were merged (CYB-403).** The measure–change–verify loop is the same; only the
  tooling differs. Separate modules duplicated the reasoning and produced weaker evidence each.
- **Logging and detection were split (CYB-402 and CYB-404).** "Where does the telemetry come from" and "what do we
  query for" fail in different ways, and each needs its own labs.
- **Threat intelligence was folded into CYB-401** as its third lab, because a standalone eight-hour CTI module
  produced one weak deliverable.
- **CYB-410 moved into the assessment section.** It is published as the
  [Level 4 integrated assessment](../assessments/level-4-assessment.md), with marking criteria and model answers.

Versions were verified against primary sources rather than memory: OpenSCAP 1.4.6 (22 Oct 2026), SSG 0.1.82
(1 Sep 2026, Ubuntu 24.04 CIS profiles), Lynis 3.1.7 (25 Jun 2026), Wazuh 4.14.9 (8 GB/4 cores for single-node
Docker), Suricata 8.0.7, Zeek 9.0.1 LTS, YARA 4.6.0, Sysmon 15.22, Autopsy 4.23.1, NIST SP 800-61 **Rev 3**
(April 2025), ATT&CK **v20.0**, CIS-CAT Lite (free, registration required), and the 2026 NVD change that stopped
enrichment of every CVE (CVSS v4.0 supported; backlogged records may be "Not Scheduled").

**Verification status:** the prioritisation scoring script (LAB-403-03), the multi-source event generator
(LAB-404-03) and the DNS capture generator and analysis (LAB-405-03) were executed and their outputs checked.
No other lab has been run end to end on a real VM set; expected outputs are written to specification, and
browser-GUI steps have command-line equivalents.

---

## 9. Level 5 — Advanced Practice (~70 hours published; ~124 with the planned modules)

Goal: operate at professional depth in the two hardest areas (Active Directory, cloud), conduct
sanctioned assessments with real reporting discipline, and analyse hostile code safely.

| Code | Module | Focus | Final challenge | Hrs |
| --- | --- | --- | --- | --- |
| [CYB-501](../levels/level-5-advanced/01-penetration-testing/index.md) | Penetration Testing and Security Assessment | Rules of engagement, reconnaissance, validation, controlled exploitation, privilege escalation, evidence, risk rating, reporting, retest | Escalate, report, remediate, retest | 12 |
| [CYB-502](../levels/level-5-advanced/02-active-directory/index.md) | Active Directory Security | Domain architecture, Kerberos and NTLM, delegation, ACL paths, BloodHound and PingCastle, defensive auditing, hardening, recovery | Detect, harden, recover | 14 |
| [CYB-503](../levels/level-5-advanced/03-cloud-security/index.md) | Cloud Security | Shared responsibility, least privilege, object storage, segmentation, secrets, audit logs, misconfiguration scanning, containers | Container hardening | 11 |
| [CYB-504](../levels/level-5-advanced/04-malware-analysis/index.md) | Malware Analysis and Reverse Engineering | Static triage, PE structure, strings, capability detection, sandbox design, behavioural observation, YARA | YARA classification | 11 |
| [CYB-505](../levels/level-5-advanced/05-security-automation/index.md) | Security Automation | Log parsing, normalisation, offline enrichment, report merging, detection testing, guarded response automation | Guarded automation | 11 |
| [CYB-506](../levels/level-5-advanced/06-threat-hunting/index.md) | Threat Hunting and Detection Engineering | Falsifiable hypotheses, data requirements, beacon analysis, ATT&CK coverage, blind spots, tuning, validation | Validate and tune | 11 |
| CYB-507 | Reporting, Communication, and Professional Practice | Executive vs technical writing, risk language, remediation prioritisation, presenting findings, CV and portfolio | Executive brief plus technical annex | 6 |
| CYB-508 | Capstone Project and Portfolio Review | Self-directed project (see §10), supervised milestones, peer review, final defence | Capstone artefact, report and defence | 48 |

Modules 501–506 and all six **CYB-508 capstone briefs** are published; 507 is **not written**.

**Exit criteria:** can plan an engagement, operate in AD and cloud environments, hunt with
hypotheses rather than hope, analyse a sample without endangering the host, automate safely, and
defend your conclusions to a non-technical audience.

**Delivery note (29 October 2026).** Six of eight modules are published, with 18 labs and 30 pages.

- **The three advanced tracks were renumbered.** The plan had hunting as 504, malware as 505 and automation as 506.
  Published order is malware (504) → automation (505) → hunting (506), because hunting assumes the querying and
  testing habits the other two build, and it is a poor first module for a learner who has never parsed a log.
- **Cloud does not use LocalStack.** LocalStack now requires an account token before it will start, which would have
  forced a signup into a lab that promises none. CYB-503 uses MinIO for S3-compatible storage (with a real policy
  engine), static analysis of deliberately unsafe Terraform, a synthetic CloudTrail-style extract, and Docker image
  scanning. Cost: zero, and no account.
- **Advanced offensive content stays in dedicated labs.** CYB-501 tests only a lab target; CYB-502 builds its own
  `lab.local` forest; privilege escalation is confined to those VMs. No module enumerates or exploits a public system.
- **CYB-508 now has six published briefs** — network assessment, web application security, SOC investigation,
  Linux hardening, threat detection, and security automation — each with a 100-mark rubric, starter data and a
  reference solution whose outputs were measured by running it. **CYB-507 remains unwritten**, so the level still
  ends without its reporting module. That is a gap, not a decision.
- **Verification is uneven and stated per lab.** Executed and checked: the LAB-505-01 parser (13 events, 3 malformed
  lines skipped, 7 tests passing), LAB-505-02 enrichment and merge (13 events → 10 IOC hits; 6 findings → 4),
  LAB-505-03 containment refusal paths and mock API (exit codes 0/1/2/3/4 and bounded retries observed), LAB-506-01
  generator and interval analysis (36 connections, mean 300s, CV 0.019 against a benign backup at CV 0.000),
  LAB-506-02 coverage audit (18 rules, 16 techniques, 7 overclaims), LAB-506-03 tuning measurement (precision 0.27 →
  1.00 with recall 1.00 → 0.62). **Not executed:** the MinIO, Checkov, Trivy, BloodHound, PingCastle, capa and YARA
  walkthroughs, and every VM-based step. Those pages are written to specification with expected-output patterns, not
  verified transcripts, and students should treat them accordingly.

---

## 10. Capstone routes (CYB-508, choose one of six briefs)

The four routes below are the conceptual categories. The [six published briefs](../projects/index.md) instantiate
them: assessment → briefs 1–2, defensive build → 3–4, engineering → 4–6, applied research → brief 5 or an extension.

| Option | Deliverable | Evidence required |
| --- | --- | --- |
| A — Defensive build | Monitored, hardened lab with three working detections and an IR playbook | Architecture diagram, hardening baselines, Sigma rules with test results, tabletop record, post-incident review |
| B — Offensive assessment | Full assessment of an instructor-provided lab range | Scope and RoE, methodology log, findings with reproduction steps, risk ratings, remediation advice, retest plan |
| C — Engineering | A small security tool or automation with tests and documentation | Threat model, design, code with tests, usage docs, measured outcome |
| D — Applied research | Threat-intelligence or technique study with defensive recommendations | Research question, method, ATT&CK mapping, evidence, limitations, defence guidance |

**Common requirements:** reproducibility notes, ethical statement, references with access dates,
and a signed declaration that all activity stayed inside the authorized scope. Each brief carries its own 100-mark
rubric, a submission checklist and a reference solution; see [Capstone Projects](../projects/index.md).

---

## 11. Time budget and study plans

| Plan | Duration | Weekly load | Notes |
| --- | --- | --- | --- |
| Standard (2 semesters) | 32 weeks | 12–14 h | One level per 6–7 weeks; capstone in the final 6 weeks |
| Extended (self-paced) | 12–18 months | 6–8 h | Recommended for working learners; levels may be paused between modules |
| Fast track | ~10 weeks | 15 h | ~150 h: CYB-102/103/105/106/108, CYB-202/203/204/205, CYB-301/302/303, CYB-401/404/405. Not a substitute for the full program |
| Assessment-only | — | — | Experienced practitioners may attempt level assessments directly; capstone still required for the certificate of completion |

Total guided content: **≈482 hours**. Practice, note-taking, and revision typically add 30–40%.

---

## 12. Assessment architecture (summary)

| Type | Frequency | Weight in level result | Public? |
| --- | --- | --- | --- |
| Module quiz (5 items per module, 200 in total) | Per module | 15% | Questions and explained key both public, on separate pages |
| Practical lab rubric (4 criteria, 5 bands) | Per module | 45% | Rubric public |
| Level assessment (practical + written, 70/30) | Per level | 40% | Brief, criteria and model answers public |
| Capstone, one of six briefs | Once | 100 marks, pass/merit/distinction | Brief, rubric, starter data and reference solution public |

Full assessment system: [Assessments](../assessments/index.md). The reasoning for publishing keys, and what it
costs, is in [How Assessment Works §7](../policies/assessment-format.md#7-answer-keys-and-publication-rules).

Full rubrics, blueprints, and integrity rules: [assessment-format.md](../policies/assessment-format.md).

---

## 13. Module page anatomy (authoring contract)

Every module directory contains, at minimum:

```
NN-module-slug/
├── index.md          # overview, outcomes, prerequisites, reading order
├── 01-topic.md       # lessons following the lesson template
├── 02-topic.md
├── lab-01-....md     # practicals following the lab template
└── assets/           # diagrams, sanitised captures, sample data
```

Module front matter must declare: code, level, prerequisites, estimated hours, difficulty,
lab count, assessment, safety classification, version, and `last_reviewed` date.

---

## 14. Coverage map against the proposed level list

The five-level progression supplied by the instructor is preserved. Adjustments made for
coherence, with reasons:

| Proposed area | Placement in this roadmap | Adjustment and reason |
| --- | --- | --- |
| Foundations, ethics, computing, networking, Linux, Windows, virtualization | L1 (CYB-101…115) | Added explicit orientation/study-method module and a readiness assessment; virtualization expanded to include isolation verification and reset strategy, because lab safety depends on it |
| Security tools, reconnaissance, packet analysis, scripting, vulnerability assessment, lab operations | L2 (CYB-201…206 published) | Reconnaissance scoped to the learner's own lab. Networking and Kali preparation open the level so the analyst host is built before it is used; enumeration folds service/protocol interpretation into the discovery module; SSH and host hardening were added as modules because remote administration is taught, not assumed. Vulnerability assessment and self-instrumentation move to Levels 3 and 4 where their targets and log sources exist |
| Web security, cryptography, IAM, secure coding, common vulnerabilities | L3 (CYB-301…308) | Split web topics into four modules by failure class; added API security (a dominant real-world gap); cryptography taught as applied engineering, with encoding/hashing literacy introduced earlier in CYB-104 |
| Defensive security, hardening, logging, CTI, SIEM, forensics, IR | L4 (CYB-401…409) | Threat intelligence moved here from L5: it is a detection input, not an advanced specialism; forensics and IR given separate modules with evidence-handling emphasis |
| Advanced PT methodology, AD, cloud, threat hunting, malware analysis, automation, capstone | L5 (CYB-501…508) | Malware analysis constrained to sandboxed, instructor-supplied or synthetic samples; automation paired with guardrails and testing; added professional communication as its own module because reporting is the actual deliverable |

Deliberate exclusions from the core path (candidates for an elective track): hardware/embedded
security, ICS/SCADA, mobile application security, red-team adversary emulation at scale, and
formal cryptography mathematics. They are noted so learners know what the course does **not**
cover rather than assuming completeness.

---

## 15. Release gates and milestones

| Milestone | Definition of done |
| --- | --- |
| M0 — Planning baseline | This roadmap, progress report, standards, and safety policy exist and are reviewed |
| M1 — Site live | Framework, navigation, search, CI checks, and GitHub Pages deployment work end to end with a single published page |
| M2 — Level 1 complete | All 8 modules published, every lab verified on a clean VM, readiness assessment available |
| M3 — Level 2 complete | Includes a working sample-evidence set and replayable lab notebooks |
| M4 — Level 3 complete | Vulnerable-app versions pinned, all exploit steps reproducible offline |
| M5 — Level 4 complete | SIEM and logging labs rebuilt from scratch by a second reviewer |
| M6 — Level 5 complete | AD and cloud labs bounded by explicit cost and scope statements |
| M7 — Capstone ready | Four capstone briefs, rubrics, and exemplar (redacted) reports |
| M8 — Public launch | Link check, secret scan, accessibility pass, legal review of offensive content, published release notes |

---

## 16. Open decisions for the instructor

These do not block authoring of Levels 1–2 but must be settled before Level 4–5 publication.

1. **Credentialing:** is a certificate of completion issued, and by whom? This determines
   assessment rigour and identity verification.
2. **Cohort support:** does the course run with scheduled cohorts and a discussion channel
   (GitHub Discussions is currently disabled), or is it purely self-paced?
3. **Closed-book assessment variants:** keys are published (§12), so a cohort that needs a
   proctored, closed-book test needs a second item bank that is *not* published. Not written.
4. **Language:** English only, or an Urdu-language companion track for local accessibility?
5. **Scope of live external platforms:** may optional exercises use third-party ranges
   (for example TryHackMe or Hack The Box) that require their own accounts and terms? If yes,
   the safety policy needs a clause distinguishing "authorized by that platform's terms" from
   "authorized by this course".
6. **Licence:** content licence (for example CC BY-NC-SA 4.0) and code licence (for example MIT),
   plus a third-party attribution policy.

---

## Changelog

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-28 | Initial curriculum architecture created after repository audit |

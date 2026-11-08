# Cyber Security with Kali Linux - A Guided Self-Study Program

A complete, safety-first cybersecurity curriculum for university students and independent learners: from first
principles to a portfolio-grade capstone. It is written to be studied alone or taught in a classroom, and every
practical exercise runs in a lab the learner builds and controls.

**Status:** 40 modules, 86 labs, 223 pages, 200 keyed self-check questions, five integrated level assessments and
six capstone briefs — roughly **400 guided hours**, against about 480 in the full plan. Levels 1 and 4 are complete;
Levels 2, 3 and 5 each have six of their eight modules. The six unwritten modules are named in the
[roadmap](docs/curriculum/roadmap.md) and have no page, so a module never appears in the navigation as if it were
available. Every page states its own status, and nothing is presented as finished before it exists.

---

## Instructor

Engr. Dr. Muhammad Nadeem Majeed  
Professor  
Department of Data Science (PUCIT)  
University of the Punjab, Lahore, Pakistan.

---

## Intended audience

- **University students** in computing, data science, information technology or a related discipline, including
  those who have not studied security before.
- **Career changers and working professionals** moving into security, who want a sequence rather than a pile of
  tutorials.
- **Self-taught learners** who already know some tools and want the judgement behind them: scope, evidence,
  reporting, and knowing when *not* to act.
- **Instructors** who need a ready curriculum with labs, rubrics and answer keys they can adapt.

No prior security experience is assumed. The course is not aimed at experienced practitioners seeking advanced
exploit development, and it does not cover hardware or embedded security, ICS/SCADA, mobile application security,
or large-scale adversary emulation.

---

## Prerequisites

| Requirement | Minimum | Recommended |
| --- | --- | --- |
| Computer | 64-bit, virtualization enabled in firmware | 4 cores, SSD |
| RAM | 8 GB (workable but slow with two virtual machines) | 16 GB |
| Free disk | 60 GB | 100 GB |
| Operating system | Windows, macOS or Linux capable of running a hypervisor | Any, with a second Linux host or VM |
| Prior knowledge | Comfort using a computer and following technical instructions | Some programming helps from Level 2 onwards |
| Software | Free only: a hypervisor, Linux and Windows evaluation images, Python 3, a browser | See the setup guide |

No paid software, subscription, cloud account or textbook is required. Level 5's cloud labs use local emulation
and cost nothing. Full detail: [Prerequisites and Setup](docs/start-here/prerequisites.md).

---

## Learning outcomes

By the end of the program, a learner who has completed the labs and assessments can:

1. Explain how systems, networks and identities fail, using the vocabulary of risk rather than of tools.
2. Build, verify, snapshot and reset an isolated lab, and prove that it is isolated.
3. Administer Linux and Windows hosts from the command line, and inspect their security-relevant state.
4. Enumerate a lab network and validate findings before rating them.
5. Identify, reproduce and explain common web, API and identity vulnerabilities — and fix them in code.
6. Detect, investigate and report a security incident from logs, telemetry and packet captures.
7. Assess and harden systems against a baseline, with measured before-and-after evidence.
8. Automate security work safely, with tests, guardrails and honest failure reporting.
9. Write findings for technical and non-technical audiences, including limitations and residual risk.
10. Plan and defend a scoped piece of professional work end to end.

---

## Course levels and learning sequence

| Level | Theme | Modules | Labs | Guided hours |
| --- | --- | --- | --- | --- |
| [1 — Foundations](docs/levels/level-1.md) | Security concepts, ethics and law, computing, networking, Linux, Windows, virtualization, cryptography basics | 15 | 11 | ~52 |
| [2 — Tooling and Lab Craft](docs/levels/level-2.md) | Command line, scripting, reconnaissance, packet analysis, SSH, host assessment | 6 of 8 | 18 | ~90 |
| [3 — Applications, Cryptography and Identity](docs/levels/level-3.md) | HTTP and browser security, injection, access control, file handling, secure coding, APIs | 6 of 8 | 17 | ~68 |
| [4 — Defensive Operations](docs/levels/level-4.md) | SOC operations, endpoint telemetry, hardening, detection and SIEM, network defence, forensics, incident response | 7 | 22 | ~86 |
| [5 — Advanced Practice](docs/levels/level-5.md) | Engagement methodology, Active Directory, cloud, malware analysis, security automation, threat hunting | 6 of 8 | 18 | ~70 |
| [Capstone](docs/projects/index.md) | Six briefs: network assessment, web application security, SOC investigation, Linux hardening, threat detection, security automation | — | — | ~48 |

**Sequence.** Level 1 → Level 2 → Levels 3 and 4 (either order, though Level 3 supplies the web and identity
knowledge Level 4 assumes) → Level 5 → capstone. Each level ends with an integrated assessment. A compressed
fast track of about 150 hours exists for experienced learners, but it is not a substitute for the full program:
[Learning Sequence](docs/start-here/learning-sequence.md).

---

## Key topics

- **Foundations:** the CIA triad and risk, threats and controls, threat modelling, ethics and authorization,
  operating-system internals, networking from layers to protocols, Linux and Windows administration.
- **Lab craft:** virtualization and isolation, Kali in context, Bash, Python, Git, Nmap, tcpdump and Wireshark,
  OpenSSH, host inspection and hardening assessment.
- **Applications and identity:** HTTP and the browser security model, SQL injection and XSS, broken access
  control, session and authentication flaws, file handling and SSRF, API authorization, secure coding and
  dependency risk.
- **Defensive operations:** SOC triage, Windows and Linux telemetry, Sysmon, baselines and patch prioritisation,
  Sigma and Wazuh detection engineering, network segmentation and Suricata, disk and memory forensics, incident
  response.
- **Advanced practice:** rules of engagement and reporting, Active Directory attack paths and hardening, cloud
  IAM and storage exposure, sandboxed malware analysis and YARA, guarded automation, hypothesis-driven hunting.
- **Professional practice:** evidence handling, risk rating, remediation and retest, executive and technical
  writing, and a defended capstone.

---

## Tools used in the course

All are free or have a free edition. Versions are stated in each lab, because commands and output change between
releases; learners are taught to check the version before following instructions.

| Area | Tools |
| --- | --- |
| Platform | VirtualBox or VMware Workstation Player, Kali Linux, Ubuntu Server, Windows evaluation images, Docker |
| Network | `ip`, `ss`, `ping`, `traceroute`, `dig`, `curl`, `netcat`, Nmap, tcpdump, Wireshark, Suricata, Zeek |
| Web and API | Browser developer tools, Burp Suite Community Edition, OWASP Juice Shop, the course sample application |
| Systems | Bash, Python 3, Git, OpenSSH, Lynis, OpenSCAP, `auditd`, `journald`, PowerShell, Sysmon |
| Defensive | Wazuh, Sigma, YARA, The Sleuth Kit, Autopsy, Volatility 3 |
| Identity and cloud | Active Directory lab, BloodHound Community Edition, PingCastle, MinIO, Checkov, Trivy |
| Assessment | `pytest`, the course's synthetic datasets, spreadsheets or a local SIEM |

Kali is taught as one tool among several, not as the right answer to every task. Where a standard Linux host, a
built-in Windows tool, or a spreadsheet is the better choice, the course says so.

---

## Practical lab philosophy

- **Isolation first.** Every exercise runs on a host-only or internal virtual network, in a container bound to
  loopback, against a deliberately vulnerable application, or on synthetic data. Every lab states its scope and
  how to verify isolation.
- **Nothing real is at risk.** Lab targets are built by the learner, provided by the course, or supplied by an
  instructor. Real customer data, real accounts and public systems are out of scope by design.
- **Evidence, not screenshots of success.** Labs require commands, output, timestamps and hashes, so a result can
  be replayed by someone else.
- **Reversibility.** Snapshots, reset procedures and teardown steps are part of each lab, because a broken lab
  should cost minutes, not an evening.
- **No live malware.** Malware analysis uses inert artefacts, legitimate binaries and simulated behaviour.
- **Defender-first.** Offensive technique is taught so that detection and prevention can be improved, and every
  technique is paired with how it is caught.

The binding rules are in the [Safety Policy](docs/policies/safety-policy.md); the practical build steps are in the
[Lab Safety Guide](docs/start-here/lab-safety.md).

---

## Ethical and legal boundaries

This course teaches techniques that are illegal when used without authorization. The boundary is not the tool,
the intent, or the educational purpose — it is **written authorization from the owner of the system, within a
defined scope**.

- Test only systems you own, systems inside your isolated lab, deliberately vulnerable applications provided for
  the course, or a range you have been given written authorization to use.
- Do not scan, probe or exploit public systems, shared networks, employers' systems, or anyone else's devices —
  not "briefly", not "just to check", not "for a class".
- Authorization is specific: targets, time window, permitted techniques, and a contact. A verbal "go ahead" is not
  authorization.
- Unauthorized access is a criminal offence in most jurisdictions, including under Pakistan's Prevention of
  Electronic Crimes Act 2016. "I was studying" is not a defence.
- Findings about third-party software follow responsible disclosure, not publication.
- Data encountered in a lab is synthetic or explicitly provided; real personal data is never used as practice
  material.

Violating scope is treated as a serious conduct failure, not a technical error, and it voids any assessment it
occurs in.

---

## How to use these materials

The rhythm is the same at every level:

1. **Read the module overview and its outcomes** so you know what "finished" means.
2. **Read the lesson**, then close it and write the key ideas in your own words.
3. **Do the lab before the quiz.** The lab is where the level is earned; the quiz checks vocabulary and judgement.
4. **Check yourself honestly.** Attempt the module quiz on paper, then mark it against the published key and record
   each answer as correct, wrong, or *right for the wrong reason*. Target 4 of 5.
5. **Write it down.** Every module produces an artefact — a report, a detection, a hardened host, a capture — and
   those artefacts become your portfolio.
6. **Take the level assessment** when the modules are done, then move on.

Study time is a guide, not a deadline; practice, notes and revision typically add 30–40%. The
[Assessment Guide](docs/start-here/assessment-guide.md) explains how to mark your own work without flattering
yourself, and [How to Study](docs/start-here/how-to-study.md) covers the routine.

---

## Self-assessment and capstone

Because the course is usable without an instructor, assessment is built to be self-marked:

| Component | What it is | Where |
| --- | --- | --- |
| Module quizzes | 200 items across 40 modules, with multiple choice, short answer, scenario and troubleshooting items | [Assessments](docs/assessments/index.md) |
| Answer keys | Explained answers, plus acceptable-reasoning criteria for open questions, on separate pages | Each level key |
| Lab rubrics | Four criteria — correctness, methodology, evidence, safety — with published bands | Each lab |
| Level assessments | Practical task plus written justification, marked against published criteria | End of each level |
| Capstone | One of six briefs, each with a 100-mark rubric, starter data and a reference solution | [Projects](docs/projects/index.md) |

The answer keys are published deliberately: a self-study learner has nobody else to mark their work. The
trade-off, and the protocol for using them honestly, is in
[How Assessment Works](docs/policies/assessment-format.md#7-answer-keys-and-publication-rules).

**Certificates.** No certificate is currently offered. A credential would require instructor review of a capstone;
self-marked results are not a credential. That remains an open decision for the instructor.

---

## Published website

A published website URL for this course has **not been verified**, so none is given here and none should be assumed
from the repository name. The complete course is readable in this repository, starting at
[docs/index.md](docs/index.md), and it is structured so that the same pages can be published as a searchable
static site once the repository owner enables and verifies hosting. When that happens, the verified URL belongs in
this section and nowhere else.

---

## Repository navigation

| If you want to… | Open |
| --- | --- |
| Start the course | [Start Here](docs/start-here/index.md) |
| See what the program covers and why | [Full Roadmap](docs/curriculum/roadmap.md) |
| Compare the five levels | [Levels Overview](docs/levels/index.md) |
| Build your lab | [Prerequisites](docs/start-here/prerequisites.md) → [Lab Safety Guide](docs/start-here/lab-safety.md) |
| Do the practical work | [Lab Catalogue](docs/labs/index.md) |
| Check your understanding | [Assessments](docs/assessments/index.md) |
| Plan the capstone | [Project Guide](docs/start-here/project-guide.md) → [Six Briefs](docs/projects/index.md) |
| Read the binding rules | [Safety Policy](docs/policies/safety-policy.md) |
| Look up a term | [Glossary](docs/resources/glossary.md) |
| Know who wrote and teaches it | [Instructor](docs/instructor/index.md) |

Maintainers, teaching assistants and technical contributors start at [CONTRIBUTING.md](CONTRIBUTING.md); the
authoring and build documentation is in [docs/maintainer/](docs/maintainer/index.md). Neither is needed to study
the course.

---

## Academic and educational-use notice

This material is provided for education and authorised security practice. It is not professional security advice,
not a guarantee that any system is secure, and not a licence to test anyone else's systems. The instructor and the
University of the Punjab accept no liability for misuse, for damage caused by following the material outside an
authorised lab, or for decisions taken on the basis of it.

Learners are expected to comply with their institution's academic-integrity rules, with local law, and with the
[Safety Policy](docs/policies/safety-policy.md). When using this material in a course, assessment or publication,
attribute it and do not present another person's work or evidence as your own.

**Licence:** no licence has been chosen yet. Until one is, treat the material as all rights reserved and ask before
redistributing or adapting it.

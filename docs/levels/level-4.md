# Level 4 — Defensive Operations

**~86 guided hours · 7 modules · 22 labs · Prerequisite: Level 2 (Level 3 recommended)**

!!! note "Status: published"
    All seven modules are written, with 36 pages and 22 labs, and the level assessment is published as the
    [Level 4 integrated assessment](../assessments/level-4-assessment.md). Verification on a real VM pair is
    outstanding for every lab except the prioritisation exercise, whose code was executed.

---

## What this level is about

This is the professional core of the course: what defensive teams actually do all day.

Four activities repeat in every security operations role — **harden, detect, investigate, respond** — and this level
teaches all four with real tooling in a lab you control. You will apply a baseline to a host and prove the difference.
You will write a detection rule, test it against activity you generated, and tune out the noise. You will triage
alerts rather than admire dashboards. You will investigate a compromise, preserve evidence, and write the report your
manager would need to read.

The emphasis throughout is on **judgement**: which alert matters, which control is worth its friction, what the
evidence can support, and what you would do differently next time.

---

## What you will be able to do

By the end of Level 4 you can:

- Triage an alert queue by asset criticality, exploitability and evidence, and write a handover another analyst can
  continue.
- Map observed behaviour to MITRE ATT&CK v20.0, name the data source that would confirm it, and say how the mapping
  could be wrong.
- Assess a Linux host against a CIS Level 1 profile with OpenSCAP, and a Windows host against controls you can query.
- Prioritise a vulnerability list using KEV, EPSS v5, exposure and asset value — and defend the order in writing.
- Deploy a local Wazuh SIEM, write Sigma rules as portable specifications, and test each rule four ways.
- Segment a lab network with `nftables`, prove the denied paths fail, and place an IDS where it sees the traffic you
  care about.
- Acquire disk and memory evidence with verified hashes, build a UTC timeline, and classify artefacts with YARA.
- Run an incident from declaration to verified recovery, including a phishing triage, a simulated ransomware
  response, and a report with root cause and owned actions.

---

## Modules

| Code | Module | Focus | Labs | Hours |
| --- | --- | --- | --- | --- |
| [CYB-401](level-4-defensive-operations/01-soc-operations/index.md) | SOC Operations, ATT&CK and Threat Intelligence | Alert lifecycle, triage judgement, ATT&CK mapping, indicator confidence, brief writing | 3 | 10 |
| [CYB-402](level-4-defensive-operations/02-endpoint-telemetry/index.md) | Endpoint Telemetry and Authentication Monitoring | Windows Security log, Sysmon, `journald`, `auth.log`, authentication patterns, telemetry limits | 3 | 12 |
| [CYB-403](level-4-defensive-operations/03-hardening-and-patching/index.md) | Hardening, Baselines and Vulnerability Management | CIS/STIG/SCAP, OpenSCAP and Lynis, Windows controls, KEV/EPSS/CVSS, patch SLAs, exceptions | 3 | 12 |
| [CYB-404](level-4-defensive-operations/04-detection-and-siem/index.md) | Detection Engineering and SIEM | Hypothesis-driven rules, Sigma, Wazuh, normalisation, correlation, four tests, tuning | 3 | 14 |
| [CYB-405](level-4-defensive-operations/05-network-defence/index.md) | Network Defence and Monitoring | Zones and default deny, `nftables`, sensor placement, Suricata, TLS limits, DNS behaviour | 3 | 12 |
| [CYB-406](level-4-defensive-operations/06-digital-forensics/index.md) | Digital Forensics | Soundness, custody, verified acquisition, Sleuth Kit, MACB timeline, YARA, Volatility mapping | 3 | 14 |
| [CYB-407](level-4-defensive-operations/07-incident-response/index.md) | Incident Response | NIST SP 800-61 Rev. 3 phases, phishing scope, master timeline, containment, ransomware recovery, reporting | 4 | 12 |

**22 labs**, catalogued with times in the [lab index](../labs/index.md). Every lab states its authorized scope in an
admonition, and every offensive technique is simulated on the learner's own hosts.

---

## How the level changed from the original plan

The roadmap planned ten modules. Delivered as seven, because several planned modules produced no distinct artefact:

- **Linux hardening and Windows hardening became one module (CYB-403).** The measure–change–verify loop is identical;
  only the tooling differs. Keeping them separate duplicated the reasoning and halved the evidence each module
  produced.
- **Logging, detection engineering and SIEM became two modules (CYB-402 for telemetry, CYB-404 for rules and
  correlation).** This is the opposite move, for the opposite reason: "where does the data come from" and "what do we
  do with it" fail in different ways and deserve separate labs.
- **Threat intelligence folded into CYB-401.** A standalone CTI module was eight hours of reading with one weak
  deliverable. As the third lab of SOC operations, the brief is written for a consumer who has to act on it.
- **The level assessment moved to the assessment section.** CYB-410 now exists as the
  [Level 4 integrated assessment](../assessments/level-4-assessment.md), with its marking criteria and model answers,
  rather than as a module-level page.

---

## How the level runs

**Lab environment.** Your existing lab plus `lab-siem` (the `lab-monitor` role) with **8 GB RAM and 4 cores** for a
single-node Wazuh deployment, and a second internal network for the simulated DMZ in CYB-405. Run the SIEM and one
other VM at a time on a 16 GB host.

**Simulated activity, not real attacks.** Detection exercises use scripted, safe activity that mimics technique
behaviour — you generate the events yourself and then detect them. Forensic evidence is synthetic, built in the lab.
The ransomware exercise renames mock files; it does not encrypt anything.

**Sequence.** 401 → 402 → 403 → 404 → 405 → 406 → 407 is the intended order: judgement, then telemetry, then the
controls that generate the telemetry, then rules, then the network view, then evidence handling, then response. 406
and 407 can swap if you are preparing for an incident-response role.

**Assessment.** Each module ends with a rubric-marked lab that produces a durable artefact: a triage handover, a
before/after baseline, a tested detection, a segmentation matrix, an evidence register, an incident report.

---

## What you need before starting

- Level 2 complete; Level 3 strongly recommended (web and identity logs dominate triage).
- RAM to run several VMs concurrently, or patience to run them in sequence.
- The [Safety Policy](../policies/safety-policy.md) — evidence handling and scope rules apply to investigations too.
- A snapshot discipline: every lab that changes a host says so, and every one has a teardown section.

---

## Where learners get stuck

| Sticking point | Why it happens | What helps |
| --- | --- | --- |
| Alert volume | Everything looks urgent at first | Triage by asset criticality and technique, not by severity label |
| Detection rules that never fire | Wrong log source, wrong field, wrong normalisation | Test with `wazuh-logtest` before generating traffic; verify the parent SID |
| "The SIEM is the skill" | Tools change; reasoning does not | Focus on data sources and hypotheses; the SIEM is a query engine |
| Baselines that break things | Applying a profile wholesale | One control at a time, snapshot, verify by querying state |
| Forensics by screenshot | Breaks custody and reproducibility | Acquire, hash, document; work on the copy |
| Containment without evidence | Natural instinct to "just fix it" | Preserve first, then contain, and record the order |
| Timelines without timezones | Sources use local time | Convert everything to UTC and state the correction |

---

## After Level 4

[Level 5 — Advanced Practice](level-5.md) extends this into Active Directory, cloud, threat hunting and automation —
all of which assume you can already detect and respond competently on a single host.

---

## Related

- [Full roadmap](../curriculum/roadmap.md) · [Levels overview](index.md)
- [Lab catalogue](../labs/index.md) — environment specification and all 22 Level 4 labs
- [Assessment Guide](../start-here/assessment-guide.md)
- [Progress report](../maintainer/progress-report.md) — what is published, what is not, and why

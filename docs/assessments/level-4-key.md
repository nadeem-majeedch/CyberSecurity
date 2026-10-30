---
title: "Level 4 Answer Key"
description: "Answers and explanations for all 35 Level 4 items, plus marking criteria for the detection-and-response assessment."
module_code: ASM-L4K
level: 4
kind: assessment
prerequisites: [CYB-401]
estimated_minutes: 50
difficulty: advanced
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, answer-key, level-4, detection, incident-response]
---

# Level 4 Answer Key

!!! warning "Attempt first"
    Attempt the [Level 4 quiz](level-4-quiz.md) before reading this page.

**Marking.** One mark per item, 5 per module. Scenario items require the decision and the evidence that supports
it; a correct decision with no evidence earns half.

---

## CYB-401 · SOC Operations

**Q401.1 — B.** Escalate on asset value and confirmed follow-on behaviour, not on the label. A domain controller
with a new service and an unusual logon is a potential domain compromise; a signature hit with no follow-on is
worth a ticket, not an escalation.

**Q401.2 — B.** The rule worked: the behaviour occurred and was legitimately authorised. Calling it a false
positive teaches the wrong lesson and leads to suppressing the rule.

**Q401.3 — B.** Persistence. Scheduled tasks survive reboots and are a common ATT&CK T1053 implementation.

**Q401.4.** Action: monitor or hunt, not block — blocking on a six-month-old, medium-confidence indicator risks
outages for little gain. Weighed: confidence (medium), age (six months, so infrastructure may be reassigned),
and actionability (does it appear in your telemetry, and would blocking break anything). If it appears in logs,
hunt for prior contact; then decide.

**Q401.5.** Four elements: what was observed, with the specific evidence and timestamps; what actions were taken
and by whom; what the next action is and who owns it; and the deadline or trigger for escalation.
"Investigating" fails because it cannot be verified, continued, or handed over — a colleague cannot tell what
has been checked.

---

## CYB-402 · Endpoint Telemetry

**Q402.1 — B.** Type 3 is a network logon. Type 2 is interactive, type 10 is RDP, type 5 is a service.

**Q402.2 — B.** A document processor spawning PowerShell with an encoded command is a classic macro execution
chain. `explorer` → `notepad` and `services` → `svchost` are normal; `cmd` → `ping` is mundane.

**Q402.3 — A.** Event ID 1 is process creation (with `CommandLine`); 3 is network connection, 11 file creation,
22 DNS query.

**Q402.4.** The name is trivially chosen or copied (`svchost.exe` in the wrong directory), while the command line
shows what the process was asked to do: encoded payloads, download URLs, credentials, target paths. Behaviour
lives in the arguments, which is why living-off-the-land attacks are caught by command lines and parentage.

**Q402.5.** First: brute force against one account (many passwords, one username); defeated by account lockout
and throttling. Second: password spraying (a few passwords across many accounts); lockout does not help because
each account sees few attempts — it is defeated by breached-password screening, strong password policy and MFA,
plus detection on the distributed pattern.

---

## CYB-403 · Hardening and Patching

**Q403.1 — B.** Exploitability, exposure, asset value and compensating controls. CVSS alone ignores whether the
code is reachable; vendor ratings are inputs, not decisions.

**Q403.2 — B.** Level 2 is stricter and intended for high-security environments, with more operational impact
(and more chance of breaking something). Level 1 is the practical baseline.

**Q403.3 — B.** Percentage remediated within the SLA for their severity, measured by exposure age. Counting
patches released or scans completed measures activity, not outcome.

**Q403.4.** Any four: the control or rule, the reason it is not applied (with evidence), the compensating
control, the owner and approver, the expiry or review date, and the scope of assets affected.

**Q403.5.** Steps: (1) map each failed rule to the host's role and exposure, discarding rules that do not apply
(e.g. desktop-only controls on a headless server); (2) validate the failures that matter by checking the actual
configuration, because scanner checks produce false positives; (3) group by risk and remediate in that order,
re-running the scan to verify. For an unfixed rule, record: rule ID, why (operational constraint), compensating
control, approver, review date.

---

## CYB-404 · Detection Engineering

**Q404.1 — B.** Correlation joins on field names and types. If one source calls it `src_ip` and another
`source.address`, the rule silently matches nothing — the failure mode is absence, not error.

**Q404.2 — B.** Positive, negative, no-data, and a regression test after tuning. A rule that has never been
shown to fire, or to stay quiet, is a guess.

**Q404.3 — B.** With the data source absent or misnamed, a badly written rule returns nothing and looks healthy;
the no-data test proves the rule distinguishes "no events" from "no match".

**Q404.4.** The behaviour (what the adversary does), the data source that records it, and the expected
observable (what the rule should see, including what should not trigger it).

**Q404.5.** The exception removes the exact behaviour the rule exists to detect, so a compromised service account
becomes invisible. Proper tuning changes the logic: add context (destination rarity, parent process, volume or
time-of-day deviation), split the rule by behaviour, or lower severity and add a correlation — and keep a
detection for the original behaviour.

---

## CYB-405 · Network Defence

**Q405.1 — B.** Default deny without an explicit allowlist blocks the business; the allowlist must be justified
per flow, and denials must be logged or you cannot tune it.

**Q405.2 — B.** Behaviour plus counters. `nft list ruleset` shows intent, not effect; a reboot tests persistence,
not policy.

**Q405.3 — B.** Interception breaks end-to-end confidentiality and has legal, privacy and trust implications; it
needs authorization and a documented scope, not just a technical capability.

**Q405.4.** Hidden: request/response content, URLs and paths inside HTTPS, credentials and tokens, file contents.
Remaining: SNI, IP addresses, ports, certificate details, packet sizes and timing, and DNS names where DNS is not
encrypted.

**Q405.5.** Hypotheses: (a) DNS tunnelling or a beacon using TXT records for command and control or exfiltration;
(b) a legitimate service — CDN, telemetry, antivirus lookup, or a SaaS API — using TXT for configuration.
Distinguishing evidence: payload size and entropy per query, total volume over time, whether the parent domain is
known and aged, whether the querying host's role explains it, response content structure, and correlation with
other host behaviour (process making the query, time pattern).

---

## CYB-406 · Digital Forensics

**Q406.1 — B.** Acquire, hash, verify, analyse the copy. Tools and speed are not soundness; the hash chain is.

**Q406.2 — C.** Opinion about a suspect has no place in a custody record. Who, when, why, hash and storage
conditions are the record.

**Q406.3 — B.** Birth (creation) time, alongside Modified, Accessed and Changed (MFT metadata change).

**Q406.4.** YARA matches strings or byte patterns that benign files can share; a hit narrows the search but needs
context — location, accompanying behaviour, signer, prevalence — before it supports a conclusion. False
positives are common in shared libraries and installers.

**Q406.5.** Source: memory (process table, socket-to-PID mapping, network buffers), or live telemetry such as
Sysmon Event 3 / EDR connection records. Disk alone may not have the runtime connection state, and logs may
have rotated. Preserve first: isolate from the network without powering off, acquire memory before disk, hash
and record custody.

---

## CYB-407 · Incident Response

**Q407.1 — A.** Preparation; detection and analysis; containment, eradication and recovery; post-incident
activity.

**Q407.2 — B.** Powering off destroys memory-resident evidence (processes, connections, keys) and can trigger
logic bombs or encryption of remaining data. Isolation preserves both containment and evidence.

**Q407.3 — B.** Isolate the network, keep it powered, acquire memory, then disk. Scanning and deleting destroys
evidence; reimaging destroys everything.

**Q407.4.** Root cause is the flaw or decision that made the incident possible (an unpatched edge device, or
credentials without MFA); contributing factors made it worse or delayed response (flat network, no logging on
the segment, alert not actioned). Fixing only contributing factors leaves the cause in place.

**Q407.5.** Method: compare both hosts against an independent time source (domain controller, NTP peer, or a
capture of the same event), compute each offset, convert to a single stated timezone (UTC), and record the
conversion. Express as a range with the uncertainty: "file encrypted between 03:12:40 and 03:19:40 UTC; host B
clock was 7 minutes fast". False precision is the failure.

---

## Troubleshooting exercises — marking criteria

**T407.1** (3 marks) — three of: the decoder does not parse the real log format (check `wazuh-logtest` with a
verbatim production line, not a sample); the rule's field names differ after normalisation (inspect the decoded
JSON); the log source is not reaching the manager (agent status, `archives.json`, network path); a higher-priority
rule suppresses it; the rule is disabled or in a different ruleset. Each needs its specific check.

**T407.2** (3 marks) — stop and treat the image as unverified; re-hash the image and the original storage, check
the acquisition log and tool output for errors, and re-acquire from the original if it is still available;
document the discrepancy and notify the case owner. Must not: proceed to analyse and present findings from an
unverified image, or "fix" the hash record.

**T407.3** (3 marks) — two of: traffic bypassed the proxy (direct-to-internet egress, or a protocol the proxy does
not handle); the proxy logged to a different system or the log rotated; the destination was internal-to-external
NAT and the proxy only logs HTTP; the capture is on a segment the proxy does not see. Award the mark for stating
what evidence would distinguish them (span port placement, egress firewall logs, DNS logs).

---

## Level 4 integrated assessment — model answers

### The scripted intrusion

The lab scenario follows a common chain; the exact events are in the assessment data pack, but the shape is:

1. **Initial access** — a phishing attachment opens a document that spawns a script interpreter
   (`winword.exe` → `powershell.exe -enc ...`).
2. **Execution and persistence** — an encoded PowerShell payload downloads a second stage and creates a
   scheduled task.
3. **Discovery and credential access** — account enumeration, then authentication attempts against a file server.
4. **Lateral movement** — SMB authentication from the workstation to the server using a service account.
5. **Impact** — files renamed with a new extension; shadow copies deleted.

### Expected analytical output

| Artefact | What a strong answer contains |
| --- | --- |
| Timeline | 8–12 events minimum, UTC-normalised, with source (event ID, log, or capture) and confidence per event |
| Detection | At least two detections justified by telemetry, each with a rule or query and the observable it uses |
| Containment | Host isolated (network, not powered off), account disabled and sessions revoked, evidence acquired before remediation |
| Report | Root cause, scope (which hosts, which accounts), impact, containment, recovery, lessons learned |
| Limits | States what could not be determined (e.g. initial attachment not recovered, no memory image of host B) |

### Written component criteria

**W1 — Timeline discipline (10 marks).** Requires UTC conversion, source per event, and confidence labels. Events
inferred rather than observed must be marked as inferred.

**W2 — Detection justification (8 marks).** Requires: why the chosen telemetry would catch this behaviour, what it
would miss, and one false-positive consideration with the exception you would *not* add.

**W3 — Containment decisions (7 marks).** Requires: the order of actions and why (evidence before remediation,
scope before containment), and one alternative you rejected — for example shutting down the host — with the cost.

**W4 — Post-incident review (5 marks).** Requires: root cause versus contributing factors, and two changes with
owners and verification, not "improve awareness".

---

## Scoring

| Module score | Action |
| --- | --- |
| 5/5 | Retake at seven days |
| 4/5 | Reread the missed explanation |
| 3/5 | Return to the module's lab; detection reasoning is applied, not verbal |
| 0–2/5 | Re-do the module with the lab open beside the lesson |

Level total: 35 marks; 28 or above suggests readiness for the integrated assessment.

## Related

- [Level 4 quiz](level-4-quiz.md) · [Level 4 integrated assessment](level-4-assessment.md)
- [MITRE ATT&CK](https://attack.mitre.org/) — the mapping reference used throughout
- [Level 4 overview](../levels/level-4.md)

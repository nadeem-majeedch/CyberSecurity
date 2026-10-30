---
title: "Level 5 Module Quizzes — Advanced Practice"
description: "Thirty self-check items across CYB-501 to CYB-506: engagement management, Active Directory, cloud, malware analysis, automation and threat hunting."
module_code: ASM-L5
level: 5
kind: assessment
prerequisites: [CYB-501]
estimated_minutes: 100
difficulty: advanced
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, quiz, level-5, active-directory, cloud, malware, hunting]
---

# Level 5 Module Quizzes

Five items per module, six modules, thirty items. These assume the Level 5 lab: an isolated `lab.local` forest,
a local S3-compatible service, an offline analysis VM, and the sample telemetry from the hunting labs.

**Protocol.** Attempt on paper, then mark against the [Level 5 answer key](level-5-key.md). Target 4 of 5.
Every item that mentions a target means the lab target — there is no scenario in this course where a public
system is the right answer.

---

## CYB-501 · Penetration Testing and Security Assessment

**Q501.1** (MCQ) Which item belongs in rules of engagement rather than in the technical plan?

- A. The Nmap flags you will use for service detection
- B. The stop conditions, exclusions, emergency contact and data-handling rules
- C. The order in which you will test the login page
- D. The CVSS vector for each finding

**Q501.2** (MCQ) A scanner reports a critical vulnerability. What must happen before it appears as a finding?

- A. It should be rated critical because the scanner is authoritative
- B. It must be validated by an independent method that demonstrates the claim
- C. It should be downgraded to informational until the vendor confirms
- D. It should be reported with the scanner's exact wording

**Q501.3** (MCQ) Which evidence set lets a reviewer reproduce a finding?

- A. A screenshot of a scanner result
- B. The request, the response, the timestamp, the target, and the account/role used
- C. The tool name and version
- D. A paragraph describing what happened

**Q501.4** (Short) Distinguish technical severity from business risk, and state one factor that moves a finding
between them.

**Q501.5** (Scenario) The scope forbids denial-of-service testing. You suspect a flaw that could take the service
down. How do you establish impact without violating the rule, and what do you write in the report?

---

## CYB-502 · Active Directory Security

**Q502.1** (MCQ) What is Kerberoasting?

- A. Requesting a service ticket for an account with an SPN and cracking it offline
- B. Forcing a Kerberos downgrade to NTLM
- C. Cracking the `krbtgt` password online
- D. Adding a computer to the domain without authorization

**Q502.2** (MCQ) BloodHound shows `GenericAll` from a user to a group. What does that mean in practice?

- A. The user can read the group's description
- B. The user has full control over the group object, which can include adding themselves as a member
- C. The user can reset their own password
- D. The user is a domain admin

**Q502.3** (MCQ) After a domain compromise, why is `krbtgt` reset twice?

- A. Because the password policy requires two changes
- B. Because a single reset leaves tickets signed with the previous key valid; the second reset invalidates them
- C. Because the account has two passwords
- D. Because replication requires it

**Q502.4** (Short) How does tiering reduce credential exposure, and what breaks tiering in practice?

**Q502.5** (Scenario) Domain controller logs show many 4769 events with RC4 encryption for different SPNs from
one workstation in a short window. Name the likely activity, the two log details that support it, and one
benign explanation to exclude.

---

## CYB-503 · Cloud Security

**Q503.1** (MCQ) Under the shared responsibility model for an IaaS virtual machine, who patches the guest
operating system?

- A. The provider
- B. The customer
- C. Both, automatically
- D. Neither; patching is not required in cloud

**Q503.2** (MCQ) What characterises a least-privilege identity policy?

- A. `Action: "*"` limited to one region
- B. Explicitly allowed actions on named resources, with conditions, and everything else denied
- C. A long password and MFA
- D. A policy that is reviewed annually

**Q503.3** (MCQ) How do you prove an object bucket is not publicly readable?

- A. Read the console setting
- B. Make an unauthenticated request for a known object and observe the denial, after enabling public-access
  blocks
- C. Check that the bucket name is not in a search engine
- D. Enable versioning

**Q503.4** (Short) Why should credentials not be stored in a container image or a plain environment variable in
the manifest?

**Q503.5** (Scenario) Audit logs show `StopLogging` followed by IAM policy changes, then logging re-enabled 20
minutes later. State what this pattern suggests, the first two investigative steps, and the control that would
have made the gap smaller.

---

## CYB-504 · Malware Analysis and Reverse Engineering

**Q504.1** (MCQ) What can static analysis not tell you?

- A. The file type and hash
- B. The runtime behaviour and the configuration decrypted at execution
- C. The strings present in an unpacked binary
- D. The compiler or packer indicated by the headers

**Q504.2** (MCQ) Which sandbox configuration is appropriate for behavioural analysis?

- A. Bridged networking so the sample can reach the internet
- B. Host-only or internal networking, no shared folders, a snapshot, and simulated services
- C. The host's desktop with a firewall rule
- D. A production VM with logging enabled

**Q504.3** (MCQ) What makes a YARA rule trustworthy?

- A. It matches the sample you wrote it from
- B. It matches the intended family and stays quiet on a negative corpus of benign files
- C. It uses many strings
- D. It is private

**Q504.4** (Short) Why must an analysis report attach a confidence level to each indicator?

**Q504.5** (Scenario) A sample launches a signed Windows utility to download a payload. State what you report,
and one conclusion you must avoid drawing.

---

## CYB-505 · Security Automation

**Q505.1** (MCQ) Which default makes an automation safe to run against production?

- A. It acts on everything it finds
- B. It defaults to dry-run, with an explicit target allowlist and an `--apply` flag
- C. It requires root
- D. It logs only on failure

**Q505.2** (MCQ) What does idempotency mean for a remediation script?

- A. It runs faster the second time
- B. Running it twice produces the same end state, without duplicating or undoing work
- C. It never fails
- D. It can be run by anyone

**Q505.3** (MCQ) How should an automation obtain an API token?

- A. Hard-coded in the script, protected by file permissions
- B. From a secret store or environment injected at runtime, never logged, rotated on a schedule
- C. From a command-line argument, so it is visible in `ps`
- D. From a comment at the top of the file

**Q505.4** (Short) Why do exit codes matter more in automation than in interactive work?

**Q505.5** (Scenario) An API returns `429 Too Many Requests` during a bulk enrichment run. Describe the correct
handling, including what you must not do.

---

## CYB-506 · Threat Hunting and Detection Engineering

**Q506.1** (MCQ) Which hunting hypothesis is falsifiable?

- A. "Attackers may be in the network"
- B. "If an adversary is using scheduled tasks for persistence, then 4698 events will show task creation by
  non-administrative users on servers, which we can query"
- C. "We should look at DNS more"
- D. "The SOC should hunt for APTs"

**Q506.2** (MCQ) What must a null-result hunt report contain?

- A. Nothing; a hunt that found nothing is not worth documenting
- B. The hypothesis, the data queried, the time range, the result, and the coverage gap it revealed
- C. Only the query used
- D. A recommendation to buy a new tool

**Q506.3** (MCQ) A detection is described as covering a technique because a rule exists for a related event. What
is this?

- A. Present coverage
- B. Overclaimed coverage; the rule does not observe the technique's behaviour
- C. Partial coverage, always acceptable
- D. A false positive

**Q506.4** (Short) Why is adding an exception to a noisy rule not tuning, and what does proper tuning change?

**Q506.5** (Scenario) A host contacts one external address every 300 seconds with low variance, including
outside business hours. A backup job contacts another address hourly. State the two analyses you would run and
what would make you treat the first as benign.

---

## Troubleshooting exercises

**T506.1** A Sigma rule converts to a Wazuh rule but never fires in the lab. Name three checks, in order, and the
one that proves the data source is present at all.

**T506.2** Your enrichment script fails on 3 of 500 indicators and exits 0. Explain why that is a defect and what
the correct behaviour is.

**T506.3** A container running in the lab has network access it should not have, despite `--network none`. Give
three possible causes and the check for each.

---

## Practical challenges

| Module | Challenge | Where |
| --- | --- | --- |
| CYB-501 | Write an engagement package and run a scoped assessment on the lab | [LAB-501-01](../levels/level-5-advanced/01-penetration-testing/lab-01-engagement-package.md) |
| CYB-502 | Find an ACL path in `lab.local`, then break it and verify | [LAB-502-02](../levels/level-5-advanced/02-active-directory/lab-02-bloodhound-pingcastle.md) |
| CYB-503 | Prove a deny path and close an anonymous bucket | [LAB-503-01](../levels/level-5-advanced/03-cloud-security/lab-01-identity-and-storage.md) |
| CYB-504 | Write YARA that survives a negative corpus | [LAB-504-03](../levels/level-5-advanced/04-malware-analysis/lab-03-yara-classification.md) |
| CYB-505 | Build a guarded containment script and exercise its refusal paths | [LAB-505-03](../levels/level-5-advanced/05-security-automation/lab-03-guarded-automation.md) |
| CYB-506 | Hunt a hypothesis and tune a noisy detection without widening an exception | [LAB-506-01](../levels/level-5-advanced/06-threat-hunting/lab-01-hunt-hypothesis.md) |

---

## Next

- [Level 5 answer key](level-5-key.md)
- [Level 5 integrated assessment](level-5-assessment.md)
- [Capstone briefs](../projects/index.md)

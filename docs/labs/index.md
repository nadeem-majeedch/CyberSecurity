# Labs

Every practical exercise in this course runs in a lab you build and control. This page is the single
reference for that environment: what to build, how to verify it, how to reset it, and which labs exist.

!!! warning "Read this before your first lab"
    You may only test systems you own, systems inside your isolated lab, intentionally vulnerable
    applications provided for the course, or a range you have been given written authorization to use.
    The binding rules are in the [Safety Policy](../policies/safety-policy.md); the practical build steps are
    in the [Lab Safety Guide](../start-here/lab-safety.md).

Every lab's final challenge is assessed against a four-criterion rubric. For questions that check your
understanding, and for the level assessments and capstones, see [Assessments](../assessments/index.md).

---

## Canonical lab specification

Versions are pinned because instructions are verified against them. If you substitute a version, expect small
differences and record them in your lab log.

| Host | Role | Spec | Software |
| --- | --- | --- | --- |
| `lab-ubuntu` | Primary Linux host | 2 vCPU, 2 GB RAM, 20 GB disk, host-only | Ubuntu Server LTS (22.04.x) |
| `lab-win` | Windows host | 2 vCPU, 4 GB RAM, 50 GB disk, host-only | Windows 11 Enterprise Evaluation (or Windows 10) |
| `lab-analyst` | Analyst workstation (Level 2 onward) | 2 vCPU, 4 GB RAM, 30 GB disk, host-only | Kali Linux (introduced in CYB-112) |
| `lab-target` | Service/inventory target (Level 2) | 2 vCPU, 2 GB RAM, 20 GB disk, host-only | Ubuntu Server + common services |
| `lab-web` | Vulnerable web apps (Level 3) | 2 vCPU, 4 GB RAM, 20 GB disk, host-only | DVWA, OWASP Juice Shop, a local API |
| `lab-monitor` | SIEM, sensors and forensic workstation (Level 4; referred to as `lab-siem`) | 4 vCPU, 8 GB RAM, 50 GB disk, host-only, plus a second NIC on an internal DMZ network | Wazuh 4.14.9 (Docker single-node), Suricata 8.0.7, Zeek 9.0.1 LTS, The Sleuth Kit 4.12, Autopsy 4.23.1, Volatility 3, YARA 4.6.0 |
| `lab-ad` | Active Directory forest (Level 5) | 2–4 VMs, 16 GB host RAM recommended | Instructor-provided build |
| `lab-malware` | Analysis sandbox (Level 5) | 2 vCPU, 2 GB RAM | REMnux/FLARE VM pattern, **no network, no shared folders** |

**Network:** all lab adapters on a single host-only network using documentation ranges
(`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) or a documented private range. NAT is attached only for
package installation and removed afterwards. **Bridged mode is not used.**

**Snapshot baseline:** `clean-base` after OS install and updates. A `pre-<lab-id>` snapshot before every lab,
reverted after evidence is saved.

!!! note "Host naming"
    Level 1 refers to the hosts by role (`lab-ubuntu`, `lab-win`). From Level 2 the same machines are referred to as
    `lab-kali` (the analyst workstation, the `lab-analyst` role) and `lab-ubuntu` (the target, the `lab-target`
    role). They are the same two VMs — the newer names just say which is being used for what.

---

## Lab catalogue

| Lab ID | Title | Level | Module | Time | Status |
| --- | --- | --- | --- | --- | --- |
| [LAB-107-01](../levels/level-1-foundations/07-networking-fundamentals/lab-01-capture-local-traffic.md) | Capture a Local Exchange | 1 | CYB-107 | 60 min | Published |
| [LAB-108-01](../levels/level-1-foundations/08-addressing-and-protocols/lab-01-network-configuration.md) | Inspect Network Configuration | 1 | CYB-108 | 45 min | Published |
| [LAB-108-02](../levels/level-1-foundations/08-addressing-and-protocols/lab-02-dns-lookups.md) | Read DNS Lookup Results | 1 | CYB-108 | 45 min | Published |
| [LAB-109-01](../levels/level-1-foundations/09-linux-command-line/lab-01-files-permissions.md) | Files, Permissions and Ownership | 1 | CYB-109 | 45 min | Published |
| [LAB-109-02](../levels/level-1-foundations/09-linux-command-line/lab-02-processes-listeners-logs.md) | Processes, Listening Ports and Logs | 1 | CYB-109 | 45 min | Published |
| [LAB-110-01](../levels/level-1-foundations/10-windows-powershell-basics/lab-01-windows-inspection.md) | Inspect a Windows Host | 1 | CYB-110 | 60 min | Published |
| [LAB-111-01](../levels/level-1-foundations/11-virtualization-and-lab-networks/lab-01-isolated-network.md) | Build and Verify an Isolated Network | 1 | CYB-111 | 60 min | Published |
| [LAB-113-01](../levels/level-1-foundations/13-cryptography-hashing-signatures/lab-01-hashing-integrity.md) | Hashes, File Integrity and Signatures | 1 | CYB-113 | 60 min | Published |
| [LAB-114-01](../levels/level-1-foundations/14-passwords-mfa-phishing/lab-01-phishing-triage.md) | Triage Synthetic Phishing Emails | 1 | CYB-114 | 45 min | Published |
| [LAB-114-02](../levels/level-1-foundations/14-passwords-mfa-phishing/lab-02-password-policy.md) | Assess a Password Policy | 1 | CYB-114 | 45 min | Published |
| [LAB-115-01](../levels/level-1-foundations/15-security-logs-and-troubleshooting/lab-01-evidence-trail.md) | Follow an Evidence Trail | 1 | CYB-115 | 60 min | Published |
| [LAB-201-01](../levels/level-2-tooling/01-lab-environment-and-kali/lab-01-prepare-kali-vm.md) | Prepare and Verify a Kali VM | 2 | CYB-201 | 120 min | Published |
| [LAB-201-02](../levels/level-2-tooling/01-lab-environment-and-kali/lab-02-host-only-network.md) | Configure Host-Only Networking and Record Addresses | 2 | CYB-201 | 120 min | Published |
| [LAB-201-03](../levels/level-2-tooling/01-lab-environment-and-kali/lab-03-connectivity-validation.md) | Validate Connectivity Between Lab Hosts | 2 | CYB-201 | 90 min | Published |
| [LAB-202-01](../levels/level-2-tooling/02-bash-python-git/lab-01-bash-security-check.md) | Bash Security-Check Script | 2 | CYB-202 | 180 min | Published |
| [LAB-202-02](../levels/level-2-tooling/02-bash-python-git/lab-02-python-log-parser.md) | Python Parser for Synthetic Network Logs | 2 | CYB-202 | 240 min | Published |
| [LAB-202-03](../levels/level-2-tooling/02-bash-python-git/lab-03-git-for-artifacts.md) | Version Lab Artefacts with Git | 2 | CYB-202 | 120 min | Published |
| [LAB-203-01](../levels/level-2-tooling/03-host-discovery-and-enumeration/lab-01-host-discovery.md) | Host Discovery in an Isolated Lab | 2 | CYB-203 | 180 min | Published |
| [LAB-203-02](../levels/level-2-tooling/03-host-discovery-and-enumeration/lab-02-service-enumeration.md) | Port and Service Enumeration of a Local Target | 2 | CYB-203 | 240 min | Published |
| [LAB-203-03](../levels/level-2-tooling/03-host-discovery-and-enumeration/lab-03-tcp-udp-behaviour.md) | Compare TCP and UDP Behaviour | 2 | CYB-203 | 180 min | Published |
| [LAB-203-04](../levels/level-2-tooling/03-host-discovery-and-enumeration/lab-04-netcat-local.md) | Netcat for Controlled Local Demonstrations | 2 | CYB-203 | 180 min | Published |
| [LAB-204-01](../levels/level-2-tooling/04-packet-capture-and-analysis/lab-01-tcpdump-capture.md) | Capture with tcpdump and Inspect a pcap | 2 | CYB-204 | 240 min | Published |
| [LAB-204-02](../levels/level-2-tooling/04-packet-capture-and-analysis/lab-02-wireshark-analysis.md) | Capture and Analyse with Wireshark | 2 | CYB-204 | 240 min | Published |
| [LAB-204-03](../levels/level-2-tooling/04-packet-capture-and-analysis/lab-03-protocol-analysis.md) | Protocol Analysis: DNS, TCP, HTTP, TLS | 2 | CYB-204 | 240 min | Published |
| [LAB-205-01](../levels/level-2-tooling/05-ssh-secure-administration/lab-01-key-based-auth.md) | Key-Based Authentication End to End | 2 | CYB-205 | 240 min | Published |
| [LAB-205-02](../levels/level-2-tooling/05-ssh-secure-administration/lab-02-harden-sshd.md) | Audit and Harden sshd Without Locking Yourself Out | 2 | CYB-205 | 240 min | Published |
| [LAB-206-01](../levels/level-2-tooling/06-host-inspection-and-hardening/lab-01-host-inventory.md) | Host Inspection Inventory | 2 | CYB-206 | 240 min | Published |
| [LAB-206-02](../levels/level-2-tooling/06-host-inspection-and-hardening/lab-02-lynis-assessment.md) | Hardening Assessment with Lynis | 2 | CYB-206 | 240 min | Published |
| [LAB-206-03](../levels/level-2-tooling/06-host-inspection-and-hardening/lab-03-assessment-report.md) | Write the Assessment Report | 2 | CYB-206 | 240 min | Published |

| [LAB-301-01](../levels/level-3-applications/01-web-architecture-and-http/lab-01-web-lab-setup.md) | Build the Web Lab | 3 | CYB-301 | 90 min | Published |
| [LAB-301-02](../levels/level-3-applications/01-web-architecture-and-http/lab-02-intercept-a-session.md) | Intercept and Annotate a Session | 3 | CYB-301 | 90 min | Published |
| [LAB-301-03](../levels/level-3-applications/01-web-architecture-and-http/lab-03-cookie-and-session-attributes.md) | Evaluate Cookie and Session Attributes | 3 | CYB-301 | 90 min | Published |
| [LAB-302-01](../levels/level-3-applications/02-injection-and-xss/lab-01-sql-injection.md) | SQL Injection and Its Fix | 3 | CYB-302 | 240 min | Published |
| [LAB-302-02](../levels/level-3-applications/02-injection-and-xss/lab-02-xss.md) | Reflected and Stored XSS | 3 | CYB-302 | 240 min | Published |
| [LAB-303-01](../levels/level-3-applications/03-access-control-and-authentication/lab-01-insecure-login-workflow.md) | Insecure Login Workflow | 3 | CYB-303 | 180 min | Published |
| [LAB-303-02](../levels/level-3-applications/03-access-control-and-authentication/lab-02-broken-access-control.md) | Broken Access Control and IDOR | 3 | CYB-303 | 180 min | Published |
| [LAB-303-03](../levels/level-3-applications/03-access-control-and-authentication/lab-03-csrf.md) | Cross-Site Request Forgery | 3 | CYB-303 | 120 min | Published |
| [LAB-304-01](../levels/level-3-applications/04-file-handling-ssrf-misconfiguration/lab-01-file-upload.md) | File Upload Validation | 3 | CYB-304 | 90 min | Published |
| [LAB-304-02](../levels/level-3-applications/04-file-handling-ssrf-misconfiguration/lab-02-path-traversal.md) | Path Traversal and File Inclusion | 3 | CYB-304 | 75 min | Published |
| [LAB-304-03](../levels/level-3-applications/04-file-handling-ssrf-misconfiguration/lab-03-ssrf.md) | Server-Side Request Forgery | 3 | CYB-304 | 105 min | Published |
| [LAB-304-04](../levels/level-3-applications/04-file-handling-ssrf-misconfiguration/lab-04-headers-and-tls.md) | Security Headers, TLS and Misconfiguration | 3 | CYB-304 | 75 min | Published |
| [LAB-307-01](../levels/level-3-applications/05-secure-coding-and-dependencies/lab-01-code-review-and-threat-model.md) | Threat Model and Code Review | 3 | CYB-307 | 120 min | Published |
| [LAB-307-02](../levels/level-3-applications/05-secure-coding-and-dependencies/lab-02-vulnerable-dependencies.md) | Vulnerable Dependencies | 3 | CYB-307 | 90 min | Published |
| [LAB-307-03](../levels/level-3-applications/05-secure-coding-and-dependencies/lab-03-fix-and-verify.md) | Fix, Test and Verify | 3 | CYB-307 | 150 min | Published |
| [LAB-308-01](../levels/level-3-applications/06-api-security/lab-01-api-authorization.md) | API Authorization Failures | 3 | CYB-308 | 90 min | Published |
| [LAB-308-02](../levels/level-3-applications/06-api-security/lab-02-mass-assignment-and-rate-limiting.md) | Mass Assignment and Rate Limiting | 3 | CYB-308 | 105 min | Published |

| [LAB-401-01](../levels/level-4-defensive-operations/01-soc-operations/lab-01-alert-triage.md) | Triage a Synthetic Alert Queue | 4 | CYB-401 | 120 min | Published |
| [LAB-401-02](../levels/level-4-defensive-operations/01-soc-operations/lab-02-attck-mapping.md) | Map Activity to ATT&CK | 4 | CYB-401 | 120 min | Published |
| [LAB-401-03](../levels/level-4-defensive-operations/01-soc-operations/lab-03-ioc-brief.md) | Write a Threat-Intelligence Brief | 4 | CYB-401 | 120 min | Published |
| [LAB-402-01](../levels/level-4-defensive-operations/02-endpoint-telemetry/lab-01-windows-event-logs.md) | Windows Event Log Triage | 4 | CYB-402 | 180 min | Published |
| [LAB-402-02](../levels/level-4-defensive-operations/02-endpoint-telemetry/lab-02-linux-auth-logs.md) | Linux Authentication Log Analysis | 4 | CYB-402 | 150 min | Published |
| [LAB-402-03](../levels/level-4-defensive-operations/02-endpoint-telemetry/lab-03-sysmon-process-sequence.md) | A Suspicious Process Sequence | 4 | CYB-402 | 150 min | Published |
| [LAB-403-01](../levels/level-4-defensive-operations/03-hardening-and-patching/lab-01-linux-baseline.md) | Linux Baseline Assessment and Verified Remediation | 4 | CYB-403 | 180 min | Published |
| [LAB-403-02](../levels/level-4-defensive-operations/03-hardening-and-patching/lab-02-windows-hardening.md) | Windows Controls You Can Prove | 4 | CYB-403 | 180 min | Published |
| [LAB-403-03](../levels/level-4-defensive-operations/03-hardening-and-patching/lab-03-vulnerability-prioritisation.md) | Vulnerability Prioritisation and Patch Plan | 4 | CYB-403 | 180 min | Published |
| [LAB-404-01](../levels/level-4-defensive-operations/04-detection-and-siem/lab-01-wazuh-deployment.md) | Deploy a Local SIEM and Ingest Telemetry | 4 | CYB-404 | 180 min | Published |
| [LAB-404-02](../levels/level-4-defensive-operations/04-detection-and-siem/lab-02-sigma-rule.md) | Write, Convert and Test a Detection | 4 | CYB-404 | 210 min | Published |
| [LAB-404-03](../levels/level-4-defensive-operations/04-detection-and-siem/lab-03-correlation-and-tuning.md) | Correlation, Tuning and a Detection Report | 4 | CYB-404 | 210 min | Published |
| [LAB-405-01](../levels/level-4-defensive-operations/05-network-defence/lab-01-segmentation.md) | Segmentation You Can Prove | 4 | CYB-405 | 180 min | Published |
| [LAB-405-02](../levels/level-4-defensive-operations/05-network-defence/lab-02-suricata-ids.md) | Suricata: Detect Traffic You Generated | 4 | CYB-405 | 180 min | Published |
| [LAB-405-03](../levels/level-4-defensive-operations/05-network-defence/lab-03-dns-analysis.md) | DNS Behaviour Analysis | 4 | CYB-405 | 150 min | Published |
| [LAB-406-01](../levels/level-4-defensive-operations/06-digital-forensics/lab-01-acquisition-and-custody.md) | Evidence Register and Verified Acquisition | 4 | CYB-406 | 240 min | Published |
| [LAB-406-02](../levels/level-4-defensive-operations/06-digital-forensics/lab-02-disk-and-timeline.md) | Disk Triage and a Defensible Timeline | 4 | CYB-406 | 240 min | Published |
| [LAB-406-03](../levels/level-4-defensive-operations/06-digital-forensics/lab-03-yara-and-memory.md) | YARA Classification and Memory Artefacts | 4 | CYB-406 | 180 min | Published |
| [LAB-407-01](../levels/level-4-defensive-operations/07-incident-response/lab-01-phishing-triage.md) | Phishing Triage and Scope | 4 | CYB-407 | 150 min | Published |
| [LAB-407-02](../levels/level-4-defensive-operations/07-incident-response/lab-02-timeline.md) | Master Timeline from Mixed Evidence | 4 | CYB-407 | 150 min | Published |
| [LAB-407-03](../levels/level-4-defensive-operations/07-incident-response/lab-03-ransomware.md) | Simulated Ransomware: Contain and Recover | 4 | CYB-407 | 120 min | Published |
| [LAB-407-04](../levels/level-4-defensive-operations/07-incident-response/lab-04-report-and-review.md) | The Incident Report and Post-Incident Review | 4 | CYB-407 | 120 min | Published |

| [LAB-501-01](../levels/level-5-advanced/01-penetration-testing/lab-01-engagement-package.md) | Scope, Rules of Engagement and Test Plan | 5 | CYB-501 | 180 min | Published |
| [LAB-501-02](../levels/level-5-advanced/01-penetration-testing/lab-02-lab-assessment.md) | Authorized Assessment of a Lab Target | 5 | CYB-501 | 240 min | Published |
| [LAB-501-03](../levels/level-5-advanced/01-penetration-testing/lab-03-privesc-and-report.md) | Escalate, Report, Remediate, Retest | 5 | CYB-501 | 240 min | Published |
| [LAB-502-01](../levels/level-5-advanced/02-active-directory/lab-01-build-domain.md) | Build the Isolated Domain | 5 | CYB-502 | 240 min | Published |
| [LAB-502-02](../levels/level-5-advanced/02-active-directory/lab-02-bloodhound-pingcastle.md) | Enumerate, Map and Audit | 5 | CYB-502 | 240 min | Published |
| [LAB-502-03](../levels/level-5-advanced/02-active-directory/lab-03-detect-harden-recover.md) | Detect, Harden, Recover | 5 | CYB-502 | 240 min | Published |
| [LAB-503-01](../levels/level-5-advanced/03-cloud-security/lab-01-identity-and-storage.md) | Least Privilege and Object Storage | 5 | CYB-503 | 180 min | Published |
| [LAB-503-02](../levels/level-5-advanced/03-cloud-security/lab-02-misconfiguration-and-audit.md) | Misconfiguration Detection and Audit Logs | 5 | CYB-503 | 180 min | Published |
| [LAB-503-03](../levels/level-5-advanced/03-cloud-security/lab-03-container-hardening.md) | Container Hardening | 5 | CYB-503 | 180 min | Published |
| [LAB-504-01](../levels/level-5-advanced/04-malware-analysis/lab-01-static-triage.md) | Static Triage | 5 | CYB-504 | 180 min | Published |
| [LAB-504-02](../levels/level-5-advanced/04-malware-analysis/lab-02-sandbox-behaviour.md) | Sandbox and Behaviour | 5 | CYB-504 | 180 min | Published |
| [LAB-504-03](../levels/level-5-advanced/04-malware-analysis/lab-03-yara-classification.md) | YARA Classification | 5 | CYB-504 | 180 min | Published |
| [LAB-505-01](../levels/level-5-advanced/05-security-automation/lab-01-log-parsing.md) | Parse and Normalise Logs | 5 | CYB-505 | 180 min | Published |
| [LAB-505-02](../levels/level-5-advanced/05-security-automation/lab-02-enrichment.md) | Enrichment and Report Normalisation | 5 | CYB-505 | 180 min | Published |
| [LAB-505-03](../levels/level-5-advanced/05-security-automation/lab-03-guarded-automation.md) | Guarded Automation | 5 | CYB-505 | 180 min | Published |
| [LAB-506-01](../levels/level-5-advanced/06-threat-hunting/lab-01-hunt-hypothesis.md) | Hunt a Hypothesis | 5 | CYB-506 | 180 min | Published |
| [LAB-506-02](../levels/level-5-advanced/06-threat-hunting/lab-02-coverage.md) | Coverage and Blind Spots | 5 | CYB-506 | 180 min | Published |
| [LAB-506-03](../levels/level-5-advanced/06-threat-hunting/lab-03-validate-and-tune.md) | Validate and Tune | 5 | CYB-506 | 180 min | Published |

**86 labs published** — 11 at Level 1, 18 at Level 2, 17 at Level 3, 22 at Level 4, 18 at Level 5. Nothing is listed
here before it exists.

---

## Lab shapes by level

| Level | What you add | What you practise on | Notable constraint |
| --- | --- | --- | --- |
| 1 | Ubuntu + Windows VMs | Your own hosts | No vulnerable services; this is administration and inspection |
| 2 | Analyst VM + target VM | Your own lab subnet | All scanning stays inside the lab range |
| 3 | DVWA, Juice Shop, local API | Deliberately vulnerable apps | Bound to localhost or the lab address only |
| 4 | SIEM, IDS, forensic tooling | Scripted activity you generate | Preserve evidence before containing |
| 5 | AD lab, cloud sandbox, analysis VM | Instructor-built range and sandbox account | Malware VM has no network; cloud lab has a budget cap |

---

## Build order (do this once)

1. Install the hypervisor and enable virtualization ([Prerequisites](../start-here/prerequisites.md)).
2. Create the host-only network; disable its DHCP server if you assign static addresses.
3. Build `lab-ubuntu`, update it, snapshot as `clean-base`.
4. Build `lab-win`, update it, snapshot as `win-clean`.
5. Verify isolation from both guests — `ping 8.8.8.8` must fail.
6. Record your environment in `lab-environment.md` (host OS, hypervisor version, addresses, snapshots).
7. Add further hosts as each level requires them, snapshotting each after a clean build.

---

## Isolation verification (run this every lab)

```bash
ip -br addr show            # confirm the lab address
ip route show               # confirm there is no default route on the lab interface
ping -c 2 8.8.8.8           # MUST fail
ping -c 2 192.0.2.30        # MUST succeed (peer host)
```

Paste the output into your notes with the date. "I checked" is not evidence; the transcript is.

---

## Reset and teardown

After every lab:

1. Save evidence outside the VM (text transcripts, no secrets, no real personal data).
2. Revert to `pre-<lab-id>`.
3. Confirm the VM boots and networking matches your documented state.
4. Log the revert: date, lab, anomalies.

At the end of a level, revert everything to `clean-base` and shut the VMs down. Keep at most 3–4 snapshots per
VM; snapshots grow and are not backups.

---

## Resource planning

| Scenario | RAM guidance |
| --- | --- |
| Level 1 | 8 GB workable; run two VMs at a time |
| Level 2 | 12 GB comfortable (analyst + target) |
| Level 3 | 12 GB (target + vulnerable apps + analyst) |
| Level 4 | 16 GB recommended (SIEM is the heavy one) |
| Level 5 AD | 16–24 GB, or run the forest on a separate machine |

---

## Related

- [Lab Safety Guide](../start-here/lab-safety.md) — build steps, isolation proof, snapshots
- [Safety Policy](../policies/safety-policy.md) — the binding rules
- [Troubleshooting](../start-here/troubleshooting.md) — when networking or a package fails
- [Lab template](../maintainer/lab-template.md) — how each lab page is written

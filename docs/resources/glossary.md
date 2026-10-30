# Glossary

Terms used throughout the course, defined once and linked from lessons. Definitions are deliberately
short: enough to use the term correctly, not a textbook entry.

If a lesson uses a term that is missing here, that is a content defect — report it.

---

## A

- **Access control** — The mechanism that decides who may do what to a resource. Enforced server-side;
  anything enforced only in a browser is a suggestion.
- **Active Directory (AD)** — Microsoft's directory service for Windows domains: users, computers, groups,
  and the policies that bind them. Also the most attacked system in most enterprises.
- **Alert** — A signal from a detection system that something may require attention. Not the same as an
  incident.
- **ARP (Address Resolution Protocol)** — Resolves an IPv4 address to a MAC address on a local network.
  Trivially spoofable, which is why local network trust is fragile.
- **Asset** — Anything worth protecting: data, systems, accounts, services, reputation, physical process.
- **Attack surface** — The sum of points where an attacker could interact with a system. Reducing it is
  usually cheaper than defending it.
- **ATT&CK** — MITRE's knowledge base of adversary tactics and techniques, used to structure detection
  coverage and threat intelligence.
- **Authentication** — Proving a claimed identity. Distinct from authorization.
- **Authorization** — Deciding what an authenticated identity may do. In this course, also the written
  permission required before testing any system.
- **Availability** — The property that a system is usable when needed. One leg of the CIA triad.

## B

- **Baseline** — A documented, known-good configuration or behaviour used as a reference for comparison.
- **Blue team** — Defensive work: monitoring, detection, response, hardening.
- **Brute force** — Trying many candidate secrets until one works. Illegal against systems you do not own,
  and ineffective against well-designed authentication.

## C

- **CIDR** — Notation for network ranges (`192.0.2.0/24`), where the suffix is the number of leading
  network bits.
- **CIA triad** — Confidentiality, Integrity, Availability: the three properties security work protects.
- **Control** — A safeguard that reduces risk. *Preventive* (stops), *detective* (reveals), *corrective*
  (recovers).
- **Credential** — Evidence of identity: a password, key, certificate, or token. Treat as a secret, always.
- **CVE** — A public identifier for a disclosed vulnerability (e.g. `CVE-2021-44228`).
- **CVSS** — A scoring system for vulnerability severity. A starting point for prioritisation, not a
  decision by itself.

## D

- **Detection engineering** — Designing, testing, and tuning rules that identify specific behaviours, with
  known false-positive rates.
- **DHCP** — Automatically assigns network configuration to hosts. Convenient, and a common source of
  "why did my lab address change?" confusion.
- **DNS** — The name-to-address system. Heavily used for both legitimate traffic and command-and-control,
  which is why DNS logging matters.
- **DoS (Denial of Service)** — Making a service unavailable. Prohibited against any target in this course.

## E

- **Exploit** — Code or a technique that takes advantage of a vulnerability to produce an unintended effect.

## F

- **False negative** — A real problem that a detection missed.
- **False positive** — An alert with no real problem behind it. The main source of alert fatigue.
- **Forensic soundness** — Handling evidence so that it can be shown not to have been altered: hashing,
  documented custody, write-blocking, reproducibility.

## H

- **Hardening** — Reducing a system's attack surface by removing services, restricting access, and applying
  secure configuration.

## I

- **IAM (Identity and Access Management)** — The systems and policies governing identities and their
  permissions.
- **IDS / IPS** — Intrusion Detection / Prevention System: inspects traffic and alerts (IDS) or blocks (IPS).
- **Incident** — A confirmed or suspected event that harms, or could harm, confidentiality, integrity, or
  availability. Escalated from an alert after triage.
- **Indicator of Compromise (IOC)** — An artefact suggesting intrusion: a hash, domain, IP, registry key.
  Useful, but brittle on its own.
- **Integrity** — The property that data is accurate and unaltered. One leg of the CIA triad.

## K

- **Kerberos** — The default authentication protocol in Active Directory; ticket-based, and the subject of
  several well-known attack techniques.

## L

- **Lateral movement** — Moving from one compromised host to another inside a network.
- **Least privilege** — Granting the minimum access needed for a task, for the minimum time.

## M

- **MFA (Multi-Factor Authentication)** — Authentication using two or more independent factor types. Phishable
  in some forms; not a synonym for "secure".
- **MITRE ATT&CK** — See **ATT&CK**.

## N

- **NAT (Network Address Translation)** — Rewrites addresses between networks. Convenient for labs, not a
  security control.
- **NIST** — US National Institute of Standards and Technology; publisher of widely used security guidance
  (e.g. SP 800-61 for incident response).

## O

- **OWASP** — Open Worldwide Application Security Project; publishes the Top 10 and the Juice Shop lab
  application used in Level 3.

## P

- **Packet** — A unit of network data with headers and payload. Captures are evidence; treat them as such.
- **PECA 2016** — Pakistan's Prevention of Electronic Crimes Act, which criminalises unauthorized access and
  interference. See the [Safety Policy](../policies/safety-policy.md#5-legal-framework).
- **Penetration test** — An authorized, scoped assessment that attempts to exploit weaknesses, with a report
  and remediation advice.
- **Phishing** — Deceiving a person into an action (credential entry, malware execution) via a message.
- **PKI (Public Key Infrastructure)** — The system of certificates and authorities that binds public keys to
  identities.
- **Port** — A numbered endpoint for a network service (22 SSH, 80 HTTP, 443 HTTPS).
- **Privilege escalation** — Gaining permissions beyond those intended, vertically (more rights) or
  horizontally (another user's rights).
- **Purple team** — Deliberate collaboration between offensive and defensive teams to improve detection.

## R

- **Red team** — Authorized adversary simulation, testing detection and response rather than only
  vulnerabilities.
- **Remediation** — The specific fix for a finding, with a way to verify it worked.
- **Risk** — The combination of likelihood and impact of a threat exploiting a vulnerability. The organising
  concept of the whole course.
- **Root cause** — The underlying reason a defect exists, as opposed to where it manifested.

## S

- **Scope** — The defined boundary of permitted testing: targets, methods, and time. Out-of-scope means
  prohibited, not "optional".
- **Secure coding** — Writing software so that common defect classes cannot occur, rather than filtering
  attacks afterwards.
- **SIEM** — Security Information and Event Management: centralised collection, correlation, and querying of
  security telemetry.
- **Sigma** — A vendor-neutral rule format for detections, translatable to many SIEM platforms.
- **Snapshot** — A saved VM state you can revert to. A reset button, not a backup.
- **SOC (Security Operations Centre)** — The team and process that monitor, triage, and respond to alerts.
- **SQL injection** — Injecting SQL through unsanitised input. Fixed by parameterised queries, not by
  escaping alone.
- **Subnet** — A logical division of a network, defined by an address and prefix length.
- **SSRF (Server-Side Request Forgery)** — Making a server issue requests to a destination the attacker
  chooses.

## T

- **Threat** — A potential cause of harm: an actor, a mistake, a failure.
- **Threat hunting** — Proactively searching for undetected adversary activity, driven by a hypothesis.
- **Threat intelligence** — Analysed information about threats, with confidence levels and relevance, used to
  prioritise defence.
- **Triage** — Rapidly assessing an alert to decide whether it is real, how urgent, and who should handle it.

## V

- **Vulnerability** — A weakness that can be exploited. Distinct from a threat (who might use it) and a risk
  (how bad it would be).
- **Vulnerability assessment** — Systematic identification of weaknesses, typically with scanners plus
  verification. Broader and shallower than a penetration test.

## X

- **XSS (Cross-Site Scripting)** — Injecting script into a page viewed by others. Fixed with context-aware
  output encoding and CSP.

## Z

- **Zero-day** — A vulnerability with no available patch at the time of exploitation.

---

## Related

- [How to Study](../start-here/how-to-study.md) — the review habits that make vocabulary stick
- [Curriculum](../curriculum/index.md) — where each term is introduced
- [Troubleshooting](../start-here/troubleshooting.md) — when a term in an error message is unfamiliar

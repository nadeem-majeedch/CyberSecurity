# Safety Policy

**Status:** binding on all learners, instructors, teaching assistants, and contributors.
**Version:** 1.0 · **Date:** 28 October 2026
**Review:** annually, or after any safety incident.

---

## 1. Purpose

This course teaches techniques that are illegal when applied to systems you do not own or have
written permission to test. The difference between a lab exercise and a criminal act is
**authorization**, not intent, curiosity, or educational purpose.

This policy defines exactly what you may do, on what, and what happens if you do something else.
It applies to every lab, every exercise, every optional challenge, and every "try it yourself"
suggestion in this material.

> **The single rule behind every other rule:** if you cannot point to the authorization that covers
> a target, that target is out of scope. Ignorance of the boundary is not permission to test it.

---

## 2. Scope of application

This policy applies to:

- Enrolled students and self-paced learners following this material.
- Instructors, teaching assistants, and guest contributors.
- Anyone writing, reviewing, or publishing content in this repository.
- Activity performed on personal equipment, university equipment, cloud accounts, or any network.

It applies **from the moment you begin Level 1**, including setup steps, not only during
"offensive" modules.

---

## 3. Authorized targets — the allowlist

You may interact with a target only if it falls into one of these categories:

| Category | Examples | Conditions |
| --- | --- | --- |
| **Localhost** | Services you start on `127.0.0.1` / `::1` | You started the service; it is not exposed to a network |
| **Your own isolated lab network** | VMs on a host-only or NAT segment; addresses in `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, or a private range defined in the lab spec | Isolation verified before any active testing |
| **Intentionally vulnerable applications** | DVWA, OWASP Juice Shop, OWASP WebGoat, Metasploitable-style VMs, CloudGoat-style cloud labs | Run locally or in your own sandbox account, at the pinned version |
| **Instructor-provided lab range** | A range built for the course, with a written scope statement | Only within the stated window and scope; credentials are personal, never shared |
| **Systems you own outright** | Your own laptop, your own home router | Still respect anyone else's data on shared or family devices |
| **Explicitly authorized third-party training platforms** | A platform whose own terms authorize testing of its designated targets | You comply with that platform's rules *and* this policy; see §9 |
| **Written permission from an asset owner** | A signed engagement letter or a scoped test agreement | Keep the document; do not exceed its scope, dates, or methods |

Everything else is **out of scope by default**. That includes your university's systems, your
employer's systems, your ISP, a friend's website, a public bug-bounty target without reading its
programme rules, and any address you found by accident.

---

## 4. Prohibited actions

The following are prohibited in this course, without exception, regardless of target:

1. **Scanning, enumerating, or probing any public IP address, domain, or service** that is not in
   the allowlist — including "just one `nmap` to see if it works".
2. **Exploiting any system you do not own or have written authorization to test**, even with a
   benign payload, even if the vulnerability is obvious.
3. **Denial-of-service, stress testing, or resource exhaustion** against anything, including lab
   targets shared with other learners.
4. **Credential attacks against real accounts** — password spraying, brute force, credential
   stuffing, or using credentials found in breaches, dumps, or stealer logs.
5. **Social engineering of real people** — phishing, pretexting, vishing, or impersonation, whether
   or not the target is a student, staff member, or relative. Simulated social engineering is
   permitted only inside a sanctioned tabletop exercise with named participants who consented.
6. **Accessing, copying, or retaining real personal data.** If a lab target contains anything that
   looks like real data (names, emails, national ID numbers, health or financial records, credentials),
   stop, do not copy it, and report it to the instructor.
7. **Distributing malware, live samples, or functional exploit code for real-world targets.**
   See §7.
8. **Bypassing university or employer security controls**, network filtering, or endpoint protection
   in order to complete an exercise.
9. **Publishing lab flags, answer keys, or another learner's work.** See the
   [assessment format](assessment-format.md) §7.
10. **Using anonymisation infrastructure to hide out-of-scope activity.** Tor, VPN chains, or proxy
    rotation do not make unauthorized activity acceptable; they make it look deliberate.
11. **Testing a target because a lab instruction was ambiguous.** Ambiguity means stop and ask.

If you believe an exercise requires one of the above, it does not. Report the exercise as a content
defect.

---

## 5. Legal framework

Cybersecurity law differs by jurisdiction, but the pattern is consistent: unauthorized access,
interference, and data acquisition are criminal offences, and "I was learning" is not a defence.

**Pakistan.** The Prevention of Electronic Crimes Act, 2016 (PECA) criminalises, among other things,
unauthorized access to an information system or data, unauthorized copying or transmission of data,
interference with an information system or data, unauthorized access to critical infrastructure
information systems, and unauthorized use of identity information (broadly ss. 3–6 and 13). Penalties
include imprisonment and fines, and are aggravated where critical infrastructure or sensitive data is
involved. PECA has been amended since 2016 — **verify the current text with qualified counsel before
relying on this summary**, which is included for orientation only and is not legal advice.

**Comparable provisions elsewhere** include the U.S. Computer Fraud and Abuse Act, the UK Computer
Misuse Act 1990, Canada's Criminal Code computer provisions, Australia's Criminal Code computer
offences, India's Information Technology Act 2000, and the EU Directive 2013/40/EU on attacks against
information systems — plus data protection regimes (GDPR, UK GDPR/DPA 2018, Pakistan's personal data
protection framework as enacted) whenever personal data is involved.

**Civil and institutional exposure.** Unauthorized testing can also breach contract, terms of
service, and university acceptable-use policies, leading to suspension, expulsion, loss of
internship or employment, and civil claims — consequences that frequently outlast any criminal
outcome.

**Course position.** This course requires authorization for every action. Where the law and this
policy differ, the stricter applies.

---

## 6. Isolation requirements

Before any active testing (discovery, enumeration, exploitation, traffic manipulation):

1. **Use a virtual machine.** Never run scanning or exploitation tooling from your host operating
   system against a network.
2. **Use host-only or NAT networking** for targets, not bridged mode. Bridged laboratory VMs expose
   vulnerable services to the physical network.
3. **Verify isolation and record it.** For example, confirm that `ping 8.8.8.8` fails from the target
   VM, or that the VM has no default route, and paste the output into your notes.
4. **Snapshot before testing**, and revert after. A snapshot is your reset button, not a backup of
   work you care about.
5. **Keep credentials and personal files out of the lab.** No shared folders exposing your home
   directory, no browser profiles signed into personal or university accounts.
6. **Use synthetic data.** If you need a database, generate one; do not import real data.
7. **Do not run intentionally vulnerable applications on a network interface reachable by others.**
   Bind them to `127.0.0.1` unless the lab explicitly requires otherwise.

A lab that cannot be isolated safely is a lab defect: report it rather than improvising.

---

## 7. Malware and exploit code

- **Live malware is never distributed through this repository.** The malware-analysis module uses
  inert samples, synthetic artefacts that emulate behaviour, or samples supplied by the instructor
  under a controlled distribution process.
- **Samples are handled only in an isolated, snapshotted analysis VM** with no shared folders, no
  clipboard sharing, and no bridged network. Networking is disabled or restricted to a simulated
  service.
- **EICAR** is acceptable as a detection test. Real families are not, outside instructor control.
- **Exploit code** in lessons is limited to what is necessary to demonstrate a class of
  vulnerability against a deliberately vulnerable application, and must be accompanied by the
  corresponding fix.
- **No weaponised tooling, no persistence, no evasion development** targeting production systems.
  Detection engineering may describe adversary techniques in order to detect them.
- **Never upload samples** to public multi-scanner services unless the instructor explicitly directs
  it and the sample is known-safe; submissions can disclose your identity and the sample itself.

---

## 8. Data handling and privacy

- Collect only synthetic or lab-generated data.
- Redact anything real before it enters notes, screenshots, or a report: credentials, tokens, personal
  identifiers, internal hostnames, and customer data.
- Store evidence in an encrypted location if it could identify a person.
- Delete lab evidence when the module ends; keep only what the assessment requires.
- Do not include real data in any file committed to this repository.
- If you discover real personal data in a lab target, stop and report it (§10).

---

## 9. External platforms and cloud

- Third-party training platforms (lab ranges, CTF sites, practice environments) authorize testing
  **only** within their own rules, designated targets, and acceptable-use terms. Their authorization
  does not extend to any other host, and this course's authorization does not extend to them.
- Cloud labs use **your own sandbox account** or an instructor-provided one, with budget alerts and a
  teardown checklist. Never test against another person's or organisation's cloud tenant, even if
  credentials were provided by mistake.
- Do not commit cloud keys, API tokens, or account identifiers to the repository. CI secret scanning
  exists to catch mistakes, not to license them.

---

## 10. If something goes wrong

**Scenario: you scanned or touched something out of scope.**
Stop immediately. Do not attempt to "clean up" traces or repeat the action to check. Record time,
target, command, and data touched. Notify the instructor in writing the same day. Early, honest
reporting is treated as a safety-process success; concealment is treated as a serious violation.

**Scenario: you found a real vulnerability by accident.**
Do not exploit it, do not enumerate further, do not screenshot data. Preserve only enough to
describe the issue (host, timestamp, observed behaviour), and report to the instructor, who will
handle responsible disclosure to the asset owner. Follow coordinated disclosure norms: no public
details before the owner has had a reasonable opportunity to remediate.

**Scenario: a lab target behaves destructively.**
Revert the snapshot, document what happened, and report it as a lab defect so the next learner does
not hit it.

**Scenario: someone asks you to test a system "just quickly".**
Decline and refer them to this policy. Authorization must come from the asset owner in writing, with
a defined scope — not from a colleague's verbal request.

---

## 11. Consequences

Violations are handled as conduct matters, not as technical mistakes. Depending on severity and
intent, consequences include:

| Severity | Example | Consequence |
| --- | --- | --- |
| Minor | Isolation check skipped; vulnerability app bound to a LAN interface | Written warning; lab must be repeated with evidence |
| Moderate | Scanning a non-allowlisted host on a private network | Lab and level assessment voided; mandatory ethics review; instructor discretion over continuation |
| Serious | Testing a public system, accessing real data, distributing malware or flags | Course termination, referral under the university's disciplinary policy, and where applicable referral to law enforcement |

Repeated minor issues escalate. The instructor may also require a written reflection or a supervised
re-run before readmission to practical work.

---

## 12. Acknowledgement

Learners confirm the following before their first lab (recorded in the learner's own notes; no data
is collected by this site):

> I have read the Safety Policy. I will only test systems I own, systems running in my own isolated
> lab, intentionally vulnerable applications provided for this course, or systems for which I hold
> written authorization. I understand that unauthorized access or interference is a criminal offence
> under PECA 2016 and equivalent laws elsewhere, that "educational purpose" is not a legal defence,
> and that I am responsible for verifying the scope of every target before I act. I will stop and ask
> if I am unsure, and I will report any accidental out-of-scope activity immediately.

Instructor-supervised cohorts may additionally require a signed scope-and-ethics statement as
described in CYB-103.

---

## 13. Exceptions and review

Exceptions (for example, a sanctioned engagement, a partner lab range, or a research project with
ethics approval) must be:

1. Requested in writing, naming the target, dates, methods, and data involved.
2. Approved in writing by the instructor before any activity.
3. Recorded with the approval reference in the learner's lab notes and in the relevant lab page.

This policy is reviewed annually and after any incident. Proposed changes go through the same review
gate as course content, with the safety reviewer's approval recorded in the changelog.

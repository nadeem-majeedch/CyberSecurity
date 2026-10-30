---
title: "Level 2 Integrated Assessment — Enumerate, Validate, Report"
description: "A four-hour assessment of an unfamiliar lab host plus a ninety-minute written justification of scan choices, false-positive decisions and evidence limits."
module_code: ASM-L2A
level: 2
kind: assessment
prerequisites: [CYB-203, CYB-204, CYB-206]
estimated_minutes: 330
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-206-02, LAB-206-03]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, level-2, enumeration, reporting, false-positives]
---

# Level 2 Integrated Assessment

**Part A:** practical, 4 hours, 70 marks. **Part B:** written, 90 minutes, 30 marks. Open book.

The difference between this and the module labs is that nobody tells you what is wrong with the target, and
some of what a scanner reports will be wrong. Your marks come from what you can prove, not from how many lines
your findings table has.

---

## The brief

> *A small business has asked for a health check of one server before it is moved to a new office. You have a
> two-hour window on the host, a lab network, and no credentials for the application. Produce a findings table
> and a short report the owner can act on. Anything you cannot demonstrate, you must label as unverified.*

**Target:** your own lab VM, or an instructor-provided host on the isolated range. If you are alone, build the
target by applying at least four deliberate weaknesses from the list below — this is the only assessment in the
course where you are expected to make your own target *worse*.

| Weakening option | How | Why it is useful |
| --- | --- | --- |
| Anonymous FTP | Install and enable `vsftpd` with `anonymous_enable=YES` | Tests version and configuration findings |
| Root SSH with passwords | `PermitRootLogin yes`, `PasswordAuthentication yes` | Tests privilege and authentication findings |
| Database on all interfaces | Bind MySQL/PostgreSQL to `0.0.0.0` | Tests bind-address interpretation |
| World-writable web directory | `chmod 777 /var/www/html/uploads` | Tests permission findings |
| Old PHP banner | Install an end-of-life PHP package | Tests version-versus-patch-level reasoning |
| Extra listener | `nc -lk 0.0.0.0 9999` | Tests whether "open port" is a finding at all |

**Constraints:** no exploitation, no denial of service, no authenticated testing, no traffic to anything
outside the range. Port scanning is limited to the target's address.

---

## Part A — Practical (70 marks)

**A1. Discovery and inventory (15 marks).** Identify live hosts on the range, then enumerate the target's TCP
services and a small, named set of UDP ports. Record each service with the method that confirmed it. Produce a
table with: port, protocol, service, version observed, how confirmed, and confidence.

**A2. Configuration review (20 marks).** With local access to the target (console or SSH as your own account),
inspect users, groups, permissions, services, listening sockets and scheduled tasks. Identify at least four
issues that a remote scan would not have shown. For each: command, output, and why it matters.

**A3. Validation (10 marks).** For every finding, state the check that turned a claim into evidence. Where a
scanner claim could not be confirmed, record it as rejected and say why.

**A4. Findings table and report (20 marks).** Produce the report using the
[Assessment Report Template](../policies/assessment-report-template.md): executive summary, scope, method,
findings with severity and remediation, and limitations.

**A5. Evidence package (5 marks).** Named files, SHA-256 hashes for captures and exports, and a README mapping
artefacts to findings.

### Artefacts

```text
level-2-assessment/
├── README.md
├── 01-inventory.md
├── 02-configuration-review.md
├── 03-validation-log.md
├── 04-report.md
└── evidence/            # captures, command output, hashes
```

---

## Part B — Written justification (30 marks, 90 minutes)

**B1 (10 marks).** Justify your scan sequence: what you ran first, what you deliberately did not run, and why
the order matters for both evidence quality and safety.

**B2 (8 marks).** Name one scanner claim you rejected. What did you check, and what would have changed your
mind? Explain why rejecting it was the correct call rather than caution.

**B3 (7 marks).** Which finding in your report is the weakest, and what evidence would make it strong? Be
specific about the command or observation that is missing.

**B4 (5 marks).** State three things your assessment cannot tell the business owner, and how you would phrase
each limitation in the report without undermining the findings you did establish.

---

## Marking

### Part A (70)

| Task | Marks | Full marks requires |
| --- | --- | --- |
| A1 Inventory | 15 | Confirmed services distinguished from inferred ones; UDP states not overstated |
| A2 Configuration review | 20 | Four or more local findings, each with command and output; at least one not visible remotely |
| A3 Validation | 10 | A validation entry per finding; at least one rejected claim with reasoning |
| A4 Report | 20 | Template followed; severities justified; remediation specific and verifiable |
| A5 Evidence | 5 | Hashes, naming, README; a peer could replay |

### Part B (30)

| Criterion | Marks | Descriptor |
| --- | --- | --- |
| Method justification | 10 | Sequence defended; rejected options named |
| Evidence discipline | 8 | Distinguishes demonstrated from inferred; rejection reasoning is technical, not timid |
| Self-critique | 7 | Identifies the weakest finding accurately and says what would fix it |
| Limits and communication | 5 | Limitations stated plainly, without disowning the findings |

### Domain weights

| Domain | Weight |
| --- | --- |
| Reconnaissance and enumeration | 30% |
| Analysis and validation | 30% |
| Reporting | 25% |
| Safety and scope | 15% |

The safety gate applies: scanning an address outside the brief voids the assessment.

---

## Self-marking

1. Mark Part A from the artefacts alone, without your memory of the session.
2. Apply the replay test to one finding: hand your notes to a peer and see whether they can reproduce the
   evidence. Every question they ask is a documentation gap.
3. Mark Part B against the elements in the [key](level-2-key.md#level-2-integrated-assessment-model-answers),
   not against its wording.
4. Record the weakest domain; that is what Level 3 will expose again.

---

## Common pitfalls

- **A findings table built from scanner output.** Every row needs the check that confirmed it.
- **Severity by vibes.** "Critical" for a banner is the fastest way to lose the reporting marks.
- **No rejected findings.** A submission with zero false positives usually means nothing was validated.
- **Remediation that is a verb.** "Secure FTP" cannot be retested; "set `anonymous_enable=NO`, restart, retry
  anonymous login and record `530`" can.
- **Silent scope drift.** Noticing another host on the range and scanning it "because it was there" voids the
  safety criterion.

---

## Submission checklist

- [ ] Inventory with confirmation method and confidence per service
- [ ] Four or more local configuration findings with commands and output
- [ ] Validation log including at least one rejected claim
- [ ] Report using the template, with scope and limitations
- [ ] Remediation steps that include a verification command
- [ ] Evidence hashed and mapped in the README
- [ ] No traffic to any address outside the brief

---

## Related

- [Level 2 quiz](level-2-quiz.md) · [Answer key](level-2-key.md)
- [CYB-206 · Host Inspection and Hardening Assessment](../levels/level-2-tooling/06-host-inspection-and-hardening/index.md)
- [Assessment Report Template](../policies/assessment-report-template.md)
- [Level 3](../levels/level-3.md)

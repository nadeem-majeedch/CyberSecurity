---
title: "CYB-406 · Digital Forensics"
description: "Acquire evidence without altering it, build a timeline from a disk image, classify artefacts with YARA, and write findings the evidence supports."
module_code: CYB-406
level: 4
kind: reference
prerequisites: [CYB-404, CYB-105]
estimated_minutes: 840
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-406-01, LAB-406-02, LAB-406-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [forensics, chain-of-custody, hashing, sleuthkit, autopsy, yara, volatility, timeline]
---

# CYB-406 · Digital Forensics

**Level 4** · 14 hours · **Prerequisites:** [CYB-404](../04-detection-and-siem/index.md), [CYB-105](../../level-1-foundations/06-computer-hardware-os-fundamentals/index.md)

## Why this module exists

Everything else in Level 4 produces a conclusion quickly. Forensics produces one that must survive someone else
checking it.

That changes the method. You work on copies, you hash them, you record who touched what and when, and you distinguish
what the evidence *shows* from what you *think happened*. A timeline with one wrong timezone is worse than no
timeline, because it is persuasive and wrong.

This module builds that discipline on synthetic evidence you create yourself, so mistakes cost nothing and the habit
survives into work where they cost a case.

## Module outcomes

By the end of this module you can:

- Explain forensic soundness and apply it: acquire, hash, verify, and never analyse the original.
- Complete an evidence register and chain-of-custody record that a reviewer can follow.
- Acquire a disk image and a memory image from lab systems, with integrity verification at both ends.
- Use The Sleuth Kit to list, extract and recover files, and build a MACB timeline that is explicit about timezone.
- Classify artefacts with YARA, and explain why a YARA hit is a lead rather than a conclusion.
- Map Volatility 3 plugins to the questions they answer, and state what memory analysis cannot recover.
- Write findings that separate observation, inference and confidence.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Soundness, Artefacts and Timelines](01-forensic-soundness.md) | 3 h |
| Lab | [LAB-406-01 · Evidence Register and Verified Acquisition](lab-01-acquisition-and-custody.md) | 4 h |
| Lab | [LAB-406-02 · Disk Triage and a Defensible Timeline](lab-02-disk-and-timeline.md) | 4 h |
| Lab | [LAB-406-03 · YARA Classification and Memory Artefacts](lab-03-yara-and-memory.md) | 3 h |

## What you need

- `lab-ubuntu` with `sleuthkit`, `ewf-tools`, `yara`, and a second scratch disk.
- A **synthetic disk image** created in LAB-406-01 from a file-backed ext4 filesystem — no real user data, no real
  malware, and small enough to hash in seconds.
- Autopsy 4.23.1 (optional GUI) if you want to compare interfaces; the command-line tools are the reference.
- Volatility 3 for the memory section, and a memory image you acquire from your own lab VM. If you cannot acquire
  one, the plugin-mapping exercise still stands on its own.
- YARA 4.6.0.

## A note on what is synthetic

The disk image, the deleted files, the "webshell" text and the memory strings are all **created by you** for the
exercise. Nothing in this module requires a real malware sample, a real victim system, or a real memory capture from
anyone else's machine.

That is deliberate: the skills are acquisition discipline, artefact interpretation and reporting. A real sample adds
risk, not learning, at this stage.

## Assessment

LAB-406-01 is marked on integrity: hashes before and after, a register with no gaps, and a custody record that shows
the original was never opened for analysis. LAB-406-02 is marked on the timeline's timezone statement and on whether
findings distinguish observation from inference. LAB-406-03 requires a YARA rule with a negative test and a memory
section that names its limits.

## Where this fits

[CYB-407](../07-incident-response/index.md) uses these artefacts during containment and eradication, where the
temptation to "just clean it up" destroys exactly the evidence this module teaches you to preserve.

## References

1. NIST SP 800-86 — Guide to Integrating Forensic Techniques into Incident Response. Accessed 2026-10-29.
2. NIST SP 800-101 Rev. 1 — Guidelines on Mobile Device Forensics (acquisition and integrity principles). Accessed
   2026-10-29.
3. The Sleuth Kit 4.12 — `fls`, `icat`, `istat`, `mactime`, `tsk_recover`. <https://www.sleuthkit.org/sleuthkit/man/>
   Accessed 2026-10-29.
4. Autopsy 4.23.1. <https://www.autopsy.com/> Accessed 2026-10-29.
5. Volatility 3 — plugin reference and symbol tables. <https://volatility3.readthedocs.io/> Accessed 2026-10-29.
6. YARA 4.6.0 documentation. <https://yara.readthedocs.io/> Accessed 2026-10-29.
7. RFC 3227 — Guidelines for Evidence Collection and Archiving. Accessed 2026-10-29.

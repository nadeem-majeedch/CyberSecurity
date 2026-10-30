---
title: "Soundness, Artefacts and Timelines"
description: "Order of volatility, hashing and custody, what disk and memory artefacts can show, and how to build a timeline that survives review."
module_code: CYB-406
level: 4
kind: lesson
prerequisites: [CYB-404]
estimated_minutes: 180
difficulty: advanced
safety: none
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [forensic-soundness, chain-of-custody, mactime, volatility, yara, anti-forensics]
---

# Soundness, Artefacts and Timelines

## What this lesson covers

1. Forensic soundness: what it means operationally, and the four habits that implement it.
2. Order of volatility, and why it dictates the acquisition sequence.
3. Hashing, verification, and an evidence register that a reviewer can follow.
4. Disk artefacts: inodes, MFT records, timestamps, deleted data, unallocated space.
5. Building a timeline, and the timezone statement that makes it defensible.
6. Memory: what lives only in RAM, which plugins answer which question, and the limits.
7. YARA: useful triage, dangerous as proof.
8. Anti-forensics, and what survives it.
9. Writing findings: observation, inference, confidence.

## Why it matters

Forensics is the part of security where being wrong has consequences beyond a missed alert. A conclusion that cannot
be reproduced is not evidence, and a timeline with an unstated timezone can point at the wrong person.

Soundness is not bureaucracy. It is the set of practices that let someone else repeat your work and reach the same
conclusion — or show you where you went wrong.

## 1. Forensic soundness in four habits

1. **Preserve the original.** Acquire an image; analyse the image. Opening the original for "a quick look" changes
   access times and, on a live system, changes state.
2. **Hash before and after.** SHA-256 of the source, of the image, and of any derived extract. Matching hashes show the
   copy is faithful; a second hash after analysis shows the copy was not altered.
3. **Record everything you do.** Tool and version, command, time (with timezone), operator, and result. Notes written
   afterwards are reconstruction, not a record.
4. **Keep custody continuous.** Every transfer gets a signature, a time, and a purpose. A gap in custody is a gap in
   the evidence, regardless of how good the analysis was.

**What soundness does not mean:** that you can never touch a live system. Incident response routinely must. It means
you document the trade-off: what you changed by acting, and why acting was necessary.

## 2. Order of volatility

Acquire the most perishable evidence first:

| Order | Evidence | Why it disappears |
| --- | --- | --- |
| 1 | CPU registers, cache | Immediately |
| 2 | RAM, running processes, network connections | Reboot, process exit, connection close |
| 3 | Swap / pagefile, temporary files | Overwritten by use |
| 4 | Disk | Deleted data is overwritten over time |
| 5 | Remote logs, SIEM | Retention windows, rotation |
| 6 | Backups, archives | Slowest to change, still finite |

**Practical consequence:** if a host is running and you need memory, capture memory before you image the disk.
Imaging first can take an hour, during which the memory you needed is gone.

**The exception that proves the rule:** if the system is cryptographically locked or actively being wiped, pulling the
power may preserve more than an orderly shutdown. That decision is made by the incident lead, documented, and never
by habit.

## 3. Hashing and the evidence register

```bash
sha256sum /dev/sdb > source-hash.txt          # the device, if you have a write blocker
sudo dcfldd if=/dev/sdb of=/evidence/disk.img bs=4M hash=sha256 hashwindow=0 hashlog=dcfldd.log
sha256sum /evidence/disk.img
```

**Expected:** the source hash and the image hash match, and `dcfldd`'s log records the same value. If they differ, stop
and find out why before analysing anything.

For a file-backed synthetic image (the approach in LAB-406-01), the same discipline applies with a hash of the image
file before and after every analysis session.

**An evidence register entry needs:**

| Field | Example |
| --- | --- |
| Exhibit ID | `EX-406-01` |
| Description | Synthetic ext4 image, 512 MiB, created from `lab-ubuntu` scratch disk |
| Source | `lab-ubuntu`, `/dev/sdb`, acquired 2026-10-29 09:14 UTC |
| Acquisition method and tool | `dcfldd 1.9.1`, write-blocked via lab policy (no writes issued) |
| Hash | SHA-256 `…` (full value, not truncated) |
| Storage | `/evidence/EX-406-01/disk.img`, read-only mount, host `lab-ubuntu` |
| Custodian and transfers | Name, role, time, signature, purpose |
| Analysis performed | Tools, versions, commands, outputs produced |

**Write the hash out in full.** A truncated hash is unverifiable, and copying the first eight characters is a habit
that ruins evidence registers.

## 4. Disk artefacts worth knowing

| Artefact | What it tells you | Caveat |
| --- | --- | --- |
| Inode / MFT record | File metadata, timestamps, data runs | Timestamps are updatable by the system and by attackers |
| Directory entry | Name-to-inode mapping, deleted entries | Deleted entries may persist after the data is gone |
| Journal (`$LogFile`, ext4 journal) | Recent metadata changes | Circular; overwritten quickly |
| Unallocated space | Deleted content, fragments | No structure; carving is probabilistic |
| Slack space | Tail of the last cluster | Small but occasionally decisive |
| Prefetch / Amcache (Windows) | Execution history | Not present on servers by default; can be cleared |
| Shell history, `.bash_history` | Commands typed | Often disabled, truncated, or edited |
| Systemd journal / event logs | Service and auth activity | Rotation; can be cleared by an administrator |

**MACB** stands for Modified, Accessed, Changed (inode metadata) and Birth (creation), where the filesystem supports
it. Not every filesystem records all four, and "accessed" is often disabled by `noatime`. State which timestamps your
filesystem actually maintains before drawing conclusions from their absence.

## 5. Timelines

A body file is the intermediate representation:

```bash
fls -r -m / -o 2048 disk.img > body.txt
mactime -b body.txt -d -z UTC > timeline.csv
head -5 timeline.csv
```

- `-m /` sets the mount prefix used in paths.
- `-o 2048` is the partition offset in sectors; get it from `mmls disk.img`. Using the wrong offset is the most common
  reason a "disk" appears empty.
- `-z UTC` states the timezone. **Always state it.** A timeline without a timezone is a list of numbers.

A defensible timeline section says: "All times UTC, derived from filesystem timestamps, which reflect the system clock
at write time; the host's clock was within N seconds of NTP per the SIEM." That sentence is what separates analysis
from storytelling.

**Super-timelines** merge disk, log and network events into one ordered view. They are powerful and easy to get wrong:
different sources have different clock accuracy, and a 30-second skew reorders events at the boundaries where the
interesting things happen.

## 6. Memory forensics

Memory holds what disk never sees: running processes, injected code, network connections, decrypted keys, and
command lines that were never written to a log.

| Question | Volatility 3 plugin | What it shows |
| --- | --- | --- |
| What was running? | `windows.pslist`, `linux.pslist` | Process list from kernel structures |
| What was hidden? | `windows.psscan` | Pool scanning; finds terminated or unlinked processes |
| Who started what? | `windows.pstree`, `windows.cmdline` | Parent-child relationships and arguments |
| What network activity? | `windows.netscan` | Connections and listening sockets |
| What is suspicious? | `windows.malfind` | Executable memory regions not backed by a file |
| What was loaded? | `windows.dlllist` | Loaded modules and paths |

**Limits to state explicitly:**

- Symbol tables must match the kernel version; a mismatch produces errors, not results.
- Memory is smeared: freed pages are reused, so absence of an artefact is weak evidence.
- Full-disk encryption and memory encryption reduce what is recoverable.
- Acquiring memory changes the system (a driver is loaded), which must be documented.
- A memory image is highly sensitive: it can contain credentials and personal data. Handle, store and destroy it
  accordingly.

**Acquisition in this course** is from your own lab VM with `avml` (Linux) or `winpmem` (Windows), into the isolated
lab, hashed immediately. Never acquire memory from a system you do not own.

## 7. YARA: triage, not proof

```yara
rule LAB406_Synthetic_Marker
{
    meta:
        author = "CYB-406 lab"
        description = "Detects a harmless marker string used in synthetic lab artefacts"
        date = "2026-10-29"
    strings:
        $a = "LAB406-WEBSHELL-MARKER" ascii wide
        $b = /eval\s*\(\s*base64_decode\s*\(/ ascii
    condition:
        any of them
}
```

- `strings` define the evidence; `condition` defines the logic. Both need testing.
- Modifiers matter: `ascii`, `wide`, `nocase`, `fullword`. A rule without `wide` misses UTF-16 strings in Windows
  artefacts.
- **A hit means "this file matches this pattern", not "this file is malicious".** Shared libraries, installers and
  test fixtures produce hits.
- Every rule needs a negative test: a benign file that must not match.
- Scanning cost grows with file size and rule complexity; scope scans to the evidence you have, not the whole disk,
  unless you have time.

## 8. Anti-forensics

| Technique | What it removes | What usually remains |
| --- | --- | --- |
| Timestomping | Plausible timestamps | Inconsistency between timestamps and logs; `$STANDARD_INFORMATION` vs `$FILE_NAME` on NTFS |
| Log deletion | Event log entries | Gaps, cleared-log events, remote copies in the SIEM |
| Secure wipe of files | File content | Directory entries, journal traces, backups |
| Living off the land | Malware on disk | Process ancestry, command lines, network flows |
| Encryption | Readable content | Metadata, key material in memory, access patterns |

The pattern: anti-forensics usually creates *absence* where absence is itself unusual. "No logons for six hours on a
busy host" is a finding.

## 9. Writing findings

Separate three things in every finding:

1. **Observation** — what the artefact says. "`/tmp/.x` was created at 10:42:11 UTC and executed at 10:42:19 UTC."
2. **Inference** — what you conclude. "This is consistent with a dropper executing a payload."
3. **Confidence and alternatives** — "High confidence; the alternative — an administrator running a test script — is
   not supported by the absence of a corresponding shell history entry or change ticket."

Then state what the evidence **cannot** show: whether data left the host, who was at the keyboard, or whether the
same actor did something else. Reports that admit limits are trusted more, not less.

## Common misconceptions

| Belief | Reality |
| --- | --- |
| "I'll just look at the original, it's read-only" | Mounting read-write, or even reading with some tools, can change metadata. Work on a copy. |
| "The hash matches, so the analysis is right" | The hash proves the copy is faithful. It says nothing about your interpretation. |
| "Timestamps prove when it happened" | They prove what the system clock recorded, which can be wrong or altered. |
| "Absence of evidence is evidence of absence" | In memory and logs, absence often means rotation, smearing, or a disabled control. |
| "A YARA hit means malware" | It means a pattern matched. Corroborate with behaviour and context. |
| "Timeline sorted by time is a timeline" | Without timezone, source and clock accuracy, it is a sorted list. |

## Key terms

**forensic soundness** · **order of volatility** · **write blocker** · **SHA-256** · **evidence register** ·
**chain of custody** · **inode** · **MFT** · **MACB** · **unallocated** · **body file** · **super-timeline** ·
**symbol table** · **smearing** · **malfind** · **YARA modifier** · **timestomping**

## Check your understanding

**1. Why hash the image again after analysis?**

<details><summary>Answer</summary>
To show the analysis did not alter the copy. A changed hash invalidates every result derived from that image, so it
must be investigated rather than explained away.
</details>

**2. A host is running and you need both memory and disk. What order, and why?**

<details><summary>Answer</summary>
Memory first: it is lost on reboot or process exit, while disk persists. Then image the disk. Document any state change
caused by the memory acquisition tool.
</details>

**3. `fls` returns nothing on a disk image. What is the first thing you check?**

<details><summary>Answer</summary>
The partition offset from `mmls`. Analysing the whole disk as if it were a filesystem is the usual cause; supply `-o`
with the start sector of the target partition.
</details>

**4. Your timeline places a login before the malware drop, but the SIEM says otherwise. What do you check?**

<details><summary>Answer</summary>
Timezone and clock accuracy on both sources, then the resolution of each timestamp. Reconcile by converting
everything to UTC with known offsets, and state the residual uncertainty.
</details>

**5. A YARA rule matches a legitimate admin tool in your evidence set. What now?**

<details><summary>Answer</summary>
The rule is too broad for this triage. Narrow it (path scope, additional strings, file type), record the false
positive, and keep the original rule's intent. Do not delete the tool from the evidence.
</details>

## Summary

- Soundness = preserve, hash, record, custody. Four habits, applied every time.
- Acquire in order of volatility; memory before disk on a running host.
- Evidence registers carry full hashes and complete custody, or they are not evidence registers.
- Disk artefacts have caveats; state which timestamps exist and what they mean.
- Timelines require an explicit timezone and a statement of clock accuracy.
- Memory answers questions disk cannot, within well-defined limits.
- YARA is triage; corroborate before concluding.
- Findings separate observation, inference and confidence.

## Next

[LAB-406-01](lab-01-acquisition-and-custody.md) builds the synthetic evidence set and the register that everything else
in this module depends on.

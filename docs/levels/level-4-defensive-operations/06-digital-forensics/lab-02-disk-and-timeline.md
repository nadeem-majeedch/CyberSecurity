---
title: "LAB-406-02 · Disk Triage and a Defensible Timeline"
description: "List, extract and recover files from the verified image, then build a UTC timeline and separate observation from inference."
module_code: CYB-406
level: 4
kind: lab
prerequisites: [CYB-406]
estimated_minutes: 240
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-406-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [sleuthkit, fls, icat, mactime, deleted-files, timeline, autopsy]
---

# LAB-406-02 · Disk Triage and a Defensible Timeline

## Scenario and background

The verified image from LAB-406-01 contains four synthetic files and one deliberate deletion. Your task is to
establish what was on the filesystem, when it changed, and what can be recovered — and then to say clearly which of
those statements the evidence supports.

The deletion is the interesting part: the file is gone from the directory listing, but its data may still be in the
image. Recovery is not the same as proof of execution, and the report must say so.

## Learning objectives

1. Continue the chain of custody by verifying the image hash before analysis.
2. List allocated and deleted entries, and distinguish them.
3. Extract a file by inode and verify the extracted content.
4. Attempt recovery of a deleted file and explain the result either way.
5. Build a MACB timeline in UTC and interpret `mtime`, `atime`, `ctime` and `crtime` correctly.
6. Write findings that separate observation, inference, confidence and non-conclusions.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Sleuth Kit | 4.12 | `fls`, `istat`, `icat`, `mactime`, `tsk_recover` |
| The image | `EX-406-01.img` | From LAB-406-01, offset 2048 |
| Autopsy | 4.23.1 | Optional GUI comparison |

!!! warning "Authorized scope — read before you begin"
    **Analyse only the copy** (`EX-406-01.img`). The original in `~/lab406/source` stays read-only and unopened.

    **All content is synthetic.** The `index.php` and `drop.sh` files are text markers; they execute nothing. Do not
    deploy them to a web server, even in the lab.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The scenario is a compromised application host: a marker file in the web root and a deleted script in `/tmp`. The
question is what the filesystem can establish about both — and the failure mode is overclaiming, such as treating a
recovered file as proof that it ran.

## Procedure

### 1. Verify the image before touching it

```bash
cd ~/lab406/evidence
sha256sum -c EX-406-01.sha256
sha256sum EX-406-01.img
```

**Expected:** `OK`, and the hash matches the register. Record the check and the time in `custody.md`. This is the
analysis session's opening entry, every session.

### 2. List the filesystem

```bash
fls -r -p -o 2048 EX-406-01.img | tee allocations.txt
```

**Expected:** the four files with full paths, plus directories. Note the inode numbers; you will need the one for
`index.php`.

```bash
fls -r -d -o 2048 EX-406-01.img | tee deleted.txt
```

**Expected:** a deleted entry for `drop.sh` (marked with a `*` or `(deleted)` depending on version), with an inode
number. If nothing appears, the deletion may have been journaled away — record that as the result rather than
adjusting the method until something appears.

### 3. Inspect and extract one file

```bash
istat -o 2048 EX-406-01.img <INODE_OF_INDEX_PHP> | tee istat-index.txt
icat -o 2048 EX-406-01.img <INODE_OF_INDEX_PHP> > extracted-index.php
sha256sum extracted-index.php | tee extracted-index.sha256
cat extracted-index.php
```

**Expected:** the file contains the `LAB406-WEBSHELL-MARKER` comment and an `echo`. `istat` shows the inode's
timestamps, size and block allocation.

**Record the extracted file's hash.** If you later run YARA on it, the hash ties the rule result to a specific
artefact.

### 4. Recover the deleted file

```bash
icat -o 2048 EX-406-01.img <INODE_OF_DROP_SH> > recovered-drop.sh 2>recovery-error.txt
ls -l recovered-drop.sh; cat recovery-error.txt
```

**Expected:** either the full content (`LAB406-DROPPER-MARKER`) or an empty file with an error about unallocated
blocks. **Both outcomes are valid findings.** If the blocks were reused, the content is gone and the only evidence is
the directory entry.

Try the batch recovery interface as a cross-check:

```bash
mkdir -p recovered
tsk_recover -o 2048 -d EX-406-01.img recovered/ 2>&1 | tee tsk-recover.log
find recovered -type f -ls
```

**Expected:** deleted files extracted with their original paths where recoverable. Compare with `icat`.

### 5. Build the timeline

```bash
fls -r -m / -o 2048 EX-406-01.img > body.txt
mactime -b body.txt -d -z UTC > timeline.csv
head -10 timeline.csv
```

**Expected:** a CSV with date, size, type (macb), mode, uid/gid, name. The `type` column tells you which timestamp
produced each row: `m` modified, `a` accessed, `c` changed, `b` birth (if the filesystem records it).

Answer these from `timeline.csv`, quoting the rows:

1. When was `index.php` modified, and when was its inode changed?
2. Does `notes.txt` have a birth time? If not, why not — does ext4 record `crtime` here, and did your image creation
   method preserve it?
3. What is the latest timestamp in the image, and what produced it?

**Expected learning point:** `ctime` is inode-change time, not creation time. Because the files were created by
`tee`/`touch` and the image was made in one session, `ctime` values cluster at image creation, while `mtime` values
carry the `touch -d` times you set. Confusing the two is the most common timeline error in student reports.

### 6. Reconcile with the log file

```bash
icat -o 2048 EX-406-01.img <INODE_OF_LAB406_LOG> > extracted-lab406.log
cat extracted-lab406.log
grep 'lab406.log' timeline.csv
```

**Expected:** the log's final line is `22:07:12Z`, and the file's `mtime` is also `22:07:12` because you set it that
way. Now answer: if the final log line had been `22:09:00` while `mtime` was `22:07:12`, what would that mean, and
which source would you trust? (Answer: a discrepancy worth investigating — clock adjustment, copied file, or edited
content. Neither source is automatically correct.)

### 7. Optional: compare with Autopsy

Open the image in Autopsy 4.23.1 as a disk image, add an ingest module for file type identification, and compare its
timeline view with `timeline.csv`. Record one thing Autopsy shows more clearly and one thing the command line shows
more precisely. Do not let the GUI replace the hashes and the UTC statement.

### 8. Write the findings

`findings.md`, for each of the following, with the three-part structure:

| # | Question | What to write |
| --- | --- | --- |
| F1 | What files were present in the web root? | Observation with path, inode, hash |
| F2 | What was deleted, and is it recoverable? | Observation plus the recovery result, including failure |
| F3 | When did the web-root file change, relative to the log events? | Observation with UTC times, then inference |
| F4 | Does the evidence show the deleted script executed? | **Non-conclusion**: filesystem timestamps do not record execution; state what would (process telemetry, auditd, shell history) |
| F5 | What is the confidence in F3? | Confidence with the reason (single source, clock assumptions) |

F4 is the marked item. A report that claims execution from an `mtime` is wrong, and the rubric reflects it.

## Evidence to collect

- `allocations.txt`, `deleted.txt`, `istat-index.txt`.
- `extracted-index.php` and its hash.
- `recovered-drop.sh` or `recovery-error.txt` (whichever your image produced).
- `body.txt`, `timeline.csv`.
- `extracted-lab406.log`.
- `findings.md` with observations, inferences, confidence and non-conclusions.
- The new `custody.md` entries for this session, including the hash verification at the start.

## Verification

- [ ] Image hash verified at the start of the session, and recorded.
- [ ] Allocated and deleted listings both produced.
- [ ] Extracted file hash recorded and tied to the rule result later.
- [ ] Recovery attempted with both `icat` and `tsk_recover`, with the outcome stated honestly.
- [ ] Timeline generated with `-z UTC` and the timezone stated in the report.
- [ ] `mtime` and `ctime` interpreted correctly, with an example from your own timeline.
- [ ] F4 states a non-conclusion and names the telemetry that would answer it.
- [ ] Every claim cites a file, inode, or timeline row.

## Teardown and reset

```bash
cd ~/lab406/evidence
rm -rf recovered extracted-*.php recovered-drop.sh body.txt
```

Keep `EX-406-01.img`, `timeline.csv`, `findings.md` and the register. Delete derived extracts only after your report
cites their hashes.

## Reflection

1. `icat` recovered the file, or it did not. In each case, what can you say about the inode's block pointers?
2. Your timeline shows `ctime` later than `mtime` for most files. Explain why that is expected here and when it would
   be suspicious.
3. The log's last line and the file's `mtime` agree because you set them to agree. What would you check first if they
   disagreed in a real case?
4. Why is "the file was recovered" weaker evidence than "the file was executed", and which Level 4 lab would supply
   the latter?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Triage | Lists files | Lists allocated and deleted | Extracts with inode, records hashes |
| Recovery | Not attempted | Attempted | Outcome explained in terms of block allocation |
| Timeline | Sorted output | UTC stated | Timestamp types interpreted, discrepancy reasoning correct |
| Findings | Narrative | Observations and inferences | Non-conclusion stated with the telemetry that would answer it |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `fls` prints nothing | Missing or wrong offset | `mmls`; use `-o <start sector>` |
| No deleted entry | Deletion journaled/overwritten, or wrong inode | Try `fls -d -r`; record the result as-is |
| `icat` output is empty | Blocks reused or freed | Check `istat` block list; that is a finding, not a tool error |
| `mactime` complains about input | Body file from a different image or malformed | Regenerate with `fls -m /` |
| All times look shifted | Local timezone used | Re-run with `-z UTC`; state the zone |
| Hash mismatch at session start | Wrong file, or copy altered | Stop; identify the file; never "fix" the hash |

## References

1. The Sleuth Kit — `fls`, `istat`, `icat`, `tsk_recover`, `mactime` man pages.
   <https://www.sleuthkit.org/sleuthkit/man/> Accessed 2026-10-29.
2. NIST SP 800-86 — forensic process and reporting. Accessed 2026-10-29.
3. Autopsy 4.23.1 — ingest modules and timeline view. <https://www.autopsy.com/> Accessed 2026-10-29.
4. ext4 — inode timestamps, `crtime` support, journal behaviour. Accessed 2026-10-29.

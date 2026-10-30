---
title: "LAB-406-01 · Evidence Register and Verified Acquisition"
description: "Build a synthetic disk image, acquire it with hashing, and complete a custody record that shows the original was never analysed."
module_code: CYB-406
level: 4
kind: lab
prerequisites: [CYB-406]
estimated_minutes: 240
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-406-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [acquisition, hashing, chain-of-custody, ext4, dcfldd, evidence-register]
---

# LAB-406-01 · Evidence Register and Verified Acquisition

## Scenario and background

You are asked to examine a host's disk. Before any analysis, three things must exist: a faithful copy, a hash that
proves it, and a record of who handled what.

You will build the evidence yourself — a small ext4 image containing synthetic files, including one deliberate
deletion — then acquire it with hashing and complete the register. Every later lab in this module analyses the copy,
never the original.

## Learning objectives

1. Create a partitioned disk image and populate it with synthetic files and a known deletion.
2. Hash the source, acquire a copy, and verify both hashes match.
3. Record acquisition details in an evidence register with full hashes.
4. Establish and document custody, including the decision to make the original read-only.
5. Confirm the image structure (`mmls`, `fsstat`) before any analysis.
6. State why a hash match proves fidelity but not correctness of interpretation.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Ubuntu | 24.04 | `lab-ubuntu` |
| `parted`, `e2fsprogs`, `util-linux` | current | Image creation, loop devices |
| Sleuth Kit | 4.12 | `mmls`, `fsstat`, `fls` |
| `dcfldd` | 1.9.x | Acquisition with inline hashing |
| `sha256sum` | coreutils | Independent verification |

!!! warning "Authorized scope — read before you begin"
    **Everything here is synthetic.** The image is a file you create, containing files you write. There is no real
    user data, no malware, and no victim system.

    **Never run these procedures against a device you do not own.** `dcfldd if=/dev/sdX` on the wrong device
    overwrites it. Check every device path twice, and prefer file-backed images while learning.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

Not an attacker this time, but the failure mode that matters in forensics: **contamination**. Opening the original,
mounting read-write, or analysing a copy without verifying it produces conclusions that cannot be defended. The
controls are procedural: read-only source, verified copy, continuous record.

## Procedure

### 1. Create the synthetic disk

```bash
sudo apt update && sudo apt install -y parted e2fsprogs sleuthkit dcfldd
mkdir -p ~/lab406/{source,evidence,work}
cd ~/lab406/source

truncate -s 512M disk.img
parted -s disk.img mklabel msdos mkpart primary ext4 1MiB 100%
sudo losetup -fP --show disk.img
```

**Expected:** `losetup` prints a device such as `/dev/loop0`, and `lsblk` shows `/dev/loop0p1`.

```bash
sudo mkfs.ext4 -q /dev/loop0p1
sudo mkdir -p /mnt/lab406
sudo mount /dev/loop0p1 /mnt/lab406
```

**Expected:** an empty ext4 filesystem mounted at `/mnt/lab406`.

### 2. Populate it with synthetic artefacts

```bash
sudo mkdir -p /mnt/lab406/{home/analyst,srv/app,tmp,var/log}

sudo tee /mnt/lab406/home/analyst/notes.txt >/dev/null <<'EOF'
Lab 406 synthetic evidence. No real data.
Change window: 2026-10-28 22:00 UTC.
EOF

sudo tee /mnt/lab406/srv/app/index.php >/dev/null <<'EOF'
<?php
// LAB406-WEBSHELL-MARKER - harmless text used to test YARA rules
// This file does not execute anything. It is a marker for classification practice.
echo "lab406 synthetic page";
EOF

sudo tee /mnt/lab406/tmp/drop.sh >/dev/null <<'EOF'
#!/bin/sh
# LAB406-DROPPER-MARKER - synthetic, does nothing
echo "lab406 synthetic dropper marker"
EOF

sudo tee /mnt/lab406/var/log/lab406.log >/dev/null <<'EOF'
2026-10-28T22:01:03Z service started
2026-10-28T22:03:44Z synthetic event A
2026-10-28T22:07:12Z synthetic event B
EOF

# Give the files distinct, documented timestamps
sudo touch -d '2026-10-28 22:00:00 UTC' /mnt/lab406/home/analyst/notes.txt
sudo touch -d '2026-10-28 22:05:00 UTC' /mnt/lab406/srv/app/index.php
sudo touch -d '2026-10-28 22:06:30 UTC' /mnt/lab406/tmp/drop.sh
sudo touch -d '2026-10-28 22:07:12 UTC' /mnt/lab406/var/log/lab406.log

# Deliberate deletion, so later labs have something to recover
sudo rm /mnt/lab406/tmp/drop.sh
sudo ls -la /mnt/lab406/tmp
```

**Expected:** `/tmp` is empty — the file is deleted but its data and directory entry may remain in the image. That is
the point.

```bash
sudo umount /mnt/lab406
sudo losetup -d /dev/loop0
ls -l ~/lab406/source/disk.img
```

**Expected:** a 512 MiB image file. Applying `losetup -d` to the device printed earlier; check with `losetup -a` that
it is detached.

### 3. Hash the source before acquisition

```bash
cd ~/lab406/source
sha256sum disk.img | tee disk.img.sha256
```

**Expected:** a 64-hex-character hash. Record it in the register exactly; do not truncate.

**Establish the convention now:** this file is the **original**. It will be made read-only and never mounted again.

```bash
chmod 444 disk.img
ls -l disk.img
```

### 4. Acquire a verified copy

```bash
cd ~/lab406/evidence
sudo dcfldd if=../source/disk.img of=EX-406-01.img bs=4M hash=sha256 hashlog=EX-406-01.dcfldd.log
sudo chown "$USER":"$USER" EX-406-01.img EX-406-01.dcfldd.log
sha256sum EX-406-01.img | tee EX-406-01.sha256
cat EX-406-01.dcfldd.log
```

**Expected:** three values agree — the source hash, `dcfldd`'s computed hash, and the copy's hash. If any differ, delete
the copy and repeat; do not analyse it.

```bash
diff <(cut -d' ' -f1 disk.img.sha256) <(cut -d' ' -f1 EX-406-01.sha256) && echo "HASH MATCH"
```

**Expected:** `HASH MATCH`.

**On write blockers:** in production you would acquire through a hardware write blocker, or a software equivalent such
as `blockdev --setro` on the source device. For a file-backed image, the equivalent is the read-only permission and
the discipline of never mounting the original. State which method you used; "we didn't write to it" is not a method.

### 5. Confirm the image structure

```bash
cd ~/lab406/evidence
mmls EX-406-01.img | tee EX-406-01.mmls.txt
fsstat -o 2048 EX-406-01.img | tee EX-406-01.fsstat.txt
fls -o 2048 EX-406-01.img | head -20
```

**Expected:** `mmls` shows one Linux partition starting at sector **2048**; `fsstat` reports ext4 with the volume
details; `fls` lists the root directory.

**Record the offset.** Every later command needs `-o 2048` for this image. Analysing without it produces "cannot
determine file system type" or an empty listing, and the usual response — trying random flags — is how people conclude
that a disk is encrypted.

### 6. Complete the evidence register

`~/lab406/evidence/register.md`:

| Field | Your entry |
| --- | --- |
| Exhibit ID | `EX-406-01` |
| Description | Synthetic ext4 disk image, 512 MiB, one partition at sector 2048 |
| Source | File `~/lab406/source/disk.img`, created 2026-10-29 by the student |
| Nature of evidence | **Synthetic.** Contains no real user data; created for training |
| Acquisition method | `dcfldd 1.9.x`, `bs=4M`, SHA-256 inline hash; source made read-only before acquisition |
| Hash (SHA-256) | full 64-character value from `disk.img.sha256` |
| Copy hash | full value from `EX-406-01.sha256`, with the `HASH MATCH` verification |
| Storage | `~/lab406/evidence/EX-406-01.img`, read-only after acquisition |
| Custodian | your name and role |
| Transfers | time (UTC), from, to, purpose, signature |
| Analysis performed | none yet; `mmls`, `fsstat`, `fls` only |
| Retention / destruction | retained for the module; deleted at teardown with the hash record kept |

Then `custody.md`:

```text
2026-10-29T09:14Z  Created image at ~/lab406/source/disk.img (synthetic). Operator: <name>
2026-10-29T09:20Z  Hashed source; set read-only (chmod 444). Source sealed.
2026-10-29T09:22Z  Acquired copy EX-406-01.img with dcfldd; hash verified match.
2026-10-29T09:30Z  Ran mmls/fsstat/fls against the copy only.
```

**Every line needs a timezone.** Use UTC throughout; convert at the end if a report requires local time, and say so.

### 7. Prove the original is untouched

```bash
cd ~/lab406/source
sha256sum -c disk.img.sha256
stat -c '%a %n' disk.img
```

**Expected:** `disk.img: OK` and mode `444`. If the hash check fails, you analysed the wrong file — stop and find out
which.

## Evidence to collect

- `source/disk.img.sha256` and `evidence/EX-406-01.sha256`.
- `evidence/EX-406-01.dcfldd.log`.
- `evidence/EX-406-01.mmls.txt`, `EX-406-01.fsstat.txt`.
- `evidence/register.md` and `custody.md`.
- `evidence/hash-verification.txt` — the `diff` and `sha256sum -c` outputs.

## Verification

- [ ] Image is partitioned, with the offset recorded (2048).
- [ ] Synthetic artefacts include one deliberate deletion.
- [ ] Source hash recorded in full before acquisition.
- [ ] Copy hash matches, verified by an independent command as well as `dcfldd`.
- [ ] Source set read-only and re-verified after analysis.
- [ ] Register states that the evidence is synthetic and names the acquisition method.
- [ ] Custody record has times, timezone, actor and purpose for each step.
- [ ] Analysis commands in the record reference only the copy.

## Teardown and reset

```bash
cd ~/lab406
sudo chmod 644 source/disk.img
rm -f evidence/EX-406-01.img source/disk.img
```

Keep the hash files and the register. If you continue to LAB-406-02, **do not** delete the image — it is the input.

## Reflection

1. You hashed the source, then the copy, then the source again. What does each check rule out?
2. The register says the evidence is synthetic. Why does that matter if the analysis is the same either way?
3. A colleague mounts the original read-write "just to check a filename". What has changed, and what must be recorded?
4. `fls` on the image without `-o 2048` returns nothing useful. Explain what the tool was actually reading.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Creation | Image exists, no structure | Partitioned, populated, deletion present | Structure and deletion documented as intentional |
| Acquisition | Copy made | Hash recorded | Hashes cross-verified, method and write protection stated |
| Register | Partial fields | Complete fields | Full hashes, synthetic nature stated, retention defined |
| Custody | Times only | Times, actors, purpose | UTC throughout, sealed original, verification after analysis |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `losetup` shows no partition device | `-P` not used, or partition table not re-read | `sudo losetup -d`, reattach with `-P`, check `lsblk` |
| `mmls` reports no partitions | Image is a bare filesystem, not a partitioned disk | Recreate with `parted` as shown |
| Hash mismatch | Copy interrupted, or wrong source file | Delete the copy, re-acquire, compare paths carefully |
| `fsstat` says "cannot determine file system" | Wrong offset | Use the start sector from `mmls` |
| `chmod 444` then `dcfldd` fails | Running as a user without read permission is fine; the failure is usually the path | Use an absolute path; check `ls -l` |
| `dcfldd` not found | Package missing | `sudo apt install dcfldd` |
| Image larger than expected | Sparse file expanded by copying | Expected; `dcfldd` writes the full size |

## References

1. NIST SP 800-86 — Guide to Integrating Forensic Techniques into Incident Response. Accessed 2026-10-29.
2. RFC 3227 — Guidelines for Evidence Collection and Archiving. Accessed 2026-10-29.
3. The Sleuth Kit — `mmls`, `fsstat`, `fls` manual pages. <https://www.sleuthkit.org/sleuthkit/man/> Accessed
   2026-10-29.
4. `dcfldd` — hashing and acquisition options. Accessed 2026-10-29.
5. `losetup(8)`, `parted(8)`, `mkfs.ext4(8)`. Accessed 2026-10-29.

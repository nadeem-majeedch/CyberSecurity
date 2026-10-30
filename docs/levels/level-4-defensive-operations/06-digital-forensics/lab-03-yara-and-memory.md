---
title: "LAB-406-03 · YARA Classification and Memory Artefacts"
description: "Write YARA rules with a negative test, scan extracted and raw evidence, then plan a memory acquisition and map Volatility plugins to questions."
module_code: CYB-406
level: 4
kind: lab
prerequisites: [CYB-406]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-406-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [yara, detection, memory-forensics, volatility, false-positives, acquisition]
---

# LAB-406-03 · YARA Classification and Memory Artefacts

## Scenario and background

You have a verified image and a set of extracted files. Two questions remain: which artefacts resemble known patterns,
and what would memory have told you that the disk cannot?

The first is a YARA exercise with a deliberate false-positive trap. The second is an acquisition and mapping exercise:
you will learn what each Volatility plugin answers, and state plainly what memory analysis cannot recover.

## Learning objectives

1. Write YARA rules with metadata, string modifiers and a precise condition.
2. Test each rule against a positive and a negative artefact, and explain the negative.
3. Scan extracted files and a raw image, and interpret the difference in results.
4. Describe memory acquisition on Linux and Windows, including integrity and consent requirements.
5. Map Volatility 3 plugins to investigative questions.
6. State the limits of memory evidence: smearing, symbol mismatch, encryption.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| YARA | 4.6.0 | `yara --version` |
| Python | 3.10+ | Volatility 3 runs as a Python package |
| Volatility 3 | current | `pip install volatility3` |
| `avml` or `winpmem` | current | Memory acquisition, own lab VM only |
| `EX-406-01.img` | — | From LAB-406-01 |

!!! warning "Authorized scope — read before you begin"
    **YARA rules here match harmless marker strings.** The files that match are text; nothing executes them.

    **Memory acquisition is invasive.** It loads a driver or kernel module, changes system state, and captures
    credentials and personal data. Acquire only from **your own lab VM**, with a snapshot taken first, and delete the
    image at teardown. Never capture memory from a system you do not own or administer.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The disk shows a marker file in a web root and a deleted script. YARA answers "does anything here match a known
pattern?" — which is classification, not attribution. Memory would answer "what was running, and what did it
connect to?" — which is behaviour. Neither answers "who did it".

## Procedure

The lab has two independent parts. Part A classifies evidence with YARA and is fully self-contained. Part B covers
memory acquisition and plugin mapping; if you cannot acquire a memory image, complete the mapping table from your
installed plugin list and record the gap rather than inventing results.

## Part A — YARA with a negative test

### 1. Install and confirm

```bash
sudo apt install -y yara
yara --version
```

**Expected:** `4.6.0`.

### 2. Write the rules

`rules/lab406.yar`:

```yara
rule LAB406_Synthetic_Marker
{
    meta:
        author = "CYB-406 lab"
        description = "Matches the harmless marker strings placed in the synthetic image"
        date = "2026-10-29"
        reference = "LAB-406-01"
    strings:
        $web = "LAB406-WEBSHELL-MARKER" ascii wide
        $drop = "LAB406-DROPPER-MARKER" ascii wide
    condition:
        any of them
}

rule LAB406_PHP_Eval_Base64
{
    meta:
        author = "CYB-406 lab"
        description = "PHP that decodes base64 and evaluates it - a common webshell shape"
        date = "2026-10-29"
        falsepositives = "Legitimate encoders, licence checks, template engines"
    strings:
        $eval = "eval" ascii nocase
        $b64  = "base64_decode" ascii nocase
    condition:
        all of them and filesize < 1MB
}
```

**Why `all of them` and not `any of them`:** `base64_decode` alone appears in legitimate code constantly. Requiring
both strings, in a small file, reduces noise at the cost of missing variants — a trade-off you must state.

### 3. Build the test set

```bash
mkdir -p ~/lab406/work/rules ~/lab406/work/tests
cp ~/lab406/evidence/extracted-index.php ~/lab406/work/tests/
```

Create a positive artefact and a negative one — both plain text:

```bash
cat > ~/lab406/work/tests/shell-synthetic.php <<'EOF'
<?php
// LAB406 synthetic sample: this is a STRING, not executable code.
// eval(base64_decode("ZWNobyAibGFiNDA2Ijs="));
echo "lab406";
EOF

cat > ~/lab406/work/tests/benign-encoder.php <<'EOF'
<?php
// Legitimate use of base64 for an inline image placeholder; no eval.
$placeholder = base64_decode("bGFiNDA2");
echo "<img alt='$placeholder'>";
EOF
```

### 4. Run positive and negative tests

```bash
cd ~/lab406/work
yara -s rules/lab406.yar tests/shell-synthetic.php
yara -s rules/lab406.yar tests/benign-encoder.php && echo "NO MATCH (expected)" || echo "MATCH (unexpected)"
```

**Expected:** the shell sample matches both rules, with `-s` listing the matching strings and offsets. The benign file
matches nothing, so the second command prints `NO MATCH (expected)`.

**If the benign file matches**, your condition is too loose — do not "fix" the file. Adjust the rule, re-run both
tests, and record the change.

### 5. Scan extracted files and the raw image

```bash
yara -r rules/lab406.yar ~/lab406/work/tests
yara -r rules/lab406.yar ~/lab406/evidence/EX-406-01.img | head
```

**Expected:** the directory scan matches the positive sample. The raw-image scan may also match, because deleted
content can persist in unallocated blocks — including the deleted `drop.sh` marker.

**Interpret carefully:** a raw-image hit gives an offset, not a path. It is a lead that requires mapping back to an
inode or carving the content out, which is exactly what LAB-406-02 did with `icat`.

### 6. Write the false-positive analysis

`yara-notes.md`:

| Rule | Positive test | Negative test | False-positive risk | Tuning option |
| --- | --- | --- | --- | --- |
| `LAB406_Synthetic_Marker` | matches marker files | no match on benign PHP | Low here; in production, marker strings are unique by design | none needed |
| `LAB406_PHP_Eval_Base64` | matches synthetic shell | no match on benign encoder | Moderate: encoders, obfuscators, template engines | add path scope, require `$_POST`/`$_GET`, raise specificity |

Then answer: if you deployed the second rule across a shared hosting estate, what would you expect the alert volume to
look like, and what would you change before doing so?

## Part B — Memory acquisition and plugin mapping

### 7. Acquire from your own lab VM

On `lab-ubuntu`, with a snapshot already taken:

```bash
sudo apt install -y linux-headers-$(uname -r) || true
# avml is distributed as a static binary from Microsoft's releases; verify the checksum of the download
sudo ./avml /evidence/mem-EX-406-02.lime
sha256sum /evidence/mem-EX-406-02.lime | tee /evidence/mem-EX-406-02.sha256
sudo chmod 400 /evidence/mem-EX-406-02.lime
```

On Windows, the equivalent is `winpmem` writing a raw image, run elevated, with the same immediate hashing.

**Record in the register:** tool and version, time (UTC), hash, size, that the acquisition loaded a driver/module and
therefore changed system state, and who authorised it. If you cannot acquire (no permissions, no snapshot capacity),
say so and complete step 8 from documentation — a documented gap is acceptable; an invented result is not.

### 8. Map plugins to questions

Install and inspect what your version provides:

```bash
python3 -m venv ~/vol-venv && source ~/vol-venv/bin/activate
pip install volatility3
vol -h | head -20
vol -f /evidence/mem-EX-406-02.lime linux.pslist 2>&1 | head -20
```

**Expected:** a plugin list, then a process table if the image and symbol tables match. A symbol error means the
kernel profile does not match the image — record it; it is not a reason to try random flags.

Complete `memory-map.md`:

| Investigative question | Plugin (Linux image) | Plugin (Windows image) | What it proves |
| --- | --- | --- | --- |
| Which processes were running? | `linux.pslist` | `windows.pslist` | Kernel's view at capture time |
| What is hidden or terminated? | run `vol -h` for available scan plugins | `windows.psscan` | Pool scan; may find unlinked processes |
| Parent-child relationships | `linux.pstree` | `windows.pstree` | Ancestry, not intent |
| Command history in memory | `linux.bash` | `windows.cmdline` | Commands and arguments |
| Network connections | `linux.sockstat` | `windows.netscan` | Connections that may never hit disk |
| Suspicious executable memory | consult `vol -h` for your version | `windows.malfind` | Executable pages not backed by a file |

**Do not invent plugin names.** Run `vol -h` and use what your installed version lists; the available set changes
between releases, and a hallucinated plugin name in a report is exactly the kind of error this module is trying to
prevent.

### 9. State the limits

`memory-limits.md`, five points:

1. **Smearing** — freed pages are reused, so absence of a process is weak evidence.
2. **Symbol mismatch** — wrong kernel version produces errors or misleading output.
3. **Encryption** — some memory and all swapped-encrypted content may be unreadable.
4. **State change** — acquisition loads code into the kernel; document it.
5. **Sensitivity** — the image may contain credentials and personal data; store it read-only, access-controlled, and
   delete it at teardown.

## Evidence to collect

- `rules/lab406.yar`.
- `tests/shell-synthetic.php`, `tests/benign-encoder.php`.
- `yara-positive.txt`, `yara-negative.txt`, `yara-raw-image.txt`.
- `yara-notes.md`.
- `memory-map.md`, `memory-limits.md`.
- Memory register entry (or a documented reason acquisition was not performed).

## Verification

- [ ] YARA 4.6.0 confirmed.
- [ ] Both rules have metadata and precise conditions.
- [ ] Positive test matches with `-s` showing the strings.
- [ ] Negative test does not match, and the result is recorded.
- [ ] Raw-image scan interpreted as offset evidence, not path evidence.
- [ ] False-positive table names a concrete tuning option.
- [ ] Memory acquisition documented with hash, authorisation and state change — or explicitly not performed.
- [ ] Plugin table uses names present in your `vol -h` output.
- [ ] Five limits stated in your own words.

## Teardown and reset

```bash
deactivate 2>/dev/null || true
rm -rf ~/vol-venv
sudo shred -u /evidence/mem-EX-406-02.lime 2>/dev/null || sudo rm -f /evidence/mem-EX-406-02.lime
```

Keep the hash record even after destroying the image. Delete the synthetic test files only after the report cites
them.

## Reflection

1. Your second rule requires two strings. Describe a real webshell that would evade it, and the rule change that would
   catch that variant without flooding you.
2. The raw-image scan can match deleted content. Why is that both useful and dangerous in a report?
3. Memory would show a process that never touched disk in a useful way. Name one such artefact and the plugin.
4. If the symbol table does not match, what can you still legitimately do with the image, and what can you not?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Rules | One broad rule | Two rules with conditions | Metadata, modifiers, and documented trade-off |
| Testing | Positive only | Positive and negative | Negative explained and rule adjusted if needed |
| Raw scan | Not attempted | Attempted | Offset-versus-path distinction explained |
| Memory | Not addressed | Acquisition described | Acquisition documented with integrity and state change, plugins mapped honestly |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `yara: invalid rule` | Syntax error or bad modifier | Check quotes and `condition`; compile with `yara rules.yar` alone |
| Negative file matches | Condition too broad | Tighten (require both strings, add path or size) and re-test |
| Raw scan is very slow | Rule too generic over 512 MiB | Scope with `-r` on extracted files first; accept cost knowingly |
| `vol` command not found | venv not active, or entry point missing | `python3 -m volatility3 -h` inside the venv |
| Symbol error | Kernel/image mismatch | Record it; do not guess flags |
| `avml` fails | Missing privileges or unsupported kernel | Run as root; check the release notes; record the failure |

## References

1. YARA 4.6.0 — rule syntax, modifiers, `-s`, `-r`. <https://yara.readthedocs.io/> Accessed 2026-10-29.
2. Volatility 3 — installation and plugin reference. <https://volatility3.readthedocs.io/> Accessed 2026-10-29.
3. Microsoft — AVML (Acquire Volatile Memory for Linux). Accessed 2026-10-29.
4. Velociraptor/winpmem — Windows memory acquisition. Accessed 2026-10-29.
5. NIST SP 800-86 — memory as volatile evidence. Accessed 2026-10-29.
6. MITRE ATT&CK — T1055 Process Injection; T1620 Reflective Code Loading. Accessed 2026-10-29.

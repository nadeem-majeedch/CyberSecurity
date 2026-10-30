---
title: "LAB-202-01 · Bash Security-Check Script"
description: "Write a strict-mode Bash script that checks local security settings and returns a meaningful exit code."
module_code: CYB-202
level: 2
kind: lab
prerequisites: [CYB-202]
estimated_minutes: 180
difficulty: intermediate
safety: local-only
lab_ids: [LAB-202-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [bash, hardening, automation]
---

# LAB-202-01 · Bash Security-Check Script

## Scenario and background

An internal review asks for a repeatable way to confirm a baseline on each Linux host in a lab range. Manual
checking produces different results every time and cannot be attached to a report. You will write a script that
checks a defined set of local settings, prints pass/fail per item, and returns an exit code a pipeline can act
on.

The script is deliberately **read-only**: it inspects, it does not change anything. Changes are Level 4 work,
where they are applied deliberately and verified.

## Learning objectives

By the end of this lab you can:

1. Write a Bash script with strict mode and predictable word splitting.
2. Implement a reusable check function with uniform output.
3. Return an aggregate exit code that reflects the worst result.
4. Guard the script so it only inspects the intended host.
5. Document the checks so a reviewer knows what was tested and what was not.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Bash | 5.x | Present on Kali and Ubuntu |
| coreutils, grep, awk | standard | Used for inspection |
| `shellcheck` | 0.9+ | Optional: `sudo apt install -y shellcheck` |

## Setup

```bash
mkdir -p ~/lab/level-2/lab-202/scripts ~/lab/level-2/lab-202/evidence
cd ~/lab/level-2/lab-202/scripts
```

Run this lab on `lab-ubuntu` (the target/reference host), not on your physical machine.

## Target addresses and lab topology

```
lab-ubuntu 192.0.2.20/24  ← this lab runs locally on this host (no network activity)
```

No scanning, no remote connections. The script reads local configuration only.

## Numbered commands and actions

### 1. Create the script skeleton

```bash
cat > security-check.sh <<'SH'
#!/usr/bin/env bash
# Read-only local security baseline checks. Safe to run repeatedly.
set -euo pipefail
IFS=$'\n\t'

if [[ "$(id -u)" -ne 0 ]]; then
  echo "note: some checks need root; re-run with sudo for full coverage" >&2
fi

fail=0
note() { printf '%s\n' "$*"; }
check() {
  local name="$1" expect="$2" actual="$3"
  if [[ "$actual" == "$expect" ]]; then
    printf '[PASS] %-34s %s\n' "$name" "$actual"
  else
    printf '[FAIL] %-34s got=%s want=%s\n' "$name" "$actual" "$expect"
    fail=1
  fi
}
SH
chmod +x security-check.sh
```

### 2. Add the checks

Append each check. Read every command first, and note what it inspects.

```bash
cat >> security-check.sh <<'SH'

# --- SSH configuration -------------------------------------------------------
sshd_cfg=/etc/ssh/sshd_config
if [[ -r "$sshd_cfg" ]]; then
  pw=$(grep -Ei '^\s*PasswordAuthentication' "$sshd_cfg" | awk '{print tolower($2)}' | tail -1)
  check "sshd: password authentication" "no" "${pw:-unset}"
  root_login=$(grep -Ei '^\s*PermitRootLogin' "$sshd_cfg" | awk '{print tolower($2)}' | tail -1)
  check "sshd: permit root login"       "no" "${root_login:-unset}"
else
  note "[SKIP] sshd config not readable (run as root)"
fi

# --- Accounts ----------------------------------------------------------------
uid0=$(awk -F: '$3==0 {print $1}' /etc/passwd | tr '\n' ' ')
check "only root has uid 0" "root " "$uid0"

empty_pw=$(sudo -n awk -F: '($2=="" ) {print $1}' /etc/shadow 2>/dev/null | tr '\n' ' ' || true)
check "no empty password hashes" "" "$empty_pw"

# --- Files and permissions ---------------------------------------------------
check "world-writable files in /etc" "" "$(find /etc -xdev -type f -perm -0002 2>/dev/null | head -5 | tr '\n' ' ')"
check "/etc/passwd mode" "644" "$(stat -c '%a' /etc/passwd)"
check "/etc/shadow mode" "640" "$(stat -c '%a' /etc/shadow 2>/dev/null || echo unreadable)"

# --- Kernel and services -----------------------------------------------------
check "IP forwarding disabled" "0" "$(cat /proc/sys/net/ipv4/ip_forward)"
check "no telnet listener" "" "$(ss -tlnH 2>/dev/null | awk '$4 ~ /:23$/ {print $4}' | tr '\n' ' ')"

# --- Result ------------------------------------------------------------------
if [[ "$fail" -eq 0 ]]; then
  note "RESULT: all checks passed"
else
  note "RESULT: one or more checks failed"
fi
exit "$fail"
SH
```

**Why `[FAIL]` instead of trying to fix things:** an inspection script that "corrects" settings hides drift
instead of revealing it. Fixing belongs to a deliberate change with its own verification.

### 3. Verify quoting and structure

```bash
bash -n security-check.sh          # syntax only
shellcheck security-check.sh       # if installed
```

**Expected:** no output from `bash -n`. `shellcheck` may report `SC2016` or similar — read each one and either
fix it or note why it is acceptable.

### 4. Run it and capture evidence

```bash
sudo ./security-check.sh | tee ~/lab/level-2/lab-202/evidence/security-check-before.txt
echo "exit: $?" | tee -a ~/lab/level-2/lab-202/evidence/security-check-before.txt
```

**Expected:** one line per check, then a `RESULT:` line. On a default Ubuntu Server, expect failures like
`sshd: password authentication got=yes want=no` — that is a genuine finding, and it is the point of the lab.

### 5. Make one safe change and re-run

Do not change SSH yet (that is LAB-205-01). Instead, test the script's sensitivity:

```bash
sudo cp /etc/passwd /tmp/passwd.bak
# Simulate a finding: create a world-writable file in /etc (safe, removed next step)
sudo touch /etc/lab202-test && sudo chmod 666 /etc/lab202-test
sudo ./security-check.sh | grep -E "world-writable|RESULT" | tee ~/lab/level-2/lab-202/evidence/security-check-detected.txt
sudo rm -f /etc/lab202-test
```

**Expected:** the `world-writable files in /etc` check now shows the test file and `RESULT: one or more checks
failed`. This proves the script detects change rather than always printing the same thing.

### 6. Document coverage honestly

Create `~/lab/level-2/lab-202/scripts/README.md` with:

| Check | What it inspects | Why it matters | Limitations |
| --- | --- | --- | --- |
| sshd password authentication | `sshd_config` effective text | Password auth enables guessing | Does not read `sshd -T` merged config |
| uid 0 accounts | `/etc/passwd` | Extra root accounts are a backdoor | Does not cover `sudo` rules |
| empty password hashes | `/etc/shadow` | Login without a password | Needs root to read |
| world-writable in `/etc` | file modes | Tampering risk | `-xdev` skips other filesystems |
| IP forwarding | kernel parameter | Router-like behaviour on a host | Does not check `sysctl.d` overrides |
| telnet listener | listening sockets | Cleartext remote access | Only checks port 23 |

The limitations column is the most valuable part of the document. A check that claims more than it verifies is
worse than no check.

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `bash -n` | Syntax check without executing | Catches typos before running as root |
| `find -xdev` | Stay on one filesystem | Avoids scanning mounted shares |
| `find -perm -0002` | Any world-writable mode | The classic exposure test |
| `ss -tlnH` | TCP listeners, no header | Stable parsing |
| `stat -c '%a'` | Permission bits only | Machine-readable output |
| `sudo -n` | Non-interactive | Fails rather than hanging in an automated run |

## Expected observations

- `bash -n` reports no errors; the script runs end to end.
- Every check prints a `[PASS]` or `[FAIL]` line with actual and expected values.
- At least one genuine failure appears on a default Ubuntu install.
- Adding a world-writable file in `/etc` flips a check to `[FAIL]`; removing it flips it back.
- The exit code is non-zero when any check fails.

## Verification criteria

- [ ] Script contains `set -euo pipefail` and `IFS`.
- [ ] `bash -n` and (if available) `shellcheck` reviewed.
- [ ] Output saved for both the passing and the detected-change runs.
- [ ] Exit code recorded for both runs.
- [ ] Coverage table documents every check and at least one limitation per check.
- [ ] No system setting was modified (only the temporary file, which was removed).

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Script exits immediately with no output | `set -e` plus a failing command in a subshell | Guard with `|| true` where failure is expected |
| `[SKIP]` for sshd | Config not readable or absent | Run with `sudo`; on the target host only |
| Everything passes unexpectedly | Running as non-root, so checks silently skip | Re-run with `sudo` and check the output for `[SKIP]` |
| `awk: cannot open /etc/shadow` | Not root | Expected; the check prints empty and fails |
| `find` takes a long time | Large `/etc` with mounts | Keep `-xdev`, or narrow the path |
| `shellcheck` reports `SC2086` | Unquoted variable | Quote it — the warning is correct |

## Cleanup and restoration

```bash
sudo rm -f /etc/lab202-test /tmp/passwd.bak
sudo ./security-check.sh | grep "world-writable"
```

The check should return to `[PASS]` (empty). Keep the script and evidence; they are reused in LAB-206-01 and
LAB-206-03. If anything else was modified, revert to `ubuntu-baseline`.

## Questions and extension challenges

1. Why does an inspection script deliberately avoid fixing what it finds?
2. Which single check would you add for a Windows host, and how would it differ?
3. **Extension:** add a `--json` output mode and explain why structured output matters for a report pipeline.
4. **Extension:** add a `--host` argument with a scope guard that refuses any value outside `192.0.2.0/24`, even
   though the script currently does not connect to remote hosts. Explain why the guard belongs now rather than
   later.

## Related

- [Scripting and Versioning for Repeatable Work](01-scripting-and-git.md)
- [LAB-202-02 · Python Parser for Synthetic Logs](lab-02-python-log-parser.md)
- [System Inspection, Hardening Assessment and Reporting](../06-host-inspection-and-hardening/index.md)

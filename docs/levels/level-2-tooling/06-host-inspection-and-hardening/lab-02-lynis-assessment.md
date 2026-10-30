---
title: "LAB-206-02 · Hardening Assessment with Lynis"
description: "Run a baseline assessment, triage its suggestions critically, remediate a chosen subset, and prove the delta."
module_code: CYB-206
level: 2
kind: lab
prerequisites: [CYB-205]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-206-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [lynis, hardening, remediation, audit]
---

# LAB-206-02 · Hardening Assessment with Lynis

| | |
| --- | --- |
| **Level** | 2 |
| **Time** | 4 hours |
| **Prerequisites** | LAB-206-01 |
| **Lab hosts** | `lab-ubuntu` 192.0.2.20 (target), `lab-kali` (analyst) |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

Your inventory produced observations. Now you must decide which of them a hardening baseline would also flag, and
which of *those* are worth changing in this environment. A scanner's suggestion list is evidence of a possible
improvement, not a work order — and part of being an assessor is knowing the difference.

## Learning objectives

1. Install and run Lynis non-interactively, with output preserved as evidence.
2. Read the hardening index and the suggestion list without treating the score as a grade.
3. Triage suggestions into *fix*, *justify*, and *not applicable*.
4. Remediate a chosen subset and prove the change with a second run.
5. Explain a compensating control where a suggestion was declined.

## Required tools and versions

| Tool | Version | Install |
| --- | --- | --- |
| `lynis` | 3.0.9+ | `sudo apt install lynis` |
| `diffutils`, `grep` | any | present |

## Setup

```bash
mkdir -p ~/lab206/02-lynis && cd ~/lab206/02-lynis
ssh lab-ubuntu 'sudo apt update && sudo apt install -y lynis && lynis --version'
```

**Expected:** a version line such as `3.0.9`. Record it — assessments quote tool versions.

Take a snapshot named `before-lynis` before remediating anything.

## Target addresses and lab topology

```
lab-kali 192.0.2.10  --- host-only lab-only-192.0.2.0 ---  lab-ubuntu 192.0.2.20
        (analyst)                                         (target: lynis, auditd, chrony)
```

Lynis runs locally on the target. Because the lab is offline, time synchronisation checks will fail — record that
as an environment limitation rather than a finding.

## Numbered commands and actions

### Step 1 — Baseline run

```bash
ssh lab-ubuntu 'sudo lynis audit system --quick --no-colors' | tee lynis-before.txt
grep -A3 'Hardening index' lynis-before.txt
grep -c '^\s*\*' lynis-before.txt
```

**Expected:** a hardening index line (typically 60–70 on a default Ubuntu image), a suggestions section, and a
count of suggestion bullets.

Extract the machine-readable summary:

```bash
ssh lab-ubuntu 'sudo cat /var/log/lynis-report.dat' | grep -E 'hardening_index|suggestion\[\]|warning\[\]' | head -40 | tee lynis-report-before.txt
```

### Step 2 — Verify before you believe

Scanners produce false positives, and their tests assume a generic host. Verify three suggestions directly:

```bash
# Example: a suggestion about SSH
ssh lab-ubuntu 'sudo sshd -T | grep -Ei "permitrootlogin|passwordauthentication|maxauthtries"'

# Example: a suggestion about unused filesystems
ssh lab-ubuntu 'grep -E "cramfs|freevxfs|jffs2|hfs|udf" /etc/modprobe.d/* 2>/dev/null || echo "no blacklist present"'

# Example: a suggestion about core dumps
ssh lab-ubuntu 'systemctl show | grep -i coredump; cat /proc/sys/kernel/core_pattern'
```

For each, record whether Lynis's claim matches the host's actual state. If it matched (LAB-205-02 already hardened
`sshd`), say so — a suggestion that is *already fixed* is a different statement from one that is *wrong*.

### Step 3 — Triage into three buckets

Create `triage.md`:

| Lynis suggestion | Bucket | Reasoning | Action |
| --- | --- | --- | --- |
| Set `PermitRootLogin no` | Already done | Verified in LAB-205-02 | None |
| Install `auditd` | Fix | No audit trail on the host; cheap and high value | `apt install auditd` |
| Disable unused filesystem modules | Fix | Reduces kernel attack surface | `modprobe.d` blacklist |
| Enable `chrony`/`ntp` | Fix | Log correlation depends on accurate time | Install and enable |
| Set password max age | Justify | Modern guidance prefers length + breach checks over rotation | Document as accepted risk |
| Harden `/boot` permissions | Not applicable | Single-user lab VM, no multi-tenant risk | Document |

**Rules for triage:**

- **Fix** — reduces real risk in *this* environment and does not break the lab.
- **Justify** — the suggestion has merit but the cost or context argues against it; write the compensating control.
- **Not applicable** — the assumption behind the test does not hold here.

You must have at least one item in each bucket, with reasoning.

### Step 4 — Remediate the "fix" bucket

```bash
ssh lab-ubuntu 'sudo apt install -y auditd chrony'
ssh lab-ubuntu 'sudo systemctl enable --now auditd chrony'

# Disable unused filesystem modules
ssh lab-ubuntu 'sudo tee /etc/modprobe.d/lab-hardening.conf >/dev/null <<"EOF"
install cramfs /bin/false
install freevxfs /bin/false
install jffs2 /bin/false
install hfs /bin/false
install hfsplus /bin/false
install squashfs /bin/false
install udf /bin/false
EOF'

# Verify time sync and audit state
ssh lab-ubuntu 'timedatectl | head -6; sudo auditctl -s | head -5'
```

**Expected:** `System clock synchronized: yes`; `auditctl -s` reports `enabled 1`.

!!! warning "These are lab choices, not universal advice"
    Disabling `squashfs` breaks snap packages, and disabling `udf` stops optical media from mounting. Both are fine
    on this VM and wrong on a workstation. The reasoning belongs in your report; the commands do not belong in a
    copy-paste checklist.

### Step 5 — Second run and delta

```bash
ssh lab-ubuntu 'sudo lynis audit system --quick --no-colors' | tee lynis-after.txt
diff <(grep -E '^\s+\*' lynis-before.txt) <(grep -E '^\s+\*' lynis-after.txt) | tee lynis-delta.txt
grep 'Hardening index' lynis-before.txt lynis-after.txt
```

**Expected:** a smaller suggestion set, and a hardening index that has increased — by how much depends on your
baseline and choices, so report the actual numbers rather than a target.

**If the index did not move**, that is a legitimate result: check whether your remediations were among the scored
tests, and say so. Do not fabricate improvement.

### Step 6 — Verify the host still works

```bash
ssh lab-ubuntu 'sudo sshd -T | head -3; systemctl is-active auditd chrony; uptime'
scp -q lynis-delta.txt lab-ubuntu:/home/student/ && echo "transfer ok"
```

**Expected:** SSH still works, both services active, file transfer succeeds. A hardening that breaks administration
is a finding against you.

## Evidence to collect

| File | Purpose |
| --- | --- |
| `lynis-before.txt`, `lynis-after.txt` | Full runs |
| `lynis-report-before.txt` | Machine-readable summary |
| `lynis-delta.txt` | What changed |
| `triage.md` | Fix / justify / not-applicable reasoning |
| Verification outputs | The three spot checks from Step 2 |

## Verification criteria

- [ ] Lynis version recorded.
- [ ] Baseline run preserved in full.
- [ ] Three suggestions verified against the host, not taken on trust.
- [ ] At least one item in each triage bucket, with reasoning.
- [ ] Remediations applied; services active.
- [ ] Second run compared with the first, with actual index numbers quoted.
- [ ] Host still administrable afterwards (SSH and file transfer verified).
- [ ] At least one declined suggestion has a written compensating control.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `lynis: command not found` | Not installed, or wrong PATH | `sudo apt install lynis` |
| Index unchanged | Remediations not scored, or nothing applied | Check `lynis-delta.txt`; report honestly |
| Snaps stop working | `squashfs` disabled | Remove that line from the blacklist |
| `auditd` fails to start | Conflicting audit rules | `journalctl -u auditd -n 30` |
| Lynis warns about the report file | Directory permissions | It still writes to `/var/log/lynis-report.dat`; read with `sudo` |
| Time not synchronised | `chrony` blocked by the host-only network | Expected offline; note it as a lab limitation |

## Cleanup and restoration

```bash
# Option A — keep remediations for the report evidence (recommended)
ssh lab-ubuntu 'systemctl is-active auditd chrony'

# Option B — restore baseline
ssh lab-ubuntu 'sudo rm -f /etc/modprobe.d/lab-hardening.conf; sudo systemctl disable --now auditd chrony'
# Or restore snapshot before-lynis

pgrep -a tcpdump || echo "no capture running"
```

## Questions and extension challenges

1. Why is the hardening index not a grade?
2. Which of your remediation steps would break a developer workstation, and why?
3. What is a compensating control? Give one for a declined suggestion.
4. Re-run Lynis after restoring the snapshot. How reproducible is the index?
5. Which of your fixes would a real attacker notice first?

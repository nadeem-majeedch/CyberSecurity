---
title: "Inspecting a Linux Host"
description: "A repeatable inventory of accounts, permissions, processes, services and sockets — and what each one can tell you."
module_code: CYB-206
level: 2
kind: lesson
prerequisites: [CYB-205]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [audit, linux, permissions, services, sockets]
---

# Inspecting a Linux Host

## Learning objectives

1. Inventory accounts, groups and privileged access deliberately.
2. Find risky file permissions and explain the risk in each case.
3. Enumerate processes, services and listening sockets, and correlate them.
4. Distinguish a normal but unusual configuration from a genuine finding.
5. Record an inventory that another analyst could reproduce.

## Prerequisites

[CYB-205](../05-ssh-secure-administration/index.md), and `sudo` on `lab-ubuntu`.

---

## 1. The inspection order

Work outside-in, and write as you go:

```
accounts → privilege → filesystem permissions → processes → services → sockets → scheduled jobs → logs
```

Following a fixed order matters: it makes your assessment reproducible, and it stops you from chasing the first
interesting thing you find.

## 2. Accounts and privilege

```bash
# Human vs system accounts
awk -F: '$3 >= 1000 && $3 < 65534 {print $1, $3, $6, $7}' /etc/passwd

# Who can become root
getent group sudo
getent group wheel 2>/dev/null

# Accounts with a usable password hash
sudo awk -F: '$2 !~ /^[!*]/ && $2 != "" {print $1}' /etc/shadow

# Interactive shells available to system accounts (should be /usr/sbin/nologin)
awk -F: '$3 < 1000 && $7 !~ /(nologin|false|sync|shutdown)$/ {print $1, $7}' /etc/passwd

# Recent logins and failures
last -n 10
sudo lastb -n 10 2>/dev/null
```

| Check | Why it matters |
| --- | --- |
| UID 0 accounts other than root | A second root-equivalent account is a finding |
| Empty password hash | Passwordless login |
| System account with a shell | Service accounts should not have interactive access |
| Unexpected `sudo` membership | Privilege creep over time |
| Stale accounts | Offboarding gap |

```bash
awk -F: '$3 == 0 {print $1}' /etc/passwd      # any UID 0 account
sudo passwd -S student                        # password status: L, P or NP
```

## 3. Passwords and ageing

```bash
sudo grep -E '^(PASS_MAX_DAYS|PASS_MIN_DAYS|PASS_MIN_LEN|PASS_WARN_AGE|ENCRYPT_METHOD)' /etc/login.defs
sudo chage -l student
```

Modern guidance favours length over forced rotation, so treat `PASS_MAX_DAYS` findings carefully: an expiring
password policy may be a deliberate choice, not a defect. Note the reasoning rather than the raw value.

## 4. Filesystem permissions

```bash
# World-writable files outside /tmp and /proc (exclude pseudo filesystems)
sudo find / -xdev \( -path /proc -o -path /sys -o -path /tmp -o -path /run \) -prune -o \
  -type f -perm -0002 -print 2>/dev/null | head -20

# SUID/SGID binaries outside package-managed locations
sudo find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -print 2>/dev/null | sort

# Directories that are group/world writable (a path to privilege)
sudo find / -xdev -type d -perm -0002 ! -path "/tmp/*" ! -path "/proc/*" ! -path "/sys/*" -print 2>/dev/null | head
```

| Result | Interpretation |
| --- | --- |
| SUID in `/usr/bin/passwd`, `sudo`, `mount` | Normal (package-managed) |
| SUID in `/home/*` or `/tmp` | Strong finding |
| World-writable script in a root cron path | Privilege escalation |
| `.ssh` readable by others | Key disclosure |

Check whether a SUID binary belongs to a package:

```bash
dpkg -S /usr/bin/passwd 2>/dev/null || echo "not owned by a package — investigate"
```

`not owned by a package` is the sentence that turns a list into a finding.

## 5. Processes

```bash
ps -eo user,pid,ppid,stat,etime,cmd --sort=-%mem | head -20
ps -eo user,pid,cmd | awk '$1 == "root" && /home|tmp|var\/tmp/ {print}'   # root processes in odd places
pstree -p | head -30
```

Look for:

- Processes whose binary lives in a writable directory.
- Processes running as root that do not need to.
- Deleted binaries still held open: `sudo ls -l /proc/*/exe 2>/dev/null | grep deleted`.
- Unexpected shells parented by a web server (`nginx → sh` is a classic).

## 6. Services

```bash
systemctl list-units --type=service --state=running --no-pager
systemctl list-unit-files --state=enabled --no-pager | head -30
systemctl status ssh --no-pager | head -10
```

The interesting comparison is **enabled** vs **running** vs **installed**. A disabled service that is running was
started by something else; note that and find out what.

## 7. Sockets

```bash
sudo ss -tulpn
sudo ss -tulpn | grep -v '127.0.0.1\|::1'    # anything not bound to loopback
```

| Binding | Exposure |
| --- | --- |
| `127.0.0.1:5432` | Local only — good |
| `0.0.0.0:5432` | Every interface |
| `[::]:22` | IPv6 wildcard |

Correlate each socket with its process (`-p`) and its purpose. A database listening on `0.0.0.0` in a lab is a
finding even if nothing exploits it — the point of the assessment is exposure, not proof of compromise.

## 8. Scheduled work

```bash
crontab -l; sudo crontab -l
ls -l /etc/cron.* /etc/cron.d 2>/dev/null
systemctl list-timers --all --no-pager | head
sudo find /etc/cron* -type f -writable 2>/dev/null
```

A writable cron file is a persistence mechanism, whether or not anyone has used it.

## 9. From observation to finding

An observation becomes a finding when it has four parts:

| Part | Example |
| --- | --- |
| Observation | `postgres` listens on `0.0.0.0:5432` |
| Why it matters | Database reachable from any lab host on the segment |
| Evidence | `ss -tulpn` output, timestamp, host |
| Recommendation | Bind to `127.0.0.1`; if remote access is required, restrict with `pg_hba.conf` and firewall rules |

Anything less is a note, not a finding. Write every observation in that shape and prioritisation becomes easy.

---

## Practical exercises

### Exercise 1 — UID 0 audit (10 minutes)

List every UID 0 account and every account in `sudo`. Explain the difference between the two paths to root.

### Exercise 2 — SUID triage (15 minutes)

Produce the SUID list, then classify each entry as package-managed or not. Record how you decided.

### Exercise 3 — Socket map (15 minutes)

Produce `ss -tulpn`, map each listening port to its process and purpose, and flag anything bound to a wildcard
address that does not need to be.

### Exercise 4 — Deleted binary check (10 minutes)

Find processes whose executable has been deleted. Explain how that happens legitimately (package upgrade) and how
it happens maliciously.

## Expected observations

- Package-managed SUID binaries dominate the list; anything else stands out immediately.
- Most services bind to loopback; the exceptions are the interesting ones.
- `dpkg -S` resolves nearly every legitimate binary, which is what makes the unresolved ones meaningful.
- Cron directories are usually root-owned and not writable — a writable one is rare and worth explaining.

## Common mistakes and troubleshooting

| Mistake | Consequence | Fix |
| --- | --- | --- |
| Auditing as a normal user | Missing sockets, shadow, some processes | `sudo` for the inspection commands |
| Trusting `ps` alone | Misses sockets and services | Correlate with `ss` and `systemctl` |
| Reporting every SUID binary | Noise hides real findings | Classify with `dpkg -S` first |
| `find /` without `-xdev` | Walks network mounts, takes forever | `-xdev`, exclude pseudo filesystems |
| Writing observations without evidence | Unactionable report | Observation → why → evidence → recommendation |
| Changing things during inspection | Destroys the baseline | Inspect read-only; remediate after |

## Review questions

1. Why must the inspection order be fixed?
2. What makes a SUID binary suspicious rather than normal?
3. What is the difference between an enabled and a running service, and why does it matter?
4. Why is a database on `0.0.0.0` a finding even without exploitation?
5. What are the four parts of a well-formed finding?
6. Why inspect before remediating?

## Knowledge check

1. Which command lists listening TCP and UDP sockets with processes?
2. Which command identifies the package that owns a file?
3. How do you list accounts with a usable password hash?
4. What does `-xdev` do in `find`?
5. What does a deleted executable in `/proc/*/exe` suggest?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments.)*

## Summary

- Inspect in a fixed order and write as you go.
- Classify before you report: package ownership separates signal from noise.
- Correlate processes, services and sockets — each alone is incomplete.
- Writable cron files and unowned SUID binaries are the highest-value findings.
- A finding has observation, significance, evidence and recommendation.

## Next lesson

[LAB-206-01 · Host Inspection Inventory](lab-01-host-inventory.md) — apply this to `lab-ubuntu` and produce the
inventory the assessment depends on.

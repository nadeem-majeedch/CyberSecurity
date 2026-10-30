---
title: "LAB-206-01 · Host Inspection Inventory"
description: "Produce a reproducible inventory of accounts, permissions, processes, services and sockets on a lab host."
module_code: CYB-206
level: 2
kind: lab
prerequisites: [CYB-205]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-206-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [audit, inventory, linux, permissions]
---

# LAB-206-01 · Host Inspection Inventory

| | |
| --- | --- |
| **Level** | 2 |
| **Time** | 4 hours |
| **Prerequisites** | [CYB-205](../05-ssh-secure-administration/index.md) |
| **Lab hosts** | `lab-ubuntu` 192.0.2.20 (target), `lab-kali` (analyst) |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

You have inherited a lab server with no documentation. Before touching anything, you must produce an inventory
that answers: who can get in, with what privilege, what is running, and what is exposed. Everything you change
later is measured against this baseline, so it must be captured read-only and reproducibly.

## Learning objectives

1. Collect a complete account and privilege inventory.
2. Identify permission problems and separate normal from suspicious.
3. Correlate processes, services and listening sockets into one picture.
4. Record evidence with commands, timestamps and hostnames attached.
5. Write observations in the four-part finding shape.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| `ss`, `ps`, `find`, `dpkg` | distro default | present on Ubuntu |
| `systemctl` | systemd 249+ | present |
| `lynis` | 3.x | not required for this lab |

## Setup

```bash
mkdir -p ~/lab206/01-inventory && cd ~/lab206/01-inventory
ssh lab-ubuntu 'hostnamectl; uname -a; cat /etc/os-release | head -3' | tee 00-platform.txt
```

**Expected:** hostname, kernel, and Ubuntu version recorded. Every file you create from here carries the same
timestamp prefix, so the report can state *when* the inventory was taken.

```bash
date -u +"inventory_started=%Y-%m-%dT%H:%M:%SZ" | tee -a 00-platform.txt
```

## Target addresses and lab topology

```
lab-kali 192.0.2.10  --- host-only lab-only-192.0.2.0 ---  lab-ubuntu 192.0.2.20
        (analyst, read-only)                              (target under inventory)
```

The inventory is taken over SSH but describes the target's local state. Nothing is scanned from the network except
the socket list that the target itself reports.

## Numbered commands and actions

### Step 1 — Accounts and privilege

```bash
{
  echo "=== UID 0 accounts ==="; awk -F: '$3 == 0 {print $1}' /etc/passwd
  echo "=== Human accounts ==="; awk -F: '$3 >= 1000 && $3 < 65534 {print $1, $6, $7}' /etc/passwd
  echo "=== sudo group ==="; getent group sudo
  echo "=== System accounts with shells ==="
  awk -F: '$3 < 1000 && $7 !~ /(nologin|false)$/ {print $1, $7}' /etc/passwd
  echo "=== Accounts with usable hashes ==="; sudo awk -F: '$2 !~ /^[!*]/ && $2 != "" {print $1}' /etc/shadow
} | tee 01-accounts.txt
```

**Expected on a fresh lab VM:** one UID 0 account (`root`), one human account, a small `sudo` group, and no system
accounts with a shell. Anything else is worth explaining.

Check password status per account:

```bash
for u in $(awk -F: '$3 >= 1000 && $3 < 65534 {print $1}' /etc/passwd); do sudo passwd -S "$u"; done | tee 02-password-status.txt
```

**Expected:** lines like `student P 10/28/2026 0 99999 7 -1` (P = usable password, L = locked, NP = none).

### Step 2 — Permissions

```bash
{
  echo "=== SUID/SGID ==="
  sudo find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -print 2>/dev/null | sort
  echo "=== World-writable files (excl. pseudo fs) ==="
  sudo find / -xdev \( -path /proc -o -path /sys -o -path /tmp -o -path /run \) -prune -o \
    -type f -perm -0002 -print 2>/dev/null | head -20
  echo "=== Writable cron entries ==="
  sudo find /etc/cron* -type f -writable 2>/dev/null
} | tee 03-permissions.txt
```

Then classify every SUID binary:

```bash
sudo find / -xdev -type f -perm -4000 2>/dev/null | while read -r f; do
  pkg=$(dpkg -S "$f" 2>/dev/null | cut -d: -f1)
  printf '%-40s %s\n' "$f" "${pkg:-UNOWNED}"
done | tee 04-suid-classified.txt
```

**Expected:** most lines show a package name (`passwd`, `sudo`, `mount`, `su`). Any `UNOWNED` line is a finding
until proven otherwise.

### Step 3 — Processes and services

```bash
{
  echo "=== Root processes outside system paths ==="
  ps -eo user,pid,ppid,cmd | awk '$1=="root" && ($0 ~ /\/home|\/tmp|\/var\/tmp/)'
  echo "=== Deleted executables still running ==="
  sudo ls -l /proc/*/exe 2>/dev/null | grep deleted
  echo "=== Running services ==="
  systemctl list-units --type=service --state=running --no-pager
  echo "=== Enabled but not running ==="
  comm -23 <(systemctl list-unit-files --state=enabled --no-legend | awk '{print $1}' | sort) \
           <(systemctl list-units --type=service --state=running --no-legend | awk '{print $1}' | sort)
} | tee 05-processes-services.txt
```

**Expected:** no root processes from writable directories; possibly a deleted executable if you upgraded a package
without restarting (benign, and worth noting as such); a short running-service list; and a handful of enabled
services that are not running.

### Step 4 — Sockets

```bash
sudo ss -tulpn | tee 06-sockets.txt
echo "=== Not bound to loopback ===" | tee 07-exposure.txt
sudo ss -tulpn | grep -vE '127\.0\.0\.1|\[::1\]' | tee -a 07-exposure.txt
```

**Expected:** `sshd` on `0.0.0.0:22` or `[::]:22`, plus whatever you started in earlier labs (e.g. a Python server
on `:8000`). Each wildcard binding must be justified or listed as a finding.

Map each socket to a purpose:

| Port | Process | Purpose | Should it be exposed? |
| --- | --- | --- | --- |
| 22 | `sshd` | Remote administration | Yes, on the lab network |
| 8000 | `python3` | Leftover from a lab | No — stop it |
| 5432 | `postgres` | Database | No — bind to loopback |

### Step 5 — Scheduled work and logs

```bash
{
  echo "=== User crontabs ==="; crontab -l 2>/dev/null; sudo crontab -l 2>/dev/null
  echo "=== Cron dirs ==="; ls -l /etc/cron.d /etc/cron.daily 2>/dev/null | head -20
  echo "=== Timers ==="; systemctl list-timers --all --no-pager | head -10
} | tee 08-scheduled.txt

sudo journalctl --since "24 hours ago" -p warning --no-pager | tail -30 | tee 09-warnings.txt
```

### Step 6 — Write the observation register

Create `10-observations.md`. Every observation uses the four-part shape:

```markdown
## OBS-01
- Observation: PostgreSQL listens on 0.0.0.0:5432.
- Why it matters: Any host on the lab segment can reach the database; credentials are the only barrier.
- Evidence: 06-sockets.txt line 7, collected 2026-10-28T09:12Z on lab-ubuntu.
- Recommendation: Bind to 127.0.0.1 in postgresql.conf; if remote access is genuinely required, restrict with
  pg_hba.conf plus a host firewall rule.
```

Aim for **six to ten** observations. Include at least one benign-but-unusual item and explain why it is not a
finding — that distinction is what the marker is looking for.

## Evidence to collect

`00-platform.txt` through `09-warnings.txt`, plus `10-observations.md`. Keep the raw outputs; the register cites
them by filename.

## Verification criteria

- [ ] Inventory captured read-only, with no configuration changed.
- [ ] Timestamp and hostname recorded in `00-platform.txt`.
- [ ] Every SUID binary classified as package-owned or unowned.
- [ ] Every listening socket mapped to a process and a purpose.
- [ ] At least six observations written in the four-part shape.
- [ ] At least one benign anomaly explained rather than reported as a defect.
- [ ] Evidence citations name the file and the collection time.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `find` takes minutes | No `-xdev`, walking pseudo filesystems | Add `-xdev` and prune `/proc`, `/sys` |
| `ss -p` shows no process | Not root | `sudo ss -tulpn` |
| `dpkg -S` returns nothing | File not from a package | That is the finding — record it as UNOWNED |
| `lastb` empty | `btmp` not readable or no failures recorded | `sudo lastb`; failures appear after a bad login |
| Enabled-not-running list is long | Normal on a desktop image | Note the count; explain only unexpected entries |

## Cleanup and restoration

```bash
# Nothing was changed; verify that.
ssh lab-ubuntu 'sudo sshd -T | grep -i passwordauthentication'   # should still read no if you kept LAB-205-02
pgrep -a python3 | head    # stop any leftover lab server
```

## Questions and extension challenges

1. Which single observation would you fix first, and why?
2. Why is `UNOWNED` more significant than the presence of SUID itself?
3. What does an enabled-but-not-running service tell you that the running list does not?
4. Re-run the socket inventory after stopping a lab service. Record the before/after and explain the change.
5. Which of your observations would disappear if the host were behind a firewall? Which would remain?

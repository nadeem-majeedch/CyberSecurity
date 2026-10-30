---
title: "LAB-115-01 · Follow an Evidence Trail"
description: "Diagnose a deliberately broken systemd service using logs alone, fix it, and document the trail."
module_code: CYB-115
level: 1
kind: lab
prerequisites: [CYB-115]
estimated_minutes: 60
difficulty: beginner
safety: local-only
lab_ids: [LAB-115-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [logs, troubleshooting, systemd]
---

# LAB-115-01 · Follow an Evidence Trail

**Module:** CYB-115 · **Time:** 60 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-115-01`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** your own `lab-ubuntu` VM, and the throwaway service you create in this lab.
    **Targets you must not use:** any other host; and do not modify system services (`ssh`, `systemd-*`) to
    "see what happens".

    You will create, break, diagnose, and remove a service called `lab115`. Everything is reversible in three
    commands, and the snapshot is your safety net.

## Objective

Create a small systemd service, introduce a fault, and diagnose it using only log evidence — then fix it and
prove the fix, documenting each step with the command and output that justified it.

## Threat model

None. The lab simulates a service failing to start, which is the most common operational incident a junior
analyst is asked to investigate.

## Environment

| Host | Role | Notes |
| --- | --- | --- |
| `lab-ubuntu` | Target | `systemd`, `journalctl`, `sudo` |

## Before you start

```bash
mkdir -p ~/cyber/level-1/lab-115-01/evidence
cd ~/cyber/level-1/lab-115-01
hostname
```

## Procedure

### Step 1 — Create a working service

```bash
sudo tee /usr/local/bin/lab115.sh >/dev/null <<'SH'
#!/bin/bash
echo "lab115 ran at $(date -Is)"
SH
sudo chmod 755 /usr/local/bin/lab115.sh

sudo tee /etc/systemd/system/lab115.service >/dev/null <<'UNIT'
[Unit]
Description=LAB-115-01 evidence trail service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/lab115.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl start lab115.service
systemctl status lab115.service --no-pager | head -12
```

**Expected:** `Active: active (exited)` — a oneshot service that ran successfully.

### Step 2 — Record the healthy state

```bash
systemctl is-active lab115.service | tee evidence/healthy.txt
journalctl -u lab115.service --no-pager | tail -5 | tee -a evidence/healthy.txt
```

### Step 3 — Introduce a fault (the instructor-style part)

Change the `ExecStart` path to something that does not exist:

```bash
sudo sed -i 's#/usr/local/bin/lab115.sh#/usr/local/bin/lab115-missing.sh#' /etc/systemd/system/lab115.service
sudo systemctl daemon-reload
sudo systemctl restart lab115.service
echo "restart exit: $?"
```

**Expected:** a non-zero exit code and a message such as
`Job for lab115.service failed because the control process exited with error code.`

### Step 4 — Diagnose from evidence only

Do not read `/etc/systemd/system/lab115.service` yet. Work from logs:

```bash
systemctl status lab115.service --no-pager | tee evidence/failure.txt
journalctl -u lab115.service -n 15 --no-pager | tee -a evidence/failure.txt
journalctl -p err -b --no-pager | tail -10 | tee -a evidence/failure.txt
```

**Expected** in `failure.txt`: a status showing `failed`, and a journal line naming the missing path, for
example:

```text
lab115.service: Failed at step EXEC spawning /usr/local/bin/lab115-missing.sh: No such file or directory
```

Write in `trail.md`: which line identified the cause, and which command produced it.

### Step 5 — Fix and verify

```bash
sudo sed -i 's#/usr/local/bin/lab115-missing.sh#/usr/local/bin/lab115.sh#' /etc/systemd/system/lab115.service
sudo systemctl daemon-reload
sudo systemctl restart lab115.service
systemctl is-active lab115.service | tee evidence/fixed.txt
journalctl -u lab115.service -n 5 --no-pager | tee -a evidence/fixed.txt
```

**Expected:** `active`, and a fresh journal entry with the current timestamp from the script.

### Step 6 — Prove the absence lesson

```bash
sudo systemctl stop lab115.service
sudo grep -c "lab115" /var/log/syslog || echo "no entries in syslog"
journalctl -u lab115.service -n 2 --no-pager
```

Answer in `trail.md`: if a colleague claimed "the service ran at 10:00 and we see nothing in `syslog`", what
are two possible explanations, and how would you distinguish them?

### Step 7 — Document the trail

`trail.md` must contain:

| Step | Command | Observation | Conclusion |
| --- | --- | --- | --- |
| 1 | `systemctl status` | active (exited) | baseline healthy |
| 2 | | | |
| 3 | | | |
| 4 | | | |

Plus one paragraph: what was the cause, what evidence proved it, and what would have hidden it (for example,
if journald were not persistent across reboots).

## Evidence to collect

`evidence/healthy.txt`, `evidence/failure.txt`, `evidence/fixed.txt`, and `trail.md`.

## Verification

- [ ] The service started successfully before the fault.
- [ ] The failure was diagnosed from logs, not by reading the unit file early.
- [ ] `trail.md` cites the exact journal line that identified the cause.
- [ ] The fix restored `active` state and produced a new log entry.
- [ ] You explained one way the evidence could have been missing.

## Teardown and reset

```bash
sudo systemctl stop lab115.service 2>/dev/null
sudo systemctl disable lab115.service 2>/dev/null
sudo rm -f /etc/systemd/system/lab115.service /usr/local/bin/lab115.sh
sudo systemctl daemon-reload
systemctl status lab115.service --no-pager 2>&1 | head -3
```

**Expected:** `Unit lab115.service could not be found.` Revert to `pre-lab-115-01` if anything remains.

## Reflection

1. Which single command gave you the most information, and why?
2. What would you have seen if the fault had been a wrong *permission* rather than a missing file?
3. Why is "the service is active" not proof that it did what you wanted?
4. What does this lab demonstrate about the value of persistent journal storage?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Service not created or not fixed | Diagnosed and fixed | Both states evidenced, with the decisive log line quoted |
| Methodology | Read the unit file instead of logs | Used `status` then journal | Narrowed by unit, then severity, then time |
| Evidence | Unsaved output | Three transcripts plus trail | Trail table with commands, observations and conclusions |
| Safety | Left the service installed | Removed service and script | Removed, verified, and explained the cleanup |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Unit lab115.service not found` after creation | `daemon-reload` not run | `sudo systemctl daemon-reload` |
| Service active but no log entry | Script wrote nowhere and journald rate-limited | Check `journalctl -u lab115 -n 20`; the `echo` should appear |
| `status` shows `failed` with no detail | `--no-pager` missing, or output truncated | Pipe through `cat`, or use `journalctl -u lab115 -n 50` |
| Fix applied but still failing | Typo in `sed`, or old unit cached | `systemctl cat lab115.service` to confirm the current file |
| `journalctl` shows nothing from before reboot | Non-persistent journal | Note it as the absence lesson; do not "fix" it in this lab |

## Related

- [Reading Logs and Troubleshooting Methodically](01-logs-and-troubleshooting.md)
- [LAB-109-02 · Processes, Listening Ports and Logs](../09-linux-command-line/lab-02-processes-listeners-logs.md)
- [Level 2 — Tooling and Lab Craft](../../level-2.md)

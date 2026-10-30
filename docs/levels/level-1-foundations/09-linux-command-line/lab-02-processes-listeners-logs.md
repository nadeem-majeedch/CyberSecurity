---
title: "LAB-109-02 · Processes, Listening Ports and Logs"
description: "Start a service, map its port to its process, inspect the process tree, and find the log evidence."
module_code: CYB-109
level: 1
kind: lab
prerequisites: [CYB-109]
estimated_minutes: 45
difficulty: beginner
safety: local-only
lab_ids: [LAB-109-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [linux, processes, ports, logs]
---

# LAB-109-02 · Processes, Listening Ports and Logs

**Module:** CYB-109 · **Time:** 45 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-109-02`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** your own lab VM: processes you start, and services already running on it.
    **Targets you must not use:** any other host.

    You will start and stop your own processes only. Do not stop system services such as `ssh` or
    `systemd-resolved`; if you want to see what stopping them does, use `systemctl status`, not `stop`.

## Objective

Start a local service, identify the process that owns its port, trace it in the process tree, terminate it
cleanly, and locate the log entries that record each action.

## Threat model

None. Everything runs locally inside the VM; the "service" is Python's built-in HTTP server bound to
`127.0.0.1`.

## Environment

| Host | Role | Notes |
| --- | --- | --- |
| `lab-ubuntu` | Target | Python 3, `iproute2`, `systemd` |

## Before you start

```bash
mkdir -p ~/cyber/level-1/lab-109-02/evidence
hostname
```

## Procedure

### Step 1 — Start a process and note its PID

```bash
cd /tmp
python3 -m http.server 8081 --bind 127.0.0.1 > /tmp/lab109-server.log 2>&1 &
echo $! > /tmp/lab109.pid
cat /tmp/lab109.pid
```

**Expected:** a PID, e.g. `4321`.

### Step 2 — Map the port to the process

```bash
sudo ss -tlnp 'sport = :8081'
```

**Expected** (PID varies):

```text
LISTEN 0 5 127.0.0.1:8081 0.0.0.0:* users:(("python3",pid=4321,fd=3))
```

Note the bind address: `127.0.0.1` means only this machine can connect. If it were `0.0.0.0`, every
interface would be exposed — the difference between a lab tool and an incident.

### Step 3 — Inspect the process tree

```bash
ps -o pid,ppid,user,stat,comm -p "$(cat /tmp/lab109.pid)"
ps -eo pid,ppid,user,comm --forest | grep -B2 -A2 "$(cat /tmp/lab109.pid)"
```

**Expected:** your process appears with `PPID` equal to your shell's PID and user equal to your account.
Explain in your notes which process is the parent, and why that matters when you kill the parent by mistake.

### Step 4 — Confirm it is reachable, then stop it

```bash
curl -s -o /dev/null -w "http status: %{http_code}\n" http://127.0.0.1:8081/
kill "$(cat /tmp/lab109.pid)"
sleep 1
sudo ss -tlnp 'sport = :8081' || echo "port 8081 no longer listening"
curl -s -m 2 http://127.0.0.1:8081/ -o /dev/null; echo "curl exit after stop: $?"
```

**Expected:** `http status: 200`, then the port is gone, and `curl exit after stop: 7` (connection refused).

### Step 5 — Read the service log

```bash
cat /tmp/lab109-server.log
```

**Expected** (client port varies):

```text
127.0.0.1 - - [28/Oct/2026 22:05:11] "GET / HTTP/1.1" 200 -
```

This is the simplest possible access log. Every real web server produces the same structure with more
fields — and this is the data you will analyse at Level 2.

### Step 6 — Find your action in the system logs

```bash
sudo journalctl --since "10 min ago" --no-pager | tail -20
sudo grep -a "sudo" /var/log/auth.log | tail -5
```

**Expected:** your `sudo ss` and `sudo journalctl` invocations recorded with timestamp and user. You have
just generated the audit trail an investigator would read.

### Step 7 — Optional: observe a failed authentication

```bash
sudo -k                       # forget cached sudo credentials
sudo -l                       # enter a WRONG password once, then press Ctrl-C
sudo grep -a "authentication failure" /var/log/auth.log | tail -3
```

**Expected:** a line mentioning `authentication failure` and your username. **One attempt only** — this is
your own account, and repeated failures add noise for no learning benefit.

## Evidence to collect

- `evidence/port-map.txt` (the `ss` output with the PID).
- `evidence/process-tree.txt` (`ps` forest output).
- `evidence/server-log.txt` (the Python access log).
- `evidence/notes.md` answering the reflection questions below.

## Verification

- [ ] You mapped port 8081 to a specific PID and user.
- [ ] The process tree showed your shell as the parent.
- [ ] `curl` returned 200 while running and exit code 7 after stopping.
- [ ] The access log recorded your request.
- [ ] You found your `sudo` activity in `/var/log/auth.log`.

## Teardown and reset

```bash
kill "$(cat /tmp/lab109.pid)" 2>/dev/null
rm -f /tmp/lab109.pid /tmp/lab109-server.log
ss -tlnp 'sport = :8081' || echo "clean: nothing on 8081"
```

Revert to `pre-lab-109-02` if you stopped or modified any service.

## Reflection

1. What is the difference between a process existing and a port listening?
2. Why does the bind address matter more than the port number for exposure?
3. Where would you look first if a port were listening that you did not expect?
4. Why is killing the parent process sometimes worse than killing the child?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Could not map port to process | Mapped PID, stopped cleanly | Explained bind address, parent/child, and exit codes |
| Methodology | Random process hunting | Used `ss` then `ps` deliberately | Chose filters that answered the question precisely |
| Evidence | No saved output | Saved all four artefacts | Annotated with timestamps and reasoning |
| Safety | Stopped a system service | Only own process | Only own process, with a note on what not to stop |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Address already in use` | Port 8081 busy | Choose 8082, or find and stop the previous process |
| `ss` shows nothing | Wrong filter syntax or no `sudo` | `sudo ss -tlnp`, or drop the filter and `grep 8081` |
| `kill` says "No such process" | The shell job already exited | Check `ps -p <pid>`; use `jobs` to list |
| `curl exit after stop: 28` | Timeout rather than refused | Something is filtering; confirm the port with `ss` |
| No `authentication failure` line | `journalctl` only, or log rotated | Check `journalctl -u ssh` and `/var/log/auth.log` together |
| `journalctl` shows no recent entries | Clock skew in the VM | Fix time sync; note the discrepancy |

## Related

- [Working in the Linux Shell](01-linux-shell.md)
- [LAB-109-01 · Files, Permissions and Ownership](lab-01-files-permissions.md)
- [Introduction to Security Logs and Troubleshooting](../15-security-logs-and-troubleshooting/index.md)

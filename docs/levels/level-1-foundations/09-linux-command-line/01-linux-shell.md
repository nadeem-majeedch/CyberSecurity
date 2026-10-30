---
title: "Working in the Linux Shell"
description: "Paths and navigation, file operations, permissions and umask, processes, services, packages, and how to find help."
module_code: CYB-109
level: 1
kind: lesson
prerequisites: [CYB-108]
estimated_minutes: 120
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [linux, shell, bash, permissions]
---

# Working in the Linux Shell

## Learning objectives

By the end of this lesson you can:

1. Read a shell prompt and use absolute and relative paths correctly.
2. Create, inspect, copy, move, and delete files and directories without losing data.
3. Set permissions and ownership, and predict the effect of `umask`.
4. Inspect processes, find what owns a port, and stop a process deliberately.
5. Manage services and packages, and locate the log evidence for each action.
6. Use `man`, `--help`, and exit codes to answer your own questions.

## Prerequisites

[CYB-108](../08-addressing-and-protocols/index.md). A running `lab-ubuntu` VM with `sudo`.

---

## 1. The prompt and the filesystem

A typical prompt:

```text
student@lab-ubuntu:~$
```

`student` is the user, `lab-ubuntu` the host, `~` the current directory, `$` means an ordinary user (`#`
means root).

Three path facts:

- **Absolute** paths start at `/`: `/etc/ssh/sshd_config`.
- **Relative** paths start where you are: `../ssh/sshd_config`.
- `~` is your home; `.` is here; `..` is the parent.

Key directories worth memorising:

| Path | Contents | Security relevance |
| --- | --- | --- |
| `/etc` | Configuration | Most hardening lives here |
| `/var/log` | Logs | Evidence |
| `/home` | User data | Permissions, keys, history files |
| `/tmp` | Temporary, world-writable | A classic staging location for attackers |
| `/usr/bin`, `/bin` | Programs | Where tools live |
| `/proc` | Kernel and process state as files | Live process inspection |

```bash
pwd
ls -la ~
cd /etc && pwd
cd ~
```

**Expected:** your current directory, then a listing including `.bashrc` and `.ssh` (if configured), then
`/etc`, then back home.

## 2. Files without fear

| Task | Command | Caution |
| --- | --- | --- |
| Create empty file | `touch notes.txt` | None |
| Write text | `printf 'text\n' > notes.txt` | `>` overwrites |
| Append | `printf 'more\n' >> notes.txt` | None |
| View | `cat notes.txt`, `less notes.txt` | None |
| Copy | `cp -r dir1 dir2` | `-r` for directories |
| Move/rename | `mv old.txt new.txt` | Overwrites silently |
| Delete | `rm notes.txt` | **No undo, no trash** |
| Delete directory | `rm -r dir` | Very dangerous with globs |

`rm` is the command that ends careers. Two habits:

- **Look before you delete**: run the `ls` you are about to delete with, then change `ls` to `rm`.
- **Never** run `rm -rf $VARIABLE/` when the variable might be empty — it becomes `rm -rf /`.

```bash
mkdir -p /tmp/practice/docs && cd /tmp/practice
printf 'hello\n' > docs/a.txt
cp docs/a.txt docs/b.txt
ls -l docs
mv docs/b.txt docs/c.txt
rm docs/c.txt
ls docs
```

**Expected:** after the final `ls`, only `a.txt` remains.

## 3. Permissions, ownership, umask

Recap from CYB-106: mode is owner/group/other, `r=4 w=2 x=1`.

```bash
cd /tmp/practice
chmod 640 docs/a.txt
stat -c '%a %U:%G %n' docs/a.txt
sudo chown root:root docs/a.txt
stat -c '%a %U:%G %n' docs/a.txt
```

**Expected:**

```text
640 student:student docs/a.txt
640 root:root docs/a.txt
```

`chown` needs `sudo` because you are giving the file to another owner.

**umask** determines the default permissions for new files: `mode = 666 − umask` for files, `777 − umask`
for directories.

```bash
umask
printf 'x\n' > default.txt
stat -c '%a %n' default.txt
umask 077
printf 'y\n' > private.txt
stat -c '%a %n' private.txt
umask 022
```

**Expected** with the Ubuntu default `022`: `644 default.txt`, then `600 private.txt`. Setting `umask 077`
is a common hardening step so new files are private by default.

## 4. Processes and ports

```bash
ps aux | head -8
ps -eo pid,ppid,user,comm --forest | head -12
top -b -n1 | head -12
```

**Expected:** a header line, then processes with `root` and your user. `top -b -n1` prints one snapshot and
exits — useful in scripts and over SSH.

Find what owns a port:

```bash
sudo ss -tlnp | grep -E ':22|:53'
```

**Expected** (PIDs vary):

```text
LISTEN 0  4096  0.0.0.0:22  0.0.0.0:*  users:(("sshd",pid=655,fd=3))
LISTEN 0  4096  127.0.0.53:53  0.0.0.0:*  users:(("systemd-resolve",pid=582,fd=13))
```

Note the bind addresses: `0.0.0.0:22` accepts connections from any interface; `127.0.0.53:53` is local only.
That distinction is a hardening finding in miniature.

Stopping a process:

```bash
sleep 300 &
ps -o pid,comm -p $!
kill $!
```

**Expected:** the PID and `sleep`, then no error. Prefer `kill` (SIGTERM, polite) to `kill -9` (SIGKILL,
no cleanup) — the latter is a last resort.

## 5. Services and packages

```bash
systemctl status ssh --no-pager
systemctl is-enabled ssh
sudo apt update
apt list --installed 2>/dev/null | grep -c '^'
```

**Expected:** service state (active/enabled), then a package count. `apt update` refreshes metadata; it
does not upgrade anything.

Useful patterns:

```bash
sudo systemctl restart ssh      # apply config changes
systemctl list-units --type=service --state=running
apt-cache policy openssl        # installed vs candidate version
```

## 6. Logs, help, exit codes

```bash
journalctl -n 20 --no-pager
sudo tail -n 5 /var/log/auth.log
man ls | head -20
ls --help | head -5
ls /nonexistent; echo "exit code: $?"
```

**Expected:** recent journal entries, recent auth events (including your `sudo` use), manual excerpt, help
text, and `exit code: 2` for the failed `ls`.

Reading exit codes matters: `0` means success, non-zero means specific failure. Scripts depend on it, and so
does troubleshooting.

---

## Practical exercises

### Exercise 1 — Navigation without a GUI (10 minutes)

Starting from `~`, reach `/var/log` using only `cd` and relative paths, then return home with one command.
Write the command sequence in your notes.

### Exercise 2 — Build a directory tree (15 minutes)

```bash
mkdir -p ~/cyber/practice/{notes,evidence,scripts}
printf '#!/bin/bash\necho hello\n' > ~/cyber/practice/scripts/hello.sh
chmod 750 ~/cyber/practice/scripts/hello.sh
~/cyber/practice/scripts/hello.sh
```

**Expected:** `hello`. Then explain why `chmod 750` allows you to run it and what others can do.

### Exercise 3 — Predict the umask (10 minutes)

Before running, predict the mode of a new file and directory with `umask 027`. Then verify:

```bash
umask 027
touch /tmp/practice/umask-file
mkdir -p /tmp/practice/umask-dir
stat -c '%a %n' /tmp/practice/umask-file /tmp/practice/umask-dir
umask 022
```

**Expected:** `640` and `750`.

### Exercise 4 — Port to process (10 minutes)

Identify the process listening on port 22, its PID, and its user. Then answer: could a non-root user bind
port 22? Why not? (Ports below 1024 are privileged on Linux by default.)

### Exercise 5 — Read your own audit trail (10 minutes)

```bash
sudo grep -a "$(whoami)" /var/log/auth.log | tail -5
```

You should see your `sudo` invocations. This is the same evidence an investigator would use, at a very
small scale.

## Expected observations and verification

- You can explain absolute versus relative paths without notes.
- You predicted the `umask 027` results correctly.
- You mapped port 22 to a process and user.
- You found your own `sudo` activity in `/var/log/auth.log`.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| `rm -rf` with a glob in the wrong directory | Speed | `ls` first; quote paths; never run from `/` |
| `cd` with no argument fails on some shells | No `HOME` set | `cd ~` or `cd /home/<user>` |
| `Permission denied` running your script | Missing execute bit | `chmod +x script.sh` |
| `sudo: command not found` | The command is not installed | Install it; `sudo` only elevates, it does not add software |
| Editing a config and seeing no effect | Service not reloaded | `sudo systemctl reload <service>` |
| `journalctl` shows everything and nothing useful | No filter | `journalctl -u ssh -n 50`, or `-p err` |
| Losing work with `>` instead of `>>` | Both look similar | `>` truncates; `>>` appends |

## Review questions

1. What is the difference between `/etc` and `/var/log` in terms of what a security review looks at?
2. Why is `/tmp` interesting to an attacker?
3. Explain `umask 027` in terms of the permissions new files receive.
4. Why prefer `kill` over `kill -9`?
5. What does a non-zero exit code tell you that an error message may not?
6. Why is binding to `127.0.0.1` safer than `0.0.0.0` for a lab service?

## Knowledge check

1. Which command shows listening TCP ports with the owning process?
2. A file created under `umask 077` has which mode?
3. What does `chown root:root file` require, and why?
4. Where would you look for authentication events on Ubuntu?
5. What is the exit code of a successful command?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 3–6 if 2, 3 and 5 are uncertain.)*

## Summary

- Paths, permissions, and process identity are the three things you read most often on Linux.
- `rm` has no undo; look before you delete, and never let a variable expand into `/`.
- `umask` sets defaults for everything you create, which is why it is a hardening setting.
- Ports map to processes, and bind addresses decide who can reach them.
- Logs, `man`, and exit codes let you solve problems without guessing.

## Next lesson

[CYB-110 · Windows Fundamentals and PowerShell Basics](../10-windows-powershell-basics/index.md) — the same
concepts through a different operating system's model.

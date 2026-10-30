---
title: "Hardware, Operating Systems, Files, Processes and Permissions"
description: "Boot sequence, kernel and user space, files and metadata, processes and states, and permission models on Linux and Windows."
module_code: CYB-106
level: 1
kind: lesson
prerequisites: [CYB-105]
estimated_minutes: 150
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [operating-systems, permissions, processes]
---

# Hardware, Operating Systems, Files, Processes and Permissions

## Learning objectives

By the end of this lesson you can:

1. Describe the boot sequence from firmware to login prompt.
2. Explain kernel space versus user space and why the boundary matters for security.
3. Read file type, ownership, mode, and timestamps on Linux, and explain what each means.
4. Explain process creation, parent/child relationships, and the meaning of process states.
5. Convert between symbolic and octal permissions, and set them correctly.
6. Identify three permission mistakes that create exploitable risk.

## Prerequisites

[CYB-105](../05-ethics-authorization-disclosure-law/index.md). A Linux shell and a Windows terminal help;
both are used below.

---

## 1. The machine, briefly

| Component | What it does | Why a security person cares |
| --- | --- | --- |
| **CPU** | Executes instructions; has privilege rings | Ring 0 (kernel) vs ring 3 (user) is the hardware basis of isolation |
| **RAM** | Holds running code and data | Memory contains credentials and keys; memory forensics lives here |
| **Disk** | Persistent storage | Retention, deletion, and forensic recovery all depend on it |
| **Firmware (UEFI/BIOS)** | Initialises hardware, hands off to bootloader | Secure Boot and firmware passwords are real controls, often ignored |
| **Network interface** | Connects the machine | Every exposed service is reachable through it |

### The boot sequence

```text
firmware → bootloader (GRUB/Windows Boot Manager) → kernel → init/systemd → services → login
```

Three security-relevant facts:

- Firmware runs before the OS, so malware there survives reinstalls.
- The kernel is the first thing with full hardware control; its modules extend it.
- Services started at boot define your attack surface before anyone logs in.

## 2. Kernel space and user space

The CPU has privilege levels. The kernel runs with full privilege; ordinary programs run restricted and
must ask the kernel for anything sensitive (file access, network, memory) through **system calls**.

That boundary is *the* security boundary on a single machine. Two consequences:

- A vulnerability in the kernel (or a driver) can compromise everything.
- A vulnerability in a user-space program compromises only what that program can reach — which is why
  running services as an unprivileged user limits damage.

```bash
# See the kernel version and architecture
uname -a
cat /etc/os-release | head -3
```

**Expected output** (yours will differ in version numbers):

```text
Linux lab-ubuntu 6.8.0-45-generic #45-Ubuntu SMP PREEMPT_DYNAMIC x86_64 GNU/Linux
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
```

## 3. Files: more than a name

On Linux, a file's name lives in a directory entry; the file itself is an **inode** holding metadata:
owner, group, mode, size, timestamps, and pointers to data blocks. This is why a file can have multiple
names (hard links) and why deleting a name does not necessarily delete the data.

```bash
cd /tmp
printf 'hello\n' > demo.txt
stat demo.txt
file demo.txt
ls -l demo.txt
```

**Expected output** (values vary):

```text
  File: demo.txt
  Size: 6          Blocks: 8          IO Block: 4096   regular file
Access: (0644/-rw-r--r--)  Uid: ( 1000/ student)   Gid: ( 1000/ student)
Access: 2026-10-28 21:40:12.123456789 +0500
Modify: 2026-10-28 21:40:12.123456789 +0500
Change: 2026-10-28 21:40:12.123456789 +0500
demo.txt: ASCII text
-rw-r--r-- 1 student student 6 Oct 28 21:40 demo.txt
```

Read that line right to left: name, size, date, group, owner, link count, mode. **Mode** is the security
part.

### Permissions on Linux

Three permission triples, for **owner**, **group**, and **others**:

| Symbol | File meaning | Directory meaning |
| --- | --- | --- |
| `r` (4) | Read contents | List names |
| `w` (2) | Modify contents | Create/delete entries |
| `x` (1) | Execute | Enter (traverse) |

Octal is just addition: `rw-` = 4+2 = 6, `r-x` = 4+1 = 5, `rwx` = 7.

| Mode | Symbolic | Typical use |
| --- | --- | --- |
| `644` | `-rw-r--r--` | Normal file, readable by all |
| `600` | `-rw-------` | Private file, e.g. SSH key |
| `755` | `-rwxr-xr-x` | Executable, readable by all |
| `640` | `-rw-r-----` | Group-readable config |
| `777` | `-rwxrwxrwx` | World-writable — almost always a mistake |

```bash
chmod 600 demo.txt
stat -c '%a %U:%G %n' demo.txt
chmod 644 demo.txt
```

**Expected output:**

```text
600 student:student demo.txt
```

Directories need `x` to be entered: a directory with `r` but no `x` lets you list names but not access
the files. That distinction confuses beginners and appears in real findings.

### Windows permissions, for contrast

Windows uses **ACLs**: each object has a list of access control entries naming a principal and allowed or
denied rights. There is no simple octal number.

```powershell
New-Item -ItemType Directory -Force C:\lab\demo | Out-Null
"hello" | Out-File C:\lab\demo\demo.txt
icacls C:\lab\demo\demo.txt
```

**Expected output** (SIDs and names vary):

```text
C:\lab\demo\demo.txt BUILTIN\Administrators:(F)
                     NT AUTHORITY\SYSTEM:(F)
                     DESKTOP-ABC\student:(F)
```

`(F)` means full control; `(R)` read, `(W)` write, `(M)` modify. The security lesson is the same as Linux:
**who** has **what** on **which object**, and is that the minimum?

## 4. Processes

A process is a running program with its own memory, file descriptors, and identity (user/group). Processes
are created by other processes, giving a tree.

```bash
ps -eo pid,ppid,user,stat,comm --sort=pid | head -12
```

**Expected output** (PIDs and names vary):

```text
    PID    PPID USER     STAT COMMAND
      1       0 root     Ss   systemd
    412       1 root     Ss   systemd-journald
    655       1 root     Ss   sshd
   1203       1 student  Ss   systemd
   1204    1203 student  S    bash
```

| State | Meaning |
| --- | --- |
| `R` | Running or runnable |
| `S` | Sleeping, waiting for an event |
| `D` | Uninterruptible sleep (usually I/O) |
| `Z` | Zombie — finished, not yet reaped |
| `T` | Stopped |

Security relevance: every process has a **user identity**. A web server running as `www-data` cannot read
root-only files; one running as `root` can read everything. That single decision is often the difference
between a contained incident and a total compromise.

```bash
# Which user owns the listening services? (ss is in iproute2)
ss -tulpn 2>/dev/null | head
```

## 5. Services, logs, and the trail

Long-running processes are managed as **services**. On modern Ubuntu they are `systemd` units.

```bash
systemctl list-units --type=service --state=running | head
journalctl -n 10 --no-pager
```

Logs are your evidence. Where they live:

| Source | Location / command |
| --- | --- |
| System journal | `journalctl` |
| Auth events | `/var/log/auth.log` (Debian/Ubuntu) |
| Web server | `/var/log/nginx/access.log`, `error.log` |
| Windows security | Event Viewer → Security, or `Get-WinEvent -LogName Security` |

You will read logs properly in CYB-115.

---

## Practical exercises

### Exercise 1 — Inspect the machine (10 minutes)

```bash
lscpu | head -8
free -h
df -h /
```

Record CPU model, core count, RAM, and root filesystem usage in your notes. On Windows:

```powershell
Get-ComputerInfo | Select-Object CsName, OsName, CsNumberOfLogicalProcessors, CsTotalPhysicalMemory
Get-Volume | Select-Object DriveLetter, FileSystemLabel, SizeRemaining, Size
```

### Exercise 2 — Permissions ladder (20 minutes)

```bash
mkdir -p /tmp/permtest && cd /tmp/permtest
printf 'secret\n' > data.txt
chmod 600 data.txt; ls -l data.txt
chmod 644 data.txt; ls -l data.txt
chmod 777 data.txt; ls -l data.txt
```

Answer in your notes: which of these would you accept for a file holding credentials, and why? Which would
a security review reject outright?

### Exercise 3 — Directory traversal versus listing (10 minutes)

```bash
mkdir -p /tmp/permtest/dir && printf 'x\n' > /tmp/permtest/dir/inside.txt
chmod 444 /tmp/permtest/dir      # read but no execute
ls /tmp/permtest/dir             # works: names visible
cat /tmp/permtest/dir/inside.txt # fails: no traversal
chmod 755 /tmp/permtest/dir
```

**Expected:** the `ls` succeeds, the `cat` returns `Permission denied`. This is the `r` versus `x` distinction
on directories, and it is a real finding pattern (readable but non-enterable backup directories).

### Exercise 4 — Process ownership (10 minutes)

```bash
ps -eo user,pid,comm --sort=user | head -15
id
```

Find one process running as `root` and one as your user. For the root one, ask: does it need to be root?

### Exercise 5 — Windows ACL read (10 minutes)

```powershell
icacls C:\lab\demo\demo.txt
Get-Acl C:\lab\demo\demo.txt | Format-List
```

Identify every principal with access, and whether any of them should not have it.

## Expected observations and verification

- You can convert `rw-r-----` to `640` and back without looking it up.
- You can explain why a world-writable file in a web directory is a risk.
- You can name a process running as root in your VM, and whether that is justified.
- You saw the `r`-without-`x` directory behaviour and can describe it.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| `chmod 777` to "make it work" | Fastest way past a permission error | Fix ownership or add a group instead; 777 is a finding |
| Confusing file `x` with directory `x` | Same symbol, different meaning | Directory `x` = traverse; file `x` = execute |
| Editing a script that is not executable | Saved without the bit | `chmod +x script.sh`, or run with `bash script.sh` |
| `Permission denied` on a directory you own | Missing `x` on a parent directory | Check every component of the path |
| Assuming `sudo` is normal administration | Muscle memory | Use `sudo` for the specific command, not a root shell |
| Deleting a file and assuming data is gone | Names vs blocks | Use secure deletion only where policy requires it; understand journaling and snapshots |
| Windows `Access is denied` while "administrator" | UAC token filtering | Run the shell elevated explicitly, and only when needed |

## Review questions

1. Why is the kernel/user-space boundary a security boundary?
2. What does an inode store, and why can deletion not guarantee erasure?
3. Convert `rwxr-x---` to octal and explain who can do what.
4. What does process state `Z` mean, and why does it exist?
5. Why does the user a service runs as matter more than the service itself?
6. Name three permission mistakes that create real risk.

## Knowledge check

1. A file mode of `640` grants which rights to group members?
2. Which process is always PID 1 on a modern Ubuntu system?
3. A directory with mode `444` allows listing but not traversal. True or false?
4. `icacls` output `(F)` means what?
5. If a web server runs as `root`, what is the security consequence of a code-execution flaw?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 3–4 if 2 and 3 are uncertain.)*

## Summary

- Firmware, bootloader, kernel, services: each stage is a place where security can be lost or gained.
- The kernel/user-space split is the machine's fundamental isolation mechanism.
- Files are inodes plus names; permissions are triples for owner, group, others.
- Processes carry an identity, and that identity bounds the damage they can do.
- Logs are evidence, and reading them is a core skill you start now.

## Next lesson

[CYB-107 · Networking Fundamentals and the OSI/TCP-IP Models](../07-networking-fundamentals/index.md) — how
these machines talk to each other, layer by layer.

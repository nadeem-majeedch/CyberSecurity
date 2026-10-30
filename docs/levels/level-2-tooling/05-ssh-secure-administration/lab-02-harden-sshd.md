---
title: "LAB-205-02 · Audit and Harden sshd Without Locking Yourself Out"
description: "Baseline the effective sshd configuration, apply a defensible hardening set, and prove access survives every step."
module_code: CYB-205
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-205-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [sshd, hardening, audit, diff]
---

# LAB-205-02 · Audit and Harden sshd Without Locking Yourself Out

| | |
| --- | --- |
| **Level** | 2 |
| **Time** | 4 hours |
| **Prerequisites** | LAB-205-01 (key access must work first) |
| **Lab hosts** | `lab-kali` 192.0.2.10, `lab-ubuntu` 192.0.2.20 |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

An audit of the lab server found that password authentication is still enabled, root can log in directly, and the
configuration file's comments contradict what is actually active. You are to harden the service and produce a
before/after diff with evidence that the hardened service still works for authorised access and refuses the rest.

The failure mode this lab is designed to prevent: locking yourself out of a machine five kilometres away.

## Learning objectives

1. Establish a baseline of *effective* configuration, not the file's comments.
2. Apply hardening in verified increments, never a single blind edit.
3. Demonstrate that unauthorised methods are now refused.
4. Produce a reproducible before/after diff and a rollback plan.
5. Read `auth.log`/`journalctl` for the resulting evidence.

## Required tools and versions

| Tool | Version | Install |
| --- | --- | --- |
| `openssh-server` | 9.x | `sudo apt install openssh-server` |
| `sshpass` (for negative tests only) | 1.09 | `sudo apt install sshpass` — lab use, never production |
| `diffutils` | any | present |

## Setup

```bash
mkdir -p ~/lab205/config && cd ~/lab205/config
```

Confirm key access works *before* anything else:

```bash
ssh lab-ubuntu 'echo key-access-ok'
```

**Expected:** `key-access-ok`. If this fails, return to LAB-205-01.

## Target addresses and lab topology

```
lab-kali 192.0.2.10  --- host-only lab-only-192.0.2.0 ---  lab-ubuntu 192.0.2.20
        (administrator)                                   (sshd, tcp/22, accounts: student, otheruser)
```

Use two terminals on `lab-kali` so one session can verify the change while the other stays open as your rollback
path.

## Numbered commands and actions

### Step 1 — Baseline the effective configuration

```bash
ssh lab-ubuntu 'sudo sshd -T' > sshd.before.txt
wc -l sshd.before.txt
grep -Ei '^(permitrootlogin|passwordauthentication|kbdinteractiveauthentication|pubkeyauthentication|maxauthtries|x11forwarding|permitemptypasswords|allowusers|port)' sshd.before.txt
```

**Expected:** values such as

```
permitrootlogin yes
passwordauthentication yes
kbdinteractiveauthentication yes
maxauthtries 6
x11forwarding yes
```

Compare with the commented lines in `/etc/ssh/sshd_config`:

```bash
ssh lab-ubuntu 'grep -nE "^#?(PermitRootLogin|PasswordAuthentication|MaxAuthTries)" /etc/ssh/sshd_config'
```

**Expected:** many commented defaults — proof that comments are not configuration. Record one example in your notes.

### Step 2 — Capture the negative baseline

```bash
sshpass -p "$(read -rsp 'lab password: ' p; echo "$p")" ssh -o PubkeyAuthentication=no student@192.0.2.20 'echo password-login-worked'
ssh -o PreferredAuthentications=none student@192.0.2.20 'echo no-auth-worked'
```

**Expected:** the first prints `password-login-worked`; the second is refused.

!!! warning "About `sshpass`"
    `sshpass` puts a password on a command line where it can land in shell history and process lists. It is
    acceptable only in a disposable lab for a negative test. Never use it against a real host.

### Step 3 — Apply hardening in verified increments

Create the drop-in file on `lab-ubuntu`:

```bash
ssh lab-ubuntu 'sudo tee /etc/ssh/sshd_config.d/10-lab-hardening.conf >/dev/null <<"EOF"
# CYB-205 lab hardening. Later Include files override earlier ones.
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
X11Forwarding no
AllowUsers student
ClientAliveInterval 300
ClientAliveCountMax 2
EOF'
```

Check ordering matters:

```bash
ssh lab-ubuntu 'grep -rn "^Include" /etc/ssh/sshd_config; ls /etc/ssh/sshd_config.d/'
```

**Expected:** the main file includes `sshd_config.d/*.conf`; your file is listed. If a file sorts after yours and
sets a directive you changed, yours loses — a real cause of "the change did nothing".

### Step 4 — Validate syntax, then reload — never blind restart

```bash
ssh lab-ubuntu 'sudo sshd -t && echo "syntax OK"'
ssh lab-ubuntu 'sudo systemctl reload ssh'
```

**Expected:** `syntax OK`, then no output from reload.

!!! danger "Keep the original session open"
    Do not close your working SSH session until Step 5 has passed from a *new* terminal. Your open session is the
    rollback path.

### Step 5 — Verify from a fresh session

Open a **new** terminal on `lab-kali`:

```bash
ssh lab-ubuntu 'echo hardened-access-ok; sudo sshd -T | grep -Ei "^(permitrootlogin|passwordauthentication|maxauthtries|allowusers)"'
```

**Expected:**

```
hardened-access-ok
permitrootlogin no
passwordauthentication no
maxauthtries 3
allowusers student
```

### Step 6 — Prove the refusals

```bash
# 1. Password auth must now be impossible
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password student@192.0.2.20 'echo should-not-print'
# Expected: Permission denied (publickey).

# 2. Root must be refused
ssh -o PreferredAuthentications=publickey root@192.0.2.20 'echo should-not-print'
# Expected: Permission denied.

# 3. A user not in AllowUsers must be refused (create one first on lab-ubuntu)
ssh -o PreferredAuthentications=publickey otheruser@192.0.2.20 'echo should-not-print'
# Expected: Permission denied.
```

Then check the server's record of the attempts:

```bash
ssh lab-ubuntu 'sudo journalctl -u ssh --since "5 minutes ago" | grep -E "Failed|refused|Invalid user" | tail -10'
```

**Expected:** entries for the refused attempts, including `Invalid user otheruser` and a `no matching key exchange`
or `Authentication refused` style message. Note that *authentication refusals are logged* — this is the log you
will query during detection work in Level 4.

### Step 7 — Diff and rollback plan

```bash
ssh lab-ubuntu 'sudo sshd -T' > sshd.after.txt
diff -u sshd.before.txt sshd.after.txt > sshd.diff
cat sshd.diff
```

Write `~/lab205/config/rollback.md`:

```markdown
# Rollback
1. sudo rm /etc/ssh/sshd_config.d/10-lab-hardening.conf
2. sudo sshd -t && sudo systemctl reload ssh
3. Verify: ssh lab-ubuntu 'sudo sshd -T | grep -i passwordauthentication'  → passwordauthentication yes
Rollback window: until CYB-206 is complete. Snapshot: before-205.
```

### Step 8 — Confirm authorised access is unaffected

```bash
ssh lab-ubuntu 'uptime; id'
scp -q ~/lab205/config/sshd.diff lab-ubuntu:/home/student/sshd.diff && echo "transfer ok"
```

**Expected:** command output and `transfer ok`, with no password prompt.

## Evidence to collect

| Artefact | Purpose |
| --- | --- |
| `sshd.before.txt`, `sshd.after.txt` | Baseline and hardened effective config |
| `sshd.diff` | The actual change |
| Negative-test outputs | Proof that old paths are closed |
| `journalctl` excerpt | The server's record of refusals |
| `rollback.md` | Recoverability |
| Comment-vs-effective example | Evidence for the finding that documentation drifted |

## Verification criteria

- [ ] Baseline captured with `sshd -T`, not by reading comments.
- [ ] One example recorded where a comment disagreed with the effective value.
- [ ] Hardening applied via a drop-in file, not by editing the main config in place.
- [ ] `sshd -t` run before reload.
- [ ] Access verified from a *new* session before the original was closed.
- [ ] Password, root and non-allowed users all refused, with server-side log evidence.
- [ ] Diff and rollback plan written.
- [ ] Authorised key access still works at the end.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Change had no effect | Another drop-in file sorts later | `ls /etc/ssh/sshd_config.d/`; renumber your file |
| Locked out | Hardened before keys were proven | Console or snapshot restore |
| `sshd -t` error | Directive name or value invalid | Read the message; fix before reload |
| `AllowUsers` blocks the key user | Name mismatch (`student` vs `student@host`) | Use the bare account name |
| `reload` fails | Unit name differs (`ssh` vs `sshd`) | `systemctl list-units | grep -i ssh` |
| No log entries for refusals | Wrong unit or time window | `journalctl -u ssh --since "15 min ago"` |

## Cleanup and restoration

```bash
# Option A — keep hardening for CYB-206 (recommended)
ssh lab-ubuntu 'sudo sshd -T | grep -i passwordauthentication'

# Option B — restore the baseline
ssh lab-ubuntu 'sudo rm -f /etc/ssh/sshd_config.d/10-lab-hardening.conf && sudo sshd -t && sudo systemctl reload ssh'
ssh lab-ubuntu 'sudo sshd -T | grep -i passwordauthentication'    # expect: yes

pgrep -a tcpdump || echo "no capture running"
```

## Questions and extension challenges

1. Why is a drop-in file safer to manage than editing `sshd_config` in place?
2. What did `sshd -t` catch that reading the file could not?
3. Which of the six hardening directives reduces risk the most, and why?
4. Write the refusal you generated in Step 6 as a detection rule: what would you alert on?
5. Harden the same way on a Windows host using `OpenSSH Server`. Which directives are unavailable there?

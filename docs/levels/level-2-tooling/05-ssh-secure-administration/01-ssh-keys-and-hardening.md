---
title: "SSH Keys, Configuration and Hardening"
description: "How SSH authentication actually works, which sshd directives matter, and how to change them without locking yourself out."
module_code: CYB-205
level: 2
kind: lesson
prerequisites: [CYB-203]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [ssh, sshd, ed25519, hardening]
---

# SSH Keys, Configuration and Hardening

## Learning objectives

1. Explain public-key authentication as a challenge-response, not a password transfer.
2. Generate, protect and deploy an Ed25519 key pair.
3. Read the client config and the server config and map each directive to a risk.
4. Harden `sshd` incrementally, verifying access after every change.
5. Transfer files safely and explain when `rsync` beats `scp`.
6. Describe port forwarding and its security implications.

## Prerequisites

[CYB-203](../03-host-discovery-and-enumeration/index.md). You should already have found `sshd` on port 22 during
enumeration.

---

## 1. What actually happens

```
Client                                          Server
  |-- TCP connect :22 --------------------------->|
  |<------------------ banner: SSH-2.0-OpenSSH --|
  |-- key exchange (curve25519) ---------------->|   session keys derived
  |<---------------- server host key + sig ------|   client checks known_hosts
  |-- userauth: publickey (offer key id) ------->|
  |<---------------- challenge (sign this) ------|
  |-- signature over session data -------------->|   server verifies with public key
  |<---------------- success --------------------|
```

Three facts worth holding onto:

- The **private key never leaves the client**. The server holds only the public half in `authorized_keys`.
- The **host key** is the server proving its own identity, which is what `known_hosts` remembers. A changed host
  key is either a rebuild or a man-in-the-middle — you cannot tell which from the message alone.
- The signature covers **this session**, so a captured login cannot be replayed.

## 2. Keys

```bash
ssh-keygen -t ed25519 -a 100 -C "lab-kali-$(date -u +%Y%m%d)"
```

| Flag | Meaning |
| --- | --- |
| `-t ed25519` | Modern curve, short keys, fast verification |
| `-a 100` | KDF rounds for the passphrase — slows offline guessing |
| `-C` | Comment, for identifying the key later |

Protect it:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

An unencrypted private key on a shared host is a credential in the clear. Always set a passphrase and use
`ssh-agent` for convenience:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Deploy the public half:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub student@192.0.2.20
```

This appends to `~/.ssh/authorized_keys` on the target. Understand that a file, not a database, is what authorises
you — which is why file permissions there matter (`700`/`600`), and why `StrictModes yes` exists.

## 3. known_hosts

```bash
ssh-keygen -F 192.0.2.20        # look up a host key
ssh-keygen -R 192.0.2.20        # remove after a legitimate rebuild
ssh-keyscan -t ed25519 192.0.2.20 >> ~/.ssh/known_hosts   # only if you can verify out of band
```

!!! danger "Do not blindly accept a changed host key"
    `StrictHostKeyChecking=no` and habitually answering "yes" to the warning are how man-in-the-middle attacks
    succeed. Verify the fingerprint through a second channel before removing an entry.

## 4. Client configuration

`~/.ssh/config` turns long command lines into names:

```sshconfig
Host lab-ubuntu
    HostName 192.0.2.20
    User student
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30

Host *
    AddKeysToAgent yes
    HashKnownHosts yes
```

`IdentitiesOnly yes` prevents the agent from offering every key it holds — servers often reject after too many
failed offers (`Too many authentication failures`).

## 5. File transfer

| Tool | Good for | Note |
| --- | --- | --- |
| `scp` | One or two files | Simple; legacy protocol under the hood |
| `sftp` | Interactive browsing | Good for ad-hoc work |
| `rsync -avz` | Directories, re-runs | Resumable, only transfers changes |

```bash
scp report.md student@192.0.2.20:/home/student/
rsync -av --progress ~/lab205/evidence/ student@192.0.2.20:/home/student/evidence/
```

Beware the trailing slash in `rsync`: `dir/` copies contents, `dir` copies the directory itself.

## 6. Hardening sshd, incrementally

Read the effective configuration — comments in the file are not proof of what is active:

```bash
sudo sshd -T | grep -Ei 'permitrootlogin|passwordauth|pubkeyauth|x11|maxauthtries|allowusers|port'
```

Then a defensible baseline:

```conf
# /etc/ssh/sshd_config.d/10-lab-hardening.conf
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
```

| Directive | Risk it reduces |
| --- | --- |
| `PermitRootLogin no` | Direct brute force against a known-privileged account |
| `PasswordAuthentication no` | Online password guessing entirely |
| `KbdInteractiveAuthentication no` | Bypass of the above via PAM prompts |
| `MaxAuthTries 3` | Key-space probing |
| `AllowUsers` | Exposure to accounts you forgot existed |
| `X11Forwarding no` | Unneeded attack surface |

**Validate before restarting:**

```bash
sudo sshd -t && echo "syntax OK"
```

**Restart without losing your session:** keep the current shell open, start a *new* session to test, and only then
close the old one. If the new session fails, the old one is your way back.

```bash
sudo systemctl restart ssh      # Debian/Ubuntu service name
# Kali uses: sudo systemctl restart ssh
```

In Docker/containers the service may be `sshd` or absent entirely — check `systemctl list-units | grep -i ssh`.

## 7. Port forwarding, briefly

```bash
# Local forward: reach a remote-internal service through the SSH host
ssh -L 8080:127.0.0.1:8000 student@192.0.2.20
# then browse http://127.0.0.1:8080
```

Useful and legitimate — and a common exfiltration and pivot mechanism when abused. Detection focuses on
unexpected long-lived SSH sessions and unusual forwarded destinations. Note that `AllowTcpForwarding no` closes
this off entirely when it is not needed.

## 8. Logs you will read later

| Log | Contains |
| --- | --- |
| `/var/log/auth.log` (Debian) | Accepted/failed auth, invalid users, disconnects |
| `journalctl -u ssh` | Same via systemd |
| `last`, `lastb` | Successful and failed login records |

```bash
sudo journalctl -u ssh --since "1 hour ago" | grep -E 'Failed|Accepted|Invalid'
```

---

## Practical exercises

### Exercise 1 — Prove the key is what authenticates (10 minutes)

Connect with `ssh -v`, capture the line showing `Offering public key` and `Server accepts key`. Then temporarily
move `authorized_keys` aside and observe the failure mode.

### Exercise 2 — Enumerate what the server permits (10 minutes)

Run `sudo sshd -T` and list every directive whose value differs from the documented default. Explain two.

### Exercise 3 — Safe-change drill (15 minutes)

Take a snapshot. Set `MaxAuthTries 1`, reload, and confirm you can still log in with a correct key. Restore.

### Exercise 4 — Transfer comparison (10 minutes)

Copy a 5 MB file with `scp`, then again with `rsync -av --progress`. Run `rsync` a second time and explain the
difference in transfer volume.

## Expected observations

- `ssh -v` shows the key offer and acceptance.
- `sshd -T` output frequently contradicts the comments in the config file.
- With `PasswordAuthentication no`, a wrong-key login fails without ever prompting for a password.
- `rsync` on an unchanged tree transfers almost nothing.

## Common mistakes and troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Permission denied (publickey)` | Key not in `authorized_keys`, or permissions too open | `chmod 700 ~/.ssh; chmod 600 authorized_keys` |
| `Too many authentication failures` | Agent offering many keys | `IdentitiesOnly yes` in client config |
| Locked out after hardening | `PasswordAuthentication no` before keys worked | Console access or snapshot restore |
| `sshd: no hostkeys available` | Host keys missing after image copy | `sudo ssh-keygen -A` |
| Changed host key warning | VM rebuilt or cloned | Verify fingerprint, then `ssh-keygen -R` |
| Config ignored | Directive in the wrong `Include` order | Later files win; check `sshd -T` |

## Review questions

1. Why does the private key never need to travel to the server?
2. What does `known_hosts` protect against, and what does it not?
3. Why is `PasswordAuthentication no` more valuable than a long password policy?
4. What does `sshd -t` check that reading the file does not?
5. Why should you keep the old session open during a config change?
6. When is port forwarding a finding rather than a feature?

## Knowledge check

1. Which command shows the effective `sshd` configuration?
2. Which directive disables password logins?
3. What do the permissions on `~/.ssh` need to be, and why?
4. What does `IdentitiesOnly yes` prevent?
5. What does a changed host key warning mean, and what is the correct response?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments.)*

## Summary

- Keys authenticate by signature; the private half never travels.
- `known_hosts` is trust-on-first-use — verify before you reset it.
- Read effective config with `sshd -T`; harden in small verified steps.
- Keep a session open, validate with `sshd -t`, test before closing.
- `rsync` is the better default for directories; `scp` is fine for one file.

## Next lesson

[CYB-206 · Host Inspection and Hardening Assessment](../06-host-inspection-and-hardening/index.md) — turning
configuration review into a documented assessment.

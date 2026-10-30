---
title: "LAB-205-01 · Key-Based Authentication End to End"
description: "Generate a key pair, deploy the public half, prove the private key never travels, and audit the resulting access path."
module_code: CYB-205
level: 2
kind: lab
prerequisites: [CYB-203]
estimated_minutes: 240
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-205-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [ssh, keys, ssh-agent]
---

# LAB-205-01 · Key-Based Authentication End to End

| | |
| --- | --- |
| **Level** | 2 |
| **Time** | 4 hours |
| **Prerequisites** | [CYB-203](../03-host-discovery-and-enumeration/index.md) |
| **Lab hosts** | `lab-kali` 192.0.2.10 (client), `lab-ubuntu` 192.0.2.20 (server) |
| **Network** | host-only, labelled `lab-only-192.0.2.0` |

## Scenario and background

You have password access to a lab server and have been told to move to keys before the service leaves the lab
network. Before changing anything on the server, you must prove the key path works — and be able to explain the
authentication sequence from evidence rather than memory.

## Learning objectives

1. Generate a passphrase-protected Ed25519 key pair with correct file permissions.
2. Deploy the public key and authenticate without a password.
3. Demonstrate from client and server evidence that key-based auth succeeded.
4. Use `ssh-agent` and the client config to make the workflow usable.
5. Explain what `known_hosts` is protecting and when it is safe to clear.

## Required tools and versions

| Tool | Version | Install |
| --- | --- | --- |
| `openssh-client` | 9.x | `sudo apt install openssh-client` |
| `openssh-server` (on lab-ubuntu) | 9.x | `sudo apt install openssh-server` |
| `ssh-agent` | bundled | — |

## Setup

On `lab-ubuntu`:

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh --no-pager | head -5
sudo useradd -m -s /bin/bash student 2>/dev/null || true
sudo passwd student          # set a temporary lab password
```

On `lab-kali`:

```bash
mkdir -p ~/lab205 && cd ~/lab205
ssh -o PreferredAuthentications=password student@192.0.2.20 'hostname; id'   # confirm password login works first
```

!!! danger "Always confirm an existing access path first"
    Establish the password login *before* you deploy keys or change any server setting. It is your way back if the
    key path turns out to be wrong.

## Target addresses and lab topology

```
lab-kali 192.0.2.10  --- host-only lab-only-192.0.2.0 ---  lab-ubuntu 192.0.2.20
        (client, key holder)                              (sshd, tcp/22, account: student)
```

`sshd` listens on the lab interface only while you are working; the lab network is not reachable from outside the
host machine.

## Numbered commands and actions

### Step 1 — Snapshot

Take a VM snapshot of `lab-ubuntu` named `before-205`. Record the snapshot name in your notes.

### Step 2 — Generate the key

```bash
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519_lab -C "lab205-kali-$(date -u +%Y%m%d)"
```

Set a passphrase when prompted (not empty). Then:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519_lab*
ls -l ~/.ssh/
```

**Expected:** `-rw-------` on the private key, `-rw-r--r--` on the `.pub`.

### Step 3 — Deploy the public half

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_lab.pub student@192.0.2.20
```

**Expected:** a final line resembling `Number of key(s) added: 1`.

Verify on the server what was actually written:

```bash
ssh student@192.0.2.20 'ls -la ~/.ssh; echo "---"; cat ~/.ssh/authorized_keys'
```

**Expected:** `authorized_keys` contains one line beginning `ssh-ed25519` and ending with your comment. Note the
permissions: if `authorized_keys` is group- or world-writable, `StrictModes` will refuse the key.

### Step 4 — Prove the sequence

```bash
ssh -v -i ~/.ssh/id_ed25519_lab student@192.0.2.20 'echo logged-in-as $(whoami)' 2>&1 \
  | grep -E 'Offering public key|Server accepts key|Authenticated to|Authentications that can continue'
```

**Expected:** `Offering public key`, `Server accepts key`, `Authenticated to 192.0.2.20`.

Record the two `Authentications that can continue` lines — they show which methods remain available, and are what
you will compare after hardening in LAB-205-02.

### Step 5 — Negative control

```bash
# A key the server does not know
ssh -o IdentitiesOnly=yes -i /dev/null student@192.0.2.20 'echo should-not-print'
```

**Expected:** `Permission denied (publickey,password)` — the server offers only what it is configured for.

### Step 6 — Make it usable

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_lab
ssh-add -l
```

Add to `~/.ssh/config`:

```sshconfig
Host lab-ubuntu
    HostName 192.0.2.20
    User student
    IdentityFile ~/.ssh/id_ed25519_lab
    IdentitiesOnly yes
    ServerAliveInterval 30
```

Then confirm the short form works:

```bash
ssh lab-ubuntu 'uptime'
```

**Expected:** output with no key or user arguments supplied.

### Step 7 — known_hosts

```bash
ssh-keygen -F 192.0.2.20
ssh-keygen -lf ~/.ssh/known_hosts | head -3
```

**Expected:** the host entry is found and its fingerprint printed.

Then demonstrate the failure mode safely:

```bash
# On lab-ubuntu, view the server's own fingerprint
ssh lab-ubuntu 'ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub'

# On lab-kali, compare — these must match
ssh-keygen -lf ~/.ssh/known_hosts | grep 192.0.2.20
```

**Expected:** identical fingerprints. Write one sentence in your notes explaining why you would only run
`ssh-keygen -R` after verifying this out of band.

### Step 8 — Record the access path

Create `~/lab205/ssh-access-note.md` containing:

| Item | Value |
| --- | --- |
| Server | 192.0.2.20:22 |
| Account | student |
| Method | publickey (ed25519) |
| Key path (client) | `~/.ssh/id_ed25519_lab` |
| Authorised on server | `~/.ssh/authorized_keys` |
| Host key fingerprint | *(from Step 7)* |
| Password auth still enabled? | Yes (unchanged) |

## Evidence to collect

- `ssh -v` excerpt showing key offer and acceptance.
- `authorized_keys` contents and permissions.
- `ssh-add -l` output.
- Host key fingerprints from both sides.
- `ssh-access-note.md`.

## Verification criteria

- [ ] Snapshot `before-205` exists.
- [ ] Private key is `600`, `.ssh` is `700`, and it has a passphrase.
- [ ] Password login was proven to work *before* the key was deployed.
- [ ] `ssh -v` shows `Offering public key` followed by `Server accepts key`.
- [ ] An unknown key is rejected, proving the accepted key is doing the work.
- [ ] `ssh lab-ubuntu` works via the config file alone.
- [ ] Host key fingerprints match between client and server.
- [ ] Access note completed, including that password auth is still enabled.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Still prompted for a password | Wrong key offered, or `authorized_keys` perms too open | Force `-i`, check `chmod 600 authorized_keys` |
| `Permission denied (publickey)` | Key not deployed, or wrong user | `ssh-copy-id` again; check `~/.ssh` ownership on server |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | VM cloned/rebuilt | Compare fingerprints first; then `ssh-keygen -R` |
| `Too many authentication failures` | Agent offering many keys | `IdentitiesOnly yes` |
| `Authentication refused: bad ownership` | Home dir or `.ssh` group-writable | Fix ownership (`chown -R student:student`) |
| `Connection refused` | `sshd` not running | `sudo systemctl start ssh` on lab-ubuntu |

## Cleanup and restoration

```bash
# Leave the key-based access in place for LAB-205-02; remove the temporary password at the end of the level.
ssh lab-ubuntu 'wc -l ~/.ssh/authorized_keys'
# Keep the snapshot until CYB-205 is finished, then delete it.
pgrep -a ssh-agent >/dev/null && echo "agent running (expected)"
```

## Questions and extension challenges

1. What exactly does the server store to authorise your key, and where?
2. Why does `ssh -v` log *offering* and *accepting* as separate events?
3. What would an attacker need in order to impersonate `lab-ubuntu` to your client?
4. Add `-o IdentitiesOnly=yes -o PasswordAuthentication=no` and describe the failure mode if the key is missing.
5. Generate an RSA-3072 key alongside the Ed25519 one. Compare handshake and authentication timings.

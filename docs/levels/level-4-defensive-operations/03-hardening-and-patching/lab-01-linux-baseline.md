---
title: "LAB-403-01 · Linux Baseline Assessment and Verified Remediation"
description: "Assess Ubuntu 24.04 against a CIS Level 1 server profile, remediate five findings with proof, and record one exception you can defend."
module_code: CYB-403
level: 4
kind: lab
prerequisites: [CYB-403]
estimated_minutes: 180
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-403-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [openscap, cis-benchmark, lynis, auditd, ssh, remediation]
---

# LAB-403-01 · Linux Baseline Assessment and Verified Remediation

## Scenario and background

You have inherited `lab-ubuntu`, a host built for convenience rather than security. Before it goes into a monitored
network segment, it must be assessed against a published baseline, brought into line where that is sensible, and
documented where it is not.

You will produce the artefact a real review asks for: a dated assessment, a set of verified changes, and an exception
with an owner and a review date.

## Learning objectives

1. Run an OpenSCAP evaluation against a CIS Level 1 server profile on Ubuntu 24.04.
2. Summarise ARF results by outcome and severity, and distinguish `fail` from `notchecked`.
3. Triage five failures into apply/adapt/compensate/accept decisions.
4. Remediate with before/after state evidence, one control at a time.
5. Re-assess and quantify the delta without claiming more than the scan supports.

## Required tools and versions

| Tool | Version | Purpose |
| --- | --- | --- |
| Ubuntu Server | 24.04 LTS | Target |
| OpenSCAP | 1.4.6 | `oscap` scanner |
| SCAP Security Guide | 0.1.82 | Ubuntu 24.04 content, CIS profiles |
| Lynis | 3.1.7 | Second-opinion audit |
| Python | 3.12 | Result summarisation |

`auditd` 3.1.x ships with Ubuntu 24.04 and is used for one of the controls.

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab-ubuntu` only.
    **Targets you must not use:** any other host, and no external scanning service.

    **This lab changes the host.** Snapshot first. Keep the VirtualBox console window open throughout: if you disable
    an SSH setting while connected over SSH with password authentication, the console is your way back in.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The host is assumed reachable from a monitored internal segment by authenticated users. The relevant threats are
credential theft from a weakly configured SSH service, unauthorised local privilege escalation through loose file
permissions or unneeded services, and loss of accountability because authentication and configuration changes are not
logged. Everything in this lab targets those three.

## Environment

| Host | Role | Address |
| --- | --- | --- |
| `lab-ubuntu` | Target | 192.0.2.20 |
| `lab-win` | Not used | 192.0.2.40 |
| Your workstation | Analyst, SSH client | host-only adapter |

## Before you start

1. Snapshot `pre-lab-403-01`.
2. Attach NAT, install packages, then detach NAT and confirm `ping -c1 8.8.8.8` fails.
3. Create the workspace:

```bash
mkdir -p ~/lab403/evidence
cd ~/lab403
```

## Procedure

### 1. Install the scanner and the content

```bash
sudo apt update
sudo apt install -y openscap-scanner ssg-base ssg-debderived lynis python3
oscap --version | head -3
ls /usr/share/xml/scap/ssg/content/ | grep -i ubuntu
```

**Expected:** `oscap` reports 1.4.x, and a data stream named like `ssg-ubuntu2404-ds.xml` is present.

If the distribution package is older than the content you want, install the release archive from ComplianceAsCode
instead and point `oscap` at the extracted data stream. Record whichever you used — version and source are part of
the result.

```bash
oscap info /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml | sed -n '1,25p'
oscap info --profiles /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml | grep -i 'cis_level1_server'
```

**Expected:** a profile ID of the form `xccdf_org.ssgproject.content_profile_cis_level1_server`. Use exactly the ID
your content prints — do not copy one from a blog post.

### 2. Baseline assessment (read-only)

```bash
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
  --results ~/lab403/evidence/baseline-results.xml \
  --report  ~/lab403/evidence/baseline-report.html \
  /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml > ~/lab403/evidence/baseline-stdout.txt 2>&1
echo "exit status: $?"
```

**Expected:** `exit status: 2` — at least one rule failed. This is normal; note it rather than treating it as a
scripting error. The HTML report is the readable view, the XML is the record.

Summarise the results:

```bash
python3 - <<'PY'
import collections, xml.etree.ElementTree as ET
tree = ET.parse('/home/student/lab403/evidence/baseline-results.xml')
counts, fails = collections.Counter(), []
for rr in tree.iter():
    if rr.tag.endswith('rule-result'):
        res = next((c for c in rr if c.tag.endswith('result')), None)
        if res is None:
            continue
        val = (res.text or '').strip()
        counts[val] += 1
        if val == 'fail':
            fails.append(rr.get('idref', ''))
print('counts:', dict(counts))
print('failing rules:', len(fails))
for f in fails[:15]:
    print(' ', f)
PY
```

**Expected:** a count per outcome, with `pass`, `fail`, and usually `notapplicable`/`notchecked`. Write the counts
into `evidence/baseline-summary.txt` with the profile ID and content version.

**Do not skip this question:** why is `notchecked` not a pass? Note your answer in the file.

### 3. Second opinion with Lynis

```bash
sudo lynis audit system --quick --no-colors 2>&1 | tee evidence/lynis-before.txt | tail -25
```

**Expected:** a hardening index, warnings, and suggestions. Record the index.

Find one item Lynis reports that the OpenSCAP run did not flag, and one item both flag. That comparison is the point:
the tools have different coverage, and neither is complete.

### 4. Triage five failures

Choose five failures spread across categories. A workable set, if your scan reports them:

| Category | Example rule | Decision to make |
| --- | --- | --- |
| SSH configuration | root login permitted, X11 forwarding enabled | Apply |
| Service minimisation | an unnecessary network service enabled at boot | Apply or adapt |
| Audit logging | `auditd` not installed or no identity rules | Apply |
| File permissions | loose mode on a sensitive file | Apply |
| Authentication policy | password authentication enabled | Accept for now, with a compensating control |

For each, fill one row in `evidence/triage.md`:

| Rule ID | Observed state | Decision | Why | Verification command |
| --- | --- | --- | --- | --- |

### 5. Remediate, one control at a time

Snapshot before each change group, and keep the console open.

**(a) SSH — disable root login and X11 forwarding**

```bash
sudo tee /etc/ssh/sshd_config.d/99-lab403.conf >/dev/null <<'EOF'
PermitRootLogin no
X11Forwarding no
EOF
sudo sshd -t && echo "syntax ok"
sudo systemctl reload ssh
sudo sshd -T | grep -E '^(permitrootlogin|x11forwarding)'
```

**Expected:** `permitrootlogin no` and `x11forwarding no` from `sshd -T` — the *effective* configuration, which is
what matters, regardless of what any single file says.

Open a new SSH session to confirm you can still log in before closing the old one.

**(b) Service minimisation**

```bash
systemctl list-unit-files --state=enabled --type=service | tee evidence/enabled-services.txt
sudo systemctl disable --now avahi-daemon.service 2>/dev/null || echo "avahi not installed"
systemctl is-enabled avahi-daemon.service; systemctl is-active avahi-daemon.service
```

**Expected:** `disabled` and `inactive` (or a "not installed" message, which is also a valid outcome — record it).
If your host runs something you are unsure about, leave it and record that decision instead of disabling it.

**(c) Audit rules for identity files**

```bash
sudo apt install -y auditd audispd-plugins
sudo systemctl enable --now auditd
sudo tee /etc/audit/rules.d/99-lab403.rules >/dev/null <<'EOF'
-w /etc/passwd -p wa -k identity
-w /etc/group  -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/hosts  -p wa -k hosts
EOF
sudo augenrules --load
sudo auditctl -l
```

**Expected:** the four rules listed by `auditctl -l`.

Prove they work by touching a file you can safely change:

```bash
echo "# lab403 test $(date -Is)" | sudo tee -a /etc/hosts >/dev/null
sudo ausearch -k hosts -ts recent | tail -5
sudo sed -i '/# lab403 test/d' /etc/hosts   # restore the original content
```

**Expected:** an `ausearch` record with `key="hosts"`, the writing process, and the timestamp. If `ausearch` returns
nothing, check that `auditd` is running before touching anything else.

**(d) File permissions**

```bash
stat -c '%a %U:%G %n' /etc/shadow /etc/gshadow /etc/passwd
sudo chmod 640 /etc/shadow /etc/gshadow
stat -c '%a %U:%G %n' /etc/shadow /etc/gshadow
```

**Expected:** modes tighten to `640`, ownership unchanged (`root:shadow` on Debian-family systems). Never change
ownership of these files as a "fix".

**(e) Kernel parameter**

```bash
echo 'kernel.dmesg_restrict = 1' | sudo tee /etc/sysctl.d/99-lab403.conf
sudo sysctl --system >/dev/null
sysctl kernel.dmesg_restrict
```

**Expected:** `kernel.dmesg_restrict = 1`, and it persists because it is in a file rather than set at runtime only.

### 6. Re-assess and measure the delta

```bash
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
  --results ~/lab403/evidence/after-results.xml \
  --report  ~/lab403/evidence/after-report.html \
  /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml > ~/lab403/evidence/after-stdout.txt 2>&1

sudo lynis audit system --quick --no-colors 2>&1 | tee evidence/lynis-after.txt | tail -12
```

Count the after-results with the same Python snippet, then build `evidence/delta.csv`:

```csv
outcome,before,after,delta
pass,NNN,NNN,+N
fail,NNN,NNN,-N
notchecked,NNN,NNN,0
```

Then answer in `evidence/notes.md`:

1. Which five rules changed state, and did each match the control you applied?
2. Did any rule move from `pass` to `fail`? If so, what did your change break? (This happens — a tightened permission
   can fail a different rule.)
3. Did the Lynis index move? By how much, and does the movement match the changes?

**Honesty requirement:** the delta proves five rules changed. It does not prove the host is secure. Write that
sentence yourself, in your own words, in the notes.

### 7. Record one exception

`/etc/ssh/sshd_config.d/99-lab403.conf` leaves password authentication enabled. Write the exception:

| Field | Content |
| --- | --- |
| Rule | SSH password authentication disabled (CIS 5.2.x) |
| Reason | Key-based authentication is not yet enrolled for the lab account; disabling it now would lock out the only access path |
| Compensating control | Host-only network, no route from the lab segment to any other network, SSH reachable only from the analyst workstation |
| Owner | You (student) |
| Approved by | Self-approved for lab purposes; in production, the system owner |
| Review date | 30 days from today |
| Verification of compensation | `ip route` shows no default route to a production network; `ss -tlnp` shows SSH bound only to 192.0.2.20 |

## Evidence to collect

- `evidence/baseline-results.xml`, `baseline-report.html`, `baseline-summary.txt`
- `evidence/enabled-services.txt`
- `evidence/triage.md` — five rows with decisions and verification commands
- `evidence/after-results.xml`, `after-report.html`, `delta.csv`
- `evidence/lynis-before.txt`, `lynis-after.txt`
- `evidence/exception-register.md`
- `evidence/notes.md` — the three answers plus the honesty statement

## Verification

- [ ] Profile ID and content version recorded, copied from `oscap info`, not from memory.
- [ ] Baseline exit status of `2` explained rather than suppressed.
- [ ] Outcome counts include `notchecked`, and it is treated as a coverage gap.
- [ ] Five controls applied or explicitly decided, each with a query proving current state.
- [ ] `sshd -T` (not `sshd_config`) used to verify SSH settings, with a second session tested first.
- [ ] Audit rules loaded and demonstrated with a real event that was then reverted.
- [ ] Delta table shows before/after counts, and any regression is explained.
- [ ] Exception has an owner, a compensating control, and a future review date.

## Teardown and reset

```bash
sudo rm -f /etc/ssh/sshd_config.d/99-lab403.conf /etc/sysctl.d/99-lab403.conf /etc/audit/rules.d/99-lab403.rules
sudo augenrules --load
sudo systemctl reload ssh
sudo sysctl --system >/dev/null
```

Then revert `pre-lab-403-01` if you want the original host back. Keep `~/lab403/evidence` — copy it to your
workstation before reverting, because the snapshot does not contain it.

## Reflection

1. You verified SSH with `sshd -T`. Why is that stronger evidence than `grep PermitRootLogin /etc/ssh/sshd_config`?
2. Your exception leaves password authentication on. Name one control that would let you close the exception, and the
   order of operations required to do it without locking yourself out.
3. The scan improved by five rules. What are two things the scan cannot tell you about this host's security?
4. If a colleague applied the same profile to a developer workstation, which of your five changes would you expect to
   cause friction, and what would you do instead?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Assessment | Scan run without recording profile/version | Profile and content version recorded | ARF kept, outcomes explained, `notchecked` treated as a gap |
| Remediation | Changes applied without verification | State queried after each change | Effective configuration verified, regressions looked for and explained |
| Evidence | Screenshots only | Before/after results and delta | Delta plus honest limits and a demonstrated audit event |
| Judgement | Everything applied blindly | Five decisions recorded | Exception defensible, with compensation verified and a review date |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `oscap info` cannot find the data stream | Content package not installed, or different filename | `ls /usr/share/xml/scap/ssg/content/`; use the actual path |
| Profile ID not found | Content version uses a different profile name | `oscap info --profiles <file>` and pick the CIS Level 1 server entry |
| Evaluation aborts with an OVAL error | Missing package or unsupported platform detail | Read the message; add `--skip-valid` only to diagnose, never for the record |
| `sshd -T` says `Missing privilege separation directory` | `/run/sshd` absent after a container-like boot | `sudo mkdir -p /run/sshd` |
| `ausearch` returns nothing | `auditd` not running, or rules not loaded | `systemctl status auditd`; `auditctl -l`; `augenrules --load` |
| Locked out of SSH | Password auth disabled before keys worked | Use the VirtualBox console; revert the drop-in file |
| Lynis index changes unexpectedly | Different checks after package installation | Compare the suggestions lists, not only the number |

## References

1. OpenSCAP 1.4.6 release (22 October 2026). <https://github.com/OpenSCAP/openscap/releases> Accessed 2026-10-29.
2. ComplianceAsCode/content 0.1.82 (1 September 2026) — Ubuntu 24.04 profiles.
   <https://github.com/ComplianceAsCode/content/releases> Accessed 2026-10-29.
3. CIS Benchmarks — free PDFs for non-commercial use via the CIS download form.
   <https://learn.cisecurity.org/benchmarks> Accessed 2026-10-29.
4. Lynis 3.1.7 (25 June 2026). <https://github.com/CISOfy/lynis/releases> Accessed 2026-10-29.
5. `auditd` — `auditctl(8)`, `augenrules(8)`, `ausearch(8)` man pages. Accessed 2026-10-29.
6. OpenSSH — `sshd_config(5)` and `sshd(8)` (`-T` extended test mode). Accessed 2026-10-29.

---
title: "LAB-201-01 · Prepare and Verify a Kali VM"
description: "Import or install Kali, secure the default account, verify integrity of the download, install the required tools, and snapshot a baseline."
module_code: CYB-201
level: 2
kind: lab
prerequisites: [CYB-201]
estimated_minutes: 120
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-201-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [kali, virtualization, setup]
---

# LAB-201-01 · Prepare and Verify a Kali VM

## Prerequisites

Level 1 complete. A hypervisor installed with virtualization enabled in your firmware, the Kali Linux
installer image (or the pre-built VirtualBox image) for the current release, and about 60 GB of free disk.
Nothing else needs to be running for this lab.

## Scenario and background

You have been asked to stand up an analyst workstation for a series of internal lab exercises. Before any
tool is used, the workstation must be trustworthy: the image verified, the default account secured, the
system updated, and a known-good snapshot taken so every later lab can be reset in minutes.

A compromised or misconfigured analyst host invalidates every result you produce from it, which is why this
lab exists before any scanning.

## Learning objectives

By the end of this lab you can:

1. Verify a downloaded Kali image against its published hash before importing it.
2. Import or install Kali with the sizing this course expects.
3. Secure the default account and confirm the change.
4. Install and version-check the tools used across Level 2.
5. Create a baseline snapshot and prove that a revert restores a working system.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Hypervisor | VirtualBox 7.0.x or VMware Workstation/Fusion | Host-only networking support required |
| Kali Linux | 2024.x or later (rolling) | Pre-built VM image or installer ISO |
| `sha256sum` | coreutils | On the host, to verify the download |
| `passwd`, `apt`, `systemctl` | in Kali | Standard |

## Setup

1. Download Kali from the official site: <https://www.kali.org/get-kali/>.
2. Download the corresponding hash file if the site publishes one separately, or copy the published value.

```bash
# On the host, in the download directory
sha256sum Kali-Linux-*.7z          # filename varies by release
```

**Interpretation:** compare the printed value character by character with the published hash for that exact
file. A mismatch means a corrupted or tampered download — delete it and download again. Do not "continue
anyway"; a verified image is the whole point of this step.

## Target addresses and lab topology

```
Host machine
└── lab-kali  192.0.2.10/24  (host-only adapter; no gateway)
```

No target host is required for this lab. Networking is configured in LAB-201-02.

## Numbered commands and actions

### 1. Create the VM

In the hypervisor: New → name `lab-kali` → Linux / Debian (64-bit) → 4096 MB RAM → 2 vCPU → 25 GB disk.
For a pre-built image, use Import/Open and then adjust resources to match.

### 2. Boot and secure the account

```bash
whoami
passwd
```

`whoami` should return your user (`kali` on current images). `passwd` prompts for the current password, then
the new one twice. Choose a unique password and store it in your password manager — never in the lab notes.

**Why:** pre-built images ship with a publicly documented default credential. Leaving it unchanged is
equivalent to leaving a router on its factory password.

### 3. Update the system

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
sudo reboot
```

`apt update` refreshes package metadata; `full-upgrade` installs upgrades including kernel changes;
`autoremove` clears obsolete dependencies. A rolling distribution can require a reboot after a kernel update —
reboot before snapshotting so the snapshot is a working state.

### 4. Confirm the Level 2 toolset

```bash
for t in nmap tcpdump tshark wireshark nc python3 git ssh lynis openssl; do
  printf '%-9s ' "$t"
  if command -v "$t" >/dev/null 2>&1; then "$t" --version 2>&1 | head -1; else echo "MISSING"; fi
done
```

Install anything missing, using Kali's metapackages rather than guessing:

```bash
sudo apt install -y kali-tools-information-gathering kali-tools-sniffing-spoofing
# Individual tools if needed:
sudo apt install -y nmap tcpdump wireshark tshark netcat-traditional lynis python3 git openssh-client
```

**Why metapackages:** they keep related tools consistent with the distribution, and they are what Kali
maintains. Installing random `.deb` files from the internet is how analyst machines get compromised.

### 5. Record the baseline

```bash
mkdir -p ~/lab/level-2/lab-201/evidence
{
  echo "host: $(hostname)"; echo "date: $(date -Is)"
  cat /etc/os-release | head -2; uname -r
  for t in nmap tcpdump tshark nc python3 git ssh lynis; do
    printf '%-9s ' "$t"; command -v "$t" >/dev/null && "$t" --version 2>&1 | head -1 || echo MISSING
  done
} | tee ~/lab/level-2/lab-201/evidence/tooling-baseline.txt
```

### 6. Snapshot and prove the revert works

Power off, take a snapshot named `kali-baseline`, power on. Then:

```bash
touch /tmp/breakme
sudo systemctl stop ssh 2>/dev/null || true
```

Power off, revert to `kali-baseline`, power on, and confirm:

```bash
ls /tmp/breakme 2>/dev/null || echo "reverted: file gone"
```

**Expected:** `reverted: file gone`. You have just proved the reset mechanism that every later lab depends on.

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `apt full-upgrade` | Upgrades packages, allowing dependency changes | Keeps a rolling release consistent |
| `-y` | Assume yes | Non-interactive, reproducible |
| `autoremove` | Removes unused dependencies | Smaller snapshot, fewer surprises |
| `command -v` | Prints a path if the command exists | Safer than `which`, and scriptable |
| `--version` | Tool version | Evidence for reproducibility |

## Expected observations

- The download hash matches the published value, or you re-downloaded until it did.
- `whoami` returns a non-root user, and the new password works after reboot.
- `apt full-upgrade` completes without unmet dependencies.
- Every Level 2 tool reports a version; none is `MISSING`.
- `tooling-baseline.txt` contains host, OS, kernel, and each tool version.
- Reverting the snapshot removed the test file.

## Verification criteria

- [ ] Hash verified and recorded (paste the value and the published value side by side).
- [ ] Default password changed; login succeeds after reboot.
- [ ] `tooling-baseline.txt` saved with all tools present.
- [ ] Snapshot `kali-baseline` exists.
- [ ] Revert test passed (`reverted: file gone`).

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Import fails with "unsupported format" | Wrong archive extraction (`.7z` not unpacked) | Extract with `7z x` first, then import the `.vbox`/`.vmx` |
| `apt update` fails with 404s | Rolling release moved; stale lists | `sudo apt clean && sudo apt update` |
| `wireshark` missing but `tshark` present | Minimal image | `sudo apt install -y wireshark` (GUI needs a desktop session) |
| `nc` behaves differently than expected | Two netcat variants installed | `update-alternatives --config nc`, or use `nc.traditional` explicitly |
| Snapshot revert leaves the VM unbootable | Snapshot taken while running with pending writes | Snapshot with the VM powered off |
| Guest additions/shared folders missing | Image built for a different hypervisor | Install `virtualbox-guest-utils` or use the matching image |

## Cleanup and restoration

This lab's end state is the required starting point for the rest of the level, so **do not remove it**. To
reset later:

```bash
# In the hypervisor: power off, revert to kali-baseline, power on
```

Do not delete `~/lab/level-2/lab-201/evidence/` — it is the environment record used by later labs.

## Questions and extension challenges

1. Why is verifying a download hash more meaningful than trusting the site's TLS padlock alone?
2. What would a `full-upgrade` on a rolling release do to a lab that depends on a specific tool version, and
   how would you guard against it? *(Hint: snapshots, pinned packages, documented versions.)*
3. **Extension:** install Kali from the ISO instead of the image, and compare the toolset differences. Record
   which tools you had to install manually.
4. **Extension:** create a second snapshot after installing extra tools, and explain when you would revert to
   each.

## Related

- [Preparing the Analyst Environment](01-lab-environment.md)
- [LAB-201-02 · Configure Host-Only Networking](lab-02-host-only-network.md)
- [Lab Safety Guide](../../../start-here/lab-safety.md)

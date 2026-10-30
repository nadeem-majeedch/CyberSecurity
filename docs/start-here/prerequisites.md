# Prerequisites and Setup

This page tells you whether you are ready to start, what to install, and in what order. Do the
software setup **once, properly** — a broken lab environment is the most common reason learners stall
in the first two weeks.

---

## 1. Knowledge self-check

No prior security knowledge is assumed. These are the only expectations, all of which can be learned
in a few evenings:

| Can you… | If not |
| --- | --- |
| Create, move, rename, and delete files in a file manager or terminal? | Any beginner Linux tutorial covers this in an hour |
| Open a terminal and type a command you were given, exactly? | Practise with `pwd`, `ls`, `cd` on any system |
| Install software from an official website? | — (you will do this below) |
| Follow multi-step written instructions without skipping ahead? | This is the single most predictive skill in the course |
| Read English technical prose? | The course is written in English; glossary entries define the jargon |
| Do basic arithmetic (powers of two help)? | Subnetting in Level 1 revises what you need |

**Helpful but not required:** any programming experience (Python is taught from basics in CYB-203),
prior networking study, or IT support experience.

**Not assumed at all:** Linux, Windows administration, scripting, cryptography, or any security tool.

---

## 2. Hardware requirements

Virtual machines are the core of this course, so hardware matters more than usual.

| Component | Minimum | Recommended | Notes |
| --- | --- | --- | --- |
| RAM | 8 GB | 16 GB | Two VMs at once: ~2 GB each plus host overhead |
| Free disk | 60 GB | 100 GB | Snapshots multiply disk use; thin provisioning helps |
| CPU | 64-bit, 2 cores | 4+ cores | Virtualization (VT-x/AMD-V) must be **enabled in firmware** |
| Display | 1366×768 | 1920×1080 | Terminal output and browser devtools need width |
| Network | Any | Wired/stable | Some labs work fully offline; updates need a connection |

**On constrained hardware:** run one VM at a time, prefer Ubuntu Server (no GUI) over desktop images,
and use lightweight desktop environments. Everything in Levels 1–2 can be completed on 8 GB with
patience.

---

## 3. Software you will install

All of it is free. Versions are pinned because instructions are written and verified against them.

| Software | Purpose | Version used in the course | Cost |
| --- | --- | --- | --- |
| VirtualBox (or VMware Workstation Player) | Hypervisor for lab VMs | VirtualBox 7.0.x | Free |
| Ubuntu Server LTS | Primary Linux lab host | 22.04.x LTS (24.04 acceptable) | Free |
| Windows 11 Enterprise Evaluation **or** Windows 10/11 VM | Windows lab host for Levels 1 and 4 | Current evaluation image | Free, time-limited |
| Kali Linux | Tool-focused distribution, introduced in Level 2 | 2024.x+ rolling | Free |
| DVWA | Deliberately vulnerable web app | Latest stable, PHP/MySQL | Free (open source) |
| OWASP Juice Shop | Modern vulnerable web app | Latest LTS release | Free (MIT) |
| Python 3 | Scripting, tooling | 3.10+ | Free |
| Wireshark + tcpdump | Packet capture and analysis | 4.x | Free |
| A text editor | Notes, scripts, configuration | Any (`nano`, VS Code, Notepad++) | Free |

**Optional, later levels:** Wazuh or ELK (SIEM, Level 4), Suricata/Zeek (Level 4), Autopsy and
Volatility (Level 4), REMnux and FLARE VM (Level 5), LocalStack or CloudGoat-style lab (Level 5).

Do **not** install everything at once. Install what the current module needs; a half-configured stack
of tools is harder to debug than no tools.

---

## 4. Installation order (do it in this sequence)

### Step 1 — Enable virtualization

In firmware/BIOS, enable Intel VT-x or AMD-V. On Windows, confirm with Task Manager → Performance →
CPU → "Virtualization: Enabled". Without this, VMs will be unusably slow or refuse to start.

### Step 2 — Install the hypervisor

Install VirtualBox (or VMware Player), then the Extension Pack if prompted. Create a `VMs` directory
with enough free space, and keep VM images out of cloud-synced folders — sync clients corrupt disk
images mid-write.

### Step 3 — Create the base Linux VM

- 2 vCPU, 2048 MB RAM, 20 GB disk.
- Ubuntu Server LTS ISO, minimal install, no snaps required.
- Create a normal user; do not work as `root` day to day.
- Install OpenSSH server so you can practise remote administration inside the lab.

### Step 4 — Take a clean snapshot

Name it `clean-base`. This snapshot is your reset button for the entire course. Take a new snapshot
before every lab and revert after.

### Step 5 — Configure isolated networking

For lab work, use **host-only** or **NAT** adapters — never bridged. Verify isolation:

```bash
# From the lab VM: this must FAIL (no route to the internet)
ping -c 2 8.8.8.8
```

If that succeeds, your adapter is bridged or NAT with internet access is misconfigured for the
exercise. Fix it before continuing — see the [Lab Safety Guide](lab-safety.md).

### Step 6 — Add the vulnerable applications

Install DVWA and Juice Shop **inside the lab VM**, bound to `localhost`. Full steps arrive with
Level 3; installing them now as an exercise builds the skills you need later.

### Step 7 — Prepare the Windows VM

Download the Windows evaluation image, install it as a VM, snapshot it as `win-clean`, and record its
build number. Level 1 uses it for basic administration; Level 4 hardens it.

### Step 8 — Record your environment

Write a short `lab-environment.md` of your own: host OS, hypervisor version, each VM's role, IP,
resources, snapshot names, and the date. You will need this for reproducibility and for reporting
problems.

---

## 5. Operating system notes

| Host OS | Notes |
| --- | --- |
| Windows 10/11 | Most straightforward: VirtualBox + Windows eval VM. Enable Hyper-V off if VirtualBox complains, or use VMware with Hyper-V on |
| macOS (Intel or Apple silicon) | VirtualBox is limited on Apple silicon; use VMware Fusion, UTM, or Parallels. Choose ARM64 Ubuntu images |
| Linux | Native virtualization support; kvm/qemu also works, but instructions assume a GUI hypervisor |

Cross-platform command differences are called out in lessons with tabs where they matter. Where a
lesson says "Linux", it means your Ubuntu VM, not your host.

---

## 6. Time and connectivity

- **Levels 1–2 can be completed offline** once images are downloaded; captures and sample data are
  included with the course.
- **Level 3** needs local web apps only — no internet at lab time.
- **Level 4** needs package installs for SIEM and IDS components.
- **Level 5** may need package installs, and cloud modules need a sandbox account with budget alerts.

Budget time for downloads once: roughly 15–25 GB of images and installers.

---

## 7. Before you start, confirm

- [ ] Virtualization is enabled and verified in Task Manager (or `lscpu` on Linux).
- [ ] Hypervisor installed; a VM boots and snapshots successfully.
- [ ] Ubuntu Server VM boots, you can log in as a normal user, and `sudo` works.
- [ ] `clean-base` snapshot exists.
- [ ] Isolation verified: the lab VM cannot reach the internet from the host-only adapter.
- [ ] Windows evaluation VM installed and snapshotted.
- [ ] A notes folder and an evidence folder exist for Level 1.
- [ ] You have read the [Lab Safety Guide](lab-safety.md) and the [Safety Policy](../policies/safety-policy.md).

If any box is unchecked, fix it now. Everything later assumes it.

---

## Related

- [Lab Safety Guide](lab-safety.md) — building and proving isolation
- [Troubleshooting](troubleshooting.md) — when a VM, network, or package misbehaves
- [Level 1 — Foundations](../levels/level-1.md) — where this setup is used

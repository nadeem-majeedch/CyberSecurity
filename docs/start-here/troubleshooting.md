# Troubleshooting

A reference for the problems that actually stop learners, in the order they tend to appear. Each entry
gives the symptom, the usual cause, and the fix.

Before anything else: **write down the exact error text**. "It doesn't work" cannot be debugged; a
quoted error can usually be searched or reasoned about in a minute.

---

## 1. Virtualization and VMs

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| "VT-x is not available" / VM won't start | Virtualization disabled in firmware, or Hyper-V/WSL2 holding it | Enable VT-x/AMD-V in BIOS/UEFI; on Windows disable Hyper-V features or switch to VMware which supports Hyper-V |
| VM is extremely slow | Too little RAM, no hardware acceleration, or a busy host | Give 2 vCPU/2 GB; enable VT-x passthrough; close other VMs |
| "Cannot register the hard disk… already exists" | A VM was copied or moved incorrectly | Use **Machine → Add**, or change the disk UUID (`VBoxManage internalcommands sethduuid disk.vdi`) |
| Disk full after snapshots | Snapshots store deltas and grow | Delete old snapshots; move VMs to a larger disk; keep ≤ 3–4 per VM |
| Snapshot restore fails or VM won't boot | Corrupt snapshot chain, often from cloud-synced folders | Never keep VMs in OneDrive/Dropbox/iCloud folders; rebuild from `clean-base` |

**Rule of thumb:** if a VM behaves strangely after a snapshot operation, revert to `clean-base` and
rebuild rather than debugging a corrupt disk for an evening.

---

## 2. Networking inside the lab

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Lab VM has internet when it should not | Bridged adapter, or NAT still enabled | Switch adapter to host-only; disable adapter 2; re-run the isolation check |
| Cannot reach the target VM | Different host-only networks, or host firewall blocking | Confirm both VMs use the **same** host-only network name; check `ip -br addr`; allow the interface in the host firewall |
| `ping` works but services are unreachable | Service bound to `127.0.0.1`, or blocked by the guest firewall | Bind to the lab address, or test from inside the VM; check `ss -tlnp` |
| Address disappears after reboot | Netplan file not applied or interface name changed | Re-apply `sudo netplan apply`; confirm the interface name with `ip -br link` |
| Two VMs get the same address | Host-only DHCP still enabled alongside static config | Disable DHCP on the host-only network, or use static addresses consistently |
| DNS fails for everything | No resolver configured on the host-only segment (expected) | If you need DNS, add a lab resolver; do not add a public resolver just to make a lab "work" |

Verify what is actually listening:

```bash
ss -tlnp                     # TCP listeners and owning process
sudo ss -ulnp                # UDP listeners
sudo tcpdump -ni any port 80 # see whether packets arrive at all
```

---

## 3. Packages and tools

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `E: Unable to locate package` | Stale package lists, or no repo access from a host-only VM | Temporarily attach NAT, `sudo apt update`, install, then detach NAT |
| `Permission denied` running a tool | Tool needs privileges, or the file is not executable | Use `sudo` where the lesson says so (not habitually); `chmod +x` scripts you wrote |
| `command not found` after install | Not on `PATH`, or installed in a different environment | `which`, `echo $PATH`; for Python use a virtual environment |
| `pip install` fails with "externally managed environment" | Debian/Ubuntu PEP 668 protection | Use `python3 -m venv .venv` and activate it; do not use `--break-system-packages` |
| A tool's flags do not match the lesson | Version drift | Check `--version`; the lesson states the version it was verified against |
| Kali tool missing | Kali metapackages change | `sudo apt install <package>`; if unsure, search the tool name with `apt search` |

---

## 4. Web labs (from Level 3)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| DVWA page shows database error | MySQL not running, or database not initialised | `sudo service mysql start`; open `setup.php` and create/reset the database |
| Juice Shop will not start | Node version mismatch, or port in use | Check `--version` against the pinned requirement; `ss -tlnp | grep 3000` |
| Login loops or session resets | Cookies blocked, or clock skew in the VM | Enable cookies for localhost; sync time in the guest |
| Proxy shows nothing | Browser not configured, or HTTPS interception off | Set the browser proxy explicitly; enable TLS interception only inside the lab |
| "Connection refused" from the analyst VM to the app | App bound to localhost inside the target VM | Bind to the lab interface address, not `127.0.0.1` |

---

## 5. Site and course material

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| A page or module link 404s | Content not published yet | Check the level overview's status column; planned modules are labelled |
| Search finds nothing for a term | Term not yet covered, or British/American spelling differs | Try the [glossary](../resources/glossary.md), which lists synonyms |
| Example output differs from yours | Different tool version or OS | Compare `--version`; report the mismatch so the page can be updated |
| A command in a lesson fails | Possible content defect | Note the lesson code, your version, and the error, then report it |

---

## 6. Getting unstuck methodically

1. **Read the error literally.** Most failures are names, paths, permissions, or versions.
2. **Verify your assumption**, not the one you are confident about. Is the VM *actually* host-only?
3. **Change one variable at a time.** Two simultaneous changes teach you nothing.
4. **Reproduce minimally.** One command, one host.
5. **Check primary sources**: `man <tool>`, `--help`, official docs.
6. **Write the question down** with expected vs actual, what you tried, and the exact output.
7. **Escalate with context** — to a peer, a study group, or an instructor. Include your lab environment
   record; it answers half the questions before they are asked.

If you are stuck more than 30 minutes on something that is not the point of the lesson, park it and
continue. Return during your review session — many problems look obvious after a night's sleep.

---

## 7. Reporting a problem with the course

Include:

- The page title and module code.
- Your environment: host OS, hypervisor, VM image, tool version.
- The exact command and the exact output.
- What the page said should happen.

That is the same information a professional would put in a bug report — which is why practising it
here is useful.

---

## Related

- [Prerequisites and Setup](prerequisites.md) — the environment these fixes assume
- [Lab Safety Guide](lab-safety.md) — isolation verification and snapshots
- [Glossary](../resources/glossary.md) — terminology that may be tripping you up

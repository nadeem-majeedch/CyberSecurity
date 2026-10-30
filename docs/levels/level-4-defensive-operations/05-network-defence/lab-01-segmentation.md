---
title: "LAB-405-01 · Segmentation You Can Prove"
description: "Build three zones behind an nftables boundary, then prove every allowed flow works and every denied flow fails, with counters and logs."
module_code: CYB-405
level: 4
kind: lab
prerequisites: [CYB-405]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-405-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [segmentation, nftables, firewall, routing, verification, zones]
---

# LAB-405-01 · Segmentation You Can Prove

## Scenario and background

A diagram is not segmentation. This lab builds a three-zone network behind a Linux router and then tries to break it:
allowed flows must work, denied flows must fail, and both must leave evidence in counters and logs.

The interesting part is not writing the rules — it is discovering the **alternate paths** that make a policy
cosmetic. A dual-homed host that also answers on a management address is the most common one, and you will close it.

## Learning objectives

1. Assign addresses so that each zone is a distinct subnet behind one boundary.
2. Enable forwarding and write a default-deny `nftables` forward policy with stateful return traffic.
3. Justify each allowed flow and encode it as a rule with an identifiable comment.
4. Build a verification matrix covering allowed and denied paths, in both directions.
5. Find and eliminate a bypass path created by dual-homing.
6. Persist the policy and prove it survives a reboot.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Ubuntu Server | 24.04 | `lab-siem` (router), `lab-ubuntu` (app) |
| `nftables` | current (Ubuntu 24.04) | `nft`, `nftables.service` |
| `iproute2` | current | `ip`, `ss` |
| `openssh-server` | current | On the app host |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** the four lab hosts and the host machine's host-only adapter.
    **Targets you must not use:** any address outside `192.0.2.0/24`, `10.20.20.0/24` and `10.10.10.0/24`. Those
    ranges are documentation or private space and must not be routed anywhere.

    **Do not attach NAT to `lab-siem` while it is routing.** A Linux router with a NAT uplink and a default-deny
    policy that you have not finished writing is how a lab host becomes a path to the internet.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

An attacker who compromises the simulated DMZ host tries to reach management and application services. The policy
exists to make that path fail and to make the attempt visible. The secondary threat is the one you will find in step
6: an unintended path that bypasses the boundary entirely.

## Topology

| Host | Interfaces | Addresses | Zone |
| --- | --- | --- | --- |
| Your host machine | host-only adapter | 192.0.2.1 | Analyst |
| `lab-siem` | NIC1 host-only, NIC2 `lab-app`, NIC3 `lab-dmz` | 192.0.2.30 / 10.20.20.1 / 10.10.10.1 | Management + boundary |
| `lab-ubuntu` | NIC1 host-only, NIC2 `lab-app` | 192.0.2.20 / 10.20.20.20 | Application |
| `lab-win` | NIC1 host-only, NIC2 `lab-dmz` | 192.0.2.40 / 10.10.10.20 | Simulated DMZ |

```text
Analyst 192.0.2.1
      |
      | host-only 192.0.2.0/24
      |
lab-siem 192.0.2.30 ── 10.20.20.1 ── lab-ubuntu 10.20.20.20   (Application)
      │                                └─ 192.0.2.20 (management-only, must not serve)
      └── 10.10.10.1 ── lab-win 10.10.10.20                   (Simulated DMZ)
```

Check your host-only adapter's actual address before continuing; substitute it wherever `192.0.2.1` appears.

## Procedure

### 1. Addressing

On `lab-siem`, netplan (`/etc/netplan/99-lab405.yaml`):

```yaml
network:
  version: 2
  ethernets:
    enp0s8: { addresses: [192.0.2.30/24] }
    enp0s9: { addresses: [10.20.20.1/24] }
    enp0s10: { addresses: [10.10.10.1/24] }
```

On `lab-ubuntu`, add the second NIC and address it:

```yaml
network:
  version: 2
  ethernets:
    enp0s8: { addresses: [192.0.2.20/24] }
    enp0s9: { addresses: [10.20.20.20/24], routes: [{ to: default, via: 10.20.20.1 }] }
```

On `lab-win`, address the DMZ NIC as `10.10.10.20/24` with gateway `10.10.10.1` (PowerShell
`New-NetIPAddress`/`Set-NetIPInterface`).

```bash
sudo netplan apply
ip -brief addr
ip route
```

**Expected:** each host shows the addresses above, and `lab-ubuntu` and `lab-win` have a default route via the
boundary. `lab-siem` should **not** have a default route to the internet.

### 2. Turn on forwarding and write the policy

On `lab-siem`:

```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-lab405.conf
sudo sysctl --system
sysctl net.ipv4.ip_forward
```

`/etc/nftables.conf` — replace the file's contents:

```nft
#!/usr/sbin/nft -f
flush ruleset

table inet lab405 {
    set analysts { type ipv4_addr; elements = { 192.0.2.1 } }
    set apps     { type ipv4_addr; elements = { 10.20.20.20 } }
    set mgmt     { type ipv4_addr; elements = { 192.0.2.30 } }
    set dmz      { type ipv4_addr; elements = { 10.10.10.20 } }

    chain forward {
        type filter hook forward priority filter; policy drop;

        ct state established,related accept comment "return traffic for permitted flows"

        ip saddr @analysts ip daddr @apps tcp dport 22 accept comment "F1 analyst to app ssh"
        ip saddr @analysts ip daddr @mgmt tcp dport 443 accept comment "F2 analyst to siem dashboard"
        ip saddr @apps ip daddr @mgmt tcp dport { 1514, 1515 } accept comment "F3 agent to manager"
        ip saddr @dmz ip daddr @apps tcp dport 8080 accept comment "F4 published app service"

        ct state invalid drop comment "malformed / out-of-state"
        log prefix "lab405-drop: " level info
        counter drop comment "default deny, counted"
    }

    chain input {
        type filter hook input priority filter; policy drop;
        ct state established,related accept
        iif lo accept
        ip saddr @analysts tcp dport 22 accept comment "admin ssh to boundary"
        icmp type echo-request limit rate 5/second accept
        log prefix "lab405-input-drop: " level info
        counter drop
    }
}
```

```bash
sudo nft -f /etc/nftables.conf
sudo systemctl enable --now nftables
sudo nft list ruleset
sudo nft -a list chain inet lab405 forward
```

**Expected:** the forward chain shows `policy drop` and your four accept rules with comments. `nft -a` prints handle
numbers, which you will use later if you need to change a rule.

**Read the rules out loud as policy before testing:** "Established traffic returns. Analysts may SSH to the app.
Analysts may reach the dashboard. The app may send logs. The DMZ may reach one port on one host. Everything else is
dropped and logged, and the drop is counted."

### 3. Give the analyst a route

On your host machine (Windows, elevated):

```powershell
route add 10.20.20.0 mask 255.255.255.0 192.0.2.30
route add 10.10.10.0 mask 255.255.255.0 192.0.2.30
route print -4 | findstr "10.20.20 10.10.10"
```

On Linux/macOS: `sudo ip route add 10.20.20.0/24 via 192.0.2.30`.

**Expected:** routes present. Without them the analyst has no path to the application zone, and every F1 test will
"fail" for the wrong reason.

### 4. Close the bypass before you test

`lab-ubuntu` currently listens for SSH on every interface, including `192.0.2.20`. That address is directly reachable
from the analyst, so the policy on `lab-siem` can be bypassed entirely.

```bash
sudo ss -tlnp | grep ':22'
sudo sed -i 's/^#*ListenAddress.*/ListenAddress 10.20.20.20/' /etc/ssh/sshd_config
grep -E '^ListenAddress' /etc/ssh/sshd_config
sudo systemctl restart ssh
sudo ss -tlnp | grep ':22'
```

**Expected:** before, `0.0.0.0:22`; after, `10.20.20.20:22` only.

Repeat the reasoning for the test web service in step 5: bind it to `10.20.20.20`, not `0.0.0.0`.

**This is the lesson of the lab.** A segmentation policy is only as strong as the weakest path to the protected host.
Dual-homing, a second listener, a management interface, or a container port published on all interfaces will each
bypass the boundary you just built.

### 5. Start the published service

On `lab-ubuntu`:

```bash
mkdir -p /srv/lab405 && echo "lab405 app" | sudo tee /srv/lab405/index.html
cd /srv/lab405 && sudo python3 -m http.server 8080 --bind 10.20.20.20
```

Leave it running in a second session (or use `nohup`). Bound to the app address only.

### 6. Build the verification matrix

Run each test from the stated host. Use `nc -zv` for ports and `curl` for HTTP, with a short timeout so a drop does not
hang the matrix.

| # | Flow | From | Command | Expected |
| --- | --- | --- | --- | --- |
| T1 | F1 allowed | analyst | `ssh -o ConnectTimeout=3 student@10.20.20.20` | banner / prompt |
| T2 | F2 allowed | analyst | `curl -k -m 5 https://192.0.2.30/` | 302 or 200 |
| T3 | F4 allowed | lab-win | `curl -m 5 http://10.20.20.20:8080/` | `lab405 app` |
| T4 | DMZ → app SSH denied | lab-win | `nc -zv -w 3 10.20.20.20 22` | timeout |
| T5 | DMZ → SIEM denied | lab-win | `nc -zv -w 3 192.0.2.30 1514` | timeout |
| T6 | app → internet denied | lab-ubuntu | `curl -m 5 http://203.0.113.5/` | timeout |
| T7 | analyst → app on mgmt address denied | analyst | `nc -zv -w 3 192.0.2.20 22` | connection refused |
| T8 | return traffic works | analyst | T1 succeeded and stayed up | session stable |

**T7 is the bypass test.** "Connection refused" is the correct result: nothing is listening, because step 4 moved the
listener. If it connects, the policy is bypassed and the lab is not finished.

Then prove the drops were counted and logged:

```bash
sudo nft -a list chain inet lab405 forward | tail -5
sudo journalctl -k --since "-10 min" | grep lab405-drop | tail -5
```

**Expected:** the final `counter drop` has a non-zero packet count matching T4–T6, and kernel log lines with the
`lab405-drop:` prefix. Record both.

### 7. Confirm persistence

```bash
sudo systemctl status nftables --no-pager
sudo nft list ruleset > /tmp/before-reboot.txt
sudo reboot
# after reboot
sudo nft list ruleset | diff /tmp/before-reboot.txt - && echo "policy identical after reboot"
```

**Expected:** no diff, and T4/T5 still time out. A policy that disappears on reboot is the most common "we were
segmented last week" incident.

## Evidence to collect

- `evidence/topology.md` — addresses, interfaces, the flow table with justifications.
- `evidence/nftables.conf` — the policy as deployed.
- `evidence/matrix.md` — T1–T8 with command, expected, observed, verdict.
- `evidence/counters.txt` — counter output and log excerpt for the denied flows.
- `evidence/bypass.md` — what the bypass was, how it was found, how it was closed, and how you verified the closure.
- `evidence/persistence.txt` — diff after reboot.

## Verification

- [ ] Each zone is a distinct subnet; forwarding enabled and persistent.
- [ ] Forward chain is default drop, with `ct state established,related` first.
- [ ] Every accept rule corresponds to a justified flow.
- [ ] Allowed flows verified from the correct source host.
- [ ] Denied flows fail, with counters and log lines as evidence.
- [ ] The dual-homed bypass was identified and closed, and the closure tested.
- [ ] Policy survives a reboot and the matrix still holds.
- [ ] No default route to the internet exists on the boundary host.

## Teardown and reset

```bash
# On lab-siem
sudo nft flush ruleset
sudo systemctl disable --now nftables
sudo rm -f /etc/sysctl.d/99-lab405.conf /etc/netplan/99-lab405.yaml
sudo sysctl -w net.ipv4.ip_forward=0
```

On the analyst host: `route delete 10.20.20.0` and `route delete 10.10.10.0`. On `lab-ubuntu`, restore
`ListenAddress` if other labs need SSH on the host-only address, then revert snapshots.

## Reflection

1. Your forward chain accepts established traffic first. What would break if that rule were last?
2. T7 returned "connection refused" rather than a timeout. Explain the difference and why it is the better evidence
   that the bypass is closed.
3. The DMZ host can reach one port on one application host. Name two ways an attacker on that host could still cause
   harm, and the control that would limit each.
4. If the organisation adds a second application host on `10.20.20.0/24`, what must change in the policy, and what must
   change in the test matrix?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Policy | Accept rules, default allow | Default drop with justified flows | Stateful, logged, counted, persistent |
| Verification | Allowed flows only | Allowed and denied tested | Matrix complete in both directions, with counters and logs |
| Bypass | Not considered | Noticed and noted | Found, closed, verified, and generalised into a rule for future builds |
| Evidence | Screenshots | Commands and outputs | Reproducible artefacts plus persistence proof |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| All forwarded traffic fails | `ip_forward` off, or a missing return path | `sysctl net.ipv4.ip_forward`; check routes on both hosts |
| Allowed flow times out | Rule order, wrong set element, or wrong port | `nft -a list chain`, verify addresses with `ip -brief addr` |
| Return traffic dropped | Missing `ct state established,related` | Add it as the first rule |
| `nft -f` syntax error | Set/chain syntax or a missing semicolon | Read the line number; test with `nft -c -f /etc/nftables.conf` |
| Analyst cannot reach 10.20.20.0/24 | Missing host route | Add the route via 192.0.2.30 |
| Denied flow shows "refused" not "timeout" | Something is listening, or an ICMP reject is in play | Check `ss -tlnp` on the target; check for `reject` rules |
| Counters stay zero | Packets matched an earlier accept, or never reached the chain | Check counters on each rule; verify the path with `traceroute` |
| Policy gone after reboot | `nftables.service` not enabled, or config not at `/etc/nftables.conf` | `systemctl enable nftables`; verify the unit's ExecStart |

## References

1. `nftables` wiki — sets, verdict maps, `ct state`, counters, logging.
   <https://wiki.nftables.org/wiki-nftables/index.php/Main_Page> Accessed 2026-10-29.
2. `nft(8)`, `nftables.conf(5)` man pages. Accessed 2026-10-29.
3. NIST SP 800-41 Rev. 1 — Guidelines on Firewalls and Firewall Policy. Accessed 2026-10-29.
4. NIST SP 800-125B — Secure Virtual Network Configuration for Virtual Machine hosts. Accessed 2026-10-29.
5. MITRE ATT&CK — T1021 Remote Services, T1570 Lateral Tool Transfer. <https://attack.mitre.org/> Accessed 2026-10-29.

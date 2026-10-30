---
title: "LAB-405-02 · Suricata: Detect Traffic You Generated"
description: "Place a sensor on the DMZ link, write a rule, prove it fires on your own request, stays quiet on a benign one, and misses traffic that never crosses the link."
module_code: CYB-405
level: 4
kind: lab
prerequisites: [CYB-405]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-405-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [suricata, ids, sensor-placement, rules, eve-json]
---

# LAB-405-02 · Suricata: Detect Traffic You Generated

## Scenario and background

The segmentation from LAB-405-01 gives you a boundary. This lab puts a sensor on it and answers three questions with
evidence: does my rule fire on the behaviour, does it stay quiet on benign traffic, and does the sensor actually see
the traffic I think it sees?

The third question is the one teams skip, and it is the reason dashboards look healthy while nothing is collected.

## Learning objectives

1. Install Suricata 8.0.7 and configure AF_PACKET on a specific interface.
2. Set `HOME_NET` deliberately and explain what changes if it is wrong.
3. Write a local rule with a unique SID, test the configuration, and load it.
4. Prove a positive detection from `eve.json`, with the fields you would put in a report.
5. Prove a negative case and a placement case where the sensor sees nothing.
6. State what the sensor cannot see, including inside TLS.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Suricata | 8.0.7 | OISF stable PPA on Ubuntu 24.04 |
| `jq` | 1.6+ | Reading `eve.json` |
| `suricata-update` | bundled | Optional ruleset update, needs NAT |
| Lab from LAB-405-01 | — | `lab-siem` routing, `lab-win` in the DMZ |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** the lab hosts only: `10.20.20.20:8080` and `192.0.2.30`.
    **Targets you must not use:** any external host. Do not download a ruleset and then "test" rules against the
    internet.

    **The sensor is passive.** Do not enable inline/IPS mode in this lab; a misconfigured inline sensor is an outage,
    and this exercise is about seeing, not blocking.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

A DMZ host is compromised and probes the application zone. The sensor should record the request and its content,
because this is plaintext HTTP on a lab-only port. The same request over TLS would show the connection and the SNI,
not the path or query.

## Procedure

### 1. Install and confirm the version

```bash
sudo add-apt-repository -y ppa:oisf/suricata-stable
sudo apt update
sudo apt install -y suricata jq
suricata -V
```

**Expected:** `This is Suricata version 8.0.7 RELEASE`. If your distribution mirror offers 7.x, the PPA step is what
gets you 8.x — record whichever version you actually installed.

```bash
suricata --build-info | grep -E 'AF_PACKET|NFQueue|libmagic|Lua'
sudo systemctl stop suricata
```

**Expected:** AF_PACKET support present. Stop the service before editing the configuration; a restart mid-edit leaves
you guessing which version of the file is loaded.

### 2. Choose the interface and `HOME_NET`

Find the DMZ interface on `lab-siem`:

```bash
ip -brief addr | grep 10.10.10.1
```

Edit `/etc/suricata/suricata.yaml`:

```yaml
vars:
  address-groups:
    HOME_NET: "[192.0.2.0/24,10.20.20.0/24,10.10.10.0/24]"
    EXTERNAL_NET: "!$HOME_NET"

af-packet:
  - interface: enp0s10          # the DMZ NIC, from the command above
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
```

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v
```

**Expected:** `Configuration provided was successfully loaded`. A test run validates the YAML and the rule files; it is
much cheaper than discovering a typo from an empty `eve.json`.

**Why `HOME_NET` matters:** rules written as `$EXTERNAL_NET -> $HOME_NET` depend on it to decide direction. If you
include the DMZ in `HOME_NET`, a DMZ→app probe looks like internal-to-internal traffic and direction-sensitive rules
stop matching. Decide which side is "external" for your purpose, and write it down.

### 3. Add a local rule

```bash
sudo tee -a /var/lib/suricata/rules/local.rules >/dev/null <<'EOF'
alert http $HOME_NET any -> $HOME_NET 8080 (msg:"LAB405 synthetic marker requested"; flow:to_server,established; content:"lab405-marker"; http_uri; classtype:policy-violation; sid:4050001; rev:1;)
EOF
sudo grep -n 'rule-files' -A6 /etc/suricata/suricata.yaml
```

**Expected:** the YAML lists `local.rules`. If it does not, add `- local.rules` under `rule-files` and re-test.

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v
sudo systemctl enable --now suricata
sleep 5
sudo tail -5 /var/log/suricata/suricata.log
```

**Expected:** `engine started`, and the interface is in AF_PACKET mode. If the service exits immediately, the log
names the interface or the rule file.

### 4. Positive test

Ensure the app service from LAB-405-01 is running on `lab-ubuntu`:

```bash
# lab-ubuntu
cd /srv/lab405 && sudo python3 -m http.server 8080 --bind 10.20.20.20
```

From `lab-win` (the DMZ host):

```bash
curl -s -m 5 "http://10.20.20.20:8080/?q=lab405-marker" ; echo
sleep 3
```

On `lab-siem`:

```bash
sudo tail -3 /var/log/suricata/fast.log
sudo jq -c 'select(.event_type=="alert") | {ts:.timestamp, sid:.alert.signature_id, sig:.alert.signature, src:.src_ip, dst:.dst_ip, dport:.dest_port, url:.http.url}' \
  /var/log/suricata/eve.json | tail -3
```

**Expected:** a `fast.log` line with `[1:4050001:1] LAB405 synthetic marker requested`, and an `eve.json` alert
showing `src_ip` = `10.10.10.20`, `dst_ip` = `10.20.20.20`, `dest_port` 8080, and the URL containing the marker.

Save the JSON line as `evidence/alert-positive.json`.

**Why the URI is visible:** this is HTTP on port 8080 inside the lab. The same rule against HTTPS would not match,
because `http_uri` inspects decrypted HTTP, not TLS records.

### 5. Negative test

```bash
# lab-win
curl -s -m 5 "http://10.20.20.20:8080/?q=harmless" ; echo
sleep 3
```

**Expected:** no new `4050001` alert. Confirm by counting before and after:

```bash
sudo jq -r 'select(.event_type=="alert" and .alert.signature_id==4050001) | .timestamp' /var/log/suricata/eve.json | wc -l
```

Run the count before and after the benign request and record both numbers. "No alert" is only evidence with a count
and a time window.

### 6. Placement test — prove what the sensor cannot see

Traffic from the analyst to the application enters `lab-siem` on the host-only NIC and leaves on the app NIC. It never
touches `enp0s10`. Prove it.

Temporarily allow the analyst to reach the app's web port (the policy from LAB-405-01 permits only SSH):

```bash
# lab-siem
sudo nft insert rule inet lab405 forward ip saddr 192.0.2.1 ip daddr 10.20.20.20 tcp dport 8080 accept comment "temporary: placement test"
```

```bash
# analyst host
curl -s -m 5 "http://10.20.20.20:8080/?q=lab405-marker" ; echo
sleep 3
```

```bash
# lab-siem
sudo jq -r 'select(.event_type=="alert" and .alert.signature_id==4050001) | .timestamp' /var/log/suricata/eve.json | wc -l
```

**Expected:** the request succeeds (you get the page) and the alert count **does not increase**. The sensor is on the
DMZ link; this flow crossed two other interfaces.

Remove the temporary rule immediately:

```bash
sudo nft -a list chain inet lab405 forward | grep 'placement test'
sudo nft delete rule inet lab405 forward handle <HANDLE>
```

**Write the sentence this proves:** "The sensor observes DMZ-to-application traffic on the DMZ link; it does not
observe analyst-to-application traffic." A placement claim without this test is a guess.

### 7. Inspect what else the sensor recorded

```bash
sudo jq -c 'select(.event_type=="flow") | {src:.src_ip, dst:.dst_ip, dport:.dest_port, bytes_toserver:.flow.bytes_toserver, bytes_toclient:.flow.bytes_toclient}' \
  /var/log/suricata/eve.json | tail -5
sudo jq -c 'select(.event_type=="stats") | {ts:.timestamp, capture:.stats.capture.kernel_packets, decoded:.stats.decoder.pkts, drops:.stats.capture.kernel_drops}' \
  /var/log/suricata/eve.json | tail -2
```

**Expected:** flow records for the requests, and stats showing `kernel_packets` > 0 with `kernel_drops` ideally 0. A
non-zero and rising drop count means the sensor cannot keep up — an important finding, because a dropping IDS is a
partial blind spot, not a healthy one.

Save the stats output as `evidence/stats.json`.

## Evidence to collect

- `evidence/version.txt` — `suricata -V` and relevant `--build-info` lines.
- `evidence/rule.conf` — the `local.rules` line and the `rule-files`/`af-packet` configuration excerpts.
- `evidence/config-test.txt` — output of `suricata -T`.
- `evidence/alert-positive.json` — the alert with source, destination, port and URL.
- `evidence/negative-count.txt` — counts before and after the benign request.
- `evidence/placement.md` — the test, the count that did not move, and the sentence it proves.
- `evidence/stats.json` — capture and drop counters.
- `evidence/limits.md` — what TLS and placement each hide.

## Verification

- [ ] Suricata 8.0.7 confirmed, AF_PACKET present.
- [ ] Interface is the DMZ NIC, not "all interfaces by accident".
- [ ] `HOME_NET` set deliberately, with the direction consequence explained.
- [ ] `suricata -T` passes before the service is started.
- [ ] Positive test shows SID 4050001 with the correct source, destination and URL.
- [ ] Negative test records counts before and after, not just an absence.
- [ ] Placement test shows a successful request with no alert, and the temporary rule was removed.
- [ ] Drop counters inspected and interpreted.
- [ ] TLS limitation stated in terms of rule fields, not as a general claim.

## Teardown and reset

```bash
sudo systemctl stop suricata
sudo systemctl disable suricata
sudo sed -i '/LAB405 synthetic marker requested/d' /var/lib/suricata/rules/local.rules
```

Remove the temporary nftables rule if step 6 was interrupted. Keep the evidence; the rule itself is only interesting
with its test results.

## Reflection

1. The placement test produced a successful request and no alert. Why is that a *passing* test rather than a failure?
2. Your rule matches `http_uri`. Name two fields you would use for a TLS-based detection, and what each tells you.
3. `kernel_drops` is rising. What are your options, in order of preference, and what does each cost?
4. If `HOME_NET` included `10.10.10.0/24`, which of your tests would change behaviour, and why?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Configuration | Service running by luck | Interface and `HOME_NET` deliberate, config tested | Direction implications explained; capture health checked |
| Detection | Rule loaded, no proof | Alert observed | Alert fields used as evidence; negative case counted |
| Placement | Assumed coverage | Interface named | Placement proven by a null result, with the temporary rule cleaned up |
| Limits | Not stated | TLS mentioned | Specific fields lost to TLS, plus drop-related blind spots |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `suricata -T` fails on YAML | Indentation or duplicate key | Fix indentation; validate with a YAML parser |
| Service exits at start | Interface name wrong or not present | `ip -brief addr`; correct `af-packet.interface` |
| No alerts, no flows | Sensor on the wrong NIC | Check the route path; test with the placement procedure |
| Alert exists but no URL | Request was not parsed as HTTP (port or protocol) | Confirm plain HTTP on 8080; check `http` events in `eve.json` |
| Duplicate alerts | Request retried, or rule in multiple files | Check `rule-files`; count unique timestamps |
| `jq` returns nothing | `eve.json` rotated or wrong path | `ls -l /var/log/suricata/`; use the current file |
| Everything drops | Sensor overloaded in a VM | Reduce rules, increase resources, or accept and document the gap |

## References

1. Suricata 8.0.7 documentation — AF_PACKET, `HOME_NET`, rule keywords, `eve.json` schema.
   <https://docs.suricata.io/> Accessed 2026-10-29.
2. OISF stable PPA. <https://launchpad.net/~oisf/+archive/ubuntu/suricata-stable> Accessed 2026-10-29.
3. Suricata — `http_uri`, `flow`, `classtype`, SID conventions. Accessed 2026-10-29.
4. NIST SP 800-94 — Guide to Intrusion Detection and Prevention Systems. Accessed 2026-10-29.
5. MITRE ATT&CK — T1071 Application Layer Protocol; T1048 Exfiltration Over Alternative Protocol. Accessed 2026-10-29.

---
title: "Zones, Sensors and What Encryption Hides"
description: "Segmentation as an enforceable policy, sensor placement, the limits of signatures, and the metadata TLS leaves behind."
module_code: CYB-405
level: 4
kind: lesson
prerequisites: [CYB-404]
estimated_minutes: 210
difficulty: advanced
safety: none
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [segmentation, firewall, ids, tls, dns, netflow, sensor-placement]
---

# Zones, Sensors and What Encryption Hides

## What this lesson covers

1. Zones as a security boundary, and segmentation as an enforceable policy rather than a diagram.
2. Default-deny, stateful inspection, and why egress filtering matters more than ingress.
3. Firewall semantics that trip people up: direction, established traffic, and implicit rules.
4. Sensor placement, and the difference between what an IDS can see and what it can prove.
5. Signature limits, encrypted traffic, and the metadata that survives TLS.
6. DNS as a control point and a detection surface.
7. Network telemetry choices: full packet, flow, or neither.

## Why it matters

Segmentation is the control that decides how bad a compromise becomes. An attacker on a flat network reaches
everything; on a segmented one they reach a zone boundary and must cross it, which is where detection lives.

It is also the control most often claimed and least often tested. A diagram with coloured boxes is not segmentation.
A rule set with a test matrix showing that the denied paths are actually denied, and that the traffic is logged, is.

## 1. Zones and the policy behind them

A **zone** is a group of systems with the same trust level and the same allowed communications. In the lab:

| Zone | Members | Trust | Allowed to |
| --- | --- | --- | --- |
| Analyst | 192.0.2.10 | High | Reach management ports on servers; reach the SIEM dashboard |
| Application | 192.0.2.20 | Medium | Serve the analyst; forward logs to the SIEM; no internet |
| Management | 192.0.2.30 | High | Receive logs; answer dashboard requests from analysts only |
| Simulated DMZ | 10.10.10.20 | Low | Nothing inbound except the one published service; no egress |

The policy that follows is a list of **flows**, each with a justification:

| # | From | To | Port | Why |
| --- | --- | --- | --- | --- |
| F1 | Analyst | Application | 22/tcp | Administration |
| F2 | Analyst | Management | 443/tcp | SIEM dashboard |
| F3 | Application | Management | 1514/tcp, 1515/tcp | Agent traffic and enrollment |
| F4 | DMZ | Application | 8080/tcp | The one simulated published service |
| Default | any | any | any | **Deny, and log** |

If you cannot write the "why" column, the flow is either unnecessary or you do not yet understand the system.

## 2. Default-deny and direction

**Default deny** means the last rule drops everything not explicitly permitted. Most real incidents exploit an
environment where the default was "allow" and the exceptions accumulated for a decade.

**Direction matters more than people expect.** Inbound filtering is the obvious half: do not let the internet reach
your database. Egress filtering is the half that catches compromises: a workstation that suddenly resolves and
connects to a new external host is only visible if you log (and ideally block) outbound traffic that is not on an
allowlist.

```bash
# Inspect before changing anything
sudo nft list ruleset
sudo ss -tlnp
```

**Stateful inspection** means the firewall tracks connections, so a reply to an allowed outbound connection does not
need its own inbound rule. In `nftables` that is `ct state established,related accept`. Without it you will write
dozens of rules for return traffic and still break something.

**The classic mistakes**, in order of how often they cause incidents:

1. A rule above the default-deny that is broader than intended (`ip saddr 192.0.2.0/24 accept`).
2. Rules appended after the drop, which therefore never match.
3. `ct state` missing, so return traffic is dropped and the service "mysteriously" fails.
4. Logging everything, filling the disk, and then disabling logging.
5. A policy that exists on one host and not on its replacement.

## 3. Where to put a sensor

An IDS sees only the traffic that crosses its interface. Three placements, three different answers:

| Placement | Sees | Misses |
| --- | --- | --- |
| Span port on a core switch | East-west traffic between zones | Traffic that never crosses that switch; encrypted payloads |
| Host NIC on a server | That host's traffic, including localhost-adjacent flows | Other hosts' traffic |
| Inline (IPS) | Everything on the path, and can drop it | Availability risk: a false positive becomes an outage |

In this lab the sensor sits on the DMZ link of `lab-siem`, because that is where the simulated cross-zone traffic
travels. That choice is testable: generate traffic that does **not** cross the link and confirm the sensor does not see
it. An untested placement claim is how teams end up with a dashboard full of nothing.

**IDS versus IPS** is a policy decision as much as a technical one:

- **IDS** alerts; false positives cost analyst time.
- **IPS** blocks; false positives cost availability, and an inline device is a failure domain.

The usual professional path is IDS first, tune until the rule set is understood, then move specific high-confidence
rules inline. Moving everything inline on day one is how a security team causes an outage and loses the mandate to
monitor.

## 4. What signatures can and cannot do

A signature matches bytes or protocol structure it has seen before. That gives three properties worth stating plainly:

- **It cannot detect what it has no rule for.** Novel tooling, custom protocols and living-off-the-land behaviour
  often pass.
- **It degrades with encryption.** A rule matching an HTTP URI sees nothing inside TLS.
- **It produces false positives on legitimate traffic that resembles the pattern**, which is why every rule needs a
  negative test.

This is why network detection is strongest when combined with endpoint telemetry: the endpoint sees the decrypted
content, the network sees the connection.

## 5. What TLS hides, and what it does not

Modern TLS hides the request path, headers, body, and often the hostname (with Encrypted Client Hello). What typically
remains:

| Remaining observable | Detection value |
| --- | --- |
| Destination IP and port | Weak: shared CDN addresses; strong when it is a rare address for this estate |
| SNI (unless ECH) | Strong: the requested hostname, in the clear in most deployments |
| Certificate metadata (CN, SAN, issuer, validity) | Moderate: self-signed or mismatched names are suspicious in some contexts |
| Connection timing, duration, bytes in/out | Strong for beaconing: regular intervals, small fixed uploads |
| DNS queries preceding the connection | Strong: names, query types, cadence |
| TLS record sizes and sequence | Weak-to-moderate: research-grade fingerprinting, fragile |

**Interception is not a default.** TLS interception (a proxy with a trusted CA) breaks end-to-end guarantees, creates
a high-value target, has legal and privacy implications, and is often prohibited for personal or regulated traffic.
Decide it explicitly, document who approved it, and scope it. "We decrypt everything" is a statement about risk
appetite, not a technical setting.

## 6. DNS as a control point

DNS is attractive to attackers because blocking it breaks the network, and because many organisations log it
centrally while logging little else.

Behaviours worth detecting:

| Behaviour | Benign explanation | Suspicious when |
| --- | --- | --- |
| Many unique subdomains of one domain | CDN, telemetry, ad networks, SaaS tenants | Labels are long and random, and the domain is newly registered |
| TXT queries | SPF/DKIM/DMARC checks, service verification | High volume of TXT to one domain, with encoded-looking payloads |
| Regular query interval | NTP, monitoring, software update checks | Interval is precise (low jitter) and the domain is otherwise unknown |
| Large response sizes | Normal for some record types | TXT responses consistently near the payload capacity |
| NXDOMAIN bursts | Typos, stale links | Algorithmically generated names (DGA), high cardinality per second |

**The discriminator is not any single feature.** Long labels alone are common; `verylongsubdomain.analytics.example.com`
is unremarkable if the parent domain is known and the queries are A records at human-driven intervals. Tunnelling
usually combines long, high-entropy labels, TXT or NULL record types, a single parent domain, and machine-regular
timing.

## 7. Telemetry choices

| Option | Gives you | Costs |
| --- | --- | --- |
| Full packet capture | Everything, for forensics | Storage and privacy; usually days, not months |
| Flow records (NetFlow/IPFIX) | Who talked to whom, when, how much | No content, no payload-based detection |
| DNS/proxy logs | Names and destinations | Only what routes through the resolver or proxy |
| IDS alerts | Interpreted events | Only what the rules cover |

A defensible design uses all four at different retention: flows for months, alerts for weeks, packets for days around
an incident, and name logs for as long as policy allows.

## Common misconceptions

| Belief | Reality |
| --- | --- |
| "We have a firewall, so we are segmented" | Segmentation is the policy and its verification, not the appliance. |
| "The IDS covers the network" | It covers one link, and only the unencrypted parts. |
| "HTTPS means we are blind" | Names, timing, volume and certificates remain; endpoint telemetry covers the rest. |
| "Blocking outbound DNS stops exfiltration" | It also stops updates, telemetry and much of the business; allowlisting is the workable version. |
| "More signatures is better" | More signatures means more false positives unless each is tested and tuned. |
| "We should decrypt everything" | That is a legal and privacy decision with an availability and trust cost, not a checkbox. |

## Key terms

**zone** · **flow** · **default deny** · **stateful inspection** · **egress filtering** · **span port** · **inline** ·
**false positive cost** · **SNI** · **ECH** · **beaconing** · **jitter** · **DGA** · **TXT record** · **flow records** ·
**retention**

## Check your understanding

**1. Why is a default-deny rule useless if placed after an `accept` for the whole subnet?**

<details><summary>Answer</summary>
Rules are evaluated in order; the broad accept matches first and the drop is never reached. The policy looks strict and
behaves as allow-all.
</details>

**2. A sensor is on the DMZ link and sees no traffic between two application hosts. Is it broken?**

<details><summary>Answer</summary>
Not necessarily — that traffic may not cross the DMZ link. This is the placement question, and the test is to generate
traffic that does cross and confirm it appears.
</details>

**3. Name two observables that survive TLS, and one that does not.**

<details><summary>Answer</summary>
Survive: SNI (without ECH), destination IP/port, timing and byte counts, certificate metadata. Do not survive: HTTP
path, headers, body content.
</details>

**4. A domain shows 4,000 unique subdomains in an hour. What else do you need before calling it tunnelling?**

<details><summary>Answer</summary>
Record types, label length and entropy, whether the parent domain is known or newly registered, query timing
regularity, response sizes, and whether the same host resolves other names normally. Cardinality alone is normal for
CDNs.
</details>

**5. Why might an organisation choose IDS over IPS for a new rule set?**

<details><summary>Answer</summary>
Because an inline false positive is an outage. Alert-only lets you measure the false-positive rate against real
traffic before accepting the availability risk of blocking.
</details>

## Summary

- Zones define trust and allowed flows; every flow needs a justification.
- Default deny, in the right order, with stateful return traffic and egress filtering.
- Sensor placement is a testable claim: prove it sees what you say, and name what it misses.
- Signatures cannot see novel behaviour or encrypted payloads; they also produce false positives that need testing.
- TLS leaves names, timing, volume and certificates; interception is a governance decision.
- DNS detection combines label shape, record type, cadence and domain reputation — never one feature.
- Choose retention per telemetry type rather than capturing everything for a week.

## Next

[LAB-405-01](lab-01-segmentation.md) turns this policy into `nftables` rules and a matrix that proves the denied paths
are denied.

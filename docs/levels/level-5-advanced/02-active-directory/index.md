---
title: "CYB-502 · Active Directory Security"
description: "Build an isolated domain, understand how Kerberos and NTLM actually authenticate, find privilege paths, and detect the activity those paths produce."
module_code: CYB-502
level: 5
kind: reference
prerequisites: [CYB-405, CYB-407, CYB-402]
estimated_minutes: 960
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-502-01, LAB-502-02, LAB-502-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [active-directory, kerberos, ntlm, bloodhound, pingcastle, tiering, laps, detection]
---

# CYB-502 · Active Directory Security

**Level 5** · 16 hours · **Prerequisites:** [CYB-405](../../level-4-defensive-operations/05-network-defence/index.md), [CYB-407](../../level-4-defensive-operations/07-incident-response/index.md), [CYB-402](../../level-4-defensive-operations/02-endpoint-telemetry/index.md)

## Why this module exists

Active Directory is where most enterprise intrusions become domain-wide. Almost every documented "domain takeover"
is a chain of ordinary misconfigurations: a service account with an SPN and a weak password, an over-broad ACL, a
delegation setting nobody remembers enabling, and a workstation where a privileged credential was typed.

This module teaches the structure and the protocols first, because the misconfigurations are only visible if you know
what normal looks like. You build the domain yourself, in isolation, and then look at it the way both an attacker and
a defender would — with the explicit constraint that the attacker's view exists to produce findings you can defend.

## Module outcomes

By the end of this module you can:

- Build and verify an isolated single-domain lab with a domain controller and joined clients, with no route to any
  other network.
- Explain a Kerberos authentication exchange and where NTLM still appears, in terms of the events each produces.
- Enumerate users, groups, ACLs, SPNs and delegation settings, and interpret what each exposes.
- Use BloodHound CE and PingCastle to find privilege paths and configuration weaknesses, and explain the limits of
  both.
- Detect suspicious authentication activity from domain controller events, including the patterns that precede
  credential theft and privilege escalation.
- Apply tiering, LAPS, Protected Users, service-account and delegation hardening, and verify the change.
- Describe recovery from a domain compromise, including the krbtgt reset and the order of operations.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [Identity, Kerberos and Privilege Paths](01-identity-and-kerberos.md) | 4 h |
| Lab | [LAB-502-01 · Build the Isolated Domain](lab-01-build-domain.md) | 4 h |
| Lab | [LAB-502-02 · Enumerate, Map and Audit](lab-02-bloodhound-pingcastle.md) | 4 h |
| Lab | [LAB-502-03 · Final Challenge: Detect, Harden, Recover](lab-03-detect-harden-recover.md) | 4 h |

## What you need

| Component | Version | Notes |
| --- | --- | --- |
| Windows Server | 2025 Evaluation | **180-day** evaluation, registration required, activate within 10 days |
| Windows 11 | 23H2+ | Two clients, evaluation images |
| BloodHound CE | 9.9.0 | Docker + `bloodhound-cli`, 8 GB RAM recommended |
| SharpHound | 2.17.1 | Download from your instance's **Settings → Download Collectors** |
| PingCastle | 4.0.0.31 | Community edition is free for auditing **your own** environment |
| Sysmon | 15.22 | On the DC and clients, with a reviewed configuration |

**RAM:** the domain controller needs 4 GB, each client 4 GB, and BloodHound's stack 8 GB. Run BloodHound with the DC
and one client at a time on a 16 GB host, or use 24 GB.

## The isolation requirement

This is the most important constraint in the module. The domain is `lab.local`, built by you, on a **host-only or
internal** virtual network with **no NAT and no bridged adapter**. A domain controller reachable from a real network is
a genuine risk, and a domain joined to a real forest is a different exercise with different authorization.

!!! warning "Never target a real domain"
    Do not run SharpHound, PingCastle, or any enumeration tool against a domain you do not own or administer. The
    tools are not subtle: they generate authentication traffic and directory reads that defenders will see, and doing
    so without written authorization is a security incident.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Assessment and the final challenge

LAB-502-01 is marked on isolation proof and a working domain. LAB-502-02 is marked on findings that name a concrete
path and its evidence, not a tool screenshot. LAB-502-03 is the final challenge: a synthetic event set to detect,
then hardening that you can verify, then a written recovery plan. The rubric weights detection reasoning and
verification over the number of changes applied.

## Professional relevance and limits

BloodHound and PingCastle find **configuration** weaknesses. They do not prove exploitability, they age quickly after
a change, and they say nothing about detection coverage. Every finding needs a path, a precondition and a control that
would break it. State those limits in your report.

## Where this fits

[CYB-501](../01-penetration-testing/index.md) supplies the engagement discipline; this module applies it to identity.
[CYB-506](../06-threat-hunting/index.md) turns the detection ideas into hunts and coverage maps.

## References

1. Microsoft — Active Directory Domain Services documentation and security best practices. Accessed 2026-10-29.
2. Microsoft — Windows Server 2025 Evaluation (180 days, registration required).
   <https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2025> Accessed 2026-10-29.
3. SpecterOps — BloodHound CE 9.9.0 quickstart. <https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart> Accessed 2026-10-29.
4. PingCastle 4.0.0.31 — free for auditing your own environment; commercial licensing for service providers.
   <https://www.pingcastle.com/download/> Accessed 2026-10-29.
5. Microsoft — Windows LAPS overview. Accessed 2026-10-29.
6. MITRE ATT&CK v20.0 — Credential Access, Lateral Movement, Privilege Escalation. <https://attack.mitre.org/> Accessed 2026-10-29.

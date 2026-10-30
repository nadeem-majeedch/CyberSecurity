---
title: "Identity, Kerberos and Privilege Paths"
description: "How AD authenticates, which events prove it, why ordinary misconfigurations become domain paths, and what hardening actually verifies."
module_code: CYB-502
level: 5
kind: lesson
prerequisites: [CYB-502]
estimated_minutes: 240
difficulty: advanced
safety: none
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [active-directory, kerberos, ntlm, acls, kerberoasting, tiering, detection]
---

# Identity, Kerberos and Privilege Paths

## What this covers

1. Domain structure and the objects that matter for security.
2. Kerberos authentication, step by step, and the events each step produces.
3. Where NTLM still appears, and why relay remains possible.
4. The misconfigurations that create privilege paths, and the control that breaks each.
5. Auditing and detection: which event IDs answer which question.
6. Tiering, LAPS, Protected Users, service accounts and delegation.
7. Recovery after a domain compromise.

## Why it matters

A domain is a graph of trust. Users can act on groups, groups can act on computers, computers can act on services,
and ACLs decide all of it. Attackers do not "break" Kerberos; they walk that graph using settings that were chosen for
convenience years ago.

Defenders who understand the graph can remove the edges. Defenders who only read alerts can watch someone traverse it.

## 1. Structure

| Concept | What it is | Security relevance |
| --- | --- | --- |
| Forest | Security boundary; shares schema and global catalog | Forest compromise is the top of the impact scale |
| Domain | Administrative boundary within a forest | Domain Admin is powerful inside it, not automatically outside |
| OU | Container for policy and delegation | Where GPOs and admin delegation are scoped |
| Site | Network topology for replication and logon | Misconfigured sites cause authentication to cross links |
| DC | Domain controller; holds the directory and authenticates | Tier 0: its compromise is game over |
| SYSVOL / NETLOGON | Replicated policy and scripts | Historic home of credentials in scripts |
| Schema | Object definitions | Schema Admin is a forest-level privilege |

**Objects that matter:** users, computers, groups (security and distribution), service accounts (a user with an SPN),
group-managed service accounts (gMSA), and the ACEs on all of them. Each has a SID; group membership determines the
token a user receives at logon.

**Nested groups** are how privilege hides. A user in `Helpdesk` in `Server Admins` in `Domain Admins` is a domain admin
with two clicks of distance. Enumeration tools resolve this; a manual review often does not.

## 2. Kerberos, step by step

Kerberos issues **tickets**, not passwords. Three parties: the client, the Key Distribution Centre (KDC, on a DC), and
the service.

1. **AS exchange.** The client sends `AS-REQ`, proving identity with a timestamp encrypted using its own key (derived
   from the password hash). The KDC replies with `AS-REP` containing a **TGT** encrypted with the `krbtgt` account's
   key, plus a session key for the client.
2. **TGS exchange.** For each service, the client sends `TGS-REQ` with the TGT and the service's **SPN**. The KDC
   replies with `TGS-REP` containing a **service ticket** encrypted with the **service account's** key.
3. **Service access.** The client presents the service ticket in `AP-REQ`; the service decrypts it with its own key and
   reads the **PAC**, which carries the user's group SIDs and is signed by the KDC.

Two consequences follow directly:

- A service ticket is encrypted with the service account's key. If that key is derived from a weak password and the
  ticket uses RC4, an attacker who can request a ticket can take it away and crack it offline. That is
  **Kerberoasting**: no traffic to the service, no failed logons, nothing to alert on except the request itself.
- Accounts with **pre-authentication disabled** let anyone request an `AS-REP` encrypted with the user's key, which is
  likewise crackable offline. That is **AS-REP roasting**.

**Encryption types** are part of the evidence: AES (0x12/0x11) is the modern default; RC4 (0x17) is what makes
Kerberoasting cheap. Seeing RC4 tickets in a domain that should be AES-only is a finding.

## 3. NTLM and relay

NTLM is challenge-response: the server sends a challenge, the client returns a response derived from the password
hash. It survives because legacy applications, local accounts and some appliances still use it.

**Relay** is the attack that matters: an attacker coerces a machine or user to authenticate to them, then forwards that
authentication to a server that accepts it. Signing and channel binding are what break the relay, because the attacker
cannot produce a valid signature for the relayed session.

| Control | Breaks |
| --- | --- |
| SMB signing required (server and client) | SMB relay |
| LDAP signing and channel binding | LDAP relay |
| Extended Protection for Authentication (EPA) | HTTP/AD CS relay |
| Disabling NTLM where feasible | The whole family, at a compatibility cost |
| SMBv1 removed | Legacy relay and exploitation paths |

## 4. Misconfigurations that create paths

| Misconfiguration | What it enables | Control that breaks it |
| --- | --- | --- |
| Service account with SPN and weak password | Kerberoasting → offline crack → service access | gMSA or 25+ char managed password; AES-only; monitor 4769 RC4 |
| `DONT_REQ_PREAUTH` on an account | AS-REP roasting | Re-enable pre-authentication; strong password |
| Unconstrained delegation on a server | Capture of any authenticating user's TGT | Remove; use constrained or RBCD with protocol transition only where required |
| `GenericAll` / `WriteDACL` / `ForceChangePassword` on a privileged object | Direct reset or ACL takeover | ACL review; remove inheritance abuse; tier admins |
| `WriteOwner` on a group | Take ownership, then rewrite membership | Same |
| `AddMember` on a privileged group | Add a controlled account | Same |
| Password in `Description` or a script in SYSVOL | Credential discovery | Remove, rotate, scan |
| `adminCount=1` on stale accounts | Protected ACLs but forgotten access | Clean up; do not rely on adminCount as an inventory |
| Domain Admins logging on to workstations | Credential exposure on Tier 2 | Tiering and PAWs; deny logon rights |
| No LAPS | Shared local admin password across hosts | Windows LAPS (built in from Windows 11 23H2) |
| Print Spooler on a DC | Coercion paths | Disable the spooler on DCs |
| NTLM enabled everywhere | Relay and downgrade | Audit, then restrict; plan compatibility |

**AD CS** deserves its own module; here it is enough to know that misissued certificate templates can authenticate as
any user, and that they are a common escalation path. The lab flags templates with `Enrollee Supplies Subject` and
broad enrolment rights as findings to investigate, not to exploit.

## 5. Auditing and detection

Enable **advanced audit policy** and **directory service access auditing** with SACLs on sensitive objects, or the
events below will not exist.

| Event | Meaning | Detection value |
| --- | --- | --- |
| 4768 | TGT issued | Pre-auth type, encryption type, source |
| 4769 | Service ticket issued | **RC4 + many SPNs + one source = Kerberoasting** |
| 4771 | Pre-auth failed | Password guessing, stale credentials |
| 4776 | NTLM credential validation | NTLM use where it should not be |
| 4624 / 4625 | Logon success/failure | Type 3 network logons, bursts |
| 4672 | Special privileges assigned | Non-admin accounts receiving admin rights |
| 4720 / 4728 / 4732 / 4756 | Account and group changes | Privilege escalation |
| 5136 | Directory object modified | ACL and attribute tampering (needs auditing) |
| 4662 | Object access | DCSync-style replication rights (with SACL) |
| 7045 | Service installed | Lateral movement on servers |
| 1102 | Audit log cleared | Anti-forensics |

**The patterns worth writing detections for:**

- A single account requesting service tickets for many distinct SPNs in a short window, especially with RC4.
- `4768` with pre-authentication **not required** for an account that should require it.
- A burst of `4625` followed by `4624` type 3 from the same source, then `4672`.
- `4720`/`4732` changes to privileged groups outside a change window.
- `4662` on the domain object with replication GUIDs from a non-DC host.
- `7045` on a DC or a Tier 0 server.

## 6. Hardening

| Layer | Actions | Verification |
| --- | --- | --- |
| Identity | gMSA for services; remove unnecessary SPNs; strong passwords; Protected Users for privileged accounts | `Get-ADServiceAccount`, SPN inventory, group membership |
| Delegation | Remove unconstrained; constrain or use RBCD deliberately | `Get-ADComputer -Filter {TrustedForDelegation -eq $true}` |
| ACLs | Remove excess rights on privileged objects; review AdminSDHolder | `Get-Acl`, BloodHound paths, PingCastle findings |
| Tiering | Separate Tier 0/1/2 administration; PAWs; deny logon rights | GPO and logon-right reports; DC logon events |
| Protocols | SMB/LDAP signing, channel binding, SMBv1 off, NTLM restricted | `Get-SmbServerConfiguration`, LDAP policy, event 4776 volume |
| Local admin | Windows LAPS with rotation and escrow | LAPS policy and password age |
| Monitoring | Advanced audit, SACLs, Sysmon, alerting on the patterns above | Generate a test event and confirm the alert |

**Verification is the point.** Each row has a query or a generated event. A hardening change you cannot query is a
belief.

## 7. Recovery after compromise

Order matters, and the order is not obvious:

1. **Isolate** affected DCs and privileged hosts without destroying evidence (CYB-407).
2. **Preserve** event logs and directory evidence before cleanup.
3. **Reset `krbtgt` twice**, with replication between resets and a waiting period, to invalidate forged tickets. One
   reset is not enough.
4. **Reset privileged credentials twice**, including service accounts, and rotate LAPS passwords.
5. **Rebuild** compromised Tier 0 systems from known-good media; do not clean them.
6. **Check** for persistence: SIDHistory, AdminSDHolder, ACL changes, new SPNs, shadow credentials, certificates.
7. **Restore trust** only after the above, and re-establish tiering before normal operations resume.

## Common misconceptions

| Belief | Reality |
| --- | --- |
| "Kerberos is encrypted, so it is safe to observe" | Ticket requests reveal SPNs and encryption types; tickets themselves are crackable offline if RC4 and weak keys. |
| "Domain Admin is the only privileged group" | Account Operators, Backup Operators, and ACL rights can be just as decisive. |
| "BloodHound found it, so it is exploitable" | It found a path under stated preconditions. Prove the precondition or report it as potential. |
| "Disabling NTLM is a checkbox" | It breaks legacy applications; audit first, restrict by exception, then enforce. |
| "One krbtgt reset fixes a domain compromise" | Two resets with replication, plus credential resets and Tier 0 rebuild. |
| "PingCastle score is a security metric" | It is a heuristic snapshot of configuration, not a measure of detection or response. |

## Key terms

**forest** · **OU** · **SPN** · **TGT** · **TGS** · **PAC** · **pre-authentication** · **Kerberoasting** ·
**AS-REP roasting** · **unconstrained delegation** · **RBCD** · **ACL / ACE** · **AdminSDHolder** · **SIDHistory** ·
**tiering** · **PAW** · **LAPS** · **gMSA** · **DCSync** · **krbtgt reset**

## Check your understanding

**1. Why does Kerberoasting not require traffic to the target service?**

<details><summary>Answer</summary>
The KDC issues the service ticket encrypted with the service account's key. An attacker with any valid account can
request it and crack it offline; the service never sees the request.
</details>

**2. Which event and field would reveal an RC4 service-ticket request, and why is RC4 significant?**

<details><summary>Answer</summary>
4769, with the ticket encryption type field showing 0x17 (RC4). RC4 tickets are cheaper to crack than AES, so their
presence on accounts that should be AES-only is both a misconfiguration and a detection signal.
</details>

**3. A helpdesk group has `GenericAll` on an OU containing servers. What is the risk and the fix?**

<details><summary>Answer</summary>
Helpdesk can modify objects in the OU, including ACLs, potentially creating admin access. Fix by scoping delegation to
specific attributes/tasks, removing GenericAll, and verifying with an ACL report.
</details>

**4. Why is SMB signing a defence against relay rather than against credential theft?**

<details><summary>Answer</summary>
It does not stop an attacker obtaining a challenge-response, but it prevents them relaying it to another server,
because the relayed session cannot produce a valid signature.
</details>

**5. What makes a krbtgt reset effective, and why twice?**

<details><summary>Answer</summary>
The krbtgt key signs TGTs; resetting it invalidates forged tickets. Two resets with replication and a wait ensure the
old key is no longer accepted across all DCs and that tickets signed with the first new key are also invalidated.
</details>

## Summary

- AD is a trust graph; privilege lives in groups, ACLs and delegation.
- Kerberos issues tickets; the KDC's response is encrypted with the service key, which is why roasting works offline.
- NTLM persists; signing and channel binding break relay.
- Common misconfigurations map to specific controls and specific events.
- Detection depends on advanced audit and SACLs; the patterns are ticket anomalies, logon bursts, group changes and
  directory modification.
- Harden with gMSA, tiering, LAPS, delegation hygiene and protocol signing, and verify each change by query.
- Recovery is ordered: isolate, preserve, reset krbtgt twice, reset credentials, rebuild Tier 0, check persistence.

## Next

[LAB-502-01](lab-01-build-domain.md) builds the isolated domain this module assumes, with the isolation proof first.

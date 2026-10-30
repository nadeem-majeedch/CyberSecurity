---
title: "Cloud Security Fundamentals"
description: "Shared responsibility, identity as the perimeter, policy evaluation, storage exposure, segmentation, secrets, audit logs, misconfiguration classes and workload security."
module_code: CYB-503
level: 5
kind: lesson
prerequisites: [CYB-503]
estimated_minutes: 90
difficulty: advanced
safety: conceptual
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [cloud, iam, shared-responsibility, audit-logs, containers]
---

# Cloud Security Fundamentals

## Learning objectives

1. Assign a given control to provider or customer responsibility, and justify it.
2. Explain how a request is authorised, and where an explicit deny lands in the order.
3. Identify the three ways an object store becomes public.
4. Describe what audit logs do and do not record, and how attackers disable them.
5. Classify the misconfiguration patterns behind most cloud incidents.
6. Explain container isolation limits and the controls that compensate.

## Prerequisites

Networking (CYB-204), Linux permissions (CYB-205), web authorization and access control (CYB-304), and familiarity
with JSON or YAML.

## 1. Shared responsibility, used properly

Providers publish a split: the provider secures *of* the cloud, the customer secures *in* the cloud. That sentence is
true and useless on its own. Use it as a question:

| Question | If the answer is "provider" | If the answer is "you" |
| --- | --- | --- |
| Who patches the hypervisor? | Provider | — |
| Who patches the guest OS? | — | You (IaaS) |
| Who configures the bucket policy? | — | Always you |
| Who decides who can read the object? | — | Always you |
| Who patches the managed database engine? | Provider (PaaS) | You choose the version and the network exposure |
| Who writes the application? | — | You |

The line moves with the service model, and it moves *with configuration*, not with marketing. Two customers on the
same managed database can have wildly different exposure because one allowed `0.0.0.0/0` on the security group.

**The failure mode to name:** "it's managed, so it's secure". Managed means the provider operates it. It does not mean
your data, your identities, or your network rules are safe.

## 2. Identity is the perimeter

In a data centre, an attacker who reaches the network is inside. In cloud, reaching the network gets you to a login
prompt; the credential decides everything after that. This has consequences:

- Credential theft is the primary escalation path, not a preliminary.
- Over-broad roles turn one compromised workload into an account-wide incident.
- Long-lived access keys are the equivalent of a password taped to a monitor, with no expiry and no MFA.

### How a request is authorised

Every API call reduces to: **principal** + **action** + **resource** + **context** → allow or deny.

1. Collect identity-based policies attached to the principal (user, role, group).
2. Collect resource-based policies (bucket policy, key policy, queue policy).
3. Evaluate: **explicit deny wins**, then explicit allow, then implicit deny.
4. Apply boundaries — permissions boundaries, session policies, organisation SCPs — which can only *reduce*.
5. Apply conditions (source IP, MFA present, TLS required, time, resource tag).

Two consequences that catch people:

- **A wildcard action in a condition is not a restriction.** `"Action": "*"` with `"Condition": {"Bool": {"aws:SecureTransport": "true"}}` allows everything over TLS.
- **Resource policies can grant access identity policies never would.** A bucket policy with `"Principal": "*"` and a `GetObject` allow is public regardless of who has IAM permissions.

### The IAM questions to ask of any policy

| Question | Why |
| --- | --- |
| What is the broadest action? | `s3:*` is a finding even if the resource is narrow |
| What is the broadest resource? | `"Resource": "*"` plus a write action is privilege escalation |
| Who is the principal? | `*` or `"AWS": "*"` means anonymous |
| Are there conditions? | No condition on a write is a finding |
| Is it a role or a user? | Roles are short-lived; users with keys are not |
| Can it grant more permissions? | `iam:CreatePolicyVersion`, `iam:PassRole`, `sts:AssumeRole` are escalation primitives |

`iam:PassRole` deserves its own line: it lets a principal hand a powerful role to a service it controls, which is
privilege escalation without ever changing a policy.

## 3. Object storage: the three ways to become public

1. **ACL** on the bucket or object (`public-read`) — legacy, still works, still causes incidents.
2. **Bucket policy** with an anonymous principal — `"Principal": "*"` plus `s3:GetObject` on `arn:aws:s3:::bucket/*`.
3. **Account-level public access block disabled**, which permits the first two.

Detection is a request, not an opinion:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://BUCKET.s3.example.com/known-object.txt
# 200 = public. 403 = not public to you.
```

In the labs you do this against local MinIO, which uses the same policy language and the same evaluation rules.

Other storage controls worth knowing:

- **Encryption at rest** protects against disk theft and provider-side mistakes, not against a misconfigured policy.
- **Versioning** turns deletion into a recoverable event, and is the difference between a ransomware incident and an
  outage. It also means "deleted" data still exists — relevant to privacy requirements.
- **Object lock / immutability** is the only reliable defence against an attacker with delete rights.
- **Presigned URLs** are bearer tokens: whoever holds the link has the access, until it expires. Long expiry plus
  logged URLs equals a leak.

## 4. Network controls

Security groups are stateful allow-lists attached to interfaces; network ACLs are stateless and subnet-level. In
practice:

| Misconfiguration | Why it matters |
| --- | --- |
| `0.0.0.0/0` on 22 or 3389 | Internet-wide brute force, immediately |
| `0.0.0.0/0` on a database port | The most common cause of data exposure |
| Wide egress | Data exfiltration and command-and-control need outbound |
| Flat network | One compromised workload reaches everything |
| Public subnet for internal services | Exposure by topology, not policy |

Segmentation is the same discipline as CYB-405, applied to a different control plane: decide which flows are required,
allow those, deny the rest, and prove the deny works.

**Instance metadata** is a special case: the metadata service hands out credentials to anything that can reach it.
Requiring the session-token variant (IMDSv2) raises the bar against server-side request forgery, which is why CYB-304's
SSRF lesson connects directly here.

## 5. Secrets

A secret is anything that grants access: keys, tokens, connection strings, private keys.

| Bad | Why | Better |
| --- | --- | --- |
| Secret in source code | Copied into history, forks and CI logs forever | Secret manager, injected at runtime |
| Secret in a container image | Every layer is downloadable | Runtime injection, not build-time |
| Secret in an environment variable that is dumped | Crash handlers and `/proc` expose it | File-based injection with tight permissions |
| Long-lived access key | No expiry, no MFA, no attribution | Short-lived role credentials |
| Secret in a URL or query string | Logged by proxies and servers | Header or signed request |
| Same secret everywhere | One leak compromises all environments | Per-environment, per-service secrets |

Rotation is part of the control: a secret you cannot rotate is a secret you cannot respond to an incident with.

## 6. Audit logs

Provider audit logs (CloudTrail and equivalents) record the **control plane**: who called which API, from where, with
which identity, and whether it succeeded. They generally do **not** record what happened inside your application, and
data-plane logging (object reads) is often a separate, extra-cost setting.

What to alert on:

- Logging configuration changed — `StopLogging`, `DeleteTrail`, `PutBucketPolicy` on the log bucket.
- Identity changes — `CreateUser`, `CreateAccessKey`, `AttachUserPolicy`, `CreateLoginProfile`.
- Policy loosened — any policy change adding `*` principal or `*` action.
- Root/break-glass account used.
- Access from a new country or ASN, especially for privileged identities.
- A burst of `AccessDenied` followed by success — enumeration then exploitation.

The detection engineering from CYB-404 applies unchanged: write the rule, test it against benign data, then tune.

## 7. The misconfiguration classes

| Class | Example | Static check |
| --- | --- | --- |
| Public storage | Bucket ACL public-read | `checkov` CKV_AWS_20, CKV_AWS_53-55 |
| Open management port | SG ingress 0.0.0.0/0:22 | CKV_AWS_24 |
| Wildcard IAM | `Action: "*"`, `Resource: "*"` | CKV_AWS_1, CKV_AWS_62 |
| Unencrypted data | Volume or bucket without encryption | CKV_AWS_19, CKV_AWS_3 |
| No logging | Trail absent or not multi-region | CKV_AWS_67, CKV_AWS_35 |
| Container runs as root | `USER` missing in Dockerfile | CKV_DOCKER_3 |
| Hardcoded secret | Key in `main.tf` | `checkov --framework secrets` |

Static analysis finds these before deployment, which is the point: the cheapest fix is the one that never ships.

## 8. Containers and workloads

A container is a process with namespaces and, usually, a shared kernel. That means:

- Kernel exploits cross container boundaries; a shared kernel is a shared risk.
- Running as root inside the container is root on the host if the container escapes, and root on any mounted volume.
- `--privileged` and mounting the Docker socket are equivalent to handing over the host.
- Image layers are forever: a secret deleted in a later layer is still in the earlier one.
- Supply chain matters: an unsigned base image is an unverified dependency.

Minimum runtime posture: non-root user, read-only root filesystem, no new privileges, dropped capabilities, no host
network, resource limits, and a pinned image digest that you scan before deploying.

## 9. Cost awareness

Cloud labs fail when they are expensive. The cost-bearing resources are compute hours, NAT gateways (charged per hour,
whether used or not), egress, and storage requests. Identity, policy, IaC scanning and audit-log analysis are
free-tier-friendly or free. If you repeat these labs on a real provider: use one region, tear down the same day, set a
budget alert, and never leave a NAT gateway running.

## Common mistakes and troubleshooting

| Mistake | Symptom | Correct approach |
| --- | --- | --- |
| Assuming an allow policy is enough | Access denied anyway | Check for explicit deny, boundary or SCP |
| Testing public access with a browser cache | False "still public" | `curl -H 'Cache-Control: no-cache'` |
| Ignoring the resource policy | Identity policy correct, access still possible | Check bucket/key policy for `Principal: *` |
| Treating `checkov` output as truth | Fixing false positives | Read the check, accept with a documented reason if wrong |
| Scanning an image you did not build | Wrong result | Scan the exact digest you deploy |
| Rotating a secret without revoking the old one | Old credential still works | Revoke, then rotate |

## Summary

Cloud security is authorization at scale: identity is the perimeter, configuration is the attack surface, and audit
logs are the only reliable record. Static analysis moves the fix earlier; least privilege limits the blast radius when
something else fails; and local emulation lets you practise all of it without a bill.

## Review questions

1. A managed database is patched by the provider. Name two things you are still responsible for that can expose it.
2. Why does an explicit deny beat an allow, and what does that imply about troubleshooting "access denied"?
3. Give the three routes to a public bucket and the single account-level setting that blocks two of them.
4. What does `iam:PassRole` let an attacker do, and why is it a privilege escalation rather than a policy change?
5. Which cloud audit events would you alert on first, and what false positives would that alert produce?
6. Why is a secret in a deleted container layer still a leaked secret?

## Knowledge check

1. A bucket policy allows `s3:GetObject` to `"Principal": "*"`, and account public access block is enabled. Can an
   anonymous user read the object?
2. An identity policy allows `s3:*` on `arn:aws:s3:::logs/*`, and a bucket policy denies `s3:DeleteObject` on the same
   prefix. Can the user delete an object?
3. Your container runs as root with a read-only root filesystem and no new privileges. Name one remaining risk.
4. Audit logging is enabled in one region only. What class of activity can go unrecorded?

<details>
<summary>Answers</summary>

1. No. The public access block overrides the anonymous grant.
2. No. Explicit deny wins.
3. Kernel-level escape, or write access to a mounted volume, or a vulnerable application in the container.
4. Activity in other regions, where resources and API calls are logged separately.

</details>

## Next lesson

[LAB-503-01 · Least Privilege and Object Storage](lab-01-identity-and-storage.md) — write a policy, prove the allowed
action works, and prove the denied action fails.

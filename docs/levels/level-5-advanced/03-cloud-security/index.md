---
title: "CYB-503 · Cloud Security"
description: "Shared responsibility, least-privilege identity, object storage, segmentation, secrets, audit logging, misconfiguration detection and container hardening — all on local emulation."
module_code: CYB-503
level: 5
kind: module
prerequisites: [CYB-202, CYB-304]
estimated_minutes: 900
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-503-01, LAB-503-02, LAB-503-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [cloud, iam, s3, containers, misconfiguration, secrets]
---

# CYB-503 · Cloud Security

## Why this module exists

Cloud security is mostly ordinary security with three changes: identity *is* the perimeter, configuration is code, and
a single wrong line is public to the internet in seconds. The concepts transfer between providers; the console does
not. So this module teaches the concepts on local emulation you can break and rebuild, and teaches you to read the
policy documents providers actually use.

**No cloud account is required, and none should be created for these labs.**

## Module outcomes

By the end you can:

1. Place a control on the right side of the shared responsibility line and say why it is there.
2. Write a least-privilege policy and demonstrate that the allowed action works and the denied action fails.
3. Configure object storage so anonymous access is impossible, and prove it with a request.
4. Detect and fix the misconfigurations that cause most cloud breaches, using static analysis.
5. Manage secrets so they are not in code, images, or logs.
6. Use audit logs to reconstruct who changed what, and detect logging being disabled.
7. Harden a container image and its runtime, and verify both by inspection and by test.

## Lessons and labs

| Page | Type | Time |
| --- | --- | --- |
| [Cloud Security Fundamentals](01-cloud-security-models.md) | Lesson | 90 min |
| [LAB-503-01 · Least Privilege and Object Storage](lab-01-identity-and-storage.md) | Lab | 180 min |
| [LAB-503-02 · Misconfiguration Detection and Audit Logs](lab-02-misconfiguration-and-audit.md) | Lab | 180 min |
| [LAB-503-03 · Final Challenge: Container Hardening](lab-03-container-hardening.md) | Lab | 180 min |

## What you need

- A Linux VM (Kali or Ubuntu) with Docker, and at least 4 GB RAM.
- Python 3.10+ with `boto3`, and the MinIO client `mc`.
- `checkov` and `trivy` — installed in the labs from official releases.
- No cloud account, no credit card, no free-tier signup.

## Cost, stated plainly

Everything here runs locally at zero cost. If you later choose to repeat these exercises on a real provider, the
billable items are object storage requests and egress, NAT gateways, and running instances — not the identity and
policy work. The lessons mark which labs map to a paid service and which do not.

## Assessment

The module rubric sits inside each lab. LAB-503-03 is the module's practical assessment, and the level's own
assessment is the [Level 5 integrated assessment](../../../assessments/level-5-assessment.md) — see
[how assessment works](../../../policies/assessment-format.md) for the criteria.

## Where this fits

Depends on networking (CYB-204) and web security (CYB-304) — bucket policies and IAM are authorization problems in a
different syntax. Feeds the capstone's cloud and container work.

## Related

- [LAB-503-01](lab-01-identity-and-storage.md) · [LAB-503-02](lab-02-misconfiguration-and-audit.md) · [LAB-503-03](lab-03-container-hardening.md)
- [Level 5 overview](../../level-5.md) · [Lab catalogue](../../../labs/index.md) · [Glossary](../../../resources/glossary.md)

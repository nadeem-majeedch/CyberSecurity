---
title: "CYB-205 · OpenSSH and Secure Remote Administration"
description: "Key-based authentication, hardened sshd configuration, and file transfer you can defend."
module_code: CYB-205
level: 2
kind: reference
prerequisites: [CYB-203]
estimated_minutes: 720
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-205-01, LAB-205-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [ssh, openssh, keys, hardening]
---

# CYB-205 · OpenSSH and Secure Remote Administration

**Level 2** · 12 hours · **Prerequisites:** [CYB-203](../03-host-discovery-and-enumeration/index.md)

## Why this module exists

Every lab from here on assumes you can administer a machine you are not sitting in front of. SSH is how that
happens — and it is also one of the most attacked services on any internet-facing host. Learning it properly means
learning both the client workflow and the server configuration that makes the workflow safe.

## Module outcomes

- Generate and protect an Ed25519 key pair; authenticate without a password.
- Explain what `authorized_keys`, `known_hosts` and `~/.ssh/config` each do.
- Read `sshd_config` and justify each hardening directive.
- Verify a configuration change without locking yourself out.
- Transfer files with `scp`/`sftp` and explain why `rsync` is often better.
- Describe a port-forwarding use case and its security implications.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [SSH Keys, Configuration and Hardening](01-ssh-keys-and-hardening.md) | 4 h |
| Lab | [LAB-205-01 · Key-Based Authentication](lab-01-key-based-auth.md) | 4 h |
| Lab | [LAB-205-02 · Audit and Harden sshd](lab-02-harden-sshd.md) | 4 h |

## What you need

- `openssh-client` and `openssh-server` 9.x.
- Two lab VMs on `192.0.2.0/24`.
- A snapshot taken before changing `sshd_config`.

!!! warning "Snapshot before you touch sshd_config"
    A misconfigured `sshd` is the classic way to lock yourself out of a remote host. Take the snapshot first, and
    test with a second session open.

## Assessment

Two labs, rubric-marked. LAB-205-02 requires a before/after configuration diff with evidence that the hardened
service still works.

## Related

- [CYB-203 · Host Discovery and Service Enumeration](../03-host-discovery-and-enumeration/index.md)
- [CYB-206 · Host Inspection and Hardening Assessment](../06-host-inspection-and-hardening/index.md)
- [Lab Safety Guide](../../../start-here/lab-safety.md)

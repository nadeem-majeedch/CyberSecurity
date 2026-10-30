---
title: "CYB-404 · Detection Engineering and SIEM"
description: "Build a local SIEM, write detections as testable hypotheses, correlate events across sources, and tune noise without creating blind spots."
module_code: CYB-404
level: 4
kind: reference
prerequisites: [CYB-403, CYB-402]
estimated_minutes: 840
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-404-01, LAB-404-02, LAB-404-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [detection-engineering, siem, wazuh, sigma, correlation, false-positives, attck]
---

# CYB-404 · Detection Engineering and SIEM

**Level 4** · 14 hours · **Prerequisites:** [CYB-403](../03-hardening-and-patching/index.md), [CYB-402](../02-endpoint-telemetry/index.md)

## Why this module exists

A detection rule is a hypothesis about attacker behaviour, expressed as a query, and tested against data. Most
rules in the wild are written as though the middle step does not exist: someone copies a query, it produces alerts,
and nobody ever checks whether it fires on the behaviour it claims to detect or on everything else.

This module builds the loop properly. You will deploy a local SIEM, write rules as portable Sigma specifications,
implement them in the SIEM, and test each one four ways — positive, negative, no-data, and regression. You will then
correlate across sources, where the interesting failures live: clock skew, duplicate events, and sequences that look
malicious in isolation but are routine on a Tuesday.

## Module outcomes

By the end of this module you can:

- State a detection as a falsifiable hypothesis naming behaviour, data source, and expected observable.
- Explain why field normalisation decides whether correlation works at all.
- Write a Sigma rule with metadata a reviewer can act on, and a Sigma correlation rule for a sequence.
- Implement the same logic natively in Wazuh, and validate it with `wazuh-logtest` before trusting it.
- Run four tests against every rule, including a no-data test that proves the rule would not silently pass.
- Tune a noisy rule without allowlisting the behaviour you were trying to catch.
- Produce a detection report with coverage claims that survive scrutiny.

## Lessons and labs

| # | Item | Time |
| --- | --- | --- |
| 01 | [From Hypothesis to Tested Rule](01-detection-engineering.md) | 4 h |
| Lab | [LAB-404-01 · Deploy a Local SIEM and Ingest Telemetry](lab-01-wazuh-deployment.md) | 3 h |
| Lab | [LAB-404-02 · Write, Convert and Test a Detection](lab-02-sigma-rule.md) | 3.5 h |
| Lab | [LAB-404-03 · Correlation, Tuning and a Detection Report](lab-03-correlation-and-tuning.md) | 3.5 h |

## What you need

- A monitoring VM (`lab-siem`) with **8 GB RAM and 4 cores** for a single-node Wazuh deployment; Wazuh's own Docker
  documentation states these as the single-node requirements. With the SIEM running you cannot also run two other
  VMs comfortably on a 16 GB host — sequence your labs.
- Wazuh **4.14.9**, deployed from the official `wazuh-docker` single-node compose file on Ubuntu 24.04.
- `lab-ubuntu` as the monitored agent.
- Sigma CLI (`sigma-cli`) with `pySigma`, and Python 3.10+ for validation.
- The indexer needs `vm.max_map_count=262144` — set it before first start or the indexer will fail to boot.

## A note on tooling choices

Wazuh is used because it is open source, runs entirely locally, ships decoders and rules you can read, and includes
`wazuh-logtest` — an interactive rule tester that makes the testing discipline in this module practical rather than
theoretical.

Sigma is used as the **portable specification**, not as a magic converter. As of 2026 there is **no official pySigma
backend for Wazuh**; pySigma targets include Splunk, Elastic, OpenSearch, Sentinel and others, and Wazuh conversion is
served by community tools of varying quality. The module therefore teaches you to write the Sigma rule as the
reviewable specification, convert where an official backend exists, and hand-implement the Wazuh XML — validating it
with `wazuh-logtest` instead of trusting a converter.

## Assessment

LAB-404-02 requires four tests per rule, with the negative test being a real benign event you generated. LAB-404-03
requires a correlation rule plus a tuning decision you can defend, and a detection report with a coverage table that
distinguishes "rule exists" from "behaviour observed and caught".

## Where this fits

[CYB-405](../05-network-defence/index.md) adds the network sensor that supplies the other half of the correlation.
[CYB-407](../07-incident-response/index.md) consumes these alerts as incident evidence, and expects the timestamps to
line up.

## References

1. Wazuh 4.14.9 documentation — single-node Docker deployment, requirements, agent enrollment, rules and decoders,
   `wazuh-logtest`. <https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html> Accessed
   2026-10-29.
2. SigmaHQ — rule specification and correlation rules. <https://sigmahq.io/> Accessed 2026-10-29.
3. pySigma / sigma-cli — supported backends. <https://github.com/SigmaHQ/pySigma> Accessed 2026-10-29.
4. MITRE ATT&CK v20.0. <https://attack.mitre.org/> Accessed 2026-10-29.
5. Elastic Common Schema (ECS) — field naming reference. <https://www.elastic.co/guide/en/ecs/current/index.html>
   Accessed 2026-10-29.
6. NIST SP 800-92 — Guide to Computer Security Log Management. Accessed 2026-10-29.

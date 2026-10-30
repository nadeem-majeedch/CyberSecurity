---
title: "Baselines, Hardening and Patch Priority"
description: "How published baselines become verified controls, and how to order patching when you cannot do all of it today."
module_code: CYB-403
level: 4
kind: lesson
prerequisites: [CYB-402]
estimated_minutes: 180
difficulty: intermediate
safety: none
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [baselines, hardening, cvss, kev, epss, patch-management]
---

# Baselines, Hardening and Patch Priority

## What this lesson covers

1. What a security baseline is, and the four documents that most baselines derive from.
2. How to measure a host against a baseline without breaking it.
3. How to turn a finding into a decision: apply, adapt, compensate, or accept with a signature.
4. Why CVSS is not risk, and what KEV, EPSS, exposure and asset value add.
5. What changed at NVD in 2026, and why missing scores are now normal.
6. How to define patch SLAs you can actually meet, and the metrics that prove it.

## Why it matters

A baseline is the cheapest security control an organisation owns: it costs configuration, not licences. It is also
the easiest to fake. "We follow CIS Level 1" is a claim; an assessment report with a date, a profile ID, a result
count, and a signed exception list is evidence. The gap between those two statements is most of this module.

Patching has the same property. Every organisation says it patches promptly. Few can show the median time from
publication to deployment, or explain why the three oldest open findings are still open.

## 1. What a baseline is

A **security baseline** is a documented set of configuration settings for a defined system role, with a rationale for
each setting. Three properties matter:

- **Role-specific.** A domain controller, a developer workstation and a public web server need different settings.
  Applying a server baseline to a laptop produces friction without much protection.
- **Verifiable.** Each setting must be checkable by a machine, or it is an opinion. "Disable unnecessary services"
  is not a baseline item; "SMBv1 server support is disabled" is.
- **Owned.** Someone must be accountable for deviations. Baseline documents do not enforce themselves.

### The four sources you will meet

| Source | What it is | Cost and access | Best used for |
| --- | --- | --- | --- |
| **CIS Benchmarks** | Consensus configuration guidance per product and version, in Level 1/2 profiles | PDFs free for non-commercial use via a download form; CIS-CAT Lite is a free assessment tool, also behind a form | Broad, well-explained starting point with two strictness levels |
| **DISA STIGs** | US Department of Defense hardening requirements, with check and fix procedures | Public | High-assurance environments; excellent test procedures |
| **Vendor baselines** | Microsoft Security Baselines (in the Security Compliance Toolkit), distribution vendor guidance | Free | Settings the vendor will support, and GPO-native deployment |
| **SCAP content** | Machine-readable policy: ComplianceAsCode/content builds XCCDF + OVAL from CIS/STIG sources | Open source | Automated assessment and repeatable evidence |

These overlap heavily and disagree at the edges. That is normal: they were written for different threat models and
different operational constraints. Your job is not to pick the "correct" one but to pick one, document the choice,
and justify deviations.

!!! note "Why profile IDs matter"
    An assessment result is only meaningful with the exact profile and content version. Ubuntu 24.04 content in
    ComplianceAsCode 0.1.82 exposes profiles such as
    `xccdf_org.ssgproject.content_profile_cis_level1_server`. Profile contents change between releases, so a report
    that says "CIS Level 1: 82% compliant" without a content version cannot be compared with last quarter's number.

## 2. Measuring without changing anything

OpenSCAP evaluates a host against XCCDF rules, most of which are implemented as OVAL checks — read-only probes of
configuration and package state.

```bash
sudo apt install -y libopenscap8 openscap-scanner ssg-base ssg-debderived
oscap info /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml | head -40
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
  --results /tmp/403-results.xml \
  --report /tmp/403-report.html \
  /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml
```

Three outputs, three purposes:

- **stdout** — `pass`, `fail`, `notapplicable`, `notchecked`, `error` per rule. `notchecked` usually means a missing
  dependency or an unsupported platform, and it is **not** a pass.
- **`--results`** — ARF XML, the machine-readable record. This is the artefact you keep.
- **`--report`** — HTML for humans, including the rule rationale and fix text.

The exit status is `2` when any rule fails. That is expected, not an error: do not wrap the command in something that
aborts the script on non-zero status.

**Lynis** is a useful second opinion because it checks different things — installed software age, kernel hardening,
file permissions, and configuration smells that benchmarks do not cover:

```bash
sudo apt install -y lynis
sudo lynis audit system --quick
```

Lynis prints a **hardening index** and lists suggestions and warnings. Treat the index as a trend line for one host,
not a grade, and never compare it to a benchmark percentage — they measure different sets.

**When the tools disagree**, the disagreement is the finding. Example: OpenSCAP passes "SSH root login disabled"
because `PermitRootLogin no` is set in a drop-in file, while Lynis warns because it read only `sshd_config`. The
effective configuration is what `sshd -T` prints, which is why verification comes before remediation.

## 3. From finding to decision

Do not start at the top of the results file. Classify every failure into one of four buckets:

| Decision | When | Artefact |
| --- | --- | --- |
| **Apply** | Control fits the role, cost is acceptable | Change + before/after evidence |
| **Adapt** | Intent fits, the specific setting does not (different path, different service) | Change + note explaining the adaptation |
| **Compensate** | Control is impractical here, but the risk is covered elsewhere | Compensating control named, with how it was verified |
| **Accept** | Risk is understood, low, and owned | Exception entry, approved, with an expiry date |

An **exception register** entry needs six fields: the rule ID, the reason, the compensating control (or "none"), the
owner, the approval, and the review date. An exception without an expiry date is a permanent hole with paperwork
attached.

!!! warning "Never run generated fix scripts blind"
    `oscap xccdf generate fix` produces a remediation script, and the SSG remediation for a server profile can
    disable services you need, change SSH settings that lock you out, or tighten permissions on files an application
    writes to. Read the fix, apply one rule at a time, keep a snapshot, and keep a second session open before you
    touch SSH or the firewall.

## 4. Change discipline

The loop is: **snapshot → change one control → verify → record → repeat.**

**Verification means querying the state, not observing that the command succeeded.** On Linux, `sshd -T` prints the
effective configuration; `systemctl is-enabled` proves a service's boot state; `auditctl -l` lists loaded audit rules;
`stat -c '%a %U:%G'` proves permissions.

**Lockout is the classic failure.** Before changing SSH: keep your current session open, apply the change, open a
**new** session to test, and only then close the old one. If you disable password authentication before confirming
key-based login works, you will be rebuilding the VM.

On Windows, the same discipline applies with different tools:

| Control | Configure | Verify by |
| --- | --- | --- |
| Command-line process auditing | `auditpol /set /subcategory:"Process Creation" /success:enable` plus the process-creation policy | `auditpol /get /subcategory:"Process Creation"` and a 4688 event containing a command line |
| PowerShell script block logging | Registry/GPO under `ScriptBlockLogging` | Event ID 4104 appears with the script text after running a script |
| SMBv1 removed | `Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol` | `Get-SmbServerConfiguration` and a failed SMBv1 negotiation |
| SMB signing required | `Set-SmbServerConfiguration -RequireSecuritySignature $true` | `Get-SmbServerConfiguration` |
| Attack surface reduction rules | `Add-MpPreference -AttackSurfaceReductionRules_Ids <GUID> -AttackSurfaceReductionRules_Actions Enabled` | `Get-MpPreference` shows the ID and action; Defender operational log shows 1121/1122 when a rule fires |
| Local administrator password rotation | **Windows LAPS**, built into Windows 11 23H2 and later | LAPS policy state and password rotation event |

Two notes on that table. Legacy Microsoft LAPS (the MSI product) is deprecated; use the built-in Windows LAPS. And an
ASR rule's *configuration* is easy to prove while its *effect* depends on the rule, the application and the Defender
platform version — so report configuration state as configuration state, and test the effect separately where you can.

## 5. Three different problems people call "a vulnerability"

- **Missing patch** — the software is old and a fixed version exists.
- **Misconfiguration** — the software is current and configured insecurely.
- **Design weakness** — both are current and correct, and the architecture is still risky (no segmentation, shared
  admin accounts, a debug endpoint by design).

They are fixed by different processes: patch management, configuration management, and engineering change. Mixing
them produces the familiar outcome where a "remediated" scan is clean while the exploitable path remains.

## 6. Prioritisation: severity is not risk

**CVSS** produces a severity score from characteristics of the vulnerability itself. Version 4.0 (November 2023)
removed the Temporal metric group and replaced it with **Threat** and **Environmental**, plus a **Supplemental**
group that is not scored. Crucially, the *base* score assumes nothing about your environment: a 9.8 that requires
local access to a service you do not run is not your emergency.

Risk adds four things the base score cannot know:

1. **Exploitation in the wild** — is someone actually using it?
2. **Probability of exploitation** — how likely is exploitation activity in the near term?
3. **Exposure** — internet-facing, internal, or requires prior access?
4. **Value and blast radius** — what does this asset hold, and what trusts it?

### The two data sources worth wiring in

- **CISA KEV** — the Known Exploited Vulnerabilities catalog, actively maintained, with a JSON feed at
  `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`. Membership means observed
  exploitation. US federal civilian agencies have binding remediation timelines for KEV entries; for everyone else
  it is the strongest single signal that a patch is urgent.
- **FIRST EPSS** — a probability, from 0 to 1, that exploitation activity for a CVE is observed in the next 30 days,
  plus a percentile. The current model is **v5** (publishing since 15 June 2026); the API path is still `v1`:
  `https://api.first.org/data/v1/epss?cve=CVE-2021-44228`. EPSS is a prioritisation aid, not a verdict: a low score
  on a KEV-listed CVE means "the model and reality disagree", and reality wins.

### What changed at NVD in 2026

NVD supports CVSS v4.0 and displays it when available. But since **15 April 2026** it no longer attempts to enrich
every CVE. Enrichment effort goes to KEV-listed CVEs, software used by the US federal government, and critical
software under Executive Order 14028; other records may be marked "Lowest Priority — not scheduled for immediate
enrichment", and backlogged CVEs published before 1 March 2026 moved to "Not Scheduled". NVD also stopped routinely
adding its own severity score when the CNA already supplied one.

Three consequences for your process:

- A missing CVSS score is now **normal**, not a data error. Your tooling must fall back to the CNA score and say so.
- The absence of a score is not evidence of low risk — it often means "nobody has got to it".
- Anything that ranks by "CVSS present" will systematically deprioritise exactly the long tail where quiet
  exploitation lives. Rank by exploitability signals first, then by score.

### A worked ordering

Four findings on one estate. The right order is not the CVSS order.

| Finding | CVSS | KEV | EPSS | Exposure | Reasoning |
| --- | --- | --- | --- | --- | --- |
| B | 7.5 | **yes** | 0.94 | Internet-facing VPN | Known exploitation, trivial access path: patch tonight |
| C | 8.1 | no | 0.55 | Reachable pre-auth from the LAN | High exploitation probability and no authentication barrier |
| D | CNA 6.5; no NVD score | no | 0.31 | Local privilege escalation on a shared jump host | Modest score, but the jump host is the path to everything |
| A | 9.8 | no | 0.02 | Internal service behind authentication, not reachable | Highest score, lowest plausible path: schedule, do not panic |

Two defensible inversions: D outranks A because of blast radius, and B outranks C because observed exploitation beats
modelled probability. Write those reasons down — the ordering is the deliverable, not the number.

## 7. Patch SLAs that survive contact with reality

Define tiers by signal, not by vendor severity label:

| Tier | Trigger | Target | Change path |
| --- | --- | --- | --- |
| Emergency | KEV-listed and exposed, or active exploitation reported | 24–72 h | Out-of-band, minimal testing, rollback ready |
| Critical | CVSS ≥ 9.0 with a plausible path, or EPSS ≥ 0.5 and exposed | 7 days | Accelerated but tested |
| Standard | Other security updates | 30 days | Normal change window |
| Deferred | Not reachable, compensated, or vendor-blocked | 90 days with review | Exception, reviewed quarterly |

Then measure what you promised:

- **% of findings remediated within SLA** — the headline, segmented by tier.
- **Median time to remediate**, not mean: one forgotten year-old finding distorts an average into uselessness.
- **Age of open exceptions** — the number that reveals whether the exception process is a decision or a drawer.
- **KEV coverage** — how many KEV entries apply to your estate, and how many are closed.

## Common misconceptions

| Belief | Reality |
| --- | --- |
| "A higher CIS level is always better" | Strictness has a cost in usability and support. Level 2 on a developer laptop often ends in exceptions or a rollback. |
| "The scanner said compliant, so we are secure" | Scanners check settings, not whether the setting is enforced, monitored, or bypassed by another path. |
| "CVSS 9.8 means patch now, 6.5 means later" | Exposure and exploitation change the order constantly. KEV entries routinely score 7–8. |
| "No CVSS score means low risk" | Since 2026, it often means NVD has not enriched the record. |
| "We applied the baseline, so we are done" | Baselines drift. Without a scheduled re-assessment, you have a historical claim. |
| "Exceptions are failures" | Unowned exceptions are failures. Owned, dated, reviewed exceptions are how hardening survives real constraints. |

## Key terms

**Baseline** · **XCCDF** · **OVAL** · **ARF** · **profile** · **deviation** · **exception register** · **ASR rule** ·
**LAPS** · **CVSS base/threat/environmental** · **KEV** · **EPSS** · **exposure** · **blast radius** · **MTTR** ·
**patch SLA** · **compensating control**

## Check your understanding

**1. A scan reports 140 failures. What are your first three actions?**

<details><summary>Answer</summary>
Record the profile ID and content version, then separate `fail` from `notchecked`/`error` (the latter are coverage
gaps, not compliance). Then triage by role relevance and lockout risk before changing anything, and snapshot.
</details>

**2. Why can OpenSCAP and Lynis disagree about the same SSH setting?**

<details><summary>Answer</summary>
They read different sources. Lynis may parse `sshd_config`; OpenSCAP's OVAL may account for `Include` drop-ins. The
effective configuration is what `sshd -T` reports, so verify there before deciding.
</details>

**3. Your highest CVSS finding is internal-only and authenticated. A 7.4 is KEV-listed on the VPN. Which is first?**

<details><summary>Answer</summary>
The KEV entry: observed exploitation plus an internet-facing entry point outweighs a higher score with no reachable
path. Document the reasoning.
</details>

**4. What does an EPSS score of 0.02 on a KEV-listed CVE mean for your decision?**

<details><summary>Answer</summary>
That the model and observed reality disagree. KEV reflects confirmed exploitation, so treat the CVE as urgent and
treat the low score as a reason to check your EPSS pipeline, not a reason to wait.
</details>

**5. A vendor has not released a fix for a critical finding. What are your options?**

<details><summary>Answer</summary>
Compensating controls (remove exposure, add a WAF rule, disable the feature, segment the service), documented in an
exception with an owner and review date, plus monitoring for exploitation attempts. "Waiting" is only acceptable when
written down with a review date.
</details>

## Summary

- A baseline is role-specific, machine-verifiable, and owned; CIS, STIG, vendor and SCAP sources overlap and disagree.
- Measure read-only first, keep the ARF result, and treat `notchecked` as a gap.
- Decide per finding: apply, adapt, compensate, or accept with an expiry date.
- Change one control at a time and verify by querying state; keep a session open before touching SSH.
- CVSS is severity; risk adds exploitation, exposure, and blast radius. KEV is the strongest signal, EPSS the
  probabilistic one.
- Missing NVD scores are normal since April 2026 — rank by exploitability, never by score presence.
- SLAs by signal tier, measured with median time to remediate and exception age.

## Next

[LAB-403-01](lab-01-linux-baseline.md) puts the measure–change–verify loop on a real Ubuntu host with a real
profile.

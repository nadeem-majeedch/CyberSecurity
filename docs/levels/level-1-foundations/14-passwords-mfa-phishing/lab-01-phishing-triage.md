---
title: "LAB-114-01 · Triage Synthetic Phishing Emails"
description: "Classify three fictional phishing samples using a repeatable checklist, and document the evidence for each verdict."
module_code: CYB-114
level: 1
kind: lab
prerequisites: [CYB-114]
estimated_minutes: 45
difficulty: beginner
safety: local-only
lab_ids: [LAB-114-01]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [phishing, triage, awareness]
---

# LAB-114-01 · Triage Synthetic Phishing Emails

**Module:** CYB-114 · **Time:** 45 minutes · **Safety:** local-only · **Snapshot:** none required

!!! warning "Authorized scope — read before you begin"
    **What you may use:** the three fictional samples below. Every domain, address and credential in them is
    invented and uses reserved documentation domains (`.test`, `.invalid`) or documentation IP ranges.
    **What you must not do:** do not send these messages, do not register the domains, do not visit any URL
    that appears in a real email you receive, and do not analyse another person's mail without their consent.

    This is a reading exercise. Nothing is sent, clicked, or resolved.

## Objective

Classify three emails as phishing, legitimate, or needs-verification; cite at least three indicators for each
verdict; and write the recommendation you would give a colleague.

## Threat model

You are the recipient, not the attacker. The skill being assessed is analytic reading: sender identity, link
destination, urgency, and request type — not technical exploitation.

## Environment

- The three samples below, reproduced as plain text.
- A notes file. No mail client is required; if you use one, use your own mailbox and delete nothing.

## Sample A — "Document shared with you"

```text
From:     "SharePoint Notifications" <no-reply@sharepoint-docs.example.test>
Reply-To: support@sharepoint-docs.example.test
Subject:  [Action required] A document has been shared with you
Date:     Tue, 27 Oct 2026 03:14:22 +0500

A document titled "Salary_Review_2026.xlsx" has been shared with you.

Open document: http://sharepoint-docs.example.test/open?id=8f21c

You must sign in with your university credentials to view it.

If this was not you, ignore this message.
```

## Sample B — "Invoice overdue"

```text
From:     "Accounts - Zenith Supplies" <accounts@zenith-supplies.example.test>
Reply-To: accounts.billing@zenith-supplies.example.test
Subject:  Overdue invoice INV-2291 - payment required within 24 hours
Date:     Mon, 26 Oct 2026 11:02:09 +0500
Authentication-Results: spf=pass dkim=pass dmarc=pass header.d=zenith-supplies.example.test

Dear Procurement,

Our records show invoice INV-2291 (attached) remains unpaid. Please settle within
24 hours to avoid suspension of your account.

Attachment: INV-2291.html

Regards,
Accounts Team
```

## Sample C — "IT password expiry"

```text
From:     "IT Helpdesk" <it-helpdesk@university-portal.example.test>
Subject:  Your password expires today - revalidate now
Date:     Tue, 27 Oct 2026 08:40:11 +0500
Authentication-Results: spf=fail dkim=none dmarc=fail header.d=university-portal.example.test

Your account password will expire at 17:00 today. To keep access, revalidate your
credentials here:

    https://university-portal.example.test/verify?session=93ac

Failure to act will result in loss of email access.

IT Service Desk
```

## Procedure

### Step 1 — Set up the triage sheet

Create `triage.md` with one row per sample and these columns:

| Sample | Sender domain | Auth result | Link/attachment | Urgency | Request | Verdict | Confidence | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Step 2 — Apply the checklist to each sample

For each sample, work through the seven checks from the lesson in order:

1. Sender address versus display name.
2. Authentication results (SPF/DKIM/DMARC).
3. Link or attachment destination.
4. Urgency and threat.
5. Request type.
6. Context and plausibility.
7. Attachment type and risk.

**Guidance, not answers:** no single indicator decides a verdict. A `pass` result does not make an email safe
(Sample B), and a lookalike sender with no link still warrants verification (Sample A).

### Step 3 — Defang anything you quote

When you copy a URL into your notes, make it unclickable:

```text
hxxp://sharepoint-docs[.]example[.]test/open?id=8f21c
```

This is standard practice among analysts: it prevents accidental clicks when reports are shared.

### Step 4 — Write the recommendation

For each sample, one sentence a busy colleague could act on:

- "Report to IT; do not sign in from the link."
- "Verify by calling the number on the supplier's official site; do not open the HTML attachment."
- "Legitimate, but confirm the domain before responding." (Use this only if you genuinely concluded that.)

### Step 5 — Prioritise

Rank the three by risk if a user complied, and justify the order in two sentences.

## Evidence to collect

`triage.md` with the completed table, the seven-check notes, three recommendations, and the risk ranking.

## Verification

- [ ] Every row cites at least three specific indicators, not "looks suspicious".
- [ ] Verdicts are justified by evidence in the sample.
- [ ] URLs are defanged.
- [ ] Recommendations are actionable and do not require clicking anything.
- [ ] You distinguished a confident verdict from "needs verification", and named the verification step where you used it.

## Expected observations

Write your own table first. Then compare against this reasoning — the verdict matters less than whether your
evidence supports it, so a different verdict with stronger evidence can score full marks.

| Sample | Model verdict | Decisive evidence |
| --- | --- | --- |
| A — "Document shared with you" | **Phishing**, high confidence | Sender domain is `sharepoint-docs.example.test`, not the real service; `Reply-To` differs from `From`; an unsolicited "Salary_Review" lure aimed at curiosity; a plain `http://` link that asks you to "sign in with your university credentials" |
| B — "Invoice overdue" | **Phishing**, moderate confidence — or **needs verification** if you name the check | SPF, DKIM and DMARC all pass, so the sending domain is authentic *for that domain*; the request is still a 24-hour payment demand with an **HTML attachment**, which is a standard credential-harvesting container. Authentication proves the domain, not the intent |
| C — "IT password expiry" | **Phishing**, high confidence | `Authentication-Results` reports `spf=fail dkim=none dmarc=fail`; a deadline of 17:00 the same day; a credential link; the display name claims an internal helpdesk the domain does not belong to |

Two points that separate a competent answer from a lucky one:

- **B is the interesting case.** Accepting it because "the checks passed" is the mistake the sample exists to catch: SPF, DKIM and DMARC answer *was this domain used to send it*, not *is this request safe*. A "needs verification" verdict earns credit only if it names the out-of-band action — call the supplier on a number you already hold, or reach the accounts contact through your own records — not "ask the sender".
- **A and C fail for different reasons.** A is a lookalike domain that carries no `Authentication-Results` header at all — its absence is itself a finding. C is a convincing display name whose domain fails authentication outright. Say which of the seven checks caught each one, because the control you recommend differs: A needs link inspection and user reporting, C needs DMARC enforcement at the gateway.

A defensible risk ranking is C, then A, then B: C is one click from a working credential and claims internal authority, A is a credential harvest behind a curiosity lure, and B's impact depends on whether the recipient opens the attachment. Any order is acceptable if the justification is about **impact if the recipient complied**, and each recommendation should follow from it — C calls for a gateway block and a password reset for anyone who clicked, A for link inspection and user reporting, B for a supplier-verification call before any payment discussion.

## Teardown and reset

Nothing to revert — the lab is read-only. If you pasted the samples into a mail client for realism, delete
those drafts.

## Reflection

1. Which sample would fool most people, and why?
2. Why is an HTML attachment riskier than a plain text one?
3. What would a `pass` on all three authentication mechanisms still not prove?
4. Which single technical control would most reduce the impact of someone complying with Sample C?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Verdicts without evidence | Three indicators per sample, defensible verdicts | Distinguishes confidence levels and near-misses |
| Methodology | Judged by intuition | Applied the seven checks in order | Explains which checks were decisive and which were noise |
| Evidence | Notes unstructured | Completed table | Table plus defanged quotes and prioritisation reasoning |
| Safety | Clicked or forwarded samples | Read only | Read only, defanged, with explicit note on non-interaction |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Cannot see authentication results | Samples are plain text | Use the `Authentication-Results` line as given; real mail clients show it under "Show original" |
| Unsure about a domain | Lookalike design | Compare character by character; note substitutions and extra words |
| Tempted to call everything phishing | Uncertainty | Mark "needs verification" where evidence is genuinely ambiguous, and say what you would check |
| Notes contain clickable links | Habit | Defang with `hxxp` and `[.]` |

## Related

- [Passwords, MFA and Phishing](01-passwords-mfa-phishing.md)
- [LAB-114-02 · Assess a Password Policy](lab-02-password-policy.md)
- [Introduction to Security Logs and Troubleshooting](../15-security-logs-and-troubleshooting/index.md)

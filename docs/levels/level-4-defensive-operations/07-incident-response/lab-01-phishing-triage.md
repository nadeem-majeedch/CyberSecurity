---
title: "LAB-407-01 · Phishing Triage and Scope"
description: "Analyse a synthetic reported email, extract defensible indicators, determine who else received it, and decide containment with evidence."
module_code: CYB-407
level: 4
kind: lab
prerequisites: [CYB-407]
estimated_minutes: 150
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-407-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [phishing, email-headers, spf, dkim, dmarc, scope, containment, iocs]
---

# LAB-407-01 · Phishing Triage and Scope

## Scenario and background

A user forwards an email to the security team with the message "is this real?". The attachment is an HTML file, the
link goes to a login page, and the display name belongs to someone in finance.

The most common failure in phishing response is answering only the question asked. The user wants to know about
*their* email; you need to know how many other people received it, how many clicked, and whether anyone submitted
credentials — before you start blocking things and lose the ability to find out.

Everything in this lab is synthetic: the message, the domains, the gateway and proxy logs.

## Learning objectives

1. Parse message headers and explain the `Received` chain, `Reply-To`, and authentication results.
2. Extract and defang indicators, with a confidence for each.
3. Use gateway and proxy logs to determine scope and impact.
4. Decide containment in the right order: scope first, then block, then remediate credentials.
5. Write a triage record that another analyst could pick up.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | `email` and `hashlib` from the standard library |
| A text editor | any | Reading headers |
| `sha256sum` | coreutils | Attachment hash |

!!! warning "Authorized scope — read before you begin"
    **The email is fabricated.** Domains use `.example`, which cannot resolve on the internet. Do not visit any URL
    from the message, even defanged, and do not send the attachment anywhere.

    **No real mail infrastructure is touched.** The gateway and proxy logs are CSV files you create.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

A credential-phishing campaign against finance staff: a spoofed internal display name, a link to a lookalike login
page on an attacker-controlled domain, and an HTML attachment that redirects to the same page. The attacker's goal is
valid credentials, which are then used against the real service.

## Procedure

### 1. Create the evidence

`~/lab407/phish/reported.eml`:

```text
From: "Accounts Payable" <billing@lab-finance.example>
Reply-To: "Accounts Payable" <ap@lab-payments.example>
To: <student@lab-app.example>
Subject: URGENT: invoice INV-4071 requires approval today
Date: Wed, 29 Oct 2026 09:12:44 +0000
Message-ID: <4071.20261029@lab-finance.example>
Return-Path: <bounce@lab-payments.example>
Authentication-Results: mx.lab-app.example;
       spf=softfail (sender IP 192.0.2.200 not authorised for lab-finance.example)
       dkim=none; dmarc=fail (p=none) header.from=lab-finance.example
Received: from relay.lab-payments.example (relay.lab-payments.example [192.0.2.200])
       by mx.lab-app.example with ESMTPS id 4071abc;
       Wed, 29 Oct 2026 09:12:46 +0000
Content-Type: multipart/mixed; boundary="b4071"

--b4071
Content-Type: text/plain; charset="utf-8"

Please review the attached invoice and sign in to approve it today:
hxxp://portal.lab-finance[.]example/approve?id=INV-4071

--b4071
Content-Type: text/html; name="invoice_INV-4071.html"
Content-Disposition: attachment; filename="invoice_INV-4071.html"
Content-Transfer-Encoding: base64

PGh0bWw+PGJvZHk+PHNjcmlwdD53aW5kb3cubG9jYXRpb249J2h0dHA6Ly9wb3J0YWwubGFi
LWZpbmFuY2UuZXhhbXBsZS9hcHByb3ZlP2lkPUlOVi00MDcxJzwvc2NyaXB0PjwvYm9keT48
L2h0bWw+
--b4071--
```

Gateway and proxy logs — `~/lab407/phish/mailgateway.csv`:

```csv
received_utc,recipient,sender,subject,action
2026-10-29T09:12:47Z,student@lab-app.example,billing@lab-finance.example,URGENT: invoice INV-4071 requires approval today,delivered
2026-10-29T09:12:47Z,a.rahman@lab-app.example,billing@lab-finance.example,URGENT: invoice INV-4071 requires approval today,delivered
2026-10-29T09:12:48Z,j.chen@lab-app.example,billing@lab-finance.example,URGENT: invoice INV-4071 requires approval today,delivered
2026-10-29T09:12:48Z,m.siddiqui@lab-app.example,billing@lab-finance.example,URGENT: invoice INV-4071 requires approval today,delivered
2026-10-29T09:12:49Z,ap-team@lab-app.example,billing@lab-finance.example,URGENT: invoice INV-4071 requires approval today,quarantined
```

`~/lab407/phish/proxy.csv`:

```csv
time_utc,user,url,method,status,action
2026-10-29T09:41:12Z,a.rahman@lab-app.example,hxxp://portal.lab-finance.example/approve?id=INV-4071,GET,200,allowed
2026-10-29T09:44:03Z,a.rahman@lab-app.example,hxxp://portal.lab-finance.example/login,POST,302,allowed
2026-10-29T10:02:55Z,j.chen@lab-app.example,hxxp://portal.lab-finance.example/approve?id=INV-4071,GET,200,allowed
2026-10-29T11:15:00Z,student@lab-app.example,hxxp://portal.lab-finance.example/approve?id=INV-4071,GET,403,blocked
```

### 2. Analyse the message

Do not open the attachment in a browser. Parse it as text:

```bash
cd ~/lab407/phish
python3 - <<'PY'
from email import policy
from email.parser import BytesParser
import hashlib, pathlib

msg = BytesParser(policy=policy.default).parse(open("reported.eml", "rb"))
for h in ("From", "Reply-To", "Return-Path", "Subject", "Date", "Message-ID", "Authentication-Results"):
    print(f"{h:22} {msg.get(h)}")
print()
for i, part in enumerate(msg.walk(), 1):
    if part.get_content_maintype() == "multipart":
        continue
    payload = part.get_payload(decode=True) or b""
    print(f"[{i}] {part.get_content_type():24} {len(payload):>5} bytes  sha256={hashlib.sha256(payload).hexdigest()[:16]}...")
    if part.get_content_type() == "text/plain":
        print(payload.decode("utf-8", "replace").strip())
PY
```

**Expected:** the headers print; the plain-text part contains the defanged URL; the HTML part's payload begins
`<html><body><script>window.location='http://portal.lab-finance.example/approve?id=INV-4071'</script>`.

Record the **full** SHA-256 of the attachment (the script truncates for display; compute the full value separately).

**Answer these before moving on:**

1. `From` domain is `lab-finance.example`; `Return-Path` is `lab-payments.example`. What does that mismatch suggest?
2. `Reply-To` is a different domain again. What is the attacker trying to achieve if the recipient replies?
3. What do `spf=softfail`, `dkim=none` and `dmarc=fail (p=none)` each tell you — and what does `p=none` mean for the
   receiver?
4. Read the `Received` chain from the **bottom up**. Which host took the message first, and which IP delivered it?

### 3. Extract indicators with confidence

`iocs.md`:

| Indicator | Type | Value | Confidence | Why |
| --- | --- | --- | --- | --- |
| Sender address | email | `billing@lab-finance.example` | Medium | Spoofed display name; domain is lookalike |
| Reply-to domain | domain | `lab-payments.example` | High | Not the claimed organisation |
| Sending IP | ipv4 | `192.0.2.200` | High | Named in `Received` and in the SPF softfail |
| Phishing URL | url | `hxxp://portal.lab-finance[.]example/approve?id=INV-4071` | High | Matches the lure and the proxy logs |
| Attachment | sha256 | full hash | High | Exact file, regardless of filename |
| Subject | string | `URGENT: invoice INV-4071 requires approval today` | Low | Easy to change; useful for searching only |

**Rule:** an indicator you would block on needs high confidence and a scope check. A subject line is a search term,
not a block.

### 4. Determine scope from the logs

```bash
awk -F, 'NR>1 {print $2}' mailgateway.csv | sort | uniq -c
awk -F, 'NR>1 && $3 ~ /lab-finance\.example/ {print $2, $5}' proxy.csv
```

**Expected:** five recipients, of whom two requested the landing page and one submitted a POST to `/login` — meaning
credentials were almost certainly entered.

Now answer, with counts and names:

1. How many recipients received the message, and how many were quarantined?
2. Who clicked, who submitted credentials, and what was blocked?
3. What is your **impact statement** in one sentence?

**Expected impact statement:** "Five recipients; four delivered; two visited the landing page; one submitted
credentials; one attempt was blocked by the proxy."

### 5. Contain in the right order

Order matters, because blocking first can destroy the ability to enumerate:

1. **Preserve** the message, headers, attachment hash and the log extracts. Copy them read-only.
2. **Scope** — done above; record that it is complete for the gateway, and that mailboxes not in the log are unknown.
3. **Block** the sender domain, reply-to domain and URL at the gateway and proxy. Record the rule and the time.
4. **Contain the identity** — force a password reset and revoke sessions for `a.rahman`, and check for MFA changes,
   mailbox rules, and new OAuth grants. Credentials, not the email, are the compromise.
5. **Search** for the same indicators across the estate for the last 30 days — other campaigns reuse infrastructure.
6. **Notify** the recipients with plain guidance, and the identity team with the reset request.

`containment.md`:

| Time (UTC) | Action | Actor | Expected effect | Verified how |
| --- | --- | --- | --- | --- |
| | | | | |

**Do not** delete the email from all mailboxes before you have hashed the attachment and recorded recipients — the
mailbox copy is evidence.

### 6. Decide what "resolved" means

Write three sentences: what would make you close this incident, what would make you escalate it to SEV2, and what you
cannot determine from the evidence you have. (Expected: you cannot know whether the submitted credentials were used
successfully without authentication logs from the real service — that is the next query, and its absence is a gap.)

## Evidence to collect

- `reported.eml` and the parsed header output.
- Full SHA-256 of the attachment.
- `iocs.md`, `scope.md`, `containment.md`.
- Read-only copies of `mailgateway.csv` and `proxy.csv`.
- `impact.md` with the one-sentence statement and the gaps.

## Verification

- [ ] Headers parsed as text; attachment never opened in a browser.
- [ ] `Received` chain read bottom-up, with the originating IP identified.
- [ ] SPF, DKIM and DMARC results interpreted, including what `p=none` means.
- [ ] Full attachment hash recorded.
- [ ] Indicators carry confidence and a reason.
- [ ] Scope counts reconcile with the logs (5 recipients, 2 visits, 1 credential submission, 1 blocked).
- [ ] Containment order is preserve → scope → block → identity → search → notify.
- [ ] Identity actions include session revocation, not only a password reset.
- [ ] Gaps stated, including what the logs cannot prove.

## Teardown and reset

Keep the evidence directory; it feeds LAB-407-04. Remove nothing until the report cites it.

## Reflection

1. Why is `Reply-To` a useful indicator even when the `From` domain is the one being spoofed?
2. `dmarc=fail (p=none)` means the receiver was told the message failed and delivered it anyway. What would `p=reject`
   have changed, and why do organisations hesitate to move to it?
3. You blocked the URL at 12:00. What have you lost the ability to measure, and how would you have avoided that?
4. The user who submitted credentials is also the person who reported the email. How does that change your
   communication to them?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Analysis | Reads the body only | Parses headers and attachment | Explains authentication results and the Received chain |
| Indicators | Lists links | Types and values | Confidence with reasons; subject treated as search term |
| Scope | Recipients unknown | Counts from logs | Impact statement plus stated gaps |
| Containment | Blocks the sender | Blocks and resets password | Order justified, sessions revoked, estate-wide search, notification |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Parser returns `None` for a header | Header absent or folded unexpectedly | Print `msg.items()` to see the raw set |
| Attachment payload is empty | Base64 block corrupted when copying | Recreate the file exactly as shown |
| `awk` counts wrong | Commas inside quoted fields | Use Python's `csv` module for anything non-trivial |
| Proxy URL comparison fails | Defanged URL versus log URL | Normalise `hxxp`/`[.]` before comparing, and keep the original |
| Cannot determine credential use | No auth logs for the real service | Record as a gap and request the logs; do not infer success |

## References

1. NIST SP 800-61 Rev. 3 — detection and analysis, containment. Accessed 2026-10-29.
2. RFC 7208 (SPF), RFC 6376 (DKIM), RFC 7489 (DMARC) — authentication result semantics. Accessed 2026-10-29.
3. CISA — Phishing Guidance. <https://www.cisa.gov/phishing> Accessed 2026-10-29.
4. MITRE ATT&CK — T1566.001 Spearphishing Attachment, T1566.002 Spearphishing Link. Accessed 2026-10-29.
5. Python `email` package — `policy.default`, `walk()`, `get_payload(decode=True)`. Accessed 2026-10-29.

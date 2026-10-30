---
title: "LAB-114-02 · Assess a Password Policy"
description: "Analyse a fictional credential set and policy document, then recommend specific improvements without cracking anything."
module_code: CYB-114
level: 1
kind: lab
prerequisites: [CYB-114]
estimated_minutes: 45
difficulty: beginner
safety: local-only
lab_ids: [LAB-114-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [passwords, policy, risk]
---

# LAB-114-02 · Assess a Password Policy

**Module:** CYB-114 · **Time:** 45 minutes · **Safety:** local-only · **Snapshot:** none required

!!! warning "Authorized scope — read before you begin"
    **What you may use:** the fictional dataset and policy below. Every value is invented for teaching.
    **What you must not do:** do not test these passwords against any real account, service, or system; do not
    use cracking tools against them; do not collect or analyse credentials belonging to other people.

    This is a **policy analysis** exercise: you will reason about patterns and controls, not attempt to break
    anything.

## Objective

Assess a fictional password policy and a 12-entry credential sample, identify the weaknesses that matter, and
produce a three-recommendation improvement plan with justification.

## Threat model

This simulates a review an analyst would perform for an organisation whose credentials leaked. The realistic
threats are **credential stuffing** (reuse from other breaches) and **spraying** (common passwords across many
accounts) — not a determined offline attack against a single hash.

## Environment

- The dataset and policy below.
- A shell for counting and pattern analysis (no cracking tools).

## Dataset (fictional)

```csv
user,password
aisha.k,Summer2026!
bilal.r,P@kistan123
chen.w,qwerty12345
dana.m,Company@2026
emeka.o,Welcome1!
farah.s,iloveyou2024
gita.p,Tr0ub4dor&3x
hassan.a,Fall2025#
ines.c,Password1!
jamal.t,karachi786
kiran.b,CorrectHorseBattery9
liam.n,monkey123
```

## Procedure

### Step 1 — Save the dataset and compute simple statistics

```bash
mkdir -p ~/cyber/level-1/lab-114-02/evidence
cd ~/cyber/level-1/lab-114-02
cat > evidence/passwords.csv <<'CSV'
user,password
aisha.k,Summer2026!
bilal.r,P@kistan123
chen.w,qwerty12345
dana.m,Company@2026
emeka.o,Welcome1!
farah.s,iloveyou2024
gita.p,Tr0ub4dor&3x
hassan.a,Fall2025#
ines.c,Password1!
jamal.t,karachi786
kiran.b,CorrectHorseBattery9
liam.n,monkey123
CSV

awk -F, 'NR>1 {print length($2)}' evidence/passwords.csv | sort -n | uniq -c
awk -F, 'NR>1 {n++; s+=length($2)} END {printf "count=%d mean=%.1f\n", n, s/n}' evidence/passwords.csv
```

**Expected** (format depends on `awk`; counts must match your own file):

```text
      2 9
      3 10
      ...
count=12 mean=12.6
```

### Step 2 — Classify by pattern

Create `analysis.md` and tag each password with every pattern that applies:

| Pattern | Examples in this dataset |
| --- | --- |
| Season + year | |
| Name or place + digits | |
| Keyboard sequence | |
| Common dictionary word + digits | |
| Brand/organisation + year | |
| Symbol substitution (`@` for `a`, `0` for `o`) | |
| Long passphrase | |

Two useful observations to record: how many entries contain a **year**, and how many could be guessed from
public information about a person (name, city, season).

### Step 3 — Evaluate the policy against threats

```text
PASSWORD POLICY v3 (current)
1. Minimum length 8 characters.
2. Must contain upper case, lower case, a number, and a symbol.
3. Passwords expire every 60 days.
4. The last 3 passwords may not be reused.
5. Accounts lock after 3 failed attempts and require a helpdesk call to unlock.
6. Security questions (mother's maiden name, first school) are required for recovery.
7. Password hashes are stored as SHA-256.
```

For each clause, answer: which threat does it reduce, and what does it cost?

### Step 4 — Count the failures

Complete this table in `analysis.md`:

| Clause | Reduces | Cost or gap | Verdict |
| --- | --- | --- | --- |
| 1. 8-character minimum | Some guessing | Short passwords fall fast; passphrases excluded | Weak |
| 2. Composition rules | Trivial guessing | Predictable substitutions; encourages `Password1!` | Weak |
| 3. 60-day rotation | Little | Predictable increments; user frustration | Harmful |
| 4. History of 3 | Some reuse | Minor | Adequate |
| 5. Lockout after 3 | Online guessing | Helpdesk DoS; encourages shared accounts | Needs tuning |
| 6. Security questions | Recovery | Answers often public; bypasses the password entirely | Harmful |
| 7. SHA-256 storage | Nothing meaningful | Fast hash; offline guessing trivial | Critical |

### Step 5 — Write three recommendations

Rules: each recommendation must name the clause it replaces, the threat it addresses, the implementation
effort, and one measurable outcome.

Example shape (do not copy — write your own):

> Replace clause 3 (60-day rotation) with rotation only on evidence of compromise. Threat: predictable
> increments from forced rotation. Effort: policy edit plus awareness note. Measure: percentage of accounts
> flagged for reuse drops; helpdesk reset volume falls.

### Step 6 — Verify the improvement

For each recommendation, state how you would prove it worked in 90 days. "Better security" is not a
measurement; a rate, a count, or a test is.

## Evidence to collect

`evidence/passwords.csv`, `analysis.md` (pattern table, clause table, three recommendations with measures),
and your shell output for the length statistics.

## Verification

- [ ] Length statistics computed and recorded.
- [ ] Every password classified by pattern, with at least five distinct patterns identified.
- [ ] Each policy clause assessed for both benefit and cost.
- [ ] Three recommendations with effort and a measurable outcome.
- [ ] No cracking tools used and no real credentials involved.

## Teardown and reset

```bash
rm -rf ~/cyber/level-1/lab-114-02/evidence/passwords.csv
```

Keep `analysis.md`; delete the credential file. Even fictional credential lists should not linger in a
folder that might later hold real ones — the habit is the point.

## Reflection

1. Which single clause in the policy causes the most harm, and why?
2. Why do composition rules produce `Password1!` rather than strong passwords?
3. What does the presence of `CorrectHorseBattery9` in the sample tell you about length versus complexity?
4. If you could add only one control beyond the password policy, what would it be, and what would it fix?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Patterns listed without analysis | All clauses assessed, patterns identified | Links each weakness to a specific attack and control |
| Methodology | Judged by impression | Systematic pattern and clause review | Prioritises by risk and explains the ordering |
| Evidence | No statistics | Statistics and tables present | Measurable outcomes defined for each recommendation |
| Safety | Attempted to test credentials | Analysis only | Analysis only, credential file deleted, no tools used |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `awk: syntax error` | Quoting differences | Use the exact command; on Windows run it in the Linux VM |
| Mean length looks wrong | Header row counted | Keep `NR>1` |
| Cannot classify a password | It fits several patterns | Tag all that apply; ambiguity is realistic |
| Recommendations sound vague | No baseline | Add a number you could measure in 90 days |

## Related

- [Passwords, MFA and Phishing](01-passwords-mfa-phishing.md)
- [LAB-114-01 · Triage Synthetic Phishing Emails](lab-01-phishing-triage.md)
- [Cryptography, Hashing and Signatures](../13-cryptography-hashing-signatures/index.md)

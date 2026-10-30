---
title: "LAB-402-02 · Linux Authentication Log Analysis"
description: "Analyse a synthetic auth.log for brute force, password spraying and a success that follows, using journald and the shell."
module_code: CYB-402
level: 4
kind: lab
prerequisites: [CYB-402]
estimated_minutes: 150
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-402-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [auth-log, journald, sshd, brute-force, password-spraying]
---

# LAB-402-02 · Linux Authentication Log Analysis

## Scenario and background

An Ubuntu server on the lab network has SSH exposed to the host-only segment. Over one day it received three
different kinds of authentication traffic, and the monitoring system flagged only "failed logins: 80" — a number
that describes nothing.

You will analyse the log, separate the three patterns, and produce the finding that a number cannot: which source
was guessing at one account, which was spraying across many, and whether any attempt succeeded.

## Learning objectives

By the end of this lab you can:

1. Parse `sshd` authentication lines into account, source, and outcome.
2. Distinguish brute force from spraying using distinct-account counts, not total failures.
3. Correlate a failure burst with a later success from the same source.
4. Query the same evidence through `journalctl` and through `/var/log/auth.log`.
5. Set a detection threshold and justify it against expected false positives.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Ubuntu Server | 22.04.x | `lab-ubuntu` |
| `journalctl` | systemd 249+ | Installed |
| `awk`, `sed`, `sort`, `uniq` | standard | Analysis |
| Python 3 | 3.10+ | Dataset generation |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab-ubuntu` only, and only the synthetic log file plus lines you inject into your own
    journal with `logger`.
    **Targets you must not use:** sshd on any other host, any real account, and any external address.

    **Do not attempt to authenticate against a real account.** This lab never sends a password anywhere. The
    failures are text records written by `logger` and by the dataset generator, and you must say so in your report
    rather than implying a live attack occurred.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

Three fictional sources appear in the data: one guessing at `root`, one spraying a list of plausible usernames
across many accounts, and one apparently benign administrative client. A success appears after the spray. Your job
is to decide what the evidence supports and what it does not.

## Environment

| Host | Role | Address | Notes |
| --- | --- | --- | --- |
| `lab-ubuntu` | Target and analyst host | 192.0.2.20 | Host-only |
| `lab-analyst` | Legitimate admin client (synthetic) | 192.0.2.10 | Appears in the dataset only |

## Before you start

```bash
mkdir -p ~/lab/level-4/lab-402-02/{data,evidence}
cd ~/lab/level-4/lab-402-02
```

Generate the dataset. Every line is synthetic; addresses are documentation ranges.

```bash
python3 - <<'PY'
import random, datetime
random.seed(40202)

start = datetime.datetime(2026, 10, 28, 0, 0, 0)
users = ["admin","oracle","postgres","ubuntu","test","dev","backup","web","git","jenkins",
         "support","info","sales","hr","finance","deploy","monitor","ansible","docker","kube",
         "pi","user","guest","demo","stage","prod","api","ftp","mail","vpn",
         "svc-backup","svc-web","svc-db","ops","root","nagios","zabbix","elastic","redis","mongo"]
lines = []
t = start

def sshd(ts, msg):
    return ts.strftime("%b %d %H:%M:%S") + f" lab-ubuntu sshd[{random.randint(1000,9999)}]: {msg}"

# 1. Brute force: one account, one source, 30 attempts
for i in range(30):
    t = start + datetime.timedelta(minutes=37 + i)
    lines.append(sshd(t, f"Failed password for root from 203.0.113.9 port {40000+i} ssh2"))

# 2. Spraying: 42 distinct accounts, one attempt each, one source
for i, u in enumerate(users):
    t = start + datetime.timedelta(hours=3, seconds=i*47)
    lines.append(sshd(t, f"Failed password for invalid user {u} from 198.51.100.77 port {50000+i} ssh2"))

# 3. The success that follows the spray
t = start + datetime.timedelta(hours=3, minutes=41)
lines.append(sshd(t, "Accepted publickey for svc-backup from 198.51.100.77 port 51234 ssh2: ED25519 SHA256:AAAAexamplekeyfingerprint"))

# 4. Legitimate administration
for i in range(6):
    t = start + datetime.timedelta(hours=9, minutes=i*11)
    lines.append(sshd(t, f"Accepted publickey for analyst from 192.0.2.10 port {52000+i} ssh2: ED25519 SHA256:BBBBexamplekeyfingerprint"))

# 5. Noise: a scanner trying a handful of names
for i, u in enumerate(["test","admin","pi","oracle","ubuntu","guest","info","demo"]):
    t = start + datetime.timedelta(hours=13, minutes=i*3)
    lines.append(sshd(t, f"Invalid user {u} from 203.0.113.44 port {53000+i}"))

# 6. A few legitimate failures (typos) from the admin host
for i in range(3):
    t = start + datetime.timedelta(hours=10, minutes=i*7)
    lines.append(sshd(t, f"Failed password for analyst from 192.0.2.10 port {54000+i} ssh2"))

random.shuffle(lines)
open("data/auth.log","w").write("\n".join(lines) + "\n")
print("lines:", len(lines))
PY
wc -l data/auth.log
head -3 data/auth.log
```

**Expected:** 89 lines. The shuffle means line order does not match time order — as in a real merged log. Sort by
time before building a timeline.

## Procedure

### 1. Count outcomes before interpreting them

```bash
grep -c 'Failed password' data/auth.log
grep -c 'Accepted' data/auth.log
grep -c 'Invalid user' data/auth.log
```

**Expected:** 30 + 42 + 3 = 75 failures, 7 accepted lines, and 42 + 8 = 50 lines mentioning an invalid user
(some overlap with failures).

**Why the totals mislead:** 75 failures is the number a naive dashboard reports. It does not distinguish a single
account under attack from fifty accounts being tested, and those need different responses.

### 2. Extract structured attempts

```bash
sed -nE 's/.*Failed password for (invalid user )?([^ ]+) from ([^ ]+) port ([0-9]+).*/\2\t\3\t\4/p' \
  data/auth.log | sort -k2,2 > evidence/attempts.tsv

head -5 evidence/attempts.tsv
wc -l evidence/attempts.tsv
```

**Expected:** three columns — account, source address, source port — and 75 rows.

**Why `sort -k2,2`:** it groups by source address, which is the dimension the analysis needs.

### 3. Attempts per source

```bash
cut -f2 evidence/attempts.tsv | sort | uniq -c | sort -rn
```

**Expected:** three sources with counts of roughly 30, 42 and 3.

### 4. Distinct accounts per source — the spraying signal

```bash
cut -f2,1 evidence/attempts.tsv | sort -u | cut -f1 | uniq -c | sort -rn
```

**Expected:** one source with **42 distinct accounts, one attempt each**, one with **1 distinct account
(`root`), 30 attempts**, and one with **1 account, 3 attempts**.

That table is the finding:

| Shape | Interpretation |
| --- | --- |
| Many attempts, one account | Brute force — noisy, usually blocked by lockout |
| Many accounts, one attempt each | Password spraying — quiet, evades lockout, needs a breadth query |
| Few attempts, known admin source | Benign, but worth a threshold |

### 5. Find successes, then correlate

```bash
grep 'Accepted' data/auth.log | sed -E 's/.*for ([^ ]+) from ([^ ]+).*/\1\t\2/' | sort | uniq -c
```

**Expected:** `svc-backup` once from `198.51.100.77`, and `analyst` six times from `192.0.2.10`.

Now the correlation that decides severity:

```bash
awk -F'\t' '{print $2}' evidence/attempts.tsv | sort -u | while read -r ip; do
  fails=$(awk -F'\t' -v ip="$ip" '$2==ip' evidence/attempts.tsv | wc -l)
  succ=$(grep 'Accepted' data/auth.log | grep -c "$ip")
  printf '%-16s failures=%-3s successes=%s\n' "$ip" "$fails" "$succ"
done
```

**Expected:** the spraying source has 42 failures **and one success**; the brute-force source has 30 failures and
none; the admin source has 3 failures and 6 successes.

**Interpretation, stated carefully:** the success for `svc-backup` used **public-key** authentication, not a
password. A password spray cannot produce a public-key success by itself. So either the key was stolen, or the
source address is shared (NAT, VPN egress, hosting provider), or the account is used from an unexpected place.
Write all three possibilities; the evidence does not choose between them. This is the most important analytical
moment in the lab.

### 6. Do the same through journald

Inject three synthetic lines into your own journal so you can practise the `journalctl` path. Be explicit that these
are injected: `logger -t` sets the tag, it does not make the line real `sshd` output.

```bash
logger -t sshd -p authpriv.warning "Failed password for invalid user labdemo from 203.0.113.77 port 5555 ssh2"
logger -t sshd -p authpriv.warning "Failed password for invalid user labdemo2 from 203.0.113.77 port 5556 ssh2"
logger -t sshd -p authpriv.notice  "Accepted password for labdemo from 203.0.113.77 port 5557 ssh2"

journalctl -t sshd --since "5 min ago" --no-pager
journalctl -t sshd --since "5 min ago" -o json | jq -r '[.__REALTIME_TIMESTAMP, .MESSAGE] | @tsv' | head -3
```

**Expected:** three lines with the `sshd` tag, and JSON output with microsecond timestamps.

**Why this matters:** on many systems `auth.log` exists only if `rsyslog` is installed; on others the journal is the
only source. Your detection must know which one it can rely on.

### 7. Set thresholds and justify them

In `evidence/thresholds.md`, propose rules for:

| Rule | Logic | Threshold | Expected false positives |
| --- | --- | --- | --- |
| Brute force | failures per account per source in 10 min | ? | Users with expired passwords |
| Spraying | distinct accounts per source in 30 min | ? | Vulnerability scanners, load balancers |
| Success after failures | ≥N failures then Accepted, same source, 30 min | ? | Admin typo then success |

For each threshold, state what legitimate activity would trip it and how you would exclude that activity **without**
excluding the attack.

### 8. Write the finding

`evidence/finding.md`, under 350 words: the three sources and their shapes, the success and its authentication
method, the three hypotheses that could explain it, what additional evidence would distinguish them, and the two
detections you would deploy first.

## Evidence to collect

- `data/auth.log` — 89 synthetic lines.
- `evidence/attempts.tsv` — 75 structured rows.
- `evidence/summary.txt` — attempts by source, distinct accounts by source, successes by source.
- `evidence/journal.txt` — the `journalctl` output for the injected lines.
- `evidence/thresholds.md` and `evidence/finding.md`.

## Verification

- [ ] Totals computed before patterns were interpreted.
- [ ] Distinct-account counts per source produced, and the spray identified by breadth.
- [ ] Successes correlated with failure sources.
- [ ] The public-key detail is noticed and its implications stated.
- [ ] Three explanations are offered for the success, with the evidence that would distinguish them.
- [ ] Thresholds are justified against named false positives.

## Teardown and reset

```bash
rm -rf ~/lab/level-4/lab-402-02/data
```

The injected journal lines remain in your VM's journal; they are harmless and will age out. If you prefer a clean
journal, revert `pre-lab-402-02`.

## Reflection

1. A dashboard reported "80 failed logins". Explain why that number could not trigger the right response.
2. The successful login used a key, not a password. Which of your three hypotheses do you consider most likely, and
   what would you check first?
3. Spraying is designed to stay under lockout thresholds. What does that imply about detecting it with
   failure-count alerts?
4. Your spraying threshold counts distinct accounts per source. Name one legitimate system that would trip it.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Parsing | Manual reading | Structured extraction | Structured extraction plus reproducible commands |
| Pattern analysis | Counts failures | Distinguishes brute and spray | Distinguishes all three shapes and names the signal |
| Correlation | Successes listed | Failures joined to successes | Joined, with the authentication method's implication stated |
| Judgement | Concludes compromise | Lists possibilities | Lists possibilities with the evidence that would separate them |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `sed` produces no output | Message format differs from the pattern | Print a raw line and adjust the regex |
| `uniq -c` counts wrong | Input not sorted | Always `sort` before `uniq` |
| `journalctl -t sshd` empty | Journal does not retain that tag, or time window too narrow | Widen `--since`; confirm with `logger` test |
| No `/var/log/auth.log` | `rsyslog` not installed | Use the journal, and note the difference in your report |
| Counts differ from the expected values | Dataset regenerated with a different seed | Rerun with the exact generator shown |

## References

1. `sshd(8)` and `sshd_config(5)` — logging behaviour. Accessed 2026-10-29.
2. `journalctl(1)` — filtering by unit, tag, priority, and output format. Accessed 2026-10-29.
3. MITRE ATT&CK — T1110.001 Password Guessing; T1110.003 Password Spraying; T1078 Valid Accounts.
   Accessed 2026-10-29.
4. NIST SP 800-61 Rev. 3 — detection and analysis (April 2025).

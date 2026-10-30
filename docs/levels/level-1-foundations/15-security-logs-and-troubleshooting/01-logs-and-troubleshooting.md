---
title: "Reading Logs and Troubleshooting Methodically"
description: "Log sources and structure, filtering techniques, correlation, absence as evidence, and a fixed troubleshooting order."
module_code: CYB-115
level: 1
kind: lesson
prerequisites: [CYB-114]
estimated_minutes: 90
difficulty: beginner
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [logs, troubleshooting, detection]
---

# Reading Logs and Troubleshooting Methodically

## Learning objectives

By the end of this lesson you can:

1. Name the main Linux and Windows log sources and the question each answers.
2. Break a log line into timestamp, source, actor, action, outcome.
3. Filter logs by unit, severity, time, and event ID.
4. Correlate entries across two sources to explain one event.
5. Explain why a missing entry is evidence, and what it can mean.
6. Apply a fixed troubleshooting order and document it.

## Prerequisites

[CYB-114](../14-passwords-mfa-phishing/index.md). A running `lab-ubuntu` with `sudo`.

---

## 1. Where logs come from

| Source | Answers | Command |
| --- | --- | --- |
| systemd journal | Service lifecycle, kernel messages, most daemons | `journalctl` |
| `/var/log/auth.log` | Authentication, `sudo`, sessions (Debian/Ubuntu) | `tail`, `grep` |
| `/var/log/syslog` | General system messages | `tail` |
| Web server logs | Requests, errors, client addresses | `/var/log/nginx/*` |
| `auditd` | System calls, file access (if installed) | `ausearch`, `aureport` |
| Windows Security | Logon, privilege use, account changes | `Get-WinEvent -LogName Security` |
| Windows System | Services, drivers, hardware | `Get-WinEvent -LogName System` |
| Windows Application | Application errors and events | `Get-WinEvent -LogName Application` |

The professional habit is to know **which source answers which question** before opening any of them. Asking
"who logged in at 03:00?" and reading a web access log wastes an hour.

## 2. Anatomy of a log line

```text
Oct 28 21:52:14 lab-ubuntu sudo:  student : TTY=pts/0 ; PWD=/home/student ; USER=root ; COMMAND=/usr/bin/ss -tlnp
 │            │         │       │        │              │             │         │        └── action
 │            │         │       │        │              │             │         └── target identity
 │            │         │       │        │              │             └── working directory
 │            │         │       │        │              └── terminal
 │            │         │       │        └── actor
 │            │         │       └── source/daemon
 │            │         └── host
 │            └── timestamp
 └── month/day
```

Five questions to ask of any line: **when**, **where**, **who**, **did what**, **what happened**.

Windows equivalents are structured rather than textual: `TimeCreated`, `ProviderName`, `Id`, `LevelDisplayName`,
and a `Message` with fields. Filtering by `Id` is the equivalent of grepping for a pattern — more precise and
less fragile.

## 3. Filtering instead of scrolling

```bash
journalctl -n 20 --no-pager                       # last 20 entries
journalctl -u ssh --since "1 hour ago"            # one service, recent
journalctl -p err -b                              # errors since boot
journalctl --since "2026-10-28 21:00" --until "2026-10-28 22:00"
sudo grep -a "Failed password" /var/log/auth.log | tail -5
sudo grep -a "sudo:" /var/log/auth.log | tail -5
```

Windows:

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; Level=2} -MaxEvents 10 |
  Select-Object TimeCreated, Id, ProviderName, Message
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625; StartTime=(Get-Date).AddHours(-1)}
```

Two rules that save time:

- **Narrow by time first**, then by source, then by pattern. Reversing this order produces thousands of
  irrelevant matches.
- **Quote your patterns.** `grep -a "Failed password"` is a phrase; unquoted it is two patterns.

## 4. Correlating two sources

One event usually leaves traces in more than one place. Example: a failed `sudo` attempt.

| Source | What you see |
| --- | --- |
| `auth.log` | `sudo: authentication failure ... USER=root` |
| `journalctl -u sudo` | the same attempt, with unit context |
| `journalctl -b` | surrounding system activity at that moment |

Correlation is how you move from "something happened" to "here is what happened and in what order". At Level
4 you will do this across SIEM data; the reasoning is identical, only the scale changes.

## 5. Absence is evidence

If you expected an entry and there is none, that tells you something specific:

| Missing entry | Possible explanations |
| --- | --- |
| No failed-login events | No attempts — or auditing disabled |
| No process-creation events | Nothing ran — or audit policy off |
| No log for a service that "crashed" | It never started, or logging is misconfigured |
| A gap in timestamps | Clock skew, rotation, or tampering |

The discipline is to distinguish **"did not happen"** from **"not recorded"**. Write down which one you
believe, and why.

Related traps:

- **Timezone drift.** `journalctl` uses local time; other tools may use UTC. Convert before comparing.
- **Clock skew.** A VM that has been suspended can be minutes or hours off. Check `timedatectl`.
- **Rotation.** `logrotate` may have moved the evidence to `auth.log.1` or compressed it.
- **Tampering.** Logs are files; anyone with root can edit them. That is why centralised collection matters
  and why integrity of logs is itself a control.

## 6. A troubleshooting order that works

```
1. Define the symptom precisely.       "Port 8000 refuses connections" not "it's broken".
2. Reproduce it.                       If you cannot, you cannot verify a fix.
3. Check what changed.                 Recent config, update, or permission change?
4. Work up the stack.                  link → address → route → name → port → process → application
5. Change one variable at a time.      Two changes teach you nothing.
6. Verify, then document.              Command, output, cause, fix.
```

Step 3 is the one beginners skip. Most breakage is caused by something that changed in the last hour, and
`journalctl --since "1 hour ago"` frequently names it.

---

## Practical exercises

### Exercise 1 — Read your own trail (10 minutes)

```bash
sudo grep -a "sudo:" /var/log/auth.log | tail -5
journalctl --since "30 min ago" --no-pager | tail -20
```

Find one action you performed and reconstruct it: what, when, from which terminal, with what result.

### Exercise 2 — Filter with intent (10 minutes)

Answer using filters only (no scrolling):

1. How many errors since the last boot?
2. What did the `ssh` unit log in the last hour?
3. Which `sudo` commands ran today?

### Exercise 3 — Absence analysis (10 minutes)

```bash
sudo grep -ac "Failed password" /var/log/auth.log
sudo grep -ac "session opened" /var/log/auth.log
```

If the first count is zero, answer: no attempts, or no logging? What would you check to decide?

### Exercise 4 — Explain an event in two sources (10 minutes)

Trigger a harmless authentication event (one wrong `sudo` password, then `Ctrl-C`), then find it in both
`auth.log` and the journal. Write two sentences describing the event using only what the logs show.

## Expected observations and verification

- You can name the source that answers "who authenticated" versus "what requests arrived".
- Your filters returned small, relevant result sets.
- You found the same event in two sources and can describe the difference in wording.
- You can state one reason a log entry might be missing.

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| Grepping the wrong file | Habit | Decide which source answers the question first |
| Ignoring time zones | Logs mix local and UTC | Normalise to one zone before comparing |
| Assuming a quiet log means nothing happened | Natural inference | Check whether auditing for that event is enabled |
| Reading `journalctl` without `--no-pager` in scripts | Interactive pager | Use `--no-pager` or pipe to a file |
| Changing several things then testing | Impatience | One variable at a time, documented |
| Deleting logs to "clean up" | Misguided tidiness | Never delete evidence; rotate and archive instead |

## Review questions

1. Which log source would you check first for a failed SSH login, and why?
2. What five elements should you extract from any log line?
3. Why is "no entries" ambiguous, and how do you resolve the ambiguity?
4. Why does troubleshooting order matter more than speed?
5. What are two reasons log timestamps disagree between tools?
6. Why is log integrity a security control in itself?

## Knowledge check

1. Which command shows errors since the last boot on Ubuntu?
2. Which Windows event ID records a failed logon?
3. What does a gap in log timestamps suggest?
4. Why filter by time before pattern?
5. What is the difference between "did not happen" and "not recorded"?

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 3–5 if 1, 2 and 5 are uncertain.)*

## Summary

- Know which source answers which question before you open anything.
- Every log line answers when, where, who, did what, with what outcome.
- Filter by time, then source, then pattern; quote your patterns.
- Correlation turns isolated lines into an explanation.
- Absence is evidence, but distinguish "did not happen" from "not recorded".
- Troubleshoot in a fixed order, change one variable at a time, and document the result.

## Next lesson

That completes Level 1. Continue with the
[Level 1 readiness assessment](../../level-1.md#level-assessment), then
[Level 2 — Tooling and Lab Craft](../../level-2.md).

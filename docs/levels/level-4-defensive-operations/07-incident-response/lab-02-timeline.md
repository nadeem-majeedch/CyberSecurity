---
title: "LAB-407-02 · Master Timeline from Mixed Evidence"
description: "Normalise four evidence sources with different timezones and a fast clock, then show which orderings naive sorting gets wrong."
module_code: CYB-407
level: 4
kind: lab
prerequisites: [CYB-407]
estimated_minutes: 150
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-407-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [timeline, timezone, clock-skew, correlation, evidence, python]
---

# LAB-407-02 · Master Timeline from Mixed Evidence

## Scenario and background

Four sources recorded the same intrusion: a Windows endpoint in Athens local time, a Linux server in UTC with a clock
seven minutes fast, a firewall exporting UTC, and a proxy log in UTC.

Sorted as they are, they tell a story in the wrong order — and the wrong order changes the story. You will normalise
everything to UTC, correct the known skew, and document what remains uncertain.

## Learning objectives

1. Build a per-asset time model: timezone, offset, and known clock error.
2. Convert and correct timestamps programmatically, not by eye.
3. Merge heterogeneous sources into one ordered timeline with provenance.
4. Identify the orderings that naive sorting gets wrong, and why they matter.
5. State residual uncertainty and the events the evidence cannot place.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | `csv`, `json`, `datetime`, `zoneinfo` |
| `tzdata` | current | `pip install tzdata` if `zoneinfo` lacks the zone database |

!!! warning "Authorized scope — read before you begin"
    All evidence is **synthetic and supplied in this page**. No system is accessed, and no clock is changed. The
    hosts, users and addresses are invented.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Evidence pack

Create `~/lab407/timeline/` and the following files.

`assets.csv` — the time model. Read this before any conversion:

```csv
host,timezone,clock_offset_seconds,source_file,notes
WS-07,Europe/Athens,0,sysmon.csv,Local time without offset; DST per zone database
srv-app,UTC,420,auth.log,Clock 7 minutes FAST at time of incident per NTP log
fw-edge,UTC,0,eve.json,UTC with Z suffix
proxy,UTC,0,proxy.csv,UTC
```

`srv-app-ntp.log` — the evidence for the offset:

```text
2026-10-29T08:00:12Z ntpd[812]: offset +420.3 sec, stratum 2, synced to 192.0.2.123
```

`sysmon.csv` — endpoint, local time in Athens (UTC+2 on 29 October 2026, after EU DST ends on 25 October; verify with
the zone database rather than assuming):

```csv
local_time,event_id,image,parent_image,command_line,user
2026-10-29 11:58:03,1,explorer.exe,userinit.exe,explorer.exe,a.rahman
2026-10-29 12:09:41,1,powershell.exe,explorer.exe,"powershell.exe -NoProfile -EncodedCommand SQBFAFgA",a.rahman
2026-10-29 12:09:44,1,cmd.exe,powershell.exe,"cmd.exe /c whoami /priv > C:\Users\a.rahman\AppData\Local\Temp\p.txt",a.rahman
2026-10-29 12:10:02,11,svchost.exe,,C:\Users\a.rahman\AppData\Local\Temp\svc.exe,a.rahman
```

`auth.log` — UTC, but seven minutes **fast** (subtract 420 s):

```text
2026-10-29T10:05:44Z srv-app sshd[3312]: Accepted password for deploy from 198.51.100.23 port 51422 ssh2
2026-10-29T10:06:10Z srv-app useradd[3340]: new user: name=svcbackup, UID=1003, GID=1003
2026-10-29T10:06:31Z srv-app sudo[3351]: deploy : TTY=pts/0 ; PWD=/home/deploy ; COMMAND=/usr/sbin/useradd svcbackup
2026-10-29T10:19:58Z srv-app systemd[1]: Started Session 12 of user deploy.
```

`eve.json` — one JSON object per line, UTC:

```json
{"timestamp":"2026-10-29T10:11:20.114Z","event_type":"dns","src_ip":"192.0.2.40","dns":{"type":"query","rrname":"t.exfil-lab.example","rrtype":"TXT"}}
{"timestamp":"2026-10-29T10:12:05.882Z","event_type":"flow","src_ip":"192.0.2.40","dest_ip":"198.51.100.77","dest_port":443,"flow":{"bytes_toserver":482113,"bytes_toclient":9912}}
{"timestamp":"2026-10-29T10:18:40.003Z","event_type":"alert","src_ip":"192.0.2.40","alert":{"signature":"LAB405 synthetic marker requested","severity":2}}
```

`proxy.csv` — UTC:

```csv
time_utc,user,url,method,status
2026-10-29T09:41:12Z,a.rahman@lab-app.example,hxxp://portal.lab-finance.example/approve?id=INV-4071,GET,200
2026-10-29T09:44:03Z,a.rahman@lab-app.example,hxxp://portal.lab-finance.example/login,POST,302
```

`mailgateway.csv` — from LAB-407-01:

```csv
received_utc,recipient,sender,subject,action
2026-10-29T09:12:47Z,a.rahman@lab-app.example,billing@lab-finance.example,URGENT: invoice INV-4071 requires approval today,delivered
```

## Procedure

### 1. Write the conversion model first

`time_model.md`, before code:

| Source | Recorded as | Convert to UTC | Correction | Residual uncertainty |
| --- | --- | --- | --- | --- |
| `sysmon.csv` | Local, no offset, `Europe/Athens` | `zoneinfo` conversion | none | Up to ±1 s rounding; DST rule applied by zone data |
| `auth.log` | UTC, 7 min fast | none | subtract 420 s | ±2 s; clock was drifting |
| `eve.json` | UTC with `Z` | parse as UTC | none | Millisecond resolution |
| `proxy.csv` | UTC with `Z` | parse as UTC | none | Second resolution |

**Rule:** the correction is applied to the *recorded* time to estimate the *true* time. State the sign explicitly;
sign errors are the most common timeline bug.

### 2. Normalise and merge

`build_timeline.py`:

```python
#!/usr/bin/env python3
import csv, json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
rows = []

def add(utc_dt, host, source, event, ref, confidence="high"):
    stamp = utc_dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    rows.append({"utc": stamp, "host": host, "source": source,
                 "event": event, "ref": ref, "confidence": confidence})

# Endpoint: local time in Athens, no offset recorded
with open("sysmon.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        local = datetime.strptime(r["local_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Athens"))
        add(local, "WS-07", "sysmon", f'{r["image"]}: {r["command_line"][:60]}', "sysmon.csv")

# Server: UTC but 420 s fast -> subtract
with open("auth.log", encoding="utf-8") as f:
    for line in f:
        stamp = line.split(" ", 1)[0]
        recorded = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        add(recorded - timedelta(seconds=420), "srv-app", "auth", line.split(": ", 1)[-1].strip()[:70], "auth.log")

# Firewall: UTC already
with open("eve.json", encoding="utf-8") as f:
    for line in f:
        e = json.loads(line)
        add(datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")), "fw-edge", "suricata",
            e.get("event_type", "") + " " + str(e.get("dns", {}).get("rrname", "")), "eve.json")

# Proxy and mail: UTC already
for name, field, label in (("proxy.csv", "time_utc", "proxy"), ("mailgateway.csv", "received_utc", "mail")):
    with open(name, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            add(datetime.fromisoformat(r[field].replace("Z", "+00:00")), "proxy" if label == "proxy" else "mail",
                label, (r.get("url") or r.get("subject", ""))[:70], name)

for r in sorted(rows, key=lambda x: x["utc"]):
    print(f'{r["utc"]}  {r["host"]:<9} {r["source"]:<9} {r["event"]}')

with open("timeline.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["utc", "host", "source", "event", "ref", "confidence"])
    w.writeheader(); w.writerows(sorted(rows, key=lambda x: x["utc"]))
```

```bash
cd ~/lab407/timeline
python3 build_timeline.py | tee timeline.txt
```

**Expected:** 14 rows in UTC, beginning with the mail delivery at `09:12:47.000Z` and ending with the firewall alert at
`10:18:40.003Z`. The server session appears at `10:12:58.000Z` (10:19:58 recorded minus 7 minutes), not at the recorded
time — check that line specifically.

**Check the arithmetic by hand for one event of each source.** If the server login appears at `10:05:44Z` rather than
`09:58:44Z`, you applied the correction in the wrong direction or not at all.

### 3. Show what naive sorting gets wrong

Produce `naive.txt` by sorting on the *recorded* strings without conversion. Then complete `corrections.md`:

| # | Pair of events | Naive order | Correct order | Consequence of getting it wrong |
| --- | --- | --- | --- | --- |
| 1 | Server login vs endpoint execution | | | |
| 2 | DNS query vs endpoint execution | | | |
| 3 | Exfiltration flow vs account creation | | | |

**Expected finding for #1:** the endpoint's Athens local time reads two hours ahead, so naive sorting places the
PowerShell execution *after* the server login by a wide margin, when in fact the login came first. The consequence is
a wrong hypothesis about which credential was used and from where.

**Expected finding for #2:** the DNS query at `10:11:20Z` follows the endpoint execution at `10:09:41Z`; naive sorting
using the endpoint's local `12:09` reverses that and makes the DNS look like the cause rather than the consequence.

### 4. State the chain — and its gaps

`narrative.md`:

```text
09:12:47Z  Phishing email delivered to a.rahman (mail)
09:41:12Z  Landing page visited (proxy)
09:44:03Z  Credential POST to lookalike login (proxy)
09:58:03Z  Explorer started on WS-07 (sysmon, TZ-converted)
09:58:44Z  SSH login to srv-app as deploy from 198.51.100.23 (auth, skew-corrected)
09:59:10Z  Local account svcbackup created (auth, skew-corrected)
09:59:31Z  sudo useradd on srv-app (auth, skew-corrected)
10:09:41Z  Encoded PowerShell on WS-07 (sysmon)
10:09:44Z  cmd.exe whoami /priv redirected to temp file (sysmon)
10:10:02Z  Executable written to Temp\svc.exe (sysmon)
10:11:20Z  TXT query for t.exfil-lab.example (suricata)
10:12:05Z  Outbound flow, 482 KB to 198.51.100.77:443 (suricata)
10:12:58Z  Interactive session on srv-app (auth, skew-corrected)
10:18:40Z  Firewall alert (suricata)
```

Then `gaps.md`, at least four:

1. The proxy does not record the response body, so credential submission is inferred from the POST and a 302.
2. `svc.exe` was written but its execution is not in this extract — absence is a gap, not proof it did not run.
3. The DNS query appears after execution; the resolver logs do not show whether a response carried data.
4. Nothing places a human at the keyboard; session ownership is inferred from the account.
5. The server clock was drifting, so ±2 s is a floor on uncertainty, not a ceiling.

### 5. Confidence

Add a confidence column and justify each entry. The mail and proxy entries are high (single source, but unambiguous).
The inference "credentials were used within 14 minutes" is **medium**: the timing is consistent, but no authentication
log from the external service is in the pack.

## Evidence to collect

- `assets.csv`, `srv-app-ntp.log`, and the four source files.
- `time_model.md`.
- `build_timeline.py`, `timeline.csv`, `timeline.txt`.
- `naive.txt`, `corrections.md`.
- `narrative.md`, `gaps.md`.

## Verification

- [ ] Time model written before conversion, with the sign of each correction stated.
- [ ] All sources converted to UTC with `zoneinfo` or explicit offsets, not by eye.
- [ ] Server events shifted **back** by 420 seconds.
- [ ] One event per source hand-checked against the output.
- [ ] Three naive-sort inversions identified with their consequences.
- [ ] Narrative uses only timestamps from the generated timeline.
- [ ] At least four gaps, including one where absence is not proof.
- [ ] Confidence justified per entry, with at least one non-high value.

## Teardown and reset

Keep the directory; LAB-407-04 cites the timeline. No system state was changed.

## Reflection

1. Why is a clock that is *consistently* seven minutes fast easier to handle than one that drifts during the incident?
2. The endpoint's local time has no offset recorded. What would you ask for to remove the reliance on an assumed time
   zone?
3. Two events are one second apart after correction. What does that tell you about using order as proof of causation?
4. Which single additional log source would most reduce the gaps in this timeline?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Time model | Not stated | Timezone per source | Timezone, offset correction sign, and residual uncertainty |
| Conversion | Manual edits | Script converts | Script converts, hand-checked, reproducible |
| Ordering | Sorted as given | Correct UTC order | Inversions identified with consequences |
| Narrative | Story from memory | Timeline-based | Timeline-based with gaps and confidence |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ZoneInfoNotFoundError` | No tz database on the platform | `pip install tzdata` |
| Server events an hour off | Applied local timezone instead of skew | Server is UTC; only the 420 s correction applies |
| Endpoint events two hours off | Ignored the Athens offset or the DST date | Check the zone database's offset for 2026-10-29 |
| Duplicate rows | Source file read twice | Check loop structure; de-duplicate on `(utc, host, event)` |
| `json.loads` fails | Multi-line JSON or trailing junk | One object per line; inspect the offending line |
| Timeline looks plausible but is wrong | Conversion applied twice | Assert one known event's final timestamp |

## References

1. NIST SP 800-61 Rev. 3 — analysis and timeline construction. Accessed 2026-10-29.
2. NIST SP 800-86 — timeline analysis and time normalization. Accessed 2026-10-29.
3. RFC 9557 — date and time with time zone offset. Accessed 2026-10-29.
4. Python `zoneinfo` and `datetime` documentation. Accessed 2026-10-29.
5. MITRE ATT&CK — T1566, T1078, T1059.001, T1136.001, T1048. Accessed 2026-10-29.

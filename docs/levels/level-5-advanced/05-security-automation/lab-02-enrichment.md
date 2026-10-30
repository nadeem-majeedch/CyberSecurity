---
title: "LAB-505-02 · Enrichment and Report Normalisation"
description: "Enrich normalised events from a local IOC dataset, then merge two vulnerability scanner reports into one prioritised, deduplicated finding set."
module_code: CYB-505
level: 5
kind: lab
prerequisites: [CYB-505]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-505-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [automation, enrichment, ioc, vulnerability-management, normalisation]
---

# LAB-505-02 · Enrichment and Report Normalisation

## Prerequisites

LAB-505-01's normalised output (or the sample rows in this lab) and Python 3.10 or newer. All enrichment
data is local: no lookup service, API key or internet access is involved.

## Scenario and background

Two problems that look different and are the same shape:

1. An alert says `192.0.2.61` failed to log in. Is that a known actor, or a misconfigured printer?
2. Two scanners report the same estate. One speaks JSON, the other CSV, their severities disagree and half the
   findings are duplicates.

Both are solved by normalising first and joining second. This lab does it offline, from local data, with no third-party
lookups — because sending your internal indicators to an external service is a data-handling decision, not a default.

## Learning objectives

1. Enrich events with a local IOC table, including refanging and private-address handling.
2. Explain why an indicator hit is context, not a verdict.
3. Normalise two scanner formats into one finding schema.
4. Deduplicate findings across sources and merge their fields.
5. Prioritise by exploitability rather than by the scanner's own label.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | `csv`, `json` |
| Finished LAB-505-01 | — | `events.jsonl` is the input |

## Safety

All indicators are synthetic and **non-routable**. `lab.invalid` is under the reserved `.invalid` TLD, and the address
ranges are documentation ranges. Nothing here resolves or connects.

## Part A — IOC enrichment

### 1. The dataset

```bash
mkdir -p ~/auto-lab/enrich && cd ~/auto-lab/enrich
```

`iocs.csv`:

```csv
type,value,confidence,campaign,first_seen
ip,192.0.2.61,high,SANDSTORM-4100,2026-10-01
ip,203.0.113.77,medium,SANDSTORM-4100,2026-10-12
domain,lab.invalid,high,SANDSTORM-4100,2026-10-05
domain,evil[.]invalid,high,SANDSTORM-4100,2026-10-05
```

Note the defanged entry: `evil[.]invalid`. Indicators are shared in defanged form so they cannot be clicked, so the
loader must refang them or the match silently fails.

### 2. The enricher

`enrich.py`:

```python
#!/usr/bin/env python3
"""Enrich normalised events with local IOC context. No network calls."""
import csv
import json
import re
import sys
from pathlib import Path

DEFANG = [("hxxp", "http"), ("hXXp", "http"), ("[.]", "."), ("(.)", "."), ("[:]", ":")]
PRIVATE = [re.compile(r"^10\."), re.compile(r"^192\.168\."), re.compile(r"^172\.(1[6-9]|2\d|3[01])\.")]


def refang(value: str) -> str:
    for bad, good in DEFANG:
        value = value.replace(bad, good)
    return value.strip().lower()


def is_private(ip: str) -> bool:
    return any(p.match(ip) for p in PRIVATE)


def load_iocs(path: Path) -> dict:
    table = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if not row.get("type") or not row.get("value"):
                continue
            table[(row["type"].strip().lower(), refang(row["value"]))] = {
                "confidence": row.get("confidence", "unknown").lower(),
                "campaign": row.get("campaign") or None,
                "first_seen": row.get("first_seen") or None,
            }
    return table


def enrich(event: dict, table: dict) -> dict:
    ip = event.get("src_ip")
    if not ip:
        return {**event, "ioc": None}
    if is_private(ip):
        return {**event, "ioc": {"skipped": "private-address"}}
    match = table.get(("ip", refang(ip)))
    return {**event, "ioc": match or None}


def main() -> int:
    table = load_iocs(Path("iocs.csv"))
    events = [json.loads(l) for l in Path("../events.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    enriched = [enrich(e, table) for e in events]
    with open("enriched.jsonl", "w", encoding="utf-8") as fh:
        for e in enriched:
            fh.write(json.dumps(e, sort_keys=True) + "\n")
    hits = [e for e in enriched if e["ioc"] and "confidence" in e["ioc"]]
    print("events:", len(enriched), "ioc hits:", len(hits))
    for e in hits:
        print(e["ts"], e["event_type"], e["user"], e["src_ip"], e["ioc"]["campaign"], e["ioc"]["confidence"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```bash
python3 enrich.py
```

**Expected:**

```text
events: 13 ioc hits: 10
2026-10-29T08:12:03Z auth_failure admin 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:12:19Z auth_failure a.khan 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:12:35Z auth_failure a.khan 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:13:07Z auth_failure root 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:13:22Z ssh_closed deploy 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:20:00Z login_failed a.khan 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:20:14Z login_ok a.khan 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:21:02Z login_failed svc-report 203.0.113.77 SANDSTORM-4100 medium
2026-10-29T08:25:01Z fw_deny None 192.0.2.61 SANDSTORM-4100 high
2026-10-29T08:25:09Z fw_deny None 192.0.2.61 SANDSTORM-4100 high
```

### 3. Read the result critically

Two lines matter more than the count:

- The **successful** login at `08:20:14Z` carries the same campaign as the failures. An IOC hit is context: it can mean
  a known-bad host succeeded, or that your shared egress IP is on a list, or that a scanner is testing you.
- The success at `08:12:51Z` came from `192.0.2.74`, which is **not** in the table. The interesting event — success from
  a new address immediately after failures — is interesting precisely because it is *not* a known indicator.

Write `enrichment-notes.md` with:

1. How many events matched, and how many were skipped as private (none here — explain why the skip exists anyway).
2. What the confidence field should change about your response (`high` + failure burst vs `medium` + one event).
3. What `first_seen` tells you that a bare IOC list does not.
4. Why the enricher must not call a public API with internal addresses by default.

**On age:** an indicator from 2026-10-01 is 28 days old at the time of these events. Indicators decay: infrastructure
is reassigned, and old IPs produce false positives. A production enricher stores `last_seen` and expires entries.

## Part B — Vulnerability report normalisation

### 4. Two scanners, one estate

```bash
mkdir -p ~/auto-lab/vuln && cd ~/auto-lab/vuln
```

`scan-a.json` (Trivy-style):

```json
{
  "Results": [
    {
      "Target": "web01",
      "Vulnerabilities": [
        {"VulnerabilityID": "CVE-2024-21538", "PkgName": "cross-spawn", "InstalledVersion": "7.0.0", "FixedVersion": "7.0.5", "Severity": "HIGH", "CVSS": {"nvd": {"V3Score": 7.5}}},
        {"VulnerabilityID": "CVE-2023-44487", "PkgName": "nghttp2", "InstalledVersion": "1.55.1", "FixedVersion": "1.57.0", "Severity": "HIGH", "CVSS": {"nvd": {"V3Score": 7.5}}}
      ]
    },
    {
      "Target": "db01",
      "Vulnerabilities": [
        {"VulnerabilityID": "CVE-2024-1597", "PkgName": "postgresql-jdbc", "InstalledVersion": "42.6.0", "FixedVersion": "42.7.2", "Severity": "CRITICAL", "CVSS": {"nvd": {"V3Score": 9.8}}}
      ]
    }
  ]
}
```

`scan-b.csv`:

```csv
cve,host,package,version,severity,kev,epss
CVE-2024-21538,web01,cross-spawn,7.0.0,high,false,0.12
CVE-2023-44487,web01,nghttp2,1.55.1,critical,true,0.71
CVE-2023-34362,fs01,progress-moveit,2020.1.0,unknown,true,0.94
```

Three disagreements to notice before writing code:

- `CVE-2023-44487` is `HIGH` in scan-a and `critical` in scan-b. The merge must resolve it, not pick arbitrarily.
- `CVE-2023-34362` has severity `unknown` and is on the KEV list. A severity-only sort would bury it.
- The first finding appears in both reports for the same asset: a duplicate.

### 5. The normaliser

`normalise_findings.py`:

```python
#!/usr/bin/env python3
"""Normalise two scanner reports into one finding schema, deduplicate and prioritise."""
import csv
import json
import sys
from pathlib import Path

SEVERITY = {"critical": "critical", "high": "high", "medium": "medium", "moderate": "medium",
            "low": "low", "info": "info", "informational": "info"}
ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0, "unknown": -1}


def tier(finding: dict) -> str:
    if finding.get("kev") is True:
        return "P1"
    score = finding.get("cvss") or 0
    if score >= 9.0:
        return "P1"
    if score >= 7.0:
        return "P2"
    if score >= 4.0:
        return "P3"
    return "P4"


def from_json(path: Path) -> list:
    findings = []
    for result in json.loads(path.read_text(encoding="utf-8"))["Results"]:
        for vuln in result.get("Vulnerabilities", []):
            score = ((vuln.get("CVSS") or {}).get("nvd") or {}).get("V3Score")
            findings.append({
                "cve": vuln["VulnerabilityID"],
                "asset": result["Target"],
                "package": vuln.get("PkgName"),
                "version": vuln.get("InstalledVersion"),
                "fix": vuln.get("FixedVersion") or None,
                "severity": SEVERITY.get(str(vuln.get("Severity", "")).lower(), "unknown"),
                "cvss": float(score) if score is not None else None,
                "kev": None,
                "epss": None,
                "source": "scan-a",
            })
    return findings


def from_csv(path: Path) -> list:
    findings = []
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if not row.get("cve") or not row.get("host"):
                continue
            raw = str(row.get("severity", "")).lower()
            findings.append({
                "cve": row["cve"].strip().upper(),
                "asset": row["host"].strip(),
                "package": row.get("package") or None,
                "version": row.get("version") or None,
                "fix": None,
                "severity": SEVERITY.get(raw, "unknown"),
                "cvss": None,
                "kev": (row.get("kev", "").strip().lower() == "true") or None,
                "epss": float(row["epss"]) if row.get("epss") else None,
                "source": "scan-b",
                "severity_raw": raw if raw not in SEVERITY else None,
            })
    return findings


def merge(findings: list) -> list:
    merged = {}
    for finding in findings:
        key = (finding["cve"], finding["asset"])
        if key not in merged:
            merged[key] = finding
            continue
        current = merged[key]
        if ORDER[finding["severity"]] > ORDER[current["severity"]]:
            current["severity"] = finding["severity"]
            current["severity_raw"] = finding.get("severity_raw")
        for field in ("cvss", "kev", "epss", "fix", "package", "version"):
            if current.get(field) is None and finding.get(field) is not None:
                current[field] = finding[field]
        current["source"] = "+".join(sorted({current["source"], finding["source"]}))
    result = list(merged.values())
    for finding in result:
        finding["tier"] = tier(finding)
    result.sort(key=lambda f: (f["tier"], -ORDER[f["severity"]], f["asset"], f["cve"]))
    return result


def main() -> int:
    findings = from_json(Path("scan-a.json")) + from_csv(Path("scan-b.csv"))
    merged = merge(findings)
    with open("findings.json", "w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2, sort_keys=True)
    print(f"{'TIER':4} {'SEV':8} {'CVE':16} {'ASSET':6} {'KEV':5} {'SRC':12}")
    for f in merged:
        print(f"{f['tier']:4} {f['severity']:8} {f['cve']:16} {f['asset']:6} {str(f['kev']):5} {f['source']:12}")
    print("input:", len(findings), "merged:", len(merged))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```bash
python3 normalise_findings.py
```

**Expected:**

```text
TIER SEV      CVE              ASSET  KEV   SRC
P1   critical CVE-2024-1597    db01   None  scan-a
P1   critical CVE-2023-44487   web01  True  scan-a+scan-b
P1   unknown  CVE-2023-34362   fs01   True  scan-b
P2   high     CVE-2024-21538   web01  None  scan-a+scan-b
input: 6 merged: 4
```

Read what the merge did:

- Six input rows became four findings: two were the same CVE on the same asset.
- `CVE-2023-44487` took the **higher** severity (critical) and gained `kev=true` from the second report.
- `CVE-2023-34362` is `P1` despite `unknown` severity, because KEV membership outranks the label.
- `CVE-2024-21538` stayed `P2`: CVSS 7.5, no KEV.

### 6. Tests that matter

```python
import normalise_findings as nf


def test_refang_and_private():
    import enrich
    assert enrich.refang("evil[.]invalid") == "evil.invalid"
    assert enrich.refang("hxxp://lab[.]invalid") == "http://lab.invalid"
    assert enrich.is_private("192.168.1.5") and not enrich.is_private("192.0.2.61")


def test_merge_prefers_higher_severity():
    merged = nf.merge([
        {"cve": "CVE-X", "asset": "a", "severity": "high", "cvss": None, "kev": None, "epss": None,
         "fix": "1.1", "package": "p", "version": "1.0", "source": "one"},
        {"cve": "CVE-X", "asset": "a", "severity": "critical", "cvss": None, "kev": True, "epss": None,
         "fix": None, "package": None, "version": None, "source": "two"},
    ])
    assert len(merged) == 1
    assert merged[0]["severity"] == "critical"
    assert merged[0]["kev"] is True
    assert merged[0]["fix"] == "1.1"


def test_kev_outranks_severity():
    assert nf.tier({"kev": True, "cvss": 5.0}) == "P1"
    assert nf.tier({"kev": None, "cvss": 9.8}) == "P1"
    assert nf.tier({"kev": None, "cvss": 7.5}) == "P2"
```

**Expected:** all pass. The second test is the important one: it pins the *merge policy* (higher severity wins, missing
fields are filled, nothing is lost), which is a decision, not an implementation detail.

## Evidence to collect

- `enriched.jsonl` and the hit count.
- `enrichment-notes.md` with the four answers.
- `findings.json` and the printed table.
- Test output.
- One paragraph on what your prioritisation would do differently on a 4,000-finding estate.

## Verification

- [ ] Refanging is applied to the dataset, and the defanged entry is reachable by lookup.
- [ ] Private addresses are explicitly skipped, with a stated reason.
- [ ] You state that an IOC hit is not a verdict, using the successful-login example.
- [ ] Six findings merge to four, with severity and KEV merged, not overwritten arbitrarily.
- [ ] The `unknown`-severity KEV finding sorts as `P1`.
- [ ] Tests pin the merge policy, not just the code paths.

## Teardown and reset

Keep both directories; LAB-505-03 uses the schema. Nothing external was contacted.

## Reflection

1. `192.0.2.61` is in your IOC list and also the source of firewall denies. What would make you treat it as confirmed
   malicious, and what keeps it "context" for now?
2. The merge takes the higher severity. When would that be the wrong policy?
3. KEV membership outranks a scanner's label. Why does that make sense, and what does it cost you in patch effort?
4. What is the risk of enriching with a free public API that requires you to submit the indicator?

## Extensions

- Add indicator expiry: drop entries older than 30 days and report how many hits disappear.
- Add a domain extractor over `raw` and match domains as well as IPs.
- Emit a CSV for a ticket system instead of JSON, and assert the column order in a test.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Enrichment | Lookup only | Refang and private skip | Confidence, age and non-verdict nature discussed |
| Normalisation | One scanner | Both, one schema | Merge policy explicit and tested |
| Prioritisation | By scanner label | KEV considered | Justified tiers with cost/benefit reasoning |
| Testing | None | Merge test | Policy tests, refang, private-address boundary |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No IOC hits | Dataset has defanged values | Refang at load **and** at lookup |
| `KeyError: 'Results'` | Wrong scanner JSON shape | Print `list(json.load(f).keys())` first |
| Duplicates remain | Key includes package or version | Key on `(cve, asset)` |
| `unknown` sorts first unexpectedly | Missing `ORDER` entry | Include `unknown: -1` |
| All tiers `P4` | `kev` is the string `"true"` | Parse to bool at ingestion |

## References

1. CISA — Known Exploited Vulnerabilities catalog (concept and fields). Accessed 2026-10-29.
2. FIRST — EPSS documentation (probability and percentile). Accessed 2026-10-29.
3. Trivy — JSON report schema. Accessed 2026-10-29.
4. RFC 2606 — reserved TLDs including `.invalid`. Accessed 2026-10-29.

#!/usr/bin/env python3
"""Reference solution for the automation capstone.

Reads mixed.log (syslog, CSV, JSONL), normalises to one schema, enriches against
iocs.csv, and writes summary.json plus findings.md. Exits 1 if more than 10% of
lines could not be parsed.
"""
import argparse, csv, json, re, sys
from collections import Counter

SYSLOG = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(?P<host>\S+)\s+sshd\[(?P<pid>\d+)\]:\s+"
    r"(?P<msg>.*)$"
)
FAILED = re.compile(r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+) port")
ACCEPTED = re.compile(r"Accepted \S+ for (?P<user>\S+) from (?P<ip>\S+) port")


def parse_line(raw):
    line = raw.rstrip("\n")
    if not line.strip():
        return None, "blank line"
    if line.startswith("{"):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            return None, "json decode error"
        if not {"ts", "host", "user", "action"} <= obj.keys():
            return None, "json missing required fields"
        return {"ts": obj["ts"], "host": obj["host"], "user": obj["user"],
                "action": obj["action"], "src_ip": obj.get("src_ip", ""),
                "domain": obj.get("domain", ""), "source_format": "json"}, None
    m = SYSLOG.match(line)
    if m:
        msg = m.group("msg")
        hit = FAILED.search(msg)
        if hit:
            return {"ts": m.group("ts"), "host": m.group("host"), "user": hit.group("user"),
                    "action": "login_failed", "src_ip": hit.group("ip"), "domain": "",
                    "source_format": "syslog"}, None
        hit = ACCEPTED.search(msg)
        if hit:
            return {"ts": m.group("ts"), "host": m.group("host"), "user": hit.group("user"),
                    "action": "login_success", "src_ip": hit.group("ip"), "domain": "",
                    "source_format": "syslog"}, None
        return None, "syslog line not a recognised authentication event"
    parts = line.split(",")
    if len(parts) == 5 and parts[0].endswith("Z") and "T" in parts[0]:
        ts, host, user, action, ip = parts
        if not re.match(r"^\d{4}-\d{2}-\d{2}T", ts):
            return None, "csv timestamp not ISO 8601"
        return {"ts": ts, "host": host, "user": user, "action": action,
                "src_ip": ip, "domain": "", "source_format": "csv"}, None
    if len(parts) == 4:
        return None, "csv record has 4 fields, expected 5"
    return None, "unrecognised format"


def load_iocs(path):
    out = {}
    for row in csv.DictReader(open(path, encoding="utf-8")):
        out[(row["type"], row["indicator"])] = row
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="mixed.log")
    ap.add_argument("--iocs", default="iocs.csv")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    iocs = load_iocs(args.iocs)
    events, skipped = [], []
    for n, raw in enumerate(open(args.log, encoding="utf-8"), start=1):
        rec, why = parse_line(raw)
        if rec is None:
            skipped.append({"line": n, "reason": why, "raw": raw.rstrip("\n")[:80]})
            continue
        ip_hit = iocs.get(("ip", rec["src_ip"]))
        dom_hit = iocs.get(("domain", rec["domain"])) if rec["domain"] else None
        hit, kind, indicator = (ip_hit, "ip", rec["src_ip"]) if ip_hit else (
            (dom_hit, "domain", rec["domain"]) if dom_hit else (None, "", ""))
        rec["verdict"] = hit["verdict"] if hit else ""
        rec["confidence"] = hit["confidence"] if hit else ""
        rec["source"] = hit["source"] if hit else ""
        rec["indicator"] = indicator
        rec["indicator_type"] = kind
        events.append(rec)

    # Aggregate per indicator, host and action so one brute-force burst is one finding.
    groups = {}
    for e in events:
        if e["verdict"] != "malicious":
            continue
        key = (e["indicator"], e["host"], e["action"])
        g = groups.setdefault(key, {"count": 0, "first": e["ts"], "last": e["ts"],
                                   "users": set(), "confidence": e["confidence"],
                                   "type": e["indicator_type"], "source": e["source"]})
        g["count"] += 1
        g["first"] = min(g["first"], e["ts"])
        g["last"] = max(g["last"], e["ts"])
        g["users"].add(e["user"])

    findings = []
    for (indicator, host, action), g in sorted(groups.items(), key=lambda kv: (kv[1]["first"], kv[0])):
        severity = "high" if (g["confidence"] == "high" or action == "login_success") else "medium"
        findings.append({
            "title": f"{action} from malicious {g['type']} {indicator} on {host}",
            "severity": severity,
            "indicator": indicator,
            "indicator_type": g["type"],
            "confidence": g["confidence"],
            "source": g["source"],
            "count": g["count"],
            "first_seen": g["first"],
            "last_seen": g["last"],
            "users": sorted(g["users"]),
        })

    summary = {
        "lines_read": len(events) + len(skipped),
        "events_normalised": len(events),
        "skipped": skipped,
        "by_format": dict(Counter(e["source_format"] for e in events)),
        "by_action": dict(Counter(e["action"] for e in events)),
        "top_sources": Counter(e["src_ip"] for e in events if e["src_ip"]).most_common(3),
        "findings": findings,
        "finding_count": len(findings),
    }
    import os
    os.makedirs(args.out, exist_ok=True)
    json.dump(summary, open(f"{args.out}/summary.json", "w"), indent=2)
    with open(f"{args.out}/findings.md", "w", encoding="utf-8") as f:
        f.write("# Findings\n\n")
        for i, x in enumerate(findings, 1):
            f.write(f"{i}. **{x['severity'].upper()}** {x['title']} (confidence: {x['confidence']})\n")
            f.write(f"   - {x['count']} event(s), {x['first_seen']} to {x['last_seen']}, users: {', '.join(x['users'])}\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "skipped"}, indent=2))
    print("skipped:")
    for s in skipped:
        print(f"  line {s['line']}: {s['reason']}")
    if len(skipped) > 0.10 * summary["lines_read"]:
        print("error: skipped rate above 10%", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Reference analysis for the SOC investigation capstone.

Usage (from the folder holding events.csv, hosts.csv and dns.csv):
    python soc_analysis.py --data . --out timeline.md

Corrects each host clock using hosts.csv, sorts the events, flags behaviours of
interest and prints the count of flagged events. All data is synthetic.
"""
import argparse, csv, os
from datetime import datetime, timedelta


def clock(s):
    return datetime.strptime(s, "%H:%M:%S")


def load(data):
    hosts = {r["host"]: int(r["clock_offset_seconds"])
             for r in csv.DictReader(open(os.path.join(data, "hosts.csv"), encoding="utf-8"))}
    events = list(csv.DictReader(open(os.path.join(data, "events.csv"), encoding="utf-8")))
    for e in events:
        e["utc"] = clock(e["ts_local"]) - timedelta(seconds=hosts[e["host"]])
    events.sort(key=lambda e: e["utc"])
    dns = list(csv.DictReader(open(os.path.join(data, "dns.csv"), encoding="utf-8")))
    return hosts, events, dns


FLAGS = [
    ("office spawns powershell", lambda e: e["parent"] == "winword.exe" and e["process"] == "powershell.exe"),
    ("encoded powershell", lambda e: e["process"] == "powershell.exe" and " -enc " in e["cmdline"]),
    ("task created as SYSTEM", lambda e: e["process"] == "schtasks.exe" and "/ru SYSTEM" in e["cmdline"]),
    ("shadow copies deleted", lambda e: "delete shadows" in e["cmdline"]),
    ("mass file rename", lambda e: ".locked" in e["cmdline"]),
    ("local admin group change", lambda e: e["event_id"] == "4732"),
    ("service account network logon", lambda e: e["event_id"] == "4624" and e["user"] == "svc_backup" and "type 3" in e["outcome"]),
    ("external connection", lambda e: e["event_id"] == "3"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=".")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    hosts, events, dns = load(args.data)
    rows = []
    for e in events:
        flags = [name for name, fn in FLAGS if fn(e)]
        rows.append((e["utc"].strftime("%H:%M:%S"), e["host"], e["event_id"], e["user"],
                     e["process"] or "-", e["outcome"], ", ".join(flags) or ""))

    print(f"events={len(events)} hosts={len(hosts)} flagged={sum(1 for r in rows if r[6])}")
    for r in rows:
        print("  " + " | ".join(r))

    txt = [d for d in dns if d["qtype"] == "TXT"]
    gaps = [(clock(b["ts_local"]) - clock(a["ts_local"])).total_seconds()
            for a, b in zip(txt, txt[1:])]
    print(f"dns_txt={len(txt)} intervals_s={gaps}")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("| UTC | Host | Event | User | Process | Observation | Flag |\n")
            f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
            for r in rows:
                f.write("| " + " | ".join(r) + " |\n")
        print("wrote", args.out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Reference harness for the threat-detection capstone.

Evaluates the Sigma-subset rules in ./rules against events.jsonl and labels.csv.
Supports one `selection` block per rule with |contains, |startswith, |endswith
modifiers, list values (OR within a field), and a condition naming the selection.

Usage (from the threat-detection folder, with rules/ beside it):
    python run_detections.py --data . --rules rules
"""
import argparse, csv, json, os
import yaml

FIELD_MAP = {"Image": "process", "ParentImage": "parent", "CommandLine": "cmdline",
             "User": "user", "Computer": "host"}


def load_events(data):
    labels = {r["id"]: r for r in csv.DictReader(open(os.path.join(data, "labels.csv"), encoding="utf-8"))}
    events = [json.loads(line) for line in open(os.path.join(data, "events.jsonl"), encoding="utf-8")]
    for e in events:
        e["label"] = labels[e["id"]]["label"]
        e["note"] = labels[e["id"]]["note"]
    return events


def match_clause(event, clause):
    for raw_key, expected in clause.items():
        field, _, modifier = raw_key.partition("|")
        modifier = modifier or "equals"
        base = field.split("|")[0]
        actual = str(event.get(FIELD_MAP.get(base, base), ""))
        values = expected if isinstance(expected, list) else [expected]
        if not any(_cmp(actual, str(v), modifier) for v in values):
            return False
    return True


def _cmp(actual, value, modifier):
    if modifier == "contains":
        return value.lower() in actual.lower()
    if modifier == "startswith":
        return actual.lower().startswith(value.lower())
    if modifier == "endswith":
        return actual.lower().endswith(value.lower())
    return actual == value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=".")
    ap.add_argument("--rules", default="rules")
    args = ap.parse_args()

    events = load_events(args.data)
    names = sorted(n for n in os.listdir(args.rules) if n.endswith(".yml"))
    matched_ids = set()
    print(f"events={len(events)} rules={len(names)}")
    print(f"{'rule':38} {'TP':>3} {'FP':>3}")
    for name in names:
        doc = yaml.safe_load(open(os.path.join(args.rules, name), encoding="utf-8"))
        matched = [e for e in events if match_clause(e, doc["detection"]["selection"])]
        matched_ids |= {e["id"] for e in matched}
        tp = [e for e in matched if e["label"] == "malicious"]
        fp = [e for e in matched if e["label"] == "benign"]
        print(f"{name[:38]:38} {len(tp):>3} {len(fp):>3}")
        for e in fp:
            print(f"    benign match: {e['id']} {e['host']} {e['user']} - {e['note']}")

    malicious = [e for e in events if e["label"] == "malicious"]
    tp = [e for e in malicious if e["id"] in matched_ids]
    fp = [e for e in events if e["label"] == "benign" and e["id"] in matched_ids]
    fn = [e for e in malicious if e["id"] not in matched_ids]
    precision = len(tp) / (len(tp) + len(fp)) if tp or fp else 0.0
    recall = len(tp) / len(malicious) if malicious else 0.0
    print(f"\nunion TP={len(tp)} FP={len(fp)} FN={len(fn)} precision={precision:.2f} recall={recall:.2f}")
    for e in fn:
        print("    missed:", e["id"], e["process"], e["note"])


if __name__ == "__main__":
    main()

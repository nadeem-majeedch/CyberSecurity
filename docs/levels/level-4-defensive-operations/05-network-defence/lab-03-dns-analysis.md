---
title: "LAB-405-03 · DNS Behaviour Analysis"
description: "Generate a synthetic capture containing benign, CDN-like and tunnelling-like DNS, then separate them by label shape, record type and cadence."
module_code: CYB-405
level: 4
kind: lab
prerequisites: [CYB-405]
estimated_minutes: 150
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-405-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [dns, tunnelling, beaconing, tshark, zeek, entropy, pcap]
---

# LAB-405-03 · DNS Behaviour Analysis

## Scenario and background

A resolver log shows one domain with thousands of unique subdomains. Is that a CDN, a telemetry service, or a tunnel?

You will answer that with evidence. The capture is **synthetic and generated locally**: it contains three behaviours
with the same protocol and different shapes, so the only way to separate them is analysis rather than a signature.

## Learning objectives

1. Generate a reproducible synthetic DNS capture containing distinct behavioural clusters.
2. Extract queries, record types, response codes and timings with `tshark`.
3. Compute per-domain statistics: unique names, label length, character entropy, record-type mix, and inter-arrival
   jitter.
4. Run Zeek over the same capture and reconcile its view with your own.
5. Classify each cluster, state confidence, and name the benign explanation you rejected.
6. Explain which real-world conditions would make this analysis unreliable.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | Generator and analysis |
| Scapy | current | `pip install scapy` in a virtual environment |
| `tshark` | 4.x | Wireshark CLI |
| Zeek | 9.0.1 LTS | Optional but recommended |

!!! warning "Authorized scope — read before you begin"
    **This lab generates its own traffic.** No live DNS queries are required, and none should be sent to a public
    resolver as part of the exercise.

    **The pcap is synthetic.** It contains no real domains, no real infrastructure and no payload from any real
    system. Use `.example`/`.test` names only, which are reserved and cannot resolve on the internet.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

An implant uses DNS tunnelling for command and control or exfiltration: data is encoded into subdomain labels and
returned in TXT records. The defender sees the resolver traffic, not the implant. The detection question is whether
behaviour separates the tunnel from legitimate high-cardinality DNS such as CDNs.

## Procedure

### 1. Generate the capture

`gen_dns.py` — deterministic, with an explicit seed:

```python
#!/usr/bin/env python3
"""Generate a synthetic DNS capture with three behavioural clusters. Lab use only."""
import argparse, base64, os, random, string
from scapy.all import DNS, DNSQR, IP, UDP, wrpcap

rng = random.Random(405)

def base32_label(nbytes=30):
    return base64.b32encode(bytes(rng.getrandbits(8) for _ in range(nbytes))).decode().lower().rstrip("=")

def pkt(ts, qname, qtype="A", src="10.10.10.20", dst="10.20.20.1"):
    dns = DNS(id=rng.randrange(65535), qr=0, rd=1, qd=DNSQR(qname=qname, qtype=qtype))
    p = IP(src=src, dst=dst) / UDP(sport=rng.randrange(1024, 65535), dport=53) / dns
    p.time = ts
    return p

def build():
    packets, t = [], 1_790_000_000.0

    # Cluster A: a normal application - few names, short labels, A/AAAA, human-ish irregular timing
    for i in range(40):
        t += rng.uniform(0.5, 9.0)
        qname = rng.choice(["api.lab-app.example", "login.lab-app.example", "cdn.lab-app.example"])
        packets.append(pkt(t, qname, rng.choice(["A", "AAAA"])))

    # Cluster B: CDN-like - many unique short labels under one known parent, A records
    for i in range(120):
        t += rng.uniform(0.2, 1.5)
        packets.append(pkt(t, f"img{i:04d}.static.lab-cdn.example", "A"))

    # Cluster C: tunnelling-like - long random labels, TXT queries, precise 5s cadence
    for i in range(60):
        t += 5.0 + rng.uniform(-0.05, 0.05)
        packets.append(pkt(t, f"{base32_label()}.t.exfil-lab.example", "TXT"))

    # Cluster D: DGA-like - random 12-char labels across three sibling domains
    # (this capture holds queries only, so the NXDOMAIN rate a real DGA produces is not observable here)
    for i in range(50):
        t += rng.uniform(0.1, 0.8)
        label = "".join(rng.choice(string.ascii_lowercase + string.digits) for _ in range(12))
        packets.append(pkt(t, f"{label}.{rng.choice(['bad1', 'bad2', 'bad3'])}.test", "A"))

    return packets

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dns-mixed.pcap")
    a = ap.parse_args()
    pkts = build()
    wrpcap(a.out, pkts)
    print(f"wrote {len(pkts)} packets to {a.out}")
```

```bash
python3 -m venv ~/dns-venv && source ~/dns-venv/bin/activate
pip install scapy
python3 gen_dns.py --out dns-mixed.pcap
capinfos dns-mixed.pcap | head -12
```

**Expected:** about 270 packets, a valid pcap that `capinfos` and `tshark` can read.

**Note the design:** clusters A, B and C share a resolver and a port. They differ in label length, record type,
cardinality and timing — not in protocol.

### 2. Extract the query stream

```bash
tshark -r dns-mixed.pcap -Y "dns.flags.response == 0" \
  -T fields -e frame.time_epoch -e ip.src -e dns.qry.name -e dns.qry.type \
  > queries.tsv
wc -l queries.tsv
sort -k3 queries.tsv | head -5
awk -F'\t' '{print $4}' queries.tsv | sort | uniq -c
```

**Expected:** 270 query rows; type counts dominated by A (187) and AAAA (23), with a distinct TXT block of 60
(type 16).

**Why request-only:** the generator writes queries only. A real analysis also inspects responses — TXT payload length,
answer counts, and the NXDOMAIN ratio that makes a DGA obvious. None of those are measurable here, which is why the
DGA judgement below is medium confidence and why adding responses is an extension exercise.

### 3. Compute behaviour statistics

`analyse.py`:

```python
#!/usr/bin/env python3
import csv, math, statistics as st
from collections import defaultdict, Counter

def entropy(s):
    if not s:
        return 0.0
    counts = Counter(s)
    return -sum((c / len(s)) * math.log2(c / len(s)) for c in counts.values())

rows = []
with open("queries.tsv", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 4:
            continue
        rows.append({"ts": float(parts[0]), "src": parts[1], "qname": parts[2], "qtype": parts[3]})

by_parent = defaultdict(list)
for r in rows:
    labels = r["qname"].split(".")
    parent = ".".join(labels[-2:])          # registrable domain
    by_parent[parent].append(r)

print(f"{'parent':<26}{'n':>5}{'uniq':>6}{'maxlab':>7}{'ent':>6}{'txt%':>6}{'jit':>6}")
for parent, evs in sorted(by_parent.items()):
    names = [e["qname"] for e in evs]
    labels = [n.split(".")[0] for n in names]
    times = sorted(e["ts"] for e in evs)
    gaps = [b - a for a, b in zip(times, times[1:])] or [0.0]
    jitter = (st.pstdev(gaps) / st.mean(gaps)) if st.mean(gaps) else 0.0
    txt = sum(1 for e in evs if e["qtype"] == "16") / len(evs)
    print(f"{parent:<26}{len(evs):>5}{len(set(names)):>6}{max(map(len, labels)):>7}"
          f"{st.mean(map(entropy, labels)):>6.2f}{txt:>6.0%}{jitter:>6.2f}")
```

```bash
python3 analyse.py | tee stats.txt
```

**Expected output from the seeded generator** (small differences are normal if you change the seed):

```text
parent                      n  uniq maxlab   ent  txt%   jit
bad1.test                  19    19     12  3.34    0%  0.63
bad2.test                   9     9     12  3.36    0%  0.61
bad3.test                  22    22     12  3.28    0%  0.76
exfil-lab.example          60    60     48  4.47  100%  0.01
lab-app.example            40     3      5  1.86    0%  0.61
lab-cdn.example           120   120      7  2.42    0%  0.43
```

**Why registrable domain and not the last three labels:** grouping by three labels splits the DGA cluster into 50
single-query "domains", each of which looks insignificant. Grouped by registrable domain, the DGA appears as three
sibling domains with many one-shot random labels — which is the actual behavioural signal. Choose the grouping unit to
match the question you are asking.

**The discriminating combination** is: one parent domain, long labels, high entropy, TXT, and a cadence with almost no
jitter (`0.01` versus `0.43` for the CDN). Each feature alone has a benign explanation; the conjunction is hard to
explain innocently.

Note also what the CDN does *not* do: 120 unique names, but labels of at most seven characters, no TXT queries, and
human-scale jitter. Cardinality alone would have flagged it.

### 4. Zeek's view

```bash
zeek -r dns-mixed.pcap
head -3 dns.log
zeek-cut query qtype_name rcode_name < dns.log | awk '{print $2}' | sort | uniq -c
```

**Expected:** `dns.log` with one row per query, `qtype_name` including `TXT`, and the same cardinality you computed.

Now add a notice for long labels — `scripts/long_label.zeek`:

```zeek
module Lab405;

export {
    redef enum Notice::Type += { Long_Label };
}

event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count)
    {
    local labels = split_string(query, /\./);
    for ( i in labels )
        {
        if ( |labels[i]| >= 40 )
            NOTICE([$note=Long_Label,
                    $msg=fmt("DNS label of %d chars in %s", |labels[i]|, query),
                    $sub=query]);
        }
    }
```

```bash
zeek -r dns-mixed.pcap scripts/long_label.zeek
zeek-cut note msg < notice.log | head -5
wc -l notice.log
```

**Expected:** 60 notices, all from the tunnelling cluster, none from the CDN cluster. That is the point: the CDN has
120 unique names and triggers nothing, because its labels are short.

**Why a length threshold is not a detection by itself:** legitimate service names, DKIM selectors and some CDN
schemes can exceed 40 characters. The notice narrows the field; the finding comes from the combination in step 5.

### 5. Write the judgement

`analysis.md`:

| Cluster | Classification | Confidence | Evidence | Benign alternative considered and rejected |
| --- | --- | --- | --- | --- |
| `lab-app.example` | Normal application | High | 3 names, A/AAAA, irregular timing, entropy 1.86 | — |
| `lab-cdn.example` | CDN-like content delivery | High | 120 unique names, labels ≤ 7 chars, A only, moderate jitter | Tunnelling: rejected because labels are short and low entropy, and there are no TXT queries |
| `exfil-lab.example` | Probable DNS tunnel | High (in this synthetic set) | 60 unique 48-char high-entropy labels, 100% TXT, jitter 0.01 | Telemetry/SaaS: rejected because of label shape and precision cadence |
| `bad1.test`, `bad2.test`, `bad3.test` | Probable DGA | Medium | Random 12-char labels, entropy ≈ 3.3, one query per name, three sibling domains | Ad/tracking domains: rejected because names are random, one-shot, and span several unrelated parents with no reuse |

Then state the limits in `limits.md`:

1. The capture is synthetic; real captures include responses, TCP fallback and retries.
2. No responses, so TXT payload size, answer counts and the NXDOMAIN ratio are unmeasured — the last of these is a
   primary DGA indicator, which is why the DGA verdict is the weakest of the four.
3. Encrypted DNS (DoH/DoT) to an external resolver would remove this visibility entirely unless the resolver is
   controlled.
4. A tunnel over A records with short labels and jittered timing would evade every feature used here.
5. `.test` and `.example` are reserved names; real DGA analysis also uses registration age and reputation.

### 6. One defensive recommendation

In `recommendation.md`, propose **one** control and its cost:

- Resolver allowlisting (egress DNS only to a controlled resolver), or
- Response-size and TXT-rate thresholds on the resolver, or
- Blocking of long-label queries for non-allowlisted domains.

For your choice, state the operational cost, the false-positive risk, and how you would test it before enforcing.

## Evidence to collect

- `gen_dns.py`, `dns-mixed.pcap`, `capinfos` output.
- `queries.tsv`, `analyse.py`, `stats.txt`.
- `dns.log`, `notice.log`, the Zeek script.
- `analysis.md`, `limits.md`, `recommendation.md`.

## Verification

- [ ] Capture is reproducible from the script and seed, and contains four clusters.
- [ ] Extraction uses request packets only, and that choice is stated.
- [ ] Statistics include cardinality, label length, entropy, record type and jitter.
- [ ] Zeek output reconciles with the tshark-derived counts.
- [ ] The long-label notice fires only on the tunnelling cluster.
- [ ] Classification tables name the benign alternative that was rejected.
- [ ] Limitations include DoH and a short-label tunnel.
- [ ] Exactly one recommendation, with cost and test plan.

## Teardown and reset

```bash
deactivate 2>/dev/null || true
rm -rf ~/dns-venv
```

Keep the capture and the reports; they are the artefact. The pcap is synthetic and safe to retain.

## Reflection

1. Which single feature best separated the tunnel from the CDN, and why is it not sufficient alone?
2. The CDN cluster has more unique names than the tunnel. What does that tell you about using cardinality thresholds?
3. Your analysis sees queries only. Name two things response inspection would add.
4. A tunnel uses short labels over A records with human-like timing. Which features survive, and what would you need
   instead?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Extraction | Reads pcap manually | tshark fields extracted | Reproducible pipeline, request/response limitation stated |
| Analysis | Counts domains | Length and cardinality | Entropy, type mix and jitter, per parent domain |
| Judgement | "Looks suspicious" | Classifies clusters | Confidence plus the rejected benign explanation |
| Limits | None | DoH mentioned | Short-label tunnel and response-blind analysis named, with one costed recommendation |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: scapy` | Wrong interpreter or venv inactive | Activate the venv; `pip install scapy` |
| `wrpcap` writes an empty file | Packet list empty, or exception swallowed | Print `len(pkts)`; run without redirecting stderr |
| `tshark: command not found` | Wireshark CLI not installed | `sudo apt install tshark` |
| No TXT rows | Field name mismatch (`dns.qry.type` numeric) | Types are numeric in tshark output; `16` is TXT |
| Empty `dns.log` | Zeek run in the wrong directory or pcap unreadable | Check `zeek -r` output; look for `reporter.log` |
| Notice fires on CDN too | Threshold too low for your synthetic names | Inspect the longest CDN label; adjust and record why |
| Jitter looks identical everywhere | Timestamps regenerated per run with a different seed | Keep the seed fixed; regenerate once and reuse the pcap |

## References

1. Scapy — DNS layer and `wrpcap`. <https://scapy.readthedocs.io/> Accessed 2026-10-29.
2. Wireshark/tshark — `dns` display filter fields. <https://www.wireshark.org/docs/dfref/d/dns.html> Accessed
   2026-10-29.
3. Zeek 9.0.1 — `dns_request`, `NOTICE`, `dns.log`. <https://docs.zeek.org/> Accessed 2026-10-29.
4. MITRE ATT&CK — T1071.004 DNS, T1048.003 Exfiltration Over Unencrypted Non-C2 Protocol, T1568.002 DGA.
   <https://attack.mitre.org/> Accessed 2026-10-29.
5. RFC 2606 — reserved `.test`, `.example` names. Accessed 2026-10-29.

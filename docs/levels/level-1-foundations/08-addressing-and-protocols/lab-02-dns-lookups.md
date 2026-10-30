---
title: "LAB-108-02 · Read DNS Lookup Results"
description: "Interpret dig output for common record types, observe caching and TTLs, and prove the difference between hosts-file and DNS resolution."
module_code: CYB-108
level: 1
kind: lab
prerequisites: [CYB-108]
estimated_minutes: 45
difficulty: beginner
safety: local-only
lab_ids: [LAB-108-02]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [networking, dns, dig, troubleshooting]
---

# LAB-108-02 · Read DNS Lookup Results

**Module:** CYB-108 · **Time:** 45 minutes · **Safety:** local-only · **Snapshot:** `pre-lab-108-02`

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** your own resolver configuration and the `/etc/hosts` file on your lab VM.
    **What you may query:** public DNS records for documentation domains (lookups only), and names you
    create locally.

    A DNS lookup is a query, not an attack. Do not attempt zone transfers, enumeration of third-party
    domains, or any query pattern designed to extract bulk records from a system you do not own.

## Objective

Read and explain `dig` output for `A`, `AAAA`, `MX`, `TXT`, and `NS` records; demonstrate hosts-file
override; and distinguish a negative answer from a transport failure.

## Threat model

None. Read-only queries plus one temporary local file entry.

## Environment

| Host | Role | Notes |
| --- | --- | --- |
| `lab-ubuntu` | Client and local resolver | `dnsutils` installed |

Two modes: **online** (VM has temporary internet access) or **offline** (isolated). Every step has an
offline path, because a properly isolated lab will fail public lookups by design.

## Before you start

```bash
sudo apt install -y dnsutils
dig -v
```

Confirm the resolver in use:

```bash
resolvectl status 2>/dev/null | grep -A2 "DNS Servers" || cat /etc/resolv.conf
```

## Procedure

### Step 1 — Evidence folder

```bash
mkdir -p ~/cyber/level-1/lab-108-02/evidence
cd ~/cyber/level-1/lab-108-02
```

### Step 2 — A and AAAA records (online)

```bash
dig example.com A +noall +answer | tee evidence/a.txt
dig example.com AAAA +noall +answer | tee -a evidence/a.txt
```

**Expected** (addresses change over time):

```text
example.com.  3600  IN  A  93.184.216.34
```

Read the columns: name, TTL (seconds), class, type, value. **TTL** is how long a resolver may cache the
answer — which is why a DNS change can take hours to appear everywhere.

### Step 3 — Other record types (online)

```bash
dig example.com MX +short    | tee evidence/other.txt
dig example.com TXT +short   >> evidence/other.txt
dig example.com NS +short    >> evidence/other.txt
```

**Expected:** MX may return nothing (the documentation domain publishes a null MX), TXT often includes SPF
and verification strings, NS lists authoritative servers.

### Step 4 — Reverse lookup

```bash
dig -x 93.184.216.34 +short
```

**Expected:** a hostname, or nothing. Missing PTR records are normal and matter when you rely on reverse
lookups for log enrichment.

### Step 5 — Offline path: local resolution

If your VM is isolated, public lookups time out. Do this instead — it teaches the same lesson:

```bash
sudo cp /etc/hosts /etc/hosts.bak
echo '192.0.2.20  portal.example.test' | sudo tee -a /etc/hosts
getent hosts portal.example.test | tee evidence/local.txt
curl -s -m 2 http://portal.example.test/ -o /dev/null; echo "curl exit: $?" | tee -a evidence/local.txt
```

**Expected:**

```text
192.0.2.20      portal.example.test
curl exit: 7
```

The name resolved (hosts file), the connection was refused (nothing on port 80). **Two separate facts** —
that distinction is the point of the lab.

### Step 6 — Negative answer versus transport failure

```bash
dig nonexistent.invalid A +noall +comments +stats 2>&1 | head -12
getent hosts nonexistent.invalid; echo "getent exit: $?"
```

**Expected (online):** status `NXDOMAIN` in the comments — the name does not exist.
**Expected (offline):** a timeout or `communications error`, and `getent` exit code 2.

Write one sentence in `findings.md` explaining the difference between "the name does not exist" and "I could
not reach a resolver at all".

### Step 7 — Clean up the hosts entry

```bash
sudo mv /etc/hosts.bak /etc/hosts
getent hosts portal.example.test; echo "should be empty, exit: $?"
```

## Evidence to collect

`evidence/a.txt`, `evidence/other.txt`, `evidence/local.txt`, and `findings.md` with your two-sentence
explanation.

## Verification

- [ ] You can name the five columns of a `dig` answer line.
- [ ] You observed TTL and can explain what it controls.
- [ ] You resolved a name via `/etc/hosts` and showed the connection still failed.
- [ ] You distinguished NXDOMAIN from a resolver timeout (or documented which mode you ran).
- [ ] `/etc/hosts` is restored and the test entry is gone.

## Teardown and reset

```bash
sudo sed -i '/portal.example.test/d' /etc/hosts
grep -c example.test /etc/hosts || true
rm -f /etc/hosts.bak 2>/dev/null
```

Revert to `pre-lab-108-02` if your resolver configuration was altered for the online path.

## Reflection

1. Why does a resolver cache answers, and how does TTL make incident timelines confusing?
2. If `dig` returns NXDOMAIN for a domain a user insists exists, what are two plausible explanations?
3. Why is a hosts-file override a useful attack technique, and what would detect it?
4. In the offline path, why did the name resolve but the request fail?

## Rubric

| Criterion | 1 — Not yet | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Correctness | Output collected without interpretation | Records identified and explained | Explains TTL, negative answers, and resolution order |
| Methodology | Ran commands randomly | Ordered lookups | Chooses record types to answer a specific question |
| Evidence | Unsaved output | Saved transcripts | Saved, annotated, with the resolver configuration recorded |
| Safety | Queried or enumerated systems beyond scope | Lookups only | Lookups only, plus explicit note on what was not attempted |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `dig: command not found` | `dnsutils` missing | `sudo apt install -y dnsutils` |
| Everything times out | Isolated lab (expected) | Use the offline path in step 5 |
| `connection timed out; no servers could be reached` | No resolver configured | Check `resolvectl status`; fix netplan or DNS setting |
| `getent` shows nothing | Entry not added, or typo | `grep example.test /etc/hosts` |
| `curl exit: 6` instead of 7 | Name did not resolve at all | Confirm the hosts entry exists |
| Hosts file appears restored but old entry remains | Duplicate lines | `grep -n` then delete the specific line with `sed -i` |

## Related

- [IPv4 Addressing, Subnets, ARP, DNS and DHCP](01-addressing-subnets-dns.md)
- [LAB-108-01 · Inspect Network Configuration](lab-01-network-configuration.md)
- [Troubleshooting](../../../start-here/troubleshooting.md)

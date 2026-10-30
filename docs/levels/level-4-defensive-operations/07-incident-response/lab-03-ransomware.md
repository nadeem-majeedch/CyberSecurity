---
title: "LAB-407-03 · Simulated Ransomware: Contain and Recover"
description: "Run a bounded mock-ransomware script against fake documents, then preserve evidence, isolate the host, and restore from a verified backup."
module_code: CYB-407
level: 4
kind: lab
prerequisites: [CYB-407]
estimated_minutes: 120
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-407-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [ransomware, containment, recovery, backup, rto, rpo, isolation]
---

# LAB-407-03 · Simulated Ransomware: Contain and Recover

## Scenario and background

A file server is renaming documents and leaving a note. You have a backup from this morning, an RTO of two hours, and
a decision to make: restore, rebuild, or keep working and hope.

The "ransomware" here is a **bounded mock script**. It appends a marker to files in one directory, renames them with a
new extension, and writes a note. It does not encrypt, does not propagate, does not touch system files, and refuses to
run outside its target directory.

## Learning objectives

1. Preserve evidence before containment, and record the order.
2. Isolate a host at the network layer without powering it off.
3. Scope an incident: what was affected, what was reachable, what was not.
4. Eradicate the mechanism and any persistence, and rotate exposed credentials.
5. Restore from a verified backup and prove integrity against a manifest.
6. Decide restore versus rebuild against stated RTO and RPO.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Ubuntu | 24.04 | `lab-ubuntu` |
| Python | 3.10+ | Mock script |
| `nftables` | current | Isolation rules |
| `tar`, `sha256sum` | coreutils | Backup and manifest |
| Snapshot | — | Taken before step 2 |

!!! warning "Authorized scope — read before you begin"
    **The script is a simulation.** It performs text replacement and renaming only, inside
    `/srv/lab407/victim`. It contains a guard that exits if the target path differs. Do not modify the guard, do not
    point it at another directory, and do not run it as root.

    **This is not ransomware and must never be replaced with real ransomware**, even in a VM. The learning is in the
    response, not the payload.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

An attacker with user-level access on a file server deploys a payload that renders documents unusable and demands
payment. Realistic complications you must handle: the backup is reachable from the affected host, the note contains a
contact address, and the payload ran under an account whose credentials may now be known to the attacker.

## Procedure

### 1. Prepare the target and the backup

```bash
sudo mkdir -p /srv/lab407/victim /srv/lab407/backup
sudo chown -R "$USER":"$USER" /srv/lab407

cd /srv/lab407/victim
for i in 1 2 3 4 5 6; do
  printf 'Synthetic document %s for LAB-407-03.\nOwner: lab\n' "$i" > "doc$i.docx"
done
printf 'Synthetic spreadsheet.\n' > budget.xlsx

cd /srv/lab407
tar -czf backup/victim-$(date -u +%Y%m%dT%H%M%SZ).tar.gz -C /srv/lab407 victim
sha256sum backup/*.tar.gz | tee backup/manifest.sha256
tar -tzf backup/*.tar.gz | wc -l
```

**Expected:** seven documents; a backup archive containing them; a manifest with one hash. Record the archive name and
hash in the incident record now — you will compare after recovery.

**Take a VM snapshot before continuing.** Recovery from snapshot is not the exercise, but it is your safety net.

### 2. Declare and assign

`incident-record.md`:

| Field | Entry |
| --- | --- |
| Incident ID | `INC-407-03` |
| Declared (UTC) | |
| Severity | SEV2 (non-critical host, confirmed impact) |
| Commander | you |
| Scribe | you, in a second role, noting the limitation |
| Technical lead | you |
| RTO / RPO | 2 hours / 24 hours |
| Known affected host | `lab-ubuntu` (`/srv/lab407/victim`) |

Note explicitly: "Single responder; no independent scribe. This is a lab limitation and would be a finding in a real
incident."

### 3. The mock payload

`/srv/lab407/mock_ransom.py`:

```python
#!/usr/bin/env python3
"""LAB-407-03 mock ransomware. Renames and marks files in ONE directory. No encryption,
no propagation, no network. Refuses to run outside its target path."""
import datetime as dt, hashlib, pathlib, sys

TARGET = pathlib.Path("/srv/lab407/victim").resolve()
ALLOWED = pathlib.Path("/srv/lab407").resolve()
NOTE = TARGET / "READ_ME_LAB407.txt"
LOG = pathlib.Path("/srv/lab407/mock-actions.log")

def main() -> int:
    if not str(TARGET).startswith(str(ALLOWED)) or TARGET.name != "victim":
        print("refusing: target outside the lab directory", file=sys.stderr)
        return 2
    if not TARGET.is_dir():
        print("refusing: target missing", file=sys.stderr)
        return 2

    for path in sorted(TARGET.glob("*.docx")) + sorted(TARGET.glob("*.xlsx")):
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()[:16]
        marked = data + b"\n[LAB407 MOCK: this file was 'locked' by a harmless simulation]\n"
        locked = path.with_suffix(path.suffix + ".locked")
        locked.write_bytes(marked)
        path.unlink()
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()} renamed {path.name} -> {locked.name} sha256:{digest}\n")

    NOTE.write_text(
        "LAB-407-03 SIMULATION\n\nYour synthetic documents have been renamed.\n"
        "This is not real ransomware. Restore from the backup at /srv/lab407/backup.\n",
        encoding="utf-8",
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```bash
python3 /srv/lab407/mock_ransom.py
ls -l /srv/lab407/victim
cat /srv/lab407/victim/READ_ME_LAB407.txt
```

**Expected:** seven `.locked` files, no original documents, one note. The log records each rename with a content hash.

### 4. Preserve before containing

Do this **before** isolating or cleaning:

```bash
mkdir -p ~/lab407/evidence
cp /srv/lab407/mock-actions.log ~/lab407/evidence/
cp /srv/lab407/victim/READ_ME_LAB407.txt ~/lab407/evidence/
ls -l /srv/lab407/victim > ~/lab407/evidence/listing-after.txt
sha256sum /srv/lab407/victim/*.locked > ~/lab407/evidence/locked-hashes.txt
cp /srv/lab407/victim/doc1.docx.locked ~/lab407/evidence/sample-locked.bin
sha256sum ~/lab407/evidence/* > ~/lab407/evidence/evidence-manifest.txt
ps -eo pid,ppid,user,cmd --sort=start_time | tail -20 > ~/lab407/evidence/processes.txt
```

**Record the time of each command.** This is the sequence a reviewer will check: evidence preserved at T1, isolation at
T2, with T1 < T2.

**What you cannot recover now:** the original file contents in place, and any process state from before the script
exited. State that in the record — it bounds what the investigation can claim.

### 5. Contain at the network layer

```bash
# Deny all forwarding and input except established sessions and loopback
sudo nft add table inet lab407
sudo nft 'add chain inet lab407 input { type filter hook input priority 0; policy drop; }'
sudo nft add rule inet lab407 input ct state established,related accept
sudo nft add rule inet lab407 input iif lo accept
sudo nft add rule inet lab407 input ip saddr 192.0.2.1 tcp dport 22 accept
sudo nft list chain inet lab407 input
```

**Expected:** SSH from the analyst host still works; everything else inbound is dropped.

Verify isolation from another lab host:

```bash
# from lab-siem or the analyst machine, excluding SSH
nc -zv -w 3 192.0.2.20 8080    # expect timeout
ssh student@192.0.2.20 'echo still-managed'   # expect success
```

**Record:** isolation time, method, what remains reachable, and why SSH was kept (management access for evidence
collection). **Do not power off** — memory and volatile state are already limited, and a shutdown may trigger
destructive behaviour in real incidents.

### 6. Scope

Answer with evidence:

| Question | Evidence | Answer |
| --- | --- | --- |
| Which directory was affected? | `listing-after.txt`, log | `/srv/lab407/victim` only |
| Which files? | `locked-hashes.txt` | seven documents |
| Was the backup reachable from the host? | `ls -l /srv/lab407/backup` | **Yes** — a finding |
| Is there persistence? | `crontab -l`, `systemctl list-timers`, `ls /etc/cron.*` | determine and record |
| Are credentials exposed? | contents of the script, shell history | determine and record |

The backup being on the same host is deliberate. Write it as a finding: "Backup was stored on the affected host and
reachable by the compromised account, so it could have been destroyed. RPO depends on a copy that was not verified
off-host."

### 7. Eradicate

```bash
crontab -l 2>/dev/null | tee ~/lab407/evidence/crontab.txt
systemctl list-timers --all | tee ~/lab407/evidence/timers.txt
ls -la /etc/cron.d /etc/cron.daily 2>/dev/null | tee ~/lab407/evidence/cron-dirs.txt
mv /srv/lab407/mock_ransom.py ~/lab407/evidence/mock_ransom.py.removed
sha256sum ~/lab407/evidence/mock_ransom.py.removed >> ~/lab407/evidence/evidence-manifest.txt
```

**Expected:** no persistence found (record the checks even when negative). Move rather than delete the payload: it is
evidence.

Then rotate the credential the script ran under, and any credential appearing in shell history or scripts. State what
was rotated and when; a rebuilt host with a live credential is not recovered.

### 8. Recover and verify

```bash
sudo mkdir -p /srv/lab407/restore
sudo tar -xzf /srv/lab407/backup/victim-*.tar.gz -C /srv/lab407/restore
find /srv/lab407/restore -type f | sort
cd /srv/lab407/restore/victim && sha256sum *.docx *.xlsx | sort > ~/lab407/evidence/restored-hashes.txt
```

Compare with the manifest taken before the incident. Because the backup was created before the payload ran, you need a
manifest of the **original** files: create one now from the restored set and state that this is a post-hoc comparison
of content, not a pre-incident hash. (If you still have the originals from step 1 in the archive, `tar -tzf` plus
extraction gives byte-identical content; prove it by extracting twice and hashing both.)

| Check | Method | Result |
| --- | --- | --- |
| File count restored | `find ... | wc -l` | 7 |
| Content matches archive | extract twice, `sha256sum`, `diff` | identical |
| Payload removed | `ls /srv/lab407` | absent |
| Host isolated | `nc` from another host | timeout |
| RTO met | declared time vs restore completion | record |
| RPO met | backup age vs incident time | record |

```bash
# Prove the archive is internally consistent: two independent extractions must match
sudo tar -xzf /srv/lab407/backup/victim-*.tar.gz -C /tmp/restore-b
diff -r /srv/lab407/restore/victim /tmp/restore-b/victim && echo "RESTORE IDENTICAL"
```

**Expected:** `RESTORE IDENTICAL`.

### 9. Decide: restore, rebuild, or continue

`decision.md`:

1. Which option you chose and why, referencing RTO/RPO.
2. What trust you place in the restored host, given the payload ran as a normal user and no persistence was found.
3. What heightened monitoring you will apply for 72 hours and what would trigger escalation.
4. What you would need to see before removing the isolation.

**Expected reasoning:** restore is acceptable here because the payload was user-level, no persistence was found, and
the host's integrity can be checked against the package manager (`dpkg --verify`). If kernel-level or credential-theft
activity were suspected, rebuild would be the defensible choice.

## Evidence to collect

- `incident-record.md` with declaration time, roles, RTO/RPO.
- `evidence/` — log, note, listings, hashes, sample, process list, manifest, removed payload, cron/timer checks.
- `scope.md` — the five scope answers.
- `recovery.md` — the verification table and the identical-restore proof.
- `decision.md` — restore/rebuild decision with reasoning.

## Verification

- [ ] Backup created and hashed **before** the simulation ran, and the hash recorded.
- [ ] Evidence preserved before isolation, with timestamps for both.
- [ ] Isolation applied at the network layer, verified with a denied probe; SSH retained deliberately.
- [ ] Host not powered off.
- [ ] Scope table complete, including the on-host backup finding.
- [ ] Persistence checks recorded even where negative.
- [ ] Payload preserved (moved, not deleted) and hashed.
- [ ] Credential rotation stated, not implied.
- [ ] Restore verified by independent extraction comparison.
- [ ] RTO and RPO explicitly assessed.
- [ ] Decision names the alternative and the condition that would change it.

## Teardown and reset

```bash
sudo nft delete table inet lab407 2>/dev/null || true
sudo rm -rf /srv/lab407/restore /tmp/restore-b
```

Revert the snapshot to discard the whole exercise. Keep `~/lab407/evidence` outside the VM.

## Reflection

1. You preserved evidence before isolating. What would you have lost if you had isolated first and cleaned the
   directory?
2. The backup was on the affected host. Name two changes that would make the RPO trustworthy, and their cost.
3. `dpkg --verify` returned clean. Does that prove the host is trustworthy? What else would you check?
4. Your RTO was two hours and the restore took twenty minutes. Why is meeting the RTO not the same as a successful
   recovery?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Preparation | No backup | Backup hashed | Backup verified and its reachability assessed |
| Order | Contained first | Preserved then contained | Both timestamped, with the limitation stated |
| Containment | Host powered off | Network isolation | Isolation verified, SSH retained deliberately |
| Recovery | Files copied back | Restore verified | Independent comparison, RTO/RPO assessed, decision justified |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Script refuses to run | Guard rejected the target path | Use `/srv/lab407/victim` exactly; do not edit the guard |
| No `.locked` files | Wrong directory or permissions | Check `ls -l`, run as the owning user, not root |
| SSH lost after isolation | Rule order or missing established rule | Use the serial console; insert the established rule first |
| `tar` extraction empty | Archive created with a relative path | Check `tar -tzf`; extract at the correct parent |
| Hashes differ after restore | Compared against the locked set, not the archive | Extract the archive twice and compare those |
| RTO impossible | Backup too old or too slow to restore | That is the finding; record actual times, do not adjust the objective |

## References

1. NIST SP 800-61 Rev. 3 — containment, eradication, recovery. Accessed 2026-10-29.
2. CISA #StopRansomware Guide. <https://www.cisa.gov/stopransomware> Accessed 2026-10-29.
3. NIST SP 800-34 Rev. 1 — Contingency Planning Guide (RTO/RPO definitions). Accessed 2026-10-29.
4. MITRE ATT&CK — T1486 Data Encrypted for Impact; T1490 Inhibit System Recovery. Accessed 2026-10-29.

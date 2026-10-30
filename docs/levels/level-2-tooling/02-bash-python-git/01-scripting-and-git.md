---
title: "Scripting and Versioning for Repeatable Work"
description: "Defensive Bash, structured Python parsing, and Git hygiene for lab artefacts."
module_code: CYB-202
level: 2
kind: lesson
prerequisites: [CYB-201]
estimated_minutes: 180
difficulty: intermediate
safety: local-only
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [bash, python, git, automation]
---

# Scripting and Versioning for Repeatable Work

## Learning objectives

By the end of this lesson you can:

1. Write a Bash script with strict mode, input validation, and meaningful exit codes.
2. Explain how quoting, word splitting, and globbing cause real damage.
3. Parse a structured log in Python with validation, summaries, and error handling.
4. Use Git to version lab artefacts while excluding secrets and large binaries.
5. Review any script for the ways it could act outside its intended scope.

## Prerequisites

Level 1 shell skills (CYB-109) and a working lab (CYB-201).

---

## 1. Bash that does not surprise you

Start every script with three things:

```bash
#!/usr/bin/env bash
set -euo pipefail    # exit on error, unset variable, or failed pipe stage
IFS=$'\n\t'          # predictable word splitting
```

| Directive | Effect | Failure it prevents |
| --- | --- | --- |
| `-e` | Exit on non-zero command | Continuing after a failed step and reporting success |
| `-u` | Error on unset variable | `rm -rf "$DIR/"` becoming `rm -rf /` |
| `-o pipefail` | A pipeline fails if any stage fails | `grep ... | head` hiding a broken grep |
| `IFS=$'\n\t'` | Split only on newline/tab | Filenames with spaces splitting into two arguments |

### Quoting rules that matter

```bash
name="lab host"
grep "$name" file.txt        # correct: one argument
grep $name file.txt          # wrong: two arguments, "lab" and "host"
rm -rf "$dir"                # quoted: safe if $dir is set
[ -n "${dir:-}" ] || { echo "dir unset"; exit 2; }
```

Variables are also validated, not assumed:

```bash
target="${1:?usage: $0 <target>}"
case "$target" in
  192.0.2.*) ;;                                    # allowed lab range
  *) echo "refusing non-lab target: $target" >&2; exit 3 ;;
esac
```

That `case` block is a **scope guard**. It is the difference between a lab script and a career-limiting event,
and it is exactly the pattern this course expects in every tool you write from now on.

### Structure of a good checklist script

```bash
#!/usr/bin/env bash
set -euo pipefail
fail=0
check() {                                    # name, command, expectation
  local name="$1" cmd="$2" want="$3" got
  got=$(eval "$cmd" 2>/dev/null || true)
  if [[ "$got" == "$want" ]]; then
    printf '[PASS] %-28s %s\n' "$name" "$got"
  else
    printf '[FAIL] %-28s got=%s want=%s\n' "$name" "$got" "$want"; fail=1
  fi
}
check "ssh password auth" "grep -i '^PasswordAuthentication' /etc/ssh/sshd_config | awk '{print \$2}'" "no"
exit "$fail"
```

Why it works: one function, uniform output, an exit code a pipeline can act on. `shellcheck` (install with
`sudo apt install shellcheck`) catches quoting and portability mistakes automatically — run it on everything
you write:

```bash
shellcheck script.sh
```

## 2. Python for parsing, not for cleverness

Python earns its place when the data is structured. The pattern that scales:

```python
#!/usr/bin/env python3
"""Summarise a synthetic access log by source address and status code."""
import argparse, json, logging, re, sys
from collections import Counter
from pathlib import Path

LINE = re.compile(r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - - \[(?P<ts>[^\]]+)\] "(?P<req>.*?)" (?P<status>\d{3})')

def parse(path: Path, log: logging.Logger) -> tuple[Counter, int]:
    counts, matched, total = Counter(), 0, 0
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        total += 1
        m = LINE.match(line)
        if not m:
            log.debug("unparsed line %d", n)
            continue
        matched += 1
        counts[(m["status"], m["ip"])] += 1
    log.info("parsed %d/%d lines", matched, total)
    return counts, total - matched

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logfile", type=Path)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger("parser")
    if not args.logfile.is_file():
        log.error("no such file: %s", args.logfile)
        return 2
    counts, unmatched = parse(args.logfile, log)
    rows = [{"status": s, "ip": ip, "count": c} for (s, ip), c in counts.most_common(args.top)]
    print(json.dumps(rows, indent=2) if args.json else "\n".join(f"{r['status']} {r['ip']:>15} {r['count']:>5}" for r in rows))
    if unmatched:
        log.warning("%d lines did not match; check the format", unmatched)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Four habits worth copying:

- **Report coverage.** "Parsed 982 of 1000 lines" tells you whether your regex is right. Silence does not.
- **Validate inputs.** Missing file returns exit code 2, not a traceback.
- **Separate output from logs.** Logs go to stderr; data goes to stdout, so `> out.json` works cleanly.
- **Make it testable.** `parse()` takes a path and returns data — no printing inside the logic.

## 3. Git for lab artefacts

Track scripts, notes, and sanitised evidence. Do **not** track secrets, VM images, or multi-gigabyte captures.

```bash
git init lab-notebook && cd lab-notebook
cat > .gitignore <<'GI'
*.pcap
*.pcapng
*.log
*.key
*.pem
id_*
.env
evidence/raw/
GI
git add .gitignore
git commit -m "chore: initialise lab notebook with ignore rules"
```

The rules that keep you out of trouble:

| Rule | Why |
| --- | --- |
| Write `.gitignore` **before** the first `git add` | Once committed, a secret is in history even if you delete the file |
| Ignore captures and images | Repositories are for text, not binaries |
| Commit small and often, with real messages | `git log` becomes your lab timeline |
| Never commit credentials, keys, or hashes of real passwords | Irreversible leak |
| Use branches for experiments | `git checkout -b lab-203-nmap` keeps `main` clean |

Useful commands:

```bash
git status --short
git diff                      # review before committing
git log --oneline --stat | head -20
git restore --staged FILE     # unstage without losing work
git rm --cached FILE          # stop tracking (file stays on disk)
```

If you ever commit a key by accident: assume it is compromised, revoke or regenerate it, and rotate anything
it protected. Deleting the commit is not sufficient.

---

## Practical exercises

### Exercise 1 — Fix the broken script (15 minutes)

```bash
cat > /tmp/broken.sh <<'SH'
#!/bin/bash
dir=/tmp/demo
rm -rf $dir/
echo "cleaned $dir"
SH
```

List three defects (unset-variable behaviour, unquoted expansion, no exit-code check) and rewrite it with
strict mode and validation.

### Exercise 2 — Scope guard (15 minutes)

Add a `case` guard to a script that takes a target argument, refusing anything outside `192.0.2.0/24`. Test it
with `192.0.2.20` (accepted) and `8.8.8.8` (refused, exit 3).

### Exercise 3 — Parsing coverage (20 minutes)

Take any log file you have produced in Level 2 and write the smallest Python regex that matches its main lines.
Run it and report the match ratio. Anything below 95% means your pattern is wrong or the log has more than one
format — both are findings.

### Exercise 4 — Git hygiene audit (10 minutes)

```bash
git ls-files | head -20
git log --oneline | head -5
git check-ignore -v evidence/raw/x.pcap 2>/dev/null || echo "NOT ignored"
```

Confirm nothing sensitive or large is tracked, and that your ignore rules actually match the paths you intended.

## Expected observations and verification

- Your strict-mode script exits non-zero when a check fails.
- The scope guard refuses an out-of-range target with a distinct exit code.
- Your parser reports parsed/total counts.
- `git check-ignore` confirms captures and keys are excluded.
- `shellcheck` reports no errors on your final script (warnings explained if left).

## Common mistakes and troubleshooting

| Mistake | Why it happens | Fix |
| --- | --- | --- |
| No `set -euo pipefail` | Scripts "work" until they do not | Add it first, then validate inputs |
| Silent failures | Output looks like success | Print status per check, return a non-zero exit code |
| Regex that matches 60% of lines | Pattern written from one example | Report coverage and iterate |
| `git add -A` after creating a key | Speed | Read `git status` first; use a `.gitignore` |
| Committing a pcap | It was in the folder | Add to `.gitignore`, `git rm --cached` |
| Script with a hard-coded target | Convenience | Argument plus scope guard |
| `eval` on untrusted input | Shortcut | Avoid; parse instead of execute |

## Review questions

1. What does each of `set -euo pipefail` protect against?
2. Why is a scope guard part of a safe script rather than an optional extra?
3. Why should a parser report how many lines it did not match?
4. What must be in `.gitignore` before the first commit, and why is ordering critical?
5. What do you do if you commit a private key by accident?
6. Why keep logs on stderr and data on stdout?

## Knowledge check

1. Which shell option makes a pipeline fail when any stage fails?
2. What does exit code 2 conventionally mean in these scripts?
3. What does `git rm --cached FILE` do to the working copy?
4. Why does an unquoted `$dir` risk deleting more than intended?
5. Name two artefact types that should never be committed.

*(Self-mark against the summaries above; the keyed module quiz is under Assessments. Re-read sections 1 and 3 if 1, 3 and 5 are uncertain.)*

## Summary

- Strict mode, quoting, and validation turn a script from a liability into a control.
- Scope guards encode the authorization boundary in code, where it cannot be forgotten.
- Python parsers should validate inputs, report coverage, and keep logic separate from output.
- Git tracks text artefacts; secrets, keys, and captures stay out via `.gitignore` written first.
- Review before you commit, and treat any committed secret as compromised.

## Next lesson

[CYB-203 · Host Discovery and Service Enumeration](../03-host-discovery-and-enumeration/index.md) — applying
scripts and tools to your own lab network.

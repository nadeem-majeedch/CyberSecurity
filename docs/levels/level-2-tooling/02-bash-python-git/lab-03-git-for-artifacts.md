---
title: "LAB-202-03 · Version Lab Artefacts with Git"
description: "Create a lab notebook repository, exclude secrets and captures, and use history as an audit trail."
module_code: CYB-202
level: 2
kind: lab
prerequisites: [CYB-202]
estimated_minutes: 120
difficulty: intermediate
safety: local-only
lab_ids: [LAB-202-03]
version: 1.0.0
last_reviewed: 2026-10-28
reviewers: []
status: published
tags: [git, artifacts, evidence, hygiene]
---

# LAB-202-03 · Version Lab Artefacts with Git

## Prerequisites

The CYB-202 lesson and Git on the analyst host. Any artefact to version will do — the script from
LAB-202-01 or the parser from LAB-202-02 are the natural choices.

## Scenario and background

An assessment without history is an opinion. Version control turns your scripts, notes, and sanitised evidence
into a timeline: what changed, when, and why. It also creates a specific hazard — repositories are copy-paste
friendly, so a private key or a capture containing credentials can leave your machine silently.

This lab builds the habit of writing ignore rules **first**, committing small and often, and reviewing before
every commit.

## Learning objectives

By the end of this lab you can:

1. Initialise a repository with ignore rules in place before the first commit.
2. Record a lab timeline with meaningful commit messages.
3. Use branches for experiments and merge only reviewed work.
4. Verify that secrets, keys, and captures are excluded.
5. Recover from a mistaken commit correctly (revoke, do not just delete).

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Git | 2.34+ | `git --version` |
| Bash | 5.x | Shell commands |

## Setup

```bash
mkdir -p ~/lab/level-2/lab-202/artifacts && cd ~/lab/level-2/lab-202
git config --global user.name  "Lab Learner"        # use your own name
git config --global user.email "learner@example.test"  # local-only identity
git config --global init.defaultBranch main
```

Using a documentation domain for the email keeps lab commits distinguishable from your real identity.

## Target addresses and lab topology

```
Local repository only: ~/lab/level-2/lab-202/artifacts
No remote is configured; nothing leaves the machine in this lab.
```

## Numbered commands and actions

### 1. Initialise with ignore rules first

```bash
cd ~/lab/level-2/lab-202/artifacts
git init
cat > .gitignore <<'GI'
# Never commit secrets or key material
*.key
*.pem
id_rsa*
id_ed25519*
.env
*.kdbx

# Large or sensitive evidence
*.pcap
*.pcapng
*.raw
*.E01
evidence/raw/

# Generated output
site/
__pycache__/
*.pyc
report/acme-*
GI
git add .gitignore
git commit -m "chore: initialise lab notebook and ignore secrets, captures and generated output"
git log --oneline
```

**Why first:** `.gitignore` only prevents *future* additions. Anything committed before the rules existed is in
history permanently and must be treated as leaked.

### 2. Add artefacts in logical commits

```bash
mkdir -p scripts notes evidence/raw
cp ../scripts/parse-log.py scripts/ 2>/dev/null || cp ~/lab/level-2/lab-202/scripts/parse-log.py scripts/
cp ../scripts/security-check.sh scripts/ 2>/dev/null || cp ~/lab/level-2/lab-202/scripts/security-check.sh scripts/
printf '# Lab notebook\n\nDate, host, and what was done. One entry per session.\n' > notes/README.md
git add scripts/parse-log.py
git commit -m "feat(parser): summarise access logs with coverage reporting"
git add scripts/security-check.sh
git commit -m "feat(checks): read-only local security baseline script"
git add notes/README.md
git commit -m "docs: add lab notebook conventions"
git log --oneline --stat | head -20
```

**Why small commits:** a reviewer can see one idea per commit, and `git log` becomes a readable narrative of
your work — which is exactly what an assessment reviewer wants.

### 3. Prove the ignore rules work

```bash
# Create files that must never be committed
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out lab.key 2>/dev/null
tcpdump -i lo -c 3 -w evidence/raw/demo.pcap 2>/dev/null || printf 'fake\n' > evidence/raw/demo.pcap
printf 'API_TOKEN=not-a-real-token\n' > .env

git status --short
git check-ignore -v lab.key evidence/raw/demo.pcap .env
```

**Expected:** `git status --short` shows none of those three files as untracked, and `git check-ignore -v`
prints the matching rule and line for each — for example:

```text
.gitignore:4:*.key	lab.key
.gitignore:11:evidence/raw/	evidence/raw/demo.pcap
.gitignore:8:.env	.env
```

If any of them appears in `git status`, your rules did not match the path — fix the pattern now.

### 4. Work on a branch

```bash
git checkout -b lab-202-evidence
cp ~/lab/level-2/lab-202/evidence/parse-report.txt evidence/ 2>/dev/null || echo "parse-report.txt" > evidence/parse-report.txt
git add evidence/parse-report.txt
git commit -m "docs(evidence): record parser output for the synthetic log"
git checkout main
git merge --no-ff lab-202-evidence -m "merge: bring in parser evidence from lab branch"
git log --graph --oneline | head -8
```

**Why a branch:** experiments stay isolated, and `main` always represents reviewed work.

### 5. Practise reviewing before committing

```bash
printf 'host,lab-ubuntu\ntarget,192.0.2.20\n' > notes/addresses.csv
git diff --cached --stat || true
git add notes/addresses.csv
git diff --cached
```

Read the diff before committing. Ask: does this contain anything that should not leave the machine — a token, a
hostname belonging to your employer, a real person's data?

### 6. Handle the "I committed a key" scenario (tabletop, not a real key)

Do **not** commit a real key to test this. Instead, reason it through and record the answer in
`notes/secret-history-policy.md`:

| Situation | Correct action |
| --- | --- |
| A lab-only throwaway key was committed | Still rotate it; history is permanent and may be cloned |
| A real key or token was committed | Revoke/rotate immediately, then clean up history |
| A capture with credentials was committed | Treat credentials as compromised; rotate; then remove |
| Unsure whether a file is sensitive | Assume it is; do not commit; ask |

The lesson: **removing a file does not remove it from history.** `git rm --cached` stops tracking; it does not
erase. History rewriting is a last resort, and only after rotation.

## Important command options explained

| Option | Meaning | Why used here |
| --- | --- | --- |
| `git check-ignore -v PATH` | Show which rule ignores a path | Proves your rules work, rather than assuming |
| `git add PATH` (not `-A`) | Stage exactly one thing | Avoids accidentally staging a secret |
| `git diff --cached` | Review staged content | The last chance before it is recorded |
| `--no-ff` merge | Create a merge commit | Preserves that the work happened on a branch |
| `git log --graph` | Visual history | Confirms branch structure |

## Expected observations

- The first commit contains only `.gitignore`.
- Three or more focused commits exist for scripts and notes.
- `git status` never lists `lab.key`, `.env`, or the `.pcap` under `evidence/raw/`.
- `git check-ignore -v` gives a rule for each excluded path.
- The branch merge appears in `git log --graph`.
- `notes/secret-history-policy.md` exists with the rotation-first principle.

## Verification criteria

- [ ] `.gitignore` committed before any artefact.
- [ ] At least four commits with descriptive messages.
- [ ] Three sensitive-looking files created and confirmed ignored.
- [ ] A branch was created, committed to, and merged.
- [ ] Staged content reviewed with `git diff --cached` before committing.
- [ ] Secret-history policy documented.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `fatal: not a git repository` | Wrong directory | `cd` into the repository root |
| Ignore rule does not match | Pattern anchored wrong (`/raw/` vs `raw/`) | Use `git check-ignore -v` to see which rule matched |
| File already committed before the rule | Rule added too late | `git rm --cached FILE`, rotate anything sensitive |
| `git commit` opens an editor and hangs | No `-m` given | Provide `-m`, or set `core.editor` |
| Merge conflict in a notes file | Both branches edited the same lines | Edit to keep both entries; conflicts are normal in notes |
| Cannot see the ignored file at all | It is ignored, which is correct | Use `git ls-files --others --ignored --exclude-standard` to list |

## Cleanup and restoration

```bash
rm -f ~/lab/level-2/lab-202/artifacts/lab.key
git -C ~/lab/level-2/lab-202/artifacts status --short
```

Keep the repository — LAB-206-03 adds the assessment report to it. Do not configure a remote and do not push;
publishing lab material is a separate, deliberate decision.

## Questions and extension challenges

1. Why does an ignore rule added after a commit not protect the secret?
2. What does `git diff --cached` show that `git status` does not?
3. Why is a documentation-domain email a good choice for lab commit identity?
4. **Extension:** add a pre-commit hook that refuses to commit files matching `*.key`, `*.pem`, or `.env`, and
   explain what class of mistake it prevents.
5. **Extension:** write a `commit-message` convention for your lab notebook and apply it retroactively with an
   interactive rebase message edit.

## Related

- [Scripting and Versioning for Repeatable Work](01-scripting-and-git.md)
- [LAB-206-03 · Assessment Report](../06-host-inspection-and-hardening/lab-03-assessment-report.md)
- [Quality Checklist](../../../maintainer/quality-checklist.md)

---
title: "LAB-307-02 · Vulnerable Dependencies"
description: "Inventory a sample project's dependencies, run advisory checks, generate an SBOM, and prioritise by reachability rather than score."
module_code: CYB-307
level: 3
kind: lab
prerequisites: [CYB-307]
estimated_minutes: 90
difficulty: intermediate
safety: local-only
lab_ids: [LAB-307-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [dependencies, supply-chain, pip-audit, sbom, npm-audit]
---

# LAB-307-02 · Vulnerable Dependencies

## Scenario and background

A team inherits a small service. Nobody knows why the versions are what they are, there is no lockfile, and the
last commit is two years old. Before anyone writes code, you need three answers: what is in here, which parts have
known problems, and which of those problems can actually be reached.

This lab is about the gap between a scanner report and a risk assessment. You will produce both, and the second
one is the deliverable.

## Learning objectives

By the end of this lab you can:

1. Inventory direct and transitive dependencies and identify the pins, ranges, and lockfile state.
2. Detect typosquat-shaped names and install-time execution hooks by inspection.
3. Run advisory checks and interpret the output, including what it cannot tell you.
4. Generate an SBOM and use it to answer an "are we affected?" question.
5. Prioritise findings by reachability, runtime role, and exploitability, with stated reasoning.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python + `pip` | 3.10+ | Manifest audit only — do not install the old set |
| `pip-audit` | 2.x | `pip install pip-audit` |
| `cyclonedx-bom` | 4.x | SBOM generation |
| Node.js + `npm` | 18+ | Optional JavaScript half |
| `jq` | 1.6+ | Reading JSON output |

!!! warning "Authorized scope — read before you begin"
    **What this lab touches:** files you create under `~/lab/level-3/lab-307-02`, and public package registries for
    advisory data and metadata.
    **What it must not do:** install the deliberately outdated packages into your system Python, run install
    scripts from untrusted packages, or publish anything.

    **Do not install the old pinned set globally.** Some of these versions do not build on current Python, and
    installing them into a shared environment creates the exact supply-chain exposure you are learning to assess.
    Audit the manifest; if you must install, use a throwaway virtual environment with `--no-deps`.

    Network access is required for the advisory lookups. Attach NAT for those steps only, and detach afterwards.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The adversary is not attacking your lab. The subject is **inherited risk**: a dependency you did not choose, at a
version nobody justified, with an advisory you have not read. The relevant questions are reachability (does our
code call the vulnerable function?), exposure (is the input attacker-controlled?), and role (runtime or build
tool?).

**Impact if exploited.** A vulnerable dependency is a flaw nobody on the team wrote and no code review will show.
When the affected function is reachable with attacker-controlled input, the result ranges from denial of service to
remote code execution, and the fix usually arrives as a version bump nobody scheduled.

## Environment

| Component | Detail |
| --- | --- |
| Python manifest | `requirements.txt`, five pinned packages |
| Node manifest | `package.json`, three pinned packages (optional) |
| Outputs | `audit-before.json`, `sbom-before.json`, `priorities.md`, `audit-after.json` |

## Before you start

```bash
mkdir -p ~/lab/level-3/lab-307-02 && cd ~/lab/level-3/lab-307-02
cat > requirements.txt <<'REQ'
Flask==2.0.1
Jinja2==2.11.2
requests==2.19.1
PyYAML==5.1
Pillow==8.1.0
REQ
```

And, if you have Node available, a JavaScript manifest:

```bash
cat > package.json <<'JSON'
{
  "name": "inherited-service",
  "version": "0.0.1",
  "private": true,
  "dependencies": {
    "lodash": "4.17.15",
    "minimist": "1.2.0",
    "axios": "0.21.1"
  }
}
JSON
```

No `requirements.lock`, no `package-lock.json`, no hashes. That absence is the first finding, and it is worth
noting before any scanner runs.

## Procedure

### 1. Inventory by inspection

```bash
echo "--- manifest"
cat requirements.txt

echo "--- lockfile present?"
ls -1 requirements*.lock Pipfile.lock poetry.lock package-lock.json yarn.lock 2>/dev/null || echo "none"

echo "--- pins versus ranges"
grep -nE '==|>=|~=|\^|latest' requirements.txt package.json 2>/dev/null
```

Record in `evidence/inventory.md`:

| Question | Answer |
| --- | --- |
| Direct dependencies | 5 (Python), 3 (Node) |
| Lockfile | None |
| Pins exact? | Yes, but unhashed |
| Transitive dependencies pinned? | No — resolved at install time |
| Last release of each package | Check the registry page; note any unmaintained |

**Why the missing lockfile matters even with `==` pins:** the pin fixes direct versions, but each direct package
declares its own ranges for its dependencies. Two installs a month apart can produce different trees. A lockfile
plus hashes makes the build reproducible and makes a malicious republish detectable.

### 2. Inspect for supply-chain shapes

Two categories deserve a manual pass, because scanners do not flag them.

**Typosquat-shaped names.** Compare each direct dependency against the canonical spelling:

```bash
for pkg in requests flask jinja2 pyyaml pillow lodash axios minimist; do
  printf '%-10s length=%s\n' "$pkg" "${#pkg}"
done
```

Then ask, for each: is this the exact name from the official documentation, or from memory? Names one edit
distance away (`reqeusts`, `python-dateutil` vs `dateutil`) are the standard attack.

**Install-time execution.** Python packages can run `setup.py` at install; npm packages can define `preinstall`,
`install`, and `postinstall` scripts. You cannot see those hooks from the manifest — you see them after download.
That is the argument for `--ignore-scripts` on npm and for installing Python packages in a disposable environment.

Record both as findings: *"dependency additions are not reviewed for name fidelity or install hooks"* is a process
finding with a concrete control attached.

### 3. Run the advisory check

```bash
python3 -m venv .venv-audit && . .venv-audit/bin/activate
pip install --upgrade pip pip-audit
# NAT attached for the advisory lookup
pip-audit -r requirements.txt --desc --format json -o audit-before.json || true
pip-audit -r requirements.txt --desc | tee evidence/audit-before.txt
```

**Expected:** a list of advisories. The exact set changes as new CVEs are published and old ones are withdrawn, so
record what you get rather than expecting a fixed count. Typical results for this manifest include session-cookie
handling in Flask, header leakage on redirect in old `requests`, and multiple issues in old `Pillow`.

**What `pip-audit` cannot tell you**, and must therefore go in the report as a limitation:

- Whether the vulnerable function is **reachable** from your code.
- Whether your inputs are attacker-controlled at that call site.
- Whether the vulnerable version is even installed (it audits the resolved set, not your runtime).
- Anything about non-Python components, system libraries, or container base images.

### 4. Read one advisory properly

Pick the advisory with the highest score and answer four questions in `evidence/advisory-analysis.md`:

1. Which function or code path is affected?
2. What is the precondition — specific configuration, specific call pattern?
3. Is that path reachable in this application? (For this sample: it has no application code, so the honest answer
   is "unknown — no call sites exist yet".)
4. What does the fix require: a patch bump, a configuration change, or a rewrite?

**Why this step matters more than the scan:** a report that lists CVEs with scores is a data dump. A report that
says "this advisory requires `yaml.load` on untrusted input; our service uses `safe_load` only, therefore not
reachable, patch in the next cycle" is a risk decision somebody can act on.

### 5. Generate the SBOM

```bash
pip install cyclonedx-bom
cyclonedx-py requirements requirements.txt -o sbom-before.json
jq '.components | length' sbom-before.json
jq -r '.components[] | "\(.name) \(.version)"' sbom-before.json | head
```

**Expected:** a CycloneDX document with five components and their versions. Record the component count.

**Why an SBOM at all:** when the next Log4Shell-class advisory lands, the question is "are we affected, and
where?". With an SBOM per release, that is a query. Without one, it is a week of archaeology across build scripts
and container images.

### 6. The JavaScript half (optional)

```bash
if command -v npm >/dev/null; then
  npm install --package-lock-only --ignore-scripts
  npm audit --json > audit-npm.json 2>/dev/null || true
  jq '{vulnerabilities: (.vulnerabilities | keys), total: .metadata.vulnerabilities}' audit-npm.json
fi
```

**Expected:** advisories for at least `lodash` and `minimist`, and probably `axios`.

**Why `--ignore-scripts`:** it prevents `preinstall`/`postinstall` from executing during resolution. It is the
single cheapest npm supply-chain control, and it has no effect on the audit result.

### 7. Prioritise

Build `evidence/priorities.md`:

| Package | Advisory (id) | Function affected | Reachable in our code? | Runtime or build? | Priority | Action |
| --- | --- | --- | --- | --- | --- | --- |
| … | … | … | unknown / yes / no | runtime | High / Med / Low | Bump to X / config change / accept |

Order by priority, and write one paragraph explaining the ordering rule you used. A defensible rule: **reachable
+ runtime + attacker-controlled input** first; unreachable runtime advisories next; build-only last, with a note
that they still matter for build integrity.

### 8. Remediate and re-audit

```bash
cp requirements.txt requirements-before.txt
pip index versions Flask 2>/dev/null | head -2    # check what is current
```

Update each pin to a current, supported release, then re-run:

```bash
cat > requirements.txt <<'REQ'
Flask>=3.0,<4
Jinja2>=3.1,<4
requests>=2.32,<3
PyYAML>=6.0,<7
Pillow>=10.0,<12
REQ
pip-audit -r requirements.txt --format json -o audit-after.json || true
pip-audit -r requirements.txt | tail -5
cyclonedx-py requirements requirements.txt -o sbom-after.json
```

**Expected:** no advisories, or a much shorter list. Record the before/after counts and the SBOM component counts.

**Two honest notes for the report:** version ranges (rather than pins) require a lockfile to stay reproducible, so
"fixed" here means "moved to a maintained line, with a lockfile to be added". And a major-version jump can break
the application — which is why the next step is a test run, not a deployment.

### 9. Write the supply-chain recommendations

Five bullets, each with an owner-shaped action: lockfile with hashes committed; advisory scanning in CI with a
documented exception process; SBOM per release; a review step for new direct dependencies; and a patch cadence.

## Evidence to collect

- `evidence/inventory.md` — manifest state and missing lockfile.
- `evidence/audit-before.txt`, `audit-before.json` — advisory output.
- `evidence/advisory-analysis.md` — one advisory read properly.
- `sbom-before.json`, `sbom-after.json` — component counts.
- `evidence/priorities.md` — the prioritisation table and rule.
- `audit-after.json`, `evidence/audit-after.txt` — post-remediation state.
- `evidence/recommendations.md` — the five controls.

## Verification

- [ ] Manifest, lockfile state, and pin style documented before any tool ran.
- [ ] Advisory check produced output and the exact tool version is recorded.
- [ ] One advisory analysed for affected function, precondition, and reachability.
- [ ] SBOM generated; component count matches the manifest's resolved set.
- [ ] Prioritisation table has a stated rule, not just scores.
- [ ] Post-remediation audit shows fewer or zero advisories, with the before/after counts recorded.
- [ ] Limitations of the tooling are stated in the report.

## Teardown and reset

```bash
deactivate 2>/dev/null
```

Remove `node_modules` if `npm` created one. Detach NAT. Nothing here should be deployed; the manifests are
artefacts for the report, not a service.

## Reflection

1. A `==` pin without a lockfile is not reproducible. Explain what can change between two installs and why hashes
   fix it.
2. The highest-scoring advisory was in a package with no call sites in this application. How does that change its
   priority, and what would you need before deciding it is not exploitable?
3. `--ignore-scripts` prevents install-time execution. Name one attack it stops and one it does not.
4. Your remediation moved to version ranges. What did that fix, and what did it break, in reproducibility terms?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Inventory | Scanner output only | Manifest state documented | Manifest, lockfile gap, and pin style, all before tooling |
| Analysis | CVE list copied | One advisory read | Advisory read with reachability and precondition assessed |
| Prioritisation | Sorted by score | Reachability considered | Reachability, runtime role, and input control, with a stated rule |
| Remediation | Versions bumped | Audit clean | Clean audit plus SBOM regenerated and reproducibility trade-off noted |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `pip-audit` fails to resolve | Old pins unavailable for your Python version | Audit the manifest only; do not install the set |
| Advisory list is empty | No NAT, so the lookup could not reach the index | Attach NAT, retry, record the environment |
| `cyclonedx-py` command not found | Package not installed in the venv | `pip install cyclonedx-bom` inside the venv |
| `npm audit` needs a lockfile | Lockfile absent | `npm install --package-lock-only --ignore-scripts` |
| `jq` errors on npm output | Audit wrote to stderr on failure | Redirect stderr as shown and inspect the file |
| Post-remediation audit still reports issues | A transitive package pins an old version | Record it; that is why the lockfile and CI gate matter |

## References

1. OWASP Top 10:2025 — A03 Software Supply Chain Failures. <https://owasp.org/Top10/2025/>
2. OWASP Vulnerable Dependency Management Cheat Sheet. Accessed 2026-10-29.
3. `pip-audit` documentation. <https://pypi.org/project/pip-audit/> Accessed 2026-10-29.
4. CycloneDX specification. <https://cyclonedx.org/> Accessed 2026-10-29.
5. NIST SP 800-218 — SSDF v1.1, especially PW.4 (reuse of well-secured software). Accessed 2026-10-29.

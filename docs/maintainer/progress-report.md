# Progress Report — Repository Audit and Course Development Plan

**Phase:** 0 (audit and planning) · **Date:** 28 October 2026
**Repository:** `nadeem-majeedch/CyberSecurity` (public, default branch `main`)
**Local workspace:** `CyberSecurityKali`
**Prepared by:** Course engineering (implementation agent) for Engr. Dr. Muhammad Nadeem Majeed

---

## 1. Executive summary

The audit found that the GitHub repository is **newly created and completely empty**: zero
commits, zero branches, no README, no documentation framework, no GitHub Actions workflow, and
GitHub Pages disabled. The local workspace contained no working copy and no `.git` directory —
only tool metadata.

Consequently there was **no existing architecture to preserve, no framework to avoid replacing,
and no user changes to protect**. Every claim below is verified against live API and Git output,
recorded in §2.

Phase 0 therefore delivered the missing foundation as documentation rather than code:
a full curriculum architecture (~482 guided hours across five levels plus capstone), authoring
templates, assessment design, a binding safety policy, a quality gate, and a documentation-site
architecture with an implementation checklist.

**No commit or push was performed.** Nothing was published. The working tree holds only new,
untracked planning documents, ready for the instructor's review.

**Recommendation:** approve the roadmap and safety policy, then execute Phase 0b (repository
governance) and Phase 1 (site scaffolding with CI and Pages) before any lesson authoring begins.

---

## 2. Audit method and evidence

| # | Check | Command / source | Result |
| --- | --- | --- | --- |
| A1 | Local working copy | `ls -la`, `git status` | Empty except `.freebuff/`; `fatal: not a git repository` |
| A2 | Local folder name | `pwd` | `/e/CyberSecurityKali` (differs from remote name `CyberSecurity`) |
| A3 | Remote reachability | `curl -o /dev/null -w %{http_code}` on repo URL | `200` — public and reachable |
| A4 | Remote refs | `git ls-remote` | No refs returned |
| A5 | Clone test | `git clone --depth 1` to temp dir | Succeeded with warning: "You appear to have cloned an empty repository" |
| A6 | Repository metadata | GitHub REST `/repos/...` | `size: 0`, `created_at 2026-10-28T15:57:46Z`, `pushed_at` identical, `default_branch: main`, `license: null`, `description: null`, `topics: []`, `private: false`, `fork: false`, `archived: false` |
| A7 | Commits | REST `/commits` | HTTP `409` — "Git Repository is empty" |
| A8 | Branches | REST `/branches` | `[]` |
| A9 | GitHub Pages | `has_pages` + REST `/pages` | `false`; Pages endpoint `404` |
| A10 | Actions workflows | REST `/actions/workflows` | Endpoint reachable (`200`), no workflows exist (empty repo) |
| A11 | Repository features | REST metadata | `has_issues: true`, `has_projects: true`, `has_wiki: true`, `has_discussions: false` |
| A12 | Local toolchain | `python --version`, `node`, `ruby`, `docker` | Python 3.12.10 + pip 26.2.2 present; Node, Ruby, Docker absent |
| A13 | Documentation framework | Clone + tree inspection | None. No `mkdocs.yml`, `_config.yml`, `docusaurus.config.*`, `hugo.toml`, `package.json` |
| A14 | Content inventory | Clone + tree inspection | 0 lessons, 0 labs, 0 assessments, 0 diagrams |

All remote checks were read-only. The clone was made into a temporary directory outside the
workspace and is not part of this repository.

---

## 3. Findings

| ID | Finding | Severity | Evidence | Status |
| --- | --- | --- | --- | --- |
| F-01 | Repository is empty — no commits, no branches, size 0 bytes | Informational | A5, A6, A7, A8 | Confirmed |
| F-02 | No documentation framework, static-site generator, or theme exists | Informational (no constraint) | A13 | Decision required — see §5 |
| F-03 | GitHub Pages not enabled; no deployment workflow | High | A9, A10 | Plan in Phase 1 |
| F-04 | No licence, description, or topics; repository is public but unattributed | Medium | A6 | Phase 0b |
| F-05 | No local Git repository existed before this audit; work was not version-controlled | Medium | A1 | `git init -b main` + `origin` remote configured by this phase; **0 commits** |
| F-06 | No `.gitignore`, no secret-scanning policy, no answer-key custody plan | High (before labs exist) | A1, A6 | Policy drafted in safety/architecture docs; files in Phase 0b |
| F-07 | No contribution, conduct, security-reporting, or issue/PR templates | Low | A6 | Phase 0b |
| F-08 | Discussions disabled; self-paced learners have no support channel | Low | A11 | Instructor decision (roadmap §16.2) |
| F-09 | No course content of any kind — coverage 0% against the proposed curriculum | Informational (starting point) | A14 | Addressed by roadmap |
| F-10 | No CI: no build check, link check, spell check, or secret scan | High | A10 | Phase 1 |
| F-11 | Local folder is `CyberSecurityKali` while the remote is `CyberSecurity` | Low | A2 | Keep remote name; treat Kali as one lab tool, not the course identity |
| F-12 | No accessibility or language policy | Low | A13 | Standards drafted; enforce in Phase 1 |
| F-13 | No stated legal/ethical framework for offensive content on a public site | High | A6 | Safety policy delivered this phase |

### Broken references, duplicated content, incomplete modules

- **Duplicated content:** none — no content exists. The roadmap adds a single-source-of-truth rule
  (§13 of the roadmap) and the quality checklist enforces cross-linking instead of copying.
- **Broken references:** none yet. Because a public docs site will accumulate hundreds of internal
  links, Phase 1 adds automated link checking so this stays true instead of being discovered later.
- **Incomplete modules:** all proposed modules are unwritten; this is expected at Phase 0.

---

## 4. Risk register

Likelihood/impact: H = high, M = medium, L = low. Owner: I = instructor, E = engineering.

| ID | Risk | L | I | Mitigation | Owner |
| --- | --- | --- | --- | --- | --- |
| R-01 | Public repo exposes answer keys, lab flags, or model solutions, undermining assessment integrity | H | H | Answer keys never enter this repository; private key store; public pages carry prompts only; PR review checklist blocks keys; CI secret scan | I + E |
| R-02 | Offensive material is used against third-party systems, creating legal exposure for learners and the university | M | H | Binding safety policy; localhost/lab-only mandate; authorization artefact template; explicit prohibited-action list; scenario-based ethics assessment in CYB-103 | I |
| R-03 | Live malware or real exploit payloads committed to a public repository | M | H | CYB-505 restricts to inert/synthetic/instructor-supplied samples; `.gitignore` and CI pattern blocks; distribution policy in safety policy §7 | I + E |
| R-04 | Legal exposure in Pakistan (PECA 2016) and internationally for students following instructions out of context | M | H | Jurisdiction section, "authorization first" gate in every lab, disclaimer, instructor legal review before Level 2 publication; Level 2 labs bind every capture and scan to `192.0.2.0/24` or loopback | M |
| R-05 | Tool and version drift (rolling distributions) makes labs unreproducible | H | M | Pin versions, date-stamp every lab, `last_reviewed` front matter, quarterly review cadence, snapshot-based labs | E |
| R-06 | Scope is enormous (~480 h, 46 modules) and stalls incomplete | H | H | Level-by-level release gates (M2–M6); each level independently useful; no level published until its labs are verified | I |
| R-07 | Single-maintainer bottleneck; content becomes unmaintainable | M | M | Templates, component library, contributor guide, review checklist, defined owners per level | I + E |
| R-08 | Broken links, broken builds, and dead commands erode trust | H | M | CI: `mkdocs build --strict`, link check, markdown lint, codespell; lab verification recorded in front matter | E |
| R-09 | Third-party lab applications, screenshots, and diagrams used without licence compliance | M | M | Attribution table, licence audit before embedding, prefer permissively licensed labs (for example OWASP Juice Shop, MIT) | E |
| R-10 | Cloud labs incur unexpected cost or touch another party's account | M | H | LocalStack/emulated or instructor-provided sandbox accounts, hard budget caps, teardown checklists, no shared credentials | I |
| R-11 | Site build depends on a toolchain the instructor cannot run locally | M | L | Chosen stack builds on Python, which is present locally; CI builds on GitHub regardless of local setup | E |
| R-12 | Accessibility failures (colour-only meaning, unlabelled diagrams, dense tables) exclude learners | M | M | Accessibility rules in the quality checklist, enforced at review; text alternatives for every diagram | E |

---

## 5. Framework decision

No framework existed, so this is a greenfield choice constrained by: (a) a documentation-heavy
course with code, callouts, tabs, and diagrams; (b) GitHub Pages hosting; (c) a maintainer
environment with Python but no Node or Ruby (evidence A12); (d) zero server-side logic.

**Decision: MkDocs with the Material theme, built and deployed by GitHub Actions to GitHub Pages.**

| Criterion | MkDocs Material | Jekyll (Just the Docs) | Docusaurus | Hugo |
| --- | --- | --- | --- | --- |
| Local toolchain available today | Yes (Python 3.12) | No (Ruby absent) | No (Node absent) | No (Go absent) |
| Search, callouts, tabs, math, diagrams | Built in / first-class | Partial, plugin-dependent | Excellent | Good, theme-dependent |
| Build cost for hundreds of pages | Fast | Slower on Pages | Slower, heavier | Fastest |
| Maintenance burden for non-frontend maintainer | Low (one YAML file) | Low | Medium | Medium |
| Course-friendly authoring (admonitions, snippets, tabbed OS instructions) | Excellent | Weak | Good | Good |
| Migration cost if requirements change | Low (plain Markdown) | Low | Medium (MDX) | Low |

Full architecture, directory tree, navigation, CI design, and rollback plan:
[site-architecture.md](site-architecture.md).

Fallback if the instructor prefers zero build configuration: GitHub's native Jekyll with the
Just the Docs theme, accepting weaker callouts and tabbed instructions. This is a documented
trade-off, not an oversight.

---

## 6. Deliverables produced in Phase 0

| Deliverable | File | Status |
| --- | --- | --- |
| Repository audit and risk register | this document | Complete |
| Course roadmap (levels, 46 modules, hours, capstone, coverage map, gates) | [roadmap.md](../curriculum/roadmap.md) | Complete |
| Documentation-site architecture and directory tree | [site-architecture.md](site-architecture.md) | Complete |
| Lesson template | [lesson-template.md](lesson-template.md) | Complete |
| Practical-lab template | [lab-template.md](lab-template.md) | Complete |
| Assessment format, rubrics, integrity policy | [assessment-format.md](../policies/assessment-format.md) | Complete |
| Safety policy (authorized targets, prohibited actions, legal) | [safety-policy.md](../policies/safety-policy.md) | Complete |
| Content-quality checklist and definition of done | [quality-checklist.md](quality-checklist.md) | Complete |
| Course landing page | [index.md](../index.md) | Complete |
| Repository README | [README.md](https://github.com/nadeem-majeedch/CyberSecurity/blob/main/README.md) | Complete |
| Level 1 course content (15 modules, 11 labs, review questions, knowledge checks) | [levels/](../levels/level-1.md) | Complete |
| Documentation site (framework, navigation, student guides, glossary) | [mkdocs.yml] / [maintainer/](index.md) | Complete except CI and publishing |

No lessons, labs, assets, configuration files, workflows, or dependencies were created in this
phase, by design.

---

## 7. Implementation phases and checklist

Legend: `[x]` complete · `[ ]` pending · `[~]` partially complete.

### Phase 0a — Audit and planning (this phase)
- [x] Audit remote repository state, branches, commits, Pages, Actions, features
- [x] Audit local workspace and toolchain
- [x] Confirm absence of framework, content, CI, and licence
- [x] Define curriculum architecture and module catalogue
- [x] Define lesson, lab, assessment, and quality standards
- [x] Define safety policy
- [x] Define documentation-site architecture and directory tree
- [x] Record risks and open decisions
- [x] Confirm no commit or push performed

### Phase 0b — Repository governance (½ day)
- [ ] Instructor review and approval of roadmap, safety policy, and assessment rules
- [ ] Choose licences: content licence and code licence
- [ ] Set repository description and topics
- [ ] Add `LICENSE`, `.gitignore`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md`
- [ ] Add issue and pull-request templates
- [ ] Enable branch protection on `main` (require review, block force-push)
- [ ] First commit of Phase 0 documents (on instructor instruction only)
- **Done when:** repository has a licence, contribution rules, protection, and one reviewed commit.

### Phase 1 — Site foundation (partially complete)
- [x] Add `mkdocs.yml` with Material theme, navigation, search, and metadata
- [x] Add `requirements-docs.txt` with pinned versions
- [x] Add the student/maintainer structure and navigation, expanded as each level was published
- [x] Local `mkdocs build --strict` passes with zero warnings
- [ ] Add `.github/workflows/docs.yml` (build, checks, deploy to Pages)
- [ ] Enable Pages with "GitHub Actions" as the source
- [ ] Add CI checks beyond the build: link check, markdown lint, codespell, secret scan
- [ ] Add front-matter validation script and schema
- **Done when:** every push to `main` builds, checks, and deploys; a broken link fails CI.

### Phase 2 — Level 1 content (~55 h authoring) — complete
- [x] CYB-101 to CYB-115 lessons published (fifteen modules, expanded from the original eight to cover
      the additional beginner outcomes: addressing and protocols split from networking models, Kali, applied
      cryptography, credential and phishing security, and log-based troubleshooting)
- [x] Eleven labs with scope, expected output, verification, teardown and rubrics
- [x] Review questions and knowledge checks in every module
- [ ] Lab verification log for each lab on a clean VM set — **outstanding**, and the main acceptance gap
- [ ] Level 1 readiness assessment brief, marking guide held privately — **outstanding**
- **Done when:** a learner with no prior knowledge can complete Level 1 unaided.

### Phase 3 — Level 2 (~90 h) — complete except verification
- [x] Six modules published (CYB-201 to CYB-206): lab environment and Kali, Bash/Python/Git, host discovery and
      enumeration, packet capture and analysis, OpenSSH, and host inspection with an assessment report
- [x] Eighteen labs, each with scenario, topology, numbered commands, expected observations, verification,
      troubleshooting, teardown and extension questions
- [x] Professional assessment report template published under Policies
- [ ] CYB-207 (vulnerability assessment) and CYB-208 (instrumenting the lab for defence) — **deferred** to
      Levels 3 and 4, where the vulnerable targets and log sources they need are built
- [ ] Lab verification log on a clean VM pair — **outstanding**, as with Level 1
- **Done when:** each lab is replayable by a second reviewer from the written steps alone.

**Module boundaries changed during authoring.** The original plan had nine modules, with evidence discipline,
command line, Python and service protocols as separate units. Delivered as six, because each module now ends with
a single inspectable deliverable: a validated lab, three scripts, an enumeration record, a capture set, a hardened
host, and an assessment report. The regrouping is recorded in the roadmap's delivery note.

### Phase 4 — Level 3 — six of eight modules published
- [x] CYB-301 web architecture and HTTP — three labs (lab build and isolation, interception, cookie and session
      attributes)
- [x] CYB-302 injection and XSS — two labs, each with a fix artefact and regression tests
- [x] CYB-303 access control, authentication and sessions — three labs (login workflow, IDOR/BFLA, CSRF)
- [x] CYB-304 file handling, SSRF and misconfiguration — four labs (upload, traversal, SSRF, headers/TLS)
- [x] CYB-307 secure coding, dependencies and remediation — three labs (threat model and review, dependency
      audit and SBOM, fix-and-verify with tests that fail on the vulnerable version)
- [x] CYB-308 API security — two labs (BOLA/BFLA/property exposure, mass assignment and rate limiting)
- [x] Seventeen labs with scenario, objectives, tool versions, topology, numbered commands, option explanations,
      expected observations, verification, troubleshooting, teardown, reflection questions and rubric
- [x] Versions verified against primary sources on 29 October 2026: OWASP Top 10:**2025**, ASVS 5.0.0, WSTG
      v4.2 (stable; v5.0 in development), Juice Shop 20.3.0, DVWA via its own Compose file, Burp Suite Community
      2026.10.1, OWASP ZAP 2.17.0
- [ ] CYB-305 applied cryptography — **not written**
- [ ] CYB-306 identity and federation — **not written**
- [ ] CYB-309 level assessment — **not written**
- [ ] Lab verification on a real VM pair — **outstanding**, as with Levels 1 and 2
- **Done when:** every vulnerability demonstration is reproducible and has a paired fix.

**Module boundaries changed during authoring.** The plan had nine modules. Delivered as six, plus the three
outstanding: SSRF and misconfiguration were folded into the file-handling module (they share the low-privilege
precondition and need a request-forgery topology rather than a second code module), and dependency work was folded
into secure coding so that the module ends with a remediation table instead of a scanner report. Codes were not
renumbered, so 305 and 306 remain visible gaps rather than being quietly reused.

**Two deliberate scope decisions.** First, every lab that demonstrates a vulnerability also requires its fix and,
in CYB-302, CYB-303, CYB-304 and CYB-307, tests that fail on the vulnerable version. Second, SSRF is taught
exclusively against a loopback service the learner starts; cloud metadata addresses are named as out of scope in
the lab's warning block, because that is the one exercise in the course that could reach a real control plane.

**Format reconciliation.** The Level 2 review found that labs had drifted between two heading sets. All seventeen
Level 3 labs were written against the supplied format in one pass — scenario, objectives, tools and versions,
setup, topology, numbered commands, option explanations, expected observations, verification criteria,
troubleshooting, cleanup, questions — so no normalisation pass was needed afterwards.

### Phase 5 — Level 4 — seven modules and 22 labs published
- [x] CYB-401 SOC operations, ATT&CK and threat intelligence — three labs (alert triage, ATT&CK mapping, CTI brief)
- [x] CYB-402 endpoint telemetry — three labs (Windows event log triage, Linux authentication logs, Sysmon process
      sequence with an encoded-PowerShell chain and a written detection)
- [x] CYB-403 hardening and vulnerability management — three labs (OpenSCAP against a CIS Level 1 profile,
      six verifiable Windows controls, KEV/EPSS prioritisation with a patch plan and exceptions)
- [x] CYB-404 detection engineering and SIEM — three labs (Wazuh 4.14.9 single-node deployment, Sigma rule with
      four tests, correlation with clock-skew and ordering failures)
- [x] CYB-405 network defence — three labs (nftables segmentation with a verification matrix and a bypass to close,
      Suricata rule plus a placement null-test, synthetic DNS capture analysed for tunnelling and DGA)
- [x] CYB-406 digital forensics — three labs (evidence register and verified acquisition, Sleuth Kit triage and UTC
      timeline, YARA with a negative test plus Volatility plugin mapping)
- [x] CYB-407 incident response — four labs (phishing triage and scope, master timeline with a seven-minute clock
      skew, simulated ransomware contain-and-recover, incident report with a four-inject tabletop)
- [x] 36 pages, 22 labs, 68 labs across the course; every lab has scope, expected output, verification, teardown
      and a rubric
- [x] Versions verified against primary sources on 29 October 2026 (OpenSCAP 1.4.6, SSG 0.1.82, Lynis 3.1.7,
      Wazuh 4.14.9, Suricata 8.0.7, Zeek 9.0.1 LTS, YARA 4.6.0, Sysmon 15.22, Autopsy 4.23.1, NIST SP 800-61 Rev 3,
      ATT&CK v20.0, EPSS v5, and the 15 April 2026 NVD enrichment change)
- [ ] CYB-410 level assessment — **not written**; module rubrics stand in
- [ ] Runtime verification on a real VM set — **outstanding** for every lab except the three executed below
- **Done when:** detections fire on scripted activity and the IR exercise produces a defensible report.

**What was actually executed.** Three artefacts were run rather than written to spec: the LAB-403-03 scoring
script against the synthetic scan export (its output contradicted the first draft's expected tiers, and the model
and prose were corrected); the LAB-404-03 event generator in both orders (the reversed mode initially produced
inconsistent timestamps and was rebuilt); and the LAB-405-03 DNS generator and analysis (a Scapy capture of 270
queries, which exposed a grouping error that hid the DGA cluster). Everything else is written to specification.
This is stated here because "published" means the text exists, not that a reviewer has replayed it.

**Scope changes.** Ten planned modules became seven: Linux and Windows hardening merged (same measure–change–verify
loop), logging and detection split (telemetry failure and rule failure are different problems), and threat
intelligence folded into CYB-401 as its third lab. The level assessment was not written and is listed as a gap
rather than renumbered away.

### Phase 6 — Level 5 — six of eight modules published, 18 labs
- [x] CYB-501 penetration testing — three labs (engagement package, authorized assessment of a lab target,
      escalation with report and retest)
- [x] CYB-502 Active Directory — three labs (build an isolated `lab.local` forest, BloodHound and PingCastle audit,
      detection and hardening with a recovery runbook)
- [x] CYB-503 cloud security — three labs (MinIO least privilege and anonymous-bucket closure, Checkov against
      deliberately unsafe Terraform plus a synthetic CloudTrail extract, container hardening)
- [x] CYB-504 malware analysis — three labs (static triage of a signed binary plus synthetic artifacts, sandbox
      behaviour with a self-authored probe, YARA with a negative corpus)
- [x] CYB-505 security automation — three labs (parse and normalise three log formats, offline enrichment and
      scanner-report merge, guarded containment against a mock API)
- [x] CYB-506 threat hunting — three labs (beacon hunt with interval analysis, coverage audit, validation and tuning)
- [x] 86 labs across the course; every lab has scope, verification, teardown and a rubric
- [x] No cloud account is required anywhere: LocalStack was replaced with MinIO after it began requiring a token
- [ ] CYB-507 professional reporting — **not written**
- [ ] CYB-508 capstone brief and rubric — **outlined only**
- [ ] Level 5 assessment — **not written**; module rubrics stand in
- **Done when:** each lab carries an explicit scope statement and a teardown/reset path — met for all 18.

**What was actually executed.** Six artefacts were run rather than written to specification, and three of them
changed the page:

- **LAB-505-01 parser.** 62 input lines across three formats produced 13 normalised events and 3 skipped lines, with
  7 pytest cases passing. The first draft's skip counting reported line numbers one too low for the CSV source and was
  corrected.
- **LAB-505-02 enrichment and merge.** Enrichment produced 10 IOC hits from 13 events; the scanner merge reduced 6
  findings to 4 with correct tier promotion for a KEV entry that carried `unknown` severity.
- **LAB-505-03 containment.** All five exit paths were exercised against a loopback mock API: dry run `0`, missing
  token `2`, wrong scale `3`, authentication failure `4`, and partial failure `1` after bounded retries on 500s.
- **LAB-506-01 generator and analysis.** 36 beacon connections at mean 300 s with CV 0.019, next to a benign backup at
  CV 0.000. This is the lab's central lesson, and the numbers are measured, not asserted.
- **LAB-506-02 coverage audit.** 18 rules over 16 techniques: 8 evidenced present, 7 partial, 3 absent, with 7 declared
  statuses overclaimed.
- **LAB-506-03 tuning.** Precision 0.27 → 1.00 at the cost of recall 1.00 → 0.62, losing certutil, schtasks and wmic —
  the LOLBin population. Also measured, and the reason the lab forbids deploying that tuning.

**Not executed:** the MinIO, Checkov, Trivy, BloodHound, PingCastle, capa and YARA walkthroughs, and every VM step in
CYB-501/502/504. Those pages specify expected patterns rather than verified transcripts.

**Scope changes.** Three are recorded in the roadmap: advanced tracks renumbered so hunting comes last, cloud moved off
LocalStack, and the level now ends without its reporting module or capstone brief.

### Phase 7 — Assessments, answer keys and capstones — complete (30 October 2026)
- [x] Module quiz bank: 200 items (5 per module across all 40 published modules), each with a scenario or
      troubleshooting twist rather than recall-only questions
- [x] Five integrated level assessments (70% practical, 30% written justification) and five answer keys with
      acceptable-reasoning criteria and model answers
- [x] Six capstone briefs, 100 marks each, with problem statement, scope, tasks, artefacts, validation, ethics,
      submission checklist, rubric, extensions, pitfalls, starter data and reference solution
- [x] Synthetic datasets for the three data-driven briefs, with SHA-256 manifests
- [x] Reference solutions executed rather than asserted; outputs recorded below
- [x] Policy v2.0: answer keys published on separate pages, with an attempt-first protocol
- **Done when:** a learner with no instructor can attempt, mark and improve their own work. Met.

**Verification performed (30 October 2026, Python 3.12.10, PyYAML 6.0.3):**

- **SOC dataset:** 26 events, 4 hosts, one clock offset (+420 s on FS-01), 12 flagged behaviours, 4 DNS TXT
  queries at exactly 300 s intervals. The reference script regenerates the corrected timeline.
- **Detection corpus:** 43 events, 7 labelled malicious, 4 Sigma rules, measured **TP 7, FP 2, FN 0, precision
  0.78, recall 1.00**. The two false positives are benign administrative actions, not rule defects; the page says
  so rather than tuning them away.
- **Automation corpus:** 30 lines → **27 normalised** (9 syslog, 8 CSV, 10 JSON), **3 skipped** with line numbers
  and reasons, **8 aggregated findings**, exit 0. A path bug found during review — findings named the source host
  instead of the matched domain — was fixed before publication.
- **Assessment pages:** all five quiz/key/assessment triples built and cross-linked; every level key totals its
  stated marks (30, 30, 30, 30, 30 written components).
- **Not executed:** the network-assessment, web-application and hardening briefs describe lab work whose results
  depend on the learner's build, so their reference sections state expected shapes and commands, not transcripts.

**Remaining gaps:** CYB-507 (professional reporting) is still unwritten; two Level 3 modules remain planned; no
redacted exemplar report exists yet; the new rubrics have not been second-marked by a human reviewer.

### Phase 8 — Launch and maintenance
- [ ] Accessibility pass (alt text, contrast, heading order, colour-independent meaning)
- [ ] Link and secret scan clean; legal review of offensive content
- [ ] Publish release notes and version tag
- [ ] Establish quarterly review cadence and issue triage policy
- **Done when:** site is public, checks are green, and a maintenance owner is named.

---

## 8. What was deliberately not done

- No lesson, lab, quiz, or assessment content was written (Phase 0 position; superseded by Phases 2–7).
- No `mkdocs.yml`, workflow, theme, or dependency was installed — Phase 1 must be reviewable as a
  single coherent change.
- No commit, push, tag, release, or Pages deployment was made.
- No licence was chosen on the instructor's behalf.
- No third-party lab application was downloaded, and no external service was integrated.
- No attempt was made to "improve" the empty repository by inventing existing state.

---

## 9. Recommended next actions

1. **Instructor review (blocking):** approve or amend the roadmap (§5–§10), the safety policy, and
   the assessment weighting in [assessment-format.md](../policies/assessment-format.md).
2. **Settle the six open decisions** listed in roadmap §16 — licence, credentialing, answer-key
   custody, support channel, external platforms, language.
3. **Execute Phase 0b**, then commit the planning baseline as the repository's first commit.
4. **Execute Phase 1** and publish a live skeleton site before authoring Level 1, so the authoring
   workflow is proven on a page rather than on forty modules.
5. **Pilot one Level 1 module end-to-end** (CYB-102) with two test learners before scaling, and
   use their confusion points to refine the templates.
6. **Arrange legal review** of the offensive-content sections prior to Level 2 publication.

---

## Appendix — Audit commands used

Read-only unless noted. The temporary clone lived outside the workspace and was removed.

```bash
pwd && ls -la && git status --short && git branch --show-current      # local state
git --version && git ls-remote <repo-url>                             # remote refs
curl -s -o /dev/null -w "%{http_code}" <repo-url>                    # reachability
git clone --depth 1 <repo-url> /tmp/cs_probe                          # emptiness test
curl -s https://api.github.com/repos/nadeem-majeedch/CyberSecurity   # metadata
curl -s https://api.github.com/repos/.../commits                     # 409 empty
curl -s https://api.github.com/repos/.../branches                    # []
curl -s https://api.github.com/repos/.../pages                       # 404
for c in python pip node npm ruby docker; do command -v $c; done      # toolchain
# then, workspace only:
git init -b main .                                                    # local repo created
git remote add origin <repo-url>                                     # remote linked
```

State after this phase: branch `main`, remote `origin` configured, **zero commits**, and the
Phase 0 documents present as untracked files.

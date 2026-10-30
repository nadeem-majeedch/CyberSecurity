---
title: "Final Quality Audit — 30 October 2026"
description: "Repository-wide audit of content, build, safety and GitHub Pages readiness, with the commands run, the results obtained and the issues that remain open."
module_code: MNT-AUDIT
level: 0
kind: maintainer
prerequisites: []
estimated_minutes: 20
difficulty: maintainer
safety: none
lab_ids: []
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [audit, quality, build, safety, github-pages]
---

# Final Quality Audit — 30 October 2026

This page records an audit of the repository **as it exists on disk**, not of what earlier reports claim.
Every count below was produced by a command in §3; nothing is carried over from a progress note. Where a
check could not be performed, §6 says so instead of assuming the answer.

**Verdict: PASS WITH WARNINGS.** The course is coherent, safe, internally consistent and builds cleanly, and
it is deployable to GitHub Pages without configuration changes beyond enabling Pages. It is not *complete*:
six planned modules are unwritten, six Level 5 walkthroughs were never executed, no CI workflow exists, and no
licence has been chosen. None of those is a correctness defect in what is published, and all of them are
disclosed to learners rather than hidden.

---

## 1. Scope reviewed

| Area | What was inspected |
| --- | --- |
| Content | All 222 course pages plus this report (223 files): 40 module pages, 41 lessons, 86 labs, 16 assessment pages, 9 project pages, guides, policies, glossary, instructor page |
| Structure | Level sequence, prerequisite chain, navigation (`mkdocs.yml`), placeholder markers, empty code blocks, missing assets |
| Technical | `mkdocs.yml`, `requirements-docs.txt`, `.gitignore`, build warnings, links and anchors, code-fence syntax, search index, tables and mobile layout |
| Safety | Lab targets, service exposure, malware artefacts, credentials, authorization language, disclosure of unverified work |
| Deployment | Existing workflow, Pages compatibility, base URL, dependency pinning |

Not reviewed: rendered appearance in a browser at multiple viewports (checked only through built CSS and
HTTP responses), the correctness of every one of the ~1,700 individual commands, and any environment that
was not available locally (see §6).

---

## 2. What actually exists

| Item | Count | Basis |
| --- | --- | --- |
| Markdown pages | 223 | `glob("docs/**/*.md")` — 222 course pages plus this audit |
| Published modules | 40 | module `index.md` files under `docs/levels/level-*/` |
| Lessons | 41 | non-lab pages inside module directories |
| Labs | 86 | `lab-*.md` pages: 11 / 18 / 17 / 22 / 18 for Levels 1–5 |
| Assessment pages | 16 | index, five quizzes, five keys, five level assessments |
| Capstone projects | 6 briefs | plus index, starter-file index, reference solutions |
| Quiz items | 200 | 75 + 30 + 30 + 35 + 30 |
| Python fences | 61 | all compile (§3) |
| Bash fences | 784 | 779 parse; 5 contain `<PLACEHOLDER>` tokens |
| PowerShell fences | 87 | **not** syntax-checked — no PowerShell host available |
| Words of prose | ~346,000 | `wc -w` over all Markdown |

Coverage against the plan is uneven and stated as such on every affected page:

- **Level 1** 15/15 modules, 11 labs. **Level 4** 7/7 modules, 22 labs. These are complete.
- **Levels 2, 3 and 5** have six of eight modules each. CYB-207 and CYB-208 (vulnerability assessment,
  lab instrumentation), CYB-305 and CYB-306 (applied cryptography, identity and federation), and CYB-507
  (professional reporting) have no pages. CYB-508 exists only as capstone briefs, which are published under
  **Projects**.
- The missing modules are named in the [roadmap](../curriculum/roadmap.md) and level overviews. No unwritten
  module has a stub page, so nothing in the navigation looks available before it is.

---

## 3. Commands executed and their actual results

All commands were run in the repository root with the project virtual environment.

| # | Command | Result |
| --- | --- | --- |
| 1 | `python -m mkdocs build --strict` | **exit 0**, 223 pages, 6.2 s, zero warnings other than the vendor's Material end-of-life notice |
| 2 | `python tmp/audit.py` (content inventory) | 40 modules, 41 lessons, 86 labs; 0 placeholder markers (`TODO`, `TBD`, `coming soon`, `lorem`); 0 missing images; 0 empty code blocks; 0 unclosed fences |
| 3 | `python tmp/code_check.py` (fenced-code syntax) | 0 Python blocks fail to compile; 5 bash blocks fail `bash -n`, all because of intentional `<HANDLE>`, `<INODE_OF_…>` and `<repo-url>` placeholders |
| 4 | `python tmp/review.py` (links and anchors) | **0 broken links and 0 broken anchors** after the fix in §4; 4 before it, all in the lesson template |
| 5 | `python tmp/structure_check.py` (rubrics, keys, prereqs) | all six capstone rubrics total **100**; quiz/key parity exact at 75/30/30/35/30; one prerequisite pointing at a non-existent module (fixed); heading-order anomalies only in the two templates |
| 6 | Secret-pattern scan (`AKIA…`, `ghp_…`, `sk-…`, `BEGIN … PRIVATE KEY`, `api_key=`, `password=`) | 0 real credentials. Two intentional lab values: a `labadmin-local-only` MinIO password for a loopback container, and AWS's published `AKIAIOSFODNN7EXAMPLE` placeholder that the lab then redacts |
| 7 | Offensive-target scan | 0 instances of `nmap`, `masscan`, `nikto`, `sqlmap`, `hydra`, `ffuf`, `gobuster` or Metasploit aimed at anything outside `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, `10.10.10.0/24`, `10.20.20.0/24` or loopback |
| 8 | HTTP check against the local build, 8 routes | 200 for home, Start Here, Levels, Level 2, Level 5, Curriculum, Assessments, Projects, Instructor, and the edited lab pages |
| 9 | Search-index inspection | 3,624 indexed sections; a query for "privilege escalation" matches 30 sections across levels, keys and labs |
| 10 | `git status`, `git log` | branch `main`, **zero commits**; every file untracked. Nothing was committed, pushed or published during this audit |

### Findings per audit area

**A. Content.** Levels progress from foundations (network layers, Linux, Windows) through tooling, then
applications and defence, then advanced practice; Level 2 assumes Level 1's virtualisation and CLI work, Level 3
supplies the HTTP and identity model Level 4 reads logs against, and Level 5 assumes both. 13 labs stated their
prerequisites only in front matter — fixed in §4. Defensive labs use synthetic datasets with stated properties
(26 events, four hosts, one clock offset; 43 detection events; 30 log lines) rather than vague "a log file".
All six capstone briefs carry problem, outcomes, scope, setup, tasks, artefacts, validation, ethics, checklist,
100-mark rubric, extensions and pitfalls.

**B. Technical.** Framework: MkDocs 1.6.1 with Material 9.8.0, pinned in `requirements-docs.txt`; navigation
lists all 222 pages; strict mode is enabled in `mkdocs.yml`; search plugin active; tables scroll horizontally on
narrow screens (`overflow:auto` in the built CSS); no page depends on colour alone for meaning; there are **no
images at all**, so there is no missing-asset or alt-text debt — and also no diagrams.

**C. Pages readiness.** No `.github/workflows/` directory exists, so there is no workflow to be incompatible
with. The deployment recipe in the [authoring guide](authoring-guide.md#7-deployment) is correct for Pages via
Actions (OIDC permissions, `upload-pages-artifact`, `deploy-pages`, `configure-pages`). Two build-side gaps were
closed (§4): `site_url` was unset, which produced an **empty `sitemap.xml`** and no canonical links.

**D. Safety.** Every practical exercise targets a lab the learner builds, a deliberately vulnerable local
application, loopback, or synthetic data. Public addresses appear only as resolvers for `dig` demonstrations
(`8.8.8.8`) and as documentation ranges elsewhere. No live malware is distributed or requested; malware work
uses inert artefacts, generated corpora and sandboxed observation. Vulnerable services are bound to specific
lab addresses rather than `0.0.0.0`, and the pages explain why. Legal and ethical guidance is present in the
README, the safety policy, every level overview and every offensive lab's scope block.

---

## 4. Problems found and fixed in this audit

| # | Problem | Fix |
| --- | --- | --- |
| 1 | **13 labs** carried prerequisites only in front matter, invisible to the reader | Added an explicit *Prerequisites* section to each, naming the module, the earlier labs and the environment |
| 2 | `site_url` unset → **empty `sitemap.xml`**, no canonical links | Set `site_url` to the project URL GitHub Pages assigns; sitemap now lists 222 URLs and canonical tags are absolute |
| 3 | CYB-505 listed **CYB-210** as a prerequisite; no such module exists | Changed to CYB-202 (Bash/Python/Git), which is where the scripting comes from |
| 4 | Four dead links in the lesson template (`lab-01-subnetting.md`, `../labs/lab-environment.md`, `#socket`) | Replaced with non-link paths or corrected targets; link scan is now clean |
| 5 | Six Level 5 walkthroughs (MinIO, Checkov, Trivy, capa, YARA, BloodHound/PingCastle) presented expected output with no statement that it was never executed | Added a *How this walkthrough was produced* note to each: output is a shape, not a transcript |
| 11 | README page count would have gone stale the moment this report was added | README updated to 223 in the same pass |
| 6 | Roadmap principle 8 said "**No answer keys**"; maintainer index said keys never belong in the repository | Both now state that keys are published deliberately and secrets never are, matching the assessment policy |
| 7 | Roadmap open decision asked where answer keys should be kept | Replaced with the still-open question: a **closed-book variant bank** for proctored cohorts |
| 8 | One lesson still said "Answers are not published" | Reworded to point at the module quiz and its published key |
| 9 | Authoring checklist said "No answer keys…" with no distinction | Reworded to distinguish lesson blocks from assessment files |
| 10 | Workflow recipe omitted `actions/configure-pages` | Added, so the Pages base URL is configured before upload |

Each fix was followed by re-running the affected check: the strict build (exit 0), the link/anchor scan
(0 problems) and an HTTP request for the edited pages (200, with the new sections present in the HTML).

---

## 5. Deliberate characteristics, not defects

- **Level 1 labs use a leaner heading set** (*Objective, Procedure, Evidence, Teardown, Reflection*) than
  Levels 2–5 (*Scenario, Numbered commands, Cleanup, Questions*). Scope, expected output, verification,
  troubleshooting and cleanup are present in both; renaming headings across 86 labs would be churn.
- **Inline lesson questions are not individually keyed.** The 200 keyed items cover the same ground, and the
  lesson pages say so.
- **Five bash blocks contain `<PLACEHOLDER>` tokens**, so `bash -n` rejects them. They are instructions to
  substitute a value, not runnable transcripts.
- **The two maintainer templates contain a second H1** in their worked examples. It is example content inside
  a fence, and it renders correctly.
- **No images or diagrams anywhere.** The Mermaid fence is configured but unused.

---

## 6. Outstanding issues and checks that could not be performed

| Issue | Severity | Status |
| --- | --- | --- |
| Six planned modules unwritten (CYB-207, 208, 305, 306, 507, 508) | High for completeness | Disclosed on every level page and in the roadmap; no stubs |
| No CI workflow; Pages not enabled | High for publication | Recipe documented, not committed; enabling requires the instructor's decision |
| Six Level 5 tool walkthroughs never executed by the author | Medium | Now disclosed per page; learners are told to treat output as a shape |
| All VM-based labs unverified (hypervisor, AD forest, SIEM stack) | Medium | Inherent: they depend on the learner's environment; pages give expected patterns and verification criteria |
| No licence chosen | Medium | README states "all rights reserved until a licence is chosen" |
| PowerShell blocks not syntax-checked | Low | No PowerShell host on the audit machine; 87 fences reviewed by reading only |
| Commands not executed against real tools (Nmap, Wireshark, Wazuh, Autopsy, Volatility) | Medium | Syntax reviewed; behaviour depends on pinned versions and is stated per lab |
| Rendered appearance at mobile widths | Low | Verified through CSS rules and table overflow behaviour, not a device screenshot |

---

## 7. Verdict

**PASS WITH WARNINGS.**

What is verified: the site builds strictly with zero warnings; every internal link and anchor resolves; all
223 pages are reachable from the navigation; the counts quoted in the README, home page, level pages and
roadmap match the tree; all 200 quiz items have matching key entries; every capstone rubric totals 100; no
real secret, live malware or unauthorized target appears anywhere; and the honesty statements about what is
and is not finished are consistent across the student pages, the roadmap and the progress report.

What prevents a clean PASS: the course is not finished (six modules), it has never been built by CI, Pages is
not enabled, and a meaningful part of the Level 5 walkthroughs has never been executed. Those are known,
stated and bounded — which is why this is a pass with warnings rather than a failure.

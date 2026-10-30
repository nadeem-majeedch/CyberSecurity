# Documentation Site Architecture

**Purpose:** define the documentation framework, repository structure, navigation, build pipeline,
and authoring workflow for the public GitHub Pages course site.
**Status:** decided (Phase 0) · **Implementation:** Phase 1 · **Date:** 28 October 2026

---

## 1. Requirements the architecture must satisfy

| ID | Requirement | Driven by |
| --- | --- | --- |
| RQ-1 | Hundreds of Markdown pages with per-page navigation and full-text search | Course scale (42 modules) |
| RQ-2 | Rich instructional components: callouts, tabbed OS-specific commands, code with copy button, diagrams, math | Lab-heavy content |
| RQ-3 | Zero server-side logic; fully static output | GitHub Pages |
| RQ-4 | Buildable by a maintainer with Python available and no Node/Ruby toolchain | Local environment audit |
| RQ-5 | Automated failure on broken internal links, broken build, leaked secrets | Public trust and integrity |
| RQ-6 | Learner-facing progress affordances without a backend | Self-paced study |
| RQ-7 | Versioned content, so lab instructions match the tool version they were written for | Tool drift |
| RQ-8 | Contribution by non-frontend authors (instructor, teaching assistants) | Maintainability |

---

## 2. Chosen stack

| Layer | Choice | Why |
| --- | --- | --- |
| Generator | **MkDocs** (Python) | Markdown-native, single YAML config, fast builds, satisfies RQ-1/RQ-4 |
| Theme | **Material for MkDocs** | Search, admonitions, content tabs, code annotations, diagrams, keyboard navigation out of the box (RQ-2) |
| Hosting | **GitHub Pages**, deployed from Actions | Free, matches repository, no external service (RQ-3) |
| Build environment | Pinned Python + `requirements-docs.txt` | Reproducible builds (RQ-7) |
| Diagram source | Mermaid in Markdown; SVG assets for complex figures | Text-based, diffable, theme-aware |
| Quality gate | `mkdocs build --strict`, `lychee` link check, `markdownlint-cli2`, `codespell`, `gitleaks` | Satisfies RQ-5 |
| Versioning | Git tags; optional `mike` for parallel versioned docs | RQ-7 |

Deliberately **not** used: any CMS, database, analytics that profile learners, third-party comment
platform, or JavaScript framework. The site stays static, private by default, and dependency-light.

**Recorded trade-off:** MkDocs requires a CI build step, unlike native Jekyll. This buys stronger
instructional components (tabs and callouts are used in nearly every lab) and a toolchain that
already exists on the instructor's machine. If the build step ever becomes a burden, the fallback
is Jekyll + Just the Docs, and plain-Markdown content migrates with minor link fixes.

---

## 3. Repository structure

The structure below is the one in place. Module folders are created level by level as content is
authored, so the repository never contains empty directories pretending to be finished modules.

```
CyberSecurity/
├── README.md                        # student-facing course introduction (entry point)
├── .gitignore                       # build output, lab artefacts, secrets
├── mkdocs.yml                       # site configuration and navigation
├── requirements-docs.txt            # pinned build dependencies
├── LICENSE, CONTRIBUTING.md, SECURITY.md          # Phase 0b
│
├── .github/workflows/               # Phase 1
│   ├── docs.yml                     # build + checks + deploy to Pages
│   └── content-checks.yml           # pull-request gate
├── scripts/                         # Phase 1
│   ├── check_front_matter.py
│   └── check_lab_safety.py
│
├── docs/
│   ├── index.md                     # homepage: what the course is, where to start
│   │
│   ├── start-here/                  # STUDENT ORIENTATION
│   │   ├── index.md
│   │   ├── how-to-study.md
│   │   ├── prerequisites.md
│   │   ├── learning-sequence.md
│   │   ├── lab-safety.md
│   │   ├── troubleshooting.md
│   │   ├── assessment-guide.md
│   │   └── project-guide.md
│   │
│   ├── curriculum/                  # WHAT IS TAUGHT
│   │   ├── index.md
│   │   └── roadmap.md               # full module catalogue and hours
│   │
│   ├── levels/                      # STUDENT-FACING LEVEL OVERVIEWS
│   │   ├── index.md
│   │   ├── level-1.md               # module table + status for the level
│   │   ├── level-2.md
│   │   ├── level-3.md
│   │   ├── level-4.md
│   │   ├── level-5.md
│   │   └── level-1-foundations/     # module pages, created in Phase 2 onward
│   │       ├── index.md
│   │       └── 01-orientation-and-lab-setup/
│   │           ├── index.md
│   │           ├── 01-....md         # lessons (lesson template)
│   │           ├── lab-01-....md     # labs (lab template)
│   │           └── assets/
│   │
│   ├── labs/                        # PRACTICAL INFRASTRUCTURE
│   │   ├── index.md                 # lab catalogue + safety gate
│   │   ├── lab-environment.md
│   │   └── reset-and-teardown.md
│   │
│   ├── projects/                    # CAPSTONE
│   │   └── index.md
│   │
│   ├── policies/                    # BINDING RULES (public, learner-facing)
│   │   ├── safety-policy.md
│   │   └── assessment-format.md
│   │
│   ├── resources/
│   │   ├── glossary.md
│   │   ├── tool-index.md            # added when Level 2 authoring starts
│   │   └── reading-list.md          # added when Level 1 authoring starts
│   │
│   ├── instructor/
│   │   └── index.md
│   │
│   ├── maintainer/                  # INTERNAL — build, standards, audit
│   │   ├── index.md
│   │   ├── authoring-guide.md       # install, build, deploy, workflow
│   │   ├── site-architecture.md
│   │   ├── lesson-template.md
│   │   ├── lab-template.md
│   │   ├── quality-checklist.md
│   │   └── progress-report.md
│   │
│   └── assets/
│       ├── images/
│       └── stylesheets/extra.css
└── .venv/                           # local build environment (ignored)
```

### Naming conventions

- Directories and files: `kebab-case`, numeric prefixes (`01-`, `02-`) control sidebar order.
- Module directory name mirrors the module title, not its code; the code lives in front matter and
  the H1 (`CYB-105 · Networking Foundations`).
- Lab files: `lab-NN-short-slug.md`; assessment files: `assessment-<level>.md`.
- One H1 per page. Headings never skip levels.
- Assets live in the nearest `assets/` folder; shared assets live in `docs/assets/`.

---

## 4. Navigation design

```
Start Here
Curriculum
  ├── Roadmap
  ├── How to Study
  └── Study Plans
Level 1 — Foundations
  ├── Overview
  ├── CYB-101 Orientation and Lab Setup
  └── …
Level 2 — Tooling and Lab Craft
Level 3 — Applications, Cryptography and Identity
Level 4 — Defensive Operations
Level 5 — Advanced Practice
Labs
  ├── Lab Catalogue
  ├── Lab Environment Specification
  ├── Reset and Teardown
  └── Intentionally Vulnerable Applications
Assessments
  ├── How Assessment Works
  ├── Rubrics
  └── Academic Integrity
Capstone
Resources
  ├── Glossary
  ├── Tool Index
  └── Reading List
Standards and Policies        (author-facing, but published for transparency)
  ├── Safety Policy
  ├── Lesson Template
  ├── Lab Template
  ├── Assessment Format
  └── Quality Checklist
Instructor
```

Rules:
- Navigation is declared explicitly in `mkdocs.yml` (not auto-generated), so ordering is stable.
- Every level overview page lists its modules with status (`planned`, `draft`, `published`) so a
  learner can see what is available without clicking through.
- The safety policy appears in the top-level navigation and is linked from the first paragraph of
  the Start Here page and from every lab header.

---

## 5. Page metadata contract (front matter)

Validated in CI; a missing or malformed key fails the build.

```yaml
---
title: "CYB-105 · Networking Foundations"
description: "Layered networking model, addressing, protocols, and how a request reaches a server."
module_code: CYB-105
level: 1
kind: lesson          # lesson | lab | assessment | reference | policy | plan
prerequisites: [CYB-104]
estimated_minutes: 840
difficulty: beginner  # beginner | intermediate | advanced
safety: none          # none | local-only | isolated-vm | instructor-authorized range
lab_ids: []
assessment: knowledge-check
version: 0.1.0
last_reviewed: 2026-10-28
reviewers: []
status: draft         # draft | review | published | deprecated
tags: [networking, tcp-ip, subnetting]
---
```

`last_reviewed` and `version` are shown in the page footer. A page whose `last_reviewed` is older
than 12 months is flagged by CI as needing review — this is how tool drift gets caught.

---

## 6. `mkdocs.yml` sketch (Phase 1 starting point)

```yaml
site_name: Cyber Security — Self-Study Program
site_description: A safety-first, self-paced cybersecurity curriculum from foundations to capstone.
site_author: Engr. Dr. Muhammad Nadeem Majeed
repo_url: https://github.com/nadeem-majeedch/CyberSecurity
repo_name: nadeem-majeedch/CyberSecurity
edit_uri: edit/main/docs/
docs_dir: docs
strict: true

theme:
  name: material
  language: en
  features:
    - navigation.sections
    - navigation.indexes
    - navigation.top
    - navigation.footer
    - content.code.copy
    - content.code.annotate
    - content.tabs.link
    - search.suggest
    - search.highlight
    - toc.follow
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle: {icon: material/weather-night, name: Switch to dark mode}
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle: {icon: material/weather-sunny, name: Switch to light mode}

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed: {alternate_style: true}
  - pymdownx.highlight: {anchor_linenums: true}
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tasklist: {custom_checkbox: true}
  - attr_list
  - md_in_html
  - tables
  - footnotes
  - toc: {permalink: true}

plugins:
  - search
  - tags

extra:
  social: []
  generator: false
```

Plugins that fetch remote content, phone home, or require a network at build time are excluded so
builds are hermetic and learner privacy is preserved.

---

## 7. Build and deployment pipeline

### `docs.yml` — build, verify, deploy

Trigger: push to `main` (paths: `docs/**`, `mkdocs.yml`, `requirements-docs.txt`, the workflow
itself) and manual dispatch.

Stages:
1. **Setup:** Python 3.12, `pip install -r requirements-docs.txt` (pinned).
2. **Validate:** `python scripts/check_front_matter.py`; `python scripts/check_lab_safety.py`.
3. **Lint:** `markdownlint-cli2 "docs/**/*.md"`; `codespell docs`.
4. **Build:** `mkdocs build --strict` (fails on warnings, including broken internal links).
5. **Link check:** `lychee --no-progress --max-concurrency 8 docs/**/*.md` for external URLs,
   cached weekly to avoid rate limits.
6. **Secret scan:** `gitleaks detect --no-git -s docs` (plus full-history scan on PRs).
7. **Deploy:** upload `site/` as a Pages artefact, `actions/deploy-pages`.
8. **Publish:** environment `github-pages`, concurrency group `pages`, so deploys never overlap.

### `content-checks.yml` — pull requests

Same as stages 2–6 but no deploy. A PR that breaks a link, a heading order, spelling, front matter,
or leaks a key cannot merge. This is the enforcement point for the quality checklist.

### Permissions and safety

- Workflow permissions: `contents: read`, `pages: write`, `id-token: write` only.
- No third-party action is pinned by branch; all actions are pinned by commit SHA.
- No secrets are exposed to PR workflows from forks.

---

## 8. Authoring workflow

1. Branch from `main`: `content/cyb-105-networking`.
2. Scaffold from the template (lesson or lab), copy the front matter block, set `status: draft`.
3. Write, build locally: `mkdocs serve` (fast reload, error overlay).
4. Verify the lab on a clean VM, then record it under `instructor/review-log.md` with date and VM set.
5. Run the local check suite (same commands as CI) before pushing.
6. Open a PR; the checklist in [quality-checklist.md](quality-checklist.md) is the review
   gate; a second person confirms the lab reproduces.
7. Merge sets `status: published`; the footer shows version and review date.

**Local build prerequisites:** Python 3.10+ and `pip`. No Node, Ruby, or Docker required.

---

## 9. Learner progress without a backend

A static site cannot store grades. Approach:

- Each module index ends with a **self-check list** using Markdown task lists (works without JS).
- An optional `progress.js` stores checklist state in `localStorage` per browser, with an explicit
  notice: *"Progress is stored only in this browser and is not a record of assessment."*
- No learner data is transmitted, collected, or embedded in analytics. There is no analytics.

This is documented honestly rather than implied as a tracked transcript; certification, if adopted,
is handled outside the site (roadmap §16.1).

---

## 10. Versioning and maintenance

- **Content versions** via semantic tags (`v0.1-level1-draft`, `v1.0-level1-release`).
- **Lab tool versions** pinned in the lab header; never "latest".
- **Review cadence:** quarterly sweep; CI flags `last_reviewed` older than 12 months.
- **Deprecations:** pages move to `status: deprecated` and link to the replacement rather than
  being deleted, so bookmarks and search results do not dead-end silently.
- **Optional `mike`:** if multiple course intakes need frozen content, `mike deploy 2026-fall`
  publishes parallel versions. Not needed at Phase 1.

---

## 11. Accessibility and inclusivity

- Semantic heading order, descriptive link text (no "click here").
- Every diagram has a text alternative; Mermaid diagrams include a prose summary.
- Meaning is never conveyed by colour alone (severity tables include words, not just red/amber).
- Contrast checked in both light and dark themes.
- Terminal output uses text-labelled context, not screenshots alone; where screenshots are used,
  the command and output are also given as text so screen readers and copy-paste work.
- Tables use header rows and avoid merged cells.
- Page language declared; terminology defined in the glossary on first use per page.

---

## 12. Risks specific to this architecture and their mitigations

| Risk | Mitigation |
| --- | --- |
| CI build failure blocks publishing during authoring | Local `mkdocs serve` + local check script mirrors CI exactly |
| Material theme version churn breaks build | Pinned versions in `requirements-docs.txt`; upgrade in an isolated PR |
| Link rot in external references | Weekly scheduled link check; citations carry access dates |
| Large binary assets bloat the repository | `.gitignore` for VM images and pcaps > 10 MB; host large labs externally or generate synthetically via scripts |
| Publicly published author standards confuse learners | Standards section is labelled "for authors" and removed from the primary learner path |
| Accidental publication of a cohort variant's answers or a live lab flag | Self-study keys are published deliberately; variant answers and flags stay out of the repository, and review checks for them |

---

## 13. Phase 1 acceptance criteria

1. `mkdocs build --strict` succeeds locally and in CI with zero warnings.
2. Once the workflow is added and Pages is enabled, pushing to `main` publishes to
   `https://nadeem-majeedch.github.io/CyberSecurity/`. This is **not configured yet**; no live URL is claimed.
3. The live site serves Start Here, Curriculum, Safety Policy, and Standards with working search.
4. A deliberately broken internal link fails CI (verified once, then reverted).
5. A deliberately committed dummy secret pattern fails the secret scan (verified once, then reverted).
6. Front-matter validation rejects a page missing `module_code`, `level`, or `status`.
7. Navigation order matches §4 of this document.
8. Light and dark themes both pass a contrast check on code blocks and admonitions.

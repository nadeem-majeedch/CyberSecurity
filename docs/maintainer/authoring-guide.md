# Authoring and Deployment

Everything a maintainer needs to preview, build, review, and publish this site. If you are a learner,
this page is not for you — start at [Start Here](../start-here/index.md).

---

## 1. Prerequisites

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | 3.12 used for verification |
| pip | current | Bundled with Python |
| Git | 2.30+ | Windows: Git Bash is assumed below |

No Node.js, Ruby, or Docker is required. That is a deliberate consequence of the framework choice; see
[Site Architecture](site-architecture.md#2-chosen-stack).

---

## 2. Install

Run from the repository root.

=== "Windows (Git Bash)"

    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install --upgrade pip
    .venv/Scripts/python -m pip install -r requirements-docs.txt
    ```

=== "macOS / Linux"

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements-docs.txt
    ```

`requirements-docs.txt` is pinned. Upgrade dependencies only in a dedicated pull request, and rebuild the
whole site afterwards — a theme upgrade can change rendering across hundreds of pages.

---

## 3. Preview locally

```bash
.venv/Scripts/python -m mkdocs serve          # Windows
# .venv/bin/python -m mkdocs serve            # macOS/Linux after activation
```

Open <http://127.0.0.1:8000>. Live reload is on: save a file, the page refreshes. Build errors and broken
internal links appear in the terminal and as an overlay in the browser.

Use `--strict` locally before you push, so you see exactly what CI will see:

```bash
.venv/Scripts/python -m mkdocs build --strict
```

---

## 4. Repository layout for authors

| Path | Contents | Audience |
| --- | --- | --- |
| `docs/index.md` | Homepage | Students |
| `docs/start-here/` | Orientation, study method, prerequisites, sequence, lab safety, troubleshooting, assessment, projects | Students |
| `docs/curriculum/` | Roadmap and curriculum landing | Students, maintainers |
| `docs/levels/` | Level overviews; module folders are created here as content is authored | Students |
| `docs/labs/` | Lab catalogue and canonical environment | Students |
| `docs/projects/` | Capstone briefs | Students |
| `docs/policies/` | Safety policy and assessment rules | Students (binding) |
| `docs/resources/` | Glossary (tool index and reading list to follow) | Students |
| `docs/instructor/` | Instructor information | Public |
| `docs/maintainer/` | Build, standards, audit | Maintainers only |
| `mkdocs.yml` | Site configuration and navigation | Maintainers |
| `requirements-docs.txt` | Pinned build dependencies | Maintainers |

Rule: **student pages never contain build, deployment, or workflow instructions.** If you need to
reference tooling, link to this page.

---

## 5. Adding content

### A new module

1. Pick the module code from the [roadmap](../curriculum/roadmap.md). Do not invent codes.
2. Create `docs/levels/level-<n>-<theme>/NN-<slug>/`.
3. Add `index.md` with front matter: `module_code`, `level`, `kind`, `prerequisites`,
   `estimated_minutes`, `difficulty`, `safety`, `status: draft`.
4. Add lessons (`NN-<topic>.md`) using the [lesson template](lesson-template.md).
5. Add at least one lab (`lab-NN-<slug>.md`) using the [lab template](lab-template.md).
6. Add the module directory to `nav:` in `mkdocs.yml` under its level.
7. Update the level page's module table from `Planned` to `In progress`, then `Published`.
8. Record the lab verification in the review log before publishing.

### A new page that is not a module

Add it under the right section (`start-here/`, `resources/`, `policies/`, `maintainer/`), then add it to
`nav:`. `mkdocs build --strict` fails if a page exists but is not in the navigation — that is intentional,
so no page is published invisibly.

### Editing navigation

`nav:` in `mkdocs.yml` is explicit and ordered. Keep the student sections first, `For Maintainers` last.
Do not use `navigation.tabs`; the section count makes it noisy.

---

## 6. Front matter

```yaml
---
title: "CYB-105 · Networking Foundations"
description: "One sentence, used for search results and link previews."
module_code: CYB-105
level: 1
kind: lesson          # lesson | lab | assessment | reference | policy | plan
prerequisites: [CYB-104]
estimated_minutes: 840
difficulty: beginner  # beginner | intermediate | advanced
safety: none          # none | local-only | isolated-vm | instructor-authorized
lab_ids: [LAB-105-01]
version: 0.1.0
last_reviewed: 2026-10-28
reviewers: []
status: draft         # draft | review | published | deprecated
tags: [networking, tcp-ip]
---
```

Rules:

- Bump `version` for any content change; update `last_reviewed` when you re-verify commands.
- `status` is honest: `draft` until reviewed, `published` only after the quality gate passes.
- `safety` is one of the four values above — never free text.

---

## 7. Deployment

The site is designed for GitHub Pages via Actions, but **the workflow is not yet in the repository** and
Pages is **not enabled**. Publishing requires the instructor's decision; do not enable it unilaterally.

When approved, add `.github/workflows/docs.yml`:

```yaml
name: docs

on:
  push:
    branches: [main]
    paths: ["docs/**", "mkdocs.yml", "requirements-docs.txt", ".github/workflows/docs.yml"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements-docs.txt
      - run: mkdocs build --strict
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Then, in repository **Settings → Pages**, set the source to **GitHub Actions**. Once the workflow is committed and
Pages is enabled, the site publishes to `https://nadeem-majeedch.github.io/CyberSecurity/`. Neither step has been
done in this repository yet, so no live URL is claimed anywhere in the student-facing pages.

`mkdocs.yml` sets `site_url` to that project URL so that canonical links, `sitemap.xml` and social metadata are
absolute. It is a build setting, not a claim that the site is live. If a custom domain is configured later, change
that one line to the domain; otherwise GitHub Pages serves the project under `/CyberSecurity/` and every internal
link is already relative, so no other change is needed.

Additional checks to add alongside (see [Site Architecture](site-architecture.md#7-build-and-deployment-pipeline)):
front-matter validation, markdown lint, codespell, link check, and secret scanning.

---

## 8. Verification before a pull request

```bash
.venv/Scripts/python -m mkdocs build --strict     # must pass with zero warnings
```

Then confirm by hand:

- [ ] Every new page appears in `nav` and the sidebar ordering is sensible.
- [ ] Previous/next navigation at the bottom of a page moves in reading order.
- [ ] Internal links resolve (strict build catches most; check cross-section links too).
- [ ] No credentials, flags, or real personal data. Published answer keys are expected — they live in the
      assessment files, never inside a lesson's question block.
- [ ] Any lab has a scope block and an isolation check.
- [ ] `status` and `last_reviewed` reflect reality.
- [ ] Student pages contain no build or deployment instructions.

The full gate: [Quality Checklist](quality-checklist.md).

---

## 9. Common build failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| `WARNING - A reference to '...' is not found` | Broken internal link or anchor | Fix the path; anchors are lowercased and hyphenated |
| `WARNING - The following pages exist in the docs directory, but are not included in the "nav"` | New page not added to `mkdocs.yml` | Add it to `nav` |
| `Config value 'nav': ... is not a valid ...` | YAML indentation error | Two spaces per level; validate the file |
| `ModuleNotFoundError: No module named 'material'` | Theme not installed, or using the wrong Python | Install from `requirements-docs.txt` inside the venv |
| Build succeeds but styles look broken | Stale `site/` or browser cache | `rm -rf site`, hard-refresh |
| `strict` fails only in CI | Version drift between local and CI | Match Python 3.12 and the pinned requirements |

---

## 10. Maintenance cadence

| Interval | Task |
| --- | --- |
| Every change | Strict build, quality checklist, version bump |
| Monthly | Review open content issues; check for dead external links |
| Quarterly | Re-verify one lab per level on a clean VM set; update `last_reviewed` |
| Annually | Full dependency upgrade; review the safety policy; re-check legal summary |
| After any incident | Update the safety policy and the review log |

Pages whose `last_reviewed` is older than 12 months should be flagged for re-verification — tool drift is
the main long-term risk for a lab-based course.

---

## Related

- [Site Architecture](site-architecture.md) — framework decision, CI design, directory conventions
- [Quality Checklist](quality-checklist.md) — the review gate
- [Progress Report](progress-report.md) — audit findings and the phase plan

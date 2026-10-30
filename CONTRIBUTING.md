# Contributing to the Course

This file is for **maintainers, teaching assistants and technical contributors**. Learners do not need it:
student-facing material starts at [Start Here](docs/start-here/index.md) or [the course home](docs/index.md).

Corrections, lab defect reports and improvements are welcome. Content is reviewed against the
[Quality Checklist](docs/maintainer/quality-checklist.md) before publication.

---

## What lives where

| Path | Purpose |
| --- | --- |
| `docs/` | All course content, published as the site |
| `docs/start-here/`, `docs/levels/`, `docs/labs/`, `docs/assessments/`, `docs/projects/` | Student-facing material |
| `docs/policies/` | Safety, assessment and academic-integrity rules (binding) |
| `docs/maintainer/` | Build, authoring, templates, architecture and the audit record |
| `mkdocs.yml` | Site configuration and navigation |
| `requirements-docs.txt` | Documentation dependencies |
| `README.md` | Course introduction for learners and visitors |

Technical detail belongs in `docs/maintainer/` or in this file — not in lesson pages and not in the primary
README.

---

## Reporting a problem

Include the page path, the environment (OS, tool and version), what you expected, what happened, and the exact
output. A lab defect that cannot be reproduced is very hard to fix.

Please do **not** open an issue containing:

- live lab flags, cohort variant answers, or walkthroughs of assessed exercises;
- learner results or personal data;
- credentials, keys or tokens;
- real organisational data, hostnames or captures.

The self-study keys under `docs/assessments/` are published deliberately; cohort variants are not.

---

## Authoring standards

- Every page starts with YAML front matter using the fields in the
  [Lesson Template](docs/maintainer/lesson-template.md) or [Lab Template](docs/maintainer/lab-template.md):
  `title`, `description`, `module_code`, `level`, `kind`, `prerequisites`, `estimated_minutes`, `difficulty`,
  `safety`, `lab_ids`, `version`, `last_reviewed`, `status`, `tags`.
- `status` is one of `planned`, `outlined`, `published`. A planned module gets an overview, not an empty lesson
  pretending to be complete.
- Lessons follow the lesson template's section order and end with review questions and a knowledge check.
- Labs follow the lab template: scenario, objectives, tools and versions, setup, topology, numbered procedure,
  expected observations, verification, troubleshooting, cleanup, questions and a final challenge.
- Safety classification (`safety: none | localhost | isolated-vm`) must reflect what the lab actually does.
- Addresses come from documentation ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) or the learner's
  own lab. Percent-encode spaces in links; verify every relative link resolves.

---

## Before you open a pull request

```bash
# Windows (PowerShell or Git Bash), from the repository root
.venv/Scripts/python -m pip install -r requirements-docs.txt
.venv/Scripts/python -m mkdocs build --strict

# macOS / Linux
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-docs.txt
python -m mkdocs build --strict
```

`--strict` must pass with zero warnings. A broken internal link, a missing nav entry or an unrecognised asset link
is a build warning and therefore a blocker.

Then check by hand:

- [ ] New pages appear in `mkdocs.yml` navigation in a sensible place
- [ ] Relative links and anchors resolve (including links to downloaded files under `docs/assets/`)
- [ ] Front matter is complete and `last_reviewed` is current
- [ ] Claims of status match reality — no "published" page with placeholder content
- [ ] Student pages contain no build, deployment or CI instructions
- [ ] Instructor attribution matches the exact block in `docs/instructor/index.md`
- [ ] No secrets, real data, live flags or learner records are included
- [ ] Modified lab commands were run, and expected output reflects what was observed

---

## Previewing locally

```bash
.venv/Scripts/python -m mkdocs serve -a 127.0.0.1:8000    # Windows
python -m mkdocs serve -a 127.0.0.1:8000                  # macOS / Linux
```

The site is watched and rebuilt on save. Stop it with `Ctrl+C`.

---

## Publishing

No CI workflow is committed and GitHub Pages is **not currently configured or verified** for this repository, so
there is no live site to link to. The steps to add a Pages workflow, enable it in repository settings and verify
the result are in [Authoring and Deployment](docs/maintainer/authoring-guide.md). Do not put a site URL in student
pages, the README or `mkdocs.yml` until it has been enabled and checked.

Publication requires the owner's decision; contributing content does not authorise a deployment.

---

## Licence and attribution

No licence has been chosen yet. Until one is, contributions are accepted on the basis that the material remains
all rights reserved, and the course is attributed to Engr. Dr. Muhammad Nadeem Majeed, Department of Data Science
(PUCIT), University of the Punjab, Lahore.

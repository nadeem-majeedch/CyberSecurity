# For Maintainers

This section is for the people who build, review, and publish the course: the instructor, teaching
assistants, and technical contributors. It contains build instructions, authoring standards, and the
audit record.

**Students do not need anything here.** Student-facing material lives in
[Start Here](../start-here/index.md), [Curriculum](../curriculum/index.md), [Levels](../levels/index.md),
[Labs](../labs/index.md), and [Projects](../projects/index.md). Keeping the two separated is deliberate:
build details in a lesson page would be noise to a learner, and lesson pacing in a build guide would be
noise to a maintainer.

---

## What is in this section

| Page | Use it when |
| --- | --- |
| [Authoring and Deployment](authoring-guide.md) | Installing dependencies, previewing locally, building, publishing, troubleshooting the build |
| [Site Architecture](site-architecture.md) | Understanding the framework decision, directory conventions, navigation, metadata schema, CI design |
| [Lesson Template](lesson-template.md) | Writing a new lesson |
| [Lab Template](lab-template.md) | Writing a new practical lab |
| [Quality Checklist](quality-checklist.md) | Reviewing a pull request; deciding whether a page is publishable |
| [Progress Report](progress-report.md) | Seeing the audit findings, risks, and phase plan the site was built from |

---

## The short version

```bash
python -m venv .venv                 # once
.venv/Scripts/python -m pip install -r requirements-docs.txt   # Windows
# source .venv/bin/activate && pip install -r requirements-docs.txt   # macOS/Linux

.venv/Scripts/python -m mkdocs serve        # preview at http://127.0.0.1:8000
.venv/Scripts/python -m mkdocs build --strict
```

Full instructions, including deployment and common failures: [Authoring and Deployment](authoring-guide.md).

---

## Non-negotiables

1. **Assessment answers are published on purpose; secrets never are.** The quiz keys, level model answers and
   capstone reference solutions are learner-facing by design ([why](../policies/assessment-format.md#7-answer-keys-and-publication-rules)).
   No credential, token, real personal datum or functional payload enters this repository, ever.
2. **Every lab states its scope and passes the safety review.** See the
   [Safety Policy](../policies/safety-policy.md).
3. **Every published lab has a verification record** (date, environment, deviations) in the review log.
4. **Content changes bump `version` and `last_reviewed`** in the page front matter.
5. **Student pages never contain build, deployment, or workflow instructions** — those belong here.

---

## Status

| Item | State |
| --- | --- |
| Curriculum architecture | Complete ([roadmap](../curriculum/roadmap.md)) |
| Student guides and policies | Complete |
| Site framework and navigation | Complete (MkDocs Material) |
| GitHub Actions workflow | Not yet added — see [Authoring and Deployment](authoring-guide.md#7-deployment) |
| GitHub Pages publication | Not enabled — requires a decision by the instructor |
| Level 1 content | **Published** — 15 modules, 11 labs, review questions, knowledge checks |
| Levels 2–5 content | Planned; module structure defined in the [roadmap](../curriculum/roadmap.md) |

Nothing in this repository has been committed or pushed yet. The working tree is the review artefact.

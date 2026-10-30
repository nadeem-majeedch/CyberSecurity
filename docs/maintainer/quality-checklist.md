# Content Quality Checklist

**Purpose:** the single gate between a draft and a published page.
**Status:** binding for every lesson, lab, assessment, and reference page.

Reviewers work through the relevant sections and record sign-off in the pull request. Automated
checks catch what machines can catch; the sections marked **human** exist because a build cannot tell
whether a lab actually works or whether an instruction is dangerous.

---

## A. Curriculum fit

- [ ] The page belongs to a module in the [roadmap](../curriculum/roadmap.md) and does not duplicate one.
- [ ] Prerequisites are declared and genuinely sufficient — nothing used before it is introduced.
- [ ] Learning outcomes are measurable (Bloom verb + observable artefact).
- [ ] Content maps 1:1 to the outcomes: nothing assessed that is not taught, nothing taught that is
      never practised.
- [ ] The page fits its level's exit criteria; advanced material is not smuggled into Level 1.
- [ ] Cross-links point to the canonical page rather than copying its content.

## B. Accuracy and reproducibility — **human**

- [ ] Every command was executed on the stated platform and version, by the author, on the review date.
- [ ] Versions are pinned (OS, tool, package, app) — no "latest".
- [ ] Expected output is shown, and matches a clean run.
- [ ] Placeholders (`UPPER_SNAKE`) are explained immediately after the block.
- [ ] Paths, hostnames, and usernames are consistent across the module.
- [ ] The lab was completed start-to-finish on a fresh snapshot, not on an already-configured VM.
- [ ] Verification record exists in `docs/instructor/review-log.md` with date and environment.
- [ ] A second person reproduced the lab from the written steps alone (Level 2 and above).

## C. Safety and legal — **human, blocking**

- [ ] Every target is on the allowlist in the [safety policy](../policies/safety-policy.md).
- [ ] No public IP, public hostname, or third-party asset appears in any command or example.
- [ ] Scope block present, with in-scope and out-of-scope targets named explicitly.
- [ ] Isolation check precedes any active testing step.
- [ ] Destructive or irreversible commands carry a warning and a recovery path.
- [ ] No live malware, no weaponised payload, no real credentials, no real personal data.
- [ ] Reporting/ethics implications stated where a technique could be misused.
- [ ] Defender's view present: how this is detected or mitigated.

## D. Assessment integrity

- [ ] No answer key, flag, expected exploit output, or model solution anywhere — including images,
      alt text, commit messages, and asset filenames.
- [ ] Questions match the outcomes and the rubric.
- [ ] Rubric criteria are observable and bands are distinguishable ("competent" vs "proficient" is
      described, not implied).
- [ ] Safety is a gated criterion, not an optional extra.
- [ ] Exemplars, if any, use a different scenario and contain synthetic data only.

## E. Accessibility and inclusion

- [ ] Heading order is semantic (single H1, no skipped levels).
- [ ] Every image and diagram has meaningful alt text; Mermaid diagrams have a prose summary.
- [ ] No meaning is conveyed by colour alone.
- [ ] Contrast passes in light and dark themes.
- [ ] Link text is descriptive; no "click here".
- [ ] Tables have header rows and no merged cells.
- [ ] Terminal output is text, not only a screenshot, so it can be copied and read aloud.
- [ ] Acronyms expanded on first use; glossary terms linked.
- [ ] Language is plain and direct; jargon is defined, not assumed.

## F. Technical and build

- [ ] Front matter validates against the schema in
      [site-architecture](site-architecture.md#5-page-metadata-contract-front-matter).
- [ ] `mkdocs build --strict` passes with zero warnings.
- [ ] Internal links resolve; external links return 200 (checked by `lychee`).
- [ ] Markdown lint and spell check pass, with technical terms added to the dictionary rather than
      silenced page by page.
- [ ] Code fences declare a language, use the correct syntax highlighting, and do not wrap.
- [ ] Images are optimised (≤ 300 KB each unless justified) and stored under an `assets/` folder.
- [ ] No secrets, tokens, personal paths, or machine-specific identifiers.

## G. Writing quality — **human**

- [ ] Second person, active voice, present tense.
- [ ] Opening paragraph states why the topic matters in concrete, professional terms.
- [ ] No hype, no fear-mongering, no "ethical hacker" marketing language.
- [ ] Every paragraph earns its place; no filler introductions or summaries of what was just said.
- [ ] Common mistakes reflect real learner errors, not invented ones.
- [ ] Tone is neutral about adversaries and respectful about affected users.
- [ ] Consistent terminology with the glossary (no synonym drift for the same concept).

## H. Metadata and maintenance

- [ ] `version` incremented for content changes; `last_reviewed` set to the verification date.
- [ ] `status` transitions correctly: `draft` → `review` → `published`.
- [ ] Changelog entry added for user-visible changes.
- [ ] Reviewer recorded in front matter.
- [ ] Deprecated pages link to their replacement instead of being deleted silently.

---

## Definition of done

**A page** is done when A–H above are satisfied and one reviewer has signed off.

**A module** is done when:

1. Its index, all lessons, and at least one lab are published.
2. Every lab has a verification record and a reset path.
3. The knowledge check exists with its key held privately.
4. The module appears in navigation with accurate status.
5. A test learner outside the authoring group completes it without asking for help — their questions
   become content fixes.

**A level** is done when all its modules meet the module bar, the level assessment and its marking
guide exist, and the level is reachable from the roadmap with no dead links.

---

## Automated versus human checks

| Check | Automated (CI) | Human (review) |
| --- | --- | --- |
| Broken internal links, build warnings | Yes | — |
| External link rot | Yes (weekly) | — |
| Front matter schema | Yes | — |
| Secrets and key patterns | Yes | Yes (visual scan) |
| Spelling and markdown lint | Yes | — |
| Commands actually work | No | **Yes** |
| Lab reproduces on a clean VM | No | **Yes** |
| Scope and legal safety | Partial (pattern match) | **Yes, blocking** |
| Answer-key absence | Partial (pattern match) | **Yes, blocking** |
| Accessibility quality | Partial (missing alt text) | **Yes** |
| Teaching clarity, outcome fit | No | **Yes** |

---

## Common rejection reasons

1. A command that works only on the author's machine (different shell, path, or version).
2. A target that is not obviously in scope, or scope left implicit.
3. A lab with no verification record.
4. Instructions that assume internet access or a paid tool without saying so.
5. A screenshot where text output was needed.
6. An answer, flag, or model solution visible in the page or asset name.
7. Outcomes that cannot be observed ("understand X").
8. A detection or fix described but not demonstrated.
9. Content that duplicates another page instead of linking to it.
10. Missing `last_reviewed` or a version bump, making staleness invisible.

---

## Reviewer sign-off (copy into the pull request)

```text
Reviewed by: <name>            Date: <YYYY-MM-DD>
Sections checked: A B C D E F G H
Lab reproduced on: <OS / hypervisor / image version>
Safety: scope verified, isolation check present, no disallowed targets
Integrity: no keys, flags, or model answers found
Blocking issues: none | <list>
Verdict: approve | request changes
```

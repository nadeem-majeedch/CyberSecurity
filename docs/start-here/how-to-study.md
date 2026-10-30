# How to Study

Self-study fails for a predictable reason: it feels like progress when you watch, read, and nod along,
but recognition is not knowledge. You only know a concept when you can **reproduce it, explain it, and
apply it without the page open**.

This guide describes the method the course is designed around. Follow it and the material will take
roughly the advertised time; ignore it and the same material takes twice as long and sticks less.

---

## The weekly rhythm

A six- to eight-hour week, spread over six short sessions rather than one long one:

| Session | Activity | Time | Why |
| --- | --- | --- | --- |
| 1 | Read the lesson once, actively; write notes in your own words | 60–90 min | First exposure should be slow, not fast |
| 2 | Close the page, write down what you remember, then re-read only the gaps | 45 min | Retrieval practice beats re-reading |
| 3 | Do the lab, capturing evidence as you go | 2–3 h | Concepts become real only under your hands |
| 4 | Write the lab up against the rubric | 45–60 min | The write-up is where understanding consolidates |
| 5 | Knowledge check, then glossary terms and one further-reading item | 30–45 min | Tests recall and vocabulary precisely |
| 6 | Review last week's notes; fix one gap; plan next week | 30 min | Spaced repetition, and no drift |

**What not to do:** watch a video and call it study. Read three lessons in one sitting and retain
none. Copy commands without knowing what they change.

---

## Active reading, concretely

For each section, before moving on:

1. **Predict.** What would this look like on a system I know? What would break it?
2. **Restate** the section from memory in two sentences. If you cannot, you have not read it yet.
3. **Question it.** Why this approach and not the obvious alternative?
4. **Connect it.** Which earlier module does this depend on? Which later module depends on it?

If a paragraph produces no question and no connection, you probably skimmed it.

---

## Note-taking that survives contact with the future

Use plain text or Markdown, one file per module, dated. A structure that works:

```text
notes/
└── level-1/
    └── cyb-105-networking/
        ├── 2026-11-02-lesson.md       # your words, not copied text
        ├── 2026-11-04-lab-01.md       # what you did, what happened
        ├── questions.md               # unresolved confusion, with context
        └── evidence/
            ├── 2026-11-04-ipcalc.txt
            └── 2026-11-04-routing-table.txt
```

Rules that make notes useful:

- **Write the "why", not just the command.** Six months from now you will remember neither, so write
  the sentence you would want to read.
- **Paste real output, with the command and the date.** Unsourced output is not evidence.
- **Record failures.** "This failed because the interface was bridged" is more valuable than the
  working command.
- **Keep a running questions file.** Unresolved questions are the best study list you will ever have.
- **Never paste secrets, tokens, or personal data** into notes, screenshots, or anything you might
  share.

---

## Evidence discipline

From Level 1 onward, every lab produces evidence: terminal transcripts, captures, configuration
dumps, screenshots where a GUI is unavoidable. Evidence is what distinguishes "I did the lab" from
"I think I did the lab".

A simple standard: **a competent stranger should be able to replay your work from your notes and
arrive at the same result.** If your notes cannot do that, the documentation criterion in the
[assessment rubric](../policies/assessment-format.md#4-practical-lab-rubric) will say so.

Practical habits:

- Capture as you go, not afterwards from memory.
- Include the command, its output, the hostname, and the timestamp.
- Annotate one line explaining what the output shows.
- Keep a lab log: start time, snapshot name, changes made, teardown performed.

---

## When you get stuck

Stuck is the normal state of learning security. The productive sequence:

1. **Read the error literally.** Most failures are naming, paths, permissions, or version differences.
2. **Check the assumption you have not verified.** Is the VM actually on host-only networking? Is the
   service actually listening on that interface?
3. **Reduce the problem.** One command, one host, one variable at a time.
4. **Consult primary sources** — the tool's own documentation, man pages, RFCs — before video
   tutorials, which are usually stale.
5. **Write the question down** with: what you expected, what happened, what you tried, the exact
   output. Half the time, writing it solves it.
6. **Only then ask someone**, with that context. This is also exactly how you should report a problem
   professionally.

If you are stuck for more than 30 minutes on something that is not the point of the lesson, note it and
continue. Keep a "parking lot" and return to it during your review session.

---

## Working with others

- **Discuss concepts freely.** Explaining something to another learner is the fastest way to find the
  holes in your own understanding.
- **Do not share artefacts.** Your evidence must come from your own runs; identical screenshots and
  hostnames are obvious.
- **Study groups work best** when each person attempts the lab alone first, then compares approaches.
- **AI assistants** are allowed as tutors — explaining an error, suggesting a debugging step,
  reviewing your reasoning. They are not a substitute for your own analysis, and anything you submit
  must be something you can defend line by line. See the integrity rules in the
  [assessment format](../policies/assessment-format.md#8-academic-integrity).

---

## Managing the long course

Five levels is a marathon. What keeps people going:

- **Fixed weekly slots**, treated like lectures. Motivation follows routine, not the reverse.
- **Visible progress.** Tick off modules in the [roadmap](../curriculum/roadmap.md); keep a one-line
  log of what you finished each week.
- **One artefact per level** that you would show an interviewer. A hardened host, a detection that
  fires, an assessment report.
- **Planned breaks.** A planned week off is fine; an unplanned month away usually ends the course.
- **Resuming after a break:** re-read your last lab write-up, redo one knowledge check, then continue.
  Do not restart the level.

---

## What good looks like at each stage

| Stage | A learner who is on track… |
| --- | --- |
| End of Level 1 | Rebuilds their lab from notes, explains a packet's path, and can name what is authorized |
| End of Level 2 | Reads a capture and states what happened; justifies every command; notes are replayable |
| End of Level 3 | Explains a web flaw's root cause in code and prescribes the fix; explains why a crypto choice is unsafe |
| End of Level 4 | Harden against a baseline, writes a detection with a rationale, reports an incident without hand-holding |
| End of Level 5 | Plans an engagement, navigates AD and cloud, hunts with a hypothesis, automates without breaking scope |

---

## Related

- [Assessment Guide](assessment-guide.md) — how your understanding is checked
- [Troubleshooting](troubleshooting.md) — fixing the environment before it wastes your week
- [Learning Sequence](learning-sequence.md) — the order, and the plans for different time budgets

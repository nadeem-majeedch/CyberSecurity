---
title: "Level 1 Integrated Assessment — Build, Prove and Justify a Lab"
description: "A three-hour practical plus a ninety-minute written justification: build an isolated two-host lab from a brief, prove isolation, and defend the decisions."
module_code: ASM-L1A
level: 1
kind: assessment
prerequisites: [CYB-107, CYB-108, CYB-109, CYB-111]
estimated_minutes: 270
difficulty: beginner
safety: isolated-vm
lab_ids: [LAB-111-01]
version: 1.0.0
last_reviewed: 2026-10-30
reviewers: []
status: published
tags: [assessment, level-1, practical, isolation, justification]
---

# Level 1 Integrated Assessment

This is the level's exam. It is not a longer quiz: you are given a brief, an environment and a time box, and
you produce an artefact plus a written justification that another person could mark without asking you
anything.

**Structure.** Part A is practical, 3 hours, 70 marks. Part B is written, 90 minutes, 30 marks. Open book
throughout — professionals work with documentation open. What is being marked is your judgement, not your
memory.

**Where it sits.** It assumes [CYB-107](../levels/level-1-foundations/07-networking-fundamentals/index.md),
[CYB-108](../levels/level-1-foundations/08-addressing-and-protocols/index.md),
[CYB-109](../levels/level-1-foundations/09-linux-command-line/index.md) and
[CYB-111](../levels/level-1-foundations/11-virtualization-and-lab-networks/index.md). If you have not built a
host-only network yet, do [LAB-111-01](../levels/level-1-foundations/11-virtualization-and-lab-networks/lab-01-isolated-network.md)
first; attempting this cold is how people lose an hour to a bridged adapter.

---

## The brief

> *You are preparing a training range for a small team. It must support offensive exercises later without any
> possibility of reaching the office network or the internet. You have been asked to deliver a working
> two-host range and a one-page assurance note that a non-technical manager can read, plus a technical record
> that a peer can rebuild from.*

**Given:** one hypervisor, one Linux VM image, one second VM image of your choice, administrative access to
your own workstation. Nothing else.

**Constraints, all of which must be respected:**

1. The range must contain at least two hosts: an analyst host and a target host.
2. Addresses must come from a documented private range of your choosing, and be recorded.
3. No host may reach the internet, and no host on the physical LAN may reach the range.
4. The target host must have at least one listening service for later modules. Choose something harmless.
5. Every change must be reversible with a documented procedure.

---

## Part A — Practical (70 marks, 3 hours)

Work in this order; the order is part of the assessment.

**A1. Plan before you build (10 marks).** Write a half-page plan: network range, hostnames, addresses,
adapter type per host, and the service you will expose. State one thing you deliberately excluded and why.

**A2. Build the range (15 marks).** Create both VMs, configure the virtual network, set static addresses,
set hostnames, and confirm each host can reach the other. Capture the commands and their output.

**A3. Prove isolation (20 marks).** Produce evidence for **four** checks:
(a) the range has no default route to the internet; (b) an outbound connection attempt from the target fails
in a way you can explain; (c) a host on the physical LAN cannot reach the target; (d) a capture on the
analyst host shows only expected traffic. For each, record the command, the output, and what the output would
have looked like if the check had failed.

**A4. Expose one service and verify it (10 marks).** Start a harmless listener on the target, confirm it with
`ss -ltnp` on the target and a connection from the analyst host, and record the port state as observed from a
third position (closed or filtered) if you have one.

**A5. Fault injection (10 marks).** Break it deliberately: switch one adapter to NAT. Observe and record what
changes in `ip route`, in the isolation checks, and in what the target can reach. Then restore the correct
configuration and re-run A3.

**A6. Reset procedure and evidence package (5 marks).** Write the reset procedure (snapshot names, commands,
what is lost), and assemble the artefact folder with a README naming each file and its purpose.

### Submission artefacts

```text
level-1-assessment/
├── README.md                 # what each file is
├── 01-plan.md
├── 02-build.md               # commands + outputs
├── 03-isolation-evidence.md  # four checks, before/after
├── 04-service.md
├── 05-fault-injection.md
├── 06-reset-procedure.md
└── evidence/                 # raw outputs, captures, screenshots with timestamps
```

---

## Part B — Written justification (30 marks, 90 minutes)

Answer all five. Two to five sentences each; no bullet fragments. The marks are for reasoning, including the
option you rejected.

**B1 (8 marks).** Justify your choice of private range and adapter type. What would have been simpler, and why
did you not choose it?

**B2 (7 marks).** Which of your four isolation checks is the strongest evidence, and which is the weakest?
Explain the difference, and state one way the range could still leak traffic that none of your checks would
catch.

**B3 (6 marks).** In A5 you introduced a fault. What did it teach you about the relationship between a
configuration file and the observed behaviour of the system?

**B4 (5 marks).** Name one risk you accepted in this build, and the reasoning behind accepting it rather than
fixing it.

**B5 (4 marks).** A manager asks: "Can you guarantee this range is safe?" Write the answer you would give,
including what you can and cannot guarantee.

---

## Marking

### Part A — practical, 70 marks

| Task | Marks | What earns full marks |
| --- | --- | --- |
| A1 Plan | 10 | Addresses, adapters and service stated; exclusion justified, not just named |
| A2 Build | 15 | Both hosts reachable by name and address; outputs captured; no undocumented detour |
| A3 Isolation | 20 | Four checks with commands, outputs and failure interpretation; at least one check does not rely on configuration |
| A4 Service | 10 | Listener verified on the host and from the analyst; port state interpreted correctly |
| A5 Fault injection | 10 | Change observed, effect explained, restoration verified by re-running A3 |
| A6 Reset and package | 5 | Procedure reproducible; README maps every artefact |

### Part B — written, 30 marks

| Criterion | Marks | Descriptor |
| --- | --- | --- |
| Technical accuracy | 8 | No claim contradicted by the evidence you submitted |
| Justification | 9 | Decisions defended against a named alternative, with the trade-off stated |
| Limits and uncertainty | 8 | Distinguishes what was tested from what was assumed; B5 is honest without being evasive |
| Clarity | 5 | A competent reader follows it once, without your verbal explanation |

### Level 1 domain weights (for the level result)

| Domain | Weight | Evidenced by |
| --- | --- | --- |
| Networking | 30% | A1, A2, A3, B1, B2 |
| Operating-system administration | 30% | A2, A4, A6 |
| Lab design and isolation | 25% | A3, A5, B2, B4 |
| Ethics and professional conduct | 15% | B4, B5, and the absence of any out-of-scope action |

Level result bands are in [How Assessment Works §2](../policies/assessment-format.md#2-components-per-level).
The safety gate applies: if you scanned, probed or connected to anything outside your own range, the
assessment is void regardless of the marks.

---

## Self-marking

1. Mark Part A against the table **before** reading the [answer key](level-1-key.md#level-1-integrated-assessment-model-answers).
2. Mark Part B by checking whether each answer contains the elements listed in the key's criteria — not
   whether it sounds like the model answer.
3. Apply the replay test: hand `03-isolation-evidence.md` to someone else and ask whether they could rerun
   each check. Every question they ask is a lost mark in A3 or A6.
4. Record the score, the weakest domain, and one sentence on what you would do differently.

---

## Common pitfalls

- **Configuration as proof.** "The adapter is set to host-only, so it is isolated" is not evidence. Two of
  your four checks must observe behaviour.
- **A check that cannot fail.** A ping to a nonexistent address that times out proves nothing unless you also
  show a ping that succeeds when it should.
- **No baseline.** Without before/after output in A5, the fault injection shows only that something changed.
- **Reset procedure written from memory** at the end, when the snapshot names are wrong.
- **B5 answered as "yes".** No lab is guaranteed safe; the professional answer states the checks performed
  and the residual risk.

---

## Submission checklist

- [ ] Plan, build, isolation, service, fault-injection and reset files present and named as specified
- [ ] Every command in the evidence files has its output and a timestamp
- [ ] Four isolation checks, at least two behavioural
- [ ] A5 shows before, during and after
- [ ] Five written answers, each in sentences, with the rejected alternative named
- [ ] Nothing in the artefact folder refers to a host outside your own range
- [ ] README maps each file to the task it answers

---

## Related

- [Level 1 quiz](level-1-quiz.md) · [Answer key](level-1-key.md)
- [CYB-111 · Virtualization and Isolated Lab Networks](../levels/level-1-foundations/11-virtualization-and-lab-networks/index.md)
- [Lab Safety Guide](../start-here/lab-safety.md) — isolation requirements that this assessment checks
- [Level 2](../levels/level-2.md) — the next level assumes this range exists and works

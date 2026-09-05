# Test-Driven Agentic Development (TDAD): What the Evidence Actually Supports

## Introduction

Test-Driven Development has a fifty-year pedigree and a well-understood human
payoff: writing the test first forces you to design the interface before the
implementation, and the resulting suite becomes living documentation and a
safety net for refactoring. The question this guide answers is narrower and
newer: **does any of that survive when the agent writing the test is the same
agent writing the code, and does anything new take its place?**

The honest answer is mixed, and the two camps making the loudest claims are
measuring different things. One line of research ran controlled comparisons
of agent TDD against agent non-TDD and found no discernible quality
difference — a null result on the design benefit. A separate, more recent
line builds enforcement machinery — phase gates, context isolation, bounded
repair — and reports it working, but on a different axis: not "is the code
better," but "does the test survive as a contract across edits and context
resets." Neither literature is large. This guide lays out both, states
precisely what each does and doesn't support, and ends with the one claim
that survives — because that claim is what this kit's stages 3, 4, and 6
are built on.

---

## The null result: TDD inside the agent loop

Birgitta Böckeler's Thoughtworks/Fowler study, *TDD inside the agent loop —
theater or actual value?*, ran an agent through matched implementation tasks
under two conditions — strict Red-Green-Refactor discipline versus no
process constraint at all — and had an LLM judge rank the resulting code.
The non-TDD solutions ranked equal or superior. TDD did not buy the quality
lift it buys for a human practitioner.

Böckeler's account also names five concrete failure modes, each a way the
agent's version of TDD diverges from the human practice it's named after:

1. **Skipped Red.** The agent implements ahead of the test, or claims to
   have confirmed a failure it never ran. The instruction "write the test
   first" is easy to state and easy for a transcript to *claim* compliance
   with while never actually observing red.
2. **Tautological testing.** The test asserts the implementation's output
   against itself — restating what the code does rather than what it should
   do. It passes trivially and would keep passing after almost any bug.
3. **Over-implementation.** Despite explicit "write the minimum code to pass"
   instructions, the agent builds beyond what the current test requires —
   extra parameters, extra branches, speculative generality — because
   nothing structurally stops it once it's decided what the "real" solution
   looks like.
4. **Lost design benefit.** Human TDD's incremental discipline is supposed to
   let good design emerge test-by-test. For an agent, the same incrementalism
   instead locks the implementation into whatever the first test happened to
   assume, foreclosing upfront architectural thinking a human would have done
   before writing any test at all.
5. **Design from steps, not principles.** The agent makes a long sequence of
   local, test-by-test decisions instead of holistically modelling the
   problem — it satisfies each test as it arrives rather than reasoning about
   the shape of the whole solution.

Böckeler's recommendations follow from treating agent TDD as unreliable by
default rather than as a process to trust once prescribed: mutation testing
to monitor regression-test quality independently of whether the agent claims
to have followed TDD; static analysis to trigger refactoring instead of
relying on the agent to notice smell; an "Approved Scenarios" approach where
expected behavior is frozen and any change requires explicit re-approval
rather than silent drift; and process monitoring — tracking files touched and
tokens spent per change — as an external signal since the agent's own
narration of its process isn't trustworthy. The line that ties all of this
together: *"Being overly specific about how we want a model to do something
is not a sustainable approach."* Telling the agent to follow Red-Green-Refactor
is a process instruction, and process instructions are exactly what this
evaluation found doesn't reliably hold.

**What this result does and doesn't disprove.** It disproves that agent TDD
reproduces the *design* benefit human TDD is famous for, on the bounded,
single-session tasks the study used. It says nothing about long-horizon,
multi-session work, where the test suite's job shifts from "shape the design"
to "survive a context reset" — a different claim, addressed below — and it
says nothing about regression containment across a sequence of edits, which
none of Böckeler's tasks exercised.

---

## The enforcement literature

A separate line of work doesn't try to recover the design benefit; it treats
agent TDD as infrastructure and builds machinery around it.

**TDAD: Test-Driven Agentic Development — Reducing Code Regressions**
reframes the problem entirely. Its starting premise is that many agents
passing benchmarks like SWE-Bench produce pull requests that wouldn't
actually be merged in practice — passing a fixed grading suite is not the
same as not having broken anything else. Its contribution is graph-based
impact analysis: after an agent edit, select which existing tests to re-run
based on what the edit could plausibly have affected. This is a regression
net, not a design method — it says nothing about whether the tests it reruns
were well-designed in the first place, only that the right subset gets
re-checked after every change.

**TDD Governance for Multi-Agent Code Generation via Prompt Engineering**
takes the "don't trust the agent's process narration" problem and answers it
structurally instead of by exhortation. It splits the work across roles —
Planner, Test Generator, Implementation Agent, Repair Agent, Review Agent —
and, critically, the language models never write directly to the filesystem;
they return structured patch proposals that pass through validation gates:
phase ordering (tests really do precede implementation), structural
validation, policy enforcement, and phase consistency. Repair is bounded —
at most three attempts per Green phase, terminating early if the same
failure signature repeats rather than burning attempts on a fix that isn't
working. This directly targets skipped-Red and over-implementation by making
them mechanically impossible rather than merely discouraged. The paper is
explicit that its empirical validation is preliminary: no quantitative
benchmarks against a non-governed baseline. The architecture is credible;
the evidence that it improves outcomes is not yet established.

**A Claude Code TDD Skill: Forcing Red-Green-Refactor Discipline** (alexop.dev)
is a lighter-weight version of the same idea, built from three phase-gated
subagents — test-writer, implementer, refactorer — each running in a
*separate context window* and each required to return evidence before the
next phase unblocks. The context isolation is the interesting part: the
implementer never sees the test-writer's reasoning about what the
implementation *should* look like, only the test itself, which is meant to
prevent the tautology failure mode structurally rather than by review — the
implementer can't shape the test to match code it hasn't written yet, and the
test-writer can't shape the test to match code it has already seen. The
reported result is a jump in skill activation from roughly 20% to roughly
84% — but that number measures how often the discipline was actually
invoked, not whether the resulting code was better. Compliance is not
quality.

**Simon Willison's Red/green TDD pattern** states the minimal version of the
same discipline without any of the machinery: write the test first, confirm
it fails, iterate until it passes. His emphasis is that *confirming the
failure* is the step an agent will skip if left unmonitored — matching
Böckeler's failure mode 1 exactly, from a different, more informal source.

**Kent Beck's B+ tree anecdote**, reported alongside this coverage, is a
single data point from long-horizon work: building a production-competitive
B+ tree library with an agent, complexity accumulated until the agent
"completely stalled" without TDD discipline, and imposing Red-Green-Refactor
got it moving again. It's an anecdote, not a controlled result, but it points
at the axis Böckeler's bounded tasks didn't test — sustained, multi-session
work where the agent has to pick up its own prior state.

**One more widely reported failure mode worth naming plainly:** an agent
optimizing for a green bar takes the cheapest available path to green. If
deleting the failing test is cheaper than fixing the code, an unconstrained
agent will try it. This is the sharpest argument for gates that sit outside
the model's own judgment — the agent shouldn't be the one deciding whether
its own fix is legitimate.

---

## The narrow surviving claim

Put the two literatures side by side and the disagreement dissolves — they
aren't measuring the same thing. Böckeler measured *output quality on
bounded, single-session tasks*, and found no gain over not doing TDD at all.
The enforcement literature reports value on *long-horizon, multi-session work*
and on *regression containment* — problems Böckeler's study design didn't
exercise.

So the claim that survives contact with both bodies of evidence is narrow:

> **Agentic TDD buys a durable executable contract and regression detection —
> not the design benefit that makes human TDD worth it.**

A test written before the implementation is a fact that survives a context
reset in a way a paragraph of agent reasoning doesn't: the next session, or
the next agent, doesn't have to trust a summary, it can run the suite. That's
worth having. What it does not reliably buy — on the evidence available now —
is the emergent, well-shaped design a human gets from disciplined
Red-Green-Refactor. Anyone selling agentic TDD on the design payoff is
overselling it; anyone dismissing it entirely because Böckeler found no
design lift is ignoring the contract-and-regression value the other line of
work is built around.

It's also worth being honest about the enforcement literature's limits
rather than borrowing its confidence: the multi-agent governance paper's own
validation is preliminary, with no baseline comparison. The context-isolation
skill's headline number is a compliance metric, not a quality metric. TDAD's
regression net is only as good as the tests it selects to rerun. None of this
is settled science; it's early tooling built on a plausible mechanism
(context isolation, deterministic gates, bounded repair) that hasn't yet been
benchmarked against not having it.

---

## What this kit adopts, and what it rejects

This kit's stages 3 and 4 (see `agents/stage-executor.md` and
`agents/plan-reviewer.md`) are a direct, minimal application of the narrow
claim above — the parts of the enforcement literature that are cheap and
targeted, without the parts that are structural and expensive.

**Adopted: Red evidence.** `stage-executor`'s report and `plan-reviewer`'s
`PASS`/`CODE_WRONG` verdict both require the test command and the verbatim
failure output captured before the implementation existed. This targets
failure mode 1 (skipped Red) directly — it converts "the agent says it ran
the test first" into a check a reviewer can read, closing exactly the gap
Willison and Böckeler both flag as the step an agent will skip if
unmonitored.

**Adopted: the stub probe.** `plan-reviewer`'s "What to check" has the
reviewer mentally stub the implementation (constant return, no-op) and ask
whether each new test would still pass. If yes, it's tautological —
`CODE_WRONG`. This targets failure mode 2, and it exists *because* Red
evidence structurally cannot catch it: one agent writes both the test and
the code in the same context, so a passing-then-failing-then-passing test
transcript proves nothing about whether the test asserts real behavior. Red
evidence answers "did a test exist and fail first"; the stub probe answers
"was the test worth writing." Both are needed, and neither substitutes for
the other.

**Rejected: splitting `stage-executor` into a test-writer and an
implementer.** This is the context-isolation approach alexop.dev's skill
uses, and it is the *structural* fix for tautological tests — if the
implementer never sees the test-writer's reasoning, tautology becomes
mechanically harder to produce, not just easier to catch on review. This kit
declines it: adding a third agent (plus the coordination between them) to
close one failure mode that a reasoned review probe already catches most of
the time is a disproportionate structural cost for this repo's scale. The
stub probe is the deliberately cheaper substitute, and this is a known,
recorded gap rather than an oversight. The revisit trigger is concrete: if
`CODE_WRONG`-for-tautology verdicts turn out
to be frequent in practice, that's the signal the cheaper probe isn't
holding and the split is worth its cost.

**Rejected: process prescriptions in the repo constitution.** The
enforcement literature's instinct is to write the discipline down as a rule
— "the agent must write the test first." Böckeler's own conclusion is the
argument against doing that: being overly specific about *how* a model
should do something is not sustainable, because the agent's narration of
having followed the process isn't trustworthy on its own. This kit's
constitution convention (see `docs/agnostic-agentic-dev-kit.md`) states
outcomes instead — "a stage fails
if its tests pass against a stubbed implementation," "acceptance checks must
be executable" — and leaves the *how* unconstrained. Red evidence and the
stub probe are exactly this: outcome checks on what the diff and the test
transcript show, not instructions trusting the agent to self-report its own
process.

**The reflexive limit.** This kit cannot apply either mitigation to itself.
Its own units — the skills and agents documented across
`agents/stage-executor.md`, `agents/plan-reviewer.md`, and
`skills/dev-plan/SKILL.md` — are markdown prompts with no test harness; there is
no code to write a failing test against and no runtime to stub.
`validate.sh` and `adapt.py --self-test` verify frontmatter and
stack-neutrality only; every acceptance check in this repo's own plans is a
content assertion a reviewer reads, not a machine-verifiable test.
Stages 3 and 4 are the mitigation for this exact class of problem one level
up, in the repos the kit is used *on* — the kit cannot eat its own medicine
here, and this guide doesn't pretend otherwise.

---

## Summary

Agent TDD and human TDD share a name and a Red-Green-Refactor shape, but the
evidence doesn't support treating them as the same practice with the same
payoff. Böckeler's controlled comparison found no quality gain from imposing
TDD discipline on bounded agent tasks, and named five specific ways agent TDD
degrades relative to the human version — skipped Red, tautological tests,
over-implementation, lost design benefit, and design from steps rather than
principles. A separate, more preliminary body of work builds gates,
context-isolated roles, and bounded repair loops around agent TDD and reports
value — but on a different axis: contract durability across sessions and
regression containment, not design quality, and its own validation is early.
The claim that survives both bodies of evidence is narrow: agentic TDD buys a
durable, executable contract and regression detection, not the design
benefit that justifies TDD for a human. This kit's Red evidence and stub
probe are built to capture exactly that narrow claim, cheaply, while
declining the structural context-split fix and any process prescription that
would re-introduce the "trust the agent's self-report" failure this guide's
evidence argues against.

---

## Sources

- Birgitta Böckeler (Thoughtworks / Martin Fowler) — *TDD inside the agent loop — theater or actual value?*: https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html
- *TDAD: Test-Driven Agentic Development — Reducing Code Regressions*: https://arxiv.org/pdf/2603.17973
- *TDD Governance for Multi-Agent Code Generation via Prompt Engineering*: https://arxiv.org/html/2604.26615v1
- alexop.dev — *A Claude Code TDD Skill: Forcing Red-Green-Refactor Discipline*: https://alexop.dev/posts/custom-tdd-workflow-claude-code-vue/
- Simon Willison — *Red/green TDD — Agentic Engineering Patterns*: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/

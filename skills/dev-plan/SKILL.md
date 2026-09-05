---
name: dev-plan
description: Turn an intent or spec into a staged, testable implementation plan written to the working repo's docs/plans/. Each stage has a goal, tasks, affected files, an acceptance check, and a validation command. Ordered least-to-most complex.
---

# plan

Use this when a feature or change is described in intent form (an idea, a spec,
or the output of `dev-brainstorm` / `dev-specify`) and is ready to be broken
into build stages.

## Discover first

Read `CLAUDE.md` / `AGENTS.md`, `README`, and the package/build manifest — or
dispatch a `code-explorer` subagent — to learn the repo's structure, its
test/lint/build commands, and its conventions. Bake in no fixed layout; the plan
must fit the repo as it actually is.

## Output

Write the plan to `docs/plans/<topic>.md` in the **working** repo (create the
directory if absent). Never edit the repo's `.gitignore`.

## Stage format

Order stages least → most complex, 3–7 of them. Each stage has:

- **Goal** — the concrete outcome.
- **Satisfies** — the requirement IDs (`R1, R2, …`) the stage covers; omit
  this field when the source spec has no requirement IDs.
- **Tasks** — numbered, actionable, granular enough to pick up without more
  questions.
- **Affected files** — exact paths; mark new ones `(new)`.
- **Acceptance check** — what "done" looks like, in testable terms.
- **Validation** — the discovered test/lint command to run for this stage.

## Quality bar

- Every stage answers "what does done look like?" If you can't write an
  acceptance check, the stage is under-specified.
- No affected file without a corresponding task.
- Flag assumptions and open questions explicitly — never silently invent
  requirements.

## Coherence gate

When the plan derives from a spec in `docs/specs/`, run this gate after the
plan is written and before handoff:

- **Coverage** — every requirement in the spec maps to at least one stage;
  list any orphans. On an unnumbered spec (the `dev-debug` exemption), check
  coverage against the spec's prose requirements instead of IDs.
- **Invention** — every stage traces to a requirement; list any extras.
- **Contradiction** — plan choices that conflict with the spec or the repo's
  constitution.
- **Testability** — an acceptance check that can't be phrased as a failing
  test means the requirement is under-specified.

Coverage or invention gaps route back to the skill that wrote the spec
(`dev-brainstorm`, `dev-specify`, or `dev-debug`), not into the plan.
Testability failures are fixed in the **spec**, not worked around in the
plan.

## Handoff

Once the plan passes the coherence gate (skip the gate for plans with no
source spec), the `dev-implement` skill drives it stage-by-stage.

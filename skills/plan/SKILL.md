---
name: plan
description: Turn an intent or spec into a staged, testable implementation plan written to the working repo's docs/plans/. Each stage has a goal, tasks, affected files, an acceptance check, and a validation command. Ordered least-to-most complex.
---

# plan

Use this when a feature or change is described in intent form (an idea, a spec,
or the output of `brainstorm`) and is ready to be broken into build stages.

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

## Handoff

Once the plan is written, the `implement` skill drives it stage-by-stage.

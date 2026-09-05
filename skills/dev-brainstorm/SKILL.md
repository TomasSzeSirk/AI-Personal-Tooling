---
name: dev-brainstorm
description: Turn an idea into an approved design spec through interactive dialogue — explore context, clarify one question at a time, weigh approaches, present the design in sections for approval, then write the spec to the working repo's docs/specs/. Use before planning any non-trivial feature.
---

# brainstorm

Use this for any new feature or change described as an idea, before planning or
writing code.

## Hard gate

Do **not** write code, scaffold, or hand off to `dev-plan` until the user has
approved a presented design. This applies regardless of how simple the request
seems — a short design is fine, but it must be presented and approved.

## Steps

1. **Explore context** — read the relevant files, `README`, and recent commits
   (optionally dispatch a `code-explorer` subagent) to ground the discussion.
2. **Clarify** — ask questions **one at a time**; prefer multiple-choice; focus
   on purpose, constraints, and success criteria. If the request spans multiple
   independent subsystems, flag it and suggest decomposing into sub-projects
   before refining details.
3. **Approaches** — when weighing solutions, dispatch `design-explorer`
   (Agent tool, `subagent_type: design-explorer`) to generate 2–3 options with
   trade-offs; present them with your recommendation and reasoning.
4. **Present the design in sections** — architecture, components, data flow,
   error handling, testing — each scaled to its complexity. Get approval after
   each section before moving on.
5. **Write the spec** — save the approved design to the working repo's
   `docs/specs/<topic>.md` (create the directory if absent; never edit the
   repo's `.gitignore`). Number its requirements `R1, R2, …` so `dev-plan` can
   trace stages back to them.
6. **Hand off** — invoke the `dev-plan` skill to turn the spec into a staged plan.

## Principles

- One question at a time.
- YAGNI ruthlessly — cut unnecessary features from the design.
- Propose 2–3 alternatives before settling.
- Incremental approval — validate each section before the next.

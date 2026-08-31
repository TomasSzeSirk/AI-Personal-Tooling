---
name: implement
description: Drive a staged plan to completion — one stage-executor subagent per stage, each judged by plan-reviewer, with a bounded fix-or-redispatch loop and one commit per passed stage. Orchestrator never writes code itself.
---

# implement

Use this when a staged plan under `docs/plans/` is ready to build end to end with
automated review instead of manual per-stage checkpoints.

## Role

You (the main session) are the **orchestrator**. You never write implementation
code yourself — your only direct actions are dispatching subagents, committing
passed stages, and relaying outcomes. Read the plan end to end and create one
todo per stage.

## Branch first

Stages commit as they pass, so land them on a branch — never straight onto the
repo's default branch.

1. **Skip this if the user already decided** — they named a branch, told you to
   stay put, or the repo is already on a non-default branch that matches this
   work.
2. **Otherwise propose one**, derived from the plan's filename (a plan at
   `docs/plans/user-auth.md` → branch `user-auth`), matching the naming style of
   the repo's existing branches. Ask the user to confirm or rename it, and wait
   for the answer before the first dispatch.
3. **Ask outright** — one question, no guessing — when the name is genuinely
   unclear: several plans in flight, a plan filename that doesn't describe the
   change, or an existing branch that may or may not be the right one.
4. Create it from the current branch and report the name before stage 1.

## Per-stage loop

Stages are **strictly sequential** — each depends on the ones before it. For
each stage, in order:

1. **Dispatch a fresh `stage-executor`** (Agent tool, `subagent_type:
   stage-executor`) for **this stage only**. Pass the plan path and the stage
   name/number. Capture its report.
2. **Dispatch `plan-reviewer`** (Agent tool, `subagent_type: plan-reviewer`) on
   the real diff versus this stage. It returns one of `PASS`, `CODE_WRONG`, or
   `PLAN_WRONG`.
3. **Branch on the verdict:**
   - `PASS` → commit this stage (implementation only, **not** the plan file),
     then move to the next stage.
   - `CODE_WRONG` → dispatch a **fresh** `stage-executor` for the same stage with
     the findings as fix instructions, then re-review. **Bounded to 2 retries;**
     after that, stop and escalate to the user with the findings.
   - `PLAN_WRONG` → patch the plan per the reviewer's proposed wording, then
     dispatch a fresh executor and re-review. This counts against the 2-retry
     bound.
4. **Confirm** the executor marked the stage done in the plan file.

## Rules

- One **fresh, cold** subagent per attempt — never reuse contaminated context.
- One commit per passed stage, immediately after `PASS`.
- Relay each stage's outcome (pass / retries / escalation) to the user — subagent
  reports are not visible to them otherwise.

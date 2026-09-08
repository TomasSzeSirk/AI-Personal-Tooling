---
name: dev-implement
description: Drive a staged plan to completion — one stage-executor subagent per stage, each judged by plan-reviewer, with a bounded fix-or-redispatch loop and one commit per passed stage under the repo's commit policy. Orchestrator never writes code itself.
---

# implement

Use this when a staged plan under `docs/plans/` is ready to build end to end with
automated execution and review, pausing after each stage only for the user's
manual sign-off on the result — not for design or review checkpoints.

## Role

You (the main session) are the **orchestrator**. You never write implementation
code yourself — your only direct actions are dispatching subagents, landing
passed stages under the commit policy below, and relaying outcomes. Read the
plan end to end and create one todo per stage.

## Discover first

Read `CLAUDE.md` / `AGENTS.md` and `README` in the **working** repo before the
first dispatch. They carry the conventions every stage must respect, and they
are where this skill's commit policy is overridden.

**Commit policy.** The default is **`ask`**. The working repo overrides it by
stating a commit policy in its `CLAUDE.md` / `AGENTS.md`; read that as one of:

- **`ask`** *(default)* — after each `PASS`, show the user the stage's diff
  summary and the commit message you propose, and wait for their approval
  before committing. A rejection is a stop-and-ask, not a retry.
- **`auto`** — commit each passed stage without asking, then show the user the
  resulting commit (hash, message, `git show --stat`) and wait for their
  acknowledgement before dispatching the next stage.
- **`never`** — never commit. Leave the work in the tree, show the user the
  current uncommitted changes for this stage (`git status` / `git diff`), and
  wait for their acknowledgement before dispatching the next stage.

Report the policy in effect before stage 1 whenever it is not the default, so
the user knows what will happen without reading the config. If the repo's
wording is ambiguous, ask once — do not guess your way into an unapproved
commit.

**Verification pause.** Whatever the policy, every stage ends in a hard pause
before the next stage's executor is dispatched — this is a manual-verification
checkpoint, not just a status report, so the user can catch problems before
they compound across stages. What you show them depends on whether the stage
landed a commit: a commit (`auto`, or `ask` once approved) means show the
commit itself; no commit (`never`, or an `ask` still pending approval) means
show the current working-tree changes. Either way, do not proceed until the
user has actually responded — silence is not approval.

## Branch first

Stages land as commits as they pass, so build them on a branch — never straight
onto the repo's default branch. This holds under every commit policy, `never`
included.

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

## Resuming a part-built plan

A plan handed to you directly may already be part-built — you are often not the
session that wrote it. The stage markers say what actually happened, so read
them before dispatching anything:

- **Unmarked** → not started. Dispatch an executor.
- **`(IMPLEMENTED — awaiting review)`** → the code exists but no reviewer
  judged it. Dispatch `plan-reviewer` on it first; do not re-implement, and do
  not skip it as if it were finished.
- **`(DONE — …)`** → passed review and was committed. Skip it.

Resume at the first stage that isn't done. If the markers contradict the repo
(a stage marked done with no matching commit, or uncommitted work under a done
stage), say so and ask rather than guessing which is right.

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
   - `PASS` → commit this stage per the **commit policy** — implementation
     only, **not** the plan file. Replace the stage's `(IMPLEMENTED — awaiting
     review)` marker with `(DONE — YYYY-MM-DD)`. You own the done marker; the
     executor never sets it, and it marks the stage as *reviewed*, so set it
     under `never` too. Then take the **verification pause** described above
     and wait for the user's response before dispatching the next stage.
   - `CODE_WRONG` → dispatch a **fresh** `stage-executor` for the same stage with
     the findings as fix instructions, then re-review. **Bounded to 2 retries;**
     after that, stop and escalate to the user with the findings.
   - `PLAN_WRONG` → patch the plan per the reviewer's proposed wording, then
     re-check the patched stage against the spec — does it still cover the
     requirements it claims, and does the new wording contradict the spec or
     the repo's constitution? The plan the coherence gate approved is not the
     plan you are now building; a patch that drifts from the spec is invisible
     to every later stage review. If the patch reveals the **spec** was wrong,
     stop and ask the user — the spec is theirs, and you never edit it on your
     own judgment. Then dispatch a fresh executor and re-review. This counts
     against the 2-retry bound.
4. **Confirm** the executor marked the stage `(IMPLEMENTED — awaiting review)`
   before you judged it, and that your own done marker replaced it after `PASS`.

## Rules

- One **fresh, cold** subagent per attempt — never reuse contaminated context.
- One commit per passed stage, immediately after `PASS` — never batch several
  stages into one commit, and never commit against the policy in effect.
- Never dispatch a stage's executor before the previous stage's verification
  pause has gotten a response — the pause exists for the user, not for you to
  narrate past.
- Relay each stage's outcome (pass / retries / escalation) to the user — subagent
  reports are not visible to them otherwise.
- Never edit the spec yourself. A stage review may show the spec is wrong; that
  is a stop-and-ask, not a patch.
- The working repo's `CLAUDE.md` / `AGENTS.md` outranks this skill's defaults on
  anything it actually states — commit policy, commit-message style, how to
  document and test. Where it is silent, the defaults here apply.

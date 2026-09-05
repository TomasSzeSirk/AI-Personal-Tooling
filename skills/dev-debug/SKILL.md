---
name: dev-debug
description: Turn a reported error or error log into a confirmed root-cause diagnosis, then hand off to plan for a fix. Explore context → collect the error → classify and dispatch bug-diagnoser → present the diagnosis for approval → write it as a spec. Alternative entry point to the workflow for bugs instead of new features.
---

# debug

Use this instead of `dev-brainstorm` when the starting point is broken behavior —
an exception, a stack trace, a failing test, or "X should happen but Y
happens" — rather than a new feature idea.

## Hard gate

Do **not** write a fix, scaffold, or hand off to `dev-plan` until the user has
confirmed the diagnosed root cause. A wrong diagnosis produces a plan that
fixes the wrong thing — confirmation is not optional, even when the cause
looks obvious.

## Steps

1. **Collect the error** — if the user hasn't already provided one, ask for
   the error or error log verbatim: the exception/stack trace, the failing
   command's output, or a precise description of expected vs. actual
   behavior. Ask **one clarifying question at a time** for anything missing
   that's needed to reproduce it (repro steps, environment, how often it
   happens) — don't guess at gaps.
2. **Explore context** — read the relevant files, `CLAUDE.md`/`AGENTS.md`,
   and recent commits touching the affected area, to ground the
   investigation.
3. **Classify** — from the error and context, identify the affected
   subsystem/domain and the likely error class (e.g. logic bug, bad input
   handling, race condition, integration/config issue). This scopes the
   diagnosis instead of searching the whole repo blind.
4. **Diagnose** — dispatch `bug-diagnoser` (Agent tool, `subagent_type:
   bug-diagnoser`) with the error and the classification as scope. If the
   cause could plausibly sit in more than one subsystem, dispatch several in
   parallel, one hypothesis each, rather than one broad sweep.
5. **Present the diagnosis** — root cause, the evidence chain (`file:line`),
   and confidence (`confirmed` vs `hypothesis`), in the developer's terms:
   what condition causes the failure and why, not just where it surfaced. Get
   confirmation before proceeding. On a `hypothesis`-confidence diagnosis, say
   so explicitly and offer what would raise confidence (e.g. a repro run)
   before asking for confirmation.
6. **Write the diagnosis as a spec** — save the confirmed root cause,
   evidence, and desired resolved state (the error no longer reproduces,
   covered by a regression test) to the working repo's
   `docs/specs/<topic>.md` (create the directory if absent; never edit the
   repo's `.gitignore`). This is the same location and shape `dev-brainstorm`
   writes to, so it needs no special handling downstream. This spec needs no
   requirement numbering — one root cause and one resolved state is a single
   requirement, and an `R1` with no `R2` is ceremony.
7. **Hand off** — invoke the `dev-plan` skill on that spec to turn the confirmed
   diagnosis into a staged fix plan; `dev-implement` and `dev-review` then proceed
   exactly as they would for any other plan.

## Principles

- One question at a time.
- Root cause, not symptom — a fix aimed at where the error surfaced instead
  of why it happened will resurface elsewhere.
- Never treat a `hypothesis`-confidence diagnosis as fact — surface the
  uncertainty and let the developer decide whether to confirm, investigate
  further, or reproduce first.
- No fix code here — this skill only ends in a confirmed diagnosis and a
  written spec; `dev-plan`/`dev-implement` own the actual fix.

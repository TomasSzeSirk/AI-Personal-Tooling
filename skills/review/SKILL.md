---
name: review
description: Verify a change set then review it — run the project's test/lint/build commands, then dispatch code-reviewer and security-reviewer on the diff and collate ranked findings. No success claim without evidence.
---

# review

Use this when a change set or branch is ready to check before merging.

## Step 1 — Verify

Discover the project's **test, lint, and build commands** (from `CLAUDE.md` /
`AGENTS.md`, `README`, or the package/build manifest) and **run them**. Report
the real output. Any failure stops the flow and is surfaced immediately — never
claim the work is done or passing without the command output to prove it.

## Step 2 — Check the change against its spec

Skip this when the change has no source spec. Otherwise open the spec in
`docs/specs/` and the plan it produced, and walk the requirements against what
actually shipped:

- **Coverage** — every requirement is delivered by the change set, not merely
  assigned to a stage. A requirement two stages satisfy jointly is checked
  here as one behavior, which no single stage review could do.
- **Constraints** — each requirement's specifics survived into the code. A
  stage saying "hash passwords" passes its own review whether or not the spec
  named a particular algorithm; this is where that word gets compared.
- **Accumulated deviations** — executors report deviations stage by stage and
  each is accepted alone. Read them together against the spec.

Report anything missing or altered as a finding alongside the reviewers' own.
This is the only point where the whole change exists at once and the spec is
still the thing being compared against — every earlier check judged a stage
against the plan.

## Step 3 — Review

Dispatch `code-reviewer` and `security-reviewer` (Agent tool, `subagent_type:
code-reviewer` / `security-reviewer`) on the diff, in parallel.

## Step 4 — Collate

Merge the findings, ranked by severity and deduplicated across the two
reviewers. Present them to the user; the user decides which to fix.

## Notes

- The reviewers are read-only — this skill reports, it does not auto-fix.

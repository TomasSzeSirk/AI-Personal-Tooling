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

## Step 2 — Review

Dispatch `code-reviewer` and `security-reviewer` (Agent tool, `subagent_type:
code-reviewer` / `security-reviewer`) on the diff, in parallel.

## Step 3 — Collate

Merge the findings, ranked by severity and deduplicated across the two
reviewers. Present them to the user; the user decides which to fix.

## Notes

- The reviewers are read-only — this skill reports, it does not auto-fix.

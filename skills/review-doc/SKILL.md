---
name: review-doc
description: Review a technical decision document against the Doc Craft feature taxonomy — dispatch doc-reviewer on the document and collate ranked findings with file:line and a concrete fix. Reports only; it does not rewrite the document.
---

# review-doc

Use this when a design, decision, or assessment document is ready to check.

## Step 1 — Locate

Take the document path from the user. If none was given, ask for one — do not
guess at a file.

## Step 2 — Review

Dispatch `doc-reviewer` (Agent tool, `subagent_type: doc-reviewer`) on the
document path. It loads the taxonomy at
`~/.claude/skills/doc-craft/features-decision.md` itself.

## Step 3 — Collate

Present the findings ranked most-severe first, flat — the taxonomy is seven
features, too few for grouping to help. Deduplicate where one shortfall was
raised under two features. The user decides which to fix.

## Notes

- The reviewer is read-only — this skill reports, it does not auto-fix.
- Findings about unverifiable named instances or quoted sources are defects, not
  style notes. Surface them at the top rather than folding them into a summary.

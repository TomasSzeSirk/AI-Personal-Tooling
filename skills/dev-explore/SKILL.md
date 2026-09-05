---
name: dev-explore
description: Map and research a codebase — trace flows, answer where/how questions, understand unfamiliar code. Fans out read-only code-explorer subagents and synthesizes their findings. Re-runnable anytime, not a one-time setup.
---

# explore

Use this when you need to understand code you don't know: "where is X handled",
"how does Y work", tracing a flow end to end, or gathering context before
planning a change.

## How it works

For a research question, dispatch one or more `code-explorer` subagents
(Agent tool, `subagent_type: code-explorer`). For a broad question, split it by
area so several explorers run in parallel; each returns synthesized findings,
not file dumps.

## Dispatch guidance

- Give each explorer a **single focused question** and a scope hint.
- Prefer several narrow explorers over one broad one when sweeping a large area —
  they run in parallel and each stays in context.
- Pass along anything you already know so they don't re-derive it.

## Synthesize

Collate the explorers' findings into one answer with `file:line` pointers. Note
any contradictions or gaps between reports; dispatch a follow-up explorer to
resolve them if it matters.

## Notes

- Read-only — nothing here edits code.
- Cheap to re-run; `code-explorer`'s per-project memory makes repeat runs faster
  by skipping what's already mapped.

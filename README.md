# Agnostic Agentic Dev Kit

A self-contained, stack-agnostic set of Claude Code **skills** and **subagents**
for general-purpose development. It provides a full
`brainstorm → plan → implement → review` loop (with `explore` feeding brainstorm
and plan) that works in **any** repository, in any language, without depending on
the superpowers plugin. Every worker discovers the project's own conventions and
test/lint/build commands at runtime — nothing is hard-coded to a stack.

## Components

### Skills (workflows you invoke)

| Skill | Role |
|-------|------|
| `brainstorm` | Interactive: turn an idea into an approved design spec. Explore context → clarify one question at a time → weigh approaches → present design for approval → write spec to the working repo's `docs/specs/`. |
| `explore` | Map/research unfamiliar code — trace flows, answer where/how. Read-only; fans out `code-explorer` subagents. |
| `plan` | Turn a spec/intent into a staged, testable plan in the working repo's `docs/plans/`. |
| `implement` | Orchestrate a staged plan: one `stage-executor` per stage, each judged by `plan-reviewer`, bounded fix-or-redispatch loop. TDD enforced. |
| `review` | Verify (run the project's test/lint/build), then dispatch `code-reviewer` + `security-reviewer` on the diff and collate ranked findings. |

### Subagents (cold workers, dispatched via the Agent tool)

| Subagent | Role |
|----------|------|
| `design-explorer` | Returns 2–3 solution approaches with trade-offs + a recommendation. |
| `code-explorer` | Read-only research worker; returns findings, not file dumps. |
| `stage-executor` | Builds one plan stage, tests-first, minimal diff. |
| `plan-reviewer` | Judges a stage's diff vs the plan → `PASS` / `CODE_WRONG` / `PLAN_WRONG`. |
| `code-reviewer` | Correctness + over-engineering + quality findings on a diff. |
| `security-reviewer` | Trust-boundary / secrets / injection audit on a diff. |

## Install

Symlinks `skills/` and `agents/` into `~/.claude/`, so edits to this repo
propagate everywhere and `git pull` updates all repos at once.

- **Windows:** `pwsh -File install.ps1` (needs Developer Mode or admin for symlinks).
- **macOS/Linux:** `bash install.sh`

After installing, invoke the skills by name (`brainstorm`, `explore`, `plan`,
`implement`, `review`); the subagents are dispatched automatically by the skills.

## Notes for consumers

- `plan` writes to the **working** repo's `docs/plans/`, `brainstorm` to its
  `docs/specs/`. The kit never edits a target repo's `.gitignore` — add
  `docs/plans/` and `docs/specs/` there yourself if you want them uncommitted.
- Agent memory is **per-project**: subagents write to the working repo's
  `.claude/agent-memory/<agent>/` (via `memory: project`), shared through that
  repo's git.

## Validate

`bash validate.sh` (or `pwsh -File validate.ps1`) checks every skill/agent file
for complete frontmatter and the absence of stack-specific references.

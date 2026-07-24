# Agnostic Agentic Dev Kit

A self-contained, stack-agnostic set of Claude Code **skills** and **subagents**
for general-purpose development. Provides a full
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

The units live by type under the repo's `skills/` and `agents/`; this idea's
installer knows which ones it owns via `scripts/agnostic-agentic-dev-kit/units.txt`
and links (or copies) just those into `~/.claude/`.

- **Windows:** `pwsh -File scripts/agnostic-agentic-dev-kit/install.ps1`
  (needs Developer Mode or admin for live symlinks; otherwise it copies).
- **macOS/Linux:** `bash scripts/agnostic-agentic-dev-kit/install.sh`

After installing, invoke the skills by name (`brainstorm`, `explore`, `plan`,
`implement`, `review`); the subagents are dispatched automatically by the skills.

## Use from other CLIs

`scripts/agnostic-agentic-dev-kit/adapt.py` adapts this idea's units for
agentic CLIs other than Claude Code:

```
python scripts/agnostic-agentic-dev-kit/adapt.py codex [--dry-run]
```

- **Kimi CLI** needs nothing extra for skills — it already reads
  `~/.claude/skills`, so `install.ps1`/`install.sh` above covers it.
- **Skills are symlinked when the OS permits, and only then track source
  edits** — in copy mode (see below) re-run `adapt.py` after editing a skill,
  exactly like agents.
  **Agents are generated TOML — re-run `adapt.py` after editing any
  `agents/*.md`** for the change to reach `~/.codex/agents`.
- On Windows without Developer Mode (or admin), symlink creation is denied;
  `adapt.py` falls back to copying skills and says so in its output and final
  report — don't assume a symlink happened.
- Known wart: the `## Memory` section in an agent body survives into the
  generated Codex file but points at `.claude/agent-memory/`, which Codex does
  not provision.
- The Codex skills path (`~/.agents/skills`) is per official OpenAI docs; it
  has **not** been verified against an installed `codex` on this machine. If
  Codex doesn't pick up skills there, check your installed version's actual
  skills directory and adjust the `TARGETS` entry in `adapt.py`.
- opencode and Kimi **agent** emitters are not implemented — opencode's skills
  directory and Kimi's agent format are unverified, so `adapt.py` only
  supports `codex` today.

## Validate

`bash scripts/agnostic-agentic-dev-kit/validate.sh`
(or `pwsh -File scripts/agnostic-agentic-dev-kit/validate.ps1`) checks every unit
in `units.txt` for complete frontmatter and the absence of stack-specific
references.

## Notes for consumers

- `plan` writes to the **working** repo's `docs/plans/`, `brainstorm` to its
  `docs/specs/`. The kit never edits a target repo's `.gitignore` — add
  `docs/plans/` and `docs/specs/` there yourself if you want them uncommitted.
- Agent memory is **per-project**: subagents write to the working repo's
  `.claude/agent-memory/<agent>/` (via `memory: project`), shared through that
  repo's git.
- If installed in copy mode (no symlink permission), re-run the installer after
  editing any source skill/agent so the change reaches `~/.claude/`.

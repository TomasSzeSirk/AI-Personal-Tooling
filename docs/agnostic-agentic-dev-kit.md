# Agnostic Agentic Dev Kit

A self-contained, stack-agnostic set of Claude Code **skills** and **subagents**
for general-purpose development. Provides a full
`brainstorm → plan → implement → review` loop (with `explore` feeding brainstorm
and plan) that works in **any** repository, in any language, without depending on
the superpowers plugin. `debug` is an alternative entry point for the same loop:
instead of turning an idea into a design spec, it turns a reported error into a
confirmed root-cause diagnosis, written as a spec in the same shape — so it
converges on the same `plan → implement → review` stages as `brainstorm` does.
Every worker discovers the project's own conventions and test/lint/build
commands at runtime — nothing is hard-coded to a stack.

## Components

### Skills (workflows you invoke)

| Skill | Role |
|-------|------|
| `brainstorm` | Interactive: turn an idea into an approved design spec. Explore context → clarify one question at a time → weigh approaches → present design for approval → write spec to the working repo's `docs/specs/`. |
| `debug` | Interactive: turn a reported error/log into a confirmed root-cause diagnosis. Collect the error → explore context → classify → dispatch `bug-diagnoser` → present diagnosis for confirmation → write it as a spec, same location as `brainstorm`. Alternative entry point for bugs instead of new features. |
| `explore` | Map/research unfamiliar code — trace flows, answer where/how. Read-only; fans out `code-explorer` subagents. |
| `plan` | Turn a spec/intent into a staged, testable plan in the working repo's `docs/plans/`. |
| `implement` | Orchestrate a staged plan: one `stage-executor` per stage, each judged by `plan-reviewer`, bounded fix-or-redispatch loop. TDD enforced. |
| `review` | Verify (run the project's test/lint/build), then dispatch `code-reviewer` + `security-reviewer` on the diff and collate ranked findings. |

### Subagents (cold workers, dispatched via the Agent tool)

| Subagent | Role |
|----------|------|
| `design-explorer` | Returns 2–3 solution approaches with trade-offs + a recommendation. |
| `bug-diagnoser` | Traces a reported error to its root cause with an evidence chain, not just where it surfaced. |
| `code-explorer` | Read-only research worker; returns findings, not file dumps. |
| `stage-executor` | Builds one plan stage, tests-first, minimal diff. |
| `plan-reviewer` | Judges a stage's diff vs the plan → `PASS` / `CODE_WRONG` / `PLAN_WRONG`. |
| `code-reviewer` | Correctness + over-engineering + quality findings on a diff. |
| `security-reviewer` | Trust-boundary / secrets / injection audit on a diff. |

## Workflow

Two entry points converge on the same build loop. `brainstorm` starts from an
idea, `debug` starts from a reported error — both end by writing a spec-shaped
file, and everything downstream (`plan → implement → review`) doesn't care
which one produced it.

```mermaid
flowchart TD
    subgraph LEGEND["Legend"]
        direction LR
        L1(Skill)
        L2{{Subagent}}
        L3[(File to read)]
        L4[/Developer checkpoint/]
    end

    subgraph FEATURE["New feature path"]
        BS(brainstorm)
        BSA{{design-explorer}}
        BSG[/"Approve design, section by section"/]
        BS --> BSA --> BSG
    end

    subgraph BUGFIX["Bug fix path"]
        DBG(debug)
        DBGA{{bug-diagnoser}}
        DBGG[/"Confirm root cause"/]
        DBG --> DBGA --> DBGG
    end

    EXP(explore)
    EXPA{{code-explorer}}
    EXP --> EXPA
    EXPA -. optional context .-> BS
    EXPA -. optional context .-> DBG

    SPEC[("docs/specs/&lt;topic&gt;.md<br/>design spec or confirmed diagnosis")]
    BSG --> SPEC
    DBGG --> SPEC

    SPEC --> PLAN(plan)
    PLANFILE[("docs/plans/&lt;topic&gt;.md<br/>staged plan — read before implement")]
    PLAN --> PLANFILE
    PLANFILE --> IMPL(implement)

    subgraph STAGE["Per stage, sequential"]
        SE{{stage-executor}}
        PR{{"plan-reviewer<br/>PASS / CODE_WRONG / PLAN_WRONG"}}
        SE --> PR
        PR -- "CODE_WRONG or PLAN_WRONG (max 2 retries)" --> SE
    end

    IMPL --> SE
    PR -- PASS --> COMMIT[/"1 commit per passed stage — review the diff"/]
    COMMIT -- next stage --> SE
    PR -- retries exhausted --> ESC[/"Escalation — findings need manual intervention"/]
    COMMIT -- all stages done --> REV(review)

    subgraph REVIEWERS["Parallel review"]
        CR{{code-reviewer}}
        SR{{security-reviewer}}
    end

    REV --> CR
    REV --> SR
    RFIND[/"Ranked findings — developer decides what to fix"/]
    CR --> RFIND
    SR --> RFIND
```

### Output files a developer must read or supervise

| Artifact | Written by | Why it matters |
|----------|-----------|-----------------|
| `docs/specs/<topic>.md` | `brainstorm` (design) or `debug` (confirmed diagnosis) | `plan` treats this as ground truth — a wrong or unapproved spec produces a plan for the wrong thing. Both skills gate on your approval/confirmation before writing it. |
| `docs/plans/<topic>.md` | `plan` | The stage-by-stage contract `stage-executor` and `plan-reviewer` build and judge against. Read it before `implement` runs — everything after this point is largely automated. |
| One commit per passed stage | `implement` (after `plan-reviewer` returns `PASS`) | The actual reviewable diff — `implement` relays pass/retry/escalation status, but the commit itself is what to read. |
| Escalation report (in-conversation, not a file) | `implement`, after 2 failed retries on one stage | The bounded fix-or-redispatch loop gave up — this needs your judgment call, not another automatic retry. |
| Ranked findings (in-conversation, not a file) | `review` (`code-reviewer` + `security-reviewer`, collated) | Read-only — nothing is auto-fixed. You decide which findings to act on. |

## Examples

### New feature, full loop

> "I want to add per-user rate limiting to the public API."

`brainstorm` explores the API code, asks clarifying questions one at a time,
dispatches `design-explorer` for approaches, and presents the design in
sections. Once you approve it, it writes `docs/specs/rate-limiting.md` and
hands off to `plan`, which writes `docs/plans/rate-limiting.md`. Say "go ahead
and implement it" to run `implement`, which builds and commits stage by stage,
then `review` to get ranked findings before you merge.

**Supervise:** the design sections in `brainstorm`, `docs/plans/rate-limiting.md`
before `implement` starts, each stage's commit, and the final findings.

### Bug fix from an error log

> "This is failing — [paste stack trace]. Can you debug it?"

`debug` reads the trace, asks for anything missing to reproduce it, classifies
the affected subsystem, and dispatches `bug-diagnoser` to trace the failure
back to its root cause. It presents the root cause with its evidence chain and
a confidence level (`confirmed` vs `hypothesis`) — **you must confirm it**
before it writes `docs/specs/fix-<topic>.md`. From there the flow is identical
to the feature path: `plan → implement → review`.

**Supervise:** the confirmed root cause (the hard gate — a wrong diagnosis
plans a fix for the wrong thing), then the plan/commits/findings as above.

### Research only, no build

> "How does this repo validate JWTs on incoming requests?"

`explore` fans out one or more `code-explorer` subagents and returns a
synthesized answer with `file:line` references — nothing is written or
changed. Good for orienting before deciding whether a change is even needed.

**Supervise:** nothing — it's read-only; just read the answer.

### Resume from an existing spec or plan

> "Turn `docs/specs/rate-limiting.md` into a staged plan and implement it."

Skips `brainstorm`/`debug` entirely when a spec already exists (hand-written,
or left over from an earlier session) — go straight to `plan`, then
`implement`, then `review`.

**Supervise:** same as the full loop, minus the design/diagnosis approval step
since that already happened.

## Install

The units live by type under the repo's `skills/` and `agents/`; this idea's
installer knows which ones it owns via `scripts/agnostic-agentic-dev-kit/units.txt`
and links (or copies) just those into `~/.claude/`.

- **Windows:** `pwsh -File scripts/agnostic-agentic-dev-kit/install.ps1`
  (needs Developer Mode or admin for live symlinks; otherwise it copies).
- **macOS/Linux:** `bash scripts/agnostic-agentic-dev-kit/install.sh`

After installing, invoke the skills by name (`brainstorm`, `debug`, `explore`,
`plan`, `implement`, `review`); the subagents are dispatched automatically by
the skills.

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
- Agent memory is repointed at the target's own directory: `.claude/agent-memory/`
  becomes `.codex/agent-memory/` for Codex, or `.agents/memory/` for a target
  with no convention of its own. Memory needs no platform feature — the agent
  just reads and writes the directory with its file tools — so the path only has
  to be consistent. `adapt.py` **fails loud** if the source wording changes
  enough that the rewrite stops matching, rather than shipping an agent pointed
  at a directory the target never provisions.
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

- `plan` writes to the **working** repo's `docs/plans/`, `brainstorm` and
  `debug` both to its `docs/specs/` (a confirmed diagnosis is written in the
  same shape as a design spec, so `plan` needs no special-casing to consume
  it). The kit never edits a target repo's `.gitignore` — add `docs/plans/`
  and `docs/specs/` there yourself if you want them uncommitted.
- Agent memory is **per-project**: subagents write to the working repo's
  `.claude/agent-memory/<agent>/` (via `memory: project`), shared through that
  repo's git.
- If installed in copy mode (no symlink permission), re-run the installer after
  editing any source skill/agent so the change reaches `~/.claude/`.

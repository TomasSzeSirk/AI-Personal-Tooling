# AI Personal Tooling

Personal repository of Claude Code tooling — **skills**, **subagents**, and (in
time) **MCP servers** and **commands**. Files are organized **by type** at the
repo root; each coherent collection is an **idea**, documented one-per-file in
`docs/` and installed by its own per-idea installer under `scripts/`.

## Layout

| Path | Holds |
|------|-------|
| `skills/` | Skill definitions (`<name>/SKILL.md`), by type — pooled across ideas. |
| `agents/` | Subagent definitions (`<name>.md`), by type — pooled across ideas. |
| `scripts/<idea>/` | Per-idea `install` + `validate` scripts (`.ps1` + `.sh`) and a `units.txt` manifest listing the skills/agents that idea owns. |
| `mcp/<server>/` | MCP servers — a standard package per server (its own venv/deps), installed and registered per its docs rather than symlinked into `~/.claude/`. |
| `docs/<idea>.md` | Detail for one idea — what it is, its units, how to use it. |
| `docs/specs/`, `docs/plans/` | Working design specs and plans (gitignored). |

Claude Code loads skills and agents flat by type from `~/.claude/`, so the
by-type layout mirrors how they're consumed; ideas are a documentation- and
install-level grouping, not a directory one. A unit can belong to more than one
idea without duplication.

## Ideas

| Idea | Summary | Docs |
|------|---------|------|
| Agnostic Agentic Dev Kit | Stack-agnostic `brainstorm → plan → implement → review` loop (5 skills + 6 subagents) usable in any repo. | [docs/agnostic-agentic-dev-kit.md](docs/agnostic-agentic-dev-kit.md) |
| Doc Craft | A discovered feature taxonomy for technical decision documents, plus skills to write and review against it (3 skills + 1 subagent). | [docs/doc-craft.md](docs/doc-craft.md) |
| Gemini Web MCP | MCP server fronting Gemini Web Gems as tools — a second, web-grounded model inside your agent loop. | [docs/gemini-web-mcp.md](docs/gemini-web-mcp.md) |
| OKF | Language- and architecture-agnostic codebase mapper — pluggable parsers, a dependency digraph, and declarative cross-layer policy, vendorable into any repo. | [docs/okf.md](docs/okf.md) |

## Install an idea

Run that idea's installer; it links (or copies) just that idea's units into
`~/.claude/`:

- **Windows:** `pwsh -File scripts/<idea>/install.ps1`
- **macOS/Linux:** `bash scripts/<idea>/install.sh`

Validate an idea's units with `scripts/<idea>/validate.{ps1,sh}`.

For CLIs other than Claude Code (e.g. Codex), an idea may ship an `adapt.py`
that installs its skills into that CLI's own directory and generates that
CLI's agent format — see the Agnostic Agentic Dev Kit's
[`adapt.py`](scripts/agnostic-agentic-dev-kit/adapt.py) usage in its
[docs](docs/agnostic-agentic-dev-kit.md#use-from-other-clis).

## Adding a new idea

1. Add its skills to `skills/` and agents to `agents/` (by type).
2. Create `scripts/<idea>/` with `units.txt` (paths it owns) + `install`/`validate`
   scripts (copy an existing idea's — they read `units.txt`).
3. Write `docs/<idea>.md` and add a row to the **Ideas** table above.

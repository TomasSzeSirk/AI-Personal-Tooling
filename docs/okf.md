# OKF (Organizational Knowledge Format)

**Version:** 1.0

A language- and architecture-agnostic codebase mapper. It walks a repo's
source roots, parses each file with a pluggable per-language parser, and
renders a **digraph** of nodes (one per file) — forward dependency edges,
their inversion (reverse edges), submodules, and test-coverage edges — as
markdown shards under `docs/okf/`. An optional declarative policy in
`okf.toml` flags cross-layer dependency edges as `⚠` violations, without any
code enforcing a specific architecture — the policy is data, not code.

## Model

- **Node** — one per source file: `rel` path, language, `domain` (first path
  segment under its root), optional `layer` (if `layer_rule`s assign one),
  `defines` (its public API surface), `depends_on`/`depended_on_by` (resolved
  internal edges), `external` (third-party deps), `submodules`, `tested_by`,
  and `violations`.
- **Digraph resolution** — each parser gives a file a canonical `module_id`
  and returns its imports as ids in that namespace. The engine builds a
  `module_id → node` index, resolves each import by longest-prefix match, and
  inverts forward edges to fill in reverse edges. Resolution is best-effort
  per language; unresolved imports are dropped, not errors.
- **Pluggable parsers** — Rust, Python, TypeScript, and Go today, each
  behind the same interface (`module_id`, `internal_imports`,
  `external_deps`, `defines`, `submodules`, `test_imports`). Unknown
  extensions are skipped and counted, not errors.
- **`tested_by` overlay** — test files (inline `mod tests` for Rust,
  `test_*.py`/`*_test.py` for Python, `*.test.ts`/`*.spec.ts` for TypeScript,
  `*_test.go` for Go, plus sibling test dirs) are resolved to the nodes they
  reference and recorded in `tested_by`. This overlay never touches
  `depends_on`/`depended_on_by` or policy input.
- **Declarative architecture policy** — `okf.toml`'s `[[layer_rule]]`
  entries assign each file a `layer` by glob (first match wins). An optional
  `[policy]` table compiles into a directed layer allow-list of one of five
  kinds: `inward`/`outward`/`downward` (directional along an `order` list),
  `isolate` (domains can't cross-depend except via `shared` layers), or
  `allowlist` (explicit `[from, to]` pairs). Every internal edge a node's
  policy forbids is recorded in `violations` and rendered as `⚠`.

## `setup.py` — vendor into a repo

```
python scripts/okf/setup.py --target <repo> [--source ...] [--output ...] [--with-hook] [--dry-run]
```

- Copies the mapper package (`map/model/config/classify/policy/graph/
  tests_overlay/render/prune/storage.py` + `parsers/`) into
  `<target>/scripts/okf/mapper/`.
- Writes `<target>/okf.toml` as a commented stub, only if absent — never
  clobbers a tuned config.
- Injects an "Architecture Recall (OKF map)" section into `<target>/AGENTS.md`
  between `<!-- okf:start -->`/`<!-- okf:end -->` markers (creates the file
  if absent, replaces the section if present, appends once otherwise). Fails
  loud on a mismatched marker pair rather than double-injecting.
- Runs an initial map generation and prints the summary.
- `--with-hook` adds a `.pre-commit-config.yaml` entry that regenerates the
  map on commit — opt-in only, not the default (see below).
- `--dry-run` prints the planned actions and writes nothing. Never touches
  `.gitignore`.

Re-running `setup.py --target <repo>` is idempotent: it re-vendors the
mapper, leaves an existing `okf.toml` alone, and leaves exactly one AGENTS.md
section.

## `okf.toml` schema

```toml
source = ["src"]        # string or list of source roots (default ["src"])
output = "docs/okf"      # map output dir (default "docs/okf")
ignore = []               # glob patterns to skip, in addition to SKIP_DIRS

[[layer_rule]]
glob = "domain/**"
layer = "domain"
[[layer_rule]]
glob = "adapter/**"
layer = "adapter"

[policy]
kind = "inward"           # inward | outward | downward | isolate | allowlist
order = ["domain", "adapter"]   # for inward/outward/downward
# shared = ["shared"]           # for isolate
# allow = [["adapter", "domain"]]  # for allowlist
```

A `policy` layer never assigned by any `layer_rule` produces a warning (not
fatal) when the config loads. Absent `okf.toml` yields the defaults above,
no policy, no layers.

## Running the mapper directly

```
python scripts/okf/mapper/map.py [--source ...] [--output ...] [--quiet] [--no-prune]
python scripts/okf/mapper/map.py --self-test
python scripts/okf/mapper/map.py --version
```

`--self-test` runs the in-script `assert` suite covering config loading,
each parser, digraph resolution, policy checks, the `tested_by` overlay, and
`setup.py`'s vendoring/injection — no test framework, no fixtures.

## The `okf` skill

`skills/okf/SKILL.md` regenerates the map and walks it shard-by-shard
(`docs/okf/index.md` → `docs/okf/<domain>/_index.md` → individual node
`.md`s), surfacing `⚠` violations as judgment candidates rather than
verdicts, and points at `setup.py` if the repo isn't vendored yet. Install it
with `scripts/okf/install.ps1` (Windows) or `scripts/okf/install.sh`
(macOS/Linux) — a single skill, linked (or copied) directly into
`~/.claude/skills/okf`, no `units.txt`.

## Regeneration is manual

There is no default hook regenerating the map — it's manual or
skill-driven (`python scripts/okf/mapper/map.py`, or invoke the `okf` skill). Add
`--with-hook` at setup time only if you want a pre-commit hook doing it
automatically.

## Changelog

- **1.0** (2026-07-24) — initial: pluggable parsers (rust/python/typescript/go),
  digraph (forward+reverse edges, submodules, tested_by), declarative
  architecture policy, setup + skill.

## Architecture Recall (OKF map)

Before broad architecture work or review, read `{output}/index.md` — a tiny
root index listing the domains with node/edge/violation counts and a link to
each domain's shard. Open `{output}/<domain>/_index.md` for that domain's
table (one row per file under `{source}` with its `layer` if configured,
dependency counts, and a `⚠` cross-layer-leak flag) — you load one domain, not
the whole repo. Drill into `{output}/<node>.md` for a single file's
`depends_on`/`external` instead of opening the source. This keeps context
small — read the shard, not every file.

There is no default hook regenerating this map. Regenerate manually (or via
the `okf` skill) with `python scripts/okf/mapper/map.py --source {source} --output
{output}`. Treat `⚠` flags as candidates for judgment, not verdicts.

Each node carries a `defines` list — its public API surface (exported
types/functions, language-dependent). It is parsed deterministically from
source on every map run: no LLM, no cache, nothing to go stale, nothing that
can block a commit. `depends_on` + `external` + `layer` already encode the
file's role, so `defines` adds the one signal not derivable from them — the
names of what the file exposes.

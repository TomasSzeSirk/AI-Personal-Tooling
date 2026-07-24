---
name: okf
description: Regenerate and consult a repo's OKF architecture map (docs/okf/) — nodes, dependency digraph, and declarative-policy violations. Use before broad architecture work or review, or when asked about a codebase's structure/dependencies.
---

# okf

Use this when you need an up-to-date map of a repo's file dependency graph —
before broad architecture work, before review, or to answer "what depends on
X" / "does this leak across layers" without reading every source file.

## Step 1 — Check the repo is set up

Look for `okf.toml` at the repo root and `scripts/okf/` in the working repo.
If either is missing, this repo hasn't vendored OKF yet — point the user at
`python scripts/okf/setup.py --target .` (run from wherever OKF's own repo
lives) rather than improvising a map by hand.

## Step 2 — Regenerate

Run `python scripts/okf/map.py` (add `--source`/`--output` if `okf.toml` sets
non-default roots — otherwise it reads `okf.toml` on its own). This is
deterministic, source-parsed, and cheap; there's no cache to go stale, so
always regenerate before trusting the map, don't rely on a stale `docs/okf/`.

## Step 3 — Consult, shard by shard

Don't read every node. Start at `docs/okf/index.md` — domain counts and
language mix. Drill into `docs/okf/<domain>/_index.md` for the domain you
care about (one row per file, `layer` if configured, dependency counts, a
`⚠` column). Only open `docs/okf/<node>.md` for a single file's
`depends_on`/`depended_on_by`/`external`/`tested_by` when you need that
file's specifics.

## Step 4 — Treat `⚠` as a candidate, not a verdict

A `⚠` flags a dependency edge the configured policy (`inward`/`outward`/
`downward`/`isolate`/`allowlist`) forbids. Surface it to the user or the
reviewer as something to look at — it may be a real layering leak, or an
intentional exception the policy doesn't yet encode. Don't auto-"fix" it by
editing code or `okf.toml` without asking.

## Notes

- The map is best-effort per language (four parsers: Rust, Python,
  TypeScript, Go) — unresolved imports are silently dropped, not errors.
- `tested_by` is a separate overlay; it never affects `depends_on` or
  `⚠` violations.

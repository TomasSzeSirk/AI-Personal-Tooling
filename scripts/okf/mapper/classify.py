"""Domain classification: map a repo-relative path to its owning domain, and
(opt-in) architecture layer assignment via `okf.toml` glob rules."""

from __future__ import annotations

import fnmatch
import os


def domain(rel: str, roots: list[str]) -> str:
    """First path segment under the file's root. A file directly in the root
    (no subdirectory) is domain "root".

    `rel` is repo-relative and always starts with the root's own basename
    (that's how `model.scan` builds it, regardless of whether `roots` holds
    relative or absolute paths) — so matching is done on root basenames, not
    the raw root strings."""
    rel = rel.replace("\\", "/")
    root_names = {os.path.basename(r.rstrip("/\\").replace("\\", "/")) for r in roots}
    parts = rel.split("/")
    if parts and parts[0] in root_names and len(parts) > 1:
        rest = parts[1:]
        return rest[0] if len(rest) > 1 else "root"
    return parts[0] if len(parts) > 1 else "root"


def assign_layer(rel: str, layer_rules: "list[dict] | None") -> "str | None":
    """Match `rel` against each `layer_rule`'s glob (first match wins). No
    rules, or no match -> None (unclassified — never a policy violation)."""
    if not layer_rules:
        return None
    rel = rel.replace("\\", "/")
    for rule in layer_rules:
        if fnmatch.fnmatch(rel, rule["glob"]):
            return rule["layer"]
    return None

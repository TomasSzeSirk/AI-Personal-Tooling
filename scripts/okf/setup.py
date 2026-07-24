"""Vendor OKF into a target repo — idempotent, re-runnable.

Usage: python setup.py --target <repo> [--source ...] [--output ...]
                        [--with-hook] [--dry-run]
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Runnable directly as `python setup.py` (dev) or `python scripts/okf/setup.py`
# (repo/vendored layout): put the parent of okf/ on sys.path so `okf` and
# `okf.map` import the same way in both cases.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from okf import __version__  # noqa: E402
from okf import config as config_mod  # noqa: E402
from okf import map as map_mod  # noqa: E402


class SetupError(Exception):
    pass


MARKER_START = "<!-- okf:start -->"
MARKER_END = "<!-- okf:end -->"

# Vendored as-is into <target>/scripts/okf/. setup.py, AGENTS-okf.md,
# install.*, units.txt are intentionally excluded (this list names only what
# gets copied).
VENDOR_MODULES = [
    "__init__.py",
    "map.py",
    "model.py",
    "config.py",
    "classify.py",
    "policy.py",
    "graph.py",
    "tests_overlay.py",
    "render.py",
    "prune.py",
    "storage.py",
]


def vendor(target: Path, dry_run: bool) -> list[str]:
    src_dir = Path(__file__).resolve().parent
    dest_dir = target / "scripts" / "okf"
    actions = []

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "parsers").mkdir(parents=True, exist_ok=True)

    for name in VENDOR_MODULES:
        actions.append(f"vendor: {name}")
        if not dry_run and (src_dir / name).resolve() != (dest_dir / name).resolve():
            shutil.copy2(src_dir / name, dest_dir / name)

    for parser_file in sorted((src_dir / "parsers").glob("*.py")):
        actions.append(f"vendor: parsers/{parser_file.name}")
        dest_file = dest_dir / "parsers" / parser_file.name
        if not dry_run and parser_file.resolve() != dest_file.resolve():
            shutil.copy2(parser_file, dest_file)

    return actions


def _config_stub(source: list[str], output: str) -> str:
    source_list = ", ".join(f'"{s}"' for s in source)
    return (
        f"# OKF config — vendored by okf {__version__}\n"
        f"source = [{source_list}]\n"
        f'output = "{output}"\n'
        "\n"
        "# Uncomment to assign layers (glob matched, first match wins):\n"
        "# [[layer_rule]]\n"
        '# glob = "domain/**"\n'
        '# layer = "domain"\n'
        "# [[layer_rule]]\n"
        '# glob = "adapter/**"\n'
        '# layer = "adapter"\n'
        "\n"
        "# Uncomment to enforce a layer policy\n"
        "# (kind: inward / outward / downward / isolate / allowlist):\n"
        "# [policy]\n"
        '# kind = "inward"\n'
        '# order = ["domain", "adapter"]\n'
    )


def write_config_stub(target: Path, source: list[str], output: str, dry_run: bool) -> list[str]:
    """Write okf.toml only if absent — never clobber a tuned policy."""
    toml_path = target / "okf.toml"
    if toml_path.exists():
        return []
    if dry_run:
        return [f"create: {toml_path}"]
    toml_path.write_text(_config_stub(source, output), encoding="utf-8")
    return [f"create: {toml_path}"]


def _agents_block(source: list[str], output: str) -> str:
    template_path = Path(__file__).resolve().parent / "AGENTS-okf.md"
    body = template_path.read_text(encoding="utf-8")
    body = body.replace("{source}", ", ".join(source)).replace("{output}", output)
    return f"{MARKER_START}\n{body.rstrip(chr(10))}\n{MARKER_END}\n"


def inject_agents_md(target: Path, source: list[str], output: str, dry_run: bool) -> list[str]:
    """Idempotent AGENTS.md injection: replace if markers present, append if
    the file exists without them, create otherwise. Fails loud on a partial
    marker pair rather than double-injecting."""
    agents_path = target / "AGENTS.md"
    block = _agents_block(source, output)

    if not agents_path.exists():
        if dry_run:
            return [f"create: {agents_path} (with OKF section)"]
        agents_path.write_text(block, encoding="utf-8")
        return [f"create: {agents_path}"]

    text = agents_path.read_text(encoding="utf-8")
    has_start = MARKER_START in text
    has_end = MARKER_END in text
    if has_start != has_end:
        raise SetupError(
            f"{agents_path}: mismatched OKF markers "
            f"(found {'start' if has_start else 'end'} without its pair)"
        )

    if has_start and has_end:
        start_i = text.index(MARKER_START)
        end_i = text.index(MARKER_END) + len(MARKER_END)
        tail = text[end_i:].lstrip("\n")
        new_text = text[:start_i] + block + (("\n" + tail) if tail else "")
        action = "replace"
    else:
        new_text = text.rstrip("\n") + "\n\n" + block
        action = "append"

    if dry_run:
        return [f"{action}: OKF section in {agents_path}"]
    agents_path.write_text(new_text, encoding="utf-8")
    return [f"{action}: OKF section in {agents_path}"]


def add_hook(target: Path, source: list[str], output: str, dry_run: bool) -> list[str]:
    """Opt-in only: add a pre-commit entry that regenerates the map."""
    hook_path = target / ".pre-commit-config.yaml"
    entry = (
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: okf-map\n"
        "        name: okf map regen\n"
        "        language: system\n"
        f"        entry: python scripts/okf/map.py --source {' '.join(source)} "
        f"--output {output} --quiet\n"
        "        pass_filenames: false\n"
    )

    if not hook_path.exists():
        if dry_run:
            return [f"create: {hook_path} (okf-map hook)"]
        hook_path.write_text("repos:\n" + entry, encoding="utf-8")
        return [f"create: {hook_path}"]

    text = hook_path.read_text(encoding="utf-8")
    if "id: okf-map" in text:
        return []  # already wired, idempotent no-op

    if dry_run:
        return [f"append: okf-map hook to {hook_path}"]
    hook_path.write_text(text.rstrip("\n") + "\n" + entry, encoding="utf-8")
    return [f"append: okf-map hook to {hook_path}"]


def setup_target(
    target: Path,
    source: list[str],
    output: str,
    with_hook: bool,
    dry_run: bool,
) -> dict:
    target = Path(target).resolve()
    actions: list[str] = []
    actions += vendor(target, dry_run)
    actions += write_config_stub(target, source, output, dry_run)
    actions += inject_agents_md(target, source, output, dry_run)
    if with_hook:
        actions += add_hook(target, source, output, dry_run)

    if dry_run:
        return {"status": "dry-run", "actions": actions}

    # Generate against whatever config now resolves for the target — honors a
    # pre-existing tuned okf.toml rather than the just-passed CLI defaults.
    cfg = config_mod.load(target / "okf.toml")
    roots = [str(target / r) for r in cfg.source]
    out_dir = str(target / cfg.output)
    result = map_mod.generate(
        roots, out_dir, prune=True, layer_rule=cfg.layer_rule, policy_cfg=cfg.policy,
    )
    return {"status": "ok", "actions": actions, "generate": result}


def main() -> int:
    import argparse
    import json

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Vendor OKF into a target repo.")
    parser.add_argument("--target", required=True, help="target repo root")
    parser.add_argument("--source", action="append", help="target source root (repeatable, default 'src')")
    parser.add_argument("--output", help="target map output dir (default 'docs/okf')")
    parser.add_argument("--with-hook", action="store_true", help="add a pre-commit hook that regenerates the map")
    parser.add_argument("--dry-run", action="store_true", help="print planned actions, write nothing")
    args = parser.parse_args()

    source = args.source or ["src"]
    output = args.output or "docs/okf"

    try:
        result = setup_target(Path(args.target), source, output, args.with_hook, args.dry_run)
    except SetupError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    for action in result["actions"]:
        print(action)
    if result["status"] == "dry-run":
        print("dry-run: no files written")
        return 0

    summary = {k: v for k, v in result["generate"].items() if k != "index_md"}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

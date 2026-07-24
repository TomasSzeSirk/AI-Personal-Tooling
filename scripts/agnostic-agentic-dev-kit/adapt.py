"""Adapt this repo's Claude agents/skills for use with other agentic CLIs.

Usage: python adapt.py <target> [--dry-run]
       python adapt.py --self-test
"""

from __future__ import annotations

import pathlib


class AdaptError(Exception):
    pass


def parse_agent(text: str, path: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise AdaptError(f"{path}: file must start with a '---' frontmatter line")

    fields: dict[str, str] = {}
    end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break
        if not line.strip():
            continue
        if line[0] in (" ", "\t"):
            raise AdaptError(f"{path}:{i + 1}: nested frontmatter line not supported")
        if line.lstrip().startswith("-"):
            raise AdaptError(f"{path}:{i + 1}: list frontmatter line not supported")
        if ":" not in line:
            raise AdaptError(f"{path}:{i + 1}: expected 'key: value'")
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()

    if end_index is None:
        raise AdaptError(f"{path}: missing closing '---' for frontmatter")

    body_lines = lines[end_index + 1 :]
    body = "\n".join(body_lines).lstrip("\n")

    if "name" not in fields:
        raise AdaptError(f"{path}: missing required frontmatter field 'name'")
    if "description" not in fields:
        raise AdaptError(f"{path}: missing required frontmatter field 'description'")

    return fields, body


_MODEL_REASONING_EFFORT = {"opus": "high", "sonnet": "medium"}


def emit_codex(fields: dict[str, str], body: str, path: str) -> str:
    name = fields["name"]
    description = fields["description"]
    for field_name, value in (("name", name), ("description", description)):
        if any(c in value for c in ('"', "\\", "\r", "\n")):
            raise AdaptError(
                f"{path}: {field_name} contains '\"', '\\\\', or a newline, cannot emit as TOML string"
            )
    if "'''" in body:
        raise AdaptError(f"{path}: body contains \"'''\", cannot emit as TOML literal string")

    lines = [f'name = "{name}"', f'description = "{description}"']

    effort = _MODEL_REASONING_EFFORT.get(fields.get("model"))
    if effort is not None:
        lines.append(f'model_reasoning_effort = "{effort}"')

    tools = fields.get("tools")
    if tools is not None:
        tokens = {t.strip() for t in tools.split(",")}
        if "Write" not in tokens and "Edit" not in tokens:
            lines.append('sandbox_mode = "read-only"')

    lines.append(f"developer_instructions = '''\n{body}\n'''")

    return "\n".join(lines) + "\n"


# Agent bodies tell the agent to read/write a per-project memory directory. That
# needs no platform feature — the agent just uses its file tools — so the path is
# ours to pick per target. It only has to be consistent and not collide.
DEFAULT_MEMORY_ROOT = ".agents/memory/"
_CLAUDE_MEMORY_ROOT = ".claude/agent-memory/"


def rewrite_memory(body: str, memory_root: str, path: str) -> str:
    """Repoint a Claude agent's memory prose at the target CLI's directory.

    Also drops the `memory: project` reference, since emit_* strips that
    frontmatter field and no other CLI has it.
    """
    body = body.replace("`memory: project` — writes go to", "Writes go to")
    body = body.replace(_CLAUDE_MEMORY_ROOT, memory_root)
    # Fail loud rather than shipping an agent pointed at a directory the target
    # never provisions: if the source prose is reworded, these literals stop
    # matching and the rewrite silently does nothing.
    for leftover in (".claude/", "memory: project"):
        if leftover in body:
            raise AdaptError(
                f"{path}: Claude-specific memory reference {leftover!r} survived the "
                f"rewrite — update rewrite_memory() to match the current wording"
            )
    return body


TARGETS = {
    "codex": {
        "skills": pathlib.Path("~/.agents/skills").expanduser(),
        "agents": pathlib.Path("~/.codex/agents").expanduser(),
        "ext": ".toml",
        "emit": emit_codex,
        "memory": ".codex/agent-memory/",
    },
}


def install(target_name: str, dry_run: bool) -> None:
    import shutil

    target = TARGETS[target_name]
    script_dir = pathlib.Path(__file__).resolve().parent
    root = script_dir.parent.parent
    units = [
        line.strip()
        for line in (script_dir / "units.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not dry_run:
        target["skills"].mkdir(parents=True, exist_ok=True)
        target["agents"].mkdir(parents=True, exist_ok=True)

    any_copied = False
    any_symlinked = False

    for unit in units:
        src = root / unit
        name = pathlib.Path(unit).name
        if unit.startswith("skills/"):
            dest = target["skills"] / name
            if dry_run:
                print(f"symlink: {unit}")
                continue
            if dest.exists() or dest.is_symlink():
                if dest.is_dir() and not dest.is_symlink():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            try:
                dest.symlink_to(src, target_is_directory=True)
                any_symlinked = True
                print(f"symlink: {unit}")
            except OSError:
                shutil.copytree(src, dest)
                any_copied = True
                print(f"copy: {unit}")
        elif unit.startswith("agents/"):
            stem = pathlib.Path(unit).stem
            dest = target["agents"] / f"{stem}{target['ext']}"
            text = src.read_text(encoding="utf-8")
            fields, body = parse_agent(text, str(src))
            body = rewrite_memory(body, target.get("memory", DEFAULT_MEMORY_ROOT), str(src))
            generated = target["emit"](fields, body, str(src))
            if dry_run:
                print(f"generate: {unit} -> {dest}")
                print(generated)
                continue
            dest.write_text(generated, encoding="utf-8")
            print(f"generate: {unit} -> {dest}")
        else:
            print(f"UNKNOWN unit: {unit}")
            continue

    if dry_run:
        return

    if any_symlinked:
        print("skills: symlinked (edits to sources propagate)")
    if any_copied:
        print("skills: copied (re-run after editing sources)")
    print("agents: generated (re-run after editing sources)")


def _self_test() -> None:
    good = """---
name: code-explorer
description: Read-only research worker.
tools: Read, Glob, Grep, Bash
model: sonnet
---

You are a read-only code investigator. You answer questions.
"""
    fields, body = parse_agent(good, "good.md")
    assert fields["name"] == "code-explorer"
    assert fields["tools"] == "Read, Glob, Grep, Bash"
    assert body.startswith("You are a read-only code investigator.")

    no_opening = "name: code-explorer\ndescription: x\n---\nbody\n"
    try:
        parse_agent(no_opening, "no_opening.md")
        assert False, "expected AdaptError for missing opening ---"
    except AdaptError:
        pass

    missing_name = """---
description: x
---

body
"""
    try:
        parse_agent(missing_name, "missing_name.md")
        assert False, "expected AdaptError for missing name"
    except AdaptError:
        pass

    nested = """---
name: x
description: y
  key: value
---

body
"""
    try:
        parse_agent(nested, "nested.md")
        assert False, "expected AdaptError for nested frontmatter"
    except AdaptError as e:
        assert ":4:" in str(e), f"expected line number in error, got: {e}"

    list_item = """---
name: x
description: y
  - item
---

body
"""
    try:
        parse_agent(list_item, "list_item.md")
        assert False, "expected AdaptError for list frontmatter"
    except AdaptError:
        pass

    read_only_fields = {"name": "x", "description": "y", "tools": "Read, Glob, Grep, Bash"}
    out = emit_codex(read_only_fields, "body", "x.md")
    assert 'sandbox_mode = "read-only"' in out

    write_fields = {"name": "x", "description": "y", "tools": "Read, Write, Edit, Glob, Grep, Bash"}
    out = emit_codex(write_fields, "body", "x.md")
    assert "sandbox_mode" not in out

    opus_fields = {"name": "x", "description": "y", "model": "opus"}
    out = emit_codex(opus_fields, "body", "x.md")
    assert 'model_reasoning_effort = "high"' in out

    sonnet_fields = {"name": "x", "description": "y", "model": "sonnet"}
    out = emit_codex(sonnet_fields, "body", "x.md")
    assert 'model_reasoning_effort = "medium"' in out

    other_model_fields = {"name": "x", "description": "y", "model": "gpt-9"}
    out = emit_codex(other_model_fields, "body", "x.md")
    assert "model_reasoning_effort" not in out

    try:
        emit_codex({"name": "x", "description": "y"}, "body with ''' inside", "x.md")
        assert False, "expected AdaptError for body containing '''"
    except AdaptError:
        pass

    try:
        emit_codex({"name": "x", "description": "back\\slash"}, "body", "x.md")
        assert False, "expected AdaptError for description containing backslash"
    except AdaptError:
        pass

    import tomllib

    hostile_body = 'line with \\backslash and `backtick` and "quote" and ${var}'
    hostile_fields = {"name": "x", "description": "y"}
    out = emit_codex(hostile_fields, hostile_body, "x.md")
    parsed = tomllib.loads(out)
    assert parsed["developer_instructions"] == hostile_body + "\n"

    repo_root = pathlib.Path(__file__).resolve().parents[2]
    for agent_path in sorted((repo_root / "agents").glob("*.md")):
        text = agent_path.read_text(encoding="utf-8")
        agent_fields, agent_body = parse_agent(text, str(agent_path))
        emitted = emit_codex(agent_fields, agent_body, str(agent_path))
        roundtripped = tomllib.loads(emitted)
        assert roundtripped["developer_instructions"] == agent_body + "\n", agent_path

    memory_src = (
        "## Memory\n\n"
        "`memory: project` — writes go to this repo's `.claude/agent-memory/code-explorer/`.\n"
    )
    rewritten = rewrite_memory(memory_src, ".codex/agent-memory/", "x.md")
    assert "`.codex/agent-memory/code-explorer/`" in rewritten
    assert "Writes go to this repo's" in rewritten
    assert ".claude/" not in rewritten
    assert "memory: project" not in rewritten

    assert rewrite_memory("no memory section here", DEFAULT_MEMORY_ROOT, "x.md")

    try:
        rewrite_memory("see `.claude/settings.json`", DEFAULT_MEMORY_ROOT, "x.md")
        assert False, "expected AdaptError for an unrewritten .claude/ reference"
    except AdaptError:
        pass

    # The invariant that matters: nothing Claude-specific about memory reaches a
    # generated agent, for every real agent in the repo.
    for agent_path in sorted((repo_root / "agents").glob("*.md")):
        text = agent_path.read_text(encoding="utf-8")
        agent_fields, agent_body = parse_agent(text, str(agent_path))
        agent_body = rewrite_memory(agent_body, ".codex/agent-memory/", str(agent_path))
        emitted = emit_codex(agent_fields, agent_body, str(agent_path))
        assert ".claude/" not in emitted, agent_path
        assert "memory: project" not in emitted, agent_path
        assert ".codex/agent-memory/" in emitted, agent_path
        tomllib.loads(emitted)

    print("self-test: OK")


def main() -> int:
    import argparse
    import sys

    # Windows consoles default stdout to cp1252, which can't encode characters
    # like the → and ✅ found in some agent bodies (e.g. agents/stage-executor.md).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Adapt Claude agents/skills for other CLIs.")
    parser.add_argument("target", nargs="?", help=f"one of: {', '.join(TARGETS)}")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        return 0

    if args.target is None:
        parser.print_usage(sys.stderr)
        return 1

    if args.target not in TARGETS:
        print(f"error: unknown target '{args.target}', valid targets: {', '.join(TARGETS)}", file=sys.stderr)
        return 1

    try:
        install(args.target, args.dry_run)
    except AdaptError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

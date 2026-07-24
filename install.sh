#!/usr/bin/env bash
# Symlink kit skills + agents into ~/.claude so they load in every repo.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
dest="$HOME/.claude"
mkdir -p "$dest/skills" "$dest/agents"
for d in "$root"/skills/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  ln -sfn "$d" "$dest/skills/$name"
  echo "linked skill: $name"
done
for f in "$root"/agents/*.md; do
  [ -e "$f" ] || continue
  name="$(basename "$f")"
  ln -sfn "$f" "$dest/agents/$name"
  echo "linked agent: $name"
done
echo "install: done"

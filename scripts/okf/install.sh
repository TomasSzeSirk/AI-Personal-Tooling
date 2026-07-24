#!/usr/bin/env bash
# Install the okf skill into ~/.claude/skills/okf.
# Prefers a symlink (edits propagate); falls back to copy when symlinks aren't
# permitted — re-run after edits in that case.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
target="$root/skills/okf"
dest="$HOME/.claude/skills"
mkdir -p "$dest"
link="$dest/okf"

rm -rf "$link"
if ln -sfn "$target" "$link" 2>/dev/null; then
  echo "symlink: skills/okf"
  echo "install: done (symlinked — edits to sources propagate automatically)"
else
  cp -R "$target" "$link"
  echo "copy: skills/okf"
  echo "install: done (copied — re-run after editing sources; symlinks were not permitted)"
fi

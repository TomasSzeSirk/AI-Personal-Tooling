#!/usr/bin/env bash
# Install this idea's units into ~/.claude (skills + agents listed in units.txt).
# Prefers symlinks (edits propagate); falls back to copy when symlinks aren't
# permitted — re-run after edits in that case.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
dest="$HOME/.claude"
mkdir -p "$dest/skills" "$dest/agents"
mode="symlink"

link_or_copy() { # $1=target $2=link
  rm -rf "$2"
  if ln -sfn "$1" "$2" 2>/dev/null; then echo symlink; else cp -R "$1" "$2"; echo copy; fi
}

while IFS= read -r unit; do
  [ -z "$unit" ] && continue
  name="$(basename "$unit")"
  case "$unit" in
    skills/*) how="$(link_or_copy "$root/$unit" "$dest/skills/$name")" ;;
    agents/*) how="$(link_or_copy "$root/$unit" "$dest/agents/$name")" ;;
    *)        echo "UNKNOWN unit: $unit"; continue ;;
  esac
  [ "$how" = copy ] && mode="copy"
  echo "$how: $unit"
done < "$here/units.txt"

if [ "$mode" = copy ]; then
  echo "install: done (copied — re-run after editing sources; symlinks were not permitted)"
else
  echo "install: done (symlinked — edits to sources propagate automatically)"
fi

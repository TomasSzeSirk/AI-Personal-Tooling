#!/usr/bin/env bash
# Install this idea's units into a *project's* .claude/ (skills + agents listed
# in units.txt) instead of the user-wide ~/.claude. Use this to scope the dev kit
# to one working repo — Claude Code loads project .claude/ on top of the user one.
#
#   install-local.sh [target-dir] [--link] [--dry-run]
#
# target-dir defaults to the current directory. Copies by default so the target
# repo stays self-contained (and the units can be committed there); --link
# symlinks back to this repo instead, so edits here propagate live.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
target="."
link=0
dry=0

for arg in "$@"; do
  case "$arg" in
    --link)    link=1 ;;
    --dry-run) dry=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    -*)        echo "UNKNOWN option: $arg" >&2; exit 2 ;;
    *)         target="$arg" ;;
  esac
done

[ -d "$target" ] || { echo "NOT a directory: $target" >&2; exit 2; }
target="$(cd "$target" && pwd)"
dest="$target/.claude"
if [ "$target" = "$root" ]; then
  echo "NOTE: target is this repo itself — installing into its own .claude/"
fi

install_unit() { # $1=source $2=destination
  if [ "$dry" -eq 1 ]; then return; fi
  rm -rf "$2"
  if [ "$link" -eq 1 ]; then ln -sfn "$1" "$2"; else cp -R "$1" "$2"; fi
}

[ "$dry" -eq 1 ] || mkdir -p "$dest/skills" "$dest/agents"

while IFS= read -r unit; do
  [ -z "$unit" ] && continue
  name="$(basename "$unit")"
  case "$unit" in
    skills/*) install_unit "$root/$unit" "$dest/skills/$name" ;;
    agents/*) install_unit "$root/$unit" "$dest/agents/$name" ;;
    *)        echo "UNKNOWN unit: $unit"; continue ;;
  esac
  echo "$([ "$link" -eq 1 ] && echo symlink || echo copy)$([ "$dry" -eq 1 ] && echo " (dry-run)"): $unit -> $dest/${unit%%/*}/$name"
done < "$here/units.txt"

if [ "$dry" -eq 1 ]; then
  echo "install-local: dry run — nothing written to $dest"
elif [ "$link" -eq 1 ]; then
  echo "install-local: done — symlinked into $dest (edits to $root propagate; don't commit these links)"
else
  echo "install-local: done — copied into $dest (re-run after editing sources)"
fi

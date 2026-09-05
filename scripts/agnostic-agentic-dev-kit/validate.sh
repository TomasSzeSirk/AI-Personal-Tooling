#!/usr/bin/env bash
# Validate this idea's units: frontmatter completeness, skill naming, and no
# stack-specific refs. Units are listed in units.txt (paths relative to repo root).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
forbidden='cargo|rustc|hexagonal|bit2|okf|merkle|rocksdb'
fail=0

check() {
  local f="$1"
  if [ ! -f "$f" ]; then echo "MISSING file: $f"; fail=1; return; fi
  grep -qE '^name:' "$f"        || { echo "MISSING name: $f"; fail=1; }
  grep -qE '^description:' "$f" || { echo "MISSING description: $f"; fail=1; }
  if grep -qiE "$forbidden" "$f"; then
    echo "FORBIDDEN stack ref in: $f"; grep -niE "$forbidden" "$f"; fail=1
  fi
}

# The command a developer types is the skill's *directory* name, so the
# frontmatter name must match it — otherwise the two drift and the docs describe
# a command that doesn't exist. The `dev-` prefix is what keeps these skills
# distinguishable from Claude Code's own built-in commands.
check_skill_name() {
  local unit="$1" dir name
  dir="$(basename "$unit")"
  case "$dir" in
    dev-*) ;;
    *) echo "SKILL DIR must start with 'dev-': $unit"; fail=1 ;;
  esac
  name="$(sed -n 's/^name:[[:space:]]*//p' "$root/$unit/SKILL.md" | head -n 1)"
  if [ "$name" != "$dir" ]; then
    echo "NAME MISMATCH in $unit/SKILL.md: frontmatter '$name' != directory '$dir'"
    fail=1
  fi
}

while IFS= read -r unit; do
  [ -z "$unit" ] && continue
  case "$unit" in
    skills/*) check "$root/$unit/SKILL.md"; check_skill_name "$unit" ;;
    agents/*) check "$root/$unit" ;;            # agent file
    *)        echo "UNKNOWN unit: $unit"; fail=1 ;;
  esac
done < "$here/units.txt"

if [ "$fail" -eq 0 ]; then echo "validate: OK"; fi
exit "$fail"

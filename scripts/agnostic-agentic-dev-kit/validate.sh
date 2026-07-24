#!/usr/bin/env bash
# Validate this idea's units: frontmatter completeness + no stack-specific refs.
# Units are listed in units.txt (paths relative to repo root).
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

while IFS= read -r unit; do
  [ -z "$unit" ] && continue
  case "$unit" in
    skills/*) check "$root/$unit/SKILL.md" ;;   # skill dir -> its SKILL.md
    agents/*) check "$root/$unit" ;;            # agent file
    *)        echo "UNKNOWN unit: $unit"; fail=1 ;;
  esac
done < "$here/units.txt"

if [ "$fail" -eq 0 ]; then echo "validate: OK"; fi
exit "$fail"

#!/usr/bin/env bash
# Validate kit files: frontmatter completeness + no stack-specific refs.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
forbidden='cargo|rustc|hexagonal|bit2|okf|merkle|rocksdb'
fail=0
files=$(find "$root/agents" "$root/skills" -name '*.md' 2>/dev/null || true)
for f in $files; do
  # frontmatter must contain name: and description:
  if ! grep -qE '^name:' "$f"; then echo "MISSING name: $f"; fail=1; fi
  if ! grep -qE '^description:' "$f"; then echo "MISSING description: $f"; fail=1; fi
  # forbidden stack refs (case-insensitive)
  if grep -qiE "$forbidden" "$f"; then
    echo "FORBIDDEN stack ref in: $f"; grep -niE "$forbidden" "$f"; fail=1
  fi
done
if [ "$fail" -eq 0 ]; then echo "validate: OK"; fi
exit "$fail"

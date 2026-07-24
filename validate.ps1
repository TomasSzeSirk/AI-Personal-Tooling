# Validate kit files: frontmatter completeness + no stack-specific refs.
$root = $PSScriptRoot
$forbidden = 'cargo|rustc|hexagonal|bit2|okf|merkle|rocksdb'
$fail = 0
$files = Get-ChildItem -Path "$root/agents","$root/skills" -Recurse -Filter *.md -ErrorAction SilentlyContinue
foreach ($f in $files) {
  $c = Get-Content $f.FullName -Raw
  if ($c -notmatch '(?m)^name:')        { Write-Output "MISSING name: $($f.FullName)"; $fail = 1 }
  if ($c -notmatch '(?m)^description:') { Write-Output "MISSING description: $($f.FullName)"; $fail = 1 }
  if ($c -match "(?i)$forbidden")       { Write-Output "FORBIDDEN stack ref in: $($f.FullName)"; $fail = 1 }
}
if ($fail -eq 0) { Write-Output "validate: OK" }
exit $fail

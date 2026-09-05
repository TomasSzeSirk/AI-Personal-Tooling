# Validate this idea's units: frontmatter completeness, skill naming, and no
# stack-specific refs. Units are listed in units.txt (paths relative to repo root).
$here = $PSScriptRoot
$root = Resolve-Path (Join-Path $here '../..')
$forbidden = 'cargo|rustc|hexagonal|bit2|okf|merkle|rocksdb'
$fail = 0

function Check([string]$f) {
  if (-not (Test-Path $f)) { Write-Output "MISSING file: $f"; $script:fail = 1; return }
  $c = Get-Content $f -Raw
  if ($c -notmatch '(?m)^name:')        { Write-Output "MISSING name: $f"; $script:fail = 1 }
  if ($c -notmatch '(?m)^description:') { Write-Output "MISSING description: $f"; $script:fail = 1 }
  if ($c -match "(?i)$forbidden")       { Write-Output "FORBIDDEN stack ref in: $f"; $script:fail = 1 }
}

# The command a developer types is the skill's *directory* name, so the
# frontmatter name must match it — otherwise the two drift and the docs describe
# a command that doesn't exist. The `dev-` prefix is what keeps these skills
# distinguishable from Claude Code's own built-in commands.
function Check-SkillName([string]$unit) {
  $dir = Split-Path $unit -Leaf
  if ($dir -notlike 'dev-*') {
    Write-Output "SKILL DIR must start with 'dev-': $unit"; $script:fail = 1
  }
  $skillMd = Join-Path $root "$unit/SKILL.md"
  if (-not (Test-Path $skillMd)) { return }
  $name = (Select-String -Path $skillMd -Pattern '^name:\s*(.+)$' | Select-Object -First 1).Matches.Groups[1].Value.Trim()
  if ($name -ne $dir) {
    Write-Output "NAME MISMATCH in $unit/SKILL.md: frontmatter '$name' != directory '$dir'"
    $script:fail = 1
  }
}

foreach ($unit in Get-Content (Join-Path $here 'units.txt')) {
  if ([string]::IsNullOrWhiteSpace($unit)) { continue }
  if     ($unit -like 'skills/*') { Check (Join-Path $root "$unit/SKILL.md"); Check-SkillName $unit }
  elseif ($unit -like 'agents/*') { Check (Join-Path $root $unit) }
  else   { Write-Output "UNKNOWN unit: $unit"; $fail = 1 }
}

if ($fail -eq 0) { Write-Output "validate: OK" }
exit $fail

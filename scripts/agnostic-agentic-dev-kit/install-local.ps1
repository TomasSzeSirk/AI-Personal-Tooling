# Install this idea's units into a *project's* .claude/ (skills + agents listed
# in units.txt) instead of the user-wide ~/.claude. Use this to scope the dev kit
# to one working repo — Claude Code loads project .claude/ on top of the user one.
#
#   install-local.ps1 [-Target <dir>] [-Link] [-DryRun]
#
# -Target defaults to the current directory. Copies by default so the target repo
# stays self-contained (and the units can be committed there); -Link symlinks back
# to this repo instead, so edits here propagate live (needs Developer Mode/admin).
param(
  [string]$Target = '.',
  [switch]$Link,
  [switch]$DryRun
)

$here = $PSScriptRoot
$root = (Resolve-Path (Join-Path $here '../..')).Path
if (-not (Test-Path $Target -PathType Container)) { Write-Error "NOT a directory: $Target"; exit 2 }
$targetPath = (Resolve-Path $Target).Path
$dest = Join-Path $targetPath '.claude'
if ($targetPath -eq $root) { Write-Output 'NOTE: target is this repo itself — installing into its own .claude/' }

function Install-Unit([string]$source, [string]$destination, [bool]$isDir) {
  if ($DryRun) { return }
  if (Test-Path $destination) { Remove-Item $destination -Force -Recurse }
  if ($Link) {
    New-Item -ItemType SymbolicLink -Path $destination -Target $source -ErrorAction Stop | Out-Null
  } elseif ($isDir) {
    Copy-Item $source $destination -Recurse -Force
  } else {
    Copy-Item $source $destination -Force
  }
}

if (-not $DryRun) {
  New-Item -ItemType Directory -Force -Path (Join-Path $dest 'skills'),(Join-Path $dest 'agents') | Out-Null
}

$how = if ($Link) { 'symlink' } else { 'copy' }
$suffix = if ($DryRun) { ' (dry-run)' } else { '' }

foreach ($unit in Get-Content (Join-Path $here 'units.txt')) {
  if ([string]::IsNullOrWhiteSpace($unit)) { continue }
  $name = Split-Path $unit -Leaf
  if     ($unit -like 'skills/*') { Install-Unit (Join-Path $root $unit) (Join-Path $dest "skills/$name") $true }
  elseif ($unit -like 'agents/*') { Install-Unit (Join-Path $root $unit) (Join-Path $dest "agents/$name") $false }
  else   { Write-Output "UNKNOWN unit: $unit"; continue }
  Write-Output "${how}${suffix}: $unit -> $dest"
}

if ($DryRun) {
  Write-Output "install-local: dry run — nothing written to $dest"
} elseif ($Link) {
  Write-Output "install-local: done — symlinked into $dest (edits to $root propagate; don't commit these links)"
} else {
  Write-Output "install-local: done — copied into $dest (re-run after editing sources)"
}

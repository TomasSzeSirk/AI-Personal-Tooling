# Install this idea's units into ~/.claude (skills + agents listed in units.txt).
# Prefers symlinks (edits propagate); falls back to copy when symlinks aren't
# permitted (Windows without Developer Mode/admin) — re-run after edits then.
$here = $PSScriptRoot
$root = Resolve-Path (Join-Path $here '../..')
$dest = Join-Path $HOME '.claude'
New-Item -ItemType Directory -Force -Path (Join-Path $dest 'skills'),(Join-Path $dest 'agents') | Out-Null
$mode = 'symlink'

function Link-Or-Copy([string]$target, [string]$link, [bool]$isDir) {
  if (Test-Path $link) { Remove-Item $link -Force -Recurse }
  try {
    New-Item -ItemType SymbolicLink -Path $link -Target $target -ErrorAction Stop | Out-Null
    return 'symlink'
  } catch {
    if ($isDir) { Copy-Item $target $link -Recurse -Force } else { Copy-Item $target $link -Force }
    return 'copy'
  }
}

foreach ($unit in Get-Content (Join-Path $here 'units.txt')) {
  if ([string]::IsNullOrWhiteSpace($unit)) { continue }
  $name = Split-Path $unit -Leaf
  if     ($unit -like 'skills/*') { $how = Link-Or-Copy (Join-Path $root $unit) (Join-Path $dest "skills/$name") $true }
  elseif ($unit -like 'agents/*') { $how = Link-Or-Copy (Join-Path $root $unit) (Join-Path $dest "agents/$name") $false }
  else   { Write-Output "UNKNOWN unit: $unit"; continue }
  if ($how -eq 'copy') { $mode = 'copy' }
  Write-Output "${how}: $unit"
}

if ($mode -eq 'copy') {
  Write-Output "install: done (copied — re-run after editing sources; enable Developer Mode for live symlinks)"
} else {
  Write-Output "install: done (symlinked — edits to sources propagate automatically)"
}

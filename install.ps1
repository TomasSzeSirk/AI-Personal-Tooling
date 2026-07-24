# Install kit skills + agents into ~/.claude.
# Prefers symlinks (edits propagate); falls back to copy when symlinks aren't
# permitted (Windows without Developer Mode/admin) — re-run after edits in that case.
$root = $PSScriptRoot
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

Get-ChildItem -Path (Join-Path $root 'skills') -Directory -ErrorAction SilentlyContinue | ForEach-Object {
  $how = Link-Or-Copy $_.FullName (Join-Path $dest "skills/$($_.Name)") $true
  if ($how -eq 'copy') { $mode = 'copy' }
  Write-Output "$how skill: $($_.Name)"
}
Get-ChildItem -Path (Join-Path $root 'agents') -Filter *.md -ErrorAction SilentlyContinue | ForEach-Object {
  $how = Link-Or-Copy $_.FullName (Join-Path $dest "agents/$($_.Name)") $false
  if ($how -eq 'copy') { $mode = 'copy' }
  Write-Output "$how agent: $($_.Name)"
}

if ($mode -eq 'copy') {
  Write-Output "install: done (copied — symlinks not permitted; re-run install.ps1 after editing sources, or enable Developer Mode for live symlinks)"
} else {
  Write-Output "install: done (symlinked — edits to sources propagate automatically)"
}

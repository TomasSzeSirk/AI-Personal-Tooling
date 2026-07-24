# Install the okf skill into ~/.claude/skills/okf.
# Prefers a symlink (edits propagate); falls back to copy when symlinks aren't
# permitted (Windows without Developer Mode/admin) — re-run after edits then.
$here = $PSScriptRoot
$root = Resolve-Path (Join-Path $here '../..')
$target = Join-Path $root 'skills/okf'
$dest = Join-Path $HOME '.claude/skills'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$link = Join-Path $dest 'okf'

if (Test-Path $link) { Remove-Item $link -Force -Recurse }
try {
  New-Item -ItemType SymbolicLink -Path $link -Target $target -ErrorAction Stop | Out-Null
  Write-Output "symlink: skills/okf"
  Write-Output "install: done (symlinked — edits to sources propagate automatically)"
} catch {
  Copy-Item $target $link -Recurse -Force
  Write-Output "copy: skills/okf"
  Write-Output "install: done (copied — re-run after editing sources; enable Developer Mode for live symlinks)"
}

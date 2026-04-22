$ErrorActionPreference = 'Stop'

$manifestPath = Join-Path $PSScriptRoot '..\..\manifests\workspaces\canonical_workspace.json'
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json

Write-Host "Canonical checkout: $($manifest.canonical_checkout)"
Write-Host ""

$paths = @()
$paths += $manifest.canonical_checkout
$paths += $manifest.junction_aliases
$paths += $manifest.legacy_local_only_paths

foreach ($path in $paths) {
  Write-Host "== $path =="
  if (!(Test-Path -LiteralPath $path)) {
    Write-Host "missing"
    Write-Host ""
    continue
  }

  $item = Get-Item -LiteralPath $path -Force
  if ($item.LinkType) {
    Write-Host "link_type: $($item.LinkType)"
    Write-Host "target: $($item.Target -join ', ')"
  } else {
    Write-Host "link_type: real-directory"
  }

  if (Test-Path -LiteralPath (Join-Path $path '.git')) {
    Push-Location -LiteralPath $path
    try {
      git status -sb
      git remote -v
      git log -1 --oneline
    } finally {
      Pop-Location
    }
  } else {
    Write-Host "git: no .git directory"
  }
  Write-Host ""
}

param(
  [switch]$PrintOnly
)

$Canonical = 'C:\Users\Admin\Workspace\Repos\FraWo'

if (!(Test-Path -LiteralPath $Canonical)) {
  throw "Canonical FraWo workspace not found: $Canonical"
}

$resolved = (Resolve-Path -LiteralPath $Canonical).Path
Write-Host "Canonical FraWo workspace: $resolved"

if ($PrintOnly) {
  return
}

Set-Location -LiteralPath $resolved
git status -sb

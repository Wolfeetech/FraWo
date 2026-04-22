param(
  [string]$Repository = 'Wolfeetech/FraWo',
  [string]$LabelsManifest = 'manifests\github\labels.json'
)

$ErrorActionPreference = 'Stop'
$Gh = & "$PSScriptRoot\get_gh.ps1"

& $Gh auth status | Out-Host
if ($LASTEXITCODE -ne 0) {
  throw 'GitHub CLI is not authenticated. Run scripts\github\bootstrap_gh_auth.ps1 first.'
}

$manifestPath = Join-Path (Get-Location) $LabelsManifest
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json

foreach ($label in $manifest.labels) {
  $name = [string]$label.name
  $color = [string]$label.color
  $description = [string]$label.description

  Write-Host "Ensuring label: $name"
  & $Gh label create $name `
    --repo $Repository `
    --color $color `
    --description $description `
    --force | Out-Host
}

Write-Host 'Labels synchronized.'

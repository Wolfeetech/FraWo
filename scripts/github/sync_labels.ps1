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

  $encodedName = [uri]::EscapeDataString($name)
  & $Gh api `
    --method PATCH `
    -H 'Accept: application/vnd.github+json' `
    -H 'X-GitHub-Api-Version: 2022-11-28' `
    "/repos/$Repository/labels/$encodedName" `
    -f "new_name=$name" `
    -f "color=$color" `
    -f "description=$description" *> $null

  if ($LASTEXITCODE -ne 0) {
    & $Gh api `
      --method POST `
      -H 'Accept: application/vnd.github+json' `
      -H 'X-GitHub-Api-Version: 2022-11-28' `
      "/repos/$Repository/labels" `
      -f "name=$name" `
      -f "color=$color" `
      -f "description=$description" | Out-Host
  }
}

Write-Host 'Labels synchronized.'

param(
  [string]$Repository = 'Wolfeetech/FraWo',
  [string]$IssueLabelsManifest = 'manifests\github\issue_labels_2026-04-22.json'
)

$ErrorActionPreference = 'Stop'
$Gh = & "$PSScriptRoot\get_gh.ps1"

& $Gh auth status | Out-Host
if ($LASTEXITCODE -ne 0) {
  throw 'GitHub CLI is not authenticated. Run scripts\github\bootstrap_gh_auth.ps1 first.'
}

$manifestPath = Join-Path (Get-Location) $IssueLabelsManifest
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json

foreach ($item in $manifest.issue_labels) {
  $issue = [int]$item.issue
  $labels = @($item.labels | ForEach-Object { [string]$_ })

  Write-Host "Setting labels on #${issue}: $($labels -join ', ')"
  & $Gh issue edit $issue --repo $Repository --add-label ($labels -join ',')
}

Write-Host 'Issue labels synchronized.'

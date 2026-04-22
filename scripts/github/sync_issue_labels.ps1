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

  $currentLabels = @(
    & $Gh issue view $issue `
      --repo $Repository `
      --json labels `
      --jq '.labels[].name'
  )

  $managedPrefixes = @('type:', 'status:', 'lane:', 'area:', 'needs:', 'risk:')
  $managedCurrentLabels = @(
    $currentLabels | Where-Object {
      $labelName = [string]$_
      ($managedPrefixes | Where-Object { $labelName.StartsWith($_) }).Count -gt 0
    }
  )

  $labelsToRemove = @($managedCurrentLabels | Where-Object { $labels -notcontains $_ })
  foreach ($labelToRemove in $labelsToRemove) {
    Write-Host "Removing label from #${issue}: $labelToRemove"
    & $Gh issue edit $issue --repo $Repository --remove-label $labelToRemove
  }

  if ($labels.Count -gt 0) {
    & $Gh issue edit $issue --repo $Repository --add-label ($labels -join ',')
  }
}

Write-Host 'Issue labels synchronized.'

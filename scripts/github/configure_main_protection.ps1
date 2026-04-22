param(
  [string]$Repository = 'Wolfeetech/FraWo',
  [string]$Branch = 'main',
  [switch]$StrictPullRequestMode
)

$ErrorActionPreference = 'Stop'

$Gh = & "$PSScriptRoot\get_gh.ps1"
Write-Host "Using gh: $Gh"

& $Gh auth status | Out-Host
if ($LASTEXITCODE -ne 0) {
  throw 'GitHub CLI is not authenticated. Run scripts\github\bootstrap_gh_auth.ps1 first.'
}

$requiredPullRequestReviews = $null
$requiredStatusChecks = $null

if ($StrictPullRequestMode) {
  $requiredPullRequestReviews = @{
    dismiss_stale_reviews = $true
    require_code_owner_reviews = $true
    required_approving_review_count = 1
    require_last_push_approval = $false
  }
  $requiredStatusChecks = @{
    strict = $true
    contexts = @(
      'Docs And Security Hygiene'
    )
  }
}

$payload = [ordered]@{
  required_status_checks = $requiredStatusChecks
  enforce_admins = $false
  required_pull_request_reviews = $requiredPullRequestReviews
  restrictions = $null
  required_linear_history = $false
  allow_force_pushes = $false
  allow_deletions = $false
  block_creations = $false
  required_conversation_resolution = $true
  lock_branch = $false
  allow_fork_syncing = $true
}

$payloadFile = Join-Path $env:TEMP "frawo-main-protection-$Branch.json"
$payloadJson = $payload | ConvertTo-Json -Depth 10
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($payloadFile, $payloadJson, $utf8NoBom)

Write-Host "Applying branch protection to $Repository/$Branch"
& $Gh api `
  --method PUT `
  -H 'Accept: application/vnd.github+json' `
  -H 'X-GitHub-Api-Version: 2022-11-28' `
  "/repos/$Repository/branches/$Branch/protection" `
  --input $payloadFile | Out-Host

if ($LASTEXITCODE -ne 0) {
  throw 'Branch protection API call failed.'
}

Write-Host ''
Write-Host 'Branch protection applied.'
Write-Host 'Mode:' ($(if ($StrictPullRequestMode) { 'strict PR mode' } else { 'solo-safe mode' }))

param(
  [switch]$ApplyBranchProtection,
  [switch]$StrictPullRequestMode
)

$ErrorActionPreference = 'Stop'

Write-Host '== GitHub CLI Auth =='
& "$PSScriptRoot\bootstrap_gh_auth.ps1"

Write-Host ''
Write-Host '== Labels =='
& "$PSScriptRoot\sync_labels.ps1"

Write-Host ''
Write-Host '== Issue Labels =='
& "$PSScriptRoot\sync_issue_labels.ps1"

if ($ApplyBranchProtection) {
  Write-Host ''
  Write-Host '== Main Branch Protection =='
  if ($StrictPullRequestMode) {
    & "$PSScriptRoot\configure_main_protection.ps1" -StrictPullRequestMode
  } else {
    & "$PSScriptRoot\configure_main_protection.ps1"
  }
} else {
  Write-Host ''
  Write-Host 'Branch protection not applied in this run. Add -ApplyBranchProtection when ready.'
}

Write-Host ''
Write-Host '== GitHub Setup Check =='
& "$PSScriptRoot\check_github_setup.ps1"

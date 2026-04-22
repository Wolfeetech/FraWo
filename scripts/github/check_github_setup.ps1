$ErrorActionPreference = 'Stop'

$Gh = & "$PSScriptRoot\get_gh.ps1"
Write-Host "Using gh: $Gh"

& $Gh --version
& $Gh auth status
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

Write-Host ''
Write-Host 'Repository:'
& $Gh repo view Wolfeetech/FraWo --json nameWithOwner,defaultBranchRef,url,visibility

Write-Host ''
Write-Host 'Open issues:'
& $Gh issue list --repo Wolfeetech/FraWo --limit 20

Write-Host ''
Write-Host 'Main branch protection:'
& $Gh api `
  -H 'Accept: application/vnd.github+json' `
  -H 'X-GitHub-Api-Version: 2022-11-28' `
  /repos/Wolfeetech/FraWo/branches/main/protection

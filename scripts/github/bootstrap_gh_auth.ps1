$ErrorActionPreference = 'Stop'

$Gh = & "$PSScriptRoot\get_gh.ps1"
Write-Host "Using gh: $Gh"

& $Gh --version

$oldErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$status = & $Gh auth status 2>&1
$statusExitCode = $LASTEXITCODE
$ErrorActionPreference = $oldErrorActionPreference

if ($statusExitCode -eq 0) {
  Write-Host $status
  Write-Host 'GitHub CLI is authenticated.'
  exit 0
}

Write-Host 'GitHub CLI is installed but not authenticated.'
Write-Host ''
Write-Host 'Run this interactive login from a normal PowerShell window:'
Write-Host ''
Write-Host '  gh auth login --hostname github.com --web --git-protocol https --scopes "repo,read:org,workflow"'
Write-Host ''
Write-Host 'After login, run:'
Write-Host ''
Write-Host '  powershell -ExecutionPolicy Bypass -File scripts\github\configure_main_protection.ps1'
exit 1

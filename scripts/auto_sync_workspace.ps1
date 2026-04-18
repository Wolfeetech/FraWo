param(
  [switch]$AutoCommit,
  [string]$CommitMessage = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$hostName = $env:COMPUTERNAME

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   FRAWO WORKSPACE SYNC" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "repo_root=$repoRoot"
Write-Host "host=$hostName"
Write-Host ""

Write-Host "[1/3] Sync with origin/main..." -ForegroundColor Yellow
git -C $repoRoot config pull.rebase false
git -C $repoRoot pull origin main --no-edit

Write-Host "`n[2/3] Current local status..." -ForegroundColor Yellow
$status = git -C $repoRoot status --short
if ($status) {
  $status | ForEach-Object { Write-Host $_ }
} else {
  Write-Host "working_tree=clean" -ForegroundColor Green
}

if (-not $AutoCommit) {
  Write-Host "`n[3/3] Auto-commit is disabled by default." -ForegroundColor Yellow
  Write-Host "Run with -AutoCommit to create a backup commit intentionally."
  exit 0
}

Write-Host "`n[3/3] Create intentional backup commit..." -ForegroundColor Yellow
git -C $repoRoot add -A
$postAddStatus = git -C $repoRoot status --short
if (-not $postAddStatus) {
  Write-Host "nothing_to_commit=true" -ForegroundColor Green
  exit 0
}

if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
  $CommitMessage = "chore(workstation): sync workspace from $hostName"
}

git -C $repoRoot commit -m $CommitMessage
git -C $repoRoot push origin main

Write-Host ""
Write-Host "status=ready" -ForegroundColor Green

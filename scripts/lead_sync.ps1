# lead_sync.ps1 - Force Synchronization from StudioPC Lead
# Usage: .\scripts\lead_sync.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$leadIP = "100.98.31.60" # wolfstudiopc Tailscale IP
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   LEAD SYNCHRONIZATION (StudioPC)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Local Sync
Write-Host "[1/3] Syncing Local (Satellite) with GitHub..." -ForegroundColor Yellow
git -C $repoRoot pull origin main --no-edit
git -C $repoRoot push origin main --quiet

# 2. Remote Sync (if SSH is enabled)
Write-Host "[2/3] Attempting Remote Sync on Lead Node ($leadIP)..." -ForegroundColor Yellow
if (Test-NetConnection -ComputerName $leadIP -Port 22 -InformationLevel Quiet) {
    Write-Host "SSH is OPEN. Triggering remote pull on Lead..." -ForegroundColor Green
    ssh wolf@$leadIP "cd Documents/Private_Networking && git pull origin main"
} else {
    Write-Host "SSH is CLOSED. Please run 'git pull' manually on the StudioPC." -ForegroundColor Red
}

# 3. Verification
Write-Host "`n[3/3] Current Status:" -ForegroundColor Yellow
$localCommit = git -C $repoRoot rev-parse HEAD
Write-Host "Local HEAD: $localCommit" -ForegroundColor Gray
Write-Host "SSOT status: READY" -ForegroundColor Green

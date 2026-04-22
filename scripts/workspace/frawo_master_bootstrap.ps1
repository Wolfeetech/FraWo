# frawo_master_bootstrap.ps1 - The one-click solution to unify a FraWo node
# This script ensures the machine adheres to the Lead-Satellite standard.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$canonicalRoot = "C:\Users\Admin\Workspace\Repos\FraWo"
$junctions = @("C:\WORKSPACE\FraWo", "C:\Users\Admin\Workspace\FraWo")
$legacyPath = "C:\Users\Admin\Documents\Private_Networking"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   FRAWO MASTER BOOTSTRAP (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Enable OpenSSH (Critical for AI access)
Write-Host "[1/4] Checking OpenSSH Server..." -ForegroundColor Yellow
$sshServer = Get-Service -Name sshd -ErrorAction SilentlyContinue
if ($null -eq $sshServer) {
    Write-Host "Installing OpenSSH Server..." -ForegroundColor Cyan
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
    $sshServer = Get-Service -Name sshd
}

if ($sshServer.Status -ne "Running") {
    Write-Host "Starting OpenSSH Server..." -ForegroundColor Cyan
    Set-Service -Name sshd -StartupType 'Automatic'
    Start-Service -Name sshd
    New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow | Out-Null
}
Write-Host "✅ OpenSSH Server is ACTIVE." -ForegroundColor Green

# 2. Verify / Create Canonical Path
Write-Host "[2/4] Verifying Canonical Root..." -ForegroundColor Yellow
if (-not (Test-Path $canonicalRoot)) {
    Write-Host "Creating canonical root directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $canonicalRoot -Force | Out-Null
    Write-Host "⚠️  Please clone the repository into $canonicalRoot manually if it's empty!" -ForegroundColor Yellow
}
Write-Host "✅ Canonical root: $canonicalRoot" -ForegroundColor Green

# 3. Establish Junctions
Write-Host "[3/4] Establishing Junctions..." -ForegroundColor Yellow
foreach ($j in $junctions) {
    if (Test-Path $j) {
        $item = Get-Item $j
        if ($item.Attributes -match "ReparsePoint") { Remove-Item $j -Force }
        else { Rename-Item $j ("$j.old." + (Get-Date -Format "yyyyMMdd")) }
    }
    $parent = Split-Path $j
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    New-Item -ItemType Junction -Path $j -Target $canonicalRoot | Out-Null
    Write-Host "🔗 Linked: $j -> $canonicalRoot" -ForegroundColor Gray
}

# 4. Cleanup Legacy Paths
Write-Host "[4/4] Cleaning up Legacy Paths..." -ForegroundColor Yellow
if (Test-Path $legacyPath) {
    $current = Get-Location
    if ($current.Path -like "$legacyPath*") {
        Write-Host "‼️  STILL IN LEGACY PATH. Please 'cd C:\WORKSPACE\FraWo' manually." -ForegroundColor Red
    } else {
        $lbackup = "$legacyPath.old." + (Get-Date -Format "yyyyMMdd")
        Rename-Item $legacyPath $lbackup
        New-Item -ItemType Junction -Path $legacyPath -Target $canonicalRoot | Out-Null
        Write-Host "✅ Legacy path archived and linked." -ForegroundColor Green
    }
}

Write-Host "`n🎉 Machine is now UNIFIED and READY for AI Operations." -ForegroundColor Green
Write-Host "Primary Path: C:\WORKSPACE\FraWo" -ForegroundColor Cyan

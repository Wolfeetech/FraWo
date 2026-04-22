# frawo_master_bootstrap.ps1 - The one-click solution to unify a FraWo node
# This script ensures the machine adheres to the Lead-Satellite standard.
# ASCII ONLY VERSION TO AVOID ENCODING ISSUES

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$canonicalRoot = "C:\Users\Admin\Workspace\Repos\FraWo"
if (-not (Test-Path $canonicalRoot)) {
    # Fallback for other users
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name.Split('\')[1]
    $canonicalRoot = "C:\Users\$currentUser\Workspace\Repos\FraWo"
}
# Final override if C:\WORKSPACE\FraWo already exists
if (Test-Path "C:\WORKSPACE\FraWo") {
    # If we are already in the unified path, use it as root
    $canonicalRoot = (Get-Item "C:\WORKSPACE\FraWo").Target
    if ($null -eq $canonicalRoot) { $canonicalRoot = "C:\WORKSPACE\FraWo" }
}

$junctions = @("C:\WORKSPACE\FraWo", "C:\Users\Admin\Workspace\FraWo")
$legacyPath = "C:\Users\Admin\Documents\Private_Networking"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   FRAWO MASTER BOOTSTRAP (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Enable OpenSSH
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
Write-Host "[OK] OpenSSH Server is ACTIVE." -ForegroundColor Green

# 2. Verify / Create Canonical Path
Write-Host "[2/4] Verifying Canonical Root..." -ForegroundColor Yellow
if (-not (Test-Path $canonicalRoot)) {
    Write-Host "Creating canonical root directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $canonicalRoot -Force | Out-Null
}
Write-Host "[OK] Canonical root: $canonicalRoot" -ForegroundColor Green

# 3. Establish Junctions
Write-Host "[3/4] Establishing Junctions..." -ForegroundColor Yellow
foreach ($j in $junctions) {
    if (Test-Path $j) {
        $item = Get-Item $j
        if ($item.Attributes -match "ReparsePoint") { Remove-Item $j -Force }
        else { 
            $b = "$j.old." + (Get-Date -Format "yyyyMMdd")
            if (-not (Test-Path $b)) { Rename-Item $j $b }
        }
    }
    $p = Split-Path $j
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
    if (-not (Test-Path $j)) {
        New-Item -ItemType Junction -Path $j -Target $canonicalRoot | Out-Null
    }
    Write-Host "Link: $j -> $canonicalRoot" -ForegroundColor Gray
}

# 4. Cleanup Legacy Paths
Write-Host "[4/4] Cleaning up Legacy Paths..." -ForegroundColor Yellow
if (Test-Path $legacyPath) {
    $current = Get-Location
    if ($current.Path -like "$legacyPath*") {
        Write-Host "!! STILL IN LEGACY PATH. Please 'cd C:\WORKSPACE\FraWo' manually." -ForegroundColor Red
    } else {
        $lb = "$legacyPath.old." + (Get-Date -Format "yyyyMMdd")
        if (-not (Test-Path $lb)) { Rename-Item $legacyPath $lb }
        New-Item -ItemType Junction -Path $legacyPath -Target $canonicalRoot | Out-Null
        Write-Host "[OK] Legacy path archived and linked." -ForegroundColor Green
    }
}

Write-Host "Unification complete. Machine is READY." -ForegroundColor Green
Write-Host "Primary Path: C:\WORKSPACE\FraWo" -ForegroundColor Cyan

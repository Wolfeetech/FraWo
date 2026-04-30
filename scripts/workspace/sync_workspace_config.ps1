# sync_workspace_config.ps1 - Erzwinge zentrale Workspace-Konfiguration
# Löscht lokale User-Settings und zwingt Repo-Settings

param(
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FraWo Workspace Config Sync" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detect OS
$isWindows = $PSVersionTable.Platform -eq 'Win32NT' -or $null -eq $PSVersionTable.Platform
$repoRoot = if ($isWindows) { "C:\WORKSPACE\FraWo" } else { "$HOME/workspace/FraWo" }

if (-not (Test-Path $repoRoot)) {
    Write-Host "ERROR: Repo not found at $repoRoot" -ForegroundColor Red
    exit 1
}

Set-Location $repoRoot

# 1. Git Pull - Hol die neueste zentrale Config
Write-Host "[1/5] Pulling latest config from Git..." -ForegroundColor Yellow
if (-not $DryRun) {
    git fetch origin main
    git pull origin main
    Write-Host "  ✓ Git pull completed" -ForegroundColor Green
} else {
    Write-Host "  [DRY RUN] Would run: git pull" -ForegroundColor Gray
}

# 2. Prüfe ob zentrale Config vorhanden ist
Write-Host ""
Write-Host "[2/5] Checking central config files..." -ForegroundColor Yellow

$centralFiles = @(
    ".vscode/settings.json",
    ".vscode/extensions.json",
    ".vscode/cspell.json",
    ".editorconfig",
    "FraWo.code-workspace"
)

$missingFiles = @()
foreach ($file in $centralFiles) {
    if (Test-Path (Join-Path $repoRoot $file)) {
        Write-Host "  ✓ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MISSING: $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: Central config files missing! Run 'git pull' first." -ForegroundColor Red
    exit 1
}

# 3. Lösche VS Code User Settings (NUR wenn -Force)
Write-Host ""
Write-Host "[3/5] Checking VS Code User Settings..." -ForegroundColor Yellow

$vscodeUserSettings = if ($isWindows) {
    "$env:APPDATA\Code\User\settings.json"
} else {
    "$HOME/.config/Code/User/settings.json"
}

if (Test-Path $vscodeUserSettings) {
    Write-Host "  Found User Settings: $vscodeUserSettings" -ForegroundColor Cyan

    if ($Force) {
        $backup = "$vscodeUserSettings.backup." + (Get-Date -Format "yyyyMMdd_HHmmss")
        if (-not $DryRun) {
            Copy-Item $vscodeUserSettings $backup
            Write-Host "  ✓ Backed up to: $backup" -ForegroundColor Green

            # Warnung anzeigen
            Write-Host ""
            Write-Host "  WARNING: User settings will be RESET!" -ForegroundColor Yellow
            Write-Host "  This will force the central repo settings." -ForegroundColor Yellow
            Write-Host ""
            $confirm = Read-Host "  Continue? (yes/no)"

            if ($confirm -ne "yes") {
                Write-Host "  Aborted by user." -ForegroundColor Red
                exit 1
            }

            Remove-Item $vscodeUserSettings -Force
            Write-Host "  ✓ User settings deleted (backup exists)" -ForegroundColor Green
        } else {
            Write-Host "  [DRY RUN] Would backup and delete User settings" -ForegroundColor Gray
        }
    } else {
        Write-Host "  User settings exist (use -Force to reset)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  No User settings found (good!)" -ForegroundColor Green
}

# 4. Lösche lokale .vscode Overrides im Repo
Write-Host ""
Write-Host "[4/5] Checking local .vscode overrides..." -ForegroundColor Yellow

$localVscodeOverrides = @(
    ".vscode/launch.json.local",
    ".vscode/.history",
    ".vscode/*.code-snippets"
)

foreach ($pattern in $localVscodeOverrides) {
    $files = Get-ChildItem -Path (Join-Path $repoRoot ".vscode") -Filter (Split-Path $pattern -Leaf) -ErrorAction SilentlyContinue

    foreach ($file in $files) {
        if (-not $DryRun) {
            Remove-Item $file.FullName -Recurse -Force
            Write-Host "  ✓ Removed: $($file.Name)" -ForegroundColor Green
        } else {
            Write-Host "  [DRY RUN] Would remove: $($file.Name)" -ForegroundColor Gray
        }
    }
}

if ($files.Count -eq 0) {
    Write-Host "  No local overrides found (good!)" -ForegroundColor Green
}

# 5. Installiere empfohlene Extensions
Write-Host ""
Write-Host "[5/5] Checking VS Code Extensions..." -ForegroundColor Yellow

$extensionsJson = Join-Path $repoRoot ".vscode/extensions.json"
if (Test-Path $extensionsJson) {
    $extensions = (Get-Content $extensionsJson | ConvertFrom-Json).recommendations

    Write-Host "  Recommended extensions: $($extensions.Count)" -ForegroundColor Cyan

    # Prüfe ob 'code' command verfügbar ist
    $codeCmd = Get-Command code -ErrorAction SilentlyContinue

    if ($codeCmd) {
        Write-Host ""
        Write-Host "  Run this to install all extensions:" -ForegroundColor Yellow
        Write-Host "  code --install-extension " -NoNewline -ForegroundColor Gray
        Write-Host ($extensions -join " --install-extension ") -ForegroundColor White
    } else {
        Write-Host "  'code' command not found - install extensions via VS Code UI" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Extensions list not found" -ForegroundColor Red
}

# Zusammenfassung
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sync Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No changes were made" -ForegroundColor Yellow
} else {
    Write-Host "✓ Config sync completed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Close VS Code completely" -ForegroundColor White
Write-Host "  2. Open workspace: code FraWo.code-workspace" -ForegroundColor White
Write-Host "  3. Install recommended extensions when prompted" -ForegroundColor White
Write-Host ""

if (-not $Force) {
    Write-Host "Tip: Use -Force to reset User settings to repo defaults" -ForegroundColor Gray
}

Write-Host ""

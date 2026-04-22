# force_unify_workspaces.ps1 - Unify all FraWo workspace paths
$canonicalRoot = "C:\Users\Admin\Workspace\Repos\FraWo"
$junctions = @("C:\WORKSPACE\FraWo", "C:\Users\Admin\Workspace\FraWo")
$legacyPath = "C:\Users\Admin\Documents\Private_Networking"

Write-Host "--- FRAWO WORKSPACE UNIFICATION ---" -ForegroundColor Cyan

foreach ($j in $junctions) {
    if (Test-Path $j) {
        $item = Get-Item $j
        if ($item.Attributes -match "ReparsePoint") {
            Remove-Item $j -Force
        } else {
            $backup = "$j.old." + (Get-Date -Format "yyyyMMdd")
            Rename-Item $j $backup
        }
    }
    $parent = Split-Path $j
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force }
    New-Item -ItemType Junction -Path $j -Target $canonicalRoot
}

if (Test-Path $legacyPath) {
    $current = Get-Location
    if ($current.Path -like "$legacyPath*") {
        Write-Host "WARNING: Still in legacy path. Switch to C:\WORKSPACE\FraWo soon." -ForegroundColor Yellow
    } else {
        $lbackup = "$legacyPath.old." + (Get-Date -Format "yyyyMMdd")
        Rename-Item $legacyPath $lbackup
        New-Item -ItemType Junction -Path $legacyPath -Target $canonicalRoot
    }
}
Write-Host "DONE." -ForegroundColor Green

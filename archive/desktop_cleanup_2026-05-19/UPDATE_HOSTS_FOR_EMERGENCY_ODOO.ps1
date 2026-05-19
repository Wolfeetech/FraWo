# PowerShell Script to Update Hosts File for Emergency Odoo
# RUN AS ADMINISTRATOR!

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Emergency Odoo - Hosts File Update" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Backup current hosts file
$backupPath = "C:\Users\$env:USERNAME\Desktop\hosts_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Copy-Item $hostsPath $backupPath -Force
Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
Write-Host ""

# Read current hosts file
$hostsContent = Get-Content $hostsPath

# Find and comment out Anker/Toolbox entries, add emergency redirect
$newContent = @()
$inAliasSection = $false
$aliasSection Added = $false

foreach ($line in $hostsContent) {
    if ($line -match "# --- Homeserver 2027 Internal Aliases ---") {
        $inAliasSection = $true
        $newContent += $line
        $newContent += "# ORIGINAL (Anker PVE / Toolbox - CURRENTLY OFFLINE)"
        continue
    }

    if ($line -match "# --- End Aliases ---") {
        if (!$aliasSection Added) {
            $newContent += ""
            $newContent += "# EMERGENCY REDIRECT (Stock PVE - Temporary while Anker is offline)"
            $newContent += "192.168.178.175 odoo.hs27.internal"
            $newContent += "# Other services remain offline until Anker PVE is restored"
            $newContent += ""
            $aliasSection Added = $true
        }
        $newContent += $line
        $inAliasSection = $false
        continue
    }

    if ($inAliasSection -and $line -match "100\.82\.26\.53") {
        # Comment out original Toolbox entries
        $newContent += "# $line"
    } else {
        $newContent += $line
    }
}

# Write updated content
$newContent | Set-Content $hostsPath -Force

Write-Host "[OK] Hosts file updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Yellow
Write-Host "  - Commented out all Toolbox (100.82.26.53) entries" -ForegroundColor Yellow
Write-Host "  - Added emergency redirect:" -ForegroundColor Yellow
Write-Host "    192.168.178.175 odoo.hs27.internal" -ForegroundColor Green
Write-Host ""
Write-Host "Test Odoo access:" -ForegroundColor Cyan
Write-Host "  http://odoo.hs27.internal:8069/" -ForegroundColor White
Write-Host ""
Write-Host "To restore original (when Anker is back):" -ForegroundColor Cyan
Write-Host "  1. Uncomment Toolbox entries" -ForegroundColor White
Write-Host "  2. Remove emergency redirect" -ForegroundColor White
Write-Host "  OR restore from backup: $backupPath" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "--- Generating Repository Consolidation Snapshot (PS) ---" -ForegroundColor Cyan

$catalogPath = "artifacts/repo_consolidation/repo_intake_catalog.json"
$contractPath = "SSOT_COLLABORATION_CONTRACT.md"

$ssotVerified = Test-Path $contractPath
$overallStatus = "PENDING"
$legacyRepos = @()

if (Test-Path $catalogPath) {
    $catalog = Get-Content $catalogPath | ConvertFrom-Json
    $legacyRepos = $catalog.legacy_repos
    
    $pending = $legacyRepos | Where-Object { $_.status -eq "pending_intake" }
    if ($null -eq $pending) {
        $overallStatus = "CONSOLIDATED"
    } else {
        $overallStatus = "INTAKE_IN_PROGRESS"
    }
}

$reportPath = "artifacts/repo_consolidation/latest_snapshot.md"
$report = "# Repository Consolidation Snapshot (PS): $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
$report += "**Overall Status**: $overallStatus`n"
$report += "**SSOT Contract**: $(if ($ssotVerified) { "✅ Verified" } else { "❌ Missing" })`n`n"
$report += "## Repo Status`n"
$report += "| Repo Name | Source | Status |`n"
$report += "| --- | --- | --- |`n"
foreach ($r in $legacyRepos) {
    $report += "| $($r.name) | $($r.source) | $($r.status) |`n"
}

$report | Out-File -FilePath $reportPath
Write-Host "Snapshot generated at $reportPath" -ForegroundColor Green

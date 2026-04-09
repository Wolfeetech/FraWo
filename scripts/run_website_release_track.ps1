[CmdletBinding()]
param(
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"

$rootDir = Split-Path -Parent $PSScriptRoot
$auditScript = Join-Path $PSScriptRoot "run_website_release_audit.py"
$gateScript = Join-Path $PSScriptRoot "website_release_gate.py"
$auditRoot = Join-Path $rootDir "artifacts\website_release_audit"

Push-Location $rootDir
try {
    & $PythonCommand $auditScript
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    $latestAuditDir = Get-ChildItem $auditRoot -Directory |
        Where-Object { $_.Name -match '^\d{8}_\d{6}$' } |
        Sort-Object Name |
        Select-Object -Last 1

    if (-not $latestAuditDir) {
        throw "website_release_audit_summary_not_found"
    }

    $summaryPath = Join-Path $latestAuditDir.FullName "summary.tsv"
    & $PythonCommand $gateScript $summaryPath
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}

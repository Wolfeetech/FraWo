param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$artifactRoot = Join-Path $repoRoot "artifacts\security_inventory"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$artifactDir = Join-Path $artifactRoot $timestamp
$reportPath = Join-Path $artifactDir "credential_scan.md"
$rawPath = Join-Path $artifactDir "credential_scan.txt"

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$patterns = @(
  "__ROTATED_SECRET__",
  "__ROTATED_SECRET__",
  "__ROTATED_SECRET__",
  "__ROTATED_SECRET__",
  "db_password = odoo",
  "password='__ROTATED_SECRET__'",
  "password = '__ROTATED_SECRET__'",
  'PASSWORD = "__ROTATED_SECRET__"'
)

$rgArgs = @(
  "-n",
  "--no-heading",
  "-S",
  "-g", "!artifacts/**",
  "-g", "!.git/**",
  "-g", "!scripts/tools/repo_credential_scan.ps1",
  ($patterns -join "|"),
  $repoRoot
)

$results = & rg @rgArgs
$exitCode = $LASTEXITCODE

if ($exitCode -gt 1) {
  throw "rg failed with exit code $exitCode"
}

if ($results) {
  $results | Out-File -LiteralPath $rawPath -Encoding utf8
} else {
  "no_matches=true" | Out-File -LiteralPath $rawPath -Encoding utf8
}

$lines = @(
  "# Credential Scan",
  "",
  "- Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
  "- Repo root: $repoRoot",
  "- Scan mode: high-risk literal scan",
  "- Pattern count: $($patterns.Count)",
  "- Match count: $(@($results).Count)",
  "- Raw results: artifacts/security_inventory/$timestamp/credential_scan.txt",
  ""
)

if ($results) {
  $lines += "## Matches"
  $lines += ""
  $lines += ($results | ForEach-Object { "- $_" })
} else {
  $lines += "## Matches"
  $lines += ""
  $lines += "- no_matches=true"
}

$lines | Set-Content -LiteralPath $reportPath -Encoding utf8

Write-Host "report_path=$reportPath"
Write-Host "raw_path=$rawPath"
Write-Host "match_count=$(@($results).Count)"
Write-Host "status=ready"

param()

$ErrorActionPreference = "Stop"

$profilePath = Join-Path $env:USERPROFILE "wg-studiopc.conf"
if (-not (Test-Path -LiteralPath $profilePath)) {
    throw "Missing WireGuard profile: $profilePath"
}

$archiveRoot = Join-Path $env:USERPROFILE "WireGuard-legacy-archive\2026-03-31"
New-Item -ItemType Directory -Path $archiveRoot -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = Join-Path $archiveRoot "wg-studiopc.before_refresh_$timestamp.conf"
Copy-Item -LiteralPath $profilePath -Destination $backupPath -Force

$content = Get-Content -LiteralPath $profilePath -Raw
$content = $content -replace "(?m)^DNS\s*=.*\r?\n", ""
$content = $content -replace "Endpoint\s*=\s*vpn\.yourparty\.tech:51820", "Endpoint = 91.14.44.20:51820"

$requiredLines = @(
    "Address = 10.0.0.2/32",
    "Endpoint = 91.14.44.20:51820",
    "AllowedIPs = 10.0.0.0/24, 192.168.178.0/24",
    "PersistentKeepalive = 25"
)

foreach ($line in $requiredLines) {
    if ($content -notmatch [regex]::Escape($line)) {
        throw "Refreshed profile is missing expected line: $line"
    }
}

Set-Content -LiteralPath $profilePath -Value $content -Encoding ascii

Write-Output "wireguard_profile_refreshed=true"
Write-Output "profile_path=$profilePath"
Write-Output "backup_path=$backupPath"
Write-Output "endpoint=91.14.44.20:51820"
Write-Output "dns_line_removed=true"

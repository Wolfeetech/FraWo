param()

$ErrorActionPreference = "Stop"

$workspace = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$artifactDir = Join-Path $workspace "artifacts\stockenweiler_inventory"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$hostsBackup = Join-Path $artifactDir "hosts_before_wireguard_legacy_cleanup_$timestamp.txt"
Copy-Item -LiteralPath $hostsPath -Destination $hostsBackup -Force

$services = @("WireGuardTunnel`$VPN", "WireGuardTunnel`$wg-studiopc")
foreach ($name in $services) {
    $service = Get-Service -Name $name -ErrorAction SilentlyContinue
    if ($null -ne $service) {
        if ($service.Status -ne "Stopped") {
            Stop-Service -Name $name -ErrorAction Stop
        }
        & "C:\Program Files\WireGuard\wireguard.exe" /uninstalltunnelservice ($name -replace '^WireGuardTunnel\$', '') | Out-Null
    }
}

$lines = Get-Content -LiteralPath $hostsPath
$filtered = $lines | Where-Object {
    $_ -notmatch '^\s*192\.168\.178\.175\s+yourparty\.tech\s*$' -and
    $_ -notmatch '^\s*192\.168\.178\.175\s+www\.yourparty\.tech\s*$'
}
Set-Content -LiteralPath $hostsPath -Value $filtered -Encoding ascii

Write-Output "wireguard_legacy_cleanup=done"
Write-Output "hosts_backup=$hostsBackup"
Write-Output "removed_services=WireGuardTunnel`$VPN,WireGuardTunnel`$wg-studiopc"
Write-Output "tailscale_left_untouched=true"

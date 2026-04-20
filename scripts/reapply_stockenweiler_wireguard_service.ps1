param()

$ErrorActionPreference = "Stop"

$wireguardExe = "C:\Program Files\WireGuard\wireguard.exe"
$profilePath = Join-Path $env:USERPROFILE "wg-studiopc.conf"
$workspace = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$refreshScript = Join-Path $workspace "scripts\refresh_stockenweiler_wireguard_profile.ps1"
$cleanupScript = Join-Path $workspace "scripts\clean_local_wireguard_legacy.ps1"

if (-not (Test-Path -LiteralPath $wireguardExe)) {
    throw "Missing WireGuard executable: $wireguardExe"
}

if (-not (Test-Path -LiteralPath $profilePath)) {
    throw "Missing WireGuard profile: $profilePath"
}

if (-not (Test-Path -LiteralPath $refreshScript)) {
    throw "Missing refresh script: $refreshScript"
}

if (-not (Test-Path -LiteralPath $cleanupScript)) {
    throw "Missing cleanup script: $cleanupScript"
}

powershell -ExecutionPolicy Bypass -File $refreshScript | Out-Null
powershell -ExecutionPolicy Bypass -File $cleanupScript | Out-Null

& $wireguardExe /installtunnelservice $profilePath | Out-Null
Start-Sleep -Seconds 5

$service = Get-Service -Name "WireGuardTunnel`$wg-studiopc" -ErrorAction Stop

Write-Output "stockenweiler_wireguard_service_reapplied=true"
Write-Output ("service_status=" + $service.Status)
Write-Output "service_name=WireGuardTunnel`$wg-studiopc"
Write-Output "profile_path=$profilePath"

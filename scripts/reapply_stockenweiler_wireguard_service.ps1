param()

$ErrorActionPreference = "Stop"

$wireguardExe = "C:\Program Files\WireGuard\wireguard.exe"
$profilePath = Join-Path $env:USERPROFILE "wg-studiopc.conf"

if (-not (Test-Path -LiteralPath $wireguardExe)) {
    throw "Missing WireGuard executable: $wireguardExe"
}

if (-not (Test-Path -LiteralPath $profilePath)) {
    throw "Missing WireGuard profile: $profilePath"
}

powershell -ExecutionPolicy Bypass -File "C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\scripts\refresh_stockenweiler_wireguard_profile.ps1" | Out-Null
powershell -ExecutionPolicy Bypass -File "C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\scripts\clean_local_wireguard_legacy.ps1" | Out-Null

& $wireguardExe /installtunnelservice $profilePath | Out-Null
Start-Sleep -Seconds 5

$service = Get-Service -Name "WireGuardTunnel`$wg-studiopc" -ErrorAction Stop

Write-Output "stockenweiler_wireguard_service_reapplied=true"
Write-Output ("service_status=" + $service.Status)
Write-Output "service_name=WireGuardTunnel`$wg-studiopc"
Write-Output "profile_path=$profilePath"

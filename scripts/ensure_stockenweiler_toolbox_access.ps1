param(
    [switch]$Down
)

$ErrorActionPreference = "Stop"

$remoteInterface = "wgstkw"

if ($Down) {
    ssh -o LogLevel=ERROR root@toolbox "WG_QUICK_USERSPACE_IMPLEMENTATION=wireguard-go wg-quick down $remoteInterface >/dev/null 2>&1 || true"
    Write-Output "stockenweiler_toolbox_wg=down"
    exit 0
}

$localConfigPath = Join-Path $env:USERPROFILE "wg-studiopc.conf"
if (-not (Test-Path -LiteralPath $localConfigPath)) {
    throw "Missing local WireGuard profile: $localConfigPath"
}

$tempConfig = Join-Path $env:TEMP "wgstkw.conf"
$configText = Get-Content -LiteralPath $localConfigPath -Raw
Set-Content -LiteralPath $tempConfig -Value $configText -Encoding ascii

scp -q $tempConfig root@toolbox:/root/wgstkw.conf

$remoteUp = @"
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
if ! command -v wg >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y -qq wireguard-tools >/tmp/stockenweiler-wg-tools.log 2>&1
fi
if ! command -v wireguard-go >/dev/null 2>&1; then
  apt-get install -y -qq wireguard-go >/tmp/stockenweiler-wg-go.log 2>&1
fi
install -m 600 /root/wgstkw.conf /etc/wireguard/wgstkw.conf
WG_QUICK_USERSPACE_IMPLEMENTATION=wireguard-go wg-quick down $remoteInterface >/dev/null 2>&1 || true
WG_QUICK_USERSPACE_IMPLEMENTATION=wireguard-go wg-quick up $remoteInterface >/dev/null
wg show $remoteInterface
ping -c 1 -W 3 10.0.0.1 >/dev/null
"@

ssh -o LogLevel=ERROR root@toolbox $remoteUp | Out-Null

$sshProbe = ssh -o BatchMode=yes -o LogLevel=ERROR stock-pve "hostname; whoami" 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "stock-pve SSH probe failed: $sshProbe"
}

Write-Output "stockenweiler_toolbox_wg=up"
Write-Output "stockenweiler_ssh_alias=stock-pve"
Write-Output ("stockenweiler_ssh_probe=" + ($sshProbe -join " | "))

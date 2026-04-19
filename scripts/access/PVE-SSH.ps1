$tailscaleHost = "pve"
$tailscaleFallback = "100.91.20.116"
$tailscaleUser = "root"
$legacyHost = "192.168.178.172"
$legacyUser = "mobile"
$cfg = "C:\ProgramData\WireGuard\Configurations\PVE-Surface.conf"
$svc = "WireGuardTunnel`$PVE-Surface"
$wg  = "C:\Program Files\WireGuard\wireguard.exe"
$ssh = "C:\Windows\System32\OpenSSH\ssh.exe"
$sshConfig = Join-Path $PSScriptRoot "Codex\ssh_config"

function Wait-ForSsh {
  param(
    [string]$HostName,
    [int]$Seconds = 8
  )

  for ($i = 0; $i -lt $Seconds; $i++) {
    if (Test-NetConnection -ComputerName $HostName -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue) {
      return $true
    }
    Start-Sleep -Seconds 1
  }

  return $false
}

if (Wait-ForSsh -HostName $tailscaleHost) {
  Write-Host "Verbinde zu $tailscaleHost via Tailscale-SSH/OpenSSH-Pfad..." -ForegroundColor Cyan
  & $ssh -F $sshConfig "$tailscaleUser@$tailscaleHost"
  exit $LASTEXITCODE
}

if (Wait-ForSsh -HostName $tailscaleFallback) {
  Write-Host "Verbinde zu $tailscaleFallback via Tailscale-SSH/OpenSSH-Pfad..." -ForegroundColor Cyan
  & $ssh -F $sshConfig "$tailscaleUser@$tailscaleFallback"
  exit $LASTEXITCODE
}

Write-Host "Tailscale-SSH auf $tailscaleHost ist aktuell nicht erreichbar oder verlangt Sonderauth, pruefe Legacy-WireGuard..." -ForegroundColor Yellow

if (-not (Test-Path $cfg)) {
  Write-Error "Weder Tailscale-SSH noch WireGuard-Config verfuegbar."
  exit 1
}

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
 ).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
  Start-Process -Verb RunAs -FilePath powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

if (-not (Get-Service -Name $svc -ErrorAction SilentlyContinue)) {
  & $wg /installtunnelservice $cfg | Out-Null
}

Start-Service $svc -ErrorAction SilentlyContinue

if (-not (Wait-ForSsh -HostName $legacyHost -Seconds 20)) {
  Write-Error "PVE ist weder via Tailscale noch via Legacy-WireGuard-SSH erreichbar."
  Stop-Service $svc -ErrorAction SilentlyContinue
  exit 1
}

& $ssh -o "StrictHostKeyChecking=accept-new" "$legacyUser@$legacyHost"
Stop-Service $svc -ErrorAction SilentlyContinue

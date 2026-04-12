# Aktiviert diesen Rechner als per RDP erreichbare Admin-Konsole.
# Zielbild: Zugriff primaer ueber VPN/Tailscale, NLA bleibt aktiv.

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
 ).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
  Start-Process -Verb RunAs -FilePath powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "UserAuthentication" -Value 1

Set-Service -Name TermService -StartupType Automatic
Start-Service -Name TermService

Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

Write-Host ""
Write-Host "RDP ist auf diesem Rechner aktiviert." -ForegroundColor Green
Write-Host "Empfohlener Zugriffsweg: ueber Tailscale/VPN statt offenem LAN/WAN." -ForegroundColor Green
Write-Host "Hostname: $env:COMPUTERNAME" -ForegroundColor Cyan

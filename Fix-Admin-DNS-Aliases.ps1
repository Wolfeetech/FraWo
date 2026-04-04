# Stellt lokale Kurz-Hostnamen fuer die Admin-Rolle bereit.
# Hintergrund: Tailscale publiziert stockenweiler-pve, nicht aber den
# gewohnten Alias pve. Dieser Rechner nutzt die Hosts-Datei als stabile
# Fallback-Schicht fuer Admin-Shortcuts.

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
 ).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
  Start-Process -Verb RunAs -FilePath powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$start = "# Private_Networking aliases start"
$end = "# Private_Networking aliases end"
$aliasLines = @(
  "# Private_Networking aliases start",
  "100.91.20.116 pve pve.tail150400.ts.net",
  "100.69.179.87 anker-pve",
  "# Private_Networking aliases end"
)

$content = Get-Content -Path $hostsPath
$startIndex = [Array]::IndexOf($content, $start)
$endIndex = [Array]::IndexOf($content, $end)

if ($startIndex -ge 0 -and $endIndex -ge $startIndex) {
  $before = if ($startIndex -gt 0) { $content[0..($startIndex - 1)] } else { @() }
  $after = if ($endIndex + 1 -lt $content.Length) { $content[($endIndex + 1)..($content.Length - 1)] } else { @() }
  $newContent = @($before + $aliasLines + $after)
} else {
  $newContent = @($content + "" + $aliasLines)
}

Set-Content -Path $hostsPath -Value $newContent -Encoding ASCII
ipconfig /flushdns | Out-Null

Write-Host ""
Write-Host "Lokale Admin-DNS-Aliase wurden gesetzt." -ForegroundColor Green
Write-Host "Neu: pve -> 100.91.20.116" -ForegroundColor Cyan
Write-Host "Neu: anker-pve -> 100.69.179.87" -ForegroundColor Cyan

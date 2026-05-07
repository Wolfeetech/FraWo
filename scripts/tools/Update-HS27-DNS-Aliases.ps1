# Stellt lokale hs27.internal Aliase fuer alle Services bereit.
# Dieses Skript aktualisiert die Windows-hosts-Datei mit allen 10 kanonischen Subdomains.
# Es fordert automatisch Administratorrechte an, falls diese fehlen.

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
 ).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
  Start-Process -Verb RunAs -FilePath powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$startBlock = "# --- Homeserver 2027 Internal Aliases ---"
$endBlock = "# --- End Aliases ---"

# 1. Toolbox IP ermitteln (Dynamic Discovery mit Fallback)
$toolboxIp = "100.82.26.53" # Standard-Fallback
if (Get-Command tailscale -ErrorAction SilentlyContinue) {
    $tsIp = (tailscale ip toolbox 2>$null) | Out-String
    $tsIp = $tsIp.Trim()
    if ($tsIp -match "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$") {
        $toolboxIp = $tsIp
        Write-Host "Aktive Toolbox-IP via Tailscale erkannt: $toolboxIp" -ForegroundColor Green
    } else {
        Write-Host "Tailscale online, aber toolbox IP konnte nicht ermittelt werden. Nutze Fallback: $toolboxIp" -ForegroundColor Yellow
    }
} else {
    Write-Host "Tailscale CLI nicht gefunden. Nutze bekannten Fallback: $toolboxIp" -ForegroundColor Yellow
}

# 2. Aliase definieren (Alle 10 kanonischen Frontdoors)
$aliases = @(
    "$toolboxIp portal.hs27.internal",
    "$toolboxIp cloud.hs27.internal",
    "$toolboxIp odoo.hs27.internal",
    "$toolboxIp paperless.hs27.internal",
    "$toolboxIp ha.hs27.internal",
    "$toolboxIp vault.hs27.internal",
    "$toolboxIp radio.hs27.internal",
    "$toolboxIp radio-anker.hs27.internal",
    "$toolboxIp radio-stock.hs27.internal",
    "$toolboxIp media.hs27.internal"
)

$aliasLines = @($startBlock) + $aliases + @($endBlock)

# 3. Hosts-Datei einlesen und Block ersetzen
if (Test-Path $hostsPath) {
    $content = Get-Content -Path $hostsPath
    $startIndex = [Array]::IndexOf($content, $startBlock)
    $endIndex = [Array]::IndexOf($content, $endBlock)

    if ($startIndex -ge 0 -and $endIndex -ge $startIndex) {
        $before = if ($startIndex -gt 0) { $content[0..($startIndex - 1)] } else { @() }
        $after = if ($endIndex + 1 -lt $content.Length) { $content[($endIndex + 1)..($content.Length - 1)] } else { @() }
        $newContent = $before + $aliasLines + $after
    } else {
        # Falls kein Block existiert, am Ende anfuegen
        $newContent = $content + "" + $aliasLines
    }

    # 4. Zurueckschreiben (ASCII-Encoding wird von hosts verlangt)
    Set-Content -Path $hostsPath -Value $newContent -Encoding ASCII
    
    # 5. DNS Cache leeren
    ipconfig /flushdns | Out-Null

    Write-Host ""
    Write-Host "ERFOLG: Windows hosts-Datei wurde erfolgreich aktualisiert!" -ForegroundColor Green
    Write-Host "Alle 10 'hs27.internal' Frontdoors mappen jetzt auf: $toolboxIp" -ForegroundColor Cyan
    Write-Host ""
    foreach ($alias in $aliases) {
        Write-Host "  -> $alias" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Lokaler DNS-Cache wurde geleert." -ForegroundColor Green
} else {
    Write-Host "FEHLER: Windows hosts-Datei nicht gefunden unter: $hostsPath" -ForegroundColor Red
}

# Verhindert sofortiges Schliessen des Fensters beim Relaunch
Write-Host "Beliebige Taste druecken zum Beenden..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

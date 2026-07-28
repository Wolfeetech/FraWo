# FraWo StudioPC - Aufraeumarbeiten, die Administratorrechte brauchen
# Erstellt am 28.07.2026 aus der IT-Bestandsaufnahme (Odoo #880)
#
# SO STARTEN:
#   Windows-Taste druecken, "PowerShell" tippen,
#   rechte Maustaste auf "Windows PowerShell" -> "Als Administrator ausfuehren"
#   Dann diese Zeile einfuegen und Enter druecken:
#
#   & "C:\Users\StudioPC\FraWo\scripts\admin-aufraeumen-20260728.ps1"
#
# Das Skript macht fuenf Dinge, prueft jedes einzeln und meldet das Ergebnis.
# Nichts davon ist unumkehrbar - zu jedem Schritt steht dabei, wie man ihn
# rueckgaengig macht.
#
# HINWEIS: Diese Datei ist bewusst rein in ASCII geschrieben. PowerShell 5.1
# liest Dateien ohne BOM als ANSI; ein UTF-8-Gedankenstrich wird dabei zu
# Zeichen, die wie ein Anfuehrungszeichen wirken und den Parser zerlegen.

$ErrorActionPreference = 'Continue'

# --- Administratorrechte pruefen --------------------------------------------
$istAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $istAdmin) {
    Write-Host ""
    Write-Host "  ABBRUCH: Dieses Fenster hat keine Administratorrechte." -ForegroundColor Red
    Write-Host "  Bitte PowerShell mit Rechtsklick 'Als Administrator ausfuehren' neu oeffnen."
    Write-Host ""
    return
}

Write-Host ""
Write-Host "=== FraWo Aufraeumarbeiten mit Administratorrechten ===" -ForegroundColor Cyan

$ergebnisse = @()

function Schritt {
    param($Nummer, $Titel, $Grund)
    Write-Host ""
    Write-Host "[$Nummer] $Titel" -ForegroundColor Yellow
    Write-Host "     Grund: $Grund" -ForegroundColor DarkGray
}

# --- 1. windows_exporter: process-Sammler entfernen -------------------------
Schritt 1 "Messfuehler windows_exporter beruhigen" "erzeugt 20723 Fehler pro Woche durch doppelte Messwerte"

$neuerPfad = '"C:\Program Files\windows_exporter\windows_exporter.exe" --config.file="C:\Program Files\windows_exporter\config.yaml" --collectors.enabled cpu,cs,logical_disk,memory,net,os,system,thermalzone,time'

$alt = (Get-CimInstance Win32_Service -Filter "Name='windows_exporter'").PathName
$alt | Out-File "$env:USERPROFILE\windows_exporter-alte-befehlszeile.txt" -Encoding utf8

$null = sc.exe config windows_exporter binPath= "$neuerPfad"
if ($LASTEXITCODE -eq 0) {
    Restart-Service windows_exporter -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    $jetzt = (Get-CimInstance Win32_Service -Filter "Name='windows_exporter'").PathName
    if ($jetzt -notmatch ',process,') {
        Write-Host "     OK - process-Sammler entfernt, Dienst neu gestartet" -ForegroundColor Green
        $ergebnisse += "1. windows_exporter: erledigt"
    } else {
        Write-Host "     Aenderung nicht wirksam" -ForegroundColor Red
        $ergebnisse += "1. windows_exporter: FEHLGESCHLAGEN"
    }
} else {
    Write-Host "     sc.exe meldete Fehler $LASTEXITCODE" -ForegroundColor Red
    $ergebnisse += "1. windows_exporter: FEHLGESCHLAGEN"
}
Write-Host "     Rueckgaengig: alte Zeile steht in windows_exporter-alte-befehlszeile.txt" -ForegroundColor DarkGray

# --- 2. WLAN-Adapter abschalten ---------------------------------------------
Schritt 2 "WLAN-Adapter abschalten" "nicht verbunden (PC haengt am Kabel), wirft 96 Treiberfehler pro Woche"

$wlan = Get-NetAdapter -Name 'WLAN' -ErrorAction SilentlyContinue
if ($wlan -and $wlan.Status -eq 'Disconnected') {
    Disable-NetAdapter -Name 'WLAN' -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    $status = (Get-NetAdapter -Name 'WLAN' -ErrorAction SilentlyContinue).Status
    if ($status -eq 'Disabled') {
        Write-Host "     OK - WLAN deaktiviert" -ForegroundColor Green
        $ergebnisse += "2. WLAN-Adapter: erledigt"
    } else {
        Write-Host "     Status jetzt: $status" -ForegroundColor Red
        $ergebnisse += "2. WLAN-Adapter: unklar"
    }
} elseif ($wlan) {
    Write-Host "     UEBERSPRUNGEN - WLAN ist in Benutzung" -ForegroundColor DarkYellow
    $ergebnisse += "2. WLAN-Adapter: uebersprungen (in Benutzung)"
} else {
    Write-Host "     Adapter 'WLAN' nicht gefunden" -ForegroundColor DarkYellow
    $ergebnisse += "2. WLAN-Adapter: nicht gefunden"
}
Write-Host "     Rueckgaengig: Enable-NetAdapter -Name 'WLAN'" -ForegroundColor DarkGray

# --- 3. WireGuard-Tunnel auf Manuell ----------------------------------------
Schritt 3 "WireGuard-Tunnel auf Manuell stellen" "steht auf Automatisch, ist aber gestoppt - scheitert bei jedem Systemstart"

$wgName = 'WireGuardTunnel$wg-studiopc'
$wg = Get-Service -Name $wgName -ErrorAction SilentlyContinue
if ($wg) {
    Set-Service -Name $wgName -StartupType Manual -ErrorAction SilentlyContinue
    $neu = (Get-Service -Name $wgName).StartType
    if ($neu -eq 'Manual') {
        Write-Host "     OK - Starttyp jetzt: Manuell" -ForegroundColor Green
        $ergebnisse += "3. WireGuard-Tunnel: erledigt"
    } else {
        Write-Host "     Starttyp jetzt: $neu" -ForegroundColor Red
        $ergebnisse += "3. WireGuard-Tunnel: FEHLGESCHLAGEN"
    }
} else {
    Write-Host "     Dienst nicht gefunden" -ForegroundColor DarkYellow
    $ergebnisse += "3. WireGuard-Tunnel: nicht vorhanden"
}
Write-Host "     Rueckgaengig: Set-Service -Name 'WireGuardTunnel`$wg-studiopc' -StartupType Automatic" -ForegroundColor DarkGray

# --- 4. VirtualBox deinstallieren -------------------------------------------
Schritt 4 "Oracle VirtualBox 7.2.2 deinstallieren" "seit September 2025 installiert, KEINE einzige virtuelle Maschine angelegt"

$vbPfad = "C:\Program Files\Oracle\VirtualBox\VirtualBox.exe"
if (Test-Path $vbPfad) {
    Start-Process msiexec.exe -ArgumentList '/X{2FF30437-AC91-4C9A-AFFA-EE5314FE6C83}','/qn','/norestart' -Wait
    Start-Sleep -Seconds 5
    if (Test-Path $vbPfad) {
        Write-Host "     Programm noch vorhanden - evtl. Neustart noetig" -ForegroundColor DarkYellow
        $ergebnisse += "4. VirtualBox: teilweise (nach Neustart pruefen)"
    } else {
        Write-Host "     OK - VirtualBox entfernt" -ForegroundColor Green
        $ergebnisse += "4. VirtualBox: erledigt"
    }
} else {
    Write-Host "     nicht installiert" -ForegroundColor DarkYellow
    $ergebnisse += "4. VirtualBox: war nicht installiert"
}
Write-Host "     Rueckgaengig: bei Bedarf neu von virtualbox.org installieren" -ForegroundColor DarkGray

# --- 5. Docker-Datentraeger verdichten --------------------------------------
Schritt 5 "Docker-Datentraeger verdichten (gibt rund 55 GB frei)" "Docker ist leer, die virtuelle Platte belegt aber weiterhin 57,5 GB"

$vhd = Join-Path $env:LOCALAPPDATA 'Docker\wsl\disk\docker_data.vhdx'
if (Test-Path $vhd) {
    $vorher = [math]::Round((Get-Item $vhd).Length / 1GB, 1)
    Write-Host "     Groesse vorher: $vorher GB"
    Write-Host "     Fahre WSL herunter (Docker Desktop schliesst sich dabei)..."

    Get-Process -Name '*docker*' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    wsl --shutdown
    Start-Sleep -Seconds 10

    $dpZeilen = @(
        ('select vdisk file="' + $vhd + '"'),
        'attach vdisk readonly',
        'compact vdisk',
        'detach vdisk',
        'exit'
    )
    $dpDatei = Join-Path $env:TEMP 'compact_docker.txt'
    $dpZeilen | Out-File $dpDatei -Encoding ascii

    Write-Host "     Verdichte... das dauert einige Minuten, bitte warten."
    diskpart /s $dpDatei | Out-Null
    Remove-Item $dpDatei -Force -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 3
    $nachher = [math]::Round((Get-Item $vhd).Length / 1GB, 1)
    $frei = [math]::Round($vorher - $nachher, 1)
    if ($frei -gt 1) {
        Write-Host "     OK - jetzt $nachher GB, also $frei GB freigegeben" -ForegroundColor Green
        $ergebnisse += "5. Docker-Datentraeger: $frei GB freigegeben"
    } else {
        Write-Host "     Groesse unveraendert bei $nachher GB" -ForegroundColor Red
        $ergebnisse += "5. Docker-Datentraeger: keine Aenderung"
    }
} else {
    Write-Host "     Datei nicht gefunden" -ForegroundColor DarkYellow
    $ergebnisse += "5. Docker-Datentraeger: Datei nicht gefunden"
}

# --- Zusammenfassung --------------------------------------------------------
Write-Host ""
Write-Host "=== ZUSAMMENFASSUNG ===" -ForegroundColor Cyan
foreach ($e in $ergebnisse) { Write-Host "  $e" }
Write-Host ""
$freiC = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
Write-Host "  Freier Platz auf C: $freiC GB"
Write-Host ""
Write-Host "  Docker Desktop kannst du wieder starten, wenn du es brauchst." -ForegroundColor DarkGray
Write-Host ""

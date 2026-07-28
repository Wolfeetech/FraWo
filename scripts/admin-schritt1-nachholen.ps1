# FraWo StudioPC - Nachholung von Schritt 1 (windows_exporter)
# Erstellt am 28.07.2026
#
# Warum ein eigenes Skript: Der erste Versuch ueber sc.exe scheiterte mit
# Fehler 1639 (ERROR_INVALID_COMMAND_LINE). Ursache ist die Verschachtelung
# der Anfuehrungszeichen - der neue Startbefehl enthaelt selbst welche
# ("C:\Program Files\..."), und sc.exe kann damit nicht umgehen, wenn der
# Wert ueber PowerShell durchgereicht wird.
#
# Dieser Weg umgeht das Problem: Der Startbefehl eines Dienstes steht in der
# Registrierung unter ImagePath. Dort wird er als reine Zeichenkette abgelegt,
# ganz ohne Kommandozeilen-Auswertung. Damit entfaellt das Zitierproblem.
#
# SO STARTEN (PowerShell als Administrator):
#   & "C:\Users\StudioPC\FraWo\scripts\admin-schritt1-nachholen.ps1"
#
# Diese Datei ist bewusst rein in ASCII geschrieben (PowerShell 5.1 liest
# Dateien ohne BOM als ANSI).

$ErrorActionPreference = 'Continue'

$istAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $istAdmin) {
    Write-Host ""
    Write-Host "  ABBRUCH: keine Administratorrechte." -ForegroundColor Red
    Write-Host "  PowerShell per Rechtsklick 'Als Administrator ausfuehren' neu oeffnen."
    Write-Host ""
    return
}

$schluessel = 'HKLM:\SYSTEM\CurrentControlSet\Services\windows_exporter'

Write-Host ""
Write-Host "=== windows_exporter: process-Sammler entfernen ===" -ForegroundColor Cyan
Write-Host ""

$alt = (Get-ItemProperty -Path $schluessel -Name ImagePath -ErrorAction SilentlyContinue).ImagePath
if (-not $alt) {
    Write-Host "  Dienst nicht gefunden - nichts zu tun." -ForegroundColor DarkYellow
    return
}

if ($alt -notmatch 'process') {
    Write-Host "  Der process-Sammler ist bereits entfernt. Nichts zu tun." -ForegroundColor Green
    return
}

# Sicherung der alten Zeile
$sicherung = Join-Path $env:USERPROFILE 'windows_exporter-ImagePath-alt.txt'
$alt | Out-File $sicherung -Encoding utf8
Write-Host "  Alte Zeile gesichert nach:"
Write-Host "    $sicherung" -ForegroundColor DarkGray

$neu = $alt -replace ',process,', ','

if ($neu -match 'process') {
    Write-Host "  ABBRUCH: Ersetzung hat nicht gegriffen, nichts geaendert." -ForegroundColor Red
    return
}

Set-ItemProperty -Path $schluessel -Name ImagePath -Value $neu -ErrorAction SilentlyContinue

$kontrolle = (Get-ItemProperty -Path $schluessel -Name ImagePath).ImagePath
if ($kontrolle -match 'process') {
    Write-Host "  FEHLGESCHLAGEN: Eintrag unveraendert." -ForegroundColor Red
    return
}

Write-Host "  Registrierung geaendert." -ForegroundColor Green
Write-Host "  Starte Dienst neu..."

Restart-Service windows_exporter -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

$dienst = Get-Service windows_exporter -ErrorAction SilentlyContinue
Write-Host "  Dienststatus: $($dienst.Status)"

# Nachweis: liefert der Messfuehler noch Daten?
try {
    $antwort = Invoke-WebRequest -Uri 'http://localhost:9182/metrics' -TimeoutSec 15 -UseBasicParsing
    $zeilen = ($antwort.Content -split "`n").Count
    $hatProcess = $antwort.Content -match 'windows_process_'
    Write-Host ""
    Write-Host "  Messfuehler antwortet: HTTP $($antwort.StatusCode), $zeilen Zeilen" -ForegroundColor Green
    if ($hatProcess) {
        Write-Host "  ACHTUNG: process-Werte werden noch geliefert" -ForegroundColor DarkYellow
    } else {
        Write-Host "  process-Werte sind weg - genau so soll es sein" -ForegroundColor Green
    }
} catch {
    Write-Host "  Messfuehler antwortet nicht: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Rueckgaengig machen mit dem Inhalt von:" -ForegroundColor DarkGray
    Write-Host "    $sicherung" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "  Fertig. Die Fehlermeldungen im Ereignisprotokoll sollten jetzt aufhoeren." -ForegroundColor Cyan
Write-Host ""

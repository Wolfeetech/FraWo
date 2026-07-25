# FraWo Funk - Zentrale Musikverwaltung Import-Skript
# Liest neue Musik aus M:\Inbox, sortiert sie in M:\Library ein, stoss den AzuraCast Scan an & weist Dayparting-Playlists zu.

$ErrorActionPreference = "Stop"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " FraWo Funk - Import und Playlist Auto-Sync" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Pruefe Netzlaufwerk M:
if (!(Test-Path "M:\")) {
    Write-Host "[!] Netzlaufwerk M: (\\10.1.0.94\music) nicht erreichbar!" -ForegroundColor Red
    Write-Host "Versuche Verbindung herzustellen..." -ForegroundColor Yellow
    New-SmbMapping -LocalPath "M:" -RemotePath "\\10.1.0.94\music" -Persistent $true
}

# Erstelle Inbox falls nicht vorhanden
if (!(Test-Path "M:\Inbox")) {
    New-Item -ItemType Directory -Path "M:\Inbox" | Out-Null
}

$apiDir = "C:\Users\StudioPC\FraWo\apps\yourparty\apps\api"
Set-Location $apiDir

# Starte den automatisierten Import
python3 import_new_music.py

Write-Host "Musik-Import und Playlist-Zuordnung abgeschlossen!" -ForegroundColor Green

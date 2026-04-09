# Auto-Sync Script fuer den FRAWO Workspace
cd "C:\Users\StudioPC\Documents\Homeserver 2027 Workspace"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   FRAWO WORKSPACE SYNC (STUDIOPC)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Pruefe auf neue Aenderungen von anderen Geraeten (Auto-Merge)..." -ForegroundColor Yellow
# Erzwinge den automatischen Merge-Commit ohne Texteditor
git config pull.rebase false
git pull origin main --no-edit

Write-Host "`n[2/3] Fasse lokale Aenderungen auf diesem PC zusammen..." -ForegroundColor Yellow
git add .
$status = git status --porcelain

if ($status) {
    Write-Host "-> Neue Dateien oder Aenderungen gefunden. Werden gespeichert." -ForegroundColor Green
    git commit -m "🚗 Auto-Sync von StudioPC: Automatisches Backup"
    
    Write-Host "`n[3/3] Lade Aenderungen in die zentrale Cloud hoch..." -ForegroundColor Yellow
    git push origin main
    
    Write-Host "`n✅ ERFOLG: Alles ist gruen! Dein Workspace ist gesichert und aktuell." -ForegroundColor Green
} else {
    Write-Host "`n✅ ERFOLG: Dein Workspace ist bereits auf dem absolut neuesten Stand!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Du kannst dieses Fenster jetzt schliessen (druecke Enter)." -ForegroundColor Cyan
Read-Host

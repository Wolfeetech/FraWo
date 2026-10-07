# Gemini-Abo fuer Hermes (CT160) anmelden, ohne Code abzutippen (Odoo #1966).
# Laeuft am StudioPC in einem eigenen, leeren Profilordner (stoert Antigravitys ~/.gemini nicht).
# Browser oeffnet sich, Wolf bestaetigt nur. Danach gehen die Anmeldedaten per ssh nach CT160 und der Ordner wird geloescht.
$ErrorActionPreference = "Continue"
$tmp = Join-Path $env:TEMP ("gemini-hermes-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Force (Join-Path $tmp ".gemini") | Out-Null
'{"security":{"auth":{"selectedType":"oauth-personal"}}}' | Set-Content -Encoding ascii (Join-Path $tmp ".gemini\settings.json")
$alt = @{ USERPROFILE = $env:USERPROFILE; HOME = $env:HOME }
$env:USERPROFILE = $tmp; $env:HOME = $tmp
Write-Host "Gleich oeffnet sich der Browser: mit dem Google-Konto (AI-Abo) anmelden und zulassen." -ForegroundColor Yellow
Write-Host "Wenn Gemini danach bereit ist (Eingabefeld unten): /quit eintippen." -ForegroundColor Yellow
& (Join-Path $alt.USERPROFILE "AppDataRoaming
pmgemini.cmd")
$env:USERPROFILE = $alt.USERPROFILE; $env:HOME = $alt.HOME
$cred = Join-Path $tmp ".gemini\oauth_creds.json"
if (Test-Path $cred) {
    Get-Content -Raw $cred | ssh -o BatchMode=yes root@10.1.0.227 "cat > /root/.gc && pct exec 160 -- mkdir -p /home/hermes/.gemini && pct push 160 /root/.gc /home/hermes/.gemini/oauth_creds.json --user 1000 --group 1000 --perms 600 && shred -u /root/.gc && echo uebertragen"
    Write-Host "Google-Anmeldung an Hermes uebergeben." -ForegroundColor Green
} else {
    Write-Host "Keine Anmeldedaten gefunden - Anmeldung nicht abgeschlossen?" -ForegroundColor Red
}
Remove-Item -Recurse -Force $tmp
Read-Host "Fertig - Enter zum Schliessen"

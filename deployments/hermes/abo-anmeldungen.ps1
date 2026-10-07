# Abo-Anmeldungen fuer den Hermes-Rechner (CT160), Odoo #1966.
# Start: Rechtsklick auf diese Datei -> "Mit PowerShell ausfuehren"
#   oder in PowerShell:  powershell -ExecutionPolicy Bypass -File C:\Users\StudioPC\FraWo\deployments\hermes\abo-anmeldungen.ps1
# Tokens werden nur verdeckt eingegeben und gehen direkt in Vaultwarden (agent@) und zu Hermes. Nichts wird gespeichert.

$ErrorActionPreference = "Stop"
Write-Host "=== 1/2 Claude-Abo ===" -ForegroundColor Cyan
Write-Host "Gleich oeffnet sich der Browser: dort 'Autorisieren' klicken."
Write-Host "Danach erscheint hier ein langer Schluessel, der mit sk-ant-oat beginnt."
Write-Host "Diesen mit der Maus markieren, Rechtsklick (= kopieren). Dann Enter druecken." -ForegroundColor Yellow
claude setup-token
$sicher = Read-Host "Schluessel jetzt einfuegen (Rechtsklick) und Enter" -AsSecureString
$t = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sicher)).Trim()
if ($t -notmatch '^sk-ant-oat') { Write-Host "Das sieht nicht nach dem Schluessel aus. Abbruch." -ForegroundColor Red; Read-Host "Enter zum Schliessen"; exit 1 }
$t | ssh -o BatchMode=yes root@10.1.0.227 "frawo-secret ablegen 'Claude Code Abo-Token (Hermes)' claude-setup-token >/dev/null && echo ok-tresor"
$t | ssh -o BatchMode=yes root@10.1.0.227 "cat > /root/.ct && pct push 160 /root/.ct /tmp/ct --user 1000 --group 1000 --perms 600 && shred -u /root/.ct && pct exec 160 -- su - hermes -c 'E=~/.hermes/.env; grep -v ^CLAUDE_CODE_OAUTH_TOKEN= `$E > `$E.neu; printf ""CLAUDE_CODE_OAUTH_TOKEN=%s\n"" ""`$(cat /tmp/ct)"" >> `$E.neu; mv `$E.neu `$E; chmod 600 `$E; shred -u /tmp/ct; echo ok-hermes'"
$t = $null

Write-Host ""
Write-Host "=== 2/2 Google/Gemini-Abo ===" -ForegroundColor Cyan
Write-Host "Im Menue 'Login with Google' waehlen. Den Link im Browser oeffnen, mit dem Google-Konto"
Write-Host "anmelden (das mit dem AI-Abo) und den angezeigten Code hier einfuegen."
Write-Host "Wenn Gemini bereit ist: /quit eintippen." -ForegroundColor Yellow
ssh -t root@10.1.0.227 "pct exec 160 -- su - hermes -c 'NO_BROWSER=true ~/.local/bin/gemini'"

Write-Host ""
Write-Host "Fertig. Bitte Claude im Chat Bescheid geben." -ForegroundColor Green
Read-Host "Enter zum Schliessen"

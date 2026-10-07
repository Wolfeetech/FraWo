# Abo-Anmeldungen fuer den Hermes-Rechner (CT160), Odoo #1966.
# Start:  powershell -ExecutionPolicy Bypass -File C:\Users\StudioPC\FraWo\deployments\hermes\abo-anmeldungen.ps1
# Tokens werden verdeckt eingegeben, sofort gegen Claude geprueft und erst dann in Vaultwarden (agent@) und zu Hermes gegeben.
param([switch]$NurGemini)
$ErrorActionPreference = "Continue"
$OPTI = "root@10.1.0.227"

function Teste-Und-Speichere([string]$t) {
    # 1) zu Hermes (Testdatei), 2) Test mit Claude Code auf CT160, 3) nur bei OK: .env + Tresor
    $erg = $t | ssh -o BatchMode=yes $OPTI "tr -d '
' > /root/.ct && pct push 160 /root/.ct /tmp/ct --user 1000 --group 1000 --perms 600 && shred -u /root/.ct && pct exec 160 -- su - hermes -c 'CLAUDE_CODE_OAUTH_TOKEN=`$(cat /tmp/ct) ~/.local/bin/claude -p ""Antworte nur mit OK"" 2>&1 | tail -1'"
    if ($erg -notmatch 'OK') {
        ssh -o BatchMode=yes $OPTI "pct exec 160 -- shred -u /tmp/ct" | Out-Null
        return $false
    }
    ssh -o BatchMode=yes $OPTI "pct exec 160 -- su - hermes -c 'E=~/.hermes/.env; grep -v ^CLAUDE_CODE_OAUTH_TOKEN= `$E > `$E.neu; printf ""CLAUDE_CODE_OAUTH_TOKEN=%s\n"" ""`$(cat /tmp/ct)"" >> `$E.neu; mv `$E.neu `$E; chmod 600 `$E; shred -u /tmp/ct'" | Out-Null
    for ($i = 0; $i -lt 3; $i++) {
        $r = $t | ssh -o BatchMode=yes $OPTI "tr -d '
' | frawo-secret ablegen 'Claude Code Abo-Token (Hermes)' claude-setup-token 2>&1"
        if ($r -match 'abgelegt|aktualisiert') { break }
        Start-Sleep 3
    }
    return $true
}

if (-not $NurGemini) {
    Write-Host "=== 1/2 Claude-Abo ===" -ForegroundColor Cyan
    Write-Host "Gleich oeffnet sich der Browser: dort 'Autorisieren' klicken."
    Write-Host "Danach erscheint hier ein langer Schluessel (sk-ant-oat01-...)."
    Write-Host "Den Schluessel mit der Maus markieren (auch ueber den Zeilenumbruch) und Rechtsklick = kopieren. Einfuegen muessen Sie nicht." -ForegroundColor Yellow
    Write-Host "NICHT in den Chat einfuegen." -ForegroundColor Yellow
    $vorhanden = (Get-Clipboard -Raw) -match 'sk-ant-oat01-'
    if (-not $vorhanden) { claude setup-token } else { Write-Host "Schluessel aus der Zwischenablage wird verwendet (kein neuer noetig)." -ForegroundColor Green }
    $ok = $false
    for ($v = 1; $v -le 3 -and -not $ok; $v++) {
        if (-not $vorhanden -or $v -gt 1) { Read-Host "Schluessel markieren + Rechtsklick (kopiert), dann hier nur Enter druecken" | Out-Null }
        $t = ((Get-Clipboard -Raw) -replace '\s','')
        if ($t -match '(sk-ant-oat01-[A-Za-z0-9_-]+)') { $t = $Matches[1] }
        Write-Host "Pruefe ... (Laenge $($t.Length) Zeichen)"
        $ok = Teste-Und-Speichere $t
        if (-not $ok) { Write-Host "Claude lehnt den Schluessel ab - vermutlich nicht ganz markiert. Bitte nochmal markieren + Rechtsklick." -ForegroundColor Red }
        $t = $null
    }
    Set-Clipboard -Value " "
    if ($ok) { Write-Host "Claude-Abo: OK, Hermes kann Claude Code nutzen." -ForegroundColor Green }
}

Write-Host ""
Write-Host "=== 2/2 Google/Gemini-Abo ===" -ForegroundColor Cyan
Write-Host "Im Menue 'Login with Google' waehlen. Den Link im Browser oeffnen, mit dem Google-Konto"
Write-Host "anmelden (das mit dem AI-Abo) und den angezeigten Code hier einfuegen."
Write-Host "Wenn Gemini bereit ist: /quit eintippen." -ForegroundColor Yellow
ssh -t $OPTI "pct exec 160 -- su - hermes -c 'NO_BROWSER=true ~/.local/bin/gemini'"

Write-Host ""
Write-Host "Fertig. Bitte Claude im Chat Bescheid geben." -ForegroundColor Green
Read-Host "Enter zum Schliessen"

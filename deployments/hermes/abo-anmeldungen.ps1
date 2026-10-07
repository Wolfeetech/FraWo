# Abo-Anmeldungen fuer den Hermes-Rechner (CT160), Odoo #1966.
# Start:  powershell -ExecutionPolicy Bypass -File C:\Users\StudioPC\FraWo\deployments\hermes\abo-anmeldungen.ps1
# Tokens werden verdeckt eingegeben, sofort gegen Claude geprueft und erst dann in Vaultwarden (agent@) und zu Hermes gegeben.
param([switch]$NurGemini)
$ErrorActionPreference = "Continue"
$OPTI = "root@10.1.0.227"

function Teste-Und-Speichere([string]$t) {
    # 1) zu Hermes (Testdatei), 2) Test mit Claude Code auf CT160, 3) nur bei OK: .env + Tresor
    $erg = $t | ssh -o BatchMode=yes $OPTI "cat > /root/.ct && pct push 160 /root/.ct /tmp/ct --user 1000 --group 1000 --perms 600 && shred -u /root/.ct && pct exec 160 -- su - hermes -c 'CLAUDE_CODE_OAUTH_TOKEN=`$(cat /tmp/ct) ~/.local/bin/claude -p ""Antworte nur mit OK"" 2>&1 | tail -1'"
    if ($erg -notmatch 'OK') {
        ssh -o BatchMode=yes $OPTI "pct exec 160 -- shred -u /tmp/ct" | Out-Null
        return $false
    }
    ssh -o BatchMode=yes $OPTI "pct exec 160 -- su - hermes -c 'E=~/.hermes/.env; grep -v ^CLAUDE_CODE_OAUTH_TOKEN= `$E > `$E.neu; printf ""CLAUDE_CODE_OAUTH_TOKEN=%s\n"" ""`$(cat /tmp/ct)"" >> `$E.neu; mv `$E.neu `$E; chmod 600 `$E; shred -u /tmp/ct'" | Out-Null
    for ($i = 0; $i -lt 3; $i++) {
        $r = $t | ssh -o BatchMode=yes $OPTI "frawo-secret ablegen 'Claude Code Abo-Token (Hermes)' claude-setup-token 2>&1"
        if ($r -match 'abgelegt|aktualisiert') { break }
        Start-Sleep 3
    }
    return $true
}

if (-not $NurGemini) {
    Write-Host "=== 1/2 Claude-Abo ===" -ForegroundColor Cyan
    Write-Host "Gleich oeffnet sich der Browser: dort 'Autorisieren' klicken."
    Write-Host "Danach erscheint hier ein langer Schluessel (sk-ant-oat01-...)."
    Write-Host "Markieren: Doppelklick reicht NICHT - mit der Maus vom 's' bis zum letzten Zeichen ziehen, dann Rechtsklick (kopiert)." -ForegroundColor Yellow
    Write-Host "NICHT in den Chat einfuegen." -ForegroundColor Yellow
    claude setup-token
    $ok = $false
    for ($v = 1; $v -le 3 -and -not $ok; $v++) {
        $s = Read-Host "Schluessel einfuegen (Rechtsklick) und Enter" -AsSecureString
        $t = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)).Trim()
        Write-Host "Pruefe ... (Laenge $($t.Length) Zeichen)"
        $ok = Teste-Und-Speichere $t
        if (-not $ok) { Write-Host "Claude lehnt den Schluessel ab - vermutlich unvollstaendig kopiert. Bitte nochmal." -ForegroundColor Red }
        $t = $null
    }
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

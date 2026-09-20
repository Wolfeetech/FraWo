# FraWo · Ollama auf dem StudioPC als echten Dienst einrichten
#
# Warum: Bisher lief die KI in einem Docker-Container, den Docker Desktop
# startet — und Docker Desktop startet nur bei einer BENUTZERANMELDUNG.
# Ohne dass sich jemand am StudioPC anmeldet, gab es keine KI. Für einen
# Dienst, auf den Paperless, Jarvis und Open WebUI zugreifen, taugt das nicht.
#
# Diese Aufgabe startet beim Systemstart unter dem Systemkonto — also ohne
# Anmeldung, wie ein echter Dienst.
#
# MUSS ALS ADMINISTRATOR AUSGEFÜHRT WERDEN.
# Odoo-Aufgabe #1517

$ErrorActionPreference = 'Stop'

# --- Prüfen, dass wir Administrator sind ------------------------------------
$istAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
  ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $istAdmin) {
    Write-Host "ABBRUCH: Dieses Skript braucht Administratorrechte." -ForegroundColor Red
    Write-Host "Rechtsklick auf PowerShell -> 'Als Administrator ausfuehren', dann erneut starten."
    exit 1
}

$OllamaExe   = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$ModellPfad  = "$env:USERPROFILE\.ollama\models"
$AufgabeName = "FraWo Ollama KI-Dienst"

if (-not (Test-Path $OllamaExe)) {
    Write-Host "ABBRUCH: Ollama nicht gefunden unter $OllamaExe" -ForegroundColor Red
    exit 1
}

Write-Host "=== 1. Docker-Container abschalten ===" -ForegroundColor Cyan
# Der Container darf nicht mehr automatisch hochkommen, sonst streiten sich
# beide um Port 11434.
# Native Programme (docker) koennen auf die Fehlerausgabe schreiben; in
# PowerShell 5.1 wird daraus mit ErrorActionPreference='Stop' ein Abbruch.
# Deshalb hier bewusst tolerant.
$alt = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& docker update --restart=no ollama-gpu 2>&1 | Out-Null
& docker stop ollama-gpu 2>&1 | Out-Null
$ErrorActionPreference = $alt
Write-Host "  Container gestoppt, Autostart entfernt (die Modelle bleiben, sie"
Write-Host "  liegen ohnehin unter $env:USERPROFILE\.ollama)"

Write-Host ""
Write-Host "=== 2. Alte Aufgabe entfernen, falls vorhanden ===" -ForegroundColor Cyan
# NICHT schtasks verwenden: Das Programm schreibt bei einer unbekannten Aufgabe
# auf die Fehlerausgabe, und PowerShell 5.1 macht daraus zusammen mit
# ErrorActionPreference='Stop' einen NativeCommandError, der das ganze Skript
# abbricht. Die PowerShell-eigenen Befehle kennen -ErrorAction.
$vorhanden = Get-ScheduledTask -TaskName $AufgabeName -ErrorAction SilentlyContinue
if ($vorhanden) {
    Unregister-ScheduledTask -TaskName $AufgabeName -Confirm:$false
    Write-Host "  alte Aufgabe entfernt"
} else {
    Write-Host "  keine alte Aufgabe vorhanden"
}

Write-Host ""
Write-Host "=== 3. Dienst als geplante Aufgabe anlegen ===" -ForegroundColor Cyan

# Umgebung: auf allen Adressen lauschen (damit OptiPlex, Anker und Paperless
# drankommen), Modelle aus dem bestehenden Ordner, ein Modell gleichzeitig,
# 30 Minuten Haltezeit — lang genug fuer Arbeitsschuebe, kurz genug, dass die
# Grafikkarte nicht dauerhaft belegt bleibt.
$Befehl = "cmd.exe"
$Argumente = "/c set OLLAMA_HOST=0.0.0.0:11434 && " +
             "set OLLAMA_MODELS=$ModellPfad && " +
             "set OLLAMA_KEEP_ALIVE=30m && " +
             "set OLLAMA_MAX_LOADED_MODELS=1 && " +
             "set OLLAMA_ORIGINS=* && " +
             "`"$OllamaExe`" serve"

$Aktion   = New-ScheduledTaskAction -Execute $Befehl -Argument $Argumente
$Ausloser = New-ScheduledTaskTrigger -AtStartup
$Konto    = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$Optionen = New-ScheduledTaskSettingsSet `
              -AllowStartIfOnBatteries `
              -DontStopIfGoingOnBatteries `
              -StartWhenAvailable `
              -RestartCount 3 `
              -RestartInterval (New-TimeSpan -Minutes 1) `
              -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask -TaskName $AufgabeName `
    -Action $Aktion -Trigger $Ausloser -Principal $Konto -Settings $Optionen `
    -Description "FraWo KI-Dienst (Ollama, RTX 4060). Startet ohne Anmeldung. Odoo #1517" `
    | Out-Null
Write-Host "  Aufgabe '$AufgabeName' angelegt (Start beim Systemstart, Konto SYSTEM)"

Write-Host ""
Write-Host "=== 4. Jetzt starten ===" -ForegroundColor Cyan
Start-ScheduledTask -TaskName $AufgabeName
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "=== 5. Nachpruefen (am Ziel, nicht am Rueckgabewert) ===" -ForegroundColor Cyan
try {
    $tags = Invoke-RestMethod "http://127.0.0.1:11434/api/tags" -TimeoutSec 15
    Write-Host "  OK  Dienst antwortet, $($tags.models.Count) Modelle verfuegbar" -ForegroundColor Green
} catch {
    Write-Host "  FEHLER  Dienst antwortet nicht: $_" -ForegroundColor Red
    Write-Host "  Pruefen mit: schtasks /query /tn `"$AufgabeName`" /v /fo LIST"
    exit 1
}

$lauscht = Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue
if ($lauscht) {
    Write-Host "  OK  Port 11434 lauscht auf $($lauscht[0].LocalAddress)" -ForegroundColor Green
}

Write-Host ""
Write-Host "FERTIG. Der Beweis steht aber erst nach einem Neustart:" -ForegroundColor Yellow
Write-Host "  StudioPC neu starten, NICHT anmelden, dann von einem anderen"
Write-Host "  Rechner pruefen:  curl http://10.0.0.156:11434/api/tags"

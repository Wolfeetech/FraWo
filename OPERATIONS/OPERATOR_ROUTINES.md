# Operator Routines

Stand: `2026-03-26`

## Zweck

Diese Datei ist der kanonische Tagessteuerpfad fuer den Operator-Betrieb:

- Start des Arbeitstags
- Tagesabschluss
- Handoff ohne Chat-Abhaengigkeit
- Stop-Conditions vor neuer Implementierung

## Kanonischer Steuerpfad

Verwende fuer den normalen Operator-Tag immer diese Reihenfolge:

1. `LIVE_CONTEXT.md`
2. `OPERATIONS/OPERATOR_ROUTINES.md`
3. `SECURITY_BASELINE.md`
4. `SESSION_CLOSEOUT.md`
5. danach erst neue Aenderungen

Die technischen Einstiegspunkte sind:

- `make start-day`
- `make close-day`

## Start Des Arbeitstags

### Kurzpfad

1. `LIVE_CONTEXT.md` lesen
2. `OPERATIONS/OPERATOR_ROUTINES.md` lesen
3. `SESSION_CLOSEOUT.md` lesen
4. `make start-day` ausfuehren
5. erst danach die erste Aenderung des Tages beginnen

### Was `make start-day` prueft

#### Inventar und Erreichbarkeit

- `make document-ownership-check`
- `make inventory-check`
- `make ansible-ping`

#### Laufzeit und Plattformstatus

- `make qga-check`
- `make business-drift-check`
- `make toolbox-network-check`
- `make toolbox-portal-status-check`
- `make toolbox-media-check`
- `make backup-list`
- `make proxmox-local-backup-check`
- `make pbs-stage-gate`
- `make pbs-proof-check`
- `make haos-stage-gate`
- `make surface-go-check`

#### Netzwerk und Remote-Pfade

- `make toolbox-tailscale-check`
- `make rpi-radio-integration-check`
- `make rpi-radio-usb-check`
- `make haos-reverse-proxy-check`

#### Sicherheitsbasis

- `make security-baseline-check`

#### Handoff-Refresh

- `make refresh-context`

### Remote-Only Modus

Wenn die Schicht nur remote ueber `AnyDesk` oder den `ZenBook` laeuft:

1. `make zenbook-remote-check` ausfuehren
2. danach `make remote-only-check`
3. dann `REMOTE_ONLY_WORK_WINDOW.md` als Stop-/Go-Regel verwenden

### Stop-Conditions

Nicht in neue Implementierung gehen, wenn einer dieser Punkte rot ist:

- `make document-ownership-check`
- `make ansible-ping`
- `make business-drift-check`
- `make proxmox-local-backup-check`
- `make security-baseline-check`
- `make haos-stage-gate`, falls die geplante Arbeit `HAOS` betrifft

### Tatsaechlicher Tagesstart

Vor dem ersten neuen Change muss klar sein:

- welche erste Aufgabe heute wirklich dran ist
- welche Blocker noch offen sind
- welche manuellen Operator-Aktionen noetig bleiben

## Tagesabschluss

### Kurzpfad

1. `make close-day` ausfuehren
2. offene Risiken kurz pruefen
3. Handoff-Dateien aktualisieren
4. den ersten Einstieg fuer morgen explizit hinterlassen

### Was `make close-day` prueft

- `make document-ownership-check`
- `make inventory-check`
- `make ansible-ping`
- `make qga-check`
- `make business-drift-check`
- `make backup-list`
- `make backup-prune-dry-run`
- `make proxmox-local-backup-check`
- `make haos-stage-gate`
- `make security-baseline-check`
- `make refresh-context`

### Handoff-Dateien

Diese Dateien werden nur aktualisiert, wenn sich dort wirklich etwas geaendert hat:

- `SESSION_CLOSEOUT.md`
- `MEMORY.md` fuer dauerhafte Fakten
- `VM_AUDIT.md` fuer verifizierte Laufzeit- oder QGA-Aenderungen
- `PLATFORM_STATUS.md` fuer Incidents, Break-Fix oder Statuswechsel

### Mindestinhalt Fuer Den Tagesabschluss

Der naechste Startpfad muss ohne Chat-Historie erkennbar sein:

- erste Aufgabe morgen
- offene Blocker
- exakte Resume-Kommandos
- offene Operator-Aktionen

## Close Criteria

Der Tag gilt erst dann sauber geschlossen, wenn:

- aktueller Runtime-Status verifiziert ist
- keine neuen Scratch-Dateien herumliegen
- der naechste Schritt explizit ist
- der Handoff ohne Chat-Historie verstaendlich ist

## Taeglicher Sicherheitsfokus

Jeder Tagesstart und Tagesabschluss soll dieselben Leitplanken pruefen:

- keine neuen Klartext-Secrets ausserhalb von `Vaultwarden` oder `Ansible Vault`
- nur die gewollten App-Ports sind offen
- Backup-Schutz ist noch aktiv
- keine versehentliche Public-Exposition
- Tailscale-, PBS- und HAOS-Gates sind im erwarteten Zustand

## Zugeordnete Uebergangsdokumente

- `..\MORNING_ROUTINE.md`
- `..\EVENING_ROUTINE.md`

# Odoo Agent Intake Operations

## Zweck

Dieser Runbook-Pfad beschreibt den sichere(re)n Intake fuer `agent@frawo-tech.de`, ohne Odoo blind auf die gesamte Shared-Mailbox `webmaster@frawo-tech.de` loszulassen.

## Leitentscheidung

- `agent@frawo-tech.de` bleibt Alias auf `webmaster@frawo-tech.de`
- `Nextcloud Mail` trennt Alias-Mails bereits praktisch:
  - `wolf@...` bleibt in `INBOX`
  - `info@...` geht nach `Aliases.Info`
  - `agent@...` geht nach `Aliases.Agent`
- Odoo soll fuer V1 **nicht** die komplette `webmaster`-Inbox per Fetchmail lesen
- der bevorzugte Intake-Pfad liest nur `Aliases.Agent`

## Warum dieser Pfad

- keine Kollision mit persoenlichen oder allgemeinen Funktionsmails in `webmaster`
- keine Abhaengigkeit von serverseitigem `n8n`
- kein Zwang, Odoo-Fetchmail auf einen nicht sauber filterbaren Shared-Posteingang freizugeben
- die bestehende Alias-Routing-Logik auf `VM 200` wird wiederverwendet statt umgangen

## Kanonischer Intake-Baustein

- Script: `odoo_agent_intake_bridge.py`
- Modus:
  - `dry-run` standardmaessig
  - liest nur den IMAP-Ordner `Aliases.Agent`
  - baut aus eingehenden Mails Odoo-Tasks im Masterprojekt
  - markiert Duplikate ueber `Message-ID`
  - verschiebt erfolgreich verarbeitete Mails nach `Aliases.Agent.Processed`

## Live-Stand 2026-04-09

- Ausgerollt auf `VM 200 nextcloud`, weil dort bereits der Alias-Router fuer die Shared-Mailbox laeuft.
- Runtime-Dateien:
  - `/opt/homeserver2027/tools/odoo_rpc_client.py`
  - `/opt/homeserver2027/tools/odoo_agent_intake_bridge.py`
  - `/usr/local/sbin/odoo_agent_intake_runner.sh`
  - root-only Secret: `/root/.config/homeserver2027/odoo_agent_rpc.env`
- Service-Pfad:
  - `hs27-odoo-agent-intake.service`
  - `hs27-odoo-agent-intake.timer`
- Timer-Stand:
  - `enabled`
  - `active`
  - Intervall aktuell `OnBootSec=2min`, danach `OnUnitActiveSec=5min`
- Live-Proof:
  - bestehende `agent@`-Probe aus `Aliases.Agent` wurde erfolgreich in Odoo uebernommen
  - verarbeitete Mail wurde nach `Aliases.Agent.Processed` verschoben
  - Proof-Task steht im Masterprojekt als `[agent@] HS27 alias delivery probe retry 20260408-181036`
  - Stage `Backlog`
  - Owner `wolf@frawo-tech.de` plus `agent@frawo-tech.de`

## Sicherheitsregeln

- keine produktive Verarbeitung direkt aus `INBOX`
- keine Secrets im Repo
- IMAP-Zugang nur ueber Runtime-Variablen:
  - `HS27_IMAP_USER`
  - `HS27_IMAP_PASSWORD`
- Odoo-Zugang nur ueber die bestehenden Runtime-Variablen:
  - `ODOO_RPC_URL`
  - `ODOO_RPC_DB`
  - `ODOO_RPC_USER`
  - `ODOO_RPC_API_KEY` oder `ODOO_RPC_PASSWORD`
- vor dem ersten echten `--apply` immer `dry-run`

## Standardaufruf

```powershell
python odoo_agent_intake_bridge.py `
  --imap-user webmaster@frawo-tech.de `
  --unseen-only `
  --tag "Lane A: MVP"
```

## Produktiver Apply-Pfad

```powershell
python odoo_agent_intake_bridge.py `
  --imap-user webmaster@frawo-tech.de `
  --unseen-only `
  --tag "Lane A: MVP" `
  --apply
```

## Erwartetes Verhalten

- neue Mail an `agent@frawo-tech.de`
- STRATO stellt an `webmaster@frawo-tech.de` zu
- Alias-Router auf `VM 200` verschiebt die Mail nach `Aliases.Agent`
- `odoo_agent_intake_bridge.py` liest nur diesen Ordner
- Odoo-Task entsteht im Masterprojekt `21`
- verarbeitete Mail wird nach `Aliases.Agent.Processed` verschoben

## Task-Standard

- Projekt: `Homeserver 2027: Masterplan`
- Standard-Owner:
  - `wolf@frawo-tech.de`
  - `agent@frawo-tech.de`
- Standard-Stage:
  - `Backlog`
- optionaler Lane-Tag:
  - bewusst pro Aufruf setzen, damit der Intake nicht blind falsch klassifiziert

## Heute bewusst noch offen

- keine direkte Odoo-Fetchmail-Freigabe auf dem Shared-Postfach
- keine automatische Klassifizierung ueber Lanes ohne echten Bedarf
- API-Key-only-RPC blieb fuer `agent@` in dieser Session nicht belastbar; der produktive V1-Pfad nutzt deshalb vorerst einen dedizierten bot-only RPC-Secret-Pfad ausserhalb des Repos

## Definition Of Done fuer den Intake

- `agent@`-Alias ist providerseitig sichtbar zustellbar
- Alias-Router trennt `agent@` sichtbar nach `Aliases.Agent`
- `odoo_agent_intake_bridge.py` liefert im `dry-run` nachvollziehbare Treffer
- ein erster `--apply` erzeugt kontrolliert genau einen Odoo-Task
- die Ursprungsmail landet danach in `Aliases.Agent.Processed`
- keine Nebenwirkung auf `wolf@`- oder `info@`-Mails

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

- kein systemd-/Cron-Livegang ohne sichtbaren ersten Manual-Proof
- keine direkte Odoo-Fetchmail-Freigabe auf dem Shared-Postfach
- keine automatische Klassifizierung ueber Lanes ohne echten Bedarf

## Definition Of Done fuer den Intake

- `agent@`-Alias ist providerseitig sichtbar zustellbar
- Alias-Router trennt `agent@` sichtbar nach `Aliases.Agent`
- `odoo_agent_intake_bridge.py` liefert im `dry-run` nachvollziehbare Treffer
- ein erster `--apply` erzeugt kontrolliert genau einen Odoo-Task
- die Ursprungsmail landet danach in `Aliases.Agent.Processed`
- keine Nebenwirkung auf `wolf@`- oder `info@`-Mails

# Odoo Operations

## Zweck

Odoo ist ERP-, CRM-, Angebots-, Rechnungs- und Prozessplattform fuer `FraWo`.

Der professionelle Zielzustand ist nicht nur `HTTP 200`, sondern ein bewusst definierter Business-Stack.

## Zugriff

- `http://odoo.hs27.internal/web/login`
- `http://100.99.206.128:8444/web/login`

## Normalbetrieb

- nur personengebundene Logins verwenden
- Odoo Studio bleibt optional und nicht Teil des kritischen Plattformpfads
- produktive Aenderungen an Prozessen bewusst und nachvollziehbar ausrollen
- Odoo ist die bevorzugte Business-Schale fuer `CRM`, `Sales`, `Invoicing`, `Project`, spaeter optional `Helpdesk` und `Customer Portal`
- Odoo ist nicht der Ort fuer unkontrollierte Infrastruktur- oder Medienlogik; Radio bleibt davon fachlich getrennt

## SSOT-Modell fuer dieses Projekt

- Das Odoo-Projektboard ist der operative `task SSOT` fuer `Homeserver 2027`: Backlog, In-Arbeit, Blocker, Zuweisung, Review und Abschluss gehoeren dorthin.
- Das Repo bleibt weiterhin der technische `runtime SSOT`: `LIVE_CONTEXT.md`, `MEMORY.md`, `NETWORK_INVENTORY.md`, `VM_AUDIT.md` und die Operations-Runbooks bleiben die verbindliche Wahrheit fuer Infrastruktur, Netzwerk, Gates und Betriebsrealitaet.
- Konsequenz: Aufgabenstatus lebt in Odoo; technische Fakten, Netzstand, IPs, Sicherheitsregeln und Audit-Resultate leben weiter im Repo.
- Keine fragmentierten Odoo-Projekte pro Lane als Dauerzustand pflegen; ein zentrales Masterprojekt mit Stages, Tags und klaren Verantwortlichkeiten ist der bevorzugte Weg.
- `agent@frawo-tech.de` ist fuer diesen Block eine Bot-/Automationsidentitaet, kein menschlicher Admin-Ersatz.

## Board Best Practice

- Ein zentrales Projekt fuer `Homeserver 2027`.
- Workflow-Stages mindestens: `Backlog`, `Planung`, `In Arbeit`, `Blockiert`, `Review/Abnahme`, `Erledigt`.
- Lanes ueber Tags abbilden, nicht ueber immer neue Projekte.
- Aufgaben immer mit klarer `owner`-Logik pflegen:
  - Menschen: `wolf@...`, `franz@...`
  - Bot/Automation: `agent@...` nur fuer Intake, Automationsketten oder klar begrenzte Routinejobs
- Jede operatorgebundene Abhaengigkeit bleibt als sichtbarer Blocker in Odoo und gespiegelt im Repo-Handoff.
- Keine Infrastrukturentscheidungen nur in Odoo-Kommentaren begraben; Entscheidungen muessen im Repo-SSOT nachgezogen werden.

## Hardening vor Automation

- keine Klartext-Credentials in lokalen Odoo-Helferskripten, Markdown-Dateien oder Commits
- fuer API-/Bot-Zugriffe `agent@frawo-tech.de` mit Minimalrechten und separatem Secret/API-Key statt menschlicher Owner-Credentials nutzen
- eingehende Mail oder Automations-Trigger erst aktivieren, wenn SMTP, Rollenmodell und Auditpfad stabil sind
- keine oeffentlichen Webhooks als Primarweg; interne Pfade bleiben `LAN`/`Tailscale first`
- n8n oder aehnliche Orchestrierung ist nur Transport-/Logikschicht, nicht selbst die SSOT

## Automationspfad fuer agent@

- Phase 1: Odoo zuerst nativ sauberziehen
  - Projektboard, Stages, Tags, Rollen, Mailpfad und Bot-Identitaet stabilisieren
  - einfache Intake-Wege bevorzugt Odoo-nativ ueber Alias-/Nachrichtenmodell abbilden
- Phase 2: n8n spaeter als Orchestrierung ergaenzen
  - Eingang ueber dedizierte Mailbox oder Webhook
  - Normalisierung, Routing, Tagging und Task-Anlage oder Task-Update in Odoo
  - Trigger laufen unter `agent@frawo-tech.de`, nicht unter einem menschlichen Hauptkonto
- Phase 3: geschlossene Rueckkopplung
  - eingehende Mail an `agent@...` erzeugt oder aktualisiert Odoo-Tasks
  - Odoo bleibt das sichtbare Arbeitsboard
  - Repo-Handoff bleibt die technische Wahrheit fuer alles, was ueber reine Tasksteuerung hinausgeht

## Taegliche Checks

- Login funktioniert
- Datenbank `FraWo_GbR` erreichbar
- Basis-Workflows laufen ohne UI-Fehler
- Systemmail laeuft ueber `noreply@frawo-tech.de`
- Tailscale-Frontdoor `http://100.99.206.128:8444/web/login` liefert `200`
- direkter Infrastrukturnachweis ueber `http://192.168.2.22:8069/web/login` liefert `200` vom Proxmox-Host aus

## Production-Ready bedeutet hier

- ein bewusstes Modulprofil statt "alles einschalten"
- klares Kundenportal-Zielbild und Benutzerrollen
- dokumentierter Mail- und Benachrichtigungspfad
- sichtbarer Restore-/Backup-Pfad bleibt im SSOT gruen
- keine Vermischung mit `Familie Prinz` oder Stockenweiler-Datenwelten

## Naechste sinnvolle Schritte

- Scope fuer `CRM`, `Angebote/Rechnungen`, `Projekt/Aufgaben` und optional `Customer Portal` festziehen
- reale Nutzerreisen dokumentieren: Lead -> Angebot -> Auftrag -> Rechnung -> Kundenportal
- externe Kunden erst nach bewusstem Rollen-/Portalmodell freigeben
- Homeserver-Masterprojekt in Odoo als einziges operatives Board festziehen
- `agent@frawo-tech.de` als least-privilege Botrolle dokumentieren und spaeter mit separatem API-Key anbinden
- lokale Odoo-Helferskripte auf secret-sicheren Zugriff standardisieren, bevor Mail- oder n8n-Automation live geht

## Nie tun

- keine Testinstanzen mit Produktions-IP
- keine ungeplanten Studio-/Custom-Aenderungen im Kernbetrieb
- keine Stockenweiler-/Familie-Prinz-Daten in denselben Odoo-Betrieb ziehen
- `agent@frawo-tech.de` nicht als vollwertigen menschlichen Admin missbrauchen
- n8n nicht zur versteckten Parallel-SSOT fuer Aufgaben machen

## Eskalation

- bei Langsamkeit erst Host-/Storage-Lage pruefen, dann Odoo selbst
- wenn `production-ready` gefordert ist, zuerst Prozess-/Modulprofil klaeren und nicht reflexhaft weitere Apps oder Custom-Code in Odoo ziehen

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

## Agent- und Alias-Audit 2026-04-08

- Read-only-Audit liegt jetzt reproduzierbar in `odoo_agent_readiness_audit.py`.
- Live gelesen gegen `FraWo_GbR`:
  - Projekt `21` hat bereits die Alias-Domain `frawo-tech.de`, aber noch **keinen** aktiven Aliasnamen und damit keinen scharf geschalteten Intake-Pfad.
  - Alias-Felder stehen aktuell auf:
    - `alias_name = false`
    - `alias_email = false`
    - `alias_status = not_tested`
    - `alias_contact = everyone`
    - `alias_model = project.task`
    - `alias_defaults = {'project_id': 21}`
  - `agent@frawo-tech.de` ist aktiv, `share=false`, `notification_type=email`, `totp_enabled=false`, `api_key_count=0`.
  - Heuristisch wurden am `agent@`-User keine erkennbaren `Admin`-/`Settings`-/`Studio`-Gruppen gefunden.
  - Es existiert genau ein SMTP-Server in Odoo; der Mailpfad ist also vorbereitet, aber der Intake-Pfad noch nicht live.
- Arbeitsbewertung:
  - Der Alias-/Mailpfad ist vorbereitet, aber bewusst noch **nicht** aktiviert.
  - Vor einem Livegang zuerst `agent@`-API-Key erzeugen, sicher ausserhalb des Repos ablegen und danach den Alias-Scope pruefen.
  - Weil `alias_contact` aktuell auf `everyone` steht, sollte dieser Scope vor einer echten Alias-Aktivierung bewusst ueberprueft und gegebenenfalls verengt werden.

## Taegliche Checks

- Login funktioniert
- Datenbank `FraWo_GbR` erreichbar
- Basis-Workflows laufen ohne UI-Fehler
- Systemmail laeuft ueber `noreply@frawo-tech.de`
- Tailscale-Frontdoor `http://100.99.206.128:8444/web/login` liefert `HTTP 200`
- direkter Infrastrukturnachweis ueber `http://10.1.0.22:8069/web/login` liefert `HTTP 200`

## Production-Ready bedeutet hier

- ein bewusstes Modulprofil statt "alles einschalten"
- klares Kundenportal-Zielbild und Benutzerrollen
- dokumentierter Mail- und Benachrichtigungspfad
- sichtbarer Restore-/Backup-Pfad bleibt im SSOT gruen
- keine Vermischung mit `Familie Prinz` oder Stockenweiler-Datenwelten

## Offen bleibt aktuell

- Das zentrale Homeserver-Masterprojekt in Odoo ist jetzt live als operativer Board-Standard normalisiert, muss aber noch im Alltag durch menschliche Nutzung bestaetigt werden.
- Die sechs kanonischen Projektphasen, Lane-Tags und die Owner-Regeln sind gegen die reale Odoo-Instanz validiert; offen bleibt die sichtbare Team-Abnahme im laufenden Betrieb.
- `agent@frawo-tech.de` ist als Rollenbild dokumentiert, aber API-Key, Minimalrechte und produktiver Automationspfad sind noch nicht verifiziert.
- Der eingehende Automationspfad ist noch bewusst offen:
  - zuerst Odoo-internes Alias-/Nachrichtenmodell pruefen
  - erst danach optional `n8n` als Orchestrierung davorschalten
- Odoo-Task-SSOT ist bewusst nur fuer Aufgaben gedacht; technische Wahrheit fuer Netzwerk, Sicherheitsregeln, Audits, IPs und Gates bleibt weiter im Repo-SSOT.
- Vor produktiver Automationsfreigabe fehlt noch die sichtbare End-to-End-Pruefung fuer:
  - Odoo-Projektboard
  - Mail-/Benachrichtigungspfad
  - Bot-Identitaet `agent@...`
  - Rueckkopplung in den Repo-Handoff

## Board-Check 2026-04-07

- Das Masterprojekt `🚀 Homeserver 2027: Masterplan` (`id=21`) ist jetzt auf genau sechs kanonische Projektphasen normalisiert:
  - `📝 Backlog`
  - `⚙️ Planung & Vorbereitung`
  - `🚀 In Arbeit`
  - `🤖 Automatisierung`
  - `🛑 Blockiert`
  - `✅ Erledigt`
- Der operative Board-Write wurde bewusst nicht per direkter SQL-Schreiboperation ausgefuehrt, sondern ueber Odoo-ORM mit stillerem Mail-/Chatter-Context.
- Verifiziert nach Apply:
  - `#217 Service Reachability Audit` steht auf `✅ Erledigt`
  - `#225 Nextcloud Stabilization` steht auf `✅ Erledigt`
  - der Folge-Task `Nextcloud Runtime Hardening / Version Pinning` ist sichtbar offen
  - keine offene Task im Masterprojekt ist ownerlos
  - `rootflo2525@gmail.com` ist im Masterprojekt nicht mehr als Owner verknuepft
  - `agent@frawo-tech.de` ist auf Server-/Ops-/Automation-Tasks als Co-Owner verlinkt, aber nicht als Ersatz fuer menschliche Freigabeaufgaben
- Neue sichtbare Folge-Tasks im Board:
  - `Odoo SSOT Rollout & Board Governance`
  - `agent@ Least-Privilege / API-Key Hardening`
  - `Odoo Incoming Alias / agent@ Intake`
  - `n8n Handoff Contract (disabled)`

## Firewall- und Reachability-Stand

- Repo-/SSOT-Stand:
  - die Toolbox-Mobile-Frontdoor-Ports `8443-8448` sollen per `homeserver2027-toolbox-mobile-firewall.service` nur ueber `Tailscale` offen und vom LAN aus blockiert sein
  - die groessere `UCG`-Firewall-Politik ist laut `UCG_NETWORK_ARCHITECTURE.md` noch **nicht** final ausgerollt
- Vertiefter Live-Check und Remediation vom `2026-04-07`:
  - `toolbox`: `homeserver2027-toolbox-mobile-firewall.service` ist `active`
  - `toolbox`: der Host-Dienst `caddy.service` ist `inactive`, aber die reale Frontdoor laeuft containerisiert als `toolbox-network_caddy_1`
  - `toolbox`: `iptables` enthaelt die erwartete `HOMESERVER2027_MOBILE`-Kette; `8443-8449` werden nur fuer `lo` und `tailscale0` zugelassen und sonst per `tcp-reset` abgewiesen
  - `odoo`-VM: Host-Firewall ist nicht pauschal "deaktiviert", sondern arbeitet auf Docker-/iptables-Basis; `8069/tcp` ist veroeffentlicht und lauscht wieder
  - Root Cause in `VM 220`: Compose-/Runtime-Drift
    - historischer Fehlstart wegen altem Bind auf `192.168.2.22:8069`
    - aktuelle Compose-Datei war zusaetzlich kaputt gedriftet: `web` ohne `env_file`, falscher `/etc/odoo`-Mount auf leeres `./config`, dadurch Passwortfehler gegen PostgreSQL und fehlende `odoo.conf`
    - danach zeigte sich zusaetzlich Versions-Drift: die Business-Datenbank ist `Odoo 17`, waehrend der Web-Container auf `odoo:16.0` zurueckgefallen war
  - Remediation in `VM 220`:
    - Compose wieder auf `stack.env` plus `./odoo.conf:/etc/odoo/odoo.conf:ro` gezogen
    - `docker-compose up -d --force-recreate --remove-orphans` ausgefuehrt
    - Web-Container wieder auf `odoo:17` gezogen, passend zum DB-Stand `17.0.x`
  - Root Cause auf `toolbox` fuer `8444`:
    - der Port war zwar im Docker-Caddy publiziert, aber die aktive Caddyfile enthielt keinen `:8444`-Site-Block
    - der fehlende `:8444`-Reverse-Proxy auf `10.1.0.22:8069` wurde nachgezogen und Caddy neu geladen
  - Filestore-Reconciliation in `VM 220`:
    - Odoo erwartete Dateien unter `.local/share/Odoo/filestore/FraWo_GbR`, waehrend ein grosser Teil noch im alternativen Baum `filestore/FraWo_GbR` lag
    - die fehlenden Dateien wurden nur lesend-abgleichend in den erwarteten Pfad uebernommen, ohne bestehende Dateien zu ueberschreiben
- Aktueller Laufzeitstand nach Remediation vom `2026-04-07`:
  - `http://10.1.0.22:8069/web/login` -> `HTTP 200`
  - `http://odoo.hs27.internal/web/login` -> `HTTP 200`
  - `http://100.99.206.128:8444/web/login` -> `HTTP 200`
  - der Web-Container laeuft jetzt als `odoo:17`
  - die zuvor fehlenden Filestore-Referenzen sind auf `0` gesunken
- Arbeitsbewertung:
  - der Toolbox-Firewall-Standard ist aktuell **aktiv** und nicht pauschal deaktiviert
  - die fruehere Reachability-Stoerung war primaer Compose-/Frontdoor-/Versionsdrift, nicht "Firewall aus"
  - der fruehere `base_cache_signaling`-Rest ist mit dem Versions-Fix verschwunden
  - Odoo ist wieder benutzbar; kuenftige Restarbeiten sollten jetzt eher fachliche Validierung und nicht mehr Runtime-Notfall sein

## DB-Guardrail

- keine direkten SQL-Schreiboperationen auf `FraWo_GbR`, solange kein frischer Rueckweg dokumentiert ist
- vor jedem kuenftigen DB-Fix zuerst einen aktuellen VM-Backup-/Snapshot-Stand verifizieren
- verifizierte lokale Rueckwege fuer `VM 220` existieren bereits unter `/var/lib/vz/dump`, zuletzt auch mit frischem Lauf vom `2026-04-07 19:40:44`
- bevorzugt zuerst nicht-destruktive Pfade nutzen:
  - Laufzeit-/Compose-/Proxy-Pruefung
  - filestore- und volume-basierte Reconciliation
  - Odoo-eigene Upgrade-/Repair-Pfade
- erst wenn diese nicht reichen, einen echten DB-Eingriff planen und vorher explizit begrenzen

## Naechste sinnvolle Schritte

- Scope fuer `CRM`, `Angebote/Rechnungen`, `Projekt/Aufgaben` und optional `Customer Portal` festziehen
- reale Nutzerreisen dokumentieren: Lead -> Angebot -> Auftrag -> Rechnung -> Kundenportal
- externe Kunden erst nach bewusstem Rollen-/Portalmodell freigeben
- Homeserver-Masterprojekt in Odoo als einziges operatives Board festziehen
- `agent@frawo-tech.de` als least-privilege Botrolle dokumentieren und spaeter mit separatem API-Key anbinden
- `odoo_agent_readiness_audit.py --json` als Read-only-Check vor jedem Alias-/API-Key-Schritt verwenden
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

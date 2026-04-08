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
- Phase 2: nur falls spaeter wirklich noetig eine externe Orchestrierung ergaenzen
  - in diesem Block **kein n8n auf dem Homeserver**; Kapazitaet und Betriebsruhe haben Vorrang
  - ein spaeterer Orchestrator waere nur eine optionale Off-Box-/Spaeter-Phase
  - Trigger laufen auch dann unter `agent@frawo-tech.de`, nicht unter einem menschlichen Hauptkonto
- Phase 3: geschlossene Rueckkopplung
  - eingehende Mail an `agent@...` erzeugt oder aktualisiert Odoo-Tasks
  - Odoo bleibt das sichtbare Arbeitsboard
  - Repo-Handoff bleibt die technische Wahrheit fuer alles, was ueber reine Tasksteuerung hinausgeht

## Agent- und Alias-Audit 2026-04-08

- Read-only-Audit liegt jetzt reproduzierbar in `odoo_agent_readiness_audit.py`.
- Live gelesen gegen `FraWo_GbR`:
  - Projekt `21` hat jetzt den internen Pilot-Alias `agent@frawo-tech.de`.
  - Alias-Felder stehen aktuell auf:
    - `alias_name = agent`
    - `alias_full_name = agent@frawo-tech.de`
    - `alias_email = false`
    - `alias_status = not_tested`
    - `alias_contact = employees`
    - `alias_model = project.task`
    - `alias_defaults = {'project_id': 21}`
  - `agent@frawo-tech.de` ist aktiv, `share=false`, `notification_type=email`, `totp_enabled=false`, `api_key_count=1`.
  - Heuristisch wurden am `agent@`-User keine erkennbaren `Admin`-/`Settings`-/`Studio`-Gruppen gefunden.
  - Es existiert genau ein SMTP-Server in Odoo, aber aktuell `fetchmail_count=0`; der Alias ist damit vorbereitet, der echte Mail-Intake aber noch nicht end-to-end live.
  - erlaubte `alias_contact`-Scopes in dieser Instanz:
    - `everyone`
    - `partners`
    - `followers`
    - `employees`
- Arbeitsbewertung:
  - Der Aliasname ist jetzt gesetzt, aber wegen fehlendem Incoming-Mail-Transport bewusst noch nicht als echter End-to-End-Intake bewiesen.
  - Fuer `agent@` existiert jetzt ein serverseitig erzeugter RPC-API-Key; er liegt bewusst nur als root-only Staging-Secret ausserhalb des Repos unter `/root/.config/homeserver2027/odoo_agent_rpc.env`.
  - Der Alias-Scope wurde defensiv auf `employees` gezogen; damit bleibt der Pfad fuer einen internen Pilot vorbereitet, ohne schon durch einen Aliasnamen live zu sein.
  - Auf dem Modell `res.users.apikeys` war im Read-only-Probe kein offensichtlicher oeffentlicher Create-/Reveal-Pfad sichtbar; die echte API-Key-Erzeugung bleibt daher ein bewusster UI- oder dedizierter Server-Side-Schritt.

## Mail-Intake-Probe und Orchestrierungsbewertung 2026-04-08

- Eine echte Probe-Mail an `agent@frawo-tech.de` wurde ueber den produktiven STRATO-SMTP-Pfad ausgesendet und danach read-only im technischen Postfach geprueft.
- Ergebnis:
  - die Nachricht wurde **nicht** als regulaere `agent@`-Mail zugestellt
  - stattdessen kam ein Ruecklaeufer `Returned Mail: HS27 agent intake probe ...`
  - Header-Readout zeigte `From = Strato Mail <MAILER-DAEMON@smtp.strato.de>`
  - eine erneute Live-Probe nach der Alias-Entscheidung wurde direkt ueber den produktiven Odoo-SMTP-Pfad ausgelost und von STRATO weiter mit 550 5.1.2 No such mailbox [MSG0031] fuer agent@frawo-tech.de abgewiesen
- Arbeitsbewertung:
  - der Odoo-Alias `agent@frawo-tech.de` ist inzwischen bewusst als Alias auf `webmaster@frawo-tech.de` uebernommen worden; damit ist der providerseitige Zielpfad logisch festgelegt, aber noch nicht sichtbar end-to-end bestaetigt
  - der Restblocker fuer echten Mail-Intake ist damit nicht mehr die Anlage eines eigenen Postfachs, sondern die verifizierte Zustellung von `agent@` in den technischen Basispfad `webmaster@...`
  - ein direktes Odoo-Fetchmail auf dem Shared-Postfach `webmaster@frawo-tech.de` bleibt bewusst aus, solange kein dedizierter und sauber filterbarer Empfangspfad verifiziert ist
- Orchestrierungsbewertung:
  - `n8n` wird in diesem Block bewusst **nicht** auf dem Homeserver weiterverfolgt
  - Grund: aktuelle Serverkapazitaet und Betriebsruhe sind wichtiger als eine zusaetzliche lokale Orchestrierungsschicht
  - Konsequenz: der naechste sinnvolle Pfad ist **ohne** `n8n`: zuerst sichtbare Alias-Zustellung `agent@ -> webmaster`, danach Odoo-nativer Alias-/Nachrichtenpfad
  - spaetere Orchestrierung bleibt nur eine optionale Off-Box-/Spaeter-Phase und ist aktuell kein technischer Sollpfad

## Runtime-Drift 2026-04-08

- Odoo fiel am Morgen des `2026-04-08` erneut aus, obwohl Projekt-/Task-SSOT bereits gruen war.
- Echte Root Cause Chain:
  - Compose-/Stack-Drift hatte `docker-compose.yml` erneut auf einen harten `PASSWORD=odoo`-Pfad zurueckgesetzt.
  - Die eigentliche Datenbank akzeptierte auf dem Docker-Netz aber weiter nur das zuvor etablierte Secret aus dem bestehenden Volume.
  - Nach Rueckkehr des `odoo.conf`-Mounts blockierten zusaetzlich Dateirechte `600` auf `odoo.conf` und `stack.env` den Container-Startpfad.
- Remediation:
  - `stack.env` wieder auf das tatsaechlich gueltige DB-Secret gezogen
  - `docker-compose.yml` wieder auf `env_file` plus `./odoo.conf:/etc/odoo/odoo.conf:ro` gezogen
  - Dateirechte fuer den gemounteten Startpfad auf lesbar gestellt
- Verifiziert nach Remediation:
  - `http://127.0.0.1:8069/web/login` -> `HTTP 200`
  - `http://odoo.hs27.internal/web/login` -> `HTTP 200`
  - `http://100.99.206.128:8444/web/login` -> `HTTP 200`
- Guardrail:
  - kuenftige Odoo-Stack-Arbeit immer gegen den **echten** DB-Netzpfad testen, nicht nur gegen lokale `trust`-Verbindungen innerhalb des PostgreSQL-Containers

## Frontdoor-Regression 2026-04-08 mittags

- Odoo selbst war weiter gesund, aber der `toolbox`-Frontdoor fiel erneut aus.
- Live-Befund:
  - direkter Odoo-Pfad `http://10.1.0.22:8069/web/login` blieb `HTTP 200`
  - `odoo.hs27.internal` zeigte auf `10.1.0.20`, dort wurde `:80` jedoch zunaechst verweigert
  - `100.99.206.128:8444/web/login` war zunaechst ebenfalls nicht erreichbar
- Root Cause:
  - `toolbox-network_caddy_1` hing in einer Restart-Schleife
  - Ursache war eine kaputt edierte Caddyfile mit `tls internal` innerhalb von `reverse_proxy`-Bloecken fuer `funk.frawo-tech.de` und `agent.frawo-tech.de`
  - zusaetzlich war im `:8444`-Block wieder versehentlich `tls internal` gesetzt, wodurch der dokumentierte `http`-Frontdoor auf `8444` nur noch `400 Bad Request` lieferte
- Remediation:
  - Caddyfile-Syntax fuer die Odoo-nahen Public-Mappings bereinigt
  - `tls internal` aus dem `:8444`-Block entfernt, damit der mobile Tailscale-Frontdoor wieder dem dokumentierten `http`-Pfad folgt
  - Caddy-Container sauber neu erzeugt
- Verifiziert nach Fix:
  - `toolbox-network_caddy_1` laeuft wieder stabil
  - `http://odoo.hs27.internal/web/login` -> `HTTP 200`
  - `http://100.99.206.128:8444/web/login` -> `HTTP 200`

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
- `agent@frawo-tech.de` ist als Rollenbild dokumentiert und der RPC-API-Key ist verifiziert; offen bleibt der produktive Automationspfad mit echter Mail-Zustellbarkeit und spaeterem Trigger-Rueckweg.
- Der eingehende Automationspfad ist noch bewusst offen:
  - zuerst die sichtbare Alias-Zustellung `agent@frawo-tech.de` -> `webmaster@frawo-tech.de` providerseitig bestaetigen
  - danach Odoo-internes Alias-/Nachrichtenmodell end-to-end pruefen
  - aktuell **kein** serverseitiges `n8n` einplanen; nur wenn spaeter wirklich noetig, eine externe Orchestrierung bewerten
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
- STRATO-seitig die echte Alias-Zustellung `agent@frawo-tech.de` -> `webmaster@frawo-tech.de` bestaetigen und danach denselben Probe-Pfad erneut fahren
- danach den Odoo-nativen Alias-/Nachrichtenpfad pruefen, **ohne** neue Server-Orchestrierungsschicht
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

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
- auch Runtime-Konfiguration auf `VM 220` darf keine dauerhaft liegenbleibenden Klartext-Secrets behalten; SMTP-/App-Secrets gehoeren konsequent in den Secret-/Vault-Pfad
- fuer API-/Bot-Zugriffe `agent@frawo-tech.de` mit Minimalrechten und separatem Secret/API-Key statt menschlicher Owner-Credentials nutzen
- eingehende Mail oder Automations-Trigger erst aktivieren, wenn SMTP, Rollenmodell und Auditpfad stabil sind
- keine oeffentlichen Webhooks als Primarweg; interne Pfade bleiben `LAN`/`Tailscale first`
- n8n oder aehnliche Orchestrierung ist nur Transport-/Logikschicht, nicht selbst die SSOT
- Odoo-Filestore bleibt app-exklusiv; wenn Anhaenge in `Nextcloud` sichtbar werden sollen, dann nur ueber einen kontrollierten Export-/Mirror-Pfad gemaess `OPERATIONS/STORAGE_INTEGRATION_OPERATIONS.md`

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
  - eine fruehe Probe lief noch nicht als regulaere `agent@`-Mail durch
  - dabei kam zunaechst ein Ruecklaeufer `Returned Mail: HS27 agent intake probe ...`
  - Header-Readout zeigte `From = Strato Mail <MAILER-DAEMON@smtp.strato.de>`
  - eine spaetere Live-Probe nach der Alias-Entscheidung ist jetzt gruen: MX-RCPT auf `smtpin.rzone.de` akzeptiert `agent@frawo-tech.de`, und der Volltest ueber `smtp.strato.de` lieferte sichtbaren IMAP-Treffer im technischen Basis-Postfach mit `To: agent@frawo-tech.de`
- Arbeitsbewertung:
  - der Odoo-Alias `agent@frawo-tech.de` ist inzwischen bewusst als Alias auf `webmaster@frawo-tech.de` uebernommen worden; die providerseitige Zustellung ist jetzt sichtbar end-to-end bestaetigt
  - der Restblocker fuer echten Mail-Intake ist damit nicht mehr die Provider-Zustellung, sondern nur noch die bewusste Incoming-Strategie fuer die Shared-Mailbox `webmaster@...`
  - ein direktes Odoo-Fetchmail auf dem Shared-Postfach `webmaster@frawo-tech.de` bleibt bewusst aus, solange kein dedizierter und sauber filterbarer Empfangspfad verifiziert ist
- Orchestrierungsbewertung:
  - `n8n` wird in diesem Block bewusst **nicht** auf dem Homeserver weiterverfolgt
  - Grund: aktuelle Serverkapazitaet und Betriebsruhe sind wichtiger als eine zusaetzliche lokale Orchestrierungsschicht
  - Konsequenz: der naechste sinnvolle Pfad ist **ohne** `n8n`: jetzt die Odoo-Incoming-Strategie fuer `agent@ -> webmaster` sauber festziehen und danach den Odoo-nativen Alias-/Nachrichtenpfad aktiv pruefen
  - spaetere Orchestrierung bleibt nur eine optionale Off-Box-/Spaeter-Phase und ist aktuell kein technischer Sollpfad
  - Storage-Integrationen werden davon getrennt betrachtet: kein gemeinsames Live-Dateisystem mit `Nextcloud` oder `Paperless`, sondern nur definierte Exportpfade

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

## Website-Remediation 2026-04-08 abends

- Die sichtbare FraWo-Website auf `VM 220` wurde auf den aktuellen Markenpfad gezogen, ohne den Runtime-SSOT ins Board zu verlagern.
- Live umgesetzt:
  - gebrandete Homepage mit `Smart Media & Event`, Deep-Forest-/UV-Power-Linie und direktem Radio-Pfad
  - neue Kontaktseite ohne Odoo-Placeholder-Inhalt
  - Top-Menue und Header-/Mobile-CTA zeigen jetzt auf `mailto:info@frawo-tech.de` statt auf den alten generischen `/contactus`-Pfad
  - alter Platzhalter-Footer mit `info@frawo-event.de` und `+1 555-555-5556` ist aus dem gerenderten HTML entfernt
- Semantik-/SEO-Basis:
  - `web.base.url` steht jetzt auf `https://www.frawo-tech.de`
  - `web.base.url.freeze` bleibt `True`
  - `website.domain` wurde bewusst wieder auf `NULL` zurueckgezogen, weil ein gesetzter Hostwert in dieser Ein-Website-Instanz den fehlerhaften Canonical-Pfad `"/www.frawo-tech.de/..."` erzeugte
  - Host-Preview mit `Host: www.frawo-tech.de` liefert jetzt wieder korrekte `canonical`-/`og:url`-Werte fuer Startseite und Kontaktseite
- Rueckweg:
  - scoped Rollback fuer die betroffenen Odoo-Website-Records liegt lokal in `Codex/website_backups/frawo_public_website_prepolish_20260408.sql`
  - der angewandte Sollzustand liegt in `Codex/website_backups/frawo_public_website_polish_20260408.sql`
- Wichtige Einordnung:
  - der Odoo-Inhaltspfad ist damit fuer die Website heute sichtbar gruen
  - der echte Restblock fuer den oeffentlichen Release bleibt der getrennte Public-Edge-/Forwarding-Nachweis ausserhalb von Odoo selbst

## Website-Event-Rebuild 2026-04-09

- Die FraWo-Website wurde in Odoo inhaltlich von der allgemeinen Business-/Medienmischung auf einen klaren Eventdienstleister-Auftritt umgebaut.
- Neue Leitlinie im sichtbaren Frontend:
  - `Eventdienstleister`
  - `Technikfachkraefte und Macher`
  - keine `Handwerk`-/`HWK`-Sprache im publizierten Website-Pfad
- Sichtbar live:
  - Hero `Eventbetrieb mit technischer Praezision.`
  - Services fuer `Technische Umsetzung`, `Event-Webseite & Kommunikation` und belastbaren Hintergrund
  - Kontaktseite `Projektstart ohne Umwege.`
  - Top-Menue wieder sauber auf `Kontakt`
  - Header-CTA bleibt `Projekt anfragen` per Mail
- Bildpfad:
  - die frueher vermissten Odoo-Testfotos waren nicht geloescht, sondern nur aus den aktuellen Website-Views herausgefallen
  - sie sind jetzt kontrolliert wieder im Layout referenziert, u. a. ueber `/web/image/1803`, `/web/image/1798`, `/web/image/1801`, `/web/image/1797`, `/web/image/1805` und `/web/image/1806`
- Rollback:
  - aktueller Rueckweg vor dem Rebuild liegt in `Codex/website_backups/frawo_event_site_pre_rebuild_20260409.sql`

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
  - zuerst die Incoming-Strategie fuer die Shared-Mailbox `webmaster@frawo-tech.de` bewusst festziehen
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
- Shared-Mailbox-Strategie fuer `agent@frawo-tech.de` auf `webmaster@frawo-tech.de` festziehen und danach den Odoo-Incoming-Pfad erneut fahren
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

## Website-Layout-Restore 2026-04-09
- Homepage-Hybrid auf Basis des frueheren gefaelligen FraWo-Layouts live gezogen.
- Hero wieder Smart Media & Event; alte Karten-/Band-/Kontaktdramaturgie bewusst zurueckgebracht.
- Odoo-Fotos /web/image/1803, /web/image/1798, /web/image/1801, /web/image/1797, /web/image/1805, /web/image/1806 bleiben im Renderpfad sichtbar.
- Live verifiziert: Smart Media, Karten Digitale Ordnung/Website mit Rueckgrat/Media & Event, Anpacker mit Koepfchen, Klartext statt Blendwerk, Projekt, Idee oder Rueckfrage, und kein Handwerk im gerenderten HTML.

## Website-Content-Fix 2026-04-09
- Inhaltlicher Neustand fuer Homepage, Kontaktseite und Footer live gesetzt.
- Homepage jetzt mit klarem Eventdienstleister-Fokus: technische Setups, Ablauf, Zuspielung, Website und Besucherinfo.
- Kontaktseite jetzt mit konkreten Anfragepfaden statt allgemeinem Marketingtext.
- Live verifiziert: neue Homepage-Subline FraWo plant und betreut technische Setups ..., Karten Technische Planung, Livebetrieb & Betreuung, Website & Besucherinfo, Kontaktseite Projektstart ohne Umwege, und kein Handwerk im Renderpfad.

## Website-Pro-Redesign 2026-04-09
- Homepage visuell und strukturell auf hoeheren professionellen Standard gezogen: starker dunkler Hero, modulare Leistungsflaechen, redaktionelleres Raster, groe�ere Bildflaechen, klarere Eventdienstleister-Positionierung.
- Referenzrichtung fuer Anspruch und Dramaturgie bewusst an grossen Medien-/Liveplattformen orientiert, ohne sie zu kopieren.
- Live verifiziert auf Homepage: FraWo plant und betreut technische Setups ..., Technische Planung, Livebetrieb, Keine Show ueber der Show., Technikfachkraefte und Macher. und kein Handwerk im Renderpfad.
- Kontaktseite nachgezogen und XML-Syntaxfehler durch unescaped Font-Import-URL behoben; /contactus rendert wieder mit Technik kurz briefing. Rest klaeren wir.`r

- Typografie-Update 2026-04-09: Homepage, Kontaktseite und Footer auf Poppins umgestellt. Live verifiziert: amily=Poppins:wght@400;500;600;700;800 rendert auf / und /contactus; Barlow Condensed und Manrope sind aus dem geprueften Renderpfad entfernt.

- Typografie-Feinschliff 2026-04-09: Poppins bleibt CI-Schrift, aber Gewichte wurden differenziert. Live verifiziert im Renderpfad: .frawo-display 800, .frawo-heading/.frawo-card h3/.frawo-panel h3 700, .frawo-contact-title 800, Contact-Subheads 700.

- Claude-Handoff 2026-04-09: Separater Uebergabe-Brief fuer FraWo Website-Design und Hosting in CLAUDE_WEBSITE_HOSTING_HANDOFF.md angelegt. Enthalten: Designziel, CI-Regeln (Poppins), verbotene Sprache, Hosting-/Caddy-Kontext, Rollback-Dateien und direkter Startprompt fuer Claude.

## Agent-Intake-Bridge 2026-04-09

- Der sichere Intake-Pfad fuer gent@frawo-tech.de ist jetzt repo-seitig als eigener Brueckenbaustein vorbereitet:
  - Script odoo_agent_intake_bridge.py
  - Runbook OPERATIONS/ODOO_AGENT_INTAKE_OPERATIONS.md
- Leitentscheidung:
  - Odoo liest fuer V1 **nicht** die komplette Shared-Mailbox webmaster@frawo-tech.de
  - stattdessen wird die bereits aktive Alias-Trennung ueber VM 200 genutzt:
    - gent@ -> Aliases.Agent
    - info@ -> Aliases.Info
    - wolf@ bleibt in INBOX
- Verhalten des neuen Brueckenpfads:
  - dry-run standardmaessig
  - liest nur den IMAP-Ordner Aliases.Agent
  - baut daraus Odoo-Tasks im Masterprojekt
  - setzt Standard-Owner auf wolf@frawo-tech.de plus gent@frawo-tech.de
  - erkennt Duplikate ueber Message-ID
  - verschiebt erfolgreich verarbeitete Mails nach Aliases.Agent.Processed
- Betriebsregel:
  - vor erstem produktivem --apply immer sichtbarer dry-run
  - kein systemd-/Cron-Livegang ohne ersten Manual-Proof
  - keine direkte Fetchmail-Freigabe auf der kompletten Shared-INBOX, solange dieser dedizierte Pfad nicht bewusst verworfen wird
## Agent-Intake Deployment 2026-04-09

- Der `agent@`-Intake ist jetzt nicht mehr nur vorbereitet, sondern auf `VM 200 nextcloud` produktionsnah ausgerollt.
- Ausgerollte Runtime-Dateien:
  - `/opt/homeserver2027/tools/odoo_rpc_client.py`
  - `/opt/homeserver2027/tools/odoo_agent_intake_bridge.py`
  - `/usr/local/sbin/odoo_agent_intake_runner.sh`
  - root-only Secret `/root/.config/homeserver2027/odoo_agent_rpc.env`
- Der Pfad liest bewusst **nur** `Aliases.Agent`, nicht die gesamte Shared-INBOX.
- Live verifiziert:
  - XML-RPC-Login des Bot-Users `agent@frawo-tech.de` funktioniert jetzt von `VM 200` gegen Odoo.
  - `hs27-odoo-agent-intake.service` lief erfolgreich mit `created=1 moved=1`.
  - danach lieferte der Dry-Run `checked=0`, also keine liegengebliebene Mail im Intake-Ordner.
  - Proof-Task im Masterprojekt: `[agent@] HS27 alias delivery probe retry 20260408-181036`, Stage `Backlog`, Owner `wolf + agent`, Tag `Lane A: MVP`.
- Betriebsstatus:
  - `hs27-odoo-agent-intake.timer` ist `enabled` und `active`
  - aktuelles Intervall: Boot+2min, danach alle 5 Minuten
- Einordnung:
  - API-Key-Erzeugung fuer `agent@` wurde serverseitig erneut ausprobiert, war aber fuer echten XML-RPC-Login in diesem Lauf nicht belastbar.
  - Der produktive V1-Pfad nutzt deshalb aktuell bewusst einen dedizierten bot-only RPC-Secret-Pfad ausserhalb des Repos statt menschlicher Zugangsdaten.
## Website-Copy-Refinement 2026-04-09 spaet

- Die FraWo-Website wurde textlich erneut gestrafft, weil der bisherige Ton trotz besserem Layout noch nach generierter Agentur-/Prompt-Sprache klang.
- Live umgesetzt:
  - Homepage und Kontaktseite textlich komplett auf knappe Betreiber-Sprache gezogen
  - globale und websitespezifische Homepage-Views `3636` und `3644` bewusst auf denselben Stand gebracht, damit nicht weiter zwei unterschiedliche Startseiten ausgespielt werden
  - Kontaktseite `3637` auf denselben Tonstandard gezogen
- Sichtbar live:
  - Hero `Technik fuer Veranstaltungen, die sauber laufen.`
  - Leistungsblock `Planung, Betrieb und digitale Begleitung.`
  - Vertrauensblock `Veranstaltungstechnik bewertet man nicht nach Prospekt.`
  - Kontaktseite `Technik kurz anreissen. Rest klaeren wir.`
  - `Typische Anfragen` und `Fuer die erste Mail hilfreich` als konkrete, nicht-marketinghafte Kontaktfuehrung
- Verifikation:
  - Host-Preview auf `www.frawo-tech.de` zeigt die neuen Homepage-Phrasen im gerenderten HTML
  - `/contactus` zeigt die neue Kontaktcopy und keine Prompt-/Agentur-Floskeln mehr

## Website-Visual-Finish 2026-04-10

- Der FraWo-Auftritt wurde visuell auf einen staerkeren Editorial-/Eventdienstleister-Standard gezogen.
- Live umgesetzt:
  - neue CSS-Basis mit `Poppins`, dunklerem Raster, staerkerer Typohierarchie und ruhigerem Spacing
  - Hero jetzt mit Bildstapel und Meta-Rail statt einfachem Textblock
  - breiter Service-Grid statt Standard-Dreikarten-Look
  - Proof-/Galerieblock und neu gerasterte Kontaktseite mit klaren Kontaktpfaden
- Verifikation im gerenderten HTML:
  - `frawo-hero-shell`
  - `frawo-editorial-card`
  - `frawo-service-grid`
  - `frawo-proof-gallery`
  - `frawo-contact-shell`
  - `frawo-contact-grid`
- Der Textpfad blieb dabei bewusst hart und sachlich; typische KI-/Agentur-Floskeln sind im publizierten Pfad weiterhin nicht sichtbar.


## Website-SEO-Cleanup 2026-04-10

- Die Odoo-Default-Metadaten wurden live ersetzt.
- Homepage:
  - echter Title FraWo | Eventtechnik und technische Betreuung`n  - echte Description fuer Eventtechnik, Zuspielung, Umbauten und digitale Besucherinformation
  - sauberes Canonical https://www.frawo-tech.de/`n- Kontaktseite:
  - echter Title Kontakt | FraWo`n  - echte Description fuer den Kontaktpfad
  - sauberes Canonical https://www.frawo-tech.de/contactus`n- Restpunkt: og:url auf /contactus zieht im Host-Preview noch den internen Hostnamen und braucht einen letzten gezielten Fix.



## Website-Meta-Finalisierung 2026-04-10

- Der letzte Kontaktseiten-Restpunkt wurde bereinigt.
- Root Cause: website.page(3) fuer /contactus lief noch ohne website_id als generische Seite.
- Nach Zuordnung auf website_id=1 rendert die Kontaktseite jetzt auch og:url korrekt auf https://www.frawo-tech.de/contactus.
- Ergebnis: Homepage und Kontaktseite haben jetzt saubere Description-, Canonical- und OG-Basis fuer den oeffentlichen FraWo-Auftritt.


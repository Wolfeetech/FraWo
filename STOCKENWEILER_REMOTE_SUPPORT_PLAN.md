# Stockenweiler Remote Support Plan

## Ziel

`Rentner OS` fuer Stockenweiler ist der erste externe Testkundenfall fuer betreute IT ausserhalb des Hauptstandorts.

Ziel ist eine selbstaendig nutzbare Umgebung mit kontrolliertem Fernzugriff von FRAWO aus.

## Aktueller Status

- noch nicht im aktiven Rollout
- kein integrierter Zweitstandort
- waehrend `Lane A: MVP Closeout` offen ist nur als sichtbarer `watch`-Strang
- Betriebsmodell bleibt bewusst klein: betreuter Endpunkt-Support statt Standortvernetzung
- das erste kanonische Inventar lebt jetzt in `manifests/stockenweiler/site_inventory.json`
- lokale Altquellen auf `StudioPC` sind gesichtet; erste belastbare Fakten wurden ins Inventar uebernommen
- schneller Plausibilitaetscheck jetzt per `make stockenweiler-inventory-check`
- kompakter Operator-Ueberblick jetzt per `make stockenweiler-support-brief`
- aktueller Checkstand:
  - `7` Endpunkte modelliert
  - `2` noch komplett offen
  - `5` Legacy-Fakten warten auf echte Revalidierung

## Aktuelle Blocker

- erster Live-Onboarding-Lauf hat noch nicht stattgefunden
- Haupt-PC ist noch nicht konkret identifiziert; der ehemalige Haupt-PC-Anker war laut Operator dieser `StudioPC`
- Handy ist noch nicht konkret identifiziert
- `StudioPC` haengt aktuell nicht im `192.168.178.0/24`-LAN; direkter `SSH`-Zugriff auf `192.168.178.25` lief am `2026-03-31` in Timeout
- `UCG`- und groessere Gateway-Arbeit bleibt aufgeschoben, solange der Operator-`2FA`-Pfad wegen des verlorenen Smartphones blockiert ist

## Phasenmodell

### Phase 1 - jetzt

- getrennte Support-Baseline
- `Tailscale-first`, `AnyDesk` nur Fallback
- Access-Recovery, Inventar, Legacy-Wahrheit und Support-Playbooks
- keine Standort-Vermischung
- keine Service-Migration

### Phase 2 - spaeter

- Management-Plane-Kopplung erst nach geschlossenem `Lane A`
- moeglicher Kandidat: `Tailscale Subnet Router`
- Ziel nur gerouteter Management-Zugriff, nicht Standort-Verschmelzung
- kein `Proxmox`-Cluster ueber WAN
- kein `L2`-Stretch, keine Broadcast-/VLAN-Magie
- keine sofortige Service-Zentralisierung nur wegen neuer Erreichbarkeit

### Phase 3 - erst danach

- selektive Service-Konsolidierung pro Einzelfall
- jede Migration nur mit Abhaengigkeitsbild, Cutover, Rollback und sichtbarer Nachpruefung
- keine pauschale `one instance only`-Regel

## V1 Scope

- verwalteter Haupt-PC
- verwaltetes Handy
- Scanner-/Dokumentenpfad
- Drucker-/Peripheriehilfe
- Fernhilfe bei Technikproblemen

## Nicht in V1

- volles Smart Home
- oeffentliche Adminflaechen im Elternhaus
- Standort-zu-Standort-VPN
- `Network Marriage`
- sofortige Ein-Instanz-Konsolidierung fuer `HA`, `AzuraCast` oder `Odoo`
- zweiter voll integrierter Unternehmensstandort

## Zugriffsmodell

- primaer `Tailscale-only`
- `AnyDesk` nur als GUI-/Benutzerfallback
- keine offenen WAN-Ports
- keine direkte Oeffnung von Admin-UIs

## Servicegedanke

`Rentner OS` ist zunaechst ein Managed Support Service:

- die Eltern nutzen ihre Geraete selbst
- FRAWO kann kontrolliert eingreifen, wenn Technikprobleme auftreten
- die Betriebsverantwortung bleibt dokumentiert und nachvollziehbar

## Identitaets- und Secret-Modell

- eigener Bereich `Stockenweiler` in `Vaultwarden / FraWo`
- getrennte Eintraege fuer Geraete, Tailscale, AnyDesk und Provider
- keine Vermischung mit internen FRAWO-Adminlogins

## Dokumentenpfad

- wenn Dokumentenscan relevant wird, denselben Nextcloud-/Paperless-Grundpfad verwenden
- zuerst ueber einfache, betreute Benutzerflows
- keine Sonderlogik nur fuer Stockenweiler bauen, solange der Standardpfad reicht

## Externer Name

- `online-prinz.de` ist der aktuelle kanonische externe Zielname
- `prinz-stockenweiler.de` bleibt nur Legacy-Kontext aus aelteren Workspaces
- zunaechst nur als Support-/Remote-Kontext, nicht als Release-Website

## Aktuell belastbare Legacy-Fakten

- lokaler Router-Export auf `StudioPC` zeigt aktuell:
  - `FRITZ!Box 5690 Pro` auf `192.168.178.1`
  - Telekom als Provider
  - `proxmox Host` auf `192.168.178.25`
  - `homeassistant` auf `192.168.178.67`
  - `Brother - Drucker` auf `192.168.178.153`
  - `MagentaTV` auf `192.168.178.120`
- aeltere `RadioWorkspace`-Doku bestaetigt den vorhandenen externen Server-/Support-Kontext, ist aber nicht mehr kanonisch
- alle diese Punkte gelten als `legacy_fact_needs_revalidation`, bis der erste echte Stockenweiler-Onboarding-Lauf sie sichtbar bestaetigt
- lokaler Legacy-Probe-Lauf auf `StudioPC` am `2026-03-31` zeigt:
  - `home.prinz-stockenweiler.de` loest auf `91.14.44.20` auf und liefert per `HTTPS` aktuell `Home Assistant`
  - `pve.prinz-stockenweiler.de` ist aktuell nicht aufloesbar
  - `papierkram.prinz-stockenweiler.de` loest auf `80.134.168.100` auf, antwortete aber bei `HTTPS` im aktuellen Probe-Lauf nicht rechtzeitig
  - `cloud.prinz-stockenweiler.de` loest auf `91.14.44.20` auf, antwortet aktuell aber mit `TLSV1_UNRECOGNIZED_NAME`
  - `files.alopri`, `paperless.alopri`, `vault.alopri` und `vpn.prinz-stockenweiler.de` sind aktuell nicht aufloesbar
- lokale Browser-Spuren auf `StudioPC` bestaetigen alte Arbeitsziele:
  - `Chrome`: `https://home.prinz-stockenweiler.de/dashboard-bereiche`
  - `Edge`: `https://papierkram.prinz-stockenweiler.de/dashboard`
  - `Edge`: `https://papierkram.prinz-stockenweiler.de/documents?...`
  - `Edge`: `https://cloud.prinz-stockenweiler.de/apps/dashboard/`
  - `Edge`: `http://adguard.alopri/`
- `Windows Recent` auf `StudioPC` zeigt zusaetzlich den UNC-Pfad `\\\\192.168.178.120\\scans\\Familie Prinz`; das ist ein starker Alt-Hinweis auf einen SMB-/Scan-Pfad und kollidiert mit dem Router-Export, der `.120` aktuell als `MagentaTV` fuehrt
- `.ssh/known_hosts` auf `StudioPC` zeigt fuer `192.168.178.172` und `192.168.178.25` denselben `SSH`-Hostkey; das ist ein starkes lokales Signal, dass der alte `Proxmox`-Host von `.172` auf `.25` umgezogen ist
- der ehemalige Haupt-PC-Anker fuer diesen Altstand war laut Operator dieser `StudioPC`; alte Zugangspfade sollten daher zuerst hier gesucht und gesichtet werden

## Integrationsprinzip

- Stockenweiler bleibt erst einmal ein getrennter betreuter Support-Standort
- kein direktes Vermischen der internen FRAWO-Infrastruktur mit dem Elternhaus-LAN
- spaetere Kopplung nur `management-first`, nicht `service-merge-first`
- Home Assistant fuer den Vater ist als spaetere, bewusst getrennte Erweiterung denkbar:
  - entweder als eigener externer Home-/Site-Kontext
  - oder zuerst nur als Remote-Support auf dem vorhandenen lokalen Home-Assistant-System
- solange der echte Bedarf nicht sichtbar verifiziert ist, bauen wir keinen komplexen Verbund und keine Sonderarchitektur

## Minimum Definition of Done

1. Tailscale-Zugriff dokumentiert
2. Fallback ueber AnyDesk dokumentiert
3. Haupt-PC und Handy als betreute Endpunkte erfasst
4. Passwort- und Providerdaten in `Vaultwarden / FraWo` abgelegt
5. kein oeffentlich exponierter Adminpfad aktiv

## Naechste Einstiegsschritte

1. erstes echtes Inventar aufnehmen:
   - Haupt-PC
   - Handy
   - Drucker / Scanner
   - Router / Provider
   - Zielablage: `manifests/stockenweiler/site_inventory.json`
2. Remote-Support-Standard pruefen:
   - `Tailscale`
   - `AnyDesk` nur Fallback
3. getrennten Secret-Bereich `Stockenweiler` in `Vaultwarden / FraWo` nur mit echten Daten befuellen
4. keinen Sonderpfad fuer Dokumente bauen, solange Nextcloud/Paperless-Standard reicht
5. keine WAN-Freigabe und kein Site-to-Site-VPN in V1

## Phase-2-Backlog

### Management Plane Bridge Candidate

- spaeterer Kandidat: `Tailscale Subnet Router`
- Ziel: gerouteter Management-Zugriff vom `StudioPC` auf Stockenweiler-Ziele
- nicht gleichbedeutend mit Standort-Verschmelzung
- kein `WireGuard`-Parallelstandard; hoechstens Recovery-/Notfallpfad

Aktivierung erst wenn:

- `Lane A` geschlossen ist
- Stockenweiler bewusst von `watch` auf `active` gehoben wird
- Haupt-PC und Handy verifiziert sind
- mindestens ein echter Remote-Supportfall sauber gelaufen ist

### Service Consolidation Candidates

- `Home Assistant`: zuerst `management-only`, spaeter eventuell `migrate_later`
- `Radio`: zuerst lokal halten, spaeter eventuell `migrate_later`
- `WordPress / Website`: erst spaeterer Kandidat, wenn Bedarfs- und Inhaltsbild klar ist
- `Paperless / Nextcloud`: zuerst Wahrheit und Zugriff pflegen, spaeter eventuell `migrate_later`
- `SMB / Scan`: explizit lokal halten, bis `\\\\192.168.178.120\\scans\\Familie Prinz` fachlich aufgeloest ist

### Migration Blockers

- `Lane A` ist noch aktiv
- Haupt-PC ist nicht verifiziert
- Handy ist nicht verifiziert
- primaerer Remote-Pfad ist noch nicht an einem echten Supportfall bewiesen
- Rolle von `192.168.178.120` ist noch nicht aufgeloest
- `FRITZ!Box`-/`Tailscale`-Faehigkeit fuer spaetere Management-Kopplung ist noch nicht sichtbar bestaetigt
- Upload-/Latenzprofil ist noch nicht dokumentiert

### Rollback Requirements

- jede spaetere Standort-Kopplung muss vom `StudioPC` aus rueckbaubar sein
- lokale Stockenweiler-Dienste muessen waehrend Phase-2-Tests lokal funktionsfaehig bleiben
- jeder Bridge-Pfad braucht dokumentierte Disable-/Remove-Schritte vor Aktivierung
- kein lokaler Dienst wird ohne sichtbaren Post-Check und Rollback-Pfad dekommissioniert

## Erster Live-Onboarding-Lauf

Vor Ort oder im ersten echten Remote-Lauf sammeln:

- Haupt-PC Friendly Name
- Haupt-PC OS und Login-Modell
- Haupt-PC `Tailscale`-Name oder `AnyDesk`-ID
- Handy-Modell und OS
- Handy-`Tailscale`-Name
- Router-Management-Kontaktpfad
- exaktes Brother-Modell
- MagentaTV-Box-Modell und Raumkontext

Der erste Lauf ist erst dann fachlich gruen, wenn:

- Haupt-PC als betreuter Endpunkt identifiziert ist
- Handy als betreuter Endpunkt identifiziert ist
- primaerer Fernzugriff ueber `Tailscale` oder dokumentierter `AnyDesk`-Fallback steht
- der erste Supportfall ohne WAN-Admin-Exposition routbar ist

## Erste Support-Playbooks

### TV / Magenta

- zuerst klaeren, ob TV, Receiver oder Netzproblem
- `MagentaTV`-Box, HDMI-Pfad und lokalen Netzpfad pruefen
- gefuehrte Haushaltsschritte vor Remote-Control-Werkzeugen bevorzugen

### Vater Desktop

- zuerst den Haupt-PC eindeutig identifizieren
- `Tailscale` bevorzugen, `AnyDesk` nur als dokumentierten Fallback
- keine ad hoc WAN-Freigaben bauen

### Drucker / Scanner

- zuerst auf Druck-, Scan- oder Konnektivitaetsproblem eingrenzen
- FraWo-Dokumentenpfad nur nutzen, wenn das Haushaltsproblem wirklich Dokumenten-Ingest ist

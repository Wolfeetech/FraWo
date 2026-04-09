# Stockenweiler Remote Support Plan

## Ziel

`Rentner OS` fuer Stockenweiler ist der erste externe Testkundenfall fuer betreute IT ausserhalb des Hauptstandorts.

Ziel ist eine selbstaendig nutzbare Umgebung mit kontrolliertem Fernzugriff von FRAWO aus.

Fuer die uebergeordnete Reihenfolge, Integrationslogik und den spaeteren Marriage-Pfad gilt zusaetzlich:

- `ANKER_STOCKENWEILER_MARRIAGE_PLAN.md`

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
  - `8` Endpunkte modelliert
  - `2` noch komplett offen
  - `6` Legacy-Fakten warten auf echte Revalidierung

## Aktuelle Blocker

- erster Live-Onboarding-Lauf hat noch nicht stattgefunden
- Haupt-PC ist noch nicht konkret identifiziert; der ehemalige Haupt-PC-Anker war laut Operator dieser `StudioPC`
- Handy ist noch nicht konkret identifiziert
- `StudioPC` haengt aktuell nicht direkt im `192.168.178.0/24`-LAN; der direkte LAN-/Tailscale-Pfad fehlt weiter
- ein funktionierender Recovery-Pfad existiert jetzt aber: `stock-pve` auf `StudioPC` nutzt `ProxyJump toolbox`, waehrend `toolbox` den alten Stockenweiler-`WireGuard`-Backbone im Userspace aufspannt
- lokaler `Tailscale`-Status auf `StudioPC` ist `Running`, akzeptiert Routen jetzt wieder (`RouteAll=true`), zeigt aber aktuell trotzdem nur die sichtbare Route `192.168.2.0/24` via `toolbox`; `192.168.178.0/24` ist weiter nicht sichtbar
- neue Architekturklarstellung `2026-04-03`:
  - das lokale alte `WireGuard` auf `StudioPC` ist nicht die Zielarchitektur
  - gewuenscht ist spaeter ein echtes `Site-to-Site WireGuard` zwischen `UCG` und `Stockenweiler`
  - `Tailscale` bleibt bis dahin der Management-/Operator-Pfad; `WireGuard` auf dem `StudioPC` bleibt nur Recovery/Altlast
- der professionelle Management-Bridge-Pfad ist jetzt vorbereitet, aber noch nicht fertig:
  - Zielpfad: `Tailscale`-Subnet-Router auf `stockenweiler-pve` fuer `192.168.178.0/24`
  - Zustand aktuell: `route_approval_pending`
  - `stockenweiler-pve` ist bereits in `tail150400.ts.net` eingeloggt und konfiguriert die Advertise-Route `192.168.178.0/24`
  - solange die Route im Tailscale-Admin noch nicht freigegeben ist, bleibt `ssh stock-pve` ueber den Toolbox-/WireGuard-Recovery-Pfad der sichere Arbeitsweg
- lokaler Windows-`WireGuard` ist noch nicht komplett sauber:
  - aktiver Alt-Dienst `WireGuardTunnel$VPN` laeuft weiter und braucht fuer Stop/Uninstall einen erhoehten Admin-Token
  - die `hosts`-Datei pinnt `yourparty.tech` und `www.yourparty.tech` noch auf `192.168.178.175`; das Entfernen braucht ebenfalls einen erhoehten Admin-Token
  - das kanonische lokale Profil wurde aber bereits aufgefrischt:
    - `C:\\Users\\StudioPC\\wg-studiopc.conf`
    - direkter Endpoint `91.14.44.20:51820`
    - keine lokale `DNS = ...`-Zeile mehr
  - sichtbar ist sogar schon eine lokale Route `192.168.178.0/24` ueber `10.0.0.2`, aber direkter TCP/22-Zugriff auf `192.168.178.25` scheitert weiterhin; dieser Windows-Tunnel gilt also weiter als stale, bis er mit Admin-Token sauber reapplied ist
- `AnyDesk` ist lokal vorhanden, aber die geborgenen Remote-IDs sind noch nicht auf heutige Stockenweiler-Geraete gemappt

## Aktueller Runtime-Druck und Konsolidierungshinweis

- der aktuelle Plattformaudit `artifacts/platform_health/latest_report.md` zeigt Stockenweiler nicht als leeren Reserve-Standort, sondern als unter Last stehenden Legacy-Standort
- harter Befund `2026-04-04`:
  - Host-Swap-Nutzung `6.3 / 8.0 GiB`
  - Storage `hdd-backup` bei `84%`
  - `anker-music` aktuell inaktiv
  - `VM 360 homeassistant-eltern` und `VM 210 azuracast-vm` laufen bereits mit hoher RAM-Auslastung
- daraus folgt:
  - keine neuen Zusatzlasten nach Stockenweiler kippen, bevor Payload bereinigt und Speicherpfade geklaert sind
  - Stockenweiler zuerst als Legacy-/Support-Standort stabilisieren, dann erst Ressourcenbeitrag bewerten
  - vor jedem Ausduennen der Site zuerst die essenzielle `yourparty`-Payload nach Rothkreuz sichern

## Essenzielle yourparty-Payload vor Ausduennen sichern

- `VM 210 azuracast-vm`
- `CT 207 radio-wordpress-prod`
- `CT 208 mariadb-server`
- `CT 211 radio-api`

Diese vier Bausteine sind aktuell die kanonische Minimalmenge, die vor einem Rueckbau oder einer Rollenverschiebung aus Stockenweiler gesichert werden muss.

## Neue Leitentscheidung: spaeteres S2S-WireGuard statt lokaler Dauerbastelei

- `Tailscale` ist weiter der aktuelle Managementpfad fuer Codex/Gemini und den professionellen Tagesbetrieb.
- Das gewuenschte Infrastrukturziel fuer die Standortbruecke ist aber **nicht** der lokale Windows-`WireGuard` auf `StudioPC`.
- Das gewuenschte Infrastrukturziel ist ein echtes `Site-to-Site WireGuard` zwischen `UCG-Ultra` am Anker-Standort und dem bestehenden oder neu definierten `WireGuard`-Endpunkt in `Stockenweiler`.
- Dafuer gibt es zwei saubere Varianten, die erst read-only inventarisiert und dann gegeneinander entschieden werden:
  - `Variante A`: bestehender `WireGuard`-Server in `Stockenweiler` bleibt Server, `UCG-Ultra` wird Client.
  - `Variante B`: `UCG-Ultra` hostet den neuen Server, `Stockenweiler` wird Client.
- Vor dieser Entscheidung gilt:
  - keine weitere mentale Vermischung von lokalem `StudioPC`-VPN und spaeterem Standort-VPN
  - `Tailscale` bleibt fuer Adminzugriffe aktiv
  - der naechste fachlich saubere Schritt ist die read-only Inventarisierung des heutigen `WireGuard`-Setups in `Stockenweiler`
- Scan-/Musikpfade sind noch nicht sauber aufgeloest; lokale Spuren zeigen aktuell `\\\\192.168.178.25\\music`, `\\\\192.168.178.120\\music`, `\\\\192.168.178.120\\scans\\Familie Prinz` und `\\\\192.168.178.187\\ScansDrucker`
- Disk-/Filesystem-Wahrheit auf `192.168.178.25` ist jetzt read-only dokumentiert; beide grossen HDD-Pfade sind aber aktuell voll und damit noch kein sofort nutzbarer PBS-Zielpfad
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
- lokale Scan-Ordner fuer die Eltern
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

## Aktueller Remote-Pfad-Befund

- read-only Probe auf `StudioPC` am `2026-03-31` zeigt:
  - `Tailscale`-Backend ist lokal `Running`
  - sichtbare Primary Route aktuell nur `192.168.2.0/24` via `toolbox`
  - `192.168.178.0/24` ist aktuell **nicht** als sichtbare Subnet-Route vorhanden
  - `RouteAll=true`; trotzdem ist `192.168.178.0/24` noch nicht sichtbar, was fuer fehlende Route-Freigabe im Tailscale-Admin spricht
  - `ssh stock-pve` ist jetzt **erreichbar**
  - praktischer Pfad: `StudioPC -> toolbox -> userspace WireGuard wgstkw -> 192.168.178.25`
  - lokaler Wiederanlauf-Helfer: `powershell -ExecutionPolicy Bypass -File .\\scripts\\ensure_stockenweiler_toolbox_access.ps1`
  - lokaler Profil-Refresh: `powershell -ExecutionPolicy Bypass -File .\\scripts\\refresh_stockenweiler_wireguard_profile.ps1`
  - Tailscale-Bridge-Vorbereitung und Check:
    - `python scripts/prepare_stockenweiler_tailscale_bridge.py`
    - `python scripts/check_stockenweiler_tailscale_bridge.py`
    - aktueller Zustand: `route_approval_pending`
  - spaeterer Admin-Reapply des echten Windows-Tunnel-Dienstes: `powershell -ExecutionPolicy Bypass -File .\\scripts\\reapply_stockenweiler_wireguard_service.ps1`
  - lokale Bereinigung:
    - einzig behaltenes Profil im Benutzerpfad: `C:\\Users\\StudioPC\\wg-studiopc.conf`
    - archivierte Altprofile: `C:\\Users\\StudioPC\\WireGuard-legacy-archive\\2026-03-31`
- lokaler `AnyDesk`-Fallback ist real vorhanden:
  - `AnyDesk.exe` ist installiert
  - `user.conf` enthaelt die Roster-IDs `1580356160` und `1971554928`
  - zusaetzliche lokale Trace-Kandidaten sind `1174136922`, `1342642678`, `1468499678`, `1935329794`, `612089364`, `859293713` und `1129124189`
- Konsequenz:
  - der `pve`-Zugang ist fuer read-only Wahrheit und spaetere Umsetzungen jetzt wieder da
  - der professionelle Bridge-Zielpfad ist technisch vorbereitet und der Node ist bereits joined, aber die Subnet-Route ist noch nicht freigegeben
  - weiterhin offen sind die Tailscale-Freigabe fuer `stockenweiler-pve`, die AnyDesk-Zuordnung und die Identitaet der heutigen Endgeraete

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

- zuerst strikt lokal in Stockenweiler:
  - Scan-Ordner fuer die Eltern
  - einfache lokale Verwaltung am Drucker-/Scan-Pfad
- keine automatische Vermischung mit dem FRAWO-Business-Dokumentenpfad
- falls spaeter Dokumentenautomation sinnvoll wird:
  - dann als eigener Stockenweiler-Pfad
  - bevorzugt mit eigener `Paperless`-DB statt gemeinsamer FRAWO-Business-Datenbank

## Radio / Media

- `Radio` ist nicht an Stockenweiler oder Anker als Standort gebunden
- Hosting spaeter dort, wo Hardware und Stabilitaet besser sind
- daraus folgt:
  - jetzt keine Migration
  - spaeter keine ideologische Standortwahl, sondern Runtime-/Hardware-Entscheidung

## Backup / Storage

- die lokalen HDDs am `Proxmox`-Host in Stockenweiler sind ein sinnvoller spaeterer Kandidat fuer PBS-/Backup-Ergaenzung
- Zielbild:
  - die Nodes sollen sich ergaenzen statt sich spiegelbildlich zu duplizieren
  - Stockenweiler kann spaeter Backup-Kapazitaet beitragen
- aber nicht jetzt:
  - erst nach geschlossenem `Lane A`
  - erst nach dokumentierter Management-Erreichbarkeit
  - erst nach sichtbarer Disk-/Filesystem-Wahrheit
  - erst mit Rollback

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
- lokale Legacy-Probe-Lauf auf `StudioPC` am `2026-03-31` zeigt:
  - `home.prinz-stockenweiler.de`: **erreichbar**, lädt das Home-Assistant-Frontend, zeigt aber "Unable to connect to Home Assistant" (Backend-Fehler).
  - `pve.prinz-stockenweiler.de`: **nicht erreichbar** (`ERR_NAME_NOT_RESOLVED`), DNS-Fehler.
  - `papierkram.prinz-stockenweiler.de/dashboard`: **nicht erreichbar** (`ERR_CONNECTION_TIMED_OUT`), Timeout auf Port 443.
  - `cloud.prinz-stockenweiler.de/apps/dashboard/`: **nicht erreichbar** (`ERR_SSL_UNRECOGNIZED_NAME_ALERT`), TLS/SNI-Fehler.
  - `files.alopri`, `paperless.alopri`, `vault.alopri` und `vpn.prinz-stockenweiler.de` sind aktuell nicht aufloesbar
- zusaetzlicher sichtbarer Browser-Befund ueber Gemini am `2026-03-31`:
  - `home.prinz-stockenweiler.de` zeigt das `Home Assistant`-Frontend, aber dort sofort `Unable to connect to Home Assistant`
  - `papierkram.prinz-stockenweiler.de/dashboard` endet sichtbar in `ERR_CONNECTION_TIMED_OUT`
  - `cloud.prinz-stockenweiler.de/apps/dashboard/` endet sichtbar in `ERR_SSL_UNRECOGNIZED_NAME_ALERT`
  - `pve.prinz-stockenweiler.de` endet sichtbar in `ERR_NAME_NOT_RESOLVED`
- expliziter Public-Truth-/DynDNS-Befund am `2026-03-31`:
  - `home.prinz-stockenweiler.de` und `cloud.prinz-stockenweiler.de` laufen DNS-seitig ueber `yourparty.tech` auf `91.14.44.20`
  - `papierkram.prinz-stockenweiler.de` zeigt separat direkt auf `80.134.168.100`
  - `pve.prinz-stockenweiler.de` hat aktuell keinen DNS-Eintrag
- damit ist der sichtbare Legacy-Host-Zustand aktuell: ein Frontend antwortet noch teilweise, drei Kernpfade sind klar kaputt
- lokale Browser-Spuren auf `StudioPC` bestaetigen alte Arbeitsziele:
  - `Chrome`: `https://home.prinz-stockenweiler.de/dashboard-bereiche`
  - `Edge`: `https://papierkram.prinz-stockenweiler.de/dashboard`
  - `Edge`: `https://papierkram.prinz-stockenweiler.de/documents?...`
  - `Edge`: `https://cloud.prinz-stockenweiler.de/apps/dashboard/`
  - `Edge`: `http://adguard.alopri/`
- `Windows Recent` auf `StudioPC` zeigt zusaetzlich den UNC-Pfad `\\\\192.168.178.120\\scans\\Familie Prinz`; das ist ein starker Alt-Hinweis auf einen SMB-/Scan-Pfad und kollidiert mit dem Router-Export, der `.120` aktuell als `MagentaTV` fuehrt
- `cmdkey /list` auf `StudioPC` zeigt einen gespeicherten Domaintarget-Eintrag `192.168.178.187` mit Benutzer `Scanner`; das ist ein starker lokaler Hinweis auf einen Scan-/SMB-Endpunkt
- `HKCU:\\Network\\Z` auf `StudioPC` bestaetigt einen alten gemappten Pfad `\\\\192.168.178.25\\music` mit Benutzer `wolf`
- `MountPoints2` auf `StudioPC` zeigt zusaetzlich die Explorer-Spuren `\\\\192.168.178.120\\music` und `\\\\192.168.178.187\\ScansDrucker`
- lokaler `Tailscale`-Status auf `StudioPC` zeigt aktuell nur `192.168.2.0/24` via `toolbox`; ein Stockenweiler-Subnetzpfad ist damit noch nicht sichtbar
- lokales `AnyDesk` auf `StudioPC` liefert mehrere verwertbare Remote-ID-Kandidaten, aber noch keine gesicherte Zuordnung zu heutigem Haupt-PC oder Handy
- damit ist klar: die Rolle von `.120`, `.187` und dem `music`-Pfad auf `.25` muss im ersten Live-Onboarding sichtbar aufgeloest werden, statt sie zu erraten
- `.ssh/known_hosts` auf `StudioPC` zeigt fuer `192.168.178.172` und `192.168.178.25` denselben `SSH`-Hostkey; das ist ein starkes lokales Signal, dass der alte `Proxmox`-Host von `.172` auf `.25` umgezogen ist
- der ehemalige Haupt-PC-Anker fuer diesen Altstand war laut Operator dieser `StudioPC`; alte Zugangspfade sollten daher zuerst hier gesucht und gesichtet werden

## Integrationsprinzip

- Stockenweiler bleibt erst einmal ein getrennter betreuter Support-Standort
- kein direktes Vermischen der internen FRAWO-Infrastruktur mit dem Elternhaus-LAN
- spaetere Kopplung nur `management-first`, nicht `service-merge-first`
- die Standorte sollen sich spaeter moeglichst ergaenzen:
  - z. B. Backup-/Storage-Kapazitaet in Stockenweiler
  - aber nicht als ungepruefte Sofort-Heirat der Standorte
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
   - lokaler Scan-Ordnerpfad
   - HDD-/Filesystem-Wahrheit auf `192.168.178.25`
   - Zielablage: `manifests/stockenweiler/site_inventory.json`
2. Remote-Support-Standard pruefen:
   - `Tailscale`
   - `AnyDesk` nur Fallback
   - sichtbar pruefen, ob ein Stockenweiler-Subnetzpfad oder ein gemappter `AnyDesk`-Endpunkt zuerst verfuegbar gemacht werden kann
3. getrennten Secret-Bereich `Stockenweiler` in `Vaultwarden / FraWo` nur mit echten Daten befuellen
4. lokalen Scan-Pfad fuer die Eltern stabilisieren; keine `Paperless`-Automatisierung in `V1`
5. keine WAN-Freigabe und kein Site-to-Site-VPN in V1
6. sobald irgendein gangbarer Remote-Pfad oder LAN-Zugang da ist:
   - read-only Probe `python scripts/stockenweiler_pve_storage_probe.py`
   - Ziel: Hostname, Blockdevice-Basis, Filesystem-Nutzung, `pvesm status`
   - aktueller Befund `2026-03-31`: `pve-manager/9.1.4`, `/mnt/data_family` auf `sdb1` und `/mnt/music_hdd` auf `sda2` jeweils `100%` voll, `hdd-backup` ebenfalls `100%` belegt
   - daraus folgt: spaetere PBS-/Storage-Tauglichkeit bleibt moeglich, braucht aber erst Kapazitaetsbereinigung oder Neuzuschnitt
7. fuer die oeffentliche Legacy-Wahrheit bei Bedarf:
   - `python scripts/stockenweiler_public_truth_check.py`
   - Ziel: DNS-/DynDNS-Zielpfade und HTTPS-Zustand reproduzierbar pruefen
8. fuer den aktuellen Remote-Zugriffspfad:
   - `python scripts/stockenweiler_remote_path_probe.py`
   - Ziel: `Tailscale`-Route, `ssh stock-pve` und lokaler `AnyDesk`-Fallback in einem read-only Truth-Report zusammenziehen

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
- `Radio`: spaeterer Host nur nach Hardware-/Stabilitaetskriterium, nicht nach Standortideologie
- `WordPress / Website`: erst spaeterer Kandidat, wenn Bedarfs- und Inhaltsbild klar ist
- `Paperless / Nextcloud`: lokale Scan-Ordner zuerst, spaeter eventuell eigener Stockenweiler-`Paperless`-Pfad
- `SMB / Scan`: explizit lokal halten, bis `\\\\192.168.178.120\\scans\\Familie Prinz` fachlich aufgeloest ist
- `PBS / Storage`: spaeterer Kandidat ueber die HDDs am Stockenweiler-`Proxmox`, aber nur mit dokumentierter Disk-Wahrheit und Rollback

### Migration Blockers

- `Lane A` ist noch aktiv
- Haupt-PC ist nicht verifiziert
- Handy ist nicht verifiziert
- primaerer Remote-Pfad ist noch nicht an einem echten Supportfall bewiesen
- Rolle von `192.168.178.120` ist noch nicht aufgeloest
- `FRITZ!Box`-/`Tailscale`-Faehigkeit fuer spaetere Management-Kopplung ist noch nicht sichtbar bestaetigt
- Upload-/Latenzprofil ist noch nicht dokumentiert
- Disk-Inventar und PBS-Tauglichkeit auf `192.168.178.25` sind noch nicht dokumentiert

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
- `music`-Share-Host und Benutzerpfad
- `ScansDrucker`-/Scan-Host und aktueller SMB-Pfad
- aktueller lokaler Scan-Ordnerpfad fuer die Eltern
- lokales HDD-/Filesystem-Bild auf `192.168.178.25`

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
- zuerst den lokalen Stockenweiler-Scan-Ordner stabil halten
- keinen FRAWO-Business-Dokumentenpfad als Standard unterjubeln
- spaetere `Paperless`-Automatisierung nur als eigener Stockenweiler-Pfad

# FraWo GbR - Homeserver 2027 Masterplan

## Zweck

Diese Datei ist die zentrale Gesamt-Roadmap bis zu einem fertig aufgebauten Homeserver, der den Anspruch an professionelle, nachvollziehbare und sicher betriebene IT erfuellt. Detailfragen bleiben in den Fachdokumenten, aber die strategische Linie steht hier an einer Stelle.

## Aktuelles Lane-Modell

Dieses Lane-Modell ist ab jetzt die verbindliche Arbeitsordnung. Aeltere breite Roadmap-Texte bleiben als Kontext erhalten, aber der aktive Takt folgt nur noch dieser Priorisierung:

- `Lane A: MVP Closeout` -> `done` (Data Restored & SSOT Sealed 2026-04-17)
- `Lane B: Website/Public` -> `active` (HTTPS/Public-Edge baseline aktiv; Design/Content duerfen vorlaeufig bleiben)
- `Lane C: Security/PBS/Infra` -> `active` (Recovery confirmed, Dashboard cleaned)
- `Lane D: Stockenweiler` -> `watch`
- `Lane E: Radio/Media` -> `active` (Media ready, 1,937 tracks verified in toolbox, Radio blocked by offline Pi)

Regeln (Stand 2026-04-11, nach Lane-A-Abschluss):

- `Lane A` ist abgeschlossen. `release-mvp-gate` = `MVP_READY` mit `0` offenen Blockern.
- `Lane B` ist jetzt der aktive Track: fuer `www.frawo-tech.de` zuerst die HTTPS/Public-Edge-Baseline abschliessen; Design und Content koennen vorlaeufig bleiben.
- `Lane C`, `D` und `E` bleiben sichtbar und werden nach Lane-B-Entscheid priorisiert.
- PBS-Rebuild, Surface-Recovery und Radio-Vollintegration bleiben Vollzertifizierungs-Track.

## Kanonische Steuerdateien

Diese Rollen gelten ohne Ausnahmen:

- `AI_SERVER_HANDOFF.md`
  - externer KI-Handoff
- `DOCS/Task_Archive/OPERATOR_TODO_QUEUE.md`
  - nur manuelle Unblock-Punkte
- `artifacts/release_mvp_gate/latest_release_mvp_gate.md`
  - einzige Wahrheit fuer die MVP-Entscheidung
- `GEMINI.md`
  - nur delegierbare Browser- und Operator-Jobs
- `manifests/work_lanes/current_plan.json`
  - maschinenlesbare Lane-Quelle

Jede neue Aufgabe wird ab jetzt mit genau diesen Feldern beschrieben:

- `lane`
- `goal`
- `done_when`
- `blocked_by`
- `next_operator_action`
- `next_codex_action`

## Zielbild

Der Zielzustand ist eine konsolidierte, ressourceneffiziente Dual-Node-Infrastruktur ohne Doppelbelastungen, professionell aufgeteilt in "Business/AI" und "Media/IoT".

### Node 0: Lead (Admin Orchestrator & SSOT)
- `wolfstudiopc` (100.98.31.60): **Primärer Lead-Knoten**. Alle Änderungen werden hier zentral konsolidiert. Andere Geräte (z.B. Surface) fungieren als Remote-Satelliten.

### Node 1: Anker (Business, Automation & AI Layer)
- `VM 220 odoo`: Zentrale ERP- und FraWo-Website-Instanz.
- `VM 200 nextcloud`: Zusammengelegte, Single-Source Dokumenten-Instanz.
- `VM 230 paperless`: Zusammengelegtes, zentrales Dokumentenarchiv.
- `CT 300 n8n`: Automatisierungs-Backend fuer Workflow-Pipelines.
- `VM 310 openclaw`: Isoliertes, sicheres AI-Agent-Environment fuer Vibecoding.
- `CT/VM 211 haos-edge`: Zusaetzliche HA-Ebene zur Steuerung am Anker-Standort.

### Node 2: Stockenweiler (Media, Backup & IoT Lifeboat)
- `VM 210 haos`: Zentrale Smart-Home-Steuerung fuer das Elternhaus.
- `CT 100 media`: Strukturierte Medien-Ebene (AzuraCast, Jellyfin, Media-HDD).
- `CT/VM pbs`: Zentraler Proxmox Backup Server (Anker-Instanz wird obsolet).

### Hardware & Peripherie
- `wolfstudiopc`: **LEAD** Admin-Geraet & SSOT.
- `surface-franz`: Remote-Arbeitsgerät (Satellite).
- `surface-wolfi` (Admin): Remote-Arbeitsgerät (Satellite).
- `kiosk-frontend`: Touch-Kiosk fuer Franz und Wolf (Rebuild offen).
- `zenbook_radio_anchor`: Zukuenftiger Radio-Ankerpunkt.
- `raspberry_pi_radio`: Dedizierter AzuraCast-Node.
- `iphone-15`: Mobiles Primaergeraet Franz.
- `pixel-9-pro`: Mobiles Primaergeraet Wolf.
- `UniFi Cloud Gateway Ultra`: Netzwerkkontrollpunkt & VLANs.

## Professioneller Zielstandard


Der Server gilt erst dann als wirklich fertig, wenn alle folgenden Punkte erfuellt sind:

1. Alle Zielsysteme sind gebaut, dokumentiert und reproduzierbar ueber IaC pflegbar.
2. Inventar, IP-Plan, Hostrollen und Verantwortlichkeiten sind eindeutig.
3. Interne Erreichbarkeit laeuft kontrolliert ueber DNS, Reverse Proxy und Tailscale.
4. Backups sind nicht nur konfiguriert, sondern mit Restore-Drills praktisch bewiesen.
5. Sicherheitsbasis ist nachweisbar:
   - keine unnoetigen Admin-Flaechen im LAN
   - keine offenen Datenbankports
   - keine direkte Internet-Exposition von Admin-UIs
   - saubere Snapshot- und Rollback-Pfade
6. Der Netzrand ist kontrolliert:
   - Easy Box nur Uebergang
   - spaeter UCG-Ultra mit geplantem Cutover
7. Oeffentliche Freigaben passieren nur ueber einen gehaerteten Edge-Pfad mit DNS, TLS, Auth, Logging und Monitoring.

## Operator Shortcuts

- Operator Home: `OPS_HOME.md`
- Executive Roadmap: `EXECUTIVE_ROADMAP.md`
- Gesamtstatus: `PLATFORM_STATUS.md`
- Identitaetsstandard: `IDENTITY_STANDARD.md`
- Tool-Betriebsanweisungen: `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
- Vaultwarden-Referenzregister: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Business-MVP-Gate: `artifacts/release_mvp_gate/.../release_mvp_gate.md`
- Website-Release-Gate: `artifacts/website_release_gate/.../website_release_gate.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden + STRATO Uebergang: `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`
- Mobile-Scan-Workflow: `MOBILE_SCAN_WORKFLOW.md`
- Stress-Test-Readiness: `STRESS_TEST_READINESS.md`
- Stockenweiler / Rentner OS: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
- Anker + Stockenweiler Gesamtpfad: `ANKER_STOCKENWEILER_MARRIAGE_PLAN.md`
- AI-Arbeitsmodell: `AI_OPERATING_MODEL.md`
- Hosting-Optionen: `ONLINE_HOSTING_OPTIONS.md`
- Google-Drive-Plan: `GOOGLE_DRIVE_INTEGRATION_PLAN.md`
- Odoo-Studio-Entscheidung: `ODOO_STUDIO_DECISION.md`
- 2-TB-SSD-Bewertung: `TB_SSD_ASSESSMENT.md`

## Operator Note 2026-03-25

- Auf `wolfstudiopc` war ein echter Routing-Fehler aktiv: Tailscale hat das von `toolbox` annoncierte Subnetz `192.168.2.0/24` akzeptiert und damit den direkten LAN-Pfad auf diesem PC uebersteuert.
- Der Workstation-Fix ist gesetzt: `tailscale set --accept-routes=false`.
- Damit ist die lokale Route auf diesem Admin-PC wieder priorisiert.
- Wenn Legacy-Pfade unter `192.168.2.x` trotzdem nicht sauber antworten, ist das als Infrastrukturpfad-Thema zu behandeln, nicht vorschnell als App-Defekt.

### Live-Stand nach Recovery (2026-04-19)

> [!NOTE]
> **Core platform recovered.** Proxmox, toolbox frontdoor, Toolbox-DNS und die zentrale SSOT sind wieder auf einem professionell gefuehrten Betriebsstand.

- `VM 220 odoo`: LIVE auf `10.1.0.22:8069`. Database `FraWo_Live` restored. German UI active.
- `VM 200 nextcloud`: LIVE auf `10.1.0.21`.
- `VM 230 paperless`: LIVE auf `10.1.0.23`.
- `VM 210 haos`: LIVE auf `10.1.0.24:8123`.
- `CT 100 toolbox`: LIVE auf `10.1.0.20`; mobiler Frontdoor und Split-DNS laufen wieder ueber `100.82.26.53`.
- `CT 110 Storage-Node`: LIVE. SMB Source of Truth verified.
- **ACTIVE: Lane B Deployment** (Public Edge / HTTPS / Tunnel).

### Bewusst getrennt oder aktuell blockiert

- Easy-Box-Leases und DHCP-Reservierungen sind noch nicht final abgeglichen.
- `PBS` ist nicht produktiv gruen:
  - `VM 240 pbs` existiert, ist aber im aktuellen Live-Audit gestoppt
  - Datastore, Proof-Backup und Restore-Pfad sind nicht freigegeben
  - der guarded Rebuild-Pfad ist vorbereitet, der produktive Betrieb aber blockiert
- USB-Dongles fuer HAOS sind noch nicht am Host sichtbar.
- AdGuard ist noch nicht primaerer LAN-DNS.
- Split-DNS fuer entfernte Tailscale-Clients ist technisch vorbereitet, aber noch nicht final administrativ ausgerollt:
  - der restricted nameserver fuer `hs27.internal` muss auf `100.82.26.53` zeigen, nicht auf `10.1.0.20`
- UCG-Ultra ist inzwischen Teil des aktiven Uebergangsnetzes.
- der UCG-Pfad ist aktuell bewusst vom akuten Website-Cutover getrennt:
  - das VLAN-/Subnetz-Zielbild bleibt `UCG-Ultra` und ist bereits veroeffentlicht
  - offen sind jetzt Firewall-Politik, Proxmox-VLAN-Trunk-Adoption und die geordnete Service-Migration
  - der aktuelle Public-Website-Cutover bleibt deshalb ein eigener Edge-Block und nicht Teil des laufenden UCG-Service-Uebergangs
- Public Edge ist bewusst noch nicht live.
- Public-Domain-Stand ist bereits real sichtbar, aber nicht release-faehig:
  - `frawo-tech.de` und `www.frawo-tech.de` loesen oeffentlich jetzt auf `92.211.33.54` und `2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc` auf
  - `www.frawo-tech.de` folgt aktuell sauber auf `frawo-tech.de`
  - HTTP ist jetzt fachlich richtig:
    - Apex liefert `308` auf `https://www.frawo-tech.de/`
    - `www` liefert die echte FraWo-Odoo-Website
  - HTTPS ist im Live-Check aktuell nicht gruen
  - `DMARC` ist sichtbar, `SPF` aktuell nicht
  - letzter Website-Audit: `artifacts/website_release_audit/20260330_155726`
  - letzter Website-Gate-Entscheid: `artifacts/website_release_gate/20260330_155801/website_release_gate.md` = `BLOCKED`
  - letzter Zielpfad-Preview: `artifacts/public_edge_preview/20260330_134359/report.md` = `passed`
  - der Website-Track ist jetzt nativ ohne WSL neu pruefbar
  - sichtbare Browser-Abnahme bestaetigt den Ist-Stand:
    - `www`-HTTP zeigt die echte FraWo-Seite
    - Apex-HTTP redirectet korrekt
    - HTTPS scheitert weiter mit `ERR_SSL_PROTOCOL_ERROR`
  - der Website-Inhalt selbst ist auf `VM220` jetzt korrekt vorbereitet:
    - Host `www.frawo-tech.de` auf `10.1.0.22` -> `Home | FraWo`
    - Host `frawo-tech.de` auf `10.1.0.22` -> `308` auf `https://www.frawo-tech.de/`
    - Host `www.frawo-tech.de` auf `/radio/public/frawo-funk` -> `FraWo - Funk - AzuraCast`
  - `VM220` besitzt bereits eine globale IPv6 `2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc`, die auf HTTP fuer `www.frawo-tech.de` antwortet
  - `public-dualstack-edge-check` ist jetzt explizit rot:
    - `curl -6` gegen Apex und `www` auf Port `80` ist gruen
    - `curl -4` gegen Apex und `www` auf Port `80` ist weiter rot
  - Caddy auf `VM220` ist auf `80/443` aktiv; ACME trifft jetzt den richtigen Zielpfad, scheitert aber aktuell mit `92.211.33.54: Connection refused`
- Verbindlicher Release-Scope fuer `2026-04-01` bleibt die Website auf `www.frawo-tech.de`, getragen durch die Odoo-Website mit sichtbarer Radio-Praesenz; interne Business-UIs bleiben intern oder Tailscale-only.
- `frawo-tech.de` bleibt die bevorzugte Hauptdomain fuer Website und spaetere Edge-Freigaben.
- `yourparty.tech` wird aufgeloest und ist Legacy-Kontext; `frawo-tech.de` ist die neue Primaerdomain fuer Website und Business.
- `online-prinz.de` bleibt der Zielname fuer den getrennten Fernwartungs- und Familienbetriebspfad in Stockenweiler (Rentner OS).
- internes `hs27.internal` bleibt bis zu einer bewusst geplanten DNS-Migration die aktive interne Betriebszone.
- `Radio/AzuraCast` ist aktuell operativ blockiert:
  - `radio-node` antwortet weder auf `192.168.2.155` noch auf `100.64.23.77`
  - die Toolbox-Frontdoor liefert deshalb auf `:8448` aktuell `502`
- `Jellyfin` bleibt technisch verfuegbar, gehoert aber nicht zum aktuellen Business-MVP-Freigabesignal.
- `media.hs27.internal`, `10.1.0.20:8096` und der mobile Tailscale-Pfad `100.82.26.53:8449` bleiben nutzbar, sind aber bewusst ein separater Ausbaupfad.
- Medien- und Wohnzimmerpfade bleiben fuer den laufenden Betrieb hilfreich, zaehlen aber nicht zum aktuellen Business-MVP-Gate.
- `kiosk-frontend` ist im aktuellen Live-Audit nicht betriebsbereit; der naechste professionelle Schritt ist ein `clean rebuild`.
- Historische Surface-Haertungen bleiben relevant, ersetzen aber nicht den aktuellen Rebuild-Bedarf.
- Repo- und Launcher-Stand fuer das Surface ist vorbereitet; die produktive Aussage bleibt trotzdem: Geraet aktuell nicht bereit.
- Der kleine USB-Zwischenpfad bleibt historischer Zwischenstand; fuer den naechsten sauberen PBS-Schritt zaehlt nur der guarded Rebuild auf freigegebener Hardware.
- Alte positive Surface-Verifikationen sind ueberholt und duerfen nicht mehr als aktueller Live-Stand gelesen werden.
- `wolfstudiopc` ist joined und als Admin-Geraet etabliert (`100.98.31.60`).
- `Zenbook` ist vorbereitet fuer die spaetere Migration als Radio-Anker.
- Der akute local-lvm-Thinpool-Incident ist behoben (Restored 2026-04-17).
- Alle VMs sind stabil und disk-io-errors wurden durch Snapshot-Bereinigung geloest.

### Strategischer Arbeitsmodus ab jetzt

- `release-mvp-gate` bewertet nur den Business-Kern.
- `website-release-gate` bewertet nur den oeffentlichen Website-Track.
- `production-gate` bleibt unveraendert streng fuer den Vollscope.
- der aktuelle Website-Track ist technisch ehrlich eingegrenzt:
  - Public DNS gruen
  - HTTP-Redirect gruen
  - HTTPS rot
  - Public-Mail-DNS rot
- der aktuelle Lane-B-Zielzustand ist bewusst kleiner als ein voller Website-Release:
  - zuerst gueltiges HTTPS und sauberer Public Edge
  - Design, Feintuning und Content-Reife duerfen bis spaeter provisorisch bleiben
- der aktuelle Website-Track ist fachlich nicht mehr am Odoo-Inhalt blockiert, sondern am externen Cutover:
  - `VM220` ist als Public-Origin vorbereitet
  - `STRATO` zeigt jetzt auf den echten Zielpfad
  - IPv4-Forward ist noch nicht sichtbar
  - Zertifikate koennen deshalb noch nicht erfolgreich ausgestellt werden
- `PBS`, `surface-go` und `Radio/AzuraCast` werden weiterbearbeitet, blockieren aber nicht mehr den internen Business-MVP-Release.
- Website-Release und Vollzertifizierung laufen ab jetzt bewusst auf getrennten Spuren.


## Roadmap Nach Phasen

## Phase 1 - Fundament und SSOT

Ziel:
- klare Source of Truth
- feste Routinen
- keine Altlasten

Status:
- abgeschlossen

Ergebnisse:
- `README.md`
- `LIVE_CONTEXT.md`
- `GEMINI.md`
- `MEMORY.md`
- `NETWORK_INVENTORY.md`
- `VM_AUDIT.md`
- Morgen-/Abendroutinen

## Phase 2 - Business-Plattform stabilisieren

Ziel:
- Nextcloud, Odoo und Paperless produktionsfaehig und reproduzierbar betreiben

Status:
- abgeschlossen

Ergebnisse:
- IaC-Pfade unter `/opt/homeserver2027/stacks`
- systemd-gesteuerte Compose-Stacks
- QGA auf allen relevanten Business-VMs
- Drift-Checks und Basis-Haertung

## Phase 3 - Netzwerkbasis intern aufbauen

Ziel:
- interner Frontdoor
- internes DNS
- sicherer Remote-Zugriff ohne oeffentliche Freigaben

Status:
- weitgehend abgeschlossen

Ergebnisse:
- Caddy auf `CT 100`
- AdGuard Home opt-in
- `hs27.internal`
- `portal.hs27.internal`
- Tailscale joined
- mobiler Tailscale-Frontdoor auf `8442-8449`
- `cloud.hs27.internal`
- `odoo.hs27.internal`
- `paperless.hs27.internal`
- `ha.hs27.internal`

Rest:
- `hs27.internal` bleibt die aktive Betriebszone, bis eine geplante DNS-Migration erfolgt
- spaeterer professioneller Zielpfad fuer interne Namen ist `frawo.home.arpa`
- `frawo.internal` und `frawo.lan` werden nicht als neue Zielzone eingefuehrt
- Pilot-Clients fuer AdGuard definieren
- DNS-Rollback fuer spaetere Promotion dokumentieren
- Pilot- und Rollback-Runbook ist jetzt in `ADGUARD_PILOT_ROLLOUT_PLAN.md` festgezogen; Ausfuehrung bleibt offen
- Tailnet-DNS fuer mobile Clients ist jetzt fuer `hs27.internal` ueber restricted nameserver vorbereitet und auf dem ZenBook erfolgreich verifiziert
- der korrekte restricted nameserver fuer entfernte Tailscale-Clients ist `100.82.26.53`; die administrative Finalisierung im Tailscale-Panel bleibt offen
- Split-DNS-Runbook ist jetzt in `TAILSCALE_SPLIT_DNS_PLAN.md` festgezogen und im Tailnet fuer den ZenBook-Testpfad erfolgreich umgesetzt
- Rightsizing von `VM 200` und `VM 220` in ein Wartungsfenster einplanen
- `portal.hs27.internal` spaeter vom statischen Frontdoor in eine bewusst gestaltete interne Projektstartseite ueberfuehren

## Phase 4 - HAOS & VLAN 101 Migration [COMPLETED]

Ziel:
- Home Assistant & Core Business Services professionell in VLAN 101 integriert

Status:
- **ERLEDIGT (2026-04-10)**

Ergebnisse:
- Alle VMs (200, 210, 220, 230) in VLAN 101 (`10.1.0.x`) migriert.
- AdGuard Home (CT 100) nutzt **DNS-over-HTTPS (DoH)** um EasyBox-Interception zu umgehen.
- Tailscale Subnet Routing fuer `10.1.0.0/24` aktiv und verifiziert.
- `ha.hs27.internal` und andere Dienste stabil erreichbar.

Rest:
- USB-Hardware anschliessen
- Vendor/Product-ID-Audit
  - aktueller Guardrail: der am Host sichtbare externe USB-Pfad ist nur der PBS-Backup-Stick, nicht ein HAOS-Dongle
- USB-Passthrough einrichten
- spaeter Add-on-Standard und Snapshot-Routine vor Updates festziehen

## Phase 5 - Backup und Disaster Recovery auf Produktionsniveau

Ziel:
- von lokalem Zwischenstandard zu echter Backup-Architektur

Status:
- blockiert fuer Vollzertifizierung, fuer den aktuellen Business-MVP nicht im Scope

Erreicht:
- lokaler `vzdump`-Standard
- timerbasierter Night-Run
- Odoo-Restore-Proof
- PBS-Runner, ISO und Stage-Gates vorbereitet
- guarded Rebuild-Pfad fuer `VM 240 pbs`
- Device-Inventory, Contract-Check und Datastore-Prepare-Guardrails fuer PBS

Aktueller Live-Stand:
- `VM 240 pbs` existiert, ist aber aktuell `stopped`
- der produktive PBS-Datastore ist nicht gruen
- Proof-Backup und Restore-Proof sind im aktuellen Live-Audit nicht erbracht
- der USB-/Datastore-Pfad bleibt bewusst safety-gated, damit kein falsches Medium formatiert wird

Naechster sauberer Pfad:
1. dedizierten Boot-USB und dedizierten Datastore bereitstellen
2. Seriennummern im PBS-Device-Contract freigeben
3. guarded Datastore-Prepare ausfuehren
4. `VM 240` sauber rebuilden
5. ersten echten PBS-Proof-Backup- und Restore-Drill nachweisen

## Phase 6 - Inventar und Netzgovernance finalisieren

Ziel:
- kein unbekanntes Geraet mehr im produktiven Netz
- saubere IP- und Reservierungsstrategie

Status:
- in Arbeit

Offene Punkte:
- unbekannte Hosts `.141` bis `.144`
- restliche Feinarbeit aus dem Router-Ueberblick:
  - sekundere Alias-/Raumzuordnung fuer bereits gesichtete Labels wie `RE355` und `iPhone-3-Pro`
  - finale Shelly-/Repeater-Disambiguierung mit aktuellem Lease-Stand

Definition of done:
- Lease-Tabelle abgeglichen
- DHCP-Reservierungen fuer Infrastruktur gesetzt oder sauber dokumentiert
- `unknown-review` leer
- Browser-first Arbeitsweg ist jetzt in `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` dokumentiert

## Phase 6a - Shared Frontend Node Surface Go

Ziel:
- gemeinsames internes Frontend fuer Franz und Wolf
- Kiosk-first statt ueberladener Desktop

Status:
- blockiert, nicht Teil des aktuellen Business-MVP

Erreicht:
- Repo-Standard fuer das Geraet ist vorbereitet
- Audit- und Rebuild-Pfad fuer das Frontend-Geraet existiert

Rest:
- aktueller Live-Audit sieht `SSH`, `HTTP` und `HTTPS` geschlossen
- naechster professioneller Schritt ist ein `clean rebuild`
- danach Rebuild-Pfad erneut ausrollen und visuell abnehmen
- feste DHCP-Reservierung und optionales Hardware-Tuning erst nach stabilem Grundzustand

## Phase 6b - Raspberry Pi Radio Node

Ziel:
- dedizierter interner Radio-Node statt Medienlast auf `CT 100`

Status:
- blockiert, nicht Teil des aktuellen Business-MVP

Erreicht:
- Raspberry-Pi-Image ist lokal verifiziert
- Zielmedium ist identifiziert
- Zielarchitektur fuer `AzuraCast` ist als separater Pi-Node festgelegt
- Reverse-Proxy-/Frontdoor-Pfad fuer `radio.hs27.internal` existiert
- Radio-spezifische Audit-Checks sind im Repo vorhanden

Rest:
- aktueller Audit-Stand ist `rpi_radio_integrated=no`
- aktueller Audit-Stand ist `rpi_radio_usb_music_ready=no`
- `radio-node` antwortet aktuell weder auf `192.168.2.155` noch auf `100.64.23.77`
- die mobile Frontdoor auf `100.82.26.53:8448` liefert deshalb aktuell `502`
- der naechste echte Hebel ist Vor-Ort-Recovery: Strom, LEDs, Boot und LAN-Link pruefen
- SSH-/Betriebspfad auf dem Pi sauber wiederherstellen
- SMB-/Stationspfad und Medienlayout real verifizieren
- sichtbaren SMTP-/Benachrichtigungspfad fuer `AzuraCast` erst danach finalisieren

## Phase 6c - Interner Medienserver

Ziel:
- sofort nutzbarer Medien-Mehrwert fuer Browser, Thomson und Google TV ohne Public Edge

Status:
- Baseline abgeschlossen, SMB-Cutover technisch live; Client- und Benutzerrollout offen

Erreicht:
- Jellyfin laeuft auf `CT 100 toolbox`
- `media.hs27.internal` liefert intern die Jellyfin-Oberflaeche
- der direkte LAN-Pfad `10.1.0.20:8096` ist verifiziert
- der mobile Tailscale-Frontdoor auf `100.82.26.53:8449` ist verifiziert
- alle drei Pfade liefern aktuell konsistent `HTTP 302 -> /web/`
- Bibliotheks-Stammverzeichnisse auf der Toolbox sind vorbereitet:
  - `/srv/media-library/movies`
  - `/srv/media-library/shows`
  - `/srv/media-library/music`
  - `/srv/media-library/homevideos`
- der produktive SMB-Pfad ist hostseitig auf Proxmox nach `/mnt/hs27-media` gemountet und per Bind-Mount nach `CT 100` durchgereicht
- der Docker-Bind in Jellyfin ist auf `rslave` gehaertet, damit der SMB-Inhalt im Container sichtbar bleibt

Rest:
- Jellyfin-Zugaenge in `Vaultwarden / FraWo / Media` uebernehmen
- erste Thomson-/Google-TV-Clients verbinden
- optionale PIN-Feinarbeit spaeter im Jellyfin-UI setzen

## Phase 6d - Single Source of Truth Storage Node (CT 110)

Ziel:
- Dokumente (Paperless/Nextcloud) und Medien (Radio/Jellyfin) als Single Source of Truth buendeln, anstatt isoliert mit Rsync zu jonglieren.

Status:
- live und in aktiver Integration; SMB ist produktive Source of Truth

Erreicht:
- `CT 110 storage-node` ist angelegt und laeuft im Netz auf `192.168.2.30`
- SMB ist fuer den gemeinsamen Medienpfad der verbindliche Zielstandard
- der Windows-/UNC-Zielpfad ist `\\192.168.2.30\Media\yourparty_Libary`
- Toolbox und Pi sind an den SMB-Zielpfad angebunden
- die USB-Radiobibliothek ist vollstaendig in den SMB-Zielpfad gespiegelt
- Architekturpfad fuer gemeinsame Dokumente und Medien ist damit nicht mehr nur theoretisch, sondern infrastrukturell und betrieblich aktiv

Rest:
- SMB-Freigaben auf allen betroffenen Clients sauber und reproduzierbar mounten
- Nextcloud + Paperless auf den finalen gemeinsamen Datenpfad ueberfuehren
- Jellyfin-/AzuraCast-Zugaenge final festziehen und Benutzerstandard nachziehen
- (Optional Any-Sync/Anytype Node aufziehen)

## Phase 7 - Gateway-Cutover auf UCG-Ultra

Ziel:
- professioneller Netzrand mit DHCP-, Firewall- und Segmentierungs-Kontrolle

Status:
- **ERLEDIGT** - UCG laeuft, VLAN-Schema deployed & Migration abgeschlossen.
- **LOESUNG** - DNS-over-HTTPS (DoH) umgeht die Shadowed-Routes/-DNS der EasyBox.

Erreicht (2026-04-03):
- UCG-Ultra am Anker-Standort aktiv
- Dual-WAN konfiguriert (WAN1 primaer, WAN2 Failover)
- VLAN-Schema via UniFi-API deployed:
  - VLAN 100: Anker-Lan (`10.0.0.0/24`)
  - VLAN 101: Anker-Server (`10.1.0.0/24`) -> Proxmox aktiv hier
  - VLAN 102: Anker-DMZ (`10.2.0.0/24`)
  - VLAN 103: Anker-DMZ-Radio (`10.3.0.0/24`)
  - VLAN 104: Anker-IoT (`10.4.0.0/24`) -> isoliert
  - VLAN 105: Anker-Guest (`10.5.0.0/24`) -> internet-only
  - VLAN 110: Stock-Lan (`10.10.0.0/24`) -> VPN-Endpunkt
  - VLAN 111: Stock-Server (`10.11.0.0/24`) -> VPN-Endpunkt
- SSOT: `UCG_NETWORK_ARCHITECTURE.md`
- API-Key: Vaultwarden FraWo / Core Infra / UCG Anker API Key

Ausstehend:
- Firewall-Regeln zwischen VLANs setzen
- Proxmox VLAN-Trunk-Migration (VMs von `192.168.2.x` nach `10.1.0.x`)
- WireGuard VPN zu Stockenweiler (UCG-Ultra <-> FritzBox 5690 Pro)
- StudioPC in VLAN 100 (Anker-Lan) migrieren

## Phase 8 - Public Edge und professionelle Aussenanbindung

Ziel:
- sichere, kontrollierte Oeffnung zur Oeffentlichkeit

Status:
- parallel zum internen Business-MVP
- erster geplanter externer Release am `2026-04-01` bleibt website-first ueber die Odoo-Website mit sichtbarer Radio-Praesenz
- der aktuelle operative Fokus ist aber kleiner: zuerst HTTPS/Public-Edge-Baseline, auch wenn die Website gestalterisch noch nicht final ist

Vorbedingungen:
- interner Business-MVP ueber `release-mvp-gate` technisch und sichtbar freigabefaehig
- Website-Zielsystem ist festgelegt
- Domain, DNS, TLS, Logging, Monitoring und Rollback sind definiert
- SPF, DKIM und DMARC sind sauber dokumentiert und getestet
- produktiver `Vaultwarden / FraWo`-Standard ist eingefuehrt
- FRAWO-Mailpfade bei `STRATO` sind technisch verifiziert
- keine internen Business-UIs sind Teil des Public-Scope

Bevorzugter Zielname:
- `www.frawo-tech.de` fuer die Hauptseite ueber die Odoo-Website
- `radio.frawo-tech.de` spaeter fuer eine dedizierte Radio-/Player-Seite
- `online-prinz.de` als spaeterer externer Support-Kontext im Elternhaus
- internes `hs27.internal` bleibt bis zur bewussten internen DNS-Migration unveraendert
- spaeterer professioneller interner Zielname ist `frawo.home.arpa`

Runbook:
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
- `RELEASE_READINESS_2026-04-01.md`
- `CI_CD_DELIVERY_FACTORY_PLAN.md`

Nie direkt oeffentlich:
- Proxmox
- Toolbox-Admin
- PBS
- AdGuard-Admin
- Home-Assistant-Admin
- Nextcloud-Admin
- Paperless-Admin
- Odoo-Admin

### Delivery-Fabrik fuer Public-Workloads

- Public Delivery wird als `build once, deploy anywhere`-Modell aufgebaut.
- `Coolify` ist dafuer die bevorzugte Open-Source-CD-Schicht, aber nicht die eigentliche CI-Wahrheit.
- Build-/Test-Standard bleibt repo- und registry-basiert, damit Deployments spaeter nicht an einen einzelnen Controller gebunden sind.
- `dev` und `prod` werden als getrennte Umgebungen geplant.
- zwei spaetere DMZ-Webnodes bleiben das Zielbild:
  - `Anker / Rothkreuz` als primaerer Public-Webnode in `VLAN 102`
  - `Stockenweiler` als spaeterer zweiter Public-Webnode fuer Failover/Ergaenzung
- echter dualer Betrieb ueber beide Standorte gilt in `V1` nur fuer stateless public apps; stateful Business-Dienste bleiben zunaechst intern `primary + DR`.

## Phase 9 - Optional / Wishlist

- `Ollama`
  - derzeit nicht sinnvoll auf dem bestehenden Host
  - Wiedervorlage erst bei RAM-Upgrade oder separatem AI-Node
- `Anytype`
  - Integration als lokale SSOT fuer Wissensmanagement
  - Synergie mit der HS27-Infrastruktur pruefen

## Finale Roadmap Ab `2026-03-26`

### Welle 1 - Betriebsstandard jetzt abschliessen

Ziel:
- aus dem internen Arbeitsstand einen professionell fuehrbaren Betriebsstand machen

Reihenfolge:
1. `Vaultwarden / FraWo` technisch steht; jetzt nur noch sichtbar verifizieren:
   - `Franz` sieht `FraWo` und die Kern-Collections
   - sichtbare Stichprobe der importierten Kern-Eintraege
2. das alte Klartext-Register ist aus dem Workspace entfernt; im Repo gelten nur noch `Vaultwarden` und `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
3. `STRATO`-Alias-/Postfachmodell sichtbar final verifizieren:
   - `wolf@frawo-tech.de` als Alias ueber `webmaster@...`
   - `franz@frawo-tech.de` als eigenes Postfach
   - `info@frawo-tech.de` technisch pruefen
   - `noreply@frawo-tech.de` technisch pruefen
4. Wolf- und Franz-Login-Walkthrough fuer `Vault`, `Nextcloud`, `Paperless` und `Odoo` sichtbar abschliessen
5. sichtbare SMTP-Testmails fuer `Nextcloud`, `Paperless` und `Odoo` abnehmen
6. Franz `Surface Laptop` und `iPhone` als produktive Endgeraete sichtbar abnehmen
7. `Vaultwarden`-Recovery-Material offline in zwei getrennten Kopien bestaetigen
8. SPF, DKIM und DMARC fuer die Website-/Mail-Linie dokumentieren und testen
9. `AzuraCast`-SMTP bewusst spaeter separat nachziehen; es blockiert den aktuellen Business-MVP nicht

Definition of done:
- produktive Secrets liegen nicht mehr nur in Markdown-Dateien
- Mail-Identitaeten sind technisch sauber definiert und getestet
- der operative Release- und Support-Pfad ist personengebunden und nachvollziehbar
- `release-mvp-gate` kann auf `MVP_READY` gehen

### Welle 2 - Release `2026-04-01` absichern

Ziel:
- kleiner, sauber kontrollierter erster externer Release

Verbindlicher Scope:
- `frawo-tech.de` -> Redirect auf `www.frawo-tech.de`
- `www.frawo-tech.de` -> oeffentliche FRAWO-Website ueber die Odoo-Website
- sichtbare Radio-Praesenz oder Player-Pfad auf der Website

Explizit nicht im Scope:
- Nextcloud
- Paperless
- Odoo-Admin / ERP-UI
- Home Assistant
- Proxmox
- PBS
- AdGuard
- Toolbox-Adminpfade
- breiter Radio-Public-Rollout

Reihenfolge:
1. `RELEASE_READINESS_2026-04-01.md` auf Gruen ziehen
2. `frawo-tech.de` -> `www.frawo-tech.de` Redirect-Modell finalisieren
3. Website-Zielsystem als Odoo-Website auf `VM220` festziehen, ohne oeffentlichen Adminpfad
4. sichtbare Radio-Praesenz oder Player-Pfad in die Website einbauen
5. TLS-Automation und Monitoring festziehen
6. SPF, DKIM, DMARC und den externen Testlauf fuer DNS, TLS und Mail fahren
7. Rollback fuer DNS-/TLS-/Hostwechsel dokumentiert pruefen
8. erst dann `www.frawo-tech.de` freigeben

Definition of done:
- Website ist extern erreichbar und traegt die sichtbare Radio-Praesenz
- keine Admin-UIs sind oeffentlich
- Rollback ist dokumentiert
- Release ist klein genug, um im Fehlerfall kontrolliert ruecknehmbar zu bleiben
- voller interner `production-gate` ist fuer diesen Website-Release nicht Voraussetzung

Zwischenziel fuer den laufenden Lane-B-Block:
- gueltiges HTTPS fuer `frawo-tech.de` und `www.frawo-tech.de`
- sauberer Public-Edge-Pfad auf `VM220`
- inhaltlich darf die Website bis zum spaeteren Design-Finishing vorlaeufig bleiben

### Welle 3 - Stockenweiler / `Rentner OS` v1 vorbereiten

Ziel:
- den Elternhaushalt als ersten externen Testkunden kontrolliert aufnehmen

Verbindlicher Scope:
- verwalteter Haupt-PC
- verwaltetes Handy
- Scanner-/Dokumentenpfad
- Drucker-/Peripheriehilfe
- Fernhilfe bei Technikproblemen

Verbindliches Zugriffsmodell:
- `Tailscale-only`
- `AnyDesk` nur als GUI-/Benutzerfallback
- keine offenen WAN-Ports
- keine oeffentlichen Elternhaus-Adminflaechen

Reihenfolge:
1. `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md` als Betriebsrunbook nutzen
2. ersten Geraete- und Providerbestand erfassen
3. getrennten Secret-Bereich `Stockenweiler` in `Vaultwarden / FraWo` befuellen
4. ersten echten Remote-Support-Pfad testen
5. dokumentierten Dokumenten-/Scanpfad nur ueber den Standard-Workflow anbinden

Definition of done:
- erster externer Supportfall ist technisch kontrollierbar
- keine Vermischung mit den internen FRAWO-Adminpfaden
- der Support kann von hier aus eingreifen, ohne das Elternhaus offen ins Internet zu stellen

### Welle 4 - Nach dem ersten Release

Ziel:
- erst nach stabilem Betriebs- und Release-Standard die Plattform verbreitern

Dann folgen:
1. `radio.frawo-tech.de` nur spaeter als separater dedizierter Radio-Pfad bei eigenem Green Gate
2. Surface-Recovery und `kiosk-frontend`-Pfad
3. UCG-Ultra-Cutover
4. 2-TB-SSD-Endrolle festziehen
5. Google-Drive-Integration spaeter ueber den bestehenden `rclone`-/Nextcloud-Pfad

## Was jetzt als Naechstes dran ist

Lane A und der Recovery-/SSOT-Block sind abgeschlossen. Der echte Rest folgt jetzt in dieser Reihenfolge:

1. **Split-DNS finalisieren**: restricted nameserver fuer `hs27.internal` im Tailscale-Admin auf `100.82.26.53` setzen.
2. **Radio-Node wiederbeleben**: Vor-Ort-Recovery fuer `radio-node`, damit `100.82.26.53:8448` nicht mehr `502` liefert.
3. **HTTPS/Public-Edge-Baseline schliessen**: `frawo-tech.de` und `www.frawo-tech.de` ueber Cloudflare-Proxy oder einen echten Dual-Stack-/IPv4-Pfad mit gueltigem HTTPS gruen ziehen; Design/Content duerfen dabei vorlaeufig bleiben.
4. **`wolfstudiopc`-Adminpfad haerten**: OpenSSH oder einen gleichwertigen lokalen Adminpfad sauber freigeben.
5. **Stockenweiler vorbereiten**: Tailscale-only Supportpfad weiterziehen und das abgelaufene Zertifikat fuer `home.prinz-stockenweiler.de` erneuern.
6. **HAOS-USB-Pfad vorbereiten**: Zigbee-/Z-Wave-Hardware stecken, Vendor/Product-ID sauber dokumentieren, dann Passthrough bauen.
7. **PBS guarded rebuilden**: erst mit freigegebener Hardware und echtem Proof-Backup/Restore-Drill.
8. **2-TB-SSD-Strategie final entscheiden**: aktueller Archivpfad ist okay, die Linux-Serverpartition bleibt aber noch offen.
9. **Windows-GUI-Updates kontrolliert nachziehen**: blockierte Apps spaeter mit geschlossenem GUI-/Prozesszustand aktualisieren.

## Speicherfazit

Der Stand zum Speicher ist jetzt professionell klar trennbar:

- der **akute** Speicherengpass ist behoben
- die Plattform ist wieder betriebsfaehig
- die **endgueltige** Speicherarchitektur ist aber noch nicht fertig

Konkret:

- `local-lvm` ist aus dem kritischen Bereich heraus
- `local` ist entlastet
- `CT 110` ist produktive Source of Truth fuer Medien
- die `2-TB`-SSD ist aktuell nur ein kontrollierter Archiv-/Entlastungspfad
- die finale Architekturentscheidung fuer diese SSD steht noch aus

Fuer den internen Stresstest ist das ausreichend.
Fuer den professionellen Dauerstandard folgt spaeter der geplante NTFS-Shrink plus Linux-Serverpartition.

## Die wichtigsten Dateien zum Masterplan

- [MASTERPLAN.md](MASTERPLAN.md)
- [NETWORK_INVENTORY.md](NETWORK_INVENTORY.md)
- [VM_AUDIT.md](VM_AUDIT.md)
- [CAPACITY_REVIEW.md](CAPACITY_REVIEW.md)

- [BACKUP_RESTORE_PROOF.md](BACKUP_RESTORE_PROOF.md)
- [RASPBERRY_PI_RADIO_NODE_PLAN.md](RASPBERRY_PI_RADIO_NODE_PLAN.md)
- [REMOTE_ACCESS_STANDARD.md](REMOTE_ACCESS_STANDARD.md)
- [PBS_VM_240_SETUP_PLAN.md](PBS_VM_240_SETUP_PLAN.md)
- [HAOS_VM_210_SETUP_PLAN.md](HAOS_VM_210_SETUP_PLAN.md)
- [SHARED_STORAGE_ARCHITECTURE_PLAN.md](SHARED_STORAGE_ARCHITECTURE_PLAN.md)

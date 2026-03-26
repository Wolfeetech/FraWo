# Homeserver 2027 Masterplan

## Zweck

Diese Datei ist die zentrale Gesamt-Roadmap bis zu einem fertig aufgebauten Homeserver, der den Anspruch an professionelle, nachvollziehbare und sicher betriebene IT erfuellt. Detailfragen bleiben in den Fachdokumenten, aber die strategische Linie steht hier an einer Stelle.

## Zielbild

Der Zielzustand ist eine hybride Proxmox-Infrastruktur mit klarer Rollentrennung:

- `CT 100 toolbox`
  - Caddy
  - AdGuard Home
  - Tailscale-Subnet-Router
- `VM 200 nextcloud`
  - Dokumentenablage und Kollaboration
- `VM 210 haos`
  - Home Assistant OS mit Supervisor und spaeterem USB-Passthrough
- `VM 220 odoo`
  - ERP, CRM, Rechnungen
- `VM 230 paperless`
  - Dokumentenarchiv
- `VM 240 pbs`
  - dedizierter Proxmox Backup Server
- `wolfstudiopc`
  - primÃ¤res Admin- und BrÃ¼ckengerÃ¤t (dieser PC)
  - SSOT fÃ¼r Netzwerk- und Servermanagement
- `zenbook_radio_anchor`
  - zukÃ¼nftiger Radio-Ankerpunkt ("Villa")
  - Livestream-Host fÃ¼r Studio-Broadcasts
- `raspberry_pi_radio`
  - dedizierter interner Radio-Node mit AzuraCast
- spaeter `surface_go_frontend`
  - gemeinsamer Touch-Kiosk und Frontend-Node fuer Franz und Wolf
- spaeter `UniFi Cloud Gateway Ultra`
  - zentraler Gateway, DHCP- und Firewall-Kontrollpunkt, VLAN-ready

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
- Zugangsregister: `ACCESS_REGISTER.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Bitwarden + STRATO Runbook: `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`
- Mobile-Scan-Workflow: `MOBILE_SCAN_WORKFLOW.md`
- Stress-Test-Readiness: `STRESS_TEST_READINESS.md`
- Stockenweiler / Rentner OS: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
- Hosting-Optionen: `ONLINE_HOSTING_OPTIONS.md`
- Google-Drive-Plan: `GOOGLE_DRIVE_INTEGRATION_PLAN.md`
- Odoo-Studio-Entscheidung: `ODOO_STUDIO_DECISION.md`
- 2-TB-SSD-Bewertung: `TB_SSD_ASSESSMENT.md`

## Operator Note 2026-03-25

- Auf `wolfstudiopc` war ein echter Routing-Fehler aktiv: Tailscale hat das von `toolbox` annoncierte Subnetz `192.168.2.0/24` akzeptiert und damit den direkten LAN-Pfad auf diesem PC uebersteuert.
- Der Workstation-Fix ist gesetzt: `tailscale set --accept-routes=false`.
- Damit ist die lokale Route auf diesem Admin-PC wieder priorisiert.
- Wenn `192.168.2.10`, `192.168.2.20` oder `192.168.2.30` trotzdem nicht sauber antworten, ist das als Infrastrukturpfad-Thema zu behandeln, nicht vorschnell als App-Defekt.

## Aktueller Ist-Stand

### Bereits fertig oder betriebsreif

- Workspace, SSOT, Handoffs und Routinen sind aufgebaut.
- `VM 200`, `VM 220`, `VM 230` laufen stabil aus IaC-Pfaden.
- `VM 200 nextcloud` ist jetzt nicht nur containerseitig, sondern auch applikationsseitig sauber installiert; Admin-User `frawoadmin` und Frontend-User `frontend` sind vorhanden, die Passwoerter liegen verschluesselt im Vault.
- `VM 230 paperless` hat jetzt ebenfalls Admin-User `frawoadmin` und Frontend-User `frontend`; die Passwoerter liegen verschluesselt im Vault.
- zwischen Paperless und Nextcloud ist jetzt ein erster echter Dokumentenpfad live:
  - Nextcloud-Upload nach `Paperless/Eingang`
  - Bruecke im 5-Minuten-Takt in den Paperless-Consume-Pfad
  - OCR-/Archivspiegelung nach `Paperless/Archiv`
- `CT 100` stellt internes Caddy und AdGuard im Opt-in-Betrieb bereit.
- Tailscale auf `CT 100` ist joined und laeuft.
- `VM 210` ist gebaut, stabil auf `192.168.2.24` und intern ueber `ha.hs27.internal` erreichbar.
- Reverse-Proxy-Trust fuer Home Assistant ist gesetzt.
- Lokaler Backup-Zwischenstandard ist live und deckt `VM 200`, `VM 210`, `VM 220`, `VM 230` ab.
- Odoo-Restore-Proof wurde praktisch erfolgreich gezeigt.
- Capacity-Review ist live und bestaetigt: Host-RAM ist der primaere Skalierungsengpass, Nextcloud und Odoo sind aktuell ueberdimensioniert, HAOS ist bewusst knapp aber passend dimensioniert.
- mobiler Tailscale-Frontdoor ueber die Toolbox ist live, Tailscale-only gehaertet und liefert die Kerndienste jetzt ueber `100.99.206.128:8443-8448`
- `portal.hs27.internal` ist live und der mobile Tailscale-Frontdoor deckt jetzt auch das interne Portal auf `100.99.206.128:8447`, Radio auf `:8448` und Media auf `:8449` ab
- das Toolbox-Portal ist jetzt als gruppierte `FRAWO Control`-Frontdoor aufgewertet und bildet Playback-, Work- und Operations-Ziele klarer ab
- die `FRAWO Control`-Frontdoor fuehrt jetzt auch einen Live-Status-Snapshot der Kernservices mit und ist aktuell mit `7/7` gruen
- die `FRAWO Control`-Frontdoor zeigt jetzt zusaetzlich den laufenden Medienimport fuer Jellyfin ueber `status.json`
- `radio.hs27.internal` zeigt jetzt intern auf den Raspberry-Pi-Radio-Node und liefert die AzuraCast-Login-Seite
- `media.hs27.internal` zeigt jetzt intern auf Jellyfin auf der Toolbox; der direkte LAN-Pfad `192.168.2.20:8096` und der mobile Tailscale-Pfad `100.99.206.128:8449` liefern konsistent `HTTP 302 -> /web/`
- der zentrale SMB-Medienpfad auf `CT 110` ist jetzt angelegt; die kanonische Musikbibliothek ist `\\192.168.2.30\Media\yourparty_Libary`
- `CT 100 toolbox` wurde fuer den Medienpfad operativ vergroessert: Rootfs jetzt effektiv `96G`, im Gast aktuell rund `82G` frei statt vorher `64M`
- Der Raspberry-Pi-Radio-Node ist jetzt auf ein konservatives `pi4_2gb_single_station_low_resource`-Profil getunt: `4` CPU-Kerne, `~1.8 GiB` RAM, `2 GiB` Swap, `~21 GiB` freies Rootfs und AzuraCast-Leerlauf aktuell bei `~457 MiB`
- Right-Sizing-Stage-Gate und Wartungs-Runbook fuer `VM 200` und `VM 220` sind einsatzbereit.

### Noch nicht fertig

- Easy-Box-Leases und DHCP-Reservierungen sind noch nicht final abgeglichen, auch wenn Login und der authentifizierte `overview.json`-Pfad jetzt reproduzierbar funktionieren.
- PBS-v1 ist jetzt als Interim-Build live:
  - `VM 240 pbs` ist installiert und im Netz auf `192.168.2.25`
  - Datastore `hs27-interim` liegt auf der USB-gestuetzten `40G`-Gastdisk unter `/mnt/datastore-interim`
  - Proxmox-Storage `pbs-interim` ist aktiv
  - ein taeglicher PBS-Job fuer `200,210,220,230` ist angelegt
  - der erste gruene Proof-Backup- und Restore-Lauf fuer `VM 220` ist erbracht
  - offener Restblock sind jetzt nur noch rotierende weitere Restore-Drills und spaeter groesseres PBS-Storage
- USB-Dongles fuer HAOS sind noch nicht am Host sichtbar.
- AdGuard ist noch nicht primaerer LAN-DNS.
- UCG-Ultra ist noch nicht integriert.
- Public Edge ist bewusst noch nicht live.
- Verbindlicher Release-Scope fuer `2026-04-01` ist nur die Website auf `www.frawo-tech.de`; interne Apps bleiben intern oder Tailscale-only.
- Bevorzugter spaeterer Public-Domain-Pfad ist jetzt `frawo-tech.de` (Strato, GbR-Hauptdomain) mit `www.frawo-tech.de` fuer die GbR-Website und `radio.frawo-tech.de` fuer den Radio-/Player-Pfad.
- `yourparty.tech` (Legacy-Projekt): Restlaufzeit sinnvoll nutzen, danach ggf. abschalten oder redirecten.
- `prinz-stockenweiler.de` (Ionos, Elternhaus): Wolf ist der "Internetangel"; Ziel ist die Fernwartung und Erreichbarkeit aller dortigen Services ("auf dem Server").
- internes `hs27.internal` bleibt bis zur bewussten internen DNS-Migration unveraendert.
- Der dedizierte Radio-Node auf dem Raspberry Pi 4 ist intern live: AzuraCast laeuft auf dem Pi, `radio.hs27.internal` liefert intern `HTTP 302` auf `/login`, und die Status-API ist erreichbar.

- Der Radio-Betrieb ist jetzt auch operativ verifiziert: `Radio`, `Radio Control` und `nowplaying` sind intern gruen; der Pi nutzt den zentralen SMB-Pfad produktiv und die Integrationschecks laufen von diesem Admin-PC jetzt auch ueber den Proxmox-/Toolbox-Fallback reproduzierbar.
- Der Medienserver-V1 ist technisch live und fuer Browser, LAN und den mobilen Tailscale-Pfad betriebsbereit.
- Die Jellyfin-Erstkonfiguration ist fuer den Musikpfad abgeschlossen; `media.hs27.internal`, `192.168.2.20:8096` und `100.99.206.128:8449` fuehren konsistent in die Web-Oberflaeche.
- Der verbleibende operative Block auf der Medienseite ist jetzt nicht mehr die USB->SMB-Bibliotheksmigration; die Bibliothek ist vollstaendig auf den SMB-Zielpfad gespiegelt, jetzt folgen Benutzer-/Client-Rollout und das harte Abschalten des alten USB-Zwischenpfads als Produktionsquelle.
- Das gemeinsame Frontend-Geraet auf `192.168.2.154` war bereits als `surface-go-frontend` frisch aufgebaut; der aktuelle Live-Rollout ist jedoch blockiert, weil das Geraet momentan nicht mehr bootet/startet.
- Die Root-Sleep-Haertung ist jetzt abgeschlossen: `sleep.target`, `suspend.target`, `hibernate.target` und `hybrid-sleep.target` sind maskiert, ein Reboot-Test ist erfolgreich zurueckgekommen.
- Das Surface nutzt jetzt einen robusteren lokalen Frontend-Pfad:
  - lokaler Portalservice auf `127.0.0.1:17827`
  - loopback-only HTTP auf `127.0.0.1:17827`
  - `FRAWO Control` als sichtbarer Launcher
  - Browser-/Launcher-Standard ist im Repo inzwischen auf `firefox` + produktive Launcher fuer `frontend` und `frawo` festgezogen
- Der praktische Restblock am Surface ist derzeit kein UX-Thema mehr, sondern ein Hardware-/Boot-Blocker ausserhalb des laufenden Serverpfads.
- Neu als Zwischenstufe fuer Backups: der `64GB`-USB-Stick `HS27_PORTABLEBK` ist jetzt fest an Proxmox angeschlossen und traegt das kleine PBS-v1-Zwischenstorage; `VM 240 pbs` laeuft inzwischen komplett auf `pbs-usb` (`32G` Systemdisk + `40G` Data-Disk) und `3072 MB` RAM.
- `surface-go-frontend` auf `192.168.2.154` ist jetzt als `surface-go-frontend` frisch aufgebaut; SSH, lokales Portal und der Tailnet-Pfad auf `100.106.67.127` sind verifiziert.
- `wolfstudiopc` ist joined und als Admin-GerÃ¤t etabliert (`100.98.31.60`).
- `Zenbook` ist vorbereitet fÃ¼r die spÃ¤tere Migration als Radio-Anker.
- Der akute local-lvm-Thinpool-Incident vom 25.03.2026 ist behoben:
  - alte Rollback-Snapshots entfernt
  - VM 320 odoo-restore-test entfernt
  - produktive VMs neu gestartet
  - `VM 240 pbs` auf `pbs-usb` verschoben
  - `VM 220`, `VM 230`, `VM 200` und `VM 210` Systemdisks auf `local` als `qcow2` verschoben
  - `CT 110` nach ext4-Repair wieder schreibbar gemacht
  - `HAOS` von `io-error` erholt und wieder auf `192.168.2.24:8123` bzw. `ha.hs27.internal` erreichbar
  - `CT 100 toolbox` Rootfs von `local-lvm` nach `local` verschoben
  - der alte lokale Jellyfin-Bootstrap-Bestand `bootstrap-radio-usb` entfernt
  - Jellyfin auf die aktive SMB-Bibliothek `Musik Netzwerk` umgestellt
  - local-lvm von 100% auf rund 40.4% entlastet


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
- mobiler Tailscale-Frontdoor auf `8443-8448`
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
- Split-DNS-Runbook ist jetzt in `TAILSCALE_SPLIT_DNS_PLAN.md` festgezogen und im Tailnet fuer den ZenBook-Testpfad erfolgreich umgesetzt
- Rightsizing von `VM 200` und `VM 220` in ein Wartungsfenster einplanen
- `portal.hs27.internal` spaeter vom statischen Frontdoor in eine bewusst gestaltete interne Projektstartseite ueberfuehren

## Phase 4 - HAOS professionell integrieren

Ziel:
- Home Assistant als vollwertige, snapshot-faehige, USB-faehige Plattform

Status:
- Baseline abgeschlossen, Ausbau offen

Ergebnisse:
- `VM 210`
- stabile IP `192.168.2.24`
- `ha.hs27.internal` live
- Reverse-Proxy-Trust gesetzt
- lokale Backup-Abdeckung vorhanden

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
- in Arbeit

Erreicht:
- lokaler `vzdump`-Standard
- timerbasierter Night-Run
- Odoo-Restore-Proof
- PBS-Runner, ISO und Stage-Gates vorbereitet
- `VM 240 pbs` installiert und erreichbar auf `192.168.2.25`
- Datastore `hs27-interim` auf der `40G`-USB-Data-Disk im PBS-Gast aktiv
- Proxmox-Storage `pbs-interim` aktiv
- taeglicher PBS-Backup-Job `hs27-pbs-interim-daily` fuer `200,210,220,230` angelegt
- aktuelle Interim-Retention ist jetzt platzbewusst gesetzt:
- Schedule `02:40`
  - `keep-daily=2`
  - `keep-weekly=1`
  - `keep-monthly=1`
- erster gruener PBS-Proof-Lauf ist jetzt nachgewiesen:
  - `VM 220` erfolgreich nach `pbs-interim`
  - Snapshot `vm/220/2026-03-21T10:04:30Z`
  - Proxmox-Taskstatus `exitstatus: OK`
- erster gruener PBS-Restore-Drill ist jetzt ebenfalls nachgewiesen:
  - Restore von `VM 220` nach Test-VM `920`
  - Test-IP `192.168.2.240`
  - Odoo-Login unter `/web/login` mit `HTTP 200`
  - Test-VM `920` danach wieder sauber entfernt

Fehlender Blocker:
- rotierende weitere Restore-Drills auf dem PBS-v1-Pfad fehlen noch
- fuer entspannten Dauerbetrieb zusaetzlich Host-RAM-Upgrade und spaeter groesseres separates PBS-Storage einplanen

Danach:
1. Restore-Drills rotierend auf dem PBS-v1-Pfad weiter regelmaessig nachweisen
2. Inventar- und Easy-Box-Reste finalisieren
3. spaeter groesseres separates PBS-Storage fuer den Dauerbetrieb bereitstellen
4. Host-RAM-Upgrade vor spaeterem Dauerbetrieb einplanen

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
- Repo-seitig vorbereitet, Live-Rollout aktuell durch Hardware-/Boot-Problem blockiert

Erreicht:
- Host `surface-go-frontend` auf `192.168.2.154` per Clean Rebuild neu aufgebaut
- lokaler Admin-User `frawo` ist bestaetigt und per SSH-Key angebunden
- Postinstall-Baseline angewendet:
  - `SSH/22` offen
  - `nginx` entfernt
  - Kiosk-User `frontend` erstellt
  - lokales Portal installiert
  - GDM-Autologin gesetzt
  - touchfreundliche GNOME-Defaults angewendet
- Repo-Standard fuer den produktiven Betrieb ist nachgezogen:
  - `frontend` als read-only/shared Kiosk-User
  - `frawo` mit separaten Admin-/Remote-Launchern
  - AnyDesk-Installpfad und `StudioPC Remote`-Launcher vorbereitet

Rest:
- Geraet wieder boot-/startfaehig machen
- danach Playbook erneut live ausrollen und visuell abnehmen
- feste DHCP-Reservierung
- optional `linux-surface` nur bei echten Hardware-Luecken

## Phase 6b - Raspberry Pi Radio Node

Ziel:
- dedizierter interner Radio-Node statt Medienlast auf `CT 100`

Status:
- intern produktiv auf SMB integriert, Bibliotheksmigration fachlich abgeschlossen

Erreicht:
- Raspberry-Pi-Image ist lokal verifiziert
- Zielmedium ist identifiziert
- Zielarchitektur fuer `AzuraCast` ist als separater Pi-Node festgelegt
- Pi ist per `SSH`, `Tailscale` und `Ansible` in Betrieb
- AzuraCast laeuft intern auf dem Pi
- `radio.hs27.internal` liefert intern `HTTP 302` auf `/login`
- das Host-Medienlayout fuer `RadioLibrary` und `RadioAssets` ist auf dem Pi jetzt vorbereitet
- die erste Station `FraWo - Funk` existiert
- die erste produktive Station ist auf `frawo-funk` standardisiert
- der Pi mountet `//192.168.2.30/Media` produktiv nach `/srv/radio-library/music-network`
- AzuraCast bindet den SMB-Pfad in die Station `frawo-funk`
- die Radio-Checks laufen von diesem Admin-PC jetzt reproduzierbar ueber den Proxmox-/Toolbox-Fallback
- AutoDJ-Basis und Stationspfad sind damit klar vom alten USB-Zwischenpfad getrennt

Rest:
- DHCP-Reservierung sauber festziehen
- den alten USB-Zwischenpfad operativ entfernen und nicht mehr als produktive Quelle behandeln
- Medienkurationspfad zwischen zentraler Musikfreigabe, `RadioLibrary` und `RadioAssets` sauber operationalisieren
- Ressourcen-Feintuning auf dem Pi nach den ersten echten Streams pruefen

## Phase 6c - Interner Medienserver

Ziel:
- sofort nutzbarer Medien-Mehrwert fuer Browser, Thomson und Google TV ohne Public Edge

Status:
- Baseline abgeschlossen, SMB-Cutover technisch live; Client- und Benutzerrollout offen

Erreicht:
- Jellyfin laeuft auf `CT 100 toolbox`
- `media.hs27.internal` liefert intern die Jellyfin-Oberflaeche
- der direkte LAN-Pfad `192.168.2.20:8096` ist verifiziert
- der mobile Tailscale-Frontdoor auf `100.99.206.128:8449` ist verifiziert
- alle drei Pfade liefern aktuell konsistent `HTTP 302 -> /web/`
- Bibliotheks-Stammverzeichnisse auf der Toolbox sind vorbereitet:
  - `/srv/media-library/movies`
  - `/srv/media-library/shows`
  - `/srv/media-library/music`
  - `/srv/media-library/homevideos`
- der produktive SMB-Pfad ist hostseitig auf Proxmox nach `/mnt/hs27-media` gemountet und per Bind-Mount nach `CT 100` durchgereicht
- der Docker-Bind in Jellyfin ist auf `rslave` gehaertet, damit der SMB-Inhalt im Container sichtbar bleibt

Rest:
- Jellyfin-Zugaenge in den Bitwarden Cloud uebernehmen
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
- geplant, noch nicht freigegeben

Stage Gate:
- alle Ziel-LXCs/VMs stabil
- Backup/Restore praktisch bewiesen
- Inventar und IP-Plan final
- Wartungsfenster geplant
- Rueckfall auf Easy Box dokumentiert

Aktueller maschinenlesbarer Gate:
- `make gateway-cutover-stage-gate`

Derzeitige Blocker:
- `inventory_finalized=no`
- `maintenance_window_ready=no`

## Phase 8 - Public Edge und professionelle Aussenanbindung

Ziel:
- sichere, kontrollierte Oeffnung zur Oeffentlichkeit

Status:
- bewusst spaeter
- erster geplanter externer Release am `2026-04-01` ist website-first

Vorbedingungen:
- UCG-Ultra oder gleichwertige Edge-Kontrolle aktiv
- Inventar und Zonen final
- PBS und Restore-Standard belastbar
- Domain, DNS, TLS, Auth, Logging, Monitoring und Rollback definiert
- produktives `Bitwarden Cloud` eingefuehrt
- reale FRAWO-Mailboxen vorhanden

Bevorzugter Zielname:
- `www.frawo-tech.de` fuer die Hauptseite
- `radio.frawo-tech.de` spaeter fuer Radio/Player
- `prinz-stockenweiler.de` als spaeterer externer Support-Kontext im Elternhaus
- internes `hs27.internal` bleibt bis zur bewussten internen DNS-Migration unveraendert
- spaeterer professioneller interner Zielname ist `frawo.home.arpa`

Runbook:
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
- `RELEASE_READINESS_2026-04-01.md`

Nie direkt oeffentlich:
- Proxmox
- Toolbox-Admin
- PBS
- AdGuard-Admin
- Home-Assistant-Admin
- Nextcloud-Admin
- Paperless-Admin
- Odoo-Admin

## Phase 9 - Optional / Wishlist

- `Ollama`
  - derzeit nicht sinnvoll auf dem bestehenden Host
  - Wiedervorlage erst bei RAM-Upgrade oder separatem AI-Node
- `Anytype`
  - Integration als lokale SSOT fÃ¼r Wissensmanagement
  - Synergie mit der HS27-Infrastruktur prÃ¼fen


## Finale Roadmap Ab `2026-03-26`

### Welle 1 - Betriebsstandard jetzt abschliessen

Ziel:
- aus dem internen Arbeitsstand einen professionell fuehrbaren Betriebsstand machen

Reihenfolge:
1. `Bitwarden Cloud` produktiv einfuehren
2. produktive Logins aus `ACCESS_REGISTER.md` in Bitwarden ueberfuehren
3. reale STRATO-Mailboxen anlegen:
   - `wolf@frawo-tech.de`
   - `franz@frawo-tech.de`
   - `info@frawo-tech.de`
   - `noreply@frawo-tech.de`
4. SPF, DKIM und DMARC dokumentieren und testen
5. SMTP-Absenderpfad fuer `Nextcloud`, `Paperless`, `Odoo` und `AzuraCast` vorbereiten

Definition of done:
- produktive Secrets liegen nicht mehr nur in Markdown-Dateien
- Mail-Identitaeten sind real vorhanden
- der operative Release- und Support-Pfad ist personengebunden und nachvollziehbar

### Welle 2 - Release `2026-04-01` absichern

Ziel:
- kleiner, sauber kontrollierter erster externer Release

Verbindlicher Scope:
- `frawo-tech.de` -> Redirect auf `www.frawo-tech.de`
- `www.frawo-tech.de` -> oeffentliche FRAWO-Website

Explizit nicht im Scope:
- Nextcloud
- Paperless
- Odoo
- Home Assistant
- Proxmox
- PBS
- AdGuard
- Toolbox-Adminpfade
- breiter Radio-Public-Rollout

Reihenfolge:
1. `RELEASE_READINESS_2026-04-01.md` auf Gruen ziehen
2. DNS-/TLS-/Rollback-Pfad finalisieren
3. Website-Zielsystem und Monitoring festziehen
4. externen Testlauf fuer DNS, TLS und Mail fahren
5. erst dann `www.frawo-tech.de` freigeben

Definition of done:
- Website ist extern erreichbar
- keine Admin-UIs sind oeffentlich
- Rollback ist dokumentiert
- Release ist klein genug, um im Fehlerfall kontrolliert ruecknehmbar zu bleiben

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
3. getrennten Secret-Bereich `Stockenweiler` in Bitwarden befuellen
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
1. `radio.frawo-tech.de` nur bei separatem Green Gate
2. Surface-Recovery und `frontend`-Pfad
3. UCG-Ultra-Cutover
4. 2-TB-SSD-Endrolle festziehen
5. Google-Drive-Integration spaeter ueber den bestehenden `rclone`-/Nextcloud-Pfad

## Was jetzt als Naechstes dran ist

1. **Thinpool entspannt**: [x] DONE. `local-lvm` ist von `100%` auf rund `40.4%` gefallen; `local` wurde anschliessend ueber die 2-TB-SSD-Archiventlastung wieder auf rund `73%` gedrueckt.
2. **Media Logins finalisiert**: [x] DONE. Jellyfin-, AzuraCast- und AdGuard-Zugaenge haben bekannte Endwerte; der fehlende Schritt ist jetzt nur noch die Ablage in `Bitwarden Cloud`.
3. **Identity Standard Kernsysteme live**: [x] DONE fuer `Nextcloud`, `Paperless`, `Odoo`, `Jellyfin` und `AzuraCast`.
4. **USB-Altpfad toolboxseitig retiren**: [x] DONE. Jellyfin nutzt jetzt die SMB-Bibliothek `Musik Netzwerk`; der alte lokale Bootstrap-Pfad ist entfernt.
5. **2-TB-SSD-Strategie festziehen**: die SSD dient jetzt interimistisch als kaltes Archiv fuer lokale Dump-Dateien; entscheiden, ob und wann daraus eine saubere Linux-Serverpartition fuer Archiv/Staging wird.
6. **Dokumenten-Workflow**: [x] DONE. Paperless-/Nextcloud-Pfad ist mit einem echten Dokumentenlauf abgenommen (bridge_timer live, 'probe' Document consumed).
7. **Mail- und Secret-Standard einfuehren**: STRATO-Mailboxen anlegen, `Bitwarden Cloud` einfuehren und die produktiven Logins aus den Arbeitsdateien ueberfuehren.
8. **Website-first Release 2026-04-01 vorbereiten**: `www.frawo-tech.de` als einzigen oeffentlichen Scope bis zum ersten Green Gate festziehen.
9. **Stockenweiler / Rentner OS vorbereiten**: Tailscale-only Managed Support fuer den ersten externen Testkundenfall definieren und inventarisieren.
10. **HAOS-USB-Pfad vorbereiten**: Sobald die Zigbee/Z-Wave Hardware steckt.
11. **Surface**: erst nach Hardware-/Boot-Recovery wieder in den produktiven Pfad nehmen.
12. **Gateway-Cutover**: Erst nach Abschluss der oben genannten Stabilitaets-Gates.
13. **Public Edge**: Finaler Hardening-Schritt.

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




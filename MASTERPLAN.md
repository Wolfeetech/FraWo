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
  - primäres Admin- und Brückengerät (dieser PC)
  - SSOT für Netzwerk- und Servermanagement
- `zenbook_radio_anchor`
  - zukünftiger Radio-Ankerpunkt ("Villa")
  - Livestream-Host für Studio-Broadcasts
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
- `radio.hs27.internal` zeigt jetzt intern auf den Raspberry-Pi-Radio-Node und liefert die AzuraCast-Setup-Seite
- `media.hs27.internal` zeigt jetzt intern auf Jellyfin auf der Toolbox; der direkte LAN-Pfad `192.168.2.20:8096` und der mobile Tailscale-Pfad `100.99.206.128:8449` sind verifiziert
- ein wiederholbarer Bootstrap-Sync vom Pi auf die Toolbox-Mediathek ist jetzt live und befuellt `/srv/media-library/music/bootstrap-radio-usb`
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
- Bevorzugter spaeterer Public-Domain-Pfad ist jetzt `frawo-tech.de` (Strato, GbR-Hauptdomain) mit `www.frawo-tech.de` fuer die GbR-Website und `radio.frawo-tech.de` fuer den Radio-/Player-Pfad.
- `yourparty.tech` (Legacy-Projekt): Restlaufzeit sinnvoll nutzen, danach ggf. abschalten oder redirecten.
- `prinz-stockenweiler.de` (Ionos, Elternhaus): Wolf ist der "Internetangel"; Ziel ist die Fernwartung und Erreichbarkeit aller dortigen Services ("auf dem Server").
- internes `hs27.internal` bleibt bis zur bewussten internen DNS-Migration unveraendert.
- Der dedizierte Radio-Node auf dem Raspberry Pi 4 ist intern live: AzuraCast laeuft auf dem Pi, `radio.hs27.internal` liefert intern `HTTP 302` auf `/login`, und die Status-API ist erreichbar.

- Der Radio-Betrieb ist jetzt auch operativ verifiziert: `Radio`, `Radio Control` und `nowplaying` sind intern gruen; naechster Schritt ist die Kuration nach `RadioLibrary` / `RadioAssets` und danach eine touchfreundliche Surface-Monitor-/Control-Schicht.
- Der Medienserver-V1 ist technisch live und die Jellyfin-Erstkonfiguration ist fuer den Musikpfad abgeschlossen.
- Der Medienserver-V1 hat jetzt schon einen echten Content-Pfad: Pi-USB-Musik wird in die Toolbox-Mediathek synchronisiert; der verbleibende operative Block ist jetzt vor allem der laufende Bootstrap-Import und danach die Client-/Kurationsschicht.
- Der erste grosse Medienimport laeuft nach der Rootfs-Erweiterung wieder und ist jetzt der praktische Seed fuer Jellyfin.
- Das gemeinsame Frontend-Geraet auf `192.168.2.154` ist jetzt als `surface-go-frontend` frisch aufgebaut; SSH, lokales Portal und der Tailnet-Pfad auf `100.106.67.127` sind verifiziert.
- Die Root-Sleep-Haertung ist jetzt abgeschlossen: `sleep.target`, `suspend.target`, `hibernate.target` und `hybrid-sleep.target` sind maskiert, ein Reboot-Test ist erfolgreich zurueckgekommen.
- Das Surface nutzt jetzt einen robusteren lokalen Frontend-Pfad:
  - lokaler Portalservice auf `127.0.0.1:17827`
  - loopback-only HTTP auf `127.0.0.1:17827`
  - `FRAWO Control` als sichtbarer Launcher
  - `epiphany-browser` wird aktuell ueber einen lokalen Wrapper als private Instanz gestartet
- Der praktische Restblock am Surface ist damit auf Browser-/Touch-Tastatur-Feinschliff und spaetere UX-Veredelung geschrumpft, nicht mehr auf Grundfunktion.
- Neu als Zwischenstufe fuer Backups: der `64GB`-USB-Stick `HS27_PORTABLEBK` ist jetzt fest an Proxmox angeschlossen und traegt das kleine PBS-v1-Zwischenstorage; `VM 240 pbs` laeuft mit `32G` Systemdisk auf `local-lvm`, `40G` USB-Data-Disk auf `pbs-usb` und `3072 MB` RAM.
- `surface-go-frontend` auf `192.168.2.154` ist jetzt als `surface-go-frontend` frisch aufgebaut; SSH, lokales Portal und der Tailnet-Pfad auf `100.106.67.127` sind verifiziert.
- `wolfstudiopc` ist joined und als Admin-Gerät etabliert (`100.98.31.60`).
- `Zenbook` ist vorbereitet für die spätere Migration als Radio-Anker.


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
  - Schedule `02:40,14:40`
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
- weitgehend abgeschlossen, Feinschliff offen

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

Rest:
- feste DHCP-Reservierung
- spaetere UX-Verbesserung des Frontends
- optional `linux-surface` nur bei echten Hardware-Luecken

## Phase 6b - Raspberry Pi Radio Node

Ziel:
- dedizierter interner Radio-Node statt Medienlast auf `CT 100`

Status:
- in Arbeit, interner AzuraCast-Betrieb mit erster Station und USB-Musik live

Erreicht:
- Raspberry-Pi-Image ist lokal verifiziert
- Zielmedium ist identifiziert
- Zielarchitektur fuer `AzuraCast` ist als separater Pi-Node festgelegt
- Pi ist per `SSH`, `Tailscale` und `Ansible` in Betrieb
- AzuraCast laeuft intern auf dem Pi
- `radio.hs27.internal` liefert intern `HTTP 302` auf `/login`
- das Host-Medienlayout fuer `RadioLibrary` und `RadioAssets` ist auf dem Pi jetzt vorbereitet
- die erste Station `FraWo - Funk` existiert
- die direkt am Pi steckende USB-Musikquelle ist eingebunden
- AutoDJ spielt jetzt intern bereits echte Titel aus der USB-Bibliothek

Rest:
- DHCP-Reservierung sauber festziehen
- Medienkurationspfad zwischen USB-Quelle, `RadioLibrary` und `RadioAssets` sauber operationalisieren
- Ressourcen-Feintuning auf dem Pi nach den ersten echten Streams pruefen

## Phase 6c - Interner Medienserver

Ziel:
- sofort nutzbarer Medien-Mehrwert fuer Browser, Thomson und Google TV ohne Public Edge

Status:
- in Arbeit, technischer V1 live

Erreicht:
- Jellyfin laeuft auf `CT 100 toolbox`
- `media.hs27.internal` liefert intern die Jellyfin-Oberflaeche
- der direkte LAN-Pfad `192.168.2.20:8096` ist verifiziert
- der mobile Tailscale-Frontdoor auf `100.99.206.128:8449` ist verifiziert
- Bibliotheks-Stammverzeichnisse auf der Toolbox sind vorbereitet:
  - `/srv/media-library/movies`
  - `/srv/media-library/shows`
  - `/srv/media-library/music`
  - `/srv/media-library/homevideos`

Rest:
- erste Thomson-/Google-TV-Clients verbinden
- spaeter Medienquelle und Kuration professionell von der Bootstrap-Phase in einen dauerhaften Pfad ueberfuehren

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

Vorbedingungen:
- UCG-Ultra oder gleichwertige Edge-Kontrolle aktiv
- Inventar und Zonen final
- PBS und Restore-Standard belastbar
- Domain, DNS, TLS, Auth, Logging, Monitoring und Rollback definiert

Bevorzugter Zielname:
- `www.frawo-tech.de` fuer die Hauptseite
- `radio.frawo-tech.de` fuer Radio/Player
- `prinz-stockenweiler.de` (Remote-Admin Elternhaus)
- internes `hs27.internal` bleibt bis zur bewussten internen DNS-Migration unveraendert
- spaeterer professioneller interner Zielname ist `frawo.home.arpa`


Runbook:
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`

Nie direkt oeffentlich:
- Proxmox
- Toolbox-Admin
- PBS
- AdGuard-Admin
- Home-Assistant-Admin

## Phase 9 - Optional / Wishlist

- `Ollama`
  - derzeit nicht sinnvoll auf dem bestehenden Host
  - Wiedervorlage erst bei RAM-Upgrade oder separatem AI-Node
- `Anytype`
  - Integration als lokale SSOT für Wissensmanagement
  - Synergie mit der HS27-Infrastruktur prüfen


## Was jetzt als Naechstes dran ist

1. **HAOS-USB-Pfad vorbereiten**: Sobald die Zigbee/Z-Wave Hardware steckt.
2. **Dokumenten-Workflow**: [x] DONE. Paperless-/Nextcloud-Pfad ist mit einem echten Dokumentenlauf abgenommen (bridge_timer live, 'probe' Document consumed).
3. **Radio & Control**: Radio-Kuration und Surface-Monitor (Kiosk) finalisieren.
4. **Media Clients**: Jellyfin-Anbindung für Thomson/Google TV.
5. **Phase 5 & 6**: [x] DONE. Backup-Standard (PBS VM 240) und Netzwerk-Inventar (.14x) sind stabil.
6. **Gateway-Cutover**: Erst nach Abschluss der oben genannten Stabilitäts-Gates.
7. **Public Edge**: Finaler Hardening-Schritt.


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


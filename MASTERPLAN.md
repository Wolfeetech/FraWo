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
- `CT 100` stellt internes Caddy und AdGuard im Opt-in-Betrieb bereit.
- Tailscale auf `CT 100` ist joined und laeuft.
- `VM 210` ist gebaut, stabil auf `192.168.2.24` und intern ueber `ha.hs27.internal` erreichbar.
- Reverse-Proxy-Trust fuer Home Assistant ist gesetzt.
- Lokaler Backup-Zwischenstandard ist live und deckt `VM 200`, `VM 210`, `VM 220`, `VM 230` ab.
- Odoo-Restore-Proof wurde praktisch erfolgreich gezeigt.
- Capacity-Review ist live und bestaetigt: Host-RAM ist der primaere Skalierungsengpass, Nextcloud und Odoo sind aktuell ueberdimensioniert, HAOS ist bewusst knapp aber passend dimensioniert.
- mobiler Tailscale-Frontdoor ueber die Toolbox ist live, Tailscale-only gehaertet und liefert die Kerndienste jetzt ueber `100.99.206.128:8443-8448`
- `portal.hs27.internal` ist live und der mobile Tailscale-Frontdoor deckt jetzt auch das interne Portal auf `100.99.206.128:8447`, Radio auf `:8448` und Media auf `:8449` ab
- `radio.hs27.internal` zeigt jetzt intern auf den Raspberry-Pi-Radio-Node und liefert die AzuraCast-Setup-Seite
- `media.hs27.internal` zeigt jetzt intern auf Jellyfin auf der Toolbox; der direkte LAN-Pfad `192.168.2.20:8096` und der mobile Tailscale-Pfad `100.99.206.128:8449` sind verifiziert
- Der Raspberry-Pi-Radio-Node ist jetzt auf ein konservatives `pi4_2gb_single_station_low_resource`-Profil getunt: `4` CPU-Kerne, `~1.8 GiB` RAM, `2 GiB` Swap, `~21 GiB` freies Rootfs und AzuraCast-Leerlauf aktuell bei `~457 MiB`
- Right-Sizing-Stage-Gate und Wartungs-Runbook fuer `VM 200` und `VM 220` sind einsatzbereit.

### Noch nicht fertig

- Easy-Box-Leases und DHCP-Reservierungen sind noch nicht final abgeglichen, auch wenn Login und der authentifizierte `overview.json`-Pfad jetzt reproduzierbar funktionieren.
- PBS ist vorbereitet, aber ohne separates Backup-Storage noch nicht build-ready.
- USB-Dongles fuer HAOS sind noch nicht am Host sichtbar.
- AdGuard ist noch nicht primaerer LAN-DNS.
- UCG-Ultra ist noch nicht integriert.
- Public Edge ist bewusst noch nicht live.
- Bevorzugter spaeterer Public-Domain-Pfad ist jetzt `frawo.studio` mit `www.frawo.studio` fuer die GbR-Website und `radio.frawo.studio` fuer den Radio-/Player-Pfad.
- Der dedizierte Radio-Node auf dem Raspberry Pi 4 ist intern live: AzuraCast laeuft auf dem Pi, `radio.hs27.internal` liefert intern `HTTP 302` auf `/login`, und die Status-API ist erreichbar.
- Der Radio-Betrieb ist jetzt auch operativ verifiziert: `Radio`, `Radio Control` und `nowplaying` sind intern gruen; naechster Schritt ist die Kuration nach `RadioLibrary` / `RadioAssets` und danach eine touchfreundliche Surface-Monitor-/Control-Schicht.
- Der Medienserver-V1 ist technisch live, aber die UI-basierte Erstkonfiguration von Jellyfin und die Bibliotheksanbindung fehlen noch.
- Das gemeinsame Frontend-Geraet auf `192.168.2.154` ist jetzt als `surface-go-frontend` frisch aufgebaut; SSH, Kiosk-Baseline und lokales Portal sind live, offen bleibt nur noch der Tailscale-Join und die Postinstall-Abnahme.
- Das Surface ist im Moment allerdings wieder offline bzw. schlafend; die letzte technische Arbeit dort ist daher physisch blockiert.
- ZenBook-Remote-Zugriff ist vorbereitet:
  - Tailscale joined
  - AnyDesk aktiv

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

Fehlender Blocker:
- separates Backup-Storage auf Proxmox unter `/srv/pbs-datastore`
- fuer entspannten Dauerbetrieb zusaetzlich Host-RAM-Upgrade einplanen

Danach:
1. `VM 240` bauen
2. PBS produktiv einrichten
3. Proxmox-Backups nach PBS umhaengen
4. Restore-Drills rotierend nachweisen

## Phase 6 - Inventar und Netzgovernance finalisieren

Ziel:
- kein unbekanntes Geraet mehr im produktiven Netz
- saubere IP- und Reservierungsstrategie

Status:
- in Arbeit

Offene Punkte:
- unbekannte Hosts `.141` bis `.144`
- restliche Klassifizierungen aus dem Router-Ueberblick:
  - `Surface_Laptop`
  - `RE355`
  - `iPhone-3-Pro`
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
- aktiv, Rebuild und Basis-Bootstrap abgeschlossen

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
- Tailscale-Login fuer das Surface approven
- Clean Rebuild auf `Ubuntu Desktop 24.04 LTS`
- feste DHCP-Reservierung
- `OpenSSH`, `Tailscale`, lokale Portal-Seite und Kiosk-Modus
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
- ersten Jellyfin-Admin anlegen
- Bibliotheken in der UI anbinden
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
- `www.frawo.studio` fuer die Hauptseite
- `radio.frawo.studio` fuer Radio/Player
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

## Was jetzt als Naechstes dran ist

1. Easy-Box-Leases und Reservierungen finalisieren.
2. Separates PBS-Storage bereitstellen.
3. PBS produktiv aufbauen.
4. HAOS-USB-Pfad vorbereiten, sobald Hardware steckt.
5. AzuraCast-Web-Einrichtung abschliessen und Medienpfade fuer den Raspberry-Pi-Radio-Node anbinden.
6. Gateway-Cutover erst danach.
7. Public Edge erst nach Gateway und PBS.
8. Rightsizing von `VM 200` und `VM 220` vor dem PBS-Dauerbetrieb einplanen.
9. Surface Go als `frontend-node` per Clean Rebuild in den Hybrid-Kiosk-Standard ueberfuehren.

## Die wichtigsten Dateien zum Masterplan

- [MASTERPLAN.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/MASTERPLAN.md)
- [MEMORY.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/MEMORY.md)
- [NETWORK_INVENTORY.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/NETWORK_INVENTORY.md)
- [VM_AUDIT.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/VM_AUDIT.md)
- [CAPACITY_REVIEW.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/CAPACITY_REVIEW.md)
- [BACKUP_RESTORE_PROOF.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/BACKUP_RESTORE_PROOF.md)
- [RASPBERRY_PI_RADIO_NODE_PLAN.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/RASPBERRY_PI_RADIO_NODE_PLAN.md)
- [REMOTE_ACCESS_STANDARD.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/REMOTE_ACCESS_STANDARD.md)
- [PBS_VM_240_SETUP_PLAN.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/PBS_VM_240_SETUP_PLAN.md)
- [HAOS_VM_210_SETUP_PLAN.md](/home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2/HAOS_VM_210_SETUP_PLAN.md)

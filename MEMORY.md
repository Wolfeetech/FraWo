# MEMORY - Homeserver 2027 Knowledge Base

## Status

- Dokumenttyp: zentrale Knowledge Base / RAG-Index
- Gueltig ab: 2026-03-17
- Merge-Regel: aeltere Artefakte nur konfliktfrei uebernehmen; bei Konflikten gewinnt dieses Dokument
- Legacy-Session-Cleanup: abgeschlossen, nur dieser Workspace bleibt erhalten
- Workspace-Name: `Homeserver 2027 Ops Workspace`
- Workspace-Alias: `~/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Live-Kontext-Datei: `LIVE_CONTEXT.md`
- Aktuelle Arbeitsbasis:
  - `README.md`
  - `LIVE_CONTEXT.md`
  - `NETWORK_INVENTORY.md`
  - `VM_AUDIT.md`
- `BACKUP_RESTORE_PROOF.md`
- `REMOTE_ONLY_WORK_WINDOW.md`
- `ADGUARD_PILOT_ROLLOUT_PLAN.md`
- `TAILSCALE_SPLIT_DNS_PLAN.md`
- `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md`
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
- `RASPBERRY_PI_RADIO_NODE_PLAN.md`
- `RADIO_OPERATIONS_STANDARD.md`
- `RPI_RESOURCE_ALLOCATION_PLAN.md`
- `REMOTE_ACCESS_STANDARD.md`
- `PBS_VM_240_SETUP_PLAN.md`
- `MEDIA_AND_REMOTE_PREP.md`
- `ansible/inventory/hosts.yml`
- `ansible/inventory/group_vars/all/vault.yml`

## Verifizierte Basisfakten

- Hardware: Lenovo ThinkCentre M920q
- CPU: Intel i5-8500T
- RAM: 15 GB
- Host: Proxmox VE auf lokalem NVMe-Storage
- identifizierter Shared-Frontend-Kandidat im LAN:
  - `surface-go-frontend`
  - `192.168.2.154`
  - lokaler Benutzer `frawo`
  - aktueller Stand: SSH-Key-Zugang aktiv, `frontend`-Kiosk-User vorhanden, lokales Portal installiert
- lokaler Operator-Rechner:
  - `wolf-ZenBook-UX325EA-UX325EA`
  - `Ubuntu 24.04.4 LTS`
  - `X11`
  - `tailscaled` ist installiert, aktiviert und laeuft
  - lokaler Tailscale-Client ist jetzt dem Tailnet `w.prinz1101@gmail.com` beigetreten
  - Tailscale-IP: `100.76.249.126`
  - direkter Tailnet-Zugriff auf die Toolbox ist verifiziert:
    - `http://100.99.206.128:8443`
    - `http://100.99.206.128:8447`
  - der direkte Test auf `192.168.2.24` wurde vom ZenBook aus zwar erfolgreich beantwortet, ist im lokalen LAN aber noch kein harter Beweis fuer extern wirksames Subnet-Routing
  - die doppelte Ubuntu-Quelle `dvd.list` ist deaktiviert
  - `AnyDesk 8.0.0` ist installiert und `anydesk.service` laeuft aktiv
  - die konkrete AnyDesk-ID und das Passwort werden bewusst nicht im Workspace abgelegt
- erkannte lokale Installationsmedien:
  - `/dev/mmcblk0` = `29.7G` SD-Karte im Slot
  - `/dev/sdd` = `7.7G` USB-Stick mit aktuellem Label `PVE`; Zielrolle jetzt dedizierter Install-/Image-Stick
  - `/dev/sdc` = `14.4G` Kingston USB-Stick; Zielrolle jetzt spaeterer mobiler Favorites-Stick
  - fuer den Raspberry Pi existiert jetzt ein vorbereiteter First-Boot-Seed:
    - `scripts/prepare_rpi_firstboot_seed.sh`
    - schreibt Hostname `radio-node`, Admin-User `wolf`, DHCP auf `eth0` und den ZenBook-SSH-Key auf die frisch geflashte SD-Karte
    - die aktuell gesteckte SD-Karte ist bereits auf diesen Seed umgestellt
  - fuer den Raspberry Pi existiert jetzt auch der kanonische Post-Boot-Pfad:
    - `ansible/playbooks/bootstrap_raspberry_pi_radio.yml`
  - der Raspberry Pi wurde inzwischen erfolgreich erstmals gebootet:
    - Hostname `radio-node`
    - LAN-IP `192.168.2.155`
    - SSH erreichbar
    - `docker`, `tailscaled` und `sshd` aktiv
    - `ansible`-Ping erfolgreich
    - Tailscale-Backend jetzt `Running`
    - Tailscale-IP `100.64.23.77`
    - `docker compose` ist verfuegbar
    - `2 GiB` Swapfile ist aktiv
    - `/srv/radio-library` und `/srv/radio-assets` sind vorbereitet
    - `/var/azuracast/docker.sh` liegt bereit
    - AzuraCast ist jetzt intern deployed
    - Container `azuracast` und `azuracast_updater` laufen
    - direkter Check gegen die Tailscale-IP liefert `HTTP 302` auf `/login`
    - die Status-API liefert `HTTP 200`
    - `radio.hs27.internal` ist ueber die Toolbox auf den Pi umgeschaltet
    - das Host-Medienlayout ist jetzt vorbereitet:
      - `/srv/radio-library/incoming`, `music`, `playlists`
      - `/srv/radio-assets/ids`, `jingles`, `shows`, `staging`, `sweepers`
    - die erste Station `FraWo - Funk` mit Shortcode `frawo-funk` ist jetzt angelegt
    - ein direkt am Pi steckendes USB-Musikmedium ist jetzt integriert:
      - Dateisystem `exfat`
      - UUID `76E8-CACF`
      - Mountpoint `/srv/radio-library/music-usb`
      - Quellordner `/srv/radio-library/music-usb/yourparty.radio`
      - Rollendatei `/srv/radio-library/music-usb/README_FRAWO_LIBRARY_ROLE.txt` bestaetigt den Zweck als temporaere Gesamt-Musikbibliothek
      - Host- und Container-Sicht sehen aktuell `2120` Dateien
    - `GET /api/nowplaying` zeigt jetzt echten Sendebetrieb mit aktuellem Titel
    - Low-resource-Profil ist jetzt live und verifiziert:
      - `COMPOSE_HTTP_TIMEOUT=900`
      - `PHP_FPM_MAX_CHILDREN=2`
      - `NOW_PLAYING_DELAY_TIME=15`
      - `NOW_PLAYING_MAX_CONCURRENT_PROCESSES=1`
      - `ENABLE_WEB_UPDATER=false`
      - Docker `userland-proxy=false`
      - aktueller Leerlaufbedarf AzuraCast `~457 MiB`
    - der naechste Schritt ist die kuratierte Betriebsueberfuehrung von USB-Musik zu `RadioLibrary` / `RadioAssets` und spaeter optional auf einen Netz-Medienpfad
  - fuer das Surface bleibt der professionelle Default bewusst:
    - Clean Install von Ubuntu Desktop
    - danach remote ueber `ansible/playbooks/bootstrap_surface_go_frontend.yml`
    - kein vollautomatischer Zero-Touch-Desktop-Rebuild als Default
- Proxmox `local-lvm` Thin Pool:
  - Groesse aktuell `156.88 GiB`
  - Autoextend aktiv mit `threshold=70`, `percent=20`
- LAN: `192.168.2.0/24`
- Gateway: `192.168.2.1`
- Toolbox: `CT 100`, Ziel-IP `192.168.2.20`

## Konfliktfrei uebernommene Alt-Fakten

- Toolbox-Benutzer fuer operative Arbeit: `wolf`
- Frueheres Toolbox-Audit zeigte einen sauberen Startzustand:
  - `/opt` war leer
  - keine interaktive Shell-Historie fuer `wolf`
  - Docker war noch nicht installiert
- Diese Fakten bleiben gueltig, bis ein neuer Audit sie ersetzt.

## Kanonische Topologie

| ID | Typ | Dienst | Rolle | Ziel-IP | Betriebsmodell |
| --- | --- | --- | --- | --- | --- |
| 100 | CT | Toolbox | Docker-Host, Ansible-Kontrollknoten, Caddy, Split-DNS, AdGuard Home im Opt-in-Betrieb und Tailscale-Gateway | `192.168.2.20` | LXC, Rebuild erlaubt |
| 200 | VM | Nextcloud | Dokumentenablage und Kollaboration | `192.168.2.21` | dedizierte VM mit Redis und NVMe-Fokus |
| 210 | VM | Home Assistant OS | Smart Home Zentrale mit Supervisor und Add-ons | `192.168.2.24` | dedizierte HAOS-VM mit USB-Passthrough |
| 220 | VM | Odoo | ERP, Rechnungen, CRM | `192.168.2.22` | dedizierte VM mit lokaler PostgreSQL-Persistenz |
| 230 | VM | Paperless-ngx | Archivierung der GbR-Dokumente | `192.168.2.23` | dedizierte VM |

## Netzwerk-Basisstand

- Router: Vodafone Easy Box auf `192.168.2.1`
- `CT 100` Netzwerk-Basis ist seit `2026-03-18` live verifiziert:
  - Docker laeuft in der CT
  - Stack `toolbox-network` laeuft ueber `homeserver-compose-toolbox-network.service`
  - Caddy beantwortet intern `portal.hs27.internal`, `cloud.hs27.internal`, `odoo.hs27.internal`, `paperless.hs27.internal`, `ha.hs27.internal`
  - `radio.hs27.internal` zeigt jetzt intern auf den Raspberry-Pi-Radio-Node und liefert `HTTP 302` auf `/login`
  - AdGuard Home lauscht auf `192.168.2.20:53`
  - AdGuard-Admin ist auf `CT 100` nur noch lokal unter `127.0.0.1:3000` erreichbar
  - `hs27.internal`-Rewrites zeigen im Opt-in-Betrieb auf `192.168.2.20`
  - mobiler Tailscale-Frontdoor ist live:
    - `http://100.99.206.128:8443` -> Home Assistant
    - `http://100.99.206.128:8444/web/login` -> Odoo
    - `http://100.99.206.128:8445` -> Nextcloud
    - `http://100.99.206.128:8446/accounts/login/` -> Paperless
    - `http://100.99.206.128:8447` -> internal portal
    - `http://100.99.206.128:8448` -> Radio
    - diese Ports sind per Toolbox-Firewall auf Tailscale-Traffic begrenzt und vom LAN aus nicht mehr erreichbar
  - `/dev/net/tun` ist in die CT durchgereicht
  - `tailscaled` ist installiert und aktiv
  - Forwarding-Keys fuer den spaeteren Subnet-Router sind gesetzt
  - aktueller Tailscale-Backend-State ist `Running`
  - Tailnet-DNS-Name der Toolbox: `toolbox.tail150400.ts.net.`
  - lokales Tailscale-Prefs-Set annonciert `192.168.2.0/24`
  - die Tailnet-Netzsicht bestaetigt diese Route jetzt als aktiv
  - daraus folgt: Toolbox-seitig ist der Subnet-Router produktiv aktiv und Split-DNS fuer `hs27.internal` kann sauber genutzt werden
- Geplante Edge-Hardware:
  - `UniFi Cloud Gateway Ultra (UCG-Ultra)` ist vorhanden, aber noch nicht aktiv
  - Zielrolle spaeter: zentraler Gateway fuer DHCP-Reservierungen, Firewall-Policies und VLAN-faehige Segmentierung
- Router-Zugang:
  - Login-Benutzer `vodafone`
  - Passwort liegt verschluesselt in `ansible/inventory/group_vars/all/vault.yml`
- Vollscan vom `2026-03-17` ergab 23 aktive Hosts im LAN.
- Zonenmodell:
  - `core`
  - `management`
  - `business`
  - `infra-services`
  - `smart-home-iot`
  - `media-private`
  - `trusted-clients`
  - `unknown-review`
- Uebergreifende Wahrheit:
  - Scan und Proxmox liefern den technischen Ist-Zustand.
  - Die Easy-Box-Lease-Tabelle bleibt Pflichtabgleich fuer DHCP-Reservierungen und unklare Clients.
  - Der aktuelle Automationsblocker liegt nicht an fehlenden Credentials:
    - `user_lang.json` laesst sich inzwischen per Headless-Browser reproduzierbar ueber `https://192.168.2.1` automatisiert abrufen
    - rohe CLI-HTTP-Clients laufen gegen `UNKNOWN 400 Bad Request` und sind damit fuer die EasyBox 805 unzuverlaessig
    - der eigentliche EasyBox-Login und ein authentifizierter `overview.json`-Abruf sind jetzt headless sauber reproduziert
    - offen bleibt nicht mehr der Login selbst, sondern die saubere Einordnung der verbleibenden privaten MAC-Clients und zusaetzlichen Router-Labels wie `Surface_Laptop`, `RE355` und `iPhone-3-Pro`
    - letzter Browser-Probe zeigte `trying_times=0` und `delay_time=0`; weitere Login-Versuche trotzdem nur kontrolliert und nicht blind wiederholen
  - Die manuelle Router-Seite vom `2026-03-18` hat folgende Teilaufloesungen bestaetigt:
    - `Wolf_Pixel` ist ein Bewohner-Geraet von Wolf
    - `SonRoku` ist das Roku-TV-Addon
    - die Shelly-Geraete gehoeren funktional zur Growbox
    - Bewohnerkontext fuer Personen: Wolf und Franz

## Gateway-Roadmap

- Aktueller Produktionsrand:
  - Vodafone Easy Box bleibt bis auf Weiteres der aktive Router im Live-Netz
- Geplante Zielplattform:
  - `UniFi Cloud Gateway Ultra (UCG-Ultra)` als spaeterer Ersatz fuer die Easy Box
- Warum noch nicht jetzt:
  - der Dienstestand auf Proxmox und `CT 100` wird noch aktiv aufgebaut
  - ein Gateway-Cutover wuerde DHCP, Routing und Client-Erreichbarkeit gleichzeitig beruehren
  - zu frueher Umstieg erzeugt vermeidbare Fehlersuche an zwei Stellen gleichzeitig: Dienste und Netzrand
- Richtiger Einfuehrungszeitpunkt:
  - nach dem Aufbau aller geplanten LXC-/VM-Grundsysteme
  - nach praktischem Backup-/Restore-Nachweis fuer die Business-VMs
  - nach finalem IP- und Reservierungsplan
  - in einem eigenen Wartungsfenster mit dokumentiertem Rueckweg auf die Easy Box
- Planerische Konsequenz schon heute:
  - neue Reservierungs-, VLAN- und Firewall-Ideen werden konzeptionell auf den UCG-Ultra ausgerichtet
  - operative Live-Aenderungen bleiben bis zum Cutover auf die Easy Box begrenzt

## Architekturentscheidungen

### Business

- Odoo, Nextcloud und Paperless laufen aus Isolationsgruenden in getrennten VMs.
- Business-Daten verbleiben auf dediziertem VM-Storage; keine produktive Vermischung mit Toolbox-Volumes.
- Odoo benoetigt persistente PostgreSQL-Datenhaltung in der VM.
- Nextcloud wird auf Performance optimiert, mit Redis-Cache und NVMe-nahem Storage.
- Live-Stand vom Audit:
  - `VM 200 nextcloud` ist lauffaehig, per HTTP erreichbar, QGA-verifiziert und wird jetzt ueber `homeserver-compose-nextcloud.service` aus `/opt/homeserver2027/stacks/nextcloud` betrieben.
  - `VM 220 odoo` wurde bereinigt, antwortet wieder auf Port `8069`, ist QGA-verifiziert und wird jetzt ueber `homeserver-compose-odoo.service` aus `/opt/homeserver2027/stacks/odoo` betrieben.
  - `VM 230 paperless` ist gesund, QGA-verifiziert und wird jetzt ueber `homeserver-compose-paperless.service` aus `/opt/homeserver2027/stacks/paperless` betrieben.
  - Server-Baseline auf den Business-VMs ist seit `2026-03-18` gehaertet:
    - `LLMNR=no`
    - `MulticastDNS=no`
    - keine oeffentlich gebundenen DB-Ports auf den Business-VMs beobachtet

### Smart Home

- Home Assistant laeuft als `VM 210` auf Basis von Home Assistant OS.
- Begruendung:
  - stabilster Weg fuer Supervisor und Add-on-Verwaltung
  - bester operativer Pfad fuer USB-Passthrough
  - sichere Snapshots vor Updates
  - effiziente VM-Backups statt dateibasierter Container-Sicherung
- Phase-1-Datenhaltung:
  - Recorder bleibt zunaechst auf internem HAOS-Storage
  - keine externe MariaDB in Phase 1
- Verifizierter Live-Stand vom `2026-03-18`:
  - `VM 210` ist angelegt und laeuft
  - Basiskonfiguration:
    - `q35`
    - `OVMF`
    - `2 vCPU`
    - `4096 MB` RAM
    - `32 GB` Disk auf `local-lvm`
    - MAC `BC:24:11:D5:BA:30`
  - die LAN-Adresse ist stabil auf `192.168.2.24`
  - Home Assistant antwortet dort mit `HTTP 200` auf Port `8123`
  - `ha.hs27.internal` liefert ueber Caddy auf `CT 100` ebenfalls `HTTP 200`
  - Reverse-Proxy-Trust in Home Assistant ist fuer `192.168.2.20` gesetzt
  - aktuell sind keine externen USB-/Seriell-Adapter am Proxmox-Host sichtbar
  - `lsusb` zeigt nur Root-Hubs, `/dev/serial/by-id` ist leer
  - USB-Passthrough ist damit derzeit nur konzeptionell vorbereitet, nicht praktisch pruefbar

### Media / Radio

- AzuraCast wird strategisch auf einen dedizierten `Raspberry Pi 4` verschoben.
- Begruendung:
  - klare Trennung von Infrastruktur und Media-Last
  - weniger Ressourcen- und Rootfs-Druck auf `CT 100`
  - saubererer Zielpfad fuer den spaeteren Radio-/Medienausbau
- `CT 100` bleibt Frontdoor fuer `radio.hs27.internal`, routed jetzt aber intern auf den Raspberry-Pi-Radio-Node
- der dedizierte Zielpfad ist in `RASPBERRY_PI_RADIO_NODE_PLAN.md` dokumentiert

### Shared Frontend

- Das Surface Go auf `192.168.2.154` ist als gemeinsamer `frontend-node` fuer Franz und Wolf vorgesehen.
- Zielrolle:
  - Touch-Kiosk fuer interne Startseite, Home Assistant, Nextcloud und spaeter Radio
  - optionaler lokaler Admin-Desktop als Fallback
- Aktueller Ist-Zustand:
  - Hostname `surface-go-frontend`
  - stabile Remote-Admin-Schiene ueber SSH-Key vorhanden
  - `frontend` als kiosk-User ohne sudo vorhanden
  - lokales Portal und GDM-Autologin gesetzt
  - `nginx` entfernt, `HTTP/80` und `HTTPS/443` geschlossen
  - Tailscale ist installiert, aber noch nicht im Tailnet authorisiert
- Verbindlicher Zielpfad:
  - Clean Rebuild statt In-Place-Entschlackung
  - `Ubuntu Desktop 24.04 LTS`
  - Standard-Ubuntu-Kernel zuerst, `linux-surface` nur bei realen Hardware-Luecken
  - lokaler Admin-User `frawo`
  - separater kiosk-User ohne sudo
  - kein lokaler Server-Stack auf dem Geraet

### Netzwerk

- Kein oeffentliches Port-Forwarding fuer Admin-UIs oder Business-Dienste.
- Externer Zugriff laeuft ueber Tailscale.
- `CT 100` ist das Ziel fuer den Tailscale-Subnet-Router fuer `192.168.2.0/24`.
- Tailscale ist auf `CT 100` live und dem Tailnet beigetreten.
- Caddy in `CT 100` bietet internes L7-Routing.
- AdGuard Home laeuft als interner DNS-/Filter-Dienst in `CT 100` im Opt-in-Testbetrieb.
- `portal.hs27.internal` ist die gemeinsame interne Frontdoor fuer den spaeteren Surface-Go-Kioskpfad.
- Einfuehrungsmodell fuer AdGuard Home:
  - Phase 1: Opt-in-Testbetrieb fuer Trusted Clients, Admin-Endgeraete und `hs27.internal` ist live
  - Phase 2: primaerer LAN-DNS erst nach kontrollierter DHCP-Fuehrung und dokumentiertem Rollback
- Namensmodell:
  - MagicDNS fuer Knoten
  - Split-DNS-Zone `hs27.internal` fuer Dienste

### Public Exposure

- Oeffentliche Exposition ist ausdruecklich nicht Teil der aktuellen Live-Phase.
- Wenn die Oeffnung spaeter noetig wird, gilt als Zielbild:
  - dedizierte Edge-Rolle fuer oeffentliche App-Endpunkte
  - TLS mit sauberem Domain-/DNS-Setup
  - vorgeschaltete Auth, Logging und Monitoring
  - nur explizit freigegebene App-Endpunkte, keine Admin-Oberflaechen
- Nie direkt oeffentlich exponieren:
  - Proxmox
  - Toolbox-Admin
  - PBS
  - AdGuard Home
  - Home Assistant Admin
- Stage Gate fuer Public Exposure:
  - UCG-Ultra oder gleichwertige saubere Firewall-/Segmentierungsfuehrung ist aktiv
  - Inventar, Reservierungen und Zonenmodell sind final
  - Backups und Restore sind praktisch bewiesen
  - Domain, DNS, Zertifikate, Monitoring und Rollback sind dokumentiert

### Backup / Recovery

- Zielarchitektur: dedizierte PBS-Instanz
- V1-Default: dedizierte PBS-VM, wenn keine separate Backup-Hardware bereitsteht
- PBS-Rolloutpfad ist seit `2026-03-18` vorbereitet:
  - `ansible/playbooks/deploy_pbs_vm_runner.yml`
  - `/usr/local/sbin/homeserver2027-deploy-pbs-vm.sh`
  - `make pbs-preflight`
  - `make pbs-stage-gate`
  - `make pbs-vm-check`
- Aktueller Stage-Gate-Blocker fuer PBS:
  - kein separates Backup-Storage unter `/srv/pbs-datastore` gemountet
  - die PBS-Installer-ISO liegt jetzt bereit unter `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`
  - SHA256 der aktuell gestagten ISO: `670f0a71ee25e00cc7839bebb3f399594f5257e49a224a91ce517460e7ab171e`
- Proxmox-Snapshot-Guardrails wurden gehaertet:
  - temporaere Codex-Snapshots auf den Business-VMs werden nach erfolgreicher Verifikation wieder entfernt
  - `local-lvm` ist vergroessert und hat aktive Thin-Pool-Autoextend-Regeln
- Backup-Umfang:
  - `CT 100`
  - `VM 200`
  - `VM 210`
  - `VM 220`
  - `VM 230`
- Verifizierter Zwischenstand vom `2026-03-18`:
  - lokale `vzdump`-Backups fuer `VM 200`, `VM 210`, `VM 220` und `VM 230` erfolgreich auf Storage `local`
  - Odoo-Restore-Test von `VM 220` nach `VM 920` erfolgreich
  - Test-IP `192.168.2.240`, Odoo-Login unter `/web/login` mit `HTTP 200` bestaetigt
  - Test-VM `920` danach wieder entfernt, damit kein Muell im Cluster bleibt
  - taeglicher lokaler Zwischenstandard ist jetzt live:
    - Proxmox timer `homeserver2027-local-business-backup.timer`
    - taeglicher Lauf um `02:40`
    - initial verifizierter Service-Run mit neuen Archiven fuer `200`, `220`, `230`
    - nach Integration von HAOS wurde der Service erneut erfolgreich fuer `200`, `210`, `220`, `230` ausgefuehrt
    - Retention nach dem Lauf: `2` lokale Archive pro gesicherter VM
- Restore-Standard:
  - monatlicher Test-Restore einer VM auf Test-ID
  - Erfolg bedeutet Boot plus erfolgreicher App-Login

## Guardrails, die in allen Artefakten gelten

- Snapshot vor jeder aendernden Arbeit an `CT 100` und VMs `200/210/220/230`
- Proxmox-MCP ist die primaere Lifecycle-Schnittstelle
- QEMU Guest Agent ist hilfreich, aber keine harte Abhaengigkeit
- `CT 100` darf bei Bedarf neu gebaut werden, solange Rolle und IP erhalten bleiben

## Historische Konflikte und deren Aufloesung

- Aeltere Artefakte vertauschten `VM 200` und `VM 220`.
  - Neu verbindlich: `VM 200 = Nextcloud`, `VM 220 = Odoo`
- Aeltere Artefakte fuehrten Home Assistant oder AzuraCast gemeinsam als "Media-Toolbox".
  - Neu verbindlich: `VM 210 = HAOS`, `CT 100 = Toolbox + Infra-Dienste`, `raspberry_pi_radio = AzuraCast`
- Aeltere Artefakte beschrieben `CT 100` als reine Admin-Toolbox.
  - Neu verbindlich: `CT 100` ist Admin-Toolbox plus Docker-/VPN-/Proxy-/DNS-Plattform
- Die fruehere Router-Bezeichnung `Surface_Laptop` gilt jetzt als weitgehend aufgeloest.
  - Neu verbindlich: gemeinsames Frontend-Geraet ist `yourparty-Surface-Go.local` auf `192.168.2.154`

## Deferred / Wishlist

- `Ollama` ist als spaeteres Wunschthema aufgenommen, aber aktuell nicht Teil des Umsetzungsplans.
- Begruendung:
  - der aktuelle Host hat nur `15 GB` RAM
  - fuer lokale KI-Inferenz neben Proxmox, Business-VMs, Toolbox und HAOS ist das zu knapp
  - der neue Capacity-Review bestaetigt den Host-RAM als primaeren Skalierungsengpass
- Wiedervorlage erst bei einem der folgenden Trigger:
  - RAM-Upgrade des Hosts
  - separater Inference-Node
  - Auslagerung auf externen KI-Host statt lokaler Proxmox-Nutzung

## Aktuelle Arbeitsauftraege

1. `NETWORK_INVENTORY.md` mit Easy-Box-Leases und DHCP-Reservierungen final abgleichen
   - bereits teilaufgeloest: `Wolf_Pixel`, `SonRoku`, Growbox-Shellys
   - `Surface_Laptop` ist jetzt als `yourparty-Surface-Go.local` auf `192.168.2.154` identifiziert
   - offen bleiben vor allem `fireTV`, `Franz_iphone`, `udhcpc1.21.1`, `udhcp 1.24.1` sowie die privaten MAC-Clients `.141-.144`
   - `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` ist jetzt der kanonische Browser-Pfad fuer diesen Abgleich
2. `CT 100` als Netzwerk-Basis fuer die naechste Phase vorbereiten
   - Tailnet-Join fuer `toolbox` ist abgeschlossen
   - mobiler Interimszugriff ueber `100.99.206.128:8443-8448` ist funktionsfaehig
   - Route `192.168.2.0/24` ist aktiv im Tailnet
   - AdGuard Home und internes Caddy-Routing im Opt-in-Betrieb stabil halten
   - `ADGUARD_PILOT_ROLLOUT_PLAN.md` definiert jetzt Pilot-Clients und Rollback
   - `TAILSCALE_SPLIT_DNS_PLAN.md` definiert jetzt den sauberen `hs27.internal`-Pfad fuer Tailscale-Clients
   - Split-DNS fuer `hs27.internal` ist auf dem ZenBook verifiziert; naechster Ausfuehrungsschritt ist der echte Handy-Off-LAN-Test und danach der DNS-Pilot
3. Den verifizierten lokalen Backup-/Restore-Proof fuer `VM 200`, `VM 220` und `VM 230` in PBS-Zielarchitektur, Retention und taegliche Jobs ueberfuehren
   - lokaler Proof und taeglicher Zwischenstandard auf Proxmox sind erfolgreich dokumentiert
   - Runner und Stage-Gate-Pfad fuer `VM 240` sind vorbereitet
   - die offizielle PBS-ISO ist bereits staged und verifiziert
   - naechster Schritt ist separates Backup-Storage statt weiterer Planungsarbeit
4. Die spaetere Public-Exposure-Architektur planen, aber noch nicht live schalten
   - `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` ist jetzt der kanonische Zielpfad
   - Domain-/DNS-Modell
   - Edge-Trennung
   - TLS, Monitoring, Auth und Rollback
5. `HAOS_VM_210_SETUP_PLAN.md` vom Basis-Build in den abgesicherten Betriebsstandard ueberfuehren
   - `VM 210` laeuft stabil auf `192.168.2.24`
   - `ha.hs27.internal` liefert bereits ueber `CT 100`
   - lokaler Backup-Bestand deckt `VM 210` jetzt mit ab
   - USB-Passthrough bleibt bis zum Anstecken echter Adapter nur Planungsstand
6. Hardware-Audit fuer Zigbee- und Bluetooth-Dongles:
   - erster Auditlauf abgeschlossen: aktuell keine externen Adapter sichtbar
   - bei neuer Hardware erneut `lsusb` und `/dev/serial/by-id` erfassen
   - dann Vendor-ID, Product-ID und Zielgeraet pro Adapter dokumentieren
   - Verhalten nach Host- und VM-Reboot pruefen
7. Lokale Proof-Backups bis PBS live ist mit `make backup-prune-dry-run` und `make backup-prune` sauber halten
   - Standard bis PBS: letzte `2` lokale qemu-Backups pro Business-VM behalten
8. `make business-drift-check` als Standard-Post-Change-Kontrolle fuer die IaC-gesteuerten Business-Stacks nutzen
   - Basislauf vom `2026-03-18` ist gruen fuer Nextcloud, Odoo und Paperless
9. `make start-day` und `make security-baseline-check` als verbindlichen Tagesstart verwenden
   - Sicherheits-Baseline prueft Secrets, Port-Flaechen, Tailscale-Zustand und AdGuard-Admin-Flaeche mit
   - `make start-day` prueft jetzt zusaetzlich den PBS-Stage-Gate-Pfad und den Medienserver-V1
10. Legacy-Snapshot auf `VM 100` nur dann entfernen, wenn der Tailscale-/Toolbox-Pfad dafuer ersetzt oder abgeschlossen ist
11. EasyBox-805-Weboberflaeche weiter automatisieren, weil `user_lang.json`, Login und `overview.json` jetzt reproduzierbar funktionieren, aber tieferer Lease-/DHCP-Abgleich und Owner-Mapping noch nicht vollstaendig headless abgedeckt sind
12. `UniFi Cloud Gateway Ultra` als spaetere Netzrand-Migration vorbereiten, aber erst nach abgeschlossenem LXC-/VM-Basisaufbau, validierten Backups und finalem IP-Plan aktivieren
13. Capacity-Rightsizing in ein Wartungsfenster aufnehmen
   - `VM 200 nextcloud`: Ziel `2048 MB` RAM
   - `VM 220 odoo`: Ziel `2048 MB` RAM
   - `VM 210` und `VM 230` vorerst bewusst unveraendert lassen
   - vor spaeteren zusaetzlichen Frontdoor-/Public-Edge-Diensten den Rootfs- und RAM-Bedarf von `CT 100` neu bewerten
14. Shared Frontend Node `Surface Go` in den finalen Managed-Frontend-Standard ueberfuehren
   - Clean Rebuild und Basis-Bootstrap sind abgeschlossen
   - SSH-Key-Zugang, Kiosk-User `frontend`, lokales Portal und GDM-Autologin sind live
   - naechster technischer Schritt ist der Tailnet-Join fuer das Surface und danach die Postinstall-Abnahme per Reboot
   - das Surface-Portal soll jetzt `Radio` und `Radio Control` nativ fuer AzuraCast anbieten
15. Installationsmedien und Remote-Zugriff fuer die naechste Hardwarewelle vorbereiten
   - `MEDIA_AND_REMOTE_PREP.md` ist die kanonische Anleitung
   - Raspberry Pi 4 Zielimage: `Ubuntu Server 22.04.5 LTS ARM64`
   - Surface-Zielimage: `Ubuntu Desktop 24.04.4 LTS`
   - der `7.7G`-Stick `/dev/sdd` ist jetzt fertig als dedizierter Ventoy-Install-/Image-Stick
   - der `14.4G`-Stick `/dev/sdc` ist jetzt fertig als exFAT-Favorites-Stick `FRAWO_FAVS`
   - AnyDesk auf dem ZenBook ist inzwischen installiert und aktiv
16. Remote-Zugriff professionell absichern und dokumentieren
   - `REMOTE_ACCESS_STANDARD.md` ist die kanonische Anleitung
   - Tailscale ist der primaere Remote-Pfad
   - AnyDesk ist der GUI-Fallback auf dem ZenBook
17. Raspberry-Pi-Radio-Node in den nutzbaren internen Betriebsstandard ueberfuehren
   - `RASPBERRY_PI_RADIO_NODE_PLAN.md` ist die kanonische Anleitung
   - `RADIO_OPERATIONS_STANDARD.md` ist jetzt der operative Betriebsstandard
   - `make radio-ops-check` ist der schnelle Live-Check fuer Radio, Radio Control und `nowplaying`
   - `radio.hs27.internal` zeigt jetzt intern auf den Pi und liefert die AzuraCast-Login-Seite
   - die erste Station `FraWo - Funk` spielt bereits aus der direkt angeschlossenen USB-Bibliothek
   - naechster Schritt ist die kuratierte Betriebsueberfuehrung von USB-Musik zu `RadioLibrary` / `RadioAssets`
   - direkt danach sollen touchfreundliche Surface-Monitor-/Control-Views auf dieser stabilen Basis entstehen
18. Medienserver-V1 auf der Toolbox als echten Haushalts-Mehrwert bereitstellen
   - `MEDIA_SERVER_PLAN.md` ist die kanonische Anleitung
   - `MEDIA_SERVER_CLIENT_SETUP.md` beschreibt die ersten TV-/Browser-Pfade fuer Thomson und Google TV
   - Jellyfin ist jetzt intern live auf `http://media.hs27.internal`, direkt auf `http://192.168.2.20:8096` und mobil ueber `http://100.99.206.128:8449`
   - `make toolbox-media-check` ist jetzt der schnelle Betriebscheck
   - naechster Schritt ist die UI-basierte Erstkonfiguration mit Admin-Account und Bibliotheksanbindung
19. Remote-Only-Arbeitsfenster fuer Arbeitstage ausser Haus standardisieren
   - `REMOTE_ONLY_WORK_WINDOW.md` ist die kanonische Anleitung
   - `make remote-only-check` ist der schnelle Gate-Check
   - bis physische Schritte moeglich sind, nur dort freigegebene Aufgaben ziehen
20. AdGuard-DNS-Pilot kontrolliert vorbereiten
   - `ADGUARD_PILOT_ROLLOUT_PLAN.md` ist die kanonische Anleitung
   - `make adguard-pilot-check` prueft den read-only Pilotpfad und den LAN-Rollback-Schutz
21. Tailscale-Split-DNS fuer `hs27.internal` kontrolliert vorbereiten
   - `TAILSCALE_SPLIT_DNS_PLAN.md` ist die kanonische Anleitung
   - `make tailscale-split-dns-check` prueft MagicDNS, Client-DNS, AdGuard, die Route-Voraussetzung und jetzt auch den echten `ha.hs27.internal`-Pfad ueber `100.100.100.100`
   - der restricted nameserver fuer `hs27.internal` ist im Tailnet gesetzt; ZenBook-Testpfad ist erfolgreich
22. Lease-Abgleich browser-first standardisieren
   - `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` ist die kanonische Anleitung
   - `make inventory-resolution-check` zeigt die verbleibenden Unknowns und Router-Labels
23. Public Edge als spaeteren professionellen Endzustand sauber vorkonzipieren
   - bevorzugter Marken-/Domainpfad ist jetzt `frawo.studio`
   - Zielhostnamen spaeter:
     - `www.frawo.studio`
     - `radio.frawo.studio`
   - bis dahin bleiben `portal.hs27.internal` und `radio.hs27.internal` die operativen internen Namen
   - interne Naming-Entscheidung: aktive Betriebszone bleibt `hs27.internal`; spaeterer professioneller Zielpfad ist `frawo.home.arpa`
   - `frawo.internal` und `frawo.lan` werden nicht als neue Standardzone eingefuehrt
   - `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` ist die kanonische Anleitung

## Aktive Operator-Aktionen

1. `AKTION VON DIR ERFORDERLICH:` Surface Go im Tailnet autorisieren
   - benoetigte Aktion: den vom Surface ausgegebenen Tailscale-Login-Link im Tailnet `w.prinz1101@gmail.com` bestaetigen
   - aktueller Link: `https://login.tailscale.com/a/d390b82011ece`
   - warum: Tailscale ist auf dem Surface installiert, aber noch `Logged out`
   - danach uebernehmen Codex/Gemini wieder: Tailnet-Verifikation, Reboot-Abnahme, Portal-/Radio-Control-Fit und optionales Touch-Finetuning
2. `AKTION VON DIR ERFORDERLICH:` Surface Go wieder aufwecken oder entsperren, sobald Franz vor Ort ist
   - benoetigte Aktion: Geraet physisch wecken, entsperren und wieder ins WLAN/LAN bringen
   - warum: der letzte Delta-Run lief in einen Timeout; das Fehlerbild passt zu Sleep/Suspend
   - danach uebernehmen Codex/Gemini wieder: Sleep-Ziele haerter deaktivieren, Reboot-Abnahme und Portal-Delta erneut ausrollen
3. `AKTION VON DIR ERFORDERLICH:` Jellyfin-V1 einmal in der UI initialisieren
   - benoetigte Aktion: `http://media.hs27.internal` oeffnen, den ersten Admin anlegen und die Bibliotheken `Movies`, `Shows`, `Music`, `Homevideos` an die Pfade unter `/media/*` haengen
   - warum: der Server selbst ist live und verifiziert, aber ohne Erst-Admin und Bibliothekszuordnung liefert er noch nicht den vollen Haushalts-Mehrwert fuer Thomson-/Google-TV-Clients
   - danach uebernehmen Codex/Gemini wieder: TV-Client-Pfad, Portal-/Monitor-Integration und spaetere Medienkuration
4. `AKTION VON DIR ERFORDERLICH:` separates Backup-Storage fuer PBS bereitstellen
   - benoetigte Aktion: zusaetzliches Backup-Storage liefern, anschliessen oder als Zielpfad fuer `/srv/pbs-datastore` auf Proxmox bereitstellen
   - warum: `pbs_stage_gate_ready=no`, solange `pbs_datastore_mount_state=missing` und `separate_backup_storage_ready=no`
   - danach uebernehmen Codex/Gemini wieder: `VM 240` bauen, PBS produktiv aufsetzen und Backup-Jobs umhaengen
5. `AKTION VON DIR ERFORDERLICH:` restliche Easy-Box-Geraete autoritativ zuordnen
   - benoetigte Aktion: die verbliebenen Unknown-Clients `.141-.144` sowie zusaetzliche aktuelle Router-Labels wie `Surface_Laptop`, `RE355` und `iPhone-3-Pro` fachlich bestaetigen oder benennen
   - warum: `inventory_unknown_review_count=4` und damit `inventory_finalized=no`
   - danach uebernehmen Codex/Gemini wieder: DHCP-/Reservierungsplan finalisieren und den Gateway-Cutover freigabefaehig machen
6. `AKTION VON DIR ERFORDERLICH:` HAOS-USB-Hardware am Proxmox-Host anstecken, sobald verfuegbar
   - benoetigte Aktion: Zigbee-/Bluetooth-/SkyConnect-Adapter physisch am Proxmox-Host anschliessen
   - warum: aktueller Audit zeigt nur Root-Hubs und kein `/dev/serial/by-id`
   - danach uebernehmen Codex/Gemini wieder: Vendor-/Product-ID-Audit, USB-Passthrough und Reboot-Stabilitaet testen
7. `AKTION VON DIR ERFORDERLICH:` Handy einmal echt off-LAN ueber Tailscale pruefen
   - benoetigte Aktion: WLAN am Handy aus, Tailscale verbunden lassen und `http://portal.hs27.internal`, `http://ha.hs27.internal` sowie `http://odoo.hs27.internal/web/login` testen
   - warum: Route und restricted nameserver sind jetzt live, aber der echte mobile Akzeptanztest fuer den `hs27.internal`-Pfad ist noch nicht bestaetigt
   - danach uebernehmen Codex/Gemini wieder: mobilen Betriebsstandard finalisieren und den Frontdoor fuer Endgeraete sauber freigeben

## IaC-Quellen fuer Business-Stacks

- Zielpfad im Workspace:
  - `ansible/playbooks/deploy_business_stacks.yml`
  - `ansible/templates/stacks/`
  - `ansible/templates/systemd/`
  - `ansible/inventory/host_vars/`
- Zielpfad auf den VMs:
  - `/opt/homeserver2027/stacks/<stack-name>`
- Die IaC-Deployment-Stufe ist live uebernommen.
- In-guest Altpfade unter `/home/wolf/<stack>/` wurden entfernt und gelten nicht mehr als Betriebsquelle.

## Erwartete Verifikation

- `GEMINI.md` und `MEMORY.md` nennen identische IDs, Rollen und Ziel-IPs.
- `NETWORK_INVENTORY.md` und `ansible/inventory/hosts.yml` enthalten denselben Live-Bestand.
- `VM 200`, `VM 220` und `VM 230` liefern `qm agent ... ping` erfolgreich zurueck.
- `VM 210` ist nach Bereitstellung unter `http://192.168.2.24:8123` oder ueber `ha.hs27.internal` im Tailnet erreichbar.
- Tailscale-Zugriff per direkter LAN-Zieladresse ist jetzt ueber die aktive Tailnet-Route `192.168.2.0/24` moeglich.
- Der mobile Toolbox-Tailscale-Frontdoor liefert aktuell `100.99.206.128:8443-8449`, inklusive Radio auf `:8448` und Media auf `:8449`.
- Zugriff per `ha.hs27.internal`, `odoo.hs27.internal` oder `radio.hs27.internal` ist jetzt ueber die verifizierte Split-DNS-Integration fuer `hs27.internal` vorbereitet.
- Ein lokaler Backup-/Restore-Proof fuer `VM 200`, `VM 220` und `VM 230` ist dokumentiert; der naechste Meilenstein sind taegliche PBS-Jobs.

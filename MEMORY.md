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
- neuer lokaler Studio-PC im LAN:
  - `WOLFSTUDIOPC`
  - `192.168.2.162`
  - Router-Overview bestaetigt Ethernet-Link und Hostname
  - aktueller Admin-Fingerprint: `135/139/445` offen, `22/3389/5985/5986` geschlossen
  - naechster reproduzierbarer Pfad: Repo lokal auf dem Windows-PC bereitstellen, dann `scripts\\bootstrap_windows_workspace.cmd` fuer Alias und Desktop-Shortcut ausfuehren
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
  - verifizierter Runtime-Stand vom `2026-04-07`:
    - der produktive Frontdoor laeuft containerisiert als `toolbox-network_caddy_1`
    - `homeserver2027-toolbox-mobile-firewall.service` ist aktiv und die `HOMESERVER2027_MOBILE`-iptables-Kette begrenzt `8443-8449` weiterhin auf `lo` und `tailscale0`
    - der Host-Dienst `caddy.service` kann dabei trotzdem `inactive` sein; entscheidend ist der Docker-Caddy-Stack
- Geplante Edge-Hardware / UCG-Stand:
  - `UniFi Cloud Gateway Ultra (UCG-Ultra)` ist jetzt live fuer `proxmox-anker`
  - der direkte StudioPC-Pfad in die isolierten Legacy-Gaeste laeuft waehrend der Migration nicht ueber lokale `192.168.2.x`, sondern `Tailscale first` ueber `toolbox`
  - Proxmox stellt dafuer einen temporaeren Transition-Router fuer die isolierte interne `192.168.2.0/24`-Gastwelt bereit
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

## Freigaben-Uebersicht

Interne HTTP-Freigaben (LAN, via Caddy / hs27.internal):
- `portal.hs27.internal` -> CT 100 Caddy (Frontdoor)
- `cloud.hs27.internal` -> Nextcloud (VM 200)
- `odoo.hs27.internal` -> Odoo (VM 220)
- `paperless.hs27.internal` -> Paperless (VM 230)
- `ha.hs27.internal` -> Home Assistant (VM 210)
- `radio.hs27.internal` -> AzuraCast (raspberry_pi_radio)
- `media.hs27.internal` -> Jellyfin (CT 100)

Mobile Tailscale-Frontdoor (Tailscale-only):
- `100.99.206.128:8443` -> Home Assistant
- `100.99.206.128:8444` -> Odoo
- `100.99.206.128:8445` -> Nextcloud
- `100.99.206.128:8446` -> Paperless
- `100.99.206.128:8447` -> Portal
- `100.99.206.128:8448` -> Radio
- `100.99.206.128:8449` -> Media

Storage-Freigaben (CT 110, geplant):
- NFS: `/mnt/data/documents` (Paperless + Nextcloud External Storage)
- NFS: `/mnt/data/media` (Jellyfin + AzuraCast)
- SMB: nur falls Windows-LAN-Clients zwingend benoetigt; sonst deaktiviert

Lokale Admin-Flaechen (nur localhost):
- `127.0.0.1:3000` -> AdGuard Admin (CT 100)

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
  - am `2026-03-23` wurde ein Drift bereinigt:
    - der Container lief, Nextcloud selbst war aber noch nicht wirklich installiert
    - der Stack wurde kontrolliert auf leere Nutzdatenbasis zurueckgesetzt und aus IaC neu initialisiert
    - Admin-User `frawoadmin` und Frontend-User `frontend` sind jetzt vorhanden
    - die verwendeten Passwoerter liegen ausschliesslich verschluesselt in `ansible/inventory/group_vars/all/vault.yml`
  - Nextcloud-Remediation vom `2026-04-07`:
    - Compose-Drift in `VM 200` hatte `db` auf `mariadb:10.6` zurueckfallen lassen, obwohl die vorhandenen Redo-Logs bereits von `10.11` stammten
    - zusaetzlich lief ein verwaister `nextcloud:latest`-Altcontainer ausserhalb des beabsichtigten Stackzustands; parallel lag App-Version-Drift gegen die vorhandenen Nutzdaten vor
    - der Stack wurde auf `/opt/homeserver2027/stacks/nextcloud/docker-compose.yml` mit `stack.env`, `mariadb:10.11`, `redis:alpine` und `nextcloud:latest` zurueckgefuehrt und per `docker-compose up -d --force-recreate --remove-orphans` bereinigt
    - der Standardpfad fuer App-Reparatur lief ueber `php occ upgrade`, `php occ maintenance:repair --include-expensive` und das bewusste Deaktivieren des Maintenance-Modus; direkte DB-Schreibfixes wurden dabei vermieden
    - danach liefern `cloud.hs27.internal/` und `/status.php` wieder `HTTP 200`, `maintenance=false`, `needsDbUpgrade=false`, und `homeserver-compose-nextcloud.service` ist wieder `active`
    - separater Mail-Abruf-Fix am selben Tag: Cloud-Init-DNS der VM zeigte noch auf Tailscale (`100.100.100.100`, `tail150400.ts.net`), obwohl `tailscaled` dort gar nicht lief
    - persistenter Fix lief ueber Proxmox-Cloud-Init auf `nameserver 10.1.0.20` und `searchdomain hs27.internal`
    - danach loesen VM und Container `imap.strato.de` wieder auf; der TLS-Handshake auf `993` ist verifiziert gruen
  - `VM 220 odoo` wurde bereinigt, antwortet wieder auf Port `8069`, ist QGA-verifiziert und wird jetzt ueber `homeserver-compose-odoo.service` aus `/opt/homeserver2027/stacks/odoo` betrieben.
  - Odoo-Remediation vom `2026-04-07`:
    - Compose-Drift in `VM 220` wurde bereinigt; `web` nutzt wieder `stack.env` und `./odoo.conf:/etc/odoo/odoo.conf:ro`
    - ein `docker-compose up -d --force-recreate --remove-orphans` hat den kaputten Alt-Container ersetzt
    - die mobile Toolbox-Frontdoor `100.99.206.128:8444` hatte keinen aktiven `:8444`-Caddy-Block; dieser wurde nachgezogen
    - danach zeigte sich Versions-Drift: Datenbank `FraWo_GbR` ist `Odoo 17`, waehrend der Web-Container auf `odoo:16.0` zurueckgefallen war
    - der Web-Container wurde wieder auf `odoo:17` gezogen; danach liefern direkter Odoo-Pfad, `odoo.hs27.internal` und `100.99.206.128:8444` `HTTP 200`
    - zusaetzlicher Drift lag im Filestore: Odoo 17 las aus `.local/share/Odoo/filestore/FraWo_GbR`, waehrend viele Dateien noch unter `filestore/FraWo_GbR` lagen
    - die fehlenden Filestore-Dateien wurden nicht-destruktiv in den erwarteten Pfad uebernommen; die Fehlmenge sank von `498` auf `0`
    - Guardrail ab hier: keine direkten SQL-Schreibfixes ohne frischen VM-Backup-/Snapshot-Nachweis; verifizierte lokale Rueckwege fuer `VM 220` liegen unter `/var/lib/vz/dump`, zuletzt auch vom `2026-04-07 19:40:44`
  - `VM 230 paperless` ist gesund, QGA-verifiziert und wird jetzt ueber `homeserver-compose-paperless.service` aus `/opt/homeserver2027/stacks/paperless` betrieben.
  - fuer `VM 230 paperless` sind jetzt ebenfalls ein Admin-User `frawoadmin` und ein Frontend-User `frontend` vorhanden
    - die verwendeten Passwoerter liegen ausschliesslich verschluesselt in `ansible/inventory/group_vars/all/vault.yml`
  - zwischen `VM 230 paperless` und `VM 200 nextcloud` ist jetzt ein erster echter Dokumenten-Bridge-Pfad live:
    - Nextcloud-Zielnutzer fuer den Brueckenpfad ist `frontend`
    - Uploads nach `Paperless/Eingang` in Nextcloud werden im 5-Minuten-Takt in den lokalen Paperless-Consume-Pfad verschoben
    - OCR-/Archivdateien aus `paperless_media/documents/archive` werden im 5-Minuten-Takt nach `Paperless/Archiv` in Nextcloud gespiegelt
    - Betriebscheck: `make paperless-nextcloud-bridge-check`
  - Server-Baseline auf den Business-VMs ist seit `2026-03-18` gehaertet:
    - `LLMNR=no`
    - `MulticastDNS=no`
    - keine oeffentlich gebundenen DB-Ports auf den Business-VMs beobachtet
  - Odoo-Board-Readout vom `2026-04-07`:
    - das Masterprojekt `🚀 Homeserver 2027: Masterplan` (`id=21`) ist jetzt als operativer `task SSOT` normalisiert
    - genau sechs kanonische Projektphasen sind im Projekt verknuepft: `Backlog`, `Planung & Vorbereitung`, `In Arbeit`, `Automatisierung`, `Blockiert`, `Erledigt`
    - `#217 Service Reachability Audit` steht auf `✅ Erledigt`
    - `#225 Nextcloud Stabilization` steht auf `✅ Erledigt`
    - der Folge-Task `Nextcloud Runtime Hardening / Version Pinning` ist sichtbar offen
    - `rootflo2525@gmail.com` ist nicht mehr als Owner im Masterprojekt verknuepft
    - `ownerless_open=0` ist fuer das Masterprojekt DB-seitig verifiziert
    - `agent@frawo-tech.de` ist auf Server-/Ops-/Automation-Tasks gezielt als Co-Owner verlinkt; API-Key, Alias-Intake und n8n bleiben vorbereitete Folgepunkte
  - Odoo-Agent-/Alias-Audit vom `2026-04-08`:
    - Projekt `21` hat die Alias-Domain `frawo-tech.de`, aber `alias_name=false` und damit noch keinen live geschalteten Intake-Pfad
    - Alias-Status aktuell `not_tested`, `alias_contact=employees`, `alias_model=project.task`, `alias_defaults={'project_id': 21}`
    - `agent@frawo-tech.de` ist aktiv, `share=false`, `totp_enabled=false`, `api_key_count=1`
    - heuristisch keine erkennbaren Admin-/Settings-/Studio-Gruppen am `agent@`-User gefunden
    - erlaubte Alias-Scope-Werte in der Instanz: `everyone`, `partners`, `followers`, `employees`
    - fuer einen internen Pilot ist `employees` jetzt bereits gesetzt; ein Aliasname fehlt bewusst noch, damit der Intake-Pfad nicht unkontrolliert live geht
    - serverseitig erzeugter RPC-Key fuer `agent@` liegt als root-only Staging-Secret ausserhalb des Repos unter `/root/.config/homeserver2027/odoo_agent_rpc.env`
    - Read-only-Check dafuer liegt jetzt in `odoo_agent_readiness_audit.py`
  - Odoo-Runtime-Drift vom `2026-04-08`:
    - Webcontainer fiel erneut mit `password authentication failed for user "odoo"` aus
    - lokaler PostgreSQL-Container hatte zwar eigene Env-Werte, aber der echte Docker-Netzpfad akzeptierte weiter nur das frueher etablierte Secret aus dem bestehenden Volume
    - zusaetzlich blockierten `600`-Rechte auf `odoo.conf` und `stack.env` den gemounteten Startpfad
    - Remediation: `docker-compose.yml` zurueck auf `env_file` plus `odoo.conf`-Mount, Stack wieder auf das echte DB-Secret gezogen, Dateirechte lesbar gestellt
    - danach wieder verifiziert: direkt `127.0.0.1:8069`, intern `odoo.hs27.internal` und mobil `100.99.206.128:8444` jeweils `HTTP 200`

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
  - Tailscale ist jetzt im Tailnet und aktuell ueber `100.106.67.127` verifiziert
  - GNOME-Idle ist `0`, Schlafmodus auf Netzstrom und Akku ist auf `nothing` gesetzt
  - Root-Sleep-Haertung ist jetzt fertig: `sleep.target`, `suspend.target`, `hibernate.target` und `hybrid-sleep.target` sind maskiert
  - Reboot-Test ueber den Tailnet-Pfad ist erfolgreich
  - letzter offener Rest ist nur noch die visuelle Reboot-/Kiosk-Abnahme vor Ort
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
- Der technische Surface-Kern ist jetzt gruen: SSH, Tailscale, Root-Sleep-Hardening und lokaler Portalservice stehen; offen ist vor allem lokaler UX-Feinschliff fuer Browser-/Touch-Tastatur-Verhalten.
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
- Aktueller verifizierter PBS-v1-Stand:
  - die PBS-Installer-ISO liegt bereit unter `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`
  - SHA256 der aktuell gestagten ISO: `670f0a71ee25e00cc7839bebb3f399594f5257e49a224a91ce517460e7ab171e`
  - `VM 240 pbs` ist installiert und per SSH/Web auf `192.168.2.25` erreichbar
  - Datastore `hs27-interim` liegt im Gast auf `/mnt/datastore-interim`
  - Proxmox-Storage `pbs-interim` ist aktiv
  - taeglicher PBS-Job `hs27-pbs-interim-daily` fuer `200,210,220,230` ist angelegt
  - Interim-Retention ist platzbewusst gesetzt:
- Schedule `02:40`
    - `keep-daily=2`
    - `keep-weekly=1`
    - `keep-monthly=1`
  - erster gruener Proof-Backup-Lauf ist jetzt nachgewiesen:
    - `VM 220`
    - Snapshot `vm/220/2026-03-21T10:04:30Z`
    - Proxmox-Taskstatus `exitstatus: OK`
  - erster gruener Restore-Drill auf dem PBS-v1-Pfad ist jetzt ebenfalls nachgewiesen:
    - Restore von `VM 220` nach Test-VM `920`
    - Test-IP `192.168.2.240`
    - Odoo-Login unter `/web/login` mit `HTTP 200`
    - Test-VM `920` danach wieder entfernt
  - zweiter automatisierter Restore-Drill auf dem PBS-v1-Pfad hat die Stabilität erfolgreich bestätigt
  - offener Restblock sind jetzt wiederkehrende Restore-/Betriebsnachweise, nicht mehr die Erstinbetriebnahme
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
   - Router-Label-Mapping ist inzwischen weitgehend sauber; `fireTV`, `Franz_iphone`, `udhcpc1.21.1` und `udhcp 1.24.1` sind bereits auf aktive IPs gemappt
   - offen bleiben vor allem die privaten MAC-Clients `.141-.144` sowie kleinere Alias-/Raumzuordnungen aus dem Router-Ueberblick
   - neuer Fingerprint-Stand fuer `.141-.144`: alle vier antworten auf Ping, aber halten `53/80/443/5353/8008/8069/8080` geschlossen und liefern kein HTTP; aktuell also eher stille Privat-Clients als Admin-/IoT-Endpunkte
   - `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` ist jetzt der kanonische Browser-Pfad fuer diesen Abgleich
2. Single Source of Truth Storage Node (CT 110) umsetzen
   - `ansible/playbooks/deploy_storage_node.yml` ausfuehren
   - NFS-Exports `/mnt/data/documents` und `/mnt/data/media` bereitstellen
   - Mounts fuer `VM 200`, `VM 230`, `CT 100` und `raspberry_pi_radio` vorbereiten
3. `CT 100` als Netzwerk-Basis fuer die naechste Phase vorbereiten
   - Tailnet-Join fuer `toolbox` ist abgeschlossen
   - mobiler Interimszugriff ueber `100.99.206.128:8443-8448` ist funktionsfaehig
   - Route `192.168.2.0/24` ist aktiv im Tailnet
   - AdGuard Home und internes Caddy-Routing im Opt-in-Betrieb stabil halten
   - `ADGUARD_PILOT_ROLLOUT_PLAN.md` definiert jetzt Pilot-Clients und Rollback
   - `TAILSCALE_SPLIT_DNS_PLAN.md` definiert jetzt den sauberen `hs27.internal`-Pfad fuer Tailscale-Clients
   - AdGuard DNS-Pilot (Stage A & B) ist auf dem ZenBook erfolgreich ausgerollt und stabil. Das ZenBook nutzt nun 192.168.2.20 lokal. 
   - Naechster Ausfuehrungsschritt ist der echte Handy-Off-LAN-Test (Stage C) und die finale DHCP-Promotion.
4. Den verifizierten lokalen Backup-/Restore-Proof fuer `VM 200`, `VM 220` und `VM 230` in PBS-Zielarchitektur, Retention und taegliche Jobs ueberfuehren
   - lokaler Proof und taeglicher Zwischenstandard auf Proxmox sind erfolgreich dokumentiert
   - Runner und Stage-Gate-Pfad fuer `VM 240` sind nicht nur vorbereitet, sondern live umgesetzt
   - `VM 240 pbs` laeuft jetzt mit `3072 MB` RAM, `32G` Systemdisk auf `local-lvm` und `40G` USB-Data-Disk auf `pbs-usb`
   - Datastore `hs27-interim` ist im Gast aktiv und Proxmox-Storage `pbs-interim` ist angebunden
   - taeglicher PBS-Job `hs27-pbs-interim-daily` ist angelegt
- platzbewusste Interim-Retention ist aktiv: `02:40` mit `keep-daily=2`, `keep-weekly=1`, `keep-monthly=1`
   - erster gruener Proof-Backup-Lauf ist jetzt erbracht: `VM 220` erfolgreich nach `pbs-interim`
   - erster gruener Restore-Drill ist jetzt ebenfalls erbracht: `VM 220` -> Test-VM `920` -> `HTTP 200` auf Odoo-Login
   - zweiter automatisierter Restore-Drill (`VM 220` -> `920`) war ebenfalls erfolgreich und beweist die Reproduzierbarkeit
   - der aktuelle Restblock ist jetzt primär größeres PBS-Storage für den späteren Dauerbetrieb
5. Die spaetere Public-Exposure-Architektur planen, aber noch nicht live schalten
   - `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` ist jetzt der kanonische Zielpfad
   - Domain-/DNS-Modell
   - Edge-Trennung
   - TLS, Monitoring, Auth und Rollback
6. `HAOS_VM_210_SETUP_PLAN.md` vom Basis-Build in den abgesicherten Betriebsstandard ueberfuehren
   - `VM 210` laeuft stabil auf `192.168.2.24`
   - `ha.hs27.internal` liefert bereits ueber `CT 100`
   - lokaler Backup-Bestand deckt `VM 210` jetzt mit ab
   - USB-Passthrough bleibt bis zum Anstecken echter Adapter nur Planungsstand
   - der neue Audit-Guardrail ist aktiv: der sichtbare externe USB-Pfad ist derzeit nur der PBS-Backup-Stick und zaehlt ausdruecklich nicht als HAOS-Dongle
7. Hardware-Audit fuer Zigbee- und Bluetooth-Dongles:
   - aktueller Auditlauf ist jetzt praeziser: Root-Hubs plus ein USB-Massenspeicher (`USB Disk 3.0`) sind sichtbar, aber keine seriellen Funkadapter
   - `make haos-usb-audit` ist jetzt der kanonische Schnellcheck
   - bei neuer Hardware erneut `lsusb` und `/dev/serial/by-id` erfassen
   - dann Vendor-ID, Product-ID und Zielgeraet pro Adapter dokumentieren
   - Verhalten nach Host- und VM-Reboot pruefen
8. Lokale Proof-Backups bis PBS live ist mit `make backup-prune-dry-run` und `make backup-prune` sauber halten
   - Standard bis PBS: letzte `2` lokale qemu-Backups pro Business-VM behalten
   - Runtime-Korrektur vom `2026-04-07`: `pve-root` lief voll, weil in `/var/lib/vz/dump` wieder `3` Archive pro Business-VM lagen; der aelteste Satz vom `2026-04-06` fuer `VM 200`, `210`, `220` und `230` wurde entfernt, danach fiel `pve-root` auf ca. `83%` und `apt update` lief wieder erfolgreich
9. `make business-drift-check` als Standard-Post-Change-Kontrolle fuer die IaC-gesteuerten Business-Stacks nutzen
   - Basislauf vom `2026-03-18` ist gruen fuer Nextcloud, Odoo und Paperless
10. `make start-day` und `make security-baseline-check` als verbindlichen Tagesstart verwenden
   - Sicherheits-Baseline prueft Secrets, Port-Flaechen, Tailscale-Zustand und AdGuard-Admin-Flaeche mit
   - `make start-day` prueft jetzt zusaetzlich den PBS-Stage-Gate-Pfad und den Medienserver-V1
11. Legacy-Snapshot auf `VM 100` nur dann entfernen, wenn der Tailscale-/Toolbox-Pfad dafuer ersetzt oder abgeschlossen ist
12. EasyBox-805-Weboberflaeche weiter automatisieren, weil `user_lang.json`, Login und `overview.json` jetzt reproduzierbar funktionieren, aber tieferer Lease-/DHCP-Abgleich und Owner-Mapping noch nicht vollstaendig headless abgedeckt sind
13. `UniFi Cloud Gateway Ultra` als spaetere Netzrand-Migration vorbereiten, aber erst nach abgeschlossenem LXC-/VM-Basisaufbau, validierten Backups und finalem IP-Plan aktivieren
14. Capacity-Rightsizing in ein Wartungsfenster aufnehmen
   - `VM 200 nextcloud`: Ziel `2048 MB` RAM
   - `VM 220 odoo`: Ziel `2048 MB` RAM
   - `VM 210` und `VM 230` vorerst bewusst unveraendert lassen
   - vor spaeteren zusaetzlichen Frontdoor-/Public-Edge-Diensten den Rootfs- und RAM-Bedarf von `CT 100` neu bewerten
15. Shared Frontend Node `Surface Go` in den finalen Managed-Frontend-Standard ueberfuehren
   - Clean Rebuild und Basis-Bootstrap sind abgeschlossen
   - SSH-Key-Zugang, Tailnet-Admin-Pfad, Kiosk-User `frontend`, lokales Portal und GDM-Autologin sind live
   - Root-Sleep-Haertung ist abgeschlossen; die Sleep-Targets sind maskiert
    - das Surface-Frontend nutzt jetzt einen robusteren lokalen Pfad mit dynamischen Shortcuts (Nextcloud Eingang, Archiv, Paperless Suche) und einer Dokumentenflow-Hilfe.
     - lokaler Portalservice auf `127.0.0.1:17827`
     - sichtbarer Launcher `FRAWO Control`
     - `epiphany-browser` ueber lokalen Wrapper als aktuelle Browser-Instanz
   - das Surface-Portal soll jetzt `Radio` und `Radio Control` nativ fuer AzuraCast anbieten
   - die lokale Surface-Portal-Vorlage ist jetzt auch fuer den gemeinsamen Live-Status-Snapshot aus `portal.hs27.internal/status.json` vorbereitet
   - der technische Kern ist gruen; offener Restblock ist jetzt lokaler Browser-/Touch-Tastatur-Polish
16. Installationsmedien und Remote-Zugriff fuer die naechste Hardwarewelle vorbereiten
   - `MEDIA_AND_REMOTE_PREP.md` ist die kanonische Anleitung
   - Raspberry Pi 4 Zielimage: `Ubuntu Server 22.04.5 LTS ARM64`
   - Surface-Zielimage: `Ubuntu Desktop 24.04.4 LTS`
   - der `7.7G`-Stick `/dev/sdd` ist jetzt fertig als dedizierter Ventoy-Install-/Image-Stick
   - der `14.4G`-Stick `/dev/sdc` ist jetzt fertig als exFAT-Favorites-Stick `FRAWO_FAVS`
   - AnyDesk auf dem ZenBook ist inzwischen installiert und aktiv
17. Remote-Zugriff professionell absichern und dokumentieren
   - `REMOTE_ACCESS_STANDARD.md` ist die kanonische Anleitung
   - Tailscale ist der primaere Remote-Pfad
   - AnyDesk ist der GUI-Fallback auf dem ZenBook
18. Raspberry-Pi-Radio-Node in den nutzbaren internen Betriebsstandard ueberfuehren
   - `RASPBERRY_PI_RADIO_NODE_PLAN.md` ist die kanonische Anleitung
   - `RADIO_OPERATIONS_STANDARD.md` ist jetzt der operative Betriebsstandard
   - `make radio-ops-check` ist der schnelle Live-Check fuer Radio, Radio Control und `nowplaying`
   - `radio.hs27.internal` zeigt jetzt intern auf den Pi und liefert die AzuraCast-Login-Seite
   - die erste Station `FraWo - Funk` spielt bereits aus der direkt angeschlossenen USB-Bibliothek
   - naechster Schritt ist die kuratierte Betriebsueberfuehrung von USB-Musik zu `RadioLibrary` / `RadioAssets`
   - direkt danach sollen touchfreundliche Surface-Monitor-/Control-Views auf dieser stabilen Basis entstehen
19. Medienserver-V1 auf der Toolbox als echten Haushalts-Mehrwert bereitstellen
   - `MEDIA_SERVER_PLAN.md` ist die kanonische Anleitung
   - `MEDIA_SERVER_CLIENT_SETUP.md` beschreibt die ersten TV-/Browser-Pfade fuer Thomson und Google TV
   - Jellyfin ist jetzt intern live auf `http://media.hs27.internal`, direkt auf `http://192.168.2.20:8096` und mobil ueber `http://100.99.206.128:8449`
   - `make toolbox-media-check` ist jetzt der schnelle Betriebscheck
   - ein wiederholbarer Bootstrap-Sync vom Pi ist jetzt live:
     - Quelle `wolf@100.64.23.77:/srv/radio-library/music-usb/yourparty.radio/`
     - Ziel `/srv/media-library/music/bootstrap-radio-usb/`
     - Check `make toolbox-media-sync-check`
     - Musikreport `make toolbox-music-library-report`
   - `CT 100 toolbox` wurde fuer diesen Pfad operativ vergroessert:
     - Rootfs effektiv `96G`
     - im Gast aktuell rund `82G` frei
     - Ausloeser war `No space left on device` beim ersten 67G-Bootstrap-Import
   - Jellyfin-Erstkonfiguration ist inzwischen fuer den Musikpfad abgeschlossen:
     - `StartupWizardCompleted=true`
     - mindestens ein lokaler Benutzer ist vorhanden
     - `Music` ist an `/media/music` angebunden
   - neuer Qualitaets-Check fuer den Bootstrap-Bestand:
     - `make toolbox-music-scan-issues`
     - letzter Befund: `84` `ffprobe`-Fehler, `2` verdaechtige Dateien, wenige harmlose Cover-/Bilddateien
     - auffaellige Beispiele:
       - `124 kbpsChris Stussy - Desire (Jentzen Dub).mp4`
       - `.07 Christian Harder vs Si Begg - Popland (Unreleased Si Begg Dub).flac.RlfOrq`
   - neuer Kurations-Helfer:
     - `make toolbox-music-curation-candidates`
     - letzter Befund: die einzige echte Problemdatei wurde bereits quarantainisiert; aktuell `0` neue Quarantaene-Kandidaten und `9` harmlose Sidecars
     - vorgeschlagener Quarantaene-Stamm:
       - `/srv/media-library/quarantine/bootstrap-review`
   - neuer Layout-Check:
     - `make toolbox-music-curated-layout`
     - letzter Befund: Bootstrap-Bestand gefuellt, `favorites`-Starter und `curated`-Starter sind live, `quarantine` enthaelt `1` Datei
   - neuer Auswahl-Workflow:
     - Workspace-Manifeste:
       - `manifests/media/favorites_paths.txt`
       - `manifests/media/curated_paths.txt`
     - Seed-Report:
       - `make toolbox-music-selection-seed-report`
       - letzter Befund: `1075` Kandidaten, Top-Eintraege starten mit `clean/Various Artists`, `clean/Nite Fleit`, `clean/Helena Hauff`
     - Materialisierungs-Sync:
       - `make toolbox-music-selection-sync`
       - letzter Befund: `12` Favorites und `20` Curated-Eintraege erfolgreich materialisiert
   - Bootstrap-Import ist praktisch abgeschlossen:
     - `2120/2119` Dateien Quelle/Ziel
     - `99.7%` nach Groesse
     - Timer aktiv, letzter Lauf sauber abgeschlossen
   - naechster Schritt ist jetzt, den ersten Thomson-/Google-TV-Client sauber anzubinden und den Starter-Stand spaeter gezielt zu verfeinern
   - Jellyfin-Housekeeping:
     - `/srv/jellyfin/config/data/playlists` ist jetzt angelegt
     - die vorherige harmlose Warnung zu `/config/data/playlists` taucht im aktuellen Log-Tail nicht mehr auf
   - das Toolbox-Portal ist jetzt als gruppierte `FRAWO Control`-Frontdoor modernisiert und bietet direkte Wege zu Radio, Radio Control, Media und den mobilen Frontdoors
   - das Portal hat jetzt zusaetzlich einen Live-Status-Snapshot auf `status.json`; `make toolbox-portal-status-check` ist aktuell gruen mit `7/7` gesunden Kernservices
   - der Snapshot enthaelt jetzt auch `media_sync` fuer den laufenden Jellyfin-Bibliotheksimport
   - der neue Musikreport zeigt aktuell vor allem `mp3`, `flac` und `wav` sowie einige restriktive Import-Verzeichnisse, die spaeter fuer saubere Kuration normalisiert werden muessen
20. Remote-Only-Arbeitsfenster fuer Arbeitstage ausser Haus standardisieren
   - `REMOTE_ONLY_WORK_WINDOW.md` ist die kanonische Anleitung
   - `make remote-only-check` ist der schnelle Gate-Check
   - bis physische Schritte moeglich sind, nur dort freigegebene Aufgaben ziehen
21. AdGuard-DNS-Pilot kontrolliert vorbereiten
   - `ADGUARD_PILOT_ROLLOUT_PLAN.md` ist die kanonische Anleitung
   - `make adguard-pilot-check` prueft den read-only Pilotpfad und den LAN-Rollback-Schutz
22. Tailscale-Split-DNS fuer `hs27.internal` kontrolliert vorbereiten
   - `TAILSCALE_SPLIT_DNS_PLAN.md` ist die kanonische Anleitung
   - `make tailscale-split-dns-check` prueft MagicDNS, Client-DNS, AdGuard, die Route-Voraussetzung und jetzt auch den echten `ha.hs27.internal`-Pfad ueber `100.100.100.100`
   - der restricted nameserver fuer `hs27.internal` ist im Tailnet gesetzt; ZenBook-Testpfad ist erfolgreich
23. Lease-Abgleich browser-first standardisieren
   - `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` ist die kanonische Anleitung
   - `make inventory-resolution-check` zeigt die verbleibenden Unknowns und Router-Labels
24. Public Edge als spaeteren professionellen Endzustand sauber vorkonzipieren
   - bevorzugter Marken-/Domainpfad ist jetzt `frawo-tech.de`
   - Zielhostnamen spaeter:
     - `www.frawo-tech.de`
     - `radio.frawo-tech.de`
   - bis dahin bleiben `portal.hs27.internal` und `radio.hs27.internal` die operativen internen Namen
   - interne Naming-Entscheidung: aktive Betriebszone bleibt `hs27.internal`; spaeterer professioneller Zielpfad ist `frawo.home.arpa`
   - `frawo.internal` und `frawo.lan` werden nicht als neue Standardzone eingefuehrt
   - `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` ist die kanonische Anleitung
25. Den Gesamtfortschritt des Masterplans reproduzierbar messbar halten
   - `make plan-progress` ist jetzt der kompakte Fortschritts-Check
   - letzter verifizierter Wert: `masterplan_progress_percent=69`
   - aktuelles Band: `mid_stage`
   - naechste Prioritaet bleibt trotz guter Kernbasis PBS-Storage, portabler Backup-Stick und Inventar-Finalisierung

## Aktive Operator-Aktionen

0. `AKTION VON DIR ERFORDERLICH:` Falls du die klassischen `hs27.internal`-Hostnamen schon vor der Vollmigration direkt auf `wolfstudiopc` im Browser willst, braucht es einen bewussten Windows-Hosts-/DNS-Schritt mit Admin-Token.
   - benoetigte Aktion: nur entscheiden, ob der StudioPC bis zur Vollmigration per Tailscale-Frontdoors arbeiten soll oder ob zusaetzlich lokale Hostnamen per Admin-Override wiederhergestellt werden sollen
   - warum: der aktuelle professionelle Arbeitsweg steht bereits (`Tailscale first`), aber das alte direkte `192.168.2.x`-Namensmodell kollidiert mit der UCG-Uebergangsphase
   - danach uebernehmen Codex/Gemini wieder: Netzpfad umstellen, DNS/hs27.internal anpassen und Erreichbarkeit verifizieren
1. `AKTION VON DIR ERFORDERLICH:` Proxmox-Root-SSH-Key hinterlegen
   - benoetigte Aktion: im Proxmox-UI (Node -> System -> Users -> root -> SSH Keys oder Node -> Shell) den Public Key aus `C:\\Users\\StudioPC\\.ssh\\hs27_ops_ed25519.pub` eintragen
   - warum: aktuell nimmt `root@10.1.0.92` keinen der vorhandenen Keys an, dadurch kann ich die Netzwerkfixes nicht remote ausfuehren
   - danach uebernehmen Codex/Gemini wieder: Netzwerk-Status verifizieren, Alias-IPs wiederherstellen und Tailscale-Frontdoors pruefen
2. `AKTION VON DIR ERFORDERLICH:` spaeter einen ersten Thomson-/Google-TV-Client mit Jellyfin verbinden
   - benoetigte Aktion: auf dem TV die Jellyfin-App installieren und den Server `http://192.168.2.20:8096` eintragen
   - warum: die Musikbibliothek ist bereits an Jellyfin angebunden; der naechste echte Nutzwert ist jetzt der erste Client-Rollout statt weiterer Server-Basisarbeit
   - danach uebernehmen Codex/Gemini wieder: Client-Fit, spaetere Bibliothekserweiterung und Medienkuration
3. `AKTION VON DIR ERFORDERLICH:` den `64GB`-USB-Stick an Proxmox nicht abziehen
   - benoetigte Aktion: den aktuell an Proxmox haengenden Stick eingesteckt lassen
   - warum: der Stick traegt jetzt den aktiven Interim-PBS-Datastore `hs27-interim`
   - danach uebernehmen Codex/Gemini weiter: Proof-Backups gruener machen und spaeter die finale groessere PBS-Zielarchitektur vorbereiten
4. `AKTION VON DIR ERFORDERLICH:` restliche Easy-Box-Geraete autoritativ zuordnen
   - benoetigte Aktion: die verbliebenen Unknown-Clients `.141-.144` sowie zusaetzliche aktuelle Router-Labels wie `Surface_Laptop`, `RE355` und `iPhone-3-Pro` fachlich bestaetigen oder benennen
   - warum: `inventory_unknown_review_count=4` und damit `inventory_finalized=no`
   - danach uebernehmen Codex/Gemini wieder: DHCP-/Reservierungsplan finalisieren und den Gateway-Cutover freigabefaehig machen
5. `AKTION VON DIR ERFORDERLICH:` HAOS-USB-Hardware am Proxmox-Host anstecken, sobald verfuegbar
   - benoetigte Aktion: Zigbee-/Bluetooth-/SkyConnect-Adapter physisch am Proxmox-Host anschliessen
   - warum: aktueller Audit zeigt nur Root-Hubs und kein `/dev/serial/by-id`
   - danach uebernehmen Codex/Gemini wieder: Vendor-/Product-ID-Audit, USB-Passthrough und Reboot-Stabilitaet testen
6. `AKTION VON DIR ERFORDERLICH:` spaeter einmal einen echten Dokumentenlauf ueber Nextcloud testen
   - benoetigte Aktion: eine unkritische Beispiel-PDF oder ein Scan in `Paperless/Eingang` in Nextcloud hochladen und spaeter pruefen, ob die digitale Kopie in `Paperless/Archiv` erscheint
   - warum: der technische Brueckenpfad ist jetzt live, der naechste Mehrwert ist die echte Nutzerakzeptanz mit einem realen Dokument
   - danach uebernehmen Codex/Gemini wieder: Feinjustierung, Surface-Shortcuts und spaetere Kuration
7. `AKTION VON DIR ERFORDERLICH:` Handy einmal echt off-LAN ueber Tailscale pruefen
   - benoetigte Aktion: WLAN am Handy aus, Tailscale verbunden lassen und `http://portal.hs27.internal`, `http://ha.hs27.internal` sowie `http://odoo.hs27.internal/web/login` testen
   - warum: Pixel 8 (Wolf) ist als erste mobile Test-Einheit definiert; verifiziert den `hs27.internal` Pfad ueber Tailscale.
   - danach uebernehmen Codex/Gemini wieder: mobilen Betriebsstandard finalisieren und den Frontdoor fuer Endgeraete sauber freigeben
8. `AKTION VON DIR ERFORDERLICH:` iPhone Onboarding fuer Franz
   - benoetigte Aktion: Tailscale auf dem iPhone installieren, `DOCS/MOBILE_HTTPS_TRUST.md` (iOS) anwenden und dann `DOCS/FRANZ_IPHONE_ONBOARDING.md` abarbeiten.
   - warum: Franz braucht mobilen Zugriff fuer den MVP-Abschluss; HTTPS-Vertrauen ist fuer iOS-Apps zwingend.
   - danach uebernehmen Codex/Gemini wieder: Bestaetigung der mobilen Erreichbarkeit.
9. `AKTION VON DIR ERFORDERLICH:` Login-Credentials fuer MVP Browser Acceptance
   - benoetigte Aktion: Bereitstellung der Master-Passwoerter (Vaultwarden fuer Franz und Wolf) oder Uebernahme des Login-Schritts.
   - warum: Laut BUSINESS_MVP_PROMPT.md und ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md liegen keine Klartextpasswoerter vor, der Login zur Verifikation muss aber zwingend sichtbar im Browser evaluiert werden.
   - danach uebernehmen Codex/Gemini wieder: Pruefung der restlichen sichtbaren Realitaeten im Subagenten.
10. `AKTION VON DIR ERFORDERLICH:` fehlenden 2FA-Pfad fuer den MVP-Abschluss wiederherstellen
   - benoetigte Aktion: den verlorenen Smartphone-/2FA-Pfad fuer den Operator wiederherstellen oder einen bewusst freigegebenen Ersatzpfad festlegen und danach die sichtbare Franz-Geraeteabnahme auf Surface Laptop und iPhone durchziehen
   - warum: `device_rollout_verified` bleibt im aktuellen MVP-Gate offen; ohne 2FA-/Login-Pfad kann die sichtbare Endgeraeteabnahme nicht sauber geschlossen werden
   - danach uebernehmen Codex/Gemini wieder: reale Franz-Entry-Paths pruefen, Evidenz einsammeln und den Gate-Status aktualisieren
11. `AKTION VON DIR ERFORDERLICH:` Vaultwarden-Recovery-Material in zwei getrennten Offline-Kopien bestaetigen
   - benoetigte Aktion: zwei physisch getrennte Offline-Kopien des Vaultwarden-Recovery-Materials erzeugen oder frisch bestaetigen und die sichtbare Existenz nachweisen
   - warum: `vaultwarden_recovery_material_verified` ist im aktuellen MVP-Gate noch offen und bleibt rein operator-/physisch gebunden
   - danach uebernehmen Codex/Gemini wieder: Manual-Check im Gate auf Gruen ziehen und den Handoff aktualisieren
12. Hinweis: Mobiler HTTPS-Vertrauensstandard (2026)
   - die interne CA (`frawo-ca.crt`) wird ueber `http://portal.hs27.internal/frawo-ca.crt` bereitgestellt.
   - die Installation ist fuer Bitwarden, Nextcloud und Odoo auf Android/iOS zwingend erforderlich, um untrusted-SSL-Fehler zu vermeiden.
   - Leitfaden: `DOCS/MOBILE_HTTPS_TRUST.md`.

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

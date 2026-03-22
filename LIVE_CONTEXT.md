# Live Context

## Workspace

- Name: `Homeserver 2027 Ops Workspace`
- Alias: `/home/wolf/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Desktop shortcut: `/home/wolf/Desktop/Homeserver 2027 Workspace`
- Generated at: `2026-03-22 00:10:30 CET`
- Git branch: `main`
- Pending git changes: `88`

## Shared Read Order

1. `LIVE_CONTEXT.md`
2. `MASTERPLAN.md`
3. `MORNING_ROUTINE.md`
4. `SECURITY_BASELINE.md`
5. `SESSION_CLOSEOUT.md`
6. `GEMINI.md`
7. `MEMORY.md`
8. `NETWORK_INVENTORY.md`
9. `VM_AUDIT.md`
10. `BACKUP_RESTORE_PROOF.md`
11. `CAPACITY_REVIEW.md`
12. `RIGHTSIZING_MAINTENANCE_PLAN.md`
13. `SURFACE_GO_FRONTEND_SETUP_PLAN.md`
14. `MEDIA_AND_REMOTE_PREP.md`
15. `REMOTE_ACCESS_STANDARD.md`
16. `REMOTE_ONLY_WORK_WINDOW.md`
17. `ADGUARD_PILOT_ROLLOUT_PLAN.md`
18. `TAILSCALE_SPLIT_DNS_PLAN.md`
19. `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md`
20. `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
21. `RASPBERRY_PI_RADIO_NODE_PLAN.md`
22. `AZURACAST_FIRST_STATION_BASELINE.md`
23. `RADIO_OPERATIONS_STANDARD.md`
24. `MEDIA_SERVER_PLAN.md`
25. `MEDIA_SERVER_CLIENT_SETUP.md`
26. `OPERATOR_TODO_QUEUE.md`
27. `PBS_VM_240_SETUP_PLAN.md`
28. `HAOS_VM_210_SETUP_PLAN.md`
29. `PORTABLE_BACKUP_USB_PLAN.md`

## Canonical Sources

- `README.md` updated: `2026-03-21 13:13:27`
- `MASTERPLAN.md` updated: `2026-03-21 13:15:05`
- `MORNING_ROUTINE.md` updated: `2026-03-19 10:15:51`
- `SECURITY_BASELINE.md` updated: `2026-03-19 21:56:58`
- `SESSION_CLOSEOUT.md` updated: `2026-03-21 12:38:14`
- `EVENING_ROUTINE.md` updated: `2026-03-19 00:01:26`
- `GEMINI.md` updated: `2026-03-21 13:15:05`
- `MEMORY.md` updated: `2026-03-22 00:10:30`
- `NETWORK_INVENTORY.md` updated: `2026-03-21 13:59:17`
- `VM_AUDIT.md` updated: `2026-03-18 20:48:38`
- `BACKUP_RESTORE_PROOF.md` updated: `2026-03-21 12:37:41`
- `CAPACITY_REVIEW.md` updated: `2026-03-20 20:23:49`
- `RIGHTSIZING_MAINTENANCE_PLAN.md` updated: `2026-03-18 22:21:31`
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md` updated: `2026-03-21 09:50:34`
- `MEDIA_AND_REMOTE_PREP.md` updated: `2026-03-20 09:53:52`
- `REMOTE_ACCESS_STANDARD.md` updated: `2026-03-19 18:28:25`
- `REMOTE_ONLY_WORK_WINDOW.md` updated: `2026-03-19 21:56:58`
- `ADGUARD_PILOT_ROLLOUT_PLAN.md` updated: `2026-03-19 13:38:02`
- `TAILSCALE_SPLIT_DNS_PLAN.md` updated: `2026-03-19 22:23:15`
- `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` updated: `2026-03-19 18:20:23`
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` updated: `2026-03-19 22:23:15`
- `RASPBERRY_PI_RADIO_NODE_PLAN.md` updated: `2026-03-20 09:54:59`
- `AZURACAST_FIRST_STATION_BASELINE.md` updated: `2026-03-19 23:20:05`
- `RADIO_OPERATIONS_STANDARD.md` updated: `2026-03-20 16:57:48`
- `MEDIA_SERVER_PLAN.md` updated: `2026-03-21 01:26:51`
- `MEDIA_SERVER_CLIENT_SETUP.md` updated: `2026-03-21 00:52:28`
- `OPERATOR_TODO_QUEUE.md` updated: `2026-03-21 13:22:30`
- `PBS_VM_240_SETUP_PLAN.md` updated: `2026-03-21 14:31:16`
- `HAOS_VM_210_SETUP_PLAN.md` updated: `2026-03-21 13:13:27`
- `PORTABLE_BACKUP_USB_PLAN.md` updated: `2026-03-21 10:01:39`
- `ansible/inventory/hosts.yml` updated: `2026-03-21 10:04:48`
- `ansible/inventory/group_vars/all/vault.yml` updated: `2026-03-21 14:43:32`

## Current Estate Snapshot

- Managed hosts in Ansible inventory: `27`
- Router baseline: `192.168.2.1` Vodafone Easy Box
- Planned future gateway: `UniFi Cloud Gateway Ultra (UCG-Ultra)`, not yet active
- Core business nodes: `192.168.2.20` toolbox, `192.168.2.21` nextcloud, `192.168.2.22` odoo, `192.168.2.23` paperless, `192.168.2.24` haos
- Toolbox network base: Caddy on `192.168.2.20:80`, AdGuard Home on `192.168.2.20:53` and localhost-only admin on `127.0.0.1:3000`, `hs27.internal` rewrites verified in opt-in mode
- Toolbox mobile Tailscale frontdoor: `100.99.206.128:8443` HA, `:8444` Odoo, `:8445` Nextcloud, `:8446` Paperless, `:8447` Portal, `:8448` Radio, `:8449` Media
- Toolbox Tailscale state: `/dev/net/tun` mapped, `tailscaled` active, backend `Running`, subnet route `192.168.2.0/24` is active in the Tailnet and Split-DNS for `hs27.internal` is operational
- VM 200, VM 210, VM 220 and VM 230: QEMU Guest Agent verified from Proxmox during latest audit
- Business stacks are running from `/opt/homeserver2027/stacks` under systemd-managed local IaC
- Home Assistant OS is stable on `192.168.2.24:8123` and `ha.hs27.internal` now returns `HTTP 200` through Caddy
- Local Proxmox backup proof completed on `2026-03-18` for `VM 200`, `VM 220` and `VM 230`; daily local backup coverage now includes `VM 210`
- PBS runner path is live, the official installer ISO is staged, interim USB-backed storage is mounted on Proxmox at `/srv/pbs-datastore`, `VM 240 pbs` is installed on `192.168.2.25`, datastore `hs27-interim` is active, Proxmox storage `pbs-interim` is active, and the first green proof-backup plus restore drill are already verified for `VM 220`
- Capacity review says the host is memory-overcommitted on paper; immediate right-sizing candidates are `VM 200` and `VM 220`, while `VM 210` should not be reduced
- Right-sizing stage gate is green; the actual memory reduction remains a maintenance-window change and is not yet applied
- Shared frontend node on `192.168.2.154` is now rebuilt as `surface-go-frontend`; SSH, Tailnet admin on `100.106.67.127`, root sleep hardening, and the robust local portal path `http://127.0.0.1:17827` are live via the visible `FRAWO Control` launcher
- Local media prep is staged on the ZenBook: `/dev/mmcblk0` for Raspberry Pi, `/dev/sdd` is now the ready blue Ventoy install-/image-stick, and `/dev/sdc1` is the ready exFAT Favorites-stick `FRAWO_FAVS`
- Portable backup USB path has been repurposed: the dedicated `64GB` stick is attached directly to Proxmox as `HS27_PORTABLEBK`, mounted on `/srv/portable-backup-usb`, bind-mounted to `/srv/pbs-datastore`, and now backs the interim PBS-v1 path instead of continuing as a portable archive shuttle
- Raspberry-Pi radio node is live: `radio-node` on `192.168.2.155` / `100.64.23.77`, AzuraCast containers are running, `radio.hs27.internal` currently returns `HTTP 302` to `/login`, and the status API is reachable
- Raspberry-Pi radio node uses the conservative pi4_2gb_single_station_low_resource profile with about 1.8 GiB RAM, 2 GiB swap, about 21 GiB free rootfs, COMPOSE_HTTP_TIMEOUT=900, PHP_FPM_MAX_CHILDREN=2, NOW_PLAYING_DELAY_TIME=15, NOW_PLAYING_MAX_CONCURRENT_PROCESSES=1, and ENABLE_WEB_UPDATER=false
- Media server V1 is now live on `CT 100 toolbox`: Jellyfin is reachable internally on `http://media.hs27.internal`, directly on `http://192.168.2.20:8096`, and through the mobile Tailscale frontdoor on `:8449`; the startup wizard is complete and the music library is attached while the bootstrap import continues
- ZenBook remote posture is now stronger: Tailscale joined on `100.76.249.126` and AnyDesk is installed and active as a GUI fallback
- Remote-only work windows are now codified through `REMOTE_ONLY_WORK_WINDOW.md` and `make remote-only-check`

## Active Work Queue

1. `NETWORK_INVENTORY.md` mit Easy-Box-Leases und DHCP-Reservierungen final abgleichen
   - bereits teilaufgeloest: `Wolf_Pixel`, `SonRoku`, Growbox-Shellys
   - Router-Label-Mapping ist inzwischen weitgehend sauber; `fireTV`, `Franz_iphone`, `udhcpc1.21.1` und `udhcp 1.24.1` sind bereits auf aktive IPs gemappt
   - offen bleiben vor allem die privaten MAC-Clients `.141-.144` sowie kleinere Alias-/Raumzuordnungen aus dem Router-Ueberblick
   - neuer Fingerprint-Stand fuer `.141-.144`: alle vier antworten auf Ping, aber halten `53/80/443/5353/8008/8069/8080` geschlossen und liefern kein HTTP; aktuell also eher stille Privat-Clients als Admin-/IoT-Endpunkte
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
   - Runner und Stage-Gate-Pfad fuer `VM 240` sind nicht nur vorbereitet, sondern live umgesetzt
   - `VM 240 pbs` laeuft jetzt mit `3072 MB` RAM, `32G` Systemdisk auf `local-lvm` und `40G` USB-Data-Disk auf `pbs-usb`
   - Datastore `hs27-interim` ist im Gast aktiv und Proxmox-Storage `pbs-interim` ist angebunden
   - taeglicher PBS-Job `hs27-pbs-interim-daily` ist angelegt
   - platzbewusste Interim-Retention ist aktiv: `02:40,14:40` mit `keep-daily=2`, `keep-weekly=1`, `keep-monthly=1`
   - erster gruener Proof-Backup-Lauf ist jetzt erbracht: `VM 220` erfolgreich nach `pbs-interim`
   - erster gruener Restore-Drill ist jetzt ebenfalls erbracht: `VM 220` -> Test-VM `920` -> `HTTP 200` auf Odoo-Login
   - zweiter automatisierter Restore-Drill (`VM 220` -> `920`) war ebenfalls erfolgreich und beweist die Reproduzierbarkeit
   - der aktuelle Restblock ist jetzt primär größeres PBS-Storage für den späteren Dauerbetrieb
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
   - der neue Audit-Guardrail ist aktiv: der sichtbare externe USB-Pfad ist derzeit nur der PBS-Backup-Stick und zaehlt ausdruecklich nicht als HAOS-Dongle
6. Hardware-Audit fuer Zigbee- und Bluetooth-Dongles:
   - aktueller Auditlauf ist jetzt praeziser: Root-Hubs plus ein USB-Massenspeicher (`USB Disk 3.0`) sind sichtbar, aber keine seriellen Funkadapter
   - `make haos-usb-audit` ist jetzt der kanonische Schnellcheck
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
   - SSH-Key-Zugang, Tailnet-Admin-Pfad, Kiosk-User `frontend`, lokales Portal und GDM-Autologin sind live
   - Root-Sleep-Haertung ist abgeschlossen; die Sleep-Targets sind maskiert
   - das Surface-Frontend nutzt jetzt einen robusteren lokalen Pfad:
     - lokaler Portalservice auf `127.0.0.1:17827`
     - sichtbarer Launcher `FRAWO Control`
     - `epiphany-browser` ueber lokalen Wrapper als aktuelle Browser-Instanz
   - das Surface-Portal soll jetzt `Radio` und `Radio Control` nativ fuer AzuraCast anbieten
   - die lokale Surface-Portal-Vorlage ist jetzt auch fuer den gemeinsamen Live-Status-Snapshot aus `portal.hs27.internal/status.json` vorbereitet
   - der technische Kern ist gruen; offener Restblock ist jetzt lokaler Browser-/Touch-Tastatur-Polish
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
24. Den Gesamtfortschritt des Masterplans reproduzierbar messbar halten
   - `make plan-progress` ist jetzt der kompakte Fortschritts-Check
   - letzter verifizierter Wert: `masterplan_progress_percent=69`
   - aktuelles Band: `mid_stage`
   - naechste Prioritaet bleibt trotz guter Kernbasis PBS-Storage, portabler Backup-Stick und Inventar-Finalisierung

## Operator Actions Needed

1. `AKTION VON DIR ERFORDERLICH:` spaeter einen ersten Thomson-/Google-TV-Client mit Jellyfin verbinden
   - benoetigte Aktion: auf dem TV die Jellyfin-App installieren und den Server `http://192.168.2.20:8096` eintragen
   - warum: die Musikbibliothek ist bereits an Jellyfin angebunden; der naechste echte Nutzwert ist jetzt der erste Client-Rollout statt weiterer Server-Basisarbeit
   - danach uebernehmen Codex/Gemini wieder: Client-Fit, spaetere Bibliothekserweiterung und Medienkuration
2. `AKTION VON DIR ERFORDERLICH:` den `64GB`-USB-Stick an Proxmox nicht abziehen
   - benoetigte Aktion: den aktuell an Proxmox haengenden Stick eingesteckt lassen
   - warum: der Stick traegt jetzt den aktiven Interim-PBS-Datastore `hs27-interim`
   - danach uebernehmen Codex/Gemini weiter: Proof-Backups gruener machen und spaeter die finale groessere PBS-Zielarchitektur vorbereiten
3. `AKTION VON DIR ERFORDERLICH:` restliche Easy-Box-Geraete autoritativ zuordnen
   - benoetigte Aktion: die verbliebenen Unknown-Clients `.141-.144` sowie zusaetzliche aktuelle Router-Labels wie `Surface_Laptop`, `RE355` und `iPhone-3-Pro` fachlich bestaetigen oder benennen
   - warum: `inventory_unknown_review_count=4` und damit `inventory_finalized=no`
   - danach uebernehmen Codex/Gemini wieder: DHCP-/Reservierungsplan finalisieren und den Gateway-Cutover freigabefaehig machen
4. `AKTION VON DIR ERFORDERLICH:` HAOS-USB-Hardware am Proxmox-Host anstecken, sobald verfuegbar
   - benoetigte Aktion: Zigbee-/Bluetooth-/SkyConnect-Adapter physisch am Proxmox-Host anschliessen
   - warum: aktueller Audit zeigt nur Root-Hubs und kein `/dev/serial/by-id`
   - danach uebernehmen Codex/Gemini wieder: Vendor-/Product-ID-Audit, USB-Passthrough und Reboot-Stabilitaet testen
6. `AKTION VON DIR ERFORDERLICH:` Handy einmal echt off-LAN ueber Tailscale pruefen
   - benoetigte Aktion: WLAN am Handy aus, Tailscale verbunden lassen und `http://portal.hs27.internal`, `http://ha.hs27.internal` sowie `http://odoo.hs27.internal/web/login` testen
   - warum: Route und restricted nameserver sind jetzt live, aber der echte mobile Akzeptanztest fuer den `hs27.internal`-Pfad ist noch nicht bestaetigt
   - danach uebernehmen Codex/Gemini wieder: mobilen Betriebsstandard finalisieren und den Frontdoor fuer Endgeraete sauber freigeben

## Tonight's Review Findings

1. Medium: Router lease table has not yet been reconciled with the inventory.
   - Manual router review already resolved `Wolf_Pixel`, `SonRoku` and that the Shelly devices belong to the growbox.
   - `Surface_Laptop` is now effectively resolved to `yourparty-Surface-Go.local` on `192.168.2.154`, but the device still needs a clean rebuild into the managed frontend standard.
   - Unknown devices `.141-.144`, the exact `.107`/`.114` Shelly alias split, and labels such as `fireTV` and `Franz_iphone` still need authoritative identification from the Easy Box.
   - Router credentials are now stored and `user_lang.json` is reachable through the new browser-context probe, but authenticated login and lease extraction are still not reproduced.
   - The Surface Go is now rebuilt as `surface-go-frontend`, reachable by SSH and Tailscale, and technically manageable; the remaining work is touch/browser UX polish.
2. Medium: Backup and restore are now locally proven, but the durable PBS operating model is still not live.
   - The current stopgap is now much stronger: successful local proof, successful PBS proof-backup and successful PBS restore drill.
   - The PBS guest is live on `192.168.2.25`, the datastore `hs27-interim` is active, and scheduled jobs with retention are already in place.
   - We still need larger dedicated backup storage and recurring restore drills before calling the platform fully hardened.
   - Local retention remains a useful secondary safety net while the PBS-v1 path is stabilized.
3. Low: One older snapshot still exists on `VM 100`.
   - This was left untouched intentionally because it is outside the business-VM change scope and may still be part of the Toolbox/Tailscale workstream.
4. Low: `CT 100` network foundation is now live and Tailscale is joined.
   - Internal Caddy and AdGuard opt-in DNS are running and verified.
   - `portal.hs27.internal` is now live as the shared internal frontdoor.
   - The next network step is subnet-route approval plus a controlled pilot-client rollout for AdGuard.
5. Low: `HAOS` ist jetzt intern integriert, nicht nur deployed.
   - `VM 210` ist stabil auf `192.168.2.24`.
   - `ha.hs27.internal` liefert `200` ueber den Toolbox-Frontdoor.
   - USB passthrough haengt weiterhin nur von physisch vorhandenen Adaptern ab.

## Best-Practice Actions

1. Freeze a canonical device register now and update it only from scan plus router-lease reconciliation.
2. Reserve or document fixed addresses for all infrastructure and business nodes on the Easy Box.
3. Keep unmanaged household and IoT devices explicitly separated in inventory even before VLAN-capable hardware exists.
4. Treat `unknown-review` devices as temporary exceptions and close them out before exposing any services over Tailscale.
5. Only promote devices into `trusted-clients` after owner and management posture are known.
6. Treat the UCG-Ultra as a dedicated later-phase network cutover, not as a side-task during current LXC/VM rollout work.
7. Keep router-only names that are not yet tied to a live IP explicit in the notes instead of guessing their mapping.
8. Introduce AdGuard Home first as an opt-in internal DNS service, not as immediate default DNS for the whole LAN.
9. Treat public exposure as its own hardening phase with edge separation, not as an extension of the current flat-LAN toolbox phase.
10. Treat shared frontend devices as kiosk-first endpoints, not as ad hoc desktop-server hybrids.

## Collaboration Contract

- Update canonical source files instead of creating duplicate notes.
- Gemini and Codex should use the same shared files listed above.
- The user systemd path unit should refresh this file automatically after source-file changes.
- Manual fallback: `make refresh-context`

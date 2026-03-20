# Live Context

## Workspace

- Name: `Homeserver 2027 Ops Workspace`
- Alias: `/home/wolf/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Desktop shortcut: `/home/wolf/Desktop/Homeserver 2027 Workspace`
- Generated at: `2026-03-20 18:18:41 CET`
- Git branch: `main`
- Pending git changes: `40`

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
26. `PBS_VM_240_SETUP_PLAN.md`
27. `HAOS_VM_210_SETUP_PLAN.md`

## Canonical Sources

- `README.md` updated: `2026-03-19 22:33:06`
- `MASTERPLAN.md` updated: `2026-03-20 18:18:26`
- `MORNING_ROUTINE.md` updated: `2026-03-19 10:15:51`
- `SECURITY_BASELINE.md` updated: `2026-03-19 21:56:58`
- `SESSION_CLOSEOUT.md` updated: `2026-03-19 06:20:31`
- `EVENING_ROUTINE.md` updated: `2026-03-19 00:01:26`
- `GEMINI.md` updated: `2026-03-20 18:18:26`
- `MEMORY.md` updated: `2026-03-20 18:18:26`
- `NETWORK_INVENTORY.md` updated: `2026-03-19 22:31:21`
- `VM_AUDIT.md` updated: `2026-03-18 20:48:38`
- `BACKUP_RESTORE_PROOF.md` updated: `2026-03-18 20:48:54`
- `CAPACITY_REVIEW.md` updated: `2026-03-18 21:24:13`
- `RIGHTSIZING_MAINTENANCE_PLAN.md` updated: `2026-03-18 22:21:31`
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md` updated: `2026-03-20 18:18:26`
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
- `MEDIA_SERVER_PLAN.md` updated: `2026-03-20 18:18:33`
- `MEDIA_SERVER_CLIENT_SETUP.md` updated: `2026-03-20 18:17:08`
- `PBS_VM_240_SETUP_PLAN.md` updated: `2026-03-18 07:40:25`
- `HAOS_VM_210_SETUP_PLAN.md` updated: `2026-03-18 20:42:44`
- `ansible/inventory/hosts.yml` updated: `2026-03-20 16:28:22`
- `ansible/inventory/group_vars/all/vault.yml` updated: `2026-03-18 00:47:00`

## Current Estate Snapshot

- Managed hosts in Ansible inventory: `26`
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
- PBS runner path is prepared, the official installer ISO is staged, and the PBS stage gate remains blocked until separate backup storage is mounted on Proxmox
- Capacity review says the host is memory-overcommitted on paper; immediate right-sizing candidates are `VM 200` and `VM 220`, while `VM 210` should not be reduced
- Right-sizing stage gate is green; the actual memory reduction remains a maintenance-window change and is not yet applied
- Shared frontend node on `192.168.2.154` is now rebuilt as `surface-go-frontend`; SSH, kiosk baseline, local portal and hardening are applied, but the node is currently offline/asleep and still needs Tailnet verification plus final post-install acceptance
- Local media prep is staged on the ZenBook: `/dev/mmcblk0` for Raspberry Pi, `/dev/sdd` is now the ready blue Ventoy install-/image-stick, and `/dev/sdc1` is the ready exFAT Favorites-stick `FRAWO_FAVS`
- Raspberry-Pi radio node is live: `radio-node` on `192.168.2.155` / `100.64.23.77`, AzuraCast containers are running, `radio.hs27.internal` currently returns `HTTP 302` to `/login`, and the status API is reachable
- Raspberry-Pi radio node uses the conservative pi4_2gb_single_station_low_resource profile with about 1.8 GiB RAM, 2 GiB swap, about 21 GiB free rootfs, COMPOSE_HTTP_TIMEOUT=900, PHP_FPM_MAX_CHILDREN=2, NOW_PLAYING_DELAY_TIME=15, NOW_PLAYING_MAX_CONCURRENT_PROCESSES=1, and ENABLE_WEB_UPDATER=false
- Media server V1 is now live on `CT 100 toolbox`: Jellyfin is reachable internally on `http://media.hs27.internal`, directly on `http://192.168.2.20:8096`, and through the mobile Tailscale frontdoor on `:8449`; the remaining step is the UI-based first admin and library attachment
- ZenBook remote posture is now stronger: Tailscale joined on `100.76.249.126` and AnyDesk is installed and active as a GUI fallback
- Remote-only work windows are now codified through `REMOTE_ONLY_WORK_WINDOW.md` and `make remote-only-check`

## Active Work Queue

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

## Operator Actions Needed

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

## Tonight's Review Findings

1. Medium: Router lease table has not yet been reconciled with the inventory.
   - Manual router review already resolved `Wolf_Pixel`, `SonRoku` and that the Shelly devices belong to the growbox.
   - `Surface_Laptop` is now effectively resolved to `yourparty-Surface-Go.local` on `192.168.2.154`, but the device still needs a clean rebuild into the managed frontend standard.
   - Unknown devices `.141-.144`, the exact `.107`/`.114` Shelly alias split, and labels such as `fireTV` and `Franz_iphone` still need authoritative identification from the Easy Box.
   - Router credentials are now stored and `user_lang.json` is reachable through the new browser-context probe, but authenticated login and lease extraction are still not reproduced.
   - The Surface Go currently exposes `HTTP/80` with the Ubuntu `nginx` default page and no `SSH`, so it is identified but not yet remotely manageable.
2. Medium: Backup and restore are now locally proven, but the durable PBS operating model is still not live.
   - The current stopgap is now stronger than before: successful restore proof plus a live daily local timer on Proxmox `local`.
   - The PBS runner and stage-gate path are now prepared, and the official installer ISO is staged on Proxmox.
   - We still need separate backup storage, scheduled PBS jobs and recurring restore drills before calling the platform fully hardened.
   - Local retention remains latest `2` archives per business VM until PBS takes over.
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

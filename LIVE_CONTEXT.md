# LIVE CONTEXT

## Infrastructure Recovery (2026-04-14)
- **Status**: SUCCESSFUL. Anker host stabilized.
- **Forensics**: 2TB NTFS Drive `sda2` is physically failing. Migration stopped.
- **Toolbox**: REBUILT on `local` storage (to bypass LVM threshold). 
- **Control Portal**: LIVE at `10.1.0.20`.
- **Routing**: Caddy L7 proxying restored.

## Workspace-Status

- Name: `FraWo GbR Ops Workspace`
- Repository-Status: **MASTER SSOT ACTIVE** (2026-04-14)
- Canonical Upstream: `https://github.com/Wolfeetech/FraWo`
- Sync Tooling: `make repo-sync`, `make repo-status`

## Shared Read Order

1. `INTRODUCTION_PROMPT.md`
2. `BUSINESS_MVP_PROMPT.md` oder `WEBSITE_RELEASE_PROMPT.md` oder `FULL_CERTIFICATION_PROMPT.md`
3. `AI_BOOTSTRAP_CONTEXT.md`
4. `LIVE_CONTEXT.md`
5. `MASTERPLAN.md`
6. `OPERATIONS/OPERATOR_ROUTINES.md`
7. `SECURITY_BASELINE.md`
8. `SESSION_CLOSEOUT.md`
9. `GEMINI.md`
10. `MEMORY.md`
11. `NETWORK_INVENTORY.md`
12. `VM_AUDIT.md`
13. `BACKUP_RESTORE_PROOF.md`
14. `CAPACITY_REVIEW.md`
15. `RIGHTSIZING_MAINTENANCE_PLAN.md`
16. `SURFACE_GO_FRONTEND_SETUP_PLAN.md`
17. `MEDIA_AND_REMOTE_PREP.md`
18. `REMOTE_ACCESS_STANDARD.md`
19. `REMOTE_ONLY_WORK_WINDOW.md`
20. `ADGUARD_PILOT_ROLLOUT_PLAN.md`
21. `TAILSCALE_SPLIT_DNS_PLAN.md`
22. `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md`
23. `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
24. `RASPBERRY_PI_RADIO_NODE_PLAN.md`
25. `RPI_RESOURCE_ALLOCATION_PLAN.md`
26. `AZURACAST_FIRST_STATION_BASELINE.md`
27. `RADIO_OPERATIONS_STANDARD.md`
28. `MEDIA_SERVER_PLAN.md`
29. `MEDIA_SERVER_CLIENT_SETUP.md`
30. `OPERATOR_TODO_QUEUE.md`
31. `PBS_VM_240_SETUP_PLAN.md`
32. `HAOS_VM_210_SETUP_PLAN.md`
33. `PORTABLE_BACKUP_USB_PLAN.md`

## Canonical Sources

- `INTRODUCTION_PROMPT.md` updated: `2026-04-09 19:28:37`
- `BUSINESS_MVP_PROMPT.md` updated: `2026-04-09 19:28:37`
- `WEBSITE_RELEASE_PROMPT.md` updated: `2026-04-09 19:28:39`
- `FULL_CERTIFICATION_PROMPT.md` updated: `2026-04-09 19:28:37`
- `AI_BOOTSTRAP_CONTEXT.md` updated: `2026-04-09 19:43:27`
- `README.md` updated: `2026-04-09 19:28:38`
- `MASTERPLAN.md` updated: `2026-04-05 01:33:08`
- `OPERATIONS/OPERATOR_ROUTINES.md` updated: `2026-03-26 23:23:08`
- `SECURITY_BASELINE.md` updated: `2026-03-24 11:50:08`
- `SESSION_CLOSEOUT.md` updated: `2026-04-09 19:28:38`
- `GEMINI.md` updated: `2026-04-09 20:11:43`
- `MEMORY.md` updated: `2026-04-09 20:28:34`
- `NETWORK_INVENTORY.md` updated: `2026-04-07 21:16:03`
- `VM_AUDIT.md` updated: `2026-04-09 20:28:24`
- `BACKUP_RESTORE_PROOF.md` updated: `2026-04-09 19:28:37`
- `CAPACITY_REVIEW.md` updated: `2026-04-09 19:28:37`
- `RIGHTSIZING_MAINTENANCE_PLAN.md` updated: `2026-04-09 19:28:38`
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md` updated: `2026-04-09 19:28:39`
- `MEDIA_AND_REMOTE_PREP.md` updated: `2026-04-09 19:28:38`
- `REMOTE_ACCESS_STANDARD.md` updated: `2026-04-03 21:51:18`
- `REMOTE_ONLY_WORK_WINDOW.md` updated: `2026-04-09 19:28:38`
- `ADGUARD_PILOT_ROLLOUT_PLAN.md` updated: `2026-04-05 02:05:43`
- `TAILSCALE_SPLIT_DNS_PLAN.md` updated: `2026-04-09 19:28:39`
- `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` updated: `2026-04-09 19:28:38`
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` updated: `2026-04-09 19:28:38`
- `RASPBERRY_PI_RADIO_NODE_PLAN.md` updated: `2026-04-09 19:28:38`
- `RPI_RESOURCE_ALLOCATION_PLAN.md` updated: `2026-04-09 19:28:38`
- `AZURACAST_FIRST_STATION_BASELINE.md` updated: `2026-04-09 19:28:37`
- `RADIO_OPERATIONS_STANDARD.md` updated: `2026-04-09 19:28:38`
- `MEDIA_SERVER_PLAN.md` updated: `2026-04-09 19:28:38`
- `MEDIA_SERVER_CLIENT_SETUP.md` updated: `2026-04-09 19:28:38`
- `OPERATOR_TODO_QUEUE.md` updated: `2026-04-09 19:28:38`
- `PBS_VM_240_SETUP_PLAN.md` updated: `2026-03-27 08:57:47`
- `HAOS_VM_210_SETUP_PLAN.md` updated: `2026-04-09 19:28:37`
- `PORTABLE_BACKUP_USB_PLAN.md` updated: `2026-04-09 19:28:38`
- `ansible/inventory/hosts.yml` updated: `2026-04-09 19:28:40`
- `ansible/inventory/group_vars/all/vault.yml` updated: `2026-04-09 19:28:39`

## Current Estate Snapshot

- Managed hosts in Ansible inventory: `30`
- **Branding Transition (2026-04-14)**: Das gesamte Estate wurde auf den neuen Namen **FraWo GbR** umgestellt. Sämtliche SSOT-Dokumente spiegeln nun die neue Marke wider.
- **Anker Blackout & Recovery (2026-04-14)**: Kritischer Ausfall des Master-Nodes durch fehlerhaften USB-Stick "Wolf.EE". Anker ist wieder online, Kern-VMs (200-230) intakt. Die "toolbox" (LXC 100) hat ihre virtuelle Festplatte auf `local` verloren und lässt sich nicht starten. Odoo wurde mit einem Emergency-NAT bypass direkt zugänglich gemacht.
- **Public Edge Launch**: Ein Cloudflare-Tunnel wurde als primärer öffentlicher Einstiegspunkt etabliert: [https://protocol-panel-cove-little.trycloudflare.com](https://protocol-panel-cove-little.trycloudflare.com).
- **Toolbox Portal Update**: Das interne Dashboard zeigt nun dynamisch den Status der Kerndienste und den öffentlichen Link an.
- **HAOS Recovery Success**: Der `400 Bad Request` Fehler in Home Assistant wurde durch Anpassung der `trusted_proxies` behoben.
- **Stockenweiler Recovery**: Der Fernzugriff via Tailscale SSH wurde erfolgreich autorisiert und verifiziert.
- **Subnet Focus**: Das primäre Produktionsnetz wurde auf das VLAN 101 (`10.1.0.0/24`) des UCG-Ultra migriert.
- **Repository Reorganization (2026-04-12)**: Root clutter from past remediation phases has been moved into structured subdirectories (`scripts/remediations`, `scripts/archive`, `scripts/research`, `scripts/business`, `scripts/tools`). The root directory now only contains core infrastructure files, shortcut commands, and verified administrative documents.
- **StudioPC Workstation Katarzis:** Der Rechner wurde in eine dedizierte Antigravity-Workstation transformiert.
    - **Laufwerks-Mapping (Persistent):** `P:\` (PROJEKTE), `S:\` (SAMPLES), `L:\` (LIBRARY_ASSETS) auf `C:\WORKSPACE`.
    - **Bereinigung:** Alle Gaming-Altlasten (Riot, Steam-Residuen, Vanguard) wurden entfernt.
    - **Optimierung:** Windows Telemetrie deaktiviert, GPU Studio-Treiber (572.83) verifiziert, ~250GB Speicher befreit.
- VM 200, VM 210, VM 220 and VM 230: QEMU Guest Agent verified from Proxmox during latest audit
- Business stacks are running from `/opt/homeserver2027/stacks` under systemd-managed local IaC
- Home Assistant OS is stable on `10.1.0.24:8123` and `ha.hs27.internal` now returns `HTTP 200` through Caddy
- `Nextcloud`-Reachability wurde am `2026-04-09` erneut stabilisiert: `VM 200` war per Cloud-Init versehentlich auf `10.1.0.24/24` gedriftet und kollidierte damit mit `HAOS`; die VM wurde kontrolliert auf `10.1.0.21/24` zurueckgezogen, danach liefern `http://10.1.0.21:8080/status.php`, `http://cloud.hs27.internal/status.php` und `http://100.99.206.128:8445/status.php` wieder `HTTP 200`
- `frawo-tech.de` / `www.frawo-tech.de` bleiben trotz intern gruenem Odoo-/Caddy-Pfad extern blockiert; der aktuelle Caddy-Log zeigt fuer die ACME-Challenges auf `92.211.33.54` weiter `Connection refused`, also einen Public-Edge-/Forwarding-Block ausserhalb von Odoo selbst
- `ha.hs27.internal` liefert am Abendstand `2026-04-09` ueber Caddy `HTTP 400`, waehrend der Direktpfad `10.1.0.24:8123` `HTTP 200` liefert; das ist aktuell ein kleiner HA-Reverse-Proxy-/Trust-Drift, nicht der zentrale Business-MVP-Blocker
- Direct Ansible management status: `ansible-ping=passed`
- Local Proxmox backup status: `backup-list=passed`, `proxmox-local-backup-check=passed`; the latest stress run is the deciding source for whether real archives under `/var/lib/vz/dump` are currently proven
- PBS status from latest gate: `pbs-stage-gate=failed`, `pbs-proof-check=failed`; `VM 240` existiert, ist aber gestoppt und der verifizierte Datastore-/Proof-Pfad ist aktuell nicht gruen
- Security baseline from latest gate: `security-baseline-check=passed`
- Capacity review says the host is memory-overcommitted on paper; immediate right-sizing candidates are `VM 200` and `VM 220`, while `VM 210` should not be reduced
- Right-sizing stage gate is green; the actual memory reduction remains a maintenance-window change and is not yet applied
- Shared frontend node `surface-go-frontend` on `192.168.2.154` remains blocked in the live audit; SSH, HTTP and HTTPS are currently closed and the active recommendation is `clean_rebuild_then_apply_bootstrap_surface_go_frontend_playbook`
- Local media prep is staged on the ZenBook: `/dev/mmcblk0` for Raspberry Pi, `/dev/sdd` is now the ready blue Ventoy install-/image-stick, and `/dev/sdc1` is the ready exFAT Favorites-stick `FRAWO_FAVS`
- Portable backup / PBS datastore path is currently not verified green in the latest PBS checks; der sichtbare USB-Stick meldet derzeit `No medium found`, und die datentragende USB-SSD bleibt bis zu einer expliziten Freigabe unangetastet
- Raspberry-Pi radio node remains only partially green: `radio.hs27.internal` and the mobile radio frontdoor answer through the toolbox, but the live audit still shows `rpi_radio_integrated=no` und `rpi_radio_usb_music_ready=no`
- Radio/AzuraCast is therefore not part of the current business-MVP release decision
- Media server V1 is now live on `CT 100 toolbox`: Jellyfin is reachable internally on `http://media.hs27.internal`, directly on `http://10.1.0.20:8096`, and through the mobile Tailscale frontdoor on `:8449`; the obsolete local bootstrap sync is retired and Jellyfin reads from the central SMB-backed media path
- ZenBook remote posture is now stronger: Tailscale joined on `100.76.249.126` and AnyDesk is installed and active as a GUI fallback
- Remote-only work windows are now codified through `REMOTE_ONLY_WORK_WINDOW.md` and `make remote-only-check`
- **Repository Reorganization (2026-04-12)**: Root clutter from past remediation phases has been moved into structured subdirectories (`scripts/remediations`, `scripts/archive`, `scripts/research`, `scripts/business`, `scripts/tools`). The root directory now only contains core infrastructure files, shortcut commands, and verified administrative documents.
- **StudioPC Workstation Katarzis:** Der Rechner wurde in eine dedizierte Antigravity-Workstation transformiert.
   - **Laufwerks-Mapping (Persistent):** `P:\` (PROJEKTE), `S:\` (SAMPLES), `L:\` (LIBRARY_ASSETS) auf `C:\WORKSPACE`.
   - **Bereinigung:** Alle Gaming-Altlasten (Riot, Steam-Residuen, Vanguard) wurden entfernt.
   - **Optimierung:** Windows Telemetrie deaktiviert, GPU Studio-Treiber (572.83) verifiziert, ~250GB Speicher befreit.

## Active Work Queue


## Operator Actions Needed

- [x] Geraete-Rollout: Surface Laptop und iPhone (Verifiziert am 2026-04-09)
- [x] Vaultwarden Recovery: Physischer Nachweis erbracht (2026-04-09)
- [ ] Radio/Media: Kuration der Bibliothek (Lane E)
- [ ] Website: Go-Live Vorbereitung (Lane B)

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
12. AKTION VON DIR ERFORDERLICH: Incoming-Strategie fuer agent@frawo-tech.de auf webmaster@frawo-tech.de bewusst festziehen
   - benoetigte Aktion: entscheiden, ob Odoo den Shared-Posteingang `webmaster@frawo-tech.de` fuer `agent@` direkt per Fetchmail lesen darf oder ob vorher ein engerer Provider-/Ordner-Filterpfad geschaffen werden soll
   - warum: Alias, API-Key und sichtbare Zustellung sind jetzt gruen; offen bleibt nur noch die betriebssichere Incoming-Strategie fuer den Shared-Mailpfad
   - danach uebernehmen Codex/Gemini wieder: Odoo-Intake-End-to-End erneut pruefen und den Mailpfad fachlich einhaengen
14. `AKTION VON DIR ERFORDERLICH:` Toolbox (LXC 100) neu aufbauen (Tailscale / Caddy)
   - benoetigte Aktion: entscheiden, ob CT 100 aus einem lokalen/PBS-Backup wiederhergestellt oder neu konzipiert wird.
   - warum: Nachdem der Anker-Crash die Toolbox-Disk zerstört hat, fehlt die zentrale Netzwerkbrücke für `100.99.206.128` und das offizielle Cloudflare/Proxy-Routing. Odoo läuft nur auf Bypass.
   - danach uebernehmen Codex/Gemini wieder: DNS und Proxies wieder geradebügeln.
15. `AKTION VON DIR ERFORDERLICH:` PBS-Instanz (Anker) endgültig abschreiben
   - benoetigte Aktion: Das Backup-Konzept auf den laufenden PBS in Stockenweiler (109) fokussieren und die tote Anker-PBS-Instanz löschen.
   - warum: Konsolidierung der Backup-Aktivitäten.

13. Hinweis: Mobiler HTTPS-Vertrauensstandard (2026)
   - die interne CA (`frawo-ca.crt`) wird ueber `http://portal.hs27.internal/frawo-ca.crt` bereitgestellt.
   - die Installation ist fuer Bitwarden, Nextcloud und Odoo auf Android/iOS zwingend erforderlich, um untrusted-SSL-Fehler zu vermeiden.
   - Leitfaden: `DOCS/MOBILE_HTTPS_TRUST.md`.


## Current Readiness Findings
1. Die Plattform folgt jetzt zwei echten Freigabespuren:
   - Business-MVP fuer `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`, STRATO-Mail und lokale Backups
   - Vollzertifizierung spaeter fuer `PBS`, `surface-go-frontend`, `Radio/AzuraCast` und Shared Frontend
2. Der Business-Kern ist technisch weitgehend gruen:
   - Inventory, Ansible, QGA, Toolbox, Vaultwarden-SMTP, lokale Backups und Security-Baseline sind im letzten Stresslauf bestanden.
   - Abendverifikation `2026-04-09`: `Portal=200`, `Odoo=200`, `Paperless=302`, `Nextcloud status=200`, `Vaultwarden alive=200`, mobile Frontdoors `8444=200`, `8445=200`, `8446=302`, `8447=200`
3. Die Vollzertifizierung bleibt technisch blockiert:
   - `PBS` ist nicht gruen
   - `surface-go-frontend` ist aktuell nicht erreichbar
   - `Radio/AzuraCast` ist intern adressierbar, aber nicht als integrierter Produktionspfad verifiziert
   - `www.frawo-tech.de` ist noch nicht extern freigegeben; der blocker sitzt aktuell am Public Edge und nicht mehr am Website-Inhalt
4. Freigaben duerfen nur ueber Gate-Artefakte behauptet werden:
   - `release_mvp_gate` fuer den Arbeits-MVP
   - `production_gate` fuer das volle interne Produktionssiegel

## Best-Practice Actions


## Collaboration Contract

- Update canonical source files instead of creating duplicate notes.
- Gemini and Codex should use the same shared files listed above.
- The user systemd path unit should refresh this file automatically after source-file changes.
- Manual fallback: `make refresh-context`

- Wolf_EE Review Refinement 2026-04-09: Die lokale Review-Struktur wurde weiter verfeinert. `reference_sets` ist jetzt in `source_series/essential_mixes` und `misc_reference_sets/record_data` getrennt. `download_pools` ist jetzt in `source_pools/nicotone`, `genre_buckets/genre_pool` und `artist_buckets/artist_pool` aufgeteilt. `incoming/` bleibt leer, `bulk/` enthaelt nur noch den grossen Massenblock `MUSIK`.
- Nextcloud Reachability Recovery 2026-04-09: `VM 200 nextcloud` war auf `10.1.0.24/24` gedriftet und kollidierte damit mit `VM 210 HAOS`. Proxmox `ipconfig0` wurde auf `10.1.0.21/24` zurueckgesetzt, `VM 200` neu gestartet und die Frontdoors `cloud.hs27.internal` sowie `:8445` liefern wieder `HTTP 200`. Der externe Website-Blocker bleibt getrennt: Caddy erreicht die ACME-Challenges intern, aber `92.211.33.54` liefert fuer `frawo-tech.de`/`www.frawo-tech.de` weiter `Connection refused`.
- Website Copy Refinement 2026-04-09 spaet: Die publizierte FraWo-Homepage und `/contactus` wurden live textlich neu gezogen, weil der bisherige Ton noch zu stark nach generierter Prompt-Sprache klang. Homepage-Views `3636` und `3644` wurden bewusst synchronisiert; sichtbar live sind jetzt u. a. `Technik fuer Veranstaltungen, die sauber laufen.`, `Planung, Betrieb und digitale Begleitung.` und `Veranstaltungstechnik bewertet man nicht nach Prospekt.`.
- Website Visual Finish 2026-04-10: Die FraWo-Website wurde live auf ein staerkeres, editorialeres Raster gezogen. Neu aktiv sind u. a. `frawo-hero-shell`, `frawo-editorial-card`, `frawo-service-grid`, `frawo-proof-gallery`, `frawo-contact-shell` und `frawo-contact-grid`. Die Seite wirkt damit weniger nach Standard-Dreikarten-Landingpage und deutlich mehr nach bewusst gebautem Eventdienstleister-Auftritt.
- Anti-Split-Brain-Regel 2026-04-10: Fuer `FraWo Website / Odoo Views` gilt jetzt ein harter Single-Writer-Standard. `Codex` ist einziger Writer fuer Repo-Assets und Live-Odoo-Views; `Gemini` bleibt visible-verification-only; `Claude`-Handoffs sind advisory und muessen erst in `Codex/website/` konsolidiert werden, bevor live geschrieben wird.
- Website SEO Cleanup 2026-04-10: Die generischen Odoo-Metadaten wurden live entfernt. Homepage zeigt jetzt echten Title, Description, OG-Description und sauberes Canonical auf `https://www.frawo-tech.de/`; Kontaktseite zeigt echte Description und sauberes Canonical auf `https://www.frawo-tech.de/contactus`. Restpunkt bleibt nur `og:url` auf `/contactus`, das im Host-Preview noch `http://odoo.hs27.internal/contactus` zieht.
- Website Meta Finalization 2026-04-10: Der letzte `/contactus`-Restpunkt wurde bereinigt. Ursache war, dass die Kontaktseite noch als generische `website.page` ohne `website_id` lief. Nach Zuordnung zu `website_id=1` rendert jetzt auch `og:url` sauber auf `https://www.frawo-tech.de/contactus`.

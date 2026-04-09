# Live Context

## Workspace
- Status: **Audit-Operation A-E Vollständig** (2026-04-07)
- Odoo-Sync: **Erfolgreich** (Masterprojekt `21` auf kanonischen SSOT-Stand gezogen)

- Name: `Homeserver 2027 Ops Workspace`
- Alias: `/home/wolf/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Desktop shortcut: `/home/wolf/Desktop/Homeserver 2027 Workspace`
- Generated at: `2026-04-05 01:12:43 CEST`
- Git branch: `main`
- Pending git changes: `745`

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

- `INTRODUCTION_PROMPT.md` updated: `2026-03-31 06:31:48`
- `BUSINESS_MVP_PROMPT.md` updated: `2026-03-28 07:18:15`
- `WEBSITE_RELEASE_PROMPT.md` updated: `2026-03-30 12:46:15`
- `FULL_CERTIFICATION_PROMPT.md` updated: `2026-03-28 07:18:15`
- `AI_BOOTSTRAP_CONTEXT.md` updated: `2026-04-04 02:03:02`
- `README.md` updated: `2026-03-30 10:27:01`
- `MASTERPLAN.md` updated: `2026-04-04 00:41:32`
- `OPERATIONS/OPERATOR_ROUTINES.md` updated: `2026-03-26 23:23:08`
- `SECURITY_BASELINE.md` updated: `2026-03-24 11:50:08`
- `SESSION_CLOSEOUT.md` updated: `2026-04-04 15:23:54`
- `GEMINI.md` updated: `2026-04-03 23:06:54`
- `MEMORY.md` updated: `2026-04-04 18:52:59`
- `NETWORK_INVENTORY.md` updated: `2026-04-05 01:12:38`
- `VM_AUDIT.md` updated: `2026-04-04 00:05:40`
- `BACKUP_RESTORE_PROOF.md` updated: `2026-03-25 18:07:10`
- `CAPACITY_REVIEW.md` updated: `2026-03-24 11:50:08`
- `RIGHTSIZING_MAINTENANCE_PLAN.md` updated: `2026-03-24 11:50:08`
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md` updated: `2026-03-30 22:16:11`
- `MEDIA_AND_REMOTE_PREP.md` updated: `2026-03-24 11:50:08`
- `REMOTE_ACCESS_STANDARD.md` updated: `2026-04-03 21:51:18`
- `REMOTE_ONLY_WORK_WINDOW.md` updated: `2026-03-24 11:50:08`
- `ADGUARD_PILOT_ROLLOUT_PLAN.md` updated: `2026-03-24 11:50:08`
- `TAILSCALE_SPLIT_DNS_PLAN.md` updated: `2026-03-24 11:50:08`
- `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` updated: `2026-03-24 11:50:08`
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` updated: `2026-03-30 15:46:20`
- `RASPBERRY_PI_RADIO_NODE_PLAN.md` updated: `2026-03-24 11:50:08`
- `RPI_RESOURCE_ALLOCATION_PLAN.md` updated: `2026-03-24 11:50:08`
- `AZURACAST_FIRST_STATION_BASELINE.md` updated: `2026-03-26 08:51:37`
- `RADIO_OPERATIONS_STANDARD.md` updated: `2026-03-24 11:50:08`
- `MEDIA_SERVER_PLAN.md` updated: `2026-03-26 22:26:25`
- `MEDIA_SERVER_CLIENT_SETUP.md` updated: `2026-03-25 13:44:07`
- `OPERATOR_TODO_QUEUE.md` updated: `2026-04-05 01:11:54`
- `PBS_VM_240_SETUP_PLAN.md` updated: `2026-03-27 08:57:47`
- `HAOS_VM_210_SETUP_PLAN.md` updated: `2026-03-24 11:50:08`
- `PORTABLE_BACKUP_USB_PLAN.md` updated: `2026-03-24 11:50:08`
- `ansible/inventory/hosts.yml` updated: `2026-03-31 06:41:55`
- `ansible/inventory/group_vars/all/vault.yml` updated: `2026-03-26 23:10:18`

## Current Estate Snapshot

- Managed hosts in Ansible inventory: `30`
- Router baseline: `192.168.2.1` Vodafone Easy Box
- UCG transition gateway: `UniFi Cloud Gateway Ultra (UCG-Ultra)` active for `proxmox-anker` on VLAN 101 (`10.1.0.92/24`), with legacy aliases `192.168.2.10/24`
- UCG status: **ONLINE**, internet routing restored after removal of conflicting static route `Anker-Legacy-Bridge`
- Core business nodes: `10.1.0.20` toolbox, `10.1.0.21` nextcloud, `10.1.0.22` odoo, `10.1.0.23` paperless, `10.1.0.24` haos, `10.1.0.26` vaultwarden, `10.1.0.30` storage-node
- Latest stress summary: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_234807/summary.tsv`
- Latest release-MVP gate: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_gate/20260331_095709/release_mvp_gate.md` -> `BLOCKED`
- Latest production gate: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/production_gate/20260328_072130/production_gate.md` -> `BLOCKED`
- Toolbox network base: Caddy on `10.1.0.20:80`, AdGuard Home on `10.1.0.20:53` and localhost-only admin on `127.0.0.1:3000`, `hs27.internal` rewrites verified in opt-in mode
- Toolbox mobile Tailscale frontdoor: `100.99.206.128:8443` HA, `:8444` Odoo, `:8445` Nextcloud, `:8446` Paperless, `:8447` Portal, `:8448` Radio (502: node `100.64.23.77` offline), `:8449` Media
- Toolbox Tailscale state: `/dev/net/tun` mapped, `tailscaled` active, backend `Running`, subnet route `10.1.0.0/24` is advertised (Tailnet approval pending), Split-DNS still needs to be updated to `10.1.0.20`
- Toolbox runtime nuance `2026-04-07`: der produktive Frontdoor laeuft containerisiert als `toolbox-network_caddy_1`; `homeserver2027-toolbox-mobile-firewall.service` ist `active`, waehrend der Host-Dienst `caddy.service` selbst `inactive` ist
- Toolbox DNS-Remediation `2026-04-08`: `CT 100` war auf `nameserver 127.0.0.1` gedriftet, obwohl der lokale Host-Resolver ueber `127.0.0.1:53` nicht antwortete; der funktionierende Pfad ist `10.1.0.20:53`. `/etc/resolv.conf` wurde deshalb auf `nameserver 10.1.0.20` plus `search hs27.internal` zurueckgezogen
- VM 200, VM 210, VM 220 and VM 230: QEMU Guest Agent verified from Proxmox during latest audit
- Business stacks are running from `/opt/homeserver2027/stacks` under systemd-managed local IaC
- Odoo runtime remediation `2026-04-07`: Compose-Drift in `VM 220`, fehlender `:8444`-Caddy-Block auf `toolbox` und Versionsdrift `DB=Odoo 17` vs. `Container=odoo:16.0` wurden bereinigt; `10.1.0.22:8069`, `odoo.hs27.internal` und `100.99.206.128:8444` liefern jetzt `HTTP 200`
- Odoo filestore remediation `2026-04-07`: Fehlende Attachment-Dateien wurden aus dem alternativen Baum `filestore/FraWo_GbR` in den von Odoo 17 erwarteten Pfad `.local/share/Odoo/filestore/FraWo_GbR` reconciliert; die zuvor fehlenden Referenzen sind auf `0` gesunken
- Odoo DB-Guardrail `2026-04-07`: Ab hier keine direkten SQL-Schreibfixes ohne frischen VM-Backup-/Snapshot-Nachweis; die Runtime ist wieder gruen, also kuenftige DB-Arbeit nur bewusst und mit Rueckweg
- Nextcloud runtime remediation `2026-04-07`: Compose-Drift in `VM 200` wurde bereinigt; Root Causes waren MariaDB-Drift `Redo-Logs=10.11` gegen gedriftetes `10.6`, ein verwaister `nextcloud:latest`-Altcontainer und App-Version-Drift. `cloud.hs27.internal/` und `/status.php` liefern wieder `HTTP 200`, `maintenance=false`, `needsDbUpgrade=false`, und `homeserver-compose-nextcloud.service` ist wieder `active`
- Nextcloud Mail remediation `2026-04-07`: Mail-Abruf scheiterte nicht an der App selbst, sondern an DNS-Drift in `VM 200`; Cloud-Init zeigte noch Tailscale-DNS `100.100.100.100` plus `tail150400.ts.net`, obwohl dort kein `tailscaled` lief. Persistenter Fix ueber Proxmox: `nameserver=10.1.0.20`, `searchdomain=hs27.internal`; danach loesen VM und Container `imap.strato.de` wieder auf und der TLS-Handshake auf `993` ist gruen
- Nextcloud Alias-Routing 2026-04-08: Der Shared-Posteingang webmaster@frawo-tech.de trennt Alias-Mails jetzt praktisch ueber VM 200; `agent@` und `info@` werden in `Aliases.Agent` bzw. `Aliases.Info` geroutet, waehrend `wolf@` bewusst in der Haupt-`INBOX` bleibt. `hs27-nextcloud-alias-router.timer` ist enabled/active, und die End-to-End-Proben fuer `info@` und `wolf@` verhalten sich entsprechend.
- Storage-Integrationsaudit 2026-04-08: `Nextcloud`, `Odoo` und `Paperless` bleiben auf getrennten VM-/Docker-Volumes; der sichere gemeinsame Dokumentenpfad bleibt die bestehende `Nextcloud <-> Paperless`-Bridge, waehrend der zentrale Medienpfad aktuell hostseitig als `/mnt/hs27-media/yourparty_Libary` von `//10.1.0.30/Media` verifiziert ist. `Nextcloud` hat `files_external` sichtbar an Bord; `Odoo`-Anhaenge sollen spaeter nur ueber Export/Mirror nach `Nextcloud` sichtbar werden, nicht ueber einen gemeinsamen Live-Filestore. Eine direkte `Stockenweiler`-Musikquelle ist von diesem Arbeitsplatz heute noch nicht belastbar live verifiziert.
- Toolbox Mobile-Frontdoor Remediation 2026-04-08: Die aktive Caddyfile auf CT 100 toolbox enthielt nur noch :8444 und :8447; die Mobile-Site-Bloecke fuer :8443 (HA), :8445 (Nextcloud), :8446 (Paperless), :8448 (Radio) und :8449 (Media) wurden kontrolliert wiederhergestellt. Verifiziert vom Admin-Client: 8443=200, 8444=200, 8445=302, 8446=200, 8447=200, 8449=302; :8448 bleibt erwartbar vom bekannten Radio-Node-Zustand abhaengig.
- Public-Website-Realitaet 2026-04-08: Der interne Business-Core ist auf Anker gruen, aber rawo-tech.de/www.frawo-tech.de sind heute noch nicht als oeffentlicher Releasepfad verifiziert. Public DNS auf 92.211.33.54 ist sichtbar, auf 	oolbox liegen die FraWo-Caddy-Bloecke auf 80/443, aber von proxmox-anker lief der IPv4-Pfad auf  00; damit bleibt der Public-Edge-/Forwarding-Teil ein getrennter Restblock.
- Public-Website-Design-Remediation 2026-04-08: Die Odoo-Website auf `VM 220` ist jetzt sichtbar auf FraWo gezogen: gebrandete Homepage, saubere Kontaktseite, Mailto-CTA auf `info@frawo-tech.de` und kein alter Platzhalter-Footer mehr im gerenderten HTML.
- Website-Semantik 2026-04-08: `web.base.url=https://www.frawo-tech.de` bleibt eingefroren, `website.domain` wurde in der Ein-Website-Instanz bewusst wieder auf `NULL` gesetzt, und der Host-Preview fuer `www.frawo-tech.de` liefert jetzt korrekte `canonical`-/`og:url`-Werte fuer Start- und Kontaktseite.
- Website-Rollback/Apply 2026-04-08: Scoped Rollback fuer die betroffenen Odoo-Website-Records liegt lokal in `Codex/website_backups/frawo_public_website_prepolish_20260408.sql`; der angewandte Sollzustand liegt in `Codex/website_backups/frawo_public_website_polish_20260408.sql`.
- Public-Website-Event-Rebuild 2026-04-09: Die Odoo-Website ist jetzt klar als Eventdienstleister-Auftritt gezogen. Hero `Eventbetrieb mit technischer Praezision.`, Services fuer Technik, Event-Webseite und belastbaren Hintergrund, Kontaktseite `Projektstart ohne Umwege.`, Menuepunkt `Kontakt`, CTA `Projekt anfragen`.
- Foto-Rueckkehr 2026-04-09: Die frueher vermissten Odoo-Testfotos waren nicht geloescht, sondern nur nicht mehr in den publizierten Views referenziert; sie sind jetzt kontrolliert wieder im Layout eingebunden, u. a. ueber `/web/image/1803`, `/web/image/1798`, `/web/image/1801`, `/web/image/1797`, `/web/image/1805` und `/web/image/1806`.
- Website-Rollback 2026-04-09: Der Rueckweg vor dem Event-Rebuild liegt lokal in `Codex/website_backups/frawo_event_site_pre_rebuild_20260409.sql`.
- Home Assistant OS is stable on `10.1.0.24:8123` and `ha.hs27.internal` now returns `HTTP 200` through Caddy
- Direct Ansible management status: `ansible-ping=passed`
- Local Proxmox backup status: `backup-list=passed`, `proxmox-local-backup-check=passed`; the latest stress run is the deciding source for whether real archives under `/var/lib/vz/dump` are currently proven
- Proxmox rootfs remediation `2026-04-07`: `apt update` scheiterte kurzzeitig an `No space left on device`, Ursache war lokale Backup-Retention-Drift in `/var/lib/vz/dump`; nach Rueckschnitt auf den dokumentierten Zwischenstandard `2` Archive pro Business-VM steht `pve-root` wieder bei ca. `83%` und `apt update` ist wieder gruen
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
- **StudioPC Workstation Katarzis:** Der Rechner wurde in eine dedizierte Antigravity-Workstation transformiert.
   - **Laufwerks-Mapping (Persistent):** `P:\` (PROJEKTE), `S:\` (SAMPLES), `L:\` (LIBRARY_ASSETS) auf `C:\WORKSPACE`.
   - **Bereinigung:** Alle Gaming-Altlasten (Riot, Steam-Residuen, Vanguard) wurden entfernt.
   - **Optimierung:** Windows Telemetrie deaktiviert, GPU Studio-Treiber (572.83) verifiziert, ~250GB Speicher befreit.

## Active Work Queue

- `Lane A: MVP Closeout` bleibt die aktive Delivery-Lane; die realen Freigabe-Blocker sind weiter `device_rollout_verified` und `vaultwarden_recovery_material_verified`.
- Root-level Odoo-Helper vom `2026-04-07` sind der aktuelle Implementierungshotspot: `test_odoo_smtp.py`, `debug_odoo_mail.py`, `check_odoo_dashboards.py`, `fix_odoo_dashboards.py`, `final_fix_dashboards.py`, `list_odoo_projects.py`, `odoo_masterplan_sync.py`, `fix_odoo_dns.sh`, `final_dns_fix.sh`, `harden_smtp.sh`.
- Diese Odoo-Helper derzeit als gemeinsame Scratch-Zone behandeln und keine parallelen Edits hineinziehen, solange SMTP-/Dashboard-Triage noch laeuft.
- Konfliktarme Repo-only-Arbeit liegt aktuell bei Wahrheitspflege und Drift-Abgleich zwischen `LIVE_CONTEXT.md`, `AI_SERVER_HANDOFF.md`, `MASTERPLAN.md` und `MEMORY.md`; erst danach die Odoo-Helfer in einen credentiallosen Standard konsolidieren.
- In diesem Checkout gibt es sichtbare Quellen-Drift: `README.md`, `SESSION_CLOSEOUT.md`, `OPERATOR_TODO_QUEUE.md`, `manifests/work_lanes/current_plan.json` und `scripts/` werden von Handoff-Dateien referenziert, fehlen hier aber real und muessen deshalb als `missing-in-checkout` behandelt werden.
- Neue Odoo-Leitentscheidung: Das Homeserver-Masterprojekt in Odoo wird als operativer `task SSOT` aufgebaut; Repo-Dateien bleiben weiter `runtime SSOT`. `agent@frawo-tech.de` ist dafuer die kuenftige least-privilege Automationsidentitaet; in diesem Block wird **kein n8n auf dem Homeserver** eingeplant.
- Odoo-Reachability-Incident vom `2026-04-07` ist end-to-end behoben: Root Causes waren Compose-Drift, fehlender `:8444`-Block in der aktiven Toolbox-Caddyfile, Versionsdrift `Odoo 17 DB` gegen `odoo:16.0` sowie gesplittete Filestore-Pfade; Odoo antwortet jetzt wieder ueber direkt, intern und mobil mit `HTTP 200`.
- Nextcloud-Incident vom `2026-04-07` ist technisch behoben: `VM 200` laeuft wieder ueber den vorgesehenen Stackpfad, `cloud.hs27.internal` ist gruen und der Standardpfad `occ upgrade` plus `maintenance:repair` wurde ohne direkte DB-Schreibfixes abgeschlossen.
- Odoo-Board-Apply vom `2026-04-07`: Masterprojekt `21` ist jetzt operativer `task SSOT`; die sechs kanonischen Projektphasen sind verknuepft, `#217` und `#225` stehen auf `Erledigt`, `Nextcloud Runtime Hardening / Version Pinning` ist als Folge-Task offen, `rootflo2525@gmail.com` ist aus dem Masterprojekt entfernt und `ownerless_open=0` ist DB-seitig verifiziert.
- Odoo-Automationsidentitaet vom `2026-04-07`: `agent@frawo-tech.de` ist aktiv, ohne nachweisbare Admin-/Settings-/Studio-Gruppen, und jetzt gezielt an Server-/Ops-/Automation-Tasks verlinkt; API-Key und Incoming-Pfad bleiben die echten Restpunkte, waehrend serverseitiges `n8n` in diesem Block bewusst nicht verfolgt wird.
- Odoo-Alias-/API-Key-Audit vom `2026-04-08`: Projekt `21` hat jetzt den Alias `agent@frawo-tech.de`; `alias_contact` bleibt defensiv auf `employees`, fuer `agent@frawo-tech.de` existiert ein serverseitig erzeugter RPC-Key (`api_key_count=1`) als root-only Staging-Secret ausserhalb des Repos, aber der echte Mail-Intake ist mit `fetchmail_count=0` noch nicht end-to-end live.
- Mail-/Alias-Entscheidung `2026-04-08`: `agent@frawo-tech.de` wird aus Kapazitaetsgruenden nicht als eigenes STRATO-Postfach gefuehrt, sondern ist jetzt bewusst Alias auf `webmaster@frawo-tech.de`.
- Mail-Intake-Probe `2026-04-08`: Eine erste Testmail an `agent@frawo-tech.de` lief zunaechst in einen STRATO-Ruecklaeufer `Returned Mail ...`, aber die spaetere Live-Probe ueber den produktiven Odoo-Mailpfad ist gruen: STRATO hat die Zustellung angenommen und die Nachricht wurde sichtbar im technischen Basis-Postfach mit `To: agent@frawo-tech.de` gefunden.
- Live-Probe `2026-04-08` abends: Direkter SMTP-Zustellversuch ueber den produktiven Odoo-Mailpfad ist jetzt gruen; MX-Pruefung auf `smtpin.rzone.de` akzeptiert `webmaster@frawo-tech.de` und `agent@frawo-tech.de`, und der Volltest `smtp.strato.de` -> `agent@frawo-tech.de` -> IMAP-INBOX `webmaster@frawo-tech.de` lieferte sichtbaren Inbox-Treffer mit passendem `To:`-Header.
- Architekturentscheidung `2026-04-08`: kein `n8n` auf dem Homeserver in diesem Block; wegen Kapazitaet und Betriebsruhe bleibt der Zielpfad zuerst Odoo-nativ plus providerseitig empfangsfaehiges `agent@`.
- Odoo-Runtime-Drift vom `2026-04-08`: Webcontainer fiel erneut auf dem Docker-Netzpfad mit DB-Auth-Fehler aus; Root Causes waren Compose-/Secret-Drift gegen das echte Volume-Passwort sowie zu enge `600`-Rechte auf den gemounteten Dateien. Nach Rueckzug auf den echten DB-Netzpfad und lesbare Mount-Rechte liefern direkt, intern und mobil wieder `HTTP 200`.
- Odoo-Frontdoor-Regression `2026-04-08` mittags: Odoo selbst blieb auf `10.1.0.22:8069` gesund, aber `toolbox-network_caddy_1` fiel wegen einer kaputt edierten Caddyfile in eine Restart-Schleife; nach Syntax-Fix und Rueckzug des versehentlichen TLS auf `:8444` liefern `odoo.hs27.internal` und `100.99.206.128:8444/web/login` wieder `HTTP 200`.

## Operator Actions Needed

- `AKTION VON DIR ERFORDERLICH:` Den fehlenden 2FA-Pfad rund um das verlorene Operator-Smartphone wiederherstellen oder bewusst ersetzen und danach die sichtbare Franz-Geraeteabnahme fuer Surface Laptop und iPhone abschliessen.
- `AKTION VON DIR ERFORDERLICH:` Zwei getrennte Offline-Kopien des Vaultwarden-Recovery-Materials frisch verifizieren und die sichtbare Evidenz dafuer liefern.
- `AKTION VON DIR ERFORDERLICH:` Bewusst entscheiden, ob Odoo den Shared-Posteingang `webmaster@frawo-tech.de` fuer `agent@`-Intake direkt per Fetchmail lesen darf oder ob vorher ein engerer Provider-/Ordner-Filterpfad geschaffen werden soll.


## Current Readiness Findings

1. **Die Plattform folgt jetzt zwei echten Freigabespuren:**
   - **Business-MVP:** Fokus auf `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`, STRATO-Mail und lokale Backups.
   - **Vollzertifizierung:** Spaeterer Pfad fuer `PBS`, `surface-go-frontend`, `Radio/AzuraCast` und Shared Frontend.

2. **Der Business-Kern ist technisch weitgehend gruen:**
   - Inventory, Ansible, QGA, Toolbox, Vaultwarden-SMTP, lokale Backups und Security-Baseline sind im letzten Stresslauf bestanden.

3. **Infrastruktur-Zustand (LIVE):**
   - **UniFi Firewall:** Egress fuer VLAN 101 ist geoeffnet (UDP 3478/41641, TCP 443).
   - **Tailscale Routing:** Toolbox bewirbt `10.1.0.0/24`.
   - **Split-DNS:** `hs27.internal` ist korrekt auf `10.1.0.20` (und Fallback `100.99.206.128`) konfiguriert.

## Collaboration Contract

- Update canonical source files instead of creating duplicate notes.
- Gemini and Codex should use the same shared files listed above.
- The user systemd path unit should refresh this file automatically after source-file changes.
- Manual fallback: `make refresh-context`




- Website-Layout-Restore 2026-04-09: Homepage auf den frueheren gefaelligen FraWo-Auftritt zurueckgezogen und als Hybrid neu aufgebaut. Hero wieder Smart Media & Event, alte Karten-/Band-/Kontaktdramaturgie zurueck, die Odoo-Fotos /web/image/1803, /1798, /1801, /1797, /1805, /1806 bleiben sichtbar eingebunden, und die problematische Handwerk-Sprache bleibt draussen.

- Website-Content-Fix 2026-04-09: Homepage- und Kontakttexte wurden inhaltlich auf klaren Eventdienstleister-Fokus zurueckgezogen. Aktiver Live-Text betont Technik, Ablauf, Zuspielung und Besucherinfo; Handwerk-/HWK-Naehe und Agentursprech bleiben entfernt.

- Website-Pro-Redesign 2026-04-09: FraWo-Startseite auf einen staerker redaktionellen, professionellen Eventdienstleister-Auftritt gezogen. Orientierung fuer Anspruch und Raster an grossen Medien-/Eventseiten wie sunshine live und NTS: starke Typohierarchie, modulare Sektionen, grosse Bildflaechen, klare Leistungsbloecke, kein Agentursprech.
- Kontaktseite-Fix 2026-04-09: XML-Renderfehler durch unescaped Font-Import-URL behoben; /contactus liefert wieder sauber gerendertes HTML.

- Website-Typografie 2026-04-09: FraWo-Homepage, Kontaktseite und Footer sind jetzt auf Poppins umgestellt. Die vorherige Mischtypografie mit Barlow Condensed/Manrope ist aus dem Renderpfad entfernt.

- Typografie-Feinschliff 2026-04-09: Poppins bleibt CI-weit gesetzt, aber Gewichte sind jetzt abgestuft. Hero/Display weiter 800, Section-Heads/Card-Heads/Panels auf 700, Labels weicher gezogen und Uppercase-Haerte reduziert.

- Claude-Handoff 2026-04-09: Fuer FraWo Website-Design und Hosting liegt jetzt ein separater Uebergabe-Brief in CLAUDE_WEBSITE_HOSTING_HANDOFF.md vor, inklusive CI-Regeln, Designanspruch, Hosting-Lage, Rollback-Dateien und direktem Startprompt.

- Claude-Website-Implementierung 2026-04-09: Vollständige Implementierungs-Assets für FraWo-Website erstellt. Enthält: frawo_custom_css.css (Design-System mit Poppins-CI, Farb-Tokens, alle Klassen), frawo_homepage_blocks.html (7 fertige HTML-Sektionen: Hero, Leistungen, Bild-Trennblöcke, Arbeitsweise, Warum FraWo, CTA), frawo_contactus.html (neue Kontaktseite), frawo_caddy_public_release.txt (Caddy-Block für frawo-tech.de mit echtem ACME-TLS, erst nach DNS+Port-Verifikation aktivieren). Alle Dateien liegen in Codex/website/. Browser-Tool war auf dieser Maschine nicht verfügbar, daher kein direkter Odoo-Eingriff - manuelles Einfügen über Website-Builder erforderlich.

- Odoo-Agent-Intake 2026-04-09: Fuer gent@frawo-tech.de liegt jetzt ein sicherer V1-Intake-Pfad ohne serverseitiges 
8n und ohne blindes Fetchmail auf der Shared-INBOX vor. odoo_agent_intake_bridge.py liest nur Aliases.Agent, erzeugt daraus Odoo-Tasks im Masterprojekt, erkennt Duplikate ueber Message-ID und verschiebt verarbeitete Mails nach Aliases.Agent.Processed; Betriebsrunbook: OPERATIONS/ODOO_AGENT_INTAKE_OPERATIONS.md.
- Odoo-Agent-Intake Deployment 2026-04-09: Der zuvor vorbereitete `agent@`-Bridge-Pfad ist jetzt live auf `VM 200 nextcloud`. Root-only Runtime-Secret liegt unter `/root/.config/homeserver2027/odoo_agent_rpc.env`, der Runner unter `/usr/local/sbin/odoo_agent_intake_runner.sh`, und der Timer `hs27-odoo-agent-intake.timer` ist `enabled`/`active`. Ein echter Proof aus `Aliases.Agent` wurde in Odoo als Task `[agent@] HS27 alias delivery probe retry 20260408-181036` uebernommen und danach nach `Aliases.Agent.Processed` verschoben.
- FraWo-Website-Endfassung 2026-04-09: Homepage und Kontaktseite per Odoo JSON-RPC API direkt auf View-Ebene aktualisiert (Views 3644 und 3637). Neues Design-System aktiv: dunkel #0d1117, Akzent #00e5a0, Poppins CI durchgehend. Homepage: Hero mit Odoo-Bild 1803, Headline 'Technik, die laeuft. Ablaeufe, die halten.', drei Leistungskarten, zwei Bildtrenner (1801/1797), Arbeitsweise-Block, Warum-FraWo-Sektion, CTA. Kontaktseite: 'Projektstart ohne Umwege.' mit Kontaktblock und Antwortzeit-Hinweis. CSS via custom_code_head website-weit injiziert. Live verifiziert per Browser-Screenshot.

- FraWo Website Pivot 2026-04-09: Vollstaendiger Umbau auf B2C/B2B Hybrid-Fokus. Neue Services: Heimkino/HiFi (inkl. Schallpegelmessung) und Smart Home / Architekturbeleuchtung. Rebranding auf UV-Power (Lila #a855f7) und Deep Forest abgeschlossen. Neues Logo (UV FraWo, gruener Subtitle) aus brand_assets/4.png injiziert. Homepage und Kontaktseite per API aktualisiert. Live verifiziert.

- FraWo Website Rollback 2026-04-09: Auf Wunsch des Users das 'zuviel' an Dark Mode wieder zurueckgenommen. Der elegante helle Header inkl. radial-gradient und UV-Akzenten ist wieder aktiv. Die neuen Inhalte (Heimkino/HiFi, Smart Home) wurden in dieses klare Layout integriert. Neues UV-Logo bleibt.

- Media Import 2026-04-09: `Wolf.EE` wurde read-only auf `proxmox-anker` unter `/mnt/wolf-ee` gesichtet. Der erste kontrollierte Import lief danach in den zentralen Review-Pfad `/mnt/data/media/yourparty_Libary/incoming/Wolf_EE_20260409` auf `CT 110 storage-node`; uebernommen wurden `Job Jobse`, `The_TraXx`, `Sets` und `MUSIK` mit zusammen rund `14G`. Wichtige Folge: `storage-node` steht jetzt bei ca. `91%`, daher in diesem Block keine weiteren groesseren Medienimporte mehr.
- Stockenweiler Media 2026-04-09: von `CT 100 toolbox` aktuell keine Route / kein Ping nach `192.168.178.25`; damit ist `Stockenweiler` heute kein belastbarer Live-Importpfad.
- Media Capacity Clarification 2026-04-09: `Stockenweiler` ist ueber Tailscale als Peer (`100.91.20.116`) erreichbar, aber der fuer Medienimporte relevante LAN-Pfad fehlt aktuell weiter; auf `CT 100 toolbox` gibt es keine Route fuer `192.168.178.0/24`, und `tailscale status` meldet `Some peers are advertising routes but --accept-routes is false`. Der grosse Entlastungspfad `/mnt/music_ssd` auf `proxmox-anker` ist derzeit wegen exFAT-Dateisystemfehlern kernelseitig read-only (`/dev/sdb1`, `exFAT-fs ... Filesystem has been set read-only`), daher bleibt `CT 110 storage-node` mit ca. `91%` der aktuelle Druckpunkt und weitere grosse Medienimporte sind bewusst gestoppt.

- Media Routing Recovery 2026-04-09: `stockenweiler-pve` advertised korrekt `192.168.178.0/24`; auf `CT 100 toolbox` wurde `tailscale set --accept-routes=true` gesetzt. Seitdem ist `ping 192.168.178.25` von `toolbox` wieder gruen, also ist der Stockenweiler-LAN-Pfad fuer Sichtung/Read-only-Zugriff wieder offen.
- Media SSD Reliability 2026-04-09: Auf `proxmox-anker` wurde `exfatprogs` installiert und `/dev/sdb1` (`/mnt/music_ssd`) per `fsck.exfat -p` repariert. Die Platte wurde kurz wieder `rw`, kippte unter Schreiblast aber erneut auf `ro` (`exFAT-fs ... Filesystem has been set read-only`). Damit ist sie aktuell kein belastbarer Offload-Pfad.
- Stockenweiler Snapshot 2026-04-09: `stockenweiler-pve` zeigt fuer die Musikmigration `283G` auf `/mnt/music_hdd/yourparty_Libary`; `/mnt/data_family` ist mit rund `102G` frei der realistischere temporaere Zielpfad als die fast volle `music_hdd`.

- Media Cleanup Snapshot 2026-04-09: Der Reviewbestand auf `storage-node` ist jetzt klar eingeordnet. `incoming/studiopc-import-2026-03-25` besteht fast komplett aus Recording-/Cache-Material (`studio-one-cache-audio`, `onedrive-mixxx-recordings`, `mixxx-recordings`) und ist damit der erste fachliche Aufraeumkandidat. `incoming/Wolf_EE_20260409` bleibt der strukturiertere Reviewbestand mit `MUSIK`, `Sets`, `The_TraXx` und `Job Jobse`. Zusaetzliche Uebersicht liegt in `artifacts/media_reconciliation/20260409_media_cleanup_status.md`.

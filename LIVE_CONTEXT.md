# Live Context

## Workspace

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
- VM 200, VM 210, VM 220 and VM 230: QEMU Guest Agent verified from Proxmox during latest audit
- Business stacks are running from `/opt/homeserver2027/stacks` under systemd-managed local IaC
- Odoo runtime remediation `2026-04-07`: Compose-Drift in `VM 220`, fehlender `:8444`-Caddy-Block auf `toolbox` und Versionsdrift `DB=Odoo 17` vs. `Container=odoo:16.0` wurden bereinigt; `10.1.0.22:8069`, `odoo.hs27.internal` und `100.99.206.128:8444` liefern jetzt `HTTP 200`
- Odoo filestore remediation `2026-04-07`: Fehlende Attachment-Dateien wurden aus dem alternativen Baum `filestore/FraWo_GbR` in den von Odoo 17 erwarteten Pfad `.local/share/Odoo/filestore/FraWo_GbR` reconciliert; die zuvor fehlenden Referenzen sind auf `0` gesunken
- Odoo DB-Guardrail `2026-04-07`: Ab hier keine direkten SQL-Schreibfixes ohne frischen VM-Backup-/Snapshot-Nachweis; die Runtime ist wieder gruen, also kuenftige DB-Arbeit nur bewusst und mit Rueckweg
- Nextcloud runtime remediation `2026-04-07`: Compose-Drift in `VM 200` wurde bereinigt; Root Causes waren MariaDB-Drift `Redo-Logs=10.11` gegen gedriftetes `10.6`, ein verwaister `nextcloud:latest`-Altcontainer und App-Version-Drift. `cloud.hs27.internal/` und `/status.php` liefern wieder `HTTP 200`, `maintenance=false`, `needsDbUpgrade=false`, und `homeserver-compose-nextcloud.service` ist wieder `active`
- Nextcloud Mail remediation `2026-04-07`: Mail-Abruf scheiterte nicht an der App selbst, sondern an DNS-Drift in `VM 200`; Cloud-Init zeigte noch Tailscale-DNS `100.100.100.100` plus `tail150400.ts.net`, obwohl dort kein `tailscaled` lief. Persistenter Fix ueber Proxmox: `nameserver=10.1.0.20`, `searchdomain=hs27.internal`; danach loesen VM und Container `imap.strato.de` wieder auf und der TLS-Handshake auf `993` ist gruen
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

## Active Work Queue

- `Lane A: MVP Closeout` bleibt die aktive Delivery-Lane; die realen Freigabe-Blocker sind weiter `device_rollout_verified` und `vaultwarden_recovery_material_verified`.
- Root-level Odoo-Helper vom `2026-04-07` sind der aktuelle Implementierungshotspot: `test_odoo_smtp.py`, `debug_odoo_mail.py`, `check_odoo_dashboards.py`, `fix_odoo_dashboards.py`, `final_fix_dashboards.py`, `list_odoo_projects.py`, `odoo_masterplan_sync.py`, `fix_odoo_dns.sh`, `final_dns_fix.sh`, `harden_smtp.sh`.
- Diese Odoo-Helper derzeit als gemeinsame Scratch-Zone behandeln und keine parallelen Edits hineinziehen, solange SMTP-/Dashboard-Triage noch laeuft.
- Konfliktarme Repo-only-Arbeit liegt aktuell bei Wahrheitspflege und Drift-Abgleich zwischen `LIVE_CONTEXT.md`, `AI_SERVER_HANDOFF.md`, `MASTERPLAN.md` und `MEMORY.md`; erst danach die Odoo-Helfer in einen credentiallosen Standard konsolidieren.
- In diesem Checkout gibt es sichtbare Quellen-Drift: `README.md`, `SESSION_CLOSEOUT.md`, `OPERATOR_TODO_QUEUE.md`, `manifests/work_lanes/current_plan.json` und `scripts/` werden von Handoff-Dateien referenziert, fehlen hier aber real und muessen deshalb als `missing-in-checkout` behandelt werden.
- Neue Odoo-Leitentscheidung: Das Homeserver-Masterprojekt in Odoo wird als operativer `task SSOT` aufgebaut; Repo-Dateien bleiben weiter `runtime SSOT`. `agent@frawo-tech.de` ist dafuer die kuenftige least-privilege Automationsidentitaet, waehrend n8n nur spaetere Orchestrierung und nicht die eigentliche Wahrheit sein darf.
- Odoo-Reachability-Incident vom `2026-04-07` ist end-to-end behoben: Root Causes waren Compose-Drift, fehlender `:8444`-Block in der aktiven Toolbox-Caddyfile, Versionsdrift `Odoo 17 DB` gegen `odoo:16.0` sowie gesplittete Filestore-Pfade; Odoo antwortet jetzt wieder ueber direkt, intern und mobil mit `HTTP 200`.
- Nextcloud-Incident vom `2026-04-07` ist technisch behoben: `VM 200` laeuft wieder ueber den vorgesehenen Stackpfad, `cloud.hs27.internal` ist gruen und der Standardpfad `occ upgrade` plus `maintenance:repair` wurde ohne direkte DB-Schreibfixes abgeschlossen.
- Odoo-Board-Check vom `2026-04-07`: `#217 Service Reachability Audit` ist technisch gruen und bereit zum Abhaken; `#225 Nextcloud Stabilization` ist als Incident weitgehend erledigt, sollte aber nur dann geschlossen werden, wenn ein eigener Follow-up fuer `Nextcloud Runtime Hardening / Version Pinning` sichtbar offen bleibt.

## Operator Actions Needed

- `AKTION VON DIR ERFORDERLICH:` Den fehlenden 2FA-Pfad rund um das verlorene Operator-Smartphone wiederherstellen oder bewusst ersetzen und danach die sichtbare Franz-Geraeteabnahme fuer Surface Laptop und iPhone abschliessen.
- `AKTION VON DIR ERFORDERLICH:` Zwei getrennte Offline-Kopien des Vaultwarden-Recovery-Materials frisch verifizieren und die sichtbare Evidenz dafuer liefern.


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

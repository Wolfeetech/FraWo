# Operator Todo Queue

Stand: `2026-05-30`

## Zweck

Diese Datei ist die kurze manuelle Unblock-Queue. Strategische Wahrheit steht im `MASTERPLAN.md`, Laufzeitwahrheit in `LIVE_CONTEXT.md`, maschinenlesbare Planung in `manifests/work_lanes/current_plan.json`.

## Lane Status

- `Lane A: MVP Closeout` -> `sealed`
- `Lane B: Website/Public` -> `active/prov` (HTTPS live, content pending)
- `Lane C: Security/PBS/Infra` -> `active`
- `Lane D: Stockenweiler` -> `active` (Radio/HA Parents)
- `Lane E: Radio/Media` -> `active`

## Manuelle Unblock-Punkte

### `workspace_drift_guard` [WATCH]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: Alle Agenten arbeiten dauerhaft im selben FraWo-Projekt und koordinieren ueber Repo-Dateien statt ueber verstreute Workspaces.
- `current_state`: `C:\Users\Admin\Workspace\Repos\FraWo` ist kanonisch; `C:\Users\Admin\Workspace\FraWo` und `C:\WORKSPACE\FraWo` sind Junctions dorthin; Agentenvertrag und Board sind im Repo.
- `next_operator_action`: Alte Fenster/IDE-Sessions moeglichst auf `C:\Users\Admin\Workspace\Repos\FraWo` neu oeffnen.
- `next_codex_action`: Bei kuenftigen Starts `scripts/workspace/audit_workspaces.ps1` laufen lassen, bevor grosse Arbeiten beginnen.

### `github_main_branch_protection` [DONE]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#15`
- `goal`: GitHub CLI authentifizieren und solo-safe Branch Protection fuer `main` anwenden.
- `current_state`: `gh` ist installiert; Git Credential Manager kann als temporaerer `GH_TOKEN` genutzt werden; solo-safe Branch Protection ist auf `main` aktiv.
- `verified`: Force-push deaktiviert, Branch-Loeschung deaktiviert, Conversation Resolution aktiviert.
- `next_operator_action`: Keine.
- `next_codex_action`: Issue `#15` schliessen und kuenftig `scripts/github/bootstrap_professional_github.ps1 -UseGitCredentialManager` fuer Bootstrap/Audit verwenden.

### `post_restore_backup_proof` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#9`
- `goal`: Nach CT-100-Restore, Caddy-Fixes und Firewall-Aenderungen wieder einen nachweisbaren Sicherungsstand erzeugen.
- `current_state_2026-05-31`: PBS 4.2 aktiv (VM 240, 10.4.0.25). Datastore local-backups (500GB /mnt/pbs-data). In PVE als pbs-frawo (API-Token pve@pbs!pve-token). Backup-Job daily-all-pbs 02:00 aktiv. Prune: 7d/4w/3m. rclone Google Drive Sync 05:00 -> gdrive:pbs-backups. Sync-Script mit Rate-Limit-Handling und ssd2tb-Fallback: `scripts/pbs_rclone_gdrive_sync.sh`. ansible/inventory/host_vars/pbs.yml auf aktuellen Stand gebracht. ssd2tb INACTIVE (I/O-Error) - Fallback-Pfad im Script vorbereitet, aber Hardware muss geprueft werden.
- `next_operator_action`: (1) Ersten manuellen Backup-Test starten: PVE -> Datacenter -> Backup -> daily-all-pbs -> Run Now. (2) PBS Root-Passwort in Vaultwarden speichern. (3) ssd2tb (/mnt/ssd2tb) auf I/O-Error pruefen (dmesg, smartctl).
- `next_codex_action`: Nach erstem gruenen Backup: `scripts/proxmox_pbs_restore_proof.sh` ausfuehren (Restore-Test VM 220 -> VMID 920). Nach ssd2tb-Freigabe: `PBS_DATASTORE_PATH=/mnt/pbs-data scripts/pbs_rclone_gdrive_sync.sh` testen.

### `vm_firewall_hardening_reapply` [DONE]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#8`
- `goal`: VM 210 und VM 220 haerten, ohne CT 100 -> HA/Odoo zu brechen.
- `current_state`: `firewall=0` bleibt auf PVE-Ebene bewusst gesetzt. Der Aktivierungsversuch 2026-05-31 hat erneut gezeigt, dass die Proxmox-VM-Firewall CT100 -> HA/Odoo stoert. Die abgesicherte Zielarchitektur ist deshalb dokumentiert als OS-Level/UCG-Hardening statt Re-Enable der PVE-VM-Firewall.
- `verified_2026-05-31`: Laufzeitdienste bleiben gruen (`ha.hs27.internal`, `odoo.hs27.internal`) und `DOCS/PROXMOX_PVE_ARCHITECTURE.md` dokumentiert `firewall=0` auf VM 210/220 als bewusstes Betriebsmodell wegen asymmetrischem conntrack zwischen CT100/veth und VM/tap.
- `next_operator_action`: Keine.
- `next_codex_action`: GitHub Issue `#8` als dokumentierte Architekturentscheidung schliessen.

### `pve_host_exposure_audit` [DONE]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#13`
- `goal`: NFS/RPC/SSH/PVE-UI Exposure des Proxmox Hosts auf notwendige Netze begrenzen.
- `fixed_2026-05-31`: socat:18069 (Odoo-Proxy) auf Tailscale-IP gebunden. netdata:19999 auf 127.0.0.1+Tailscale. node-exporter:9100 auf 127.0.0.1. NFS-Export /mnt/wolf-ee nur fuer 100.91.20.116 (Stockenweiler) - OK.
- `exposure_model`: Host-Management nur ueber vertrauenswuerdige LAN/Tailscale-Pfade; Metrics lokal/Tailscale-only; NFS nur fuer expliziten Storage-Consumer.
- `next_operator_action`: Keine.


### `openclaw_key_rotation_after_repo_cleanup` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#7`
- `goal`: OpenClaw SSH-Key rotieren, weil der alte private Key historisch im GitHub-Repo enthalten war.
- `current_state`: Key ist aus dem aktuellen Repo-HEAD entfernt und per `.gitignore` blockiert; historische Git-Exposition bleibt als Sicherheitsbefund bestehen.
- `next_operator_action`: Kurzes Rotationsfenster freigeben.
- `next_codex_action`: Neuen Key erzeugen, PVE/Stock/autorisierten Zugriff aktualisieren, lokalen Secret-Pfad ersetzen, alten Public Key aus `authorized_keys` entfernen und Zugriff testen.

### `split_dns_finalization` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#12`
- `goal`: `hs27.internal` loest sauber ohne Windows Hosts-Datei.
- `blocked_by`: Tailscale Admin-Aktion (DNS-Eintrag veraltet).
- `current_state_2026-05-31`: Tailscale-Admin-DNS zeigt noch auf alte Toolbox-LAN-IP `10.1.0.20` (Netz migriert; CT 100 ist jetzt `10.4.0.20`). Windows Hosts-Datei Workaround (`scripts/tools/Update-HS27-DNS-Aliases.ps1`) aktiv.
- `next_operator_action`: Tailscale Admin -> `https://login.tailscale.com/admin/dns` -> restricted nameserver fuer `hs27.internal` von `10.1.0.20` auf `10.4.0.20` aendern (oder Tailscale-IP `100.82.26.53` falls CT 100 Tailscale hat). Route `10.4.0.0/24` vorher approven falls noch ausstehend.
- `next_codex_action`: Nach Admin-Schritt: `nslookup portal.hs27.internal`, `odoo`, `cloud`, `vault`, `ha`, `paperless`, `media` gegen `100.100.100.100` pruefen; danach Hosts-Datei-Workaround entfernen oder deaktivieren.

### `nextcloud_desktop_https_callback` [DONE]

- `lane`: `Lane B/C: Website/Public + Security/PBS/Infra`
- `github_issue`: `#10`
- `goal`: Nextcloud Desktop Client Login ueber `https://cloud.hs27.internal` wieder verbinden.
- `verified_2026-05-31`: Nextcloud Desktop Client laeuft (Prozess aktiv), N: Laufwerk gemappt, cloud.frawo-tech.de antwortet 302. Verbindung funktioniert.
- `next_operator_action`: GitHub Issue `#10` schliessen.

### `ct100_storage_migration` [WATCH]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#14`
- `goal`: CT 100 Disk kontrolliert auf `ssd2tb` migrieren.
- `current_state`: CT 100 laeuft wieder; Migration bleibt sinnvoll, um NVMe/local-lvm Druck zu reduzieren, braucht aber ein kurzes Downtime-Fenster fuer Toolbox/Caddy.
- `next_operator_action`: Wartungsfenster fixieren, davor Snapshot/Backup ziehen, dann CT100 kontrolliert auf `ssd2tb` migrieren und nach dem Boot Caddy, AdGuard, Jellyfin sowie alle Frontdoors verifizieren.

### `odoo_project_ssot_sync` [DONE]

- `lane`: `Lane A/C`
- `goal`: Odoo Masterprojekt und Repo-SSOT spiegeln denselben Stand (auf Deutsch).
- `current_state`: `scripts/business/odoo_ssot_sync.py` erstellt und gepusht (2026-05-30). Projekt "🚀 Homeserver 2027: Masterplan" (id=1) mit 16 Tasks in Backlog angelegt, Sprache de_DE gesetzt, Board-Stages korrekt. Wolf (uid=6) ist aktiver Admin-Benutzer.
- `next_operator_action`: Keine.

### `odoo_sender_email_for_document_mail` [DONE]

- `lane`: `Lane A: MVP Closeout`
- `github_issue`: `#11`
- `goal`: Odoo kann Angebots-/Auftragsmails und Storno-Mails mit gueltiger Absenderadresse senden.
- `observed`: Beim Stornieren von Angebot `S00001` erscheint `Ungueltiger Vorgang`: Die Nachricht kann nicht gesendet werden, weil die E-Mail-Adresse des Absenders nicht konfiguriert ist.
- `root_cause_verified`: Angebote `S00001` und `S00002` nutzen `wolf@frawo-tech.de` als Verkaeufer, aber der zugehoerige Odoo-Partner hatte keine E-Mail-Adresse.
- `server_fix_2026-04-22`: Odoo-Partner fuer `wolf@frawo-tech.de` auf `wolf@frawo-tech.de` gesetzt; technischer `admin` auf `noreply@frawo-tech.de` gesetzt; Odoo-Webcontainer neu gestartet.
- `verification_2026-04-22`: Odoo rendert die Storno-Mail-Vorlage fuer `S00001` jetzt mit `"Wolf Admin" <wolf@frawo-tech.de>` als `email_from`; Caddy-Frontdoor `odoo.hs27.internal/web/login` antwortet `HTTP 200`.
- `verified_2026-05-30`: S00001 storniert/entfernt, S00002 invoiced. SMTP-Config aktiv (Strato smtp.strato.de, webmaster@frawo-tech.de). Fix von 2026-04-22 greift. GitHub Issue #11 schliessen.
- `next_operator_action`: Keine.

### `odoo_acl_res_users_log` [WATCH]

- `lane`: `Lane A`
- `goal`: Odoo ACL-Warnings auf `res.users.log` klaeren.
- `next_codex_action`: Odoo-App-Layer pruefen, keine Infra-Mutation.

### `radio_frontdoor_backend` [DONE]

- `lane`: `Lane E: Radio/Media`
- `goal`: funk.frawo-tech.de als Community-Radiosite (Abstimmung, Chat, Song-Wunsch).
- `verified_2026-05-31`:
  - https://funk.frawo-tech.de/ public HTTPS 200 via CF-Tunnel -> 100.78.88.33:9501
  - https://navidrome.frawo-tech.de/ public HTTPS 200 via CF-Tunnel -> 100.78.88.33:4533
  - Song-Requests aktiviert (AzuraCast enable_requests=true), API-Key genutzt, Suche laeuft
  - Art-URLs public (kein internes 172.20.0.1), Now-Playing, Voting, Chat alles verifiziert
- `next_operator_action`: Keine.
- `deployment_note`: Docker-Build-Context ist /opt/frawo-radio-backend/app/ (nicht apps/radio-backend/). Nach git-Pull sync: cp apps/radio-backend/app/api/community.py app/api/community.py

### `ha_eltern_dashboard` [ACTIVE]

- `lane`: `Lane D: Stockenweiler`
- `goal`: Spezielles Dashboard fÃ¼r Wolfs Eltern (ZDF/ARD Mediatheken, Strom).
- `current_state`: HA Eltern VM 360 lÃ¤uft auf `192.168.178.179`.
- `next_codex_action`: Dashboard YAML-Entwurf erstellen (Mediathek iFrames).

### `onkyo_avr390_setup` [ACTIVE]

- `lane`: `Lane D: Stockenweiler` (oder Anker-HW)
- `goal`: Onkyo AV R390 professionell einrichten und dokumentieren (Patching, Signalfluss, Geraeteeinstellungen) - Werkstattqualitaet.
- `current_state`: Geraet angeschlossen, Einmessung erledigt. Naechster Schritt: saubere Verkabelung + vollstaendige Dokumentation.
- `next_operator_action`: Kabel beschriften, Patchplan aufnehmen (Foto + Text).
- `next_codex_action`: Dokumentationsvorlage erstellen (Standard-Patchplan-Template fuer AV-Receiver). Odoo-Task angelegt.

### `website_access_protection` [PROPOSED]

- `lane`: `Lane B: Website/Public`
- `goal`: "Halb fertige" Seite vor der Ã–ffentlichkeit schÃ¼tzen, aber fÃ¼r Wolf/Franz sichtbar lassen.
- `next_operator_action`: Entscheidung Ã¼ber Cloudflare Access (Login-Schutz).

## Kanonische Steuerdateien

- `LIVE_CONTEXT.md`
- `MASTERPLAN.md`
- `OPS_HOME.md`
- `AI_OPERATING_MODEL.md`
- `AI_SERVER_HANDOFF.md`
- `manifests/work_lanes/current_plan.json`
- `artifacts/release_mvp_gate/latest_release_mvp_gate.md`

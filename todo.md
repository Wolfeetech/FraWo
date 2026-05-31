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
- `current_state_2026-05-30`: PBS 4.2 installiert (10.4.0.25), SSH-Key deployed, Datastore local-backups (500GB /mnt/pbs-data) angelegt. In PVE als pbs-frawo eingebunden (API-Token pve@pbs!pve-token). Backup-Job daily-all-pbs 02:00 fuer alle VMs/CTs aktiv. Prune: 7d/4w/3m. rclone Google Drive Sync taeglich 05:00 nach gdrive:pbs-backups. ssd2tb INACTIVE (I/O-Error, Hardware pruefen).
- `next_operator_action`: Ersten manuellen Backup-Test starten: PVE -> Datacenter -> Backup -> daily-all-pbs -> Run Now. PBS Root-Passwort in Vaultwarden speichern.
- `next_codex_action`: Nach erstem Backup: Restore-Test an einer VM durchfuehren (Backup-Proof). ssd2tb Hardware untersuchen.

### `vm_firewall_hardening_reapply` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#8`
- `goal`: VM 210 und VM 220 wieder mit sauber getesteter Proxmox-Firewall betreiben, ohne CT 100 -> HA/Odoo zu brechen.
- `current_state`: `firewall=0` auf VM 210 und VM 220, weil `firewall=1` im Test CT100-Verkehr geblockt hat.
- `next_operator_action`: Keine manuelle Aktion noetig, aber Reaktivierung nur als bewusstes Wartungsfenster freigeben.
- `next_codex_action`: Regelpfad mit tcpdump/counters testen, ICMP/TCP fuer interne Frontdoor erlauben, dann erst produktiv setzen.

### `pve_host_exposure_audit` [ACTIVE]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#13`
- `goal`: NFS/RPC/SSH/PVE-UI Exposure des Proxmox Hosts auf notwendige Netze begrenzen.
- `observed`: NFS/RPC Ports lauschen auf `0.0.0.0`; Cluster-Firewall ist aktiv, aber Host-Service-Exposure braucht explizite Pruefung.
- `next_codex_action`: Host-Firewall-Regeln und NFS-Bind/Export-Modell pruefen, ohne Storage-Node-Betrieb zu brechen.


- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#7`
- `current_state`: Key ist aus dem aktuellen Repo-HEAD entfernt und per `.gitignore` blockiert; historische Git-Exposition bleibt als Sicherheitsbefund bestehen.
- `next_operator_action`: Kurzes Rotationsfenster freigeben.
- `next_codex_action`: Neuen Key erzeugen, PVE/Stock/autorisierten Zugriff aktualisieren, lokalen Secret-Pfad ersetzen, alten Public Key aus `authorized_keys` entfernen und Zugriff testen.

### `split_dns_finalization` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#12`
- `goal`: `hs27.internal` loest sauber ohne Windows Hosts-Datei.
- `blocked_by`: UniFi/Tailscale Admin-Aktion.
- `next_operator_action`: UniFi DNS bzw. Tailscale restricted nameserver fuer `hs27.internal` final setzen.
- `next_codex_action`: Danach `dig/nslookup` gegen `portal`, `odoo`, `cloud`, `vault`, `ha`, `paperless`, `media` pruefen.

### `nextcloud_desktop_https_callback` [ACTIVE]

- `lane`: `Lane B/C: Website/Public + Security/PBS/Infra`
- `github_issue`: `#10`
- `goal`: Nextcloud Desktop Client Login ueber `https://cloud.hs27.internal` wieder verbinden.
- `observed`: Desktop Client meldet, dass die vom Server zurueckgegebene Server-URL nicht mit HTTPS beginnt, obwohl die Anmeldung per HTTPS gestartet wurde.
- `likely_cause`: Nextcloud erkennt Caddy/CT100 nicht sauber als HTTPS-Reverse-Proxy; vermutlich fehlen oder passen `overwriteprotocol`, `overwritehost`, `overwrite.cli.url` oder `trusted_proxies` in der Nextcloud-Konfiguration.
- `next_operator_action`: Login im Desktop Client nach Fix erneut starten.
- `next_codex_action`: Nextcloud `config.php` pruefen, Caddy-Proxy-IP `10.1.0.20` als trusted proxy setzen, HTTPS-Overwrite auf `cloud.hs27.internal` korrigieren, Web/PHP-Dienst neu laden und Desktop-Client-Login testen.

### `ct100_storage_migration` [WATCH]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#14`
- `goal`: CT 100 Disk kontrolliert auf `ssd2tb` migrieren.
- `current_state`: CT 100 laeuft wieder, aber Migration bleibt sinnvoll, um NVMe/local-lvm Druck zu reduzieren.
- `next_operator_action`: Kurzes Wartungsfenster fuer Toolbox/Caddy-Downtime freigeben.

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

### `radio_frontdoor_backend` [ACTIVE]

- `lane`: `Lane E: Radio/Media`
- `goal`: `radio.frawo-tech.de` Ã¼ber AzuraCast (Stockenweiler) bereitstellen.
- `current_state`: AzuraCast VM 210 lÃ¤uft auf `192.168.178.210`.
- `next_operator_action`: Cloudflare Tunnel Routing fÃ¼r `radio.frawo-tech.de` hinzufÃ¼gen.
- `next_codex_action`: AzuraCast Konfiguration validieren und Stream-Test durchfÃ¼hren.

### `ha_eltern_dashboard` [ACTIVE]

- `lane`: `Lane D: Stockenweiler`
- `goal`: Spezielles Dashboard fÃ¼r Wolfs Eltern (ZDF/ARD Mediatheken, Strom).
- `current_state`: HA Eltern VM 360 lÃ¤uft auf `192.168.178.179`.
- `next_codex_action`: Dashboard YAML-Entwurf erstellen (Mediathek iFrames).

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

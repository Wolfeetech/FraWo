# Operator Todo Queue

Stand: `2026-04-22`

## Zweck

Diese Datei ist die kurze manuelle Unblock-Queue. Strategische Wahrheit steht im `MASTERPLAN.md`, Laufzeitwahrheit in `LIVE_CONTEXT.md`, maschinenlesbare Planung in `manifests/work_lanes/current_plan.json`.

## Lane Status

- `Lane A: MVP Closeout` -> `sealed`
- `Lane B: Website/Public` -> `active`
- `Lane C: Security/PBS/Infra` -> `active`
- `Lane D: Stockenweiler` -> `watch`
- `Lane E: Radio/Media` -> `active/watch`

## Manuelle Unblock-Punkte

### `post_restore_backup_proof` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: Nach CT-100-Restore, Caddy-Fixes und Firewall-Aenderungen wieder einen nachweisbaren Sicherungsstand erzeugen.
- `next_operator_action`: Wartungsfenster bestaetigen, falls ein grosser Backup-/Restore-Proof laenger laufen darf.
- `next_codex_action`: Backup-Ziel pruefen, `ssd2tb` Fallback einrichten, rclone-Rate-Limit beruecksichtigen und Proof dokumentieren.

### `vm_firewall_hardening_reapply` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: VM 210 und VM 220 wieder mit sauber getesteter Proxmox-Firewall betreiben, ohne CT 100 -> HA/Odoo zu brechen.
- `current_state`: `firewall=0` auf VM 210 und VM 220, weil `firewall=1` im Test CT100-Verkehr geblockt hat.
- `next_operator_action`: Keine manuelle Aktion noetig, aber Reaktivierung nur als bewusstes Wartungsfenster freigeben.
- `next_codex_action`: Regelpfad mit tcpdump/counters testen, ICMP/TCP fuer interne Frontdoor erlauben, dann erst produktiv setzen.

### `pve_host_exposure_audit` [ACTIVE]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: NFS/RPC/SSH/PVE-UI Exposure des Proxmox Hosts auf notwendige Netze begrenzen.
- `observed`: NFS/RPC Ports lauschen auf `0.0.0.0`; Cluster-Firewall ist aktiv, aber Host-Service-Exposure braucht explizite Pruefung.
- `next_codex_action`: Host-Firewall-Regeln und NFS-Bind/Export-Modell pruefen, ohne Storage-Node-Betrieb zu brechen.

### `openclaw_key_rotation_after_repo_cleanup` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: OpenClaw SSH-Key rotieren, weil der alte private Key historisch im GitHub-Repo enthalten war.
- `current_state`: Key ist aus dem aktuellen Repo-HEAD entfernt und per `.gitignore` blockiert; historische Git-Exposition bleibt als Sicherheitsbefund bestehen.
- `next_operator_action`: Kurzes Rotationsfenster freigeben.
- `next_codex_action`: Neuen Key erzeugen, PVE/Stock/autorisierten Zugriff aktualisieren, lokalen Secret-Pfad ersetzen, alten Public Key aus `authorized_keys` entfernen und Zugriff testen.

### `split_dns_finalization` [BLOCKED]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: `hs27.internal` loest sauber ohne Windows Hosts-Datei.
- `blocked_by`: UniFi/Tailscale Admin-Aktion.
- `next_operator_action`: UniFi DNS bzw. Tailscale restricted nameserver fuer `hs27.internal` final setzen.
- `next_codex_action`: Danach `dig/nslookup` gegen `portal`, `odoo`, `cloud`, `vault`, `ha`, `paperless`, `media` pruefen.

### `nextcloud_desktop_https_callback` [ACTIVE]

- `lane`: `Lane B/C: Website/Public + Security/PBS/Infra`
- `goal`: Nextcloud Desktop Client Login ueber `https://cloud.hs27.internal` wieder verbinden.
- `observed`: Desktop Client meldet, dass die vom Server zurueckgegebene Server-URL nicht mit HTTPS beginnt, obwohl die Anmeldung per HTTPS gestartet wurde.
- `likely_cause`: Nextcloud erkennt Caddy/CT100 nicht sauber als HTTPS-Reverse-Proxy; vermutlich fehlen oder passen `overwriteprotocol`, `overwritehost`, `overwrite.cli.url` oder `trusted_proxies` in der Nextcloud-Konfiguration.
- `next_operator_action`: Login im Desktop Client nach Fix erneut starten.
- `next_codex_action`: Nextcloud `config.php` pruefen, Caddy-Proxy-IP `10.1.0.20` als trusted proxy setzen, HTTPS-Overwrite auf `cloud.hs27.internal` korrigieren, Web/PHP-Dienst neu laden und Desktop-Client-Login testen.

### `ct100_storage_migration` [WATCH]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: CT 100 Disk kontrolliert auf `ssd2tb` migrieren.
- `current_state`: CT 100 laeuft wieder, aber Migration bleibt sinnvoll, um NVMe/local-lvm Druck zu reduzieren.
- `next_operator_action`: Kurzes Wartungsfenster fuer Toolbox/Caddy-Downtime freigeben.

### `odoo_project_ssot_sync` [ACTIVE]

- `lane`: `Lane A/C`
- `goal`: Odoo Masterprojekt und Repo-SSOT spiegeln denselben Stand.
- `next_codex_action`: Odoo Masterprojekt mit den aktuellen Lane-/Projektaufgaben synchronisieren.

### `odoo_sender_email_for_document_mail` [ACTIVE]

- `lane`: `Lane A: MVP Closeout`
- `goal`: Odoo kann Angebots-/Auftragsmails und Storno-Mails mit gueltiger Absenderadresse senden.
- `observed`: Beim Stornieren von Angebot `S00001` erscheint `Ungueltiger Vorgang`: Die Nachricht kann nicht gesendet werden, weil die E-Mail-Adresse des Absenders nicht konfiguriert ist.
- `likely_cause`: Benutzer-, Firmen- oder Mail-Alias-Absender in Odoo ist leer bzw. nicht mit dem ausgehenden Mailserver abgestimmt.
- `next_operator_action`: Gewuenschte produktive Absenderadresse bestaetigen, z. B. `office@frawo-tech.de`.
- `next_codex_action`: Odoo Firma/User/Mail-Alias und ausgehenden Mailserver pruefen, Sender-Adresse setzen, Testmail/Angebotsmail senden und danach Storno-Workflow erneut testen.

### `odoo_acl_res_users_log` [WATCH]

- `lane`: `Lane A`
- `goal`: Odoo ACL-Warnings auf `res.users.log` klaeren.
- `next_codex_action`: Odoo-App-Layer pruefen, keine Infra-Mutation.

### `radio_frontdoor_backend` [BLOCKED]

- `lane`: `Lane E: Radio/Media`
- `goal`: `radio.hs27.internal` erst dann produktiv machen, wenn ein echter Backend-Service verfuegbar ist.
- `current_state`: Media/Jellyfin ist gruen; Radio ist kein verifizierter Produktivpfad.

## Kanonische Steuerdateien

- `LIVE_CONTEXT.md`
- `MASTERPLAN.md`
- `OPS_HOME.md`
- `AI_OPERATING_MODEL.md`
- `AI_SERVER_HANDOFF.md`
- `manifests/work_lanes/current_plan.json`
- `artifacts/release_mvp_gate/latest_release_mvp_gate.md`

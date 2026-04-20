# Operator Todo Queue

Stand: `2026-04-07`

## Zweck

Diese Datei ist ab jetzt nur noch die kurze manuelle Unblock-Queue.

Keine zweite Projektplanung, keine erledigte Historie, keine Nebenstrang-Roadmaps.
Der aktive Arbeitsfokus liegt in `Lane A: MVP Closeout`.

## Professional-Autopilot Regeln

- Default-Modell: `Aggressive Autopilot`
- `Codex` fuehrt
- `Gemini` prueft sichtbar
- der Operator entscheidet nur an echten Pflicht-Stopps

Pflicht-Stopp vor:

- `Infra/Public`
- `Netzwerk`
- `Datenmigration`
- `Storage/PBS`
- `Router`
- `HA/PVE`
- `Security-Boundary`
- lokalen Windows-Admin-Token-Eingriffen

Alles andere laeuft standardmaessig im Loop:

1. Truth sammeln
2. professionell beurteilen
3. Aenderung klassifizieren
4. ausfuehren oder eskalieren
5. verifizieren
6. SSOT aktualisieren

## Lane Status

- `Lane A: MVP Closeout` -> `active`
- `Lane B: Website/Public` -> `DONE` (Branding & SEO finalized)
- `Lane C: Security/Infra` -> `PASSED` (PBS restored, 1.8TB HW integrated)
- `Lane D: Stockenweiler` -> `PASSED` (Nextcloud 100GB Migration complete)
- `Lane E: Radio/Media` -> `active` (Identified in VM 220)

## Manuelle Unblock-Punkte

### `device_rollout_verified` [PARTIAL]

- `lane`: `Lane A: MVP Closeout`
- `goal`: Franz `Surface Laptop` und `iPhone` sind sichtbar als releasede MVP-Geraete abgenommen.
- `status`: iPhone ist verifiziert. Surface Laptop ist durch **Google 2FA** blockiert.
- `next_operator_action`: Erst den blockierten `2FA`-Pfad nach dem verlorenen Smartphone wiederherstellen, dann Surface Laptop prüfen.
- `next_codex_action`: Sobald 2FA unblocked: `python scripts/device_rollout_preflight.py`.

### `surface_go_kiosk_mode_verified` [X]

- `lane`: `Lane B: Website/Public Hold`
- `goal`: Tablet-UI; Lockdown; Kiosk-Autostart
- `next_codex_action`: Monitor usage metrics on next operator login.

### `vaultwarden_recovery_material_verified` [DONE]

- `lane`: `Lane A: MVP Closeout`
- `goal`: `Vaultwarden`-Recovery-Material existiert offline in zwei getrennten physischen Kopien.
- `done_when`: Zwei getrennte Offline-Kopien sind real vorhanden und frisch sichtbar nachgewiesen.
- `last_status`: `passed` (verifiziert via `!go` am 2026-04-07)

### `tailscale_route_approved_10_1_0_0_24`

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: Tailnet-Subnet-Route fuer `10.1.0.0/24` ist im Tailscale-Adminpanel freigeschaltet.
- `done_when`: Tailscale-Admin zeigt die Route als aktiv; Remote-Clients erreichen `10.1.0.20:80` und `10.1.0.20:53`.
- `blocked_by`: Route ist nur beworben, aber noch nicht im Tailnet freigegeben.
- `next_operator_action`: In `https://login.tailscale.com/admin/machines` die Route `10.1.0.0/24` bei `toolbox` approven.
- `next_codex_action`: Nach der Freigabe `tailscale status` + `dig @10.1.0.20 ha.hs27.internal` verifizieren.

### `tailscale_split_dns_update`

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: Split-DNS fuer `hs27.internal` nutzt `10.1.0.20` als restricted nameserver.
- `done_when`: `100.100.100.100` liefert `ha.hs27.internal` auf `10.1.0.20`.
- `next_operator_action`: In `https://login.tailscale.com/admin/dns` den restricted nameserver fuer `hs27.internal` auf `10.1.0.20` umstellen.

## Nicht In Dieser Queue

- `Lane B: Website/Public Hold` bleibt sichtbar, aber ohne neue Go-Live-Arbeit.
- `Lane C: Security/PBS/Infra` bleibt sichtbar, aber nur fuer Regressionen und Reapply-Pfade.
- `Lane D: Stockenweiler` bleibt sichtbar, aber ohne Live-Rollout.
- `Lane E: Radio/Media` bleibt im Erhaltungsmodus ohne Ausbau.

## Kanonische Steuerdateien

- `AI_OPERATING_MODEL.md` fuer das verbindliche AI-Arbeitsmodell
- `AI_SERVER_HANDOFF.md` fuer externen KI-Handoff
- `MASTERPLAN.md` fuer die strategische Lane-Reihenfolge
- `artifacts/release_mvp_gate/latest_release_mvp_gate.md` als einzige Wahrheit fuer die MVP-Entscheidung
- `manifests/work_lanes/current_plan.json` als maschinenlesbare Lane-Quelle

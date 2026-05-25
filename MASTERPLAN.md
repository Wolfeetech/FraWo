# MASTERPLAN - FraWo Homeserver 2027

Dieses Dokument ist das zentrale Strategiepapier fuer Aufbau und Betrieb des FraWo Homeservers 2027 an den Standorten Anker und Stockenweiler. Es definiert die aktiven Lanes, die technische Wahrheit und die naechsten Freigabeschritte.

---

## 1. Vision & Strategie

Der Homeserver 2027 ist die produktive Basis der **FraWo GbR**: ERP, Cloud, Dokumente, Vault, Medien, Backups und kontrollierte AI-/Agentenarbeit laufen unter einem gemeinsamen SSOT. Der Standard ist: interne Stabilitaet zuerst, dann oeffentliche Freigabe nur ueber gehaerteten Edge-Pfad.

## 2. Work Lanes

### Lane A: OpenClaw Agent & Control - [STATUS: ACTIVE]

- **Ziel**: Autonomer Project-Lead für die FraWo Infrastruktur.
- **Status**: V3.1 Agentic active. Multi-turn ReAct loops operational.
- **Features**: Odoo Sync, Autonomous Remediation, Safety Guardian.

### Lane B: Website & Public Activation - [STATUS: ACTIVE/PROV]

- **Ziel**: `www.frawo-tech.de` über Cloudflare Tunnel freigeben (technisch erledigt).
- **Status**: HTTPS ist aktiv. Content ist noch im Aufbau ("halb fertig").
- **Wichtig**: Optionale Cloudflare Access Rule für Baustellen-Schutz geplant.

### Lane C: Security, Backup & Infrastructure - [STATUS: ACTIVE]

- **Ziel**: Restore-Zustand absichern, Backups beweisen, DNS finalisieren und Storage nachhaltig machen.
- **Status**: hoechste operative Prioritaet nach dem CT-100-Restore.
- **Aktive Projekte**:
  - VM 210/220 Firewall-Hardening korrekt testen, bevor `firewall=1` wieder produktiv wird
  - PVE host NFS/RPC exposure auf vertrauenswuerdige interne Netze begrenzen
  - rclone rate-limit/backoff und lokales `ssd2tb` Backup-Fallback einrichten
  - CT 100 Disk kontrolliert von NVMe/local-lvm auf `ssd2tb` migrieren
  - UniFi/Tailscale Split-DNS finalisieren
  - Stockenweiler-Monitoringpfad wieder auf einen echten Metrics-Sink ziehen; `outputs.discard` auf `pve-stock` ist nur die sichere Zwischenmassnahme nach dem Swap-Fix

### Lane D: Stockenweiler Integration - [STATUS: BLOCKED/PHYSICAL]

- **Ziel**: Zweiter Standort für Radio (AzuraCast) und Eltern-Support (HA).
- **Status**: Blockiert, weil Stockenweiler physisch offline ist (Power-On vor Ort erforderlich).
- **Runtime 2026-05-03**: Host-Swap wieder `0.0GiB / 8.0GiB`. Root Cause war nicht AzuraCast selbst, sondern `telegraf`, das mehrere GiB Metriken gegen das tote Ziel `192.168.178.168:8086` gepuffert hat.
- **Running Services**: AzuraCast VM `210`, Home Assistant Eltern VM `360`, Vaultwarden CT `108`, AdGuard CT `101`. `PBS` (`109`) und `n8n` (`110`) sind aktuell nicht der laufende Arbeitspfad.
- **Aktion**: Physischer Start + Tailscale-Liveness prüfen; danach Monitoring-Sink sauber wiederherstellen und VM-Rightsizing anhand frischer Daten entscheiden.

### Lane E: Radio & Media - [STATUS: ACTIVE/BLOCKED BY LANE D]

- **Ziel**: AzuraCast auf Stockenweiler als primärer Radio-Service, Anker als Relay/Backup.
- **Status**: In Migration/Setup. IP `192.168.178.210`.
- **Roadmap**:
  1. [ ] AzuraCast Core-Dienste auf Stockenweiler VM 210 absichern.
  2. [ ] Media-Library Sync via Tailscale (rclone).
  3. [ ] Icecast Relay auf Anker für Redundanz konfigurieren.
  4. [ ] Integration in das Odoo-CRM für Supporter-Management.

### Operativer Fokus 2026-05-25 (Umsetzungspaket)

1. [ ] Cloudflare-Tunnel für `cloud.frawo-tech.de` auf `http://10.4.0.21` korrigieren und extern gegen `502` verifizieren.
2. [ ] Stockenweiler physisch einschalten, dann Tailscale/Service-Liveness bestätigen.
3. [ ] `/mnt/hs27-media` Kapazitätsdruck abbauen (Cleanup oder Erweiterung) und Restkapazität dokumentieren.
4. [ ] PBS/aktive VMs nach RAM/Swap-Lage rightsizen, um Freeze-Risiko zu reduzieren.
5. [ ] Rollen für `frawo-docker-1` und StudioPC verbindlich festlegen.
6. [ ] Nach Wiederfreigabe von Lane D die Radio-Migration auf CT 130 fortsetzen.
7. [ ] Jede abgeschlossene Aktion in Odoo (SSOT) und Repo-Dokumenten spiegeln.

---

## 3. Infrastruktur & Routing

### Netzwerk-Wahrheit

- Primaeres Netz: `10.4.0.0/24`
- Gateway: UCG-Ultra `10.4.0.1`
- Toolbox / Frontdoor: CT 100 `10.4.0.20`, Tailscale `100.82.26.53`
- DNS: AdGuard auf CT 100/101, langfristig ueber UniFi/Tailscale Split-DNS statt Windows Hosts-Datei
- Reverse Proxy: Caddy in CT 100
- TLS intern: Caddy internal CA fuer `*.hs27.internal`

### Aktuelle Topologie 2026-04-22

| ID  | Typ | Dienst                               | IP               | Status         |
| --- | --- | ------------------------------------ | ---------------- | -------------- |
| 100 | CT  | Toolbox / Caddy / AdGuard / Jellyfin | `10.4.0.20`      | LIVE           |
| 101 | CT  | AdGuard Slave                        | `10.4.0.101`     | LIVE           |
| 110 | CT  | Storage Node / SMB / NFS             | `10.4.0.30`      | LIVE           |
| 120 | CT  | Vaultwarden                          | `10.4.0.26:8080` | LIVE           |
| 200 | VM  | Nextcloud                            | `10.4.0.21:80`   | LIVE           |
| 210 | VM  | Home Assistant OS                    | `10.4.0.24:8123` | LIVE           |
| 220 | VM  | Odoo / Website Origin                | `10.4.0.22:8069` | LIVE           |
| 230 | VM  | Paperless                            | `10.4.0.23:8000` | LIVE           |
| 240 | VM  | PBS                                  | `10.4.0.x`       | watch / verify |

### Caddy Frontdoors

| Domain                    | Backend             | Status                             |
| ------------------------- | ------------------- | ---------------------------------- |
| `portal.hs27.internal`    | local `/srv/portal` | `HTTP 200`                         |
| `odoo.hs27.internal`      | `10.4.0.22:8069`    | `HTTP 200`                         |
| `vault.hs27.internal`     | `10.4.0.26:8080`    | `HTTP 200`                         |
| `ha.hs27.internal`        | `10.4.0.24:8123`    | `HTTP 200`                         |
| `cloud.hs27.internal`     | `10.4.0.21:80`      | `HTTP 302` login/HTTPS redirect    |
| `paperless.hs27.internal` | `10.4.0.23:8000`    | `HTTP 302` login redirect          |
| `media.hs27.internal`     | `10.4.0.20:8096`    | `HTTP 302` Jellyfin login redirect |

---

## 4. Restore Notes 2026-04-22

- CT 100 was restored and Caddy stack rebuilt.
- Odoo outage root cause: VM 220 Proxmox NIC firewall blocked CT 100 to `10.4.0.22:8069`.
- HAOS had the same VM-level firewall problem on VM 210.
- Temporary service-safe state: VM 210 and VM 220 `net0 firewall=0`.
- Security follow-up: re-enable only after a tested bridge/firewall design proves CT 100 traffic still reaches Odoo and HAOS.
- Vaultwarden Caddy upstream was wrong: service is `10.4.0.26:8080`, not `:80`.
- HAOS Caddy frontdoor was missing and is now `ha.hs27.internal -> 10.4.0.24:8123`.
- Jellyfin frontdoor is now `media.hs27.internal -> 10.4.0.20:8096`; `localhost` is wrong from inside the Caddy container.
- rclone Google Drive mount is active; API quota/rate limits were observed during backup traffic.

### Runtime Note 2026-05-03

- `pve-stock` lief in einen Host-Swap-Notfall, weil `telegraf` ueber Tage mehrere GiB Metriken gegen das unerreichbare InfluxDB-Ziel `http://192.168.178.168:8086` gepuffert hat.
- Remediation: `telegraf` gestoppt, `outputs.influxdb` in `/etc/telegraf/telegraf.conf` temporaer auf `outputs.discard` umgestellt, Originalkonfiguration nach `/etc/telegraf/telegraf.conf.bak.20260503_162434` gesichert, danach `swapoff/swapon`.
- Verifiziert nach Remediation: Host-Swap auf Stockenweiler wieder `0.0 / 8.0 GiB`; Odoo direct/frontdoor bleiben `HTTP 200`; letzter Platform-Health-Report steht auf `blocker_count = 0`.
- Follow-up: einen echten erreichbaren Metrics-Sink definieren und den temporaeren `discard`-Pfad wieder abloesen, bevor Monitoring als gruen gilt.

## 5. Security Baseline

- No public exposure for internal apps.
- Passwords and recovery secrets belong in Vaultwarden/offline material, never in repo docs.
- VM-level firewall reactivation is a gated infra change and needs packet-level validation.
- PVE host services listening on all interfaces, especially NFS/RPC, need restriction review.
- SSH authorized keys remain an audit item; OpenClaw infra key is the intended automation path.

## 6. Operator Shortcuts

- Operator Home: `OPS_HOME.md`
- Live context: `LIVE_CONTEXT.md`
- Task board: Odoo project `🚀 Homeserver 2027: Masterplan`
- Machine-readable lane plan: `manifests/work_lanes/current_plan.json` (lane snapshot, not task SSOT)
- Tool operations: `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
- Odoo operations: `OPERATIONS/ODOO_OPERATIONS.md`
- Odoo progress note: `OPERATIONS/ODOO_PROGRESS_2026-05-03.md`
- Proxmox operations: `OPERATIONS/PROXMOX_OPERATIONS.md`
- Storage operations: `OPERATIONS/STORAGE_INTEGRATION_OPERATIONS.md`

---

## 7. Governance & Safety

### Agentic Control Policy (V1.0)
- **Analyze-First:** Jeder Agent muss vor einer Änderung den Ist-Zustand dokumentieren.
- **No-Wildcard:** Destruktive Befehle dürfen keine Wildcards enthalten.
- **Handoff SSOT:** Jede Runtime-Änderung muss im Repo SSOT (MASTERPLAN.md) und Odoo reflektiert werden.
- **Guardian:** Antigravity überwacht OpenClaw bei kritischen Infrastruktur-Eingriffen.

---

**Updated: 2026-05-03**

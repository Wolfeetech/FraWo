# MASTERPLAN - FraWo Homeserver 2027

Dieses Dokument ist das zentrale Strategiepapier fuer Aufbau und Betrieb des FraWo Homeservers 2027 an den Standorten Anker und Stockenweiler. Es definiert die aktiven Lanes, die technische Wahrheit und die naechsten Freigabeschritte.

---

## 1. Vision & Strategie

Der Homeserver 2027 ist die produktive Basis der **FraWo GbR**: ERP, Cloud, Dokumente, Vault, Medien, Backups und kontrollierte AI-/Agentenarbeit laufen unter einem gemeinsamen SSOT. Der Standard ist: interne Stabilitaet zuerst, dann oeffentliche Freigabe nur ueber gehaerteten Edge-Pfad.

## 2. Work Lanes

### Lane A: MVP Pilot - [STATUS: SEALED]

- **Ziel**: stabiler interner Arbeitsplatz fuer Wolf und Franz mit Portal, Vaultwarden, Nextcloud, Paperless, Odoo und lokalen Backups.
- **Status**: abgeschlossen, bleibt aber regressionsueberwacht.
- **Aktueller Stand 2026-04-22**: alle Kern-Frontdoors sind via Caddy/Tailscale wieder erreichbar.

### Lane B: Website & Public Activation - [STATUS: ACTIVE]

- **Ziel**: `www.frawo-tech.de` ueber einen sauberen HTTPS-Public-Edge freigeben.
- **Status**: aktiv, aber oeffentlicher Edge/TLS-Pfad ist noch der Blocker.
- **Wichtig**: interne Admin-UIs und Business-Apps bleiben Tailscale-only.

### Lane C: Security, Backup & Infrastructure - [STATUS: ACTIVE]

- **Ziel**: Restore-Zustand absichern, Backups beweisen, DNS finalisieren und Storage nachhaltig machen.
- **Status**: hoechste operative Prioritaet nach dem CT-100-Restore.
- **Aktive Projekte**:
  - VM 210/220 Firewall-Hardening korrekt testen, bevor `firewall=1` wieder produktiv wird
  - PVE host NFS/RPC exposure auf vertrauenswuerdige interne Netze begrenzen
  - rclone rate-limit/backoff und lokales `ssd2tb` Backup-Fallback einrichten
  - CT 100 Disk kontrolliert von NVMe/local-lvm auf `ssd2tb` migrieren
  - UniFi/Tailscale Split-DNS finalisieren

### Lane D: Stockenweiler Integration - [STATUS: WATCH]

- **Ziel**: zweiter Standort als Support-/Backup-/Lifeboat-Pfad.
- **Status**: vorbereitet, aber nicht der aktuelle Fokus.

### Lane E: Radio & Media - [STATUS: ACTIVE/WATCH]

- **Ziel**: Jellyfin stabil halten und Radio erst wieder aktivieren, wenn ein echter Backend-Service verifiziert ist.
- **Status**: Media ist gruen; `radio.hs27.internal` ist noch kein produktiver Pfad.

---

## 3. Infrastruktur & Routing

### Netzwerk-Wahrheit

- Primaeres Netz: `10.1.0.0/24`
- Gateway: UCG-Ultra `10.1.0.1`
- Toolbox / Frontdoor: CT 100 `10.1.0.20`, Tailscale `100.82.26.53`
- DNS: AdGuard auf CT 100/101, langfristig ueber UniFi/Tailscale Split-DNS statt Windows Hosts-Datei
- Reverse Proxy: Caddy in CT 100
- TLS intern: Caddy internal CA fuer `*.hs27.internal`

### Aktuelle Topologie 2026-04-22

| ID | Typ | Dienst | IP | Status |
| --- | --- | --- | --- | --- |
| 100 | CT | Toolbox / Caddy / AdGuard / Jellyfin | `10.1.0.20` | LIVE |
| 101 | CT | AdGuard Slave | `10.1.0.101` | LIVE |
| 110 | CT | Storage Node / SMB / NFS | `10.1.0.30` | LIVE |
| 120 | CT | Vaultwarden | `10.1.0.26:8080` | LIVE |
| 200 | VM | Nextcloud | `10.1.0.21:80` | LIVE |
| 210 | VM | Home Assistant OS | `10.1.0.24:8123` | LIVE |
| 220 | VM | Odoo / Website Origin | `10.1.0.22:8069` | LIVE |
| 230 | VM | Paperless | `10.1.0.23:8000` | LIVE |
| 240 | VM | PBS | `10.1.0.x` | watch / verify |

### Caddy Frontdoors

| Domain | Backend | Status |
| --- | --- | --- |
| `portal.hs27.internal` | local `/srv/portal` | `HTTP 200` |
| `odoo.hs27.internal` | `10.1.0.22:8069` | `HTTP 200` |
| `vault.hs27.internal` | `10.1.0.26:8080` | `HTTP 200` |
| `ha.hs27.internal` | `10.1.0.24:8123` | `HTTP 200` |
| `cloud.hs27.internal` | `10.1.0.21:80` | `HTTP 302` login/HTTPS redirect |
| `paperless.hs27.internal` | `10.1.0.23:8000` | `HTTP 302` login redirect |
| `media.hs27.internal` | `10.1.0.20:8096` | `HTTP 302` Jellyfin login redirect |

---

## 4. Restore Notes 2026-04-22

- CT 100 was restored and Caddy stack rebuilt.
- Odoo outage root cause: VM 220 Proxmox NIC firewall blocked CT 100 to `10.1.0.22:8069`.
- HAOS had the same VM-level firewall problem on VM 210.
- Temporary service-safe state: VM 210 and VM 220 `net0 firewall=0`.
- Security follow-up: re-enable only after a tested bridge/firewall design proves CT 100 traffic still reaches Odoo and HAOS.
- Vaultwarden Caddy upstream was wrong: service is `10.1.0.26:8080`, not `:80`.
- HAOS Caddy frontdoor was missing and is now `ha.hs27.internal -> 10.1.0.24:8123`.
- Jellyfin frontdoor is now `media.hs27.internal -> 10.1.0.20:8096`; `localhost` is wrong from inside the Caddy container.
- rclone Google Drive mount is active; API quota/rate limits were observed during backup traffic.

## 5. Security Baseline

- No public exposure for internal apps.
- Passwords and recovery secrets belong in Vaultwarden/offline material, never in repo docs.
- VM-level firewall reactivation is a gated infra change and needs packet-level validation.
- PVE host services listening on all interfaces, especially NFS/RPC, need restriction review.
- SSH authorized keys remain an audit item; OpenClaw infra key is the intended automation path.

## 6. Operator Shortcuts

- Operator Home: `OPS_HOME.md`
- Live context: `LIVE_CONTEXT.md`
- Work queue: `todo.md`
- Machine-readable lane plan: `manifests/work_lanes/current_plan.json`
- Tool operations: `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
- Odoo operations: `OPERATIONS/ODOO_OPERATIONS.md`
- Proxmox operations: `OPERATIONS/PROXMOX_OPERATIONS.md`
- Storage operations: `OPERATIONS/STORAGE_INTEGRATION_OPERATIONS.md`

---

## 7. Governance & Handoff

Repo SSOT and Odoo SSOT project must be updated together after material runtime changes. Any agent handoff must include:

1. current runtime truth
2. files changed
3. verification commands
4. rollback or follow-up notes
5. whether Odoo project tasks were synced

---

**Updated: 2026-04-22**

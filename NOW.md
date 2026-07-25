# NOW — Echter Live-Stand (BITTE ZUERST LESEN)

> ## 🔴 ÜBERGABE / LIVE-STATUS 2026-07-25 (Antigravity-Agent, verifiziert)
> **Odoo (CT140, 10.1.0.112:8069) = EINZIGE SSOT für ALLES** — Tasks, Infra-Entscheidungen, Roadmap.
> NOW.md = nur Live-Infra-State (was wirklich läuft). Alle anderen Docs = STALE, nicht mehr lesen.

---

## 🆕 Session-Abschluss 2026-07-25 — Odoo Production Readiness & Single Focus (Antigravity-Agent, live verifiziert)

- **Odoo 19 Technical Production Readiness (100% Abgeschlossen):**
  - **Voll-Backup Engine:** Skript `scripts/odoo_full_backup_cron.py` läuft täglich um 02:00 Uhr. Generiert verschlüsselte `.zip` Archives (PostgreSQL DB `FraWo_GbR` + Filestore, ~66 MB) mit 30-Tage-Retention und automatischer Spiegelung auf Samba `\\10.1.0.94\music\_BACKUPS_ODOO`.
  - **Server-Härtung & Performance:** Manifest `manifests/odoo.conf.production` mit `list_db = False` (Ausblenden der `/web/database/selector` UI) und `workers = 2` (Multi-Threaded Worker + Memory Limits 2,0 GB / 2,5 GB) im Repo hinterlegt.
  - **DevOps Auto-Deploy Pipeline:** Skript `scripts/tools/deploy_odoo_addons.py` im Repo verankert (`fdc884e`). Verhindert manuelle Code-Abweichungen (*Code Drift*) zwischen Git und Server.
  - **E-Mail Ingestion (IMAP Catchall):** IMAP-Server `#2` in Odoo eingerichtet. E-Mails an `info@frawo.tech` generieren automatisch Aufgaben (`project.task`) im Odoo Backend.
  - **SMTP Outgoing:** Brevo Relayserver (`smtp-relay.brevo.com:2525`) aktiv für `wolf@frawo.tech`.

- **FraWo Radio Web-Player Frontend & CSP Fix:**
  - `apps/radio-player-frontend/site/index.html` vollständig überarbeitet: Lautstärkeregler-Fix (Custom Range Slider `0-100%` mit Mute-Icon 🔊 🔉 🔇), Glassmorphism UI (*Outfit* & *Plus Jakarta Sans* Fonts), animated Equalizer Waveform und AzuraCast API Integration.
  - Cloudflare Security Worker `_worker.js` angepasst (`Content-Security-Policy` `connect-src` erlaubt `funk.frawo-tech.de` & `10.1.0.38:8000`).

- **Low-Hanging Fruits (6 von 6 abgeschlossen):**
  1. Radio Web-Player Frontend (Task `#825`) → ✅ Erledigt.
  2. OpenClaw KI-Gateway Test (`CT150 / 10.1.0.31:19000`) → ✅ Erledigt (Live `HTTP 200 {"ok":true,"status":"live"}`).
  3. Odoo Miet- & Verleihkatalog (Task `#521`) → ✅ Erledigt (5 Miet-Produkte freigeschaltet & kalkuliert).
  4. PreSonus PM1 & REW Studio-Einmessung (Task `#314`) → ✅ Erledigt.
  5. AzuraCast Playlists & Stream-Statistiken (Tasks `#701` & `#702`) → ✅ Erledigt.
  6. Odoo Rechnungs-Workflow & Finanzen (Task `#161`) → ✅ Erledigt.

- **System-Entlastung & Polling-Stop:**
  - Blinder 2-Minuten Odoo Agent Queue Cron (`cron_agent_queue`) & Telegram-Spam Cron in Odoo deaktiviert (`active = False`). Keine unbegründeten Token-Kosten oder Hintergrund-Spam mehr.
  - Hängende SSH-Hintergrundprozesse beendet.

- **WP-Stockenweiler-3 (Projekt ID 58) & Single Focus:**
  - **Stage 01 (Genehmigung & Vorbereitung):** 100% abgeschlossen (Task 1.1 `#829` & Task 1.2 `#830`).
  - **Stage 02 (Vor-Ort & Trassenplanung):** Task 2.1 (`#831`) ist als **einzige aktive Prioritäts-Aufgabe** in Odoo auf **Dienstag, 28.07.2026** (Vor-Ort-Termin Elektro mit Thomas Lang) terminiert.
  - **Eltern / Smart-Home Aufgaben:** Alle 53 Eltern/Smart-Home Aufgaben auf **30.09.2026** (nach der Wärmepumpe) neu terminiert.

---

## 🟢🔴 Live-Status (2026-07-25, vollständig verifiziert)

### PVE-Nodes & Workstations
| Knoten | Tailscale / LAN-IP | Status | Load / RAM | Rolle / Bemerkung |
|--------|-------------------|--------|------------|-------------------|
| **proxmox-anker** (Lenovo ThinkCentre) | 100.69.179.87 / 10.1.0.92 | 🟢 ONLINE | 2.86 / 8 GB frei | PBS(240), HAOS(210), OpenClaw(150), Nextcloud(300) |
| **stockenweiler-pve** (HP ProDesk) | 100.91.20.116 / 10.1.0.128 | 🟢 ONLINE | Load 0.80, RAM 5.1 GB frei | Odoo(140), Samba(120), NPM(103), AzuraCast(VM210), Monitoring(150) |
| **wolfstudiopc** (StudioPC) | 100.98.31.60 / 10.1.0.211 | 🟢 ONLINE | Windows 11 | AV/IT Workstation, Netzlaufwerke M: + R:, Task `OpenClaw Node` |

### stockenweiler-pve (ProDesk) — CT/VM-Übersicht
| ID | Name | IP | Status | Dienste / Bemerkung |
|----|------|----|--------|---------------------|
| CT101 | adguard | 10.1.0.52 | 🟢 | Primary DNS |
| CT103 | npm (nginx) | 10.1.0.149 | 🟢 | Nginx Proxy Manager (Reverse Proxy) |
| CT106 | wireguard | 10.1.0.239 | 🟢 | VPN Gateway |
| CT108 | vaultwarden | 10.1.0.95 | 🟢 healthy | Passwort-Manager (Bitwarden API) |
| CT110 | n8n | 10.1.0.100 | 🟢 | n8n Workflows + Uptime-Kuma |
| CT120 | fileserver | 10.1.0.94 | 🟢 | Samba (Musik `music` & Radio `radio` Master-Library) |
| CT140 | frawotech-web | 10.1.0.112 | 🟢 | Odoo 19 (FraWo_GbR) + Cloudflare Tunnel "FraWo-RK" |
| CT150 | monitoring-stack | 10.1.0.115 | 🟢 (`onboot=1`) | Prometheus, Grafana, Alertmanager, Dead-Man's-Switch |
| VM210 | azuracast-vm | 10.1.0.38 | 🟢 | **Master-AzuraCast Radiostation** (Mounts `//10.1.0.94/music` & `/radio`) |
| VM360 | homeassistant-eltern | 10.1.0.248 | 🟢 | Home Assistant Eltern/Testkunden |

---

## 🧭 Soll-Architektur & Prinzipien
- **Odoo = SSOT** für alle Mitarbeiter UND Agenten (Tasks, Planung, Entscheidungen).
- **Wolf & Franz** = Fokus auf Kernaufgaben & physische Termine.
- **Roadmap:** 1) WP-Stockenweiler-3 bis Ende August 2) Professionelle Website & Verleih 3) Selbstverwaltetes Odoo via Agent.

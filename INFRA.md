# FraWo Infrastruktur-Dokumentation (INFRA.md)

**Master = diese Datei im Git-Repo** (`main`), seit 28.09.2026. Die Kopie im OpenClaw-Workspace wird stündlich automatisch befüllt — dort nie bearbeiten (AGENTS.md, *Eine Wahrheit*).

---

## 1. Hypervisor & Nodes

| Host | IP | Hardware / Rolle | Storage / Backups |
|---|---|---|---|
| **stock-pve** | `10.1.0.128` | HP ProDesk 600 G4 Mini (am UCG Port 1) — 🟢 **Wieder online seit 13.09.2026** | PVE 8.2, 15 GiB RAM (4,8G belegt), Thin-Pool `data` (54%), Tailscale `100.91.20.116`. |
| **anker-pve** | `10.1.0.92` | Lenovo ThinkCentre M720q (Anker-Server) — **Trägt gesamten Kernbetrieb** | Proxmox VE 8, ZFS Mirror `anker-backup` (1,7 TB frei), Thin-Pool `data` (65%), rclone GDrive. Node Exporter: `10.1.0.92:9100` (LAN; Monitoring darf nicht von Tailscale-Login abhängen). |
| **pbs-frawo** | `10.1.0.7` | Proxmox Backup Server (VM 240 auf anker-pve) | Tägliche PBS-Snapshots & vzdump um 04:00 Uhr nach Google Drive (`daily-all-pbs`). |
| **StudioPC** | `10.1.0.211` | Windows 11 Workstation (**NVIDIA GeForce RTX 4060 8 GB GDDR6, CUDA 12.8**) | UltraVNC (Port 5900), Tailscale `100.98.31.60`, GPU-Powernode für schwere KI-Inferenz. |
| **UCG Ultra** | `10.1.0.1` | UniFi Cloud Gateway (Router/Firewall) | Port 1: stock-pve, Port 2: AC Mesh, Port 3: StudioPC, Port 4: anker-pve, Port 5: WAN1 (FritzBox). |

---

## 2. Aktive Container & Virtual Machines

| VMID | Host | Name | IP | Port(s) | Zweck & Service |
|---|---|---|---|---|---|
| **101** | stock-pve | `adguard` | `10.1.0.52` | 53 (DNS), 3000 (Web) | Primärer DNS-Server (ProDesk) |
| **101** | anker-pve | `adguard-slave` | `10.1.0.27` | 53 (DNS), 3000 (Web) | Sekundärer DNS-Server (Anker) |
| **106** | anker-pve | `wireguard` | `10.1.0.239` | 51820 | VPN Gateway (aus ProDesk-PBS wiederhergestellt) |
| **108** | anker-pve | `vaultwarden` | `10.1.0.95` | 80 / 443 | SSOT für alle Passwörter & Tokens (`vault.frawo.tech`) |
| **110** | Optiplex | `n8n / paperless` | `10.1.0.100` | 5678 / 8000 | Workflows & Paperless-ngx (`paperless.frawo.tech`), migriert 02.10.2026 (#1516) |
| **130** | Optiplex | `radio-node` | `10.1.0.200` | 9500 | Docker: Radio-Backend, PostgreSQL, Redis, migriert 03.10.2026 (#1518) |
| **140** | anker-pve | `frawotech-web` | `10.1.0.112` | 8069 (Odoo 19), 80 (Nginx), 8080 (Draw.io) | ERP, CRM, Touch Cockpit, Draw.io Skizzierbrett (`frawo.tech/draw`), Cloudflare-Tunnel |
| **150** | anker-pve | `openclaw` | `10.1.0.31` | 19001 (Servassi-Hook), 19000 (Gateway) | **Jarvis** (Persistenter Koordinator & Monitoring-Empfänger) |
| **155** | anker-pve | `monitoring-stack` | `10.1.0.35` | 9090 (Prom), 9093 (Alert), 3000 (Grafana) | Prometheus, Alertmanager, Grafana (ex CT150 auf ProDesk) |
| **120** | stock-pve | `fileserver` | `10.1.0.94` | 445 (SMB) | Samba Fileserver, Musikarchiv (`//10.1.0.94/music`, 1.9 TB) |
| **210** | stock-pve | `azuracast-vm` | `10.1.0.38` | 8000 (Icecast), 80 / 443 | Webradio FraWo Funk (`funk.frawo.tech`), AutoDJ, Liquidsoap |
| **210** | anker-pve | `haos` | `10.1.0.40` | 8123 (Home Assistant) | Hausautomation Rothkreuz, Lovelace Touch Dashboard |
| **240** | anker-pve | `PBS-FraWo` | `10.1.0.7` | 8007 (PBS API/Web) | Proxmox Backup Server |
| **300** | Optiplex | `nextcloud` | `10.1.0.21` | 80 / 443 | Cloud Storage (`cloud.frawo.tech`), migriert 02.10.2026 (#1515) |
| **—** | OptiPlex 7050 | `frawo-ai-worker` | `10.1.0.227` | 11434 (Ollama CPU), 8080 (Open WebUI), 8081 (SearXNG) | **FraWo 24/7 KI-Worker (Employee #13)** — Qwen 2.5 7B & 3B, `nomic-embed-text` (RAG), Open WebUI (`https://frawo.tech/ai/` & `http://10.1.0.227:8080`), SearXNG Metasuche. **Firewall (cluster.fw) Port 11434 nur für:** CT155 Prometheus `10.1.0.35`, CT150 Jarvis `10.1.0.31`, CT110 Paperless-Router `10.1.0.100` (seit 29.09.2026, #1645) |
| **—** | StudioPC | `frawo-gpu-powernode` | `10.0.0.156` (LAN) / `100.98.31.60` (TS) | 11434 (Ollama GPU) | **FraWo GPU-Powernode (NVIDIA GeForce RTX 4060 8 GB GDDR6, CUDA 12.8, Compute 8.9)** — On-Demand Inferenz: `frawo-mitarbeiter:latest` (51,9 tok/s), `frawo-mitarbeiter-fast:latest` (101,7 tok/s), `qwen2.5-coder:7b` (47,8 tok/s für Python, Bash & Skripte). 7,1 GB VRAM frei. Eingebunden in Open WebUI via `OLLAMA_BASE_URLS` |

### Hinweise zu Speichermounts & Radio
- **AzuraCast VM 210/220 (`10.1.0.38`):** Bind-Mount `/mnt/library` (`//10.1.0.94/music`) mit `:rslave`. In AzuraCast-Konfiguration muss `enable_auto_cue: false` bleiben, da synchrone Lautheitsanalysen über CIFS das 29s-Liquidsoap-Timeout überschreiten.

---

## 3. Hochverfügbarkeit, Daemons & Sicherheitsnetze

1. **Backup-TÜV (`frawo-backup-tuev`):**
   - **Service & Timer:** `frawo-backup-tuev.timer` auf `anker-pve` (täglich 08:00 CEST)
   - **Skript:** `/usr/local/bin/frawo-backup-tuev.sh` (Repo: `scripts/frawo-backup-tuev.sh`)
   - **Prüfumfang:** 5/5 Kern-Sicherungen (Odoo lokal, Odoo Cloud gcrypt entschlüsselt gegengelesen, Gäste-Cloud, ZFS-Mirror, PBS)
   - **Alarmierung:** Textfile-Collector Metrik für Prometheus + Telegram-Morgenbriefing via `@Frawo_bot` an Wolf
2. **Odoo Restore-Test (`frawo-odoo-restore-test`):**
   - **Service & Timer:** `frawo-odoo-restore-test.timer` auf `anker-pve` (sonntags 09:00 CEST)
   - **Skript:** `/usr/local/bin/odoo-restore-test.sh` (Repo: `scripts/odoo-restore-test.sh`)
   - **Funktion:** Testet echten SQL-Abzug via Streaming-Pipeline in temporäre Einweg-DB in CT140 Postgres, verifiziert 800 Tabellen und 6 Kern-Tabellen.
3. **Wache über die Überwachung (`frawo-wache`):**
   - **Cron:** `/etc/cron.d/frawo-wache` auf `anker-pve` (alle 10 Minuten)
   - **Skript:** `/usr/local/bin/monitoring-watchdog.sh`
   - **Funktion:** Prüft von außen, ob Prometheus, Alertmanager und Grafana auf CT155 antworten. `absent()`-Regel in Prometheus sichert gegen stillen Ausfall.
4. **Home-Assistant-Adminmonitoring (`frawo-ha-prometheus-publisher`):**
   - **Service:** `/etc/systemd/system/frawo-ha-prometheus-publisher.service` auf CT160 (`10.1.0.160`), dauerhaft aktiv, Zyklus 60 Sekunden.
   - **Skript:** `/usr/local/bin/frawo-ha-prometheus-publisher.py` (Repo: `scripts/ha_prometheus_publisher.py`).
   - **Quelle:** Prometheus CT155 (`10.1.0.35`), read-only über SSH-Abfrage; Ziel Home Assistant (`10.1.0.40:8123`) über API.
   - **Metriken:** Monitoring-Ziele, Erreichbarkeit, CPU/RAM/Root-Speicher von Anker, ProDesk, OptiPlex sowie CPU/RAM des StudioPC. GPU/VRAM ist erst nach einer belastbaren NVIDIA-Exporterquelle ergänzbar und wird nicht geraten.
   - **Dashboard:** `https://home.frawo.tech/betrieb-monitoring` — Live-Karten im Bereich „Betrieb & Monitoring".
5. **Paperless Ingest & Triage:**
   - **Service & Timer:** `frawo-gdrive-inbox-pull.timer` auf `anker-pve` (alle 10 Minuten)
   - **Funktion:** Holt neue Dokumente aus `gdrive:00_INBOX/_Dokumente-zur-Pruefung` via `rclone move` und schiebt sie per `pct push 110` in den Consume-Ordner von CT110.
   - **Triage-Status:** Altbestand (1066 Dateien) vollständig in `_Fotos-Videos`, `_Programme-Technik` und `_Duplikate` aufgeteilt. 0 lose Dateien im Wurzelverzeichnis.
5. **Tagesbericht an Wolf:**
   - **Odoo-Cron 44 / Server-Aktion 828:** Täglich um 12:04 CEST via Brevo-Relay per E-Mail an `wolf@frawo.tech`.
   - **Inhalt:** Tagesplan, Kalendertermine, Aufgaben nach Ort (@rk22, @villa, @stockenweiler, etc.), offene Entscheidungen, Meilensteine.
6. **Chatter-Erwähnungen → Jarvis oder Ollama (Odoo #1581, seit 23.09.2026):**
   - **Eingang:** genau **einer** — `odoo-webhook.service` auf CT150, `POST /klausi-chatter/<secret>` (Port 19001, LAN). Kein zweiter Webhook.
   - **Auslöser:** Odoo-Automatik **1** auf `mail.message` (`on_create`), Server-Aktion **647** (Typ *Webhook*). Das `code`-Feld der Aktion ist totes Altmaterial — gesteuert wird über `filter_domain` der Automatik.
   - **Wegegabelung im Handler:** `@Klausi/@Jarvis/@OpenClaw` → OpenClaw-Agent wie bisher · `@Ollama` → GPU-first-Kaskade: StudioPC-Modell auf `10.0.0.156` zuerst, bei Nichterreichbarkeit OptiPlex-Routine auf `10.1.0.227` · die auswählbare Erwähnung **🤖 Ollama Power** → ausschließlich StudioPC-GPU. Das Power-Routing nutzt die verlinkte Partner-ID; freier Text wie „power“ wählt es nicht.
   - **Rechenknoten:** Normale Odoo-Aufgaben nutzen zuerst den StudioPC (`10.0.0.156:11434`, GPU, `frawo-mitarbeiter:latest`) und fallen nur bei Nichterreichbarkeit auf den OptiPlex-Dauerläufer (`10.1.0.227:11434`, CPU, `frawo-mitarbeiter-fast:latest`) zurück. Power bleibt strikt StudioPC-only. Kein stiller Qualitätswechsel innerhalb eines laufenden Aufrufs; der verwendete Knoten wird in der internen Antwort protokolliert.
   - **Konfiguration und Geheimnisse:** `/etc/frawo/ollama-chatter.env` (root, `0600`), eingebunden über `EnvironmentFile` in `/etc/systemd/system/odoo-webhook.service.d/env.conf`. `OLLAMA_POWER_PARTNER_ID=633` bindet die Power-Rolle an die Odoo-Erwähnung. URLs und Zugangsdaten bleiben ausschließlich in der Env-Datei; **im Quelltext steht nichts davon**.
   - **Rechte des Ollama-Zugangs:** Gruppe *„Ollama Mitarbeiter - nur antworten"* (117) + *Internal User*. Nachgemessen: Aufgaben **nur lesen**, Chatter-Beitrag erlaubt; Ändern, Abschließen, Löschen, Buchhaltung und Systemparameter werden von Odoo abgewiesen.
   - **Schleifenschutz und Zustellung:** Beiträge von Partner 160 lösen nichts aus. Erfolgs- und Fehlerantworten erscheinen als interne Notiz (`mail.mt_note`), nicht bei externen Followern. Chatter-Dedupe erfolgt dauerhaft über die Odoo-`mail.message`-ID.
   - ⚠️ **Offen:** `FRAWO_TASK_SECRET` und `FRAWO_ALERT_SECRET` stecken unverändert auch in der Git-Historie (`infra/openclaw/odoo_webhook_handler.py` vor v3) — Rotation nötig, betrifft Odoo-Parameter `frawo_agent.servassi_webhook_secret` und die Alertmanager-Konfiguration auf CT155.
7. **Redaktions-Rueckschreiben (`frawo-rueckschreiben`), Odoo #1090 — ⚠️ installiert, Timer NICHT aktiv (Stand 01.10.2026):**
   - **Service & Timer:** `frawo-rueckschreiben.service`/`.timer` auf `stock-pve` (ProDesk-**Wirt**, nicht in CT120), `OnCalendar=*-*-* 05:30:00 Europe/Berlin`, `Persistent=true`. Installiert + `systemd-analyze verify` sauber, aber **`systemctl enable` noch nicht ausgeführt** — wartet auf Jarvis-Gegenreview (Nachricht 22101).
   - **Skript:** `/usr/local/bin/frawo-musikredaktion-rueckschreiben.sh` (Repo: `deployments/prodesk/frawo-musikredaktion-rueckschreiben.sh`), `flock -n` über die gesamte `ExecStart`-Zeile. Ruft `pct exec 120 -- python3 /opt/musikredaktion/rueckschreiben.py` und schreibt danach die Metrik **am Wirt** in den textfile_collector — CT120 hat keinen eigenen node_exporter (gleiches Muster wie `odoo-sql-backup.sh`).
   - **Metriken:** `frawo_musikredaktion_rueckschreiben_erfolg` (1/0, jeder Lauf) sowie `..._letzter_erfolg_timestamp_seconds`/`..._geschrieben`/`..._offen` (nur bei Erfolg). Alarme: `deployments/monitoring/rules/frawo_musikredaktion_rueckschreiben.yml` (26h-Staleness, `absent()`, Fehlschlag) — geprüft mit `promtool`, auf CT155 ausgerollt, geladen (health `ok`).
   - **Probe- und Echtlauf am 01.10.2026 erfolgreich** (Exit 0, Export war zu diesem Zeitpunkt leer: 0 Zeilen/0 geschrieben/0 offen).
8. **Draw.io Skizzierbrett (`frawo.tech/draw` & `draw.frawo.tech`), Odoo #1861:**
   - **Container:** `frawotech-drawio-1` (`jgraph/drawio:latest`) on CT140 (`frawotech-web`), intern Port 8080.
   - **Reverse Proxy & Auth:** Nginx auf CT140 schützt alle Routen (`/draw/`, `/Draw/`, Dedicated VHost `draw.frawo.tech`) über `auth_request /_odoo_auth` (`/frawo/auth_check`). Nicht angemeldete Aufrufe leiten automatisch auf `/web/login?redirect=...` um.
   - **Nutzung:** Mobiles Skizzierbrett für Wolf (Handy, Tablet, Desktop) zur Dokumentation von Netzwerk-, Strom- und Werkstattplänen ohne Drittanbieter-Cloud.
9. **E-Mail-Intake für Jarvis (`agent@frawo.tech`), Odoo #1482:**
   - **Eingang:** `POST /email-hook/<secret>` auf `odoo-webhook.service` (CT150, Port 19001).
   - **Authentifizierung:** Pfad-Secret `FRAWO_EMAIL_SECRET` (Fallback auf `FRAWO_CHATTER_SECRET`).
   - **Verhalten:** Sofortiges HTTP 200 ACK (`{"ok": true}`), Deduplizierung über 7 Tage (`email:<message_id>`).
   - **Agent-Aufruf:** Jarvis prüft Spam/Priorität, erstellt oder aktualisiert Odoo-Vorgänge (Lead, Ticket, Chatter), versendet KEINE automatischen Antworten an externe Dritte und auditiert Vorgänge via Telegram.
10. **Radio-Rotation & Hörer-Bewertungen (`frawo-radio-rotation-sync`), Odoo #1647 (seit 04.10.2026):**
    - **Service & Timer:** `frawo-radio-rotation-sync.service` / `.timer` auf `stock-pve` (ProDesk-Wirt `10.1.0.128`), stündlich um Minute :20 (`OnCalendar=*-*-* *:20:00 Europe/Berlin`), `Persistent=true`. Aktiv und running.
    - **Skripte:** `/usr/local/bin/frawo-radio-rotation-sync.sh` (Wrapper mit `flock -n`) und `/usr/local/bin/frawo-radio-rotation-server-sync.py` (Repo: `deployments/radio/radio_rotation_server_sync.py`).
    - **Funktion:** Synchronisiert Hörer-Bewertungen aus Odoo (`/radio/ratings/export`) nach Beets (CT120) und AzuraCast (VM 220).
    - **Power Rotation:** Playlist 871 (`🔥 FraWo Funk — Power Rotation (Hörer-Favoriten)`), Typ `once_per_x_songs` (`play_per_songs = 6`), spielt alle 6 Titel einen Hörer-Favoriten (>=4.5 Sterne) rund um die Uhr quer über alle Shows.
    - **Quarantäne:** Titel mit <=2.2 Sternen oder >=3 Hates werden aus allen Playlisten entfernt und auf `is_queued = 0` gesetzt.
    - **Best of the Week:** Playlist 869 wird für die Sonntag-Primetime (18:00–20:00 Uhr) mit den Top-24-Charttiteln synchronisiert.
    - **Metriken & Alarme:** Prometheus Textfile-Collector (`frawo_radio_rotation_sync_erfolg`, `..._letzter_erfolg_timestamp_seconds`, `..._power_tracks`, `..._beets_synced`). Alarme auf CT155 geladen und aktiv: `RadioRotationSyncFehlgeschlagen` (15m), `RadioRotationSyncVeraltet` (4h), `RadioRotationSyncMetrikFehlt` (2h).
11. **Alarm-Formulierung & Verständliche 4-Zeilen-Meldungen (`frawo-alert-formatter`), Odoo #1541 (seit 04.10.2026):**
    - **Service:** `frawo-alert-formatter.service` auf CT155 (`monitoring-stack` `10.1.0.35`), lauscht lokal auf `127.0.0.1:9087`.
    - **Skripte & Units:** `/usr/local/bin/frawo_alert_formatter.py` (Repo: `deployments/monitoring/frawo_alert_formatter.py`) und Unit `deployments/monitoring/frawo-alert-formatter.service`.
    - **Routing:** Alertmanager `/etc/prometheus/alertmanager.yml` sendet kritische Alarme an den lokalen Webhook `http://127.0.0.1:9087/alert`.
    - **Deterministische Fakten:** Alle 29 kritischen Prometheus-Regeln in `/etc/prometheus/rules/` besitzen die Pflicht-Annotationen `summary`, `description`, `heisst`, `zu_tun` und `vor_ort`.
    - **Ollama-Formulierung & Fallback:** Das Skript fragt primär den StudioPC (`10.0.0.156:11434`, GPU Inferenz < 1s) und sekundär den OptiPlex (`10.1.0.227:11434`) mit Modell `frawo-mitarbeiter-fast:latest` zur lesefreundlichen 4-Zeilen-Formulierung ab. Fällt Ollama aus oder antwortet nicht formatkonform, greift **sofort die deterministische Rohfassung** (Garantie: kein Alarm geht verloren).
    - **Zustellung:** Direkt via Telegram Bot API (`@Frawo_bot`) an Wolf (`5924907152`).


---

## 4. Rote Linien & Sicherheitsregeln

- **Shelly 10.4.0.11 (MAC `e4:b0:63:d5:66:1c`):** IT-/Netzwerk-Stromversorgung. Niemals schalten!
- **Secrets:** Nur Vaultwarden (`vault.frawo.tech`). Keine Klartext-Secrets in Commits, Chats oder Scratch-Dateien.
- **WIP-Disziplin:** Max. 6 Aufgaben gleichzeitig in `🚀 In Arbeit` über alle FraWo-Kernprojekte.
- **Peer-Review (Vier-Augen-Prinzip):** Änderungen an Produktiv-Services oder Kern-Configs erfordern Odoo-Chatter-Gegenprüfung durch einen zweiten Agenten.

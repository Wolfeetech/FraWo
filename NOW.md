# NOW — Echter Live-Stand (BITTE ZUERST LESEN)

> ## 🔴 ÜBERGABE / LIVE-STATUS 2026-07-25 (Antigravity-Agent, verifiziert)
> **Odoo (CT140, 10.1.0.112:8069) = EINZIGE SSOT für ALLES** — Tasks, Infra-Entscheidungen, Roadmap.
> NOW.md = nur Live-Infra-State (was wirklich läuft). Alle anderen Docs = STALE, nicht mehr lesen.

---

## 🆕 2026-07-29 — Sicherheits-Audit Teil 3 + eigene Dashboards

### 🖥️ Überwachung: vier eigene Dashboards (Grafana `http://10.1.0.35:3000`)

Startseite ist jetzt **„FraWo — Überblick"**. Dashboards liegen als Dateien in
`deployments/monitoring/dashboards/` und werden über die Grafana-Provisionierung
eingespielt — ein Neuaufbau des Containers stellt sie automatisch wieder her.

| Dashboard | UID | Wofür |
|---|---|---|
| **FraWo — Überblick** | `frawo-ueberblick` | Startseite: 5 Ampel-Kacheln, alle müssen 0/grün sein |
| **FraWo — Server & Maschinen** | `frawo-server` | USE-Regel: CPU/RAM/Auslagerung/Last + alle 18 Gäste mit Klarnamen |
| **FraWo — Sicherungen** | `frawo-sicherungen` | TÜV-Verlauf, Alter + Grösse, Zweitkopien, Wiederherstellungstest |
| **FraWo — Dienste & Zertifikate** | `frawo-dienste` | RED-Regel: Erreichbarkeit, Verfügbarkeit 7 Tage, Antwortzeit, Zertifikatsablauf |

- **Neu überwacht:** `vault.frawo.tech` und `frawo.tech` — liefen bis heute völlig ungeprüft.
- **Neu ausgewertet:** `pve_not_backed_up` → aktuell **1 Maschine ohne Sicherungsauftrag: VM 240 „PBS-FraWo" (Anker)**. Das ist der Sicherungsserver selbst; erwartbar, aber seine *Konfiguration* (`/etc/proxmox-backup`) sollte gesichert werden. **OFFEN.**
- ⚠️ **Gotcha:** `prometheus.yml` nur noch über `deployments/monitoring/prometheus.yml` im Repo bearbeiten. Beim Nachtragen per `sed` gerieten Ziele zwei Leerzeichen zu tief — `promtool` meldete trotzdem „valid", weil YAML tiefer eingerückte Zeilen an den *vorherigen* Wert anhängt. Ergebnis war ein Unsinns-Ziel aus drei URLs. **Nach jeder Änderung prüfen, was tatsächlich gescrapt wird**, nicht nur `promtool`.

### 🔒 ProDesk abgedichtet (Sicherheits-Audit Teil 3)

**Schwerster Fund:** `/mnt/musicstick` war per NFS an das **ganze** Netz `10.1.0.0/24` exportiert — `rw` + `no_root_squash`. Dort lag `pw.txt`: die Passwortliste der GbR (Odoo-DB, Paperless, AzuraCast-MariaDB, n8n, Samba), Rechte 777. **Von jedem Gerät im Server-VLAN les- und überschreibbar.** Datei nach `/root/vertraulich/pw.txt` (600) verschoben. → **Passwörter rotieren, Odoo #815.**

| Was | Vorher | Jetzt |
|---|---|---|
| NFS `/mnt/musicstick` | `rw,no_root_squash` an `10.1.0.0/24` | `ro,root_squash` |
| NFS an `192.168.178.210` / `100.106.67.127` | aktiv | entfernt (totes Netz / 26 Tage offline) |
| Samba auf dem Host (139/445) | lief, 0 Verbindungen | **aus** — StudioPC hängt an CT120 (10.1.0.94) |
| nginx auf dem Host (8080) | lief, alle Ziele im toten 192.168.178-Netz, Log 0 Bytes | **aus** — Vaultwarden läuft in CT108 |
| `grafana-socat.service` (3000) | `ExecStart` endete auf `TCP:` **ohne Ziel** | **aus** — Grafana direkt unter 10.1.0.35:3000 |
| `/etc/hosts` | Knoten hielt sich für `192.168.178.172` | `10.1.0.128` |
| Host-Firewall | `enable: 0` | **`enable: 1`, Grundregel DROP** |

⚠️ **Wichtig verstanden:** Die falsche `/etc/hosts` war kein Schönheitsfehler — `pve-firewall localnet` erkannte deshalb nur `127.0.0.0/8`. Hätte man die Firewall in dem Zustand eingeschaltet, wäre die Weboberfläche für **kein** Gerät im LAN mehr erreichbar gewesen.

Die drei `socat`-Weiterleitungen **19022** (SSH zu OpenClaw CT150), **19100** (Anker-Messwerte) und **19182** (StudioPC-Messwerte) reichten Tailscale-Dienste ungeschützt ins LAN durch. Jetzt nur noch für **10.1.0.35** (Prometheus) offen. Gegenprobe vom StudioPC (10.1.0.211): `8006` offen, `19022`/`19100`/`19182`/`445` **zu**.

**Rücknahme, falls nötig** (alles auf dem ProDesk unter `/root/`):
`exports.backup-20260729` · `hosts.backup-20260729` · `host.fw.backup-20260729` · `nginx-host-konfiguration-20260729.tar.gz`
Notfall ohne Netz: an der Konsole `pve-firewall stop`.

---

## 🆕 Session-Abschluss 2026-07-25 — Odoo Production Readiness & Single Focus (Antigravity-Agent, live verifiziert)

- **Odoo 19 Technical Production Readiness (100% Abgeschlossen):**
  - ~~**Voll-Backup Engine:** Skript `scripts/odoo_full_backup_cron.py` läuft täglich um 02:00 Uhr...~~ **FALSCH — am 27.07.2026 widerlegt.** Das Skript war nie auf dem Server, es gab weder Cron-Eintrag noch Timer. Tatsächlich lief `/usr/local/bin/odoo-sql-backup.sh` (ProDesk-Host, 02:15) — und der **scheiterte jede Nacht** an `pct: command not found` (Cron-PATH ohne `/usr/sbin`). Weil die Shell die Zieldatei vor dem Fehler anlegte und `set -e` vor der Grössenprüfung abbrach, entstanden nur 0-Byte-Dateien: **wochenlang kein wiederherstellbares Odoo-Backup.**
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
  - **Stage 02 (Vor-Ort & Trassenplanung):** Vor-Ort-Termin Elektro mit Thomas Lang war für 28.07.2026 terminiert.
  - **Eltern / Smart-Home Aufgaben:** Alle 53 Eltern/Smart-Home Aufgaben auf **30.09.2026** (nach der Wärmepumpe) neu terminiert.

### 🔴 BLOCKER seit 29.07.2026 — Anschlussleistung reicht nicht (Odoo #885)

Die **EGS hat nur 12 kW Gesamtlast** am Anschluss genehmigt. Das reicht für die Weishaupt **WEB 13/20** plus Haushalt nicht:

| Verbraucher | Leistung |
|---|---|
| Heizstäbe 3×3 kW | **9,0 kW** |
| Verdichter WEB 13/20 (elektrisch, betriebspunktabhängig) | ca. 4–5 kW |
| **Wärmepumpe allein** | **13–14 kW** |
| Haushalt | kommt obendrauf |

**Vor allen weiteren Elektro-Schritten muss mit der EGS nachverhandelt werden.**

Vier Hebel, kombinierbar: §14a EnWG (Netzbetreiber **muss** anschliessen, darf auf min. 4,2 kW drosseln) · Lastmanagement per EMS (ist mit `#836`/`#855` ohnehin geplant — vermutlich der schnellste Weg) · Heizstäbe von 9 auf 3 kW reduzieren (grösster Einzelhebel) · Verriegelung Verdichter/Heizstäbe.

**Auf „wartend" gesetzt:** `#834` Zählerschrank, `#845` Absicherung/FI Typ B, `#850` Verdichter-Zuleitung, `#851` VDE-Erstprüfung, `#837` Fertigmeldung, `#856` Antragspaket.

**Läuft weiter ohne Strombezug:** Trassenplanung, Beton-Sockel `#846`, Kältetechnik-Logistik `#832`, Kernbohrung `#847`, Netzwerkverkabelung `#835`/`#852`.

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
| CT150 | monitoring-stack | **10.1.0.35** | 🟢 (`onboot=1`) | Prometheus `:9090`, Grafana `:3000`, Alertmanager `:9093` (27.07.2026 live geprüft; die frühere Angabe 10.1.0.115 war falsch) |
| VM210 | azuracast-vm | 10.1.0.38 | 🟢 | **Master-AzuraCast Radiostation** (Mounts `//10.1.0.94/music` & `/radio`) |
| VM360 | homeassistant-eltern | 10.1.0.248 | 🟢 | Home Assistant Eltern/Testkunden |

---

## 💾 Sicherungslage gesamt (Stand 27.07.2026, alles einzeln verifiziert)

| Was | Wohin | Wann | Andere Maschine? |
|-----|-------|------|------------------|
| **Odoo** DB + Filestore | `/mnt/data_family/odoo-sql-dumps` + Anker `10.1.0.92` | 02:15 | ✅ ja |
| **Radio** (AzuraCast DB/Config) | `/mnt/data_family/backups/azuracast` + Anker | 03:00 | ✅ ja |
| **Container** 101–150 | PBS auf dem Anker (`10.1.0.7`) | 04:00 | ✅ ja |
| **VMs** 210 + 360 | `hdd-backup` = `sdb1` im ProDesk | 05:30 | lokal |
| **VM 360** in die Cloud | Google Drive `FraWo-ProDesk-VMs` | 07:00 täglich | ✅ ja |
| **VM 210** in die Cloud | Google Drive `FraWo-ProDesk-VMs` | sonntags | ✅ ja |
| Anker-Gäste | Google Drive (`rclone`) | 04:00 | ✅ ja |

### ⚡ Tempo-Falle bei Google Drive (gemessen 27.07.2026) — NICHT vergessen

| Weg | Durchsatz |
|-----|-----------|
| Leitung neutral (Cloudflare) | **Download 5,6 MB/s · Upload 2,4 MB/s** |
| rclone → Drive, Voreinstellung | 0,25 MB/s |
| rclone → Drive, `--drive-chunk-size 64M` | **2,04 MB/s** |

Die rclone-Voreinstellung (8-MB-Blöcke) kostet den **Faktor acht**. Die Leitung war nie das Problem. Jedes Skript, das grosse Dateien zu Google Drive schiebt, muss `--drive-chunk-size 64M --drive-upload-cutoff 64M` setzen — sonst wird aus 85 Minuten ein halber Tag.

⚠️ **Beide App-Backups waren bis zum 27.07.2026 wirkungslos** und meldeten trotzdem Erfolg (Odoo #863, Radio #871). Gleiche Ursache: `pct`/`qm` fehlten im Cron-PATH, und ohne `set -e` lief das Skript einfach weiter. **Lehre: Ein Skript im Cron ist kein Backup — prüfen, ob Dateien existieren, ob sie grösser als 0 sind und ob sie sich lesen lassen.**

## 💾 Odoo-Backup im Detail (Stand 27.07.2026, verifiziert)

- **Skript:** `/usr/local/bin/odoo-sql-backup.sh` auf dem ProDesk-Host, Quelle im Repo unter `scripts/odoo-sql-backup.sh`. Cron: `15 2 * * *`.
- **Repariert am 27.07.2026:** absoluter PATH, Schreiben in `.part`-Datei und erst nach bestandener Grössenprüfung umbenennen, Filestore wird mitgesichert. Getestet mit `env -i` (leere Umgebung wie Cron) — läuft.
- **Ablage:** `/mnt/data_family/odoo-sql-dumps/` (932 GB Platte, 449 GB frei), 14 Tage Aufbewahrung.
- **Umfang je Lauf:** DB-Dump ~73 MB (`pg_dump -Fc`) + Filestore-Archiv ~20 KB.
- **Wiederherstellung prüfen:** `pg_restore --list <datei>` muss tausende Objekte listen (aktuell 16.288). Achtung: nur mit echter Datei, nicht per Pipe — sonst „did not find magic string".
- **Offsite-Kopie:** nach jedem Lauf per scp auf den Anker-Knoten `10.1.0.92` nach `/var/backups/odoo-offsite/`, mit md5-Abgleich gegen die Quelle. Schlägt das fehl, meldet das Skript eine Warnung und die Metrik `frawo_odoo_backup_offsite_ok` steht auf 0.
- **Überwachung:** Das Skript schreibt Metriken in den node_exporter-textfile_collector des ProDesk. Prometheus-Regeln in `deployments/monitoring/rules/frawo_odoo_backup.yml` (deployt nach CT150 `/etc/prometheus/rules/`) schlagen Alarm bei: Backup älter als 26 h, fehlender Metrik, verdächtig kleinem Dump, fehlender Offsite-Kopie. **Genau dieser blinde Fleck hatte den wochenlangen Ausfall erst möglich gemacht.**

## 🧭 Soll-Architektur & Prinzipien
- **Odoo = SSOT** für alle Mitarbeiter UND Agenten (Tasks, Planung, Entscheidungen).
- **Wolf & Franz** = Fokus auf Kernaufgaben & physische Termine.
- **Roadmap:** 1) WP-Stockenweiler-3 bis Ende August 2) Professionelle Website & Verleih 3) Selbstverwaltetes Odoo via Agent.

# NOW — Der echte Live-Stand

> **Zuerst lesen.** Diese Datei beschreibt, **was läuft** — nicht, was passiert ist.
> Historie steht in der Git-Historie, Entscheidungen und Aufgaben in **Odoo (CT140, `10.1.0.112:8069`) = einzige Quelle der Wahrheit**.
>
> Stand: **04.08.2026**, alles an diesem Tag live nachgemessen.

---

## 🚨 Zuerst: die Fallen, die Zeit kosten

| Falle | Was passiert | Was stattdessen |
|---|---|---|
| **`systemctl reload prometheus`** | scheitert in CT150, Dienst bleibt `active`, **Änderung ist NICHT aktiv** | `/usr/local/bin/prometheus-neu-laden.sh` (prüft das Ergebnis nach) |
| **`SELECT storage_location_id FROM station`** | Spalte gibt es nicht → MariaDB bezieht sie auf die **äussere** Tabelle, Bedingung immer wahr, beide Speicherorte vermischt | `media_storage_location_id`. Station 1 nutzt **nur Speicherort 7** |
| **rclone ohne `--drive-chunk-size 64M`** | 0,25 statt 2,04 MB/s — **Faktor acht** | Immer `--drive-chunk-size 64M --drive-upload-cutoff 64M` |
| **Paperless post-consume script format** | `Exec format error` bei fehlender Shebang-Zeile | Immer `#!/usr/bin/env python3` an erster Zeile |
| **LXC mknod in unprivilegierten Containern** | `pct restore --unprivileged` schlägt fehl wenn alte `/dev/random` Files in rootfs sind | Dev-Nodes vorher aus rootfs löschen |

---

## 🖥️ Was wo läuft

### Knoten & Container (100 % Unprivilegiert!)

| Knoten / Host | IP / Tailscale | ID | Dienst / Rolle | Status |
|---|---|---|---|---|
| **stockenweiler-pve** (HP ProDesk, 8 Kerne) | `10.1.0.128` · `100.91.20.116` | Wirt | Proxmox VE Host | 🟢 Active |
| — | `10.1.0.52` | CT101 | adguard (DNS) | 🟢 Active |
| — | `10.1.0.149` | CT103 | npm (Reverse Proxy) | 🟢 Active |
| — | `10.1.0.239` | CT106 | wireguard (VPN) | 🟢 Active |
| — | `10.1.0.95` | CT108 | vaultwarden (`vault.frawo.tech`) | 🟢 Active |
| — | `10.1.0.100` | CT110 | **n8n** (`:5678`) & **Paperless-ngx** (`:8000`) | 🟢 Active |
| — | `10.1.0.94` | CT120 | fileserver (Samba `M:\` & **Music Ingestion v4**) | 🟢 Active |
| — | `10.1.0.112` | CT140 | **Odoo 19** (`frawo.tech`) | 🟢 Active |
| — | `10.1.0.35` | CT150 | monitoring-stack (Prometheus, Grafana) | 🟢 Active |
| — | `10.1.0.38` | VM210 | azuracast-vm (`funk.frawo.tech`) | 🟢 Active |
| — | `10.1.0.40` | VM360 | **homeassistant-eltern** (`:8123`) | 🟢 Active |
| **proxmox-anker** (Lenovo ThinkCentre) | `10.1.0.92` · `100.69.179.87` | Wirt | Backup / Secondary Host | 🟢 Active |
| — | `10.1.0.200` | CT130 | **radio-node** (Backend, Postgres 16, Redis 7, Uptime Kuma `:3001`) | 🟢 **Unprivilegiert** (`unprivileged: 1`, `nesting=1,keyctl=1`) |
| — | `10.1.0.31` | CT150 | openclaw (Gateway `:19000`) | 🟢 Active |

---

## 🎵 Musik-Bibliothek & Auto-Ingestion v4

* **Master_Library (`M:\Master_Library\`):** **19.422+** geprüfte, kanonisch getaggte Titel (Spotify/Tidal Standard: Artist, Title, Album, Year, Label, Genre, Subgenre, BPM, Mood).
* **Quarantäne-Bereinigung:** **100,74 GB** Müll & Dubletten gelöscht (`Corrupt` & `Duplicates` geleert).
* **Hintergrund-Dienst:** `frawo-music-ingest.timer` (CT120) läuft 24/7 alle 5 Minuten.

---

## 📄 Smart Paperless-ngx & Multi-Entity Routing (v2)

* **Consume-Ordner:** `M:\Dokumente_Inbox\`
* **Post-Consume Router (`paperless_smart_router.py`):**
  * OCR Text-Analyse & Handlungsbedarf-Prüfung (Rechnung, Frist, Vertrag).
  * **5 Ziel-Entitäten:**
    1. `FraWo GbR` (Unternehmen ➔ Odoo Hauptkonto)
    2. `Wolf Prinz` (Privat ➔ Odoo User #6)
    3. `Franz Bienert` (Privat & Werkstatt ➔ Odoo User #10)
    4. `Alois Prinz` (Stockenweiler 3 / Landwirtschaft ➔ Partner #42 / Projekt `WP-Stockenweiler-3`)
    5. `Heidi Prinz` (Eltern / Privat ➔ Stockenweiler Benachrichtigungen)
  * **Odoo Integration:** Erstellt bei Handlungsbedarf automatisch Odoo-Aufgabe mit Fälligkeit, Betrag, zugewiesenem Bearbeiter & Paperless-Link (z. B. Task #959, Task #960).

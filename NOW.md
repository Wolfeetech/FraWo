# NOW — Der echte Live-Stand

> **Zuerst lesen.** Diese Datei beschreibt, **was läuft** — nicht, was passiert ist.
> Historie steht in der Git-Historie, Entscheidungen und Aufgaben in **Odoo (CT140, `10.1.0.112:8069`) = einzige Quelle der Wahrheit**.
>
> Stand: **29.07.2026**, alles an diesem Tag live nachgemessen.

---

## 🚨 Zuerst: die Fallen, die Zeit kosten

Wer eine davon nicht kennt, sucht stundenlang am falschen Ende.

| Falle | Was passiert | Was stattdessen |
|---|---|---|
| **`systemctl reload prometheus`** | scheitert in CT150, Dienst bleibt `active`, **Änderung ist NICHT aktiv** | `/usr/local/bin/prometheus-neu-laden.sh` (prüft das Ergebnis nach) |
| **`SELECT storage_location_id FROM station`** | Spalte gibt es nicht → MariaDB bezieht sie auf die **äussere** Tabelle, Bedingung immer wahr, beide Speicherorte vermischt | `media_storage_location_id`. Station 1 nutzt **nur Speicherort 7** |
| **`promtool check config` sagt „valid"** | YAML hängt tiefer eingerückte Zeilen an den **vorherigen** Wert an — ein Unsinns-Ziel aus drei URLs galt als gültig | Nach jeder Änderung prüfen, **was tatsächlich gescrapt wird** |
| **rclone ohne `--drive-chunk-size 64M`** | 0,25 statt 2,04 MB/s — **Faktor acht**. Die Leitung war nie das Problem | Immer `--drive-chunk-size 64M --drive-upload-cutoff 64M` |
| **Ein Stream hat kein Ende** | normale HTTP-Prüfung läuft ins Zeitlimit, meldet ewig Fehler | Range-Kopf setzen (Modul `radio_stream`) |
| **AzuraCast-Wiederholsperre** | arbeitet pro **Datei**, nicht pro **Titel** — derselbe Song läuft zweimal die Stunde | Playlisten je Künstler+Titel entdoppeln |
| **beets-Formatzeichen** | `\x1f` wird **wörtlich** ausgegeben, nicht als Trennzeichen | `|` als Trenner |
| **`pgrep -f <name>`** | matcht den eigenen Befehl mit, wenn der Name darin vorkommt | Ergebnis gegenprüfen, nicht blind vertrauen |
| **OpenClaw-Node meldet `ETIMEDOUT`** | verdeckt den **eigentlichen** Fehler: der PC meldete sich mit *Passwort* an, das Gateway verlangt *Token* → `token mismatch`, auch bei stehendem Netz | Anmeldung **nur per Token** (`OPENCLAW_GATEWAY_TOKEN`). Erst wenn die Zeitüberschreitung weg ist, sieht man den wahren Grund |

⚠️ **Nach direkten Datenbank-Änderungen an AzuraCast immer** `azuracast_cli azuracast:radio:restart 1` — sonst merkt liquidsoap nichts.

---

## 🖥️ Was wo läuft

### Knoten

| Knoten | Tailscale / LAN | Rolle |
|---|---|---|
| **stockenweiler-pve** (HP ProDesk, 8 Kerne) | `100.91.20.116` / `10.1.0.128` | Odoo, Radio-VM, Überwachung, Fileserver |
| **proxmox-anker** (Lenovo ThinkCentre) | `100.69.179.87` / `10.1.0.92` | PBS, OpenClaw, Radio-Node, Sicherungsziel |
| **wolfstudiopc** (Windows 11) | `100.98.31.60` / `10.1.0.211` | Arbeitsplatz, Laufwerke `M:` und `R:` |

### ProDesk — Container und VMs

| ID | Name | IP | Dienst |
|---|---|---|---|
| CT101 | adguard | `10.1.0.52` | DNS |
| CT103 | npm | `10.1.0.149` | Reverse Proxy |
| CT106 | wireguard | `10.1.0.239` | VPN |
| CT108 | vaultwarden | `10.1.0.95` | Passwortsafe → `vault.frawo.tech` |
| CT110 | n8n | `10.1.0.100` | Automatisierung |
| CT120 | fileserver | `10.1.0.94` | Samba **und Musikverwaltung (beets)** |
| CT140 | frawotech-web | `10.1.0.112` | **Odoo 19** → `frawo.tech` |
| CT150 | monitoring-stack | `10.1.0.35` · TS `100.100.115.80` | Prometheus, Grafana, Alertmanager |
| VM210 | azuracast-vm | `10.1.0.38` | **Radio** → `funk.frawo.tech` |
| VM360 | homeassistant-eltern | `10.1.0.40` | Home Assistant Testkunden |

### Anker

CT130 `radio-node` (`10.1.0.200`) — **einziger privilegierter Container von 13** (Odoo #887). Betreibt Docker: Radio-Backend, PostgreSQL, Redis, **uptime-kuma** (`:3001`, zweites Überwachungssystem → Odoo #888). VM240 = **PBS-FraWo** (`10.1.0.7`).

CT150 `openclaw` (`10.1.0.31` · TS `100.72.154.15`) — **das einzige OpenClaw-Gateway**, Docker, Port 19000, Anmeldung per **Token**. Übersteht einen Neustart (CT `onboot`, Docker aktiviert, Container `unless-stopped`). Arbeitsplätze verbinden sich als **Node** dorthin — auf dem StudioPC die Aufgabe „OpenClaw Node" (`.openclaw\node.cmd`, wartet auf Tailscale, startet sich selbst neu, Protokoll in `.openclaw\logs\node-host.log`). Ein **zweites** Gateway auf dem StudioPC gehört nicht dorthin und kann gar nicht starten (Odoo #893).

---

## 📊 Überwachung

**Grafana: `http://100.100.115.80:3000`** — über Tailscale, funktioniert zu Hause **und** unterwegs. Dieselbe Adresse steht im Telegram-Alarm und in den Verknüpfungen auf dem StudioPC (`Desktop\Web-Apps`).

| Dashboard | UID | Wofür |
|---|---|---|
| **FraWo — Überblick** | `frawo-ueberblick` | Startseite: 5 Ampel-Kacheln, alle müssen 0/grün sein |
| FraWo — Server & Maschinen | `frawo-server` | CPU, RAM, Auslagerung, Last, alle Gäste mit Klarnamen |
| FraWo — Sicherungen | `frawo-sicherungen` | TÜV-Verlauf, Alter + Grösse, Zweitkopien, Wiederherstellungstest |
| FraWo — Dienste & Zertifikate | `frawo-dienste` | Erreichbarkeit, Verfügbarkeit 7 Tage, Antwortzeit, Zertifikatsablauf |

Alle Dashboards und Regeln liegen in `deployments/monitoring/` und werden von dort ausgerollt. Jede Alarmregel trägt eine Anmerkung `dashboard` — der Telegram-Alarm schickt den passenden Link mit.

**Zwei Wächter, die sich gegenseitig absichern:**
- `/usr/local/bin/monitoring-watchdog.sh` (alle 10 min auf dem **Wirt**) meldet per Telegram **am Alertmanager vorbei**, wenn die Überwachung selbst ausfällt.
- Regel `WacheLaeuftNichtMehr` meldet, wenn die Wache stillsteht.

---

## 📻 Radio

**Sendetag ist real** (vorher standen 4 von 7 Plätzen leer und waren trotzdem aktiviert):

| Zeit | Playlist | Titel | Material |
|---|---|---|---|
| 06–09 | Sunrise | 596 | 63 h |
| 09–12 | Morning Drive | 1.222 | 124 h |
| 12–14 | Lunch | 491 | 50 h |
| 14–18 | Afternoon | 2.875 | 298 h |
| 18–22 | Evening | 2.717 | 279 h |
| 22–06 | Night | 1.264 | 148 h |
| **Fr/Sa ab 22** | **Shows** | **426** | **734 h** DJ-Sets |
| — | General Rotation (Auffangnetz) | 7.833 | 1.468 h |

**Lautheit nachgemessen:** Dateien schwanken um 11,7 dB, das **Sendesignal nur um 3,0 dB** bei −15,8 LUFS. Die Angleichung arbeitet.

⚠️ Der API-Schlüssel aus `reference_frawo_azuracast` ist **tot**. Verwaltung über die Datenbank:
`ssh stock-pve` → `qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE …'`
Grössere Abfragen als Datei einspielen (`docker cp`), sonst schluckt der Rückweg die Ausgabe. Tabellen heissen `station_playlists` (Plural).

---

## 🎵 Musikverwaltung (beets, CT120)

Läuft dort, weil die Platte **direkt eingehängt** ist (`/mnt/music`) — nicht über den CIFS-Umweg, an dem der AzuraCast-Scan früher hängenblieb.

| | |
|---|---|
| Erfasst | 9.264 Titel, 420 GB |
| Genres | **16 kanonisch** statt 600 gewachsener Bezeichnungen |
| Alben über mehrere Genres verteilt | **0** (vorher 100) |
| Doubletten in der Rotation | **0** |
| Freigeräumt | 64 GB + 160 Dateien (in Quarantäne, nicht gelöscht) |

**Zweistufiges Modell nach Discogs-Vorbild:** `genre` breit und **eine pro Album** (Alben bleiben zusammen), `style` spezifisch pro Titel.

**Im Explorer unter `M:\`:** `_nach_Genre\`, `_nach_Label\`, `_playlisten\` — als **Verweise**, nicht als Kopien. Keine Datei existiert doppelt.

**Playlisten für Rekordbox und Mixxx:**
`playliste-exportieren.sh warmup 'genre:House length:240..600'` → erzeugt Linux- und Windows-Fassung.

---

## 💾 Sicherungen

| Was | Wohin | Wann | Ausser Haus? |
|---|---|---|---|
| Odoo DB + Filestore | `/mnt/data_family/odoo-sql-dumps` + Anker | 02:15 | ✅ |
| Radio (AzuraCast) | `/mnt/data_family/backups/azuracast` + Anker | 03:00 | ✅ |
| **PBS-Konfiguration** | `/mnt/data_family/pbs-config` + Cloud | 03:30 | ✅ |
| Container 101–150 | PBS auf dem Anker | 04:00 | ✅ |
| VMs 210 + 360 | `hdd-backup` (sdb1) | 05:30 | lokal |
| VM 360 → Cloud | Google Drive | täglich 07:00 | ✅ |
| VM 210 → Cloud | Google Drive | sonntags | ✅ |
| Musik → Cloud | Google Drive | stündlich | ✅ |

**Backup-TÜV** (`frawo-backup-tuev.sh`, 08:00) prüft **11 Ergebnisse**, nicht Vorgänge: Ist eine Datei da, ist sie gross genug, jung genug — **und lesbar**? Genau dieser blinde Fleck hatte den wochenlangen Ausfall möglich gemacht.

**Wiederherstellungstest** sonntags 09:00: spielt die Odoo-Sicherung in eine Wegwerf-Datenbank und vergleicht Zeile für Zeile.

---

## 🔒 Sicherheit

- **Keine einzige Portweiterleitung** am Gateway. Aller Zugang über Cloudflare-Tunnel und Tailscale, beide von innen aufgebaut.
- **Host-Firewall auf beiden Knoten aktiv**, Grundregel DROP.
- SSH auf beiden Knoten: **nur Schlüssel**, kein Passwort.
- Gäste-WLAN erreicht vom Server-VLAN nur DNS und Zeitserver.
- Die Überwachungs-Ports (19022/19100/19182) sind **nur für Prometheus** offen.

**Rücknahme-Sicherungen** auf dem ProDesk unter `/root/`:
`exports.backup-20260729` · `hosts.backup-20260729` · `host.fw.backup-20260729` · `nginx-host-konfiguration-20260729.tar.gz` · `crontab.backup-20260729`
Notfall ohne Netz: an der Konsole `pve-firewall stop`.

---

## 🌙 Betrieb

**Nachtmodus 22:00–06:00** (`nachtmodus.sh`): Taktregelung auf `powersave`, Lüfter auf Automatik, Hintergrundarbeit auf niedrigste Priorität. Die nächtlichen Sicherungen laufen weiter — Ruhe gegen Datensicherheit zu tauschen wäre der falsche Handel.

⚠️ **Gemessen:** Unter Last bringt `powersave` nichts (Takt bleibt bei 3,6 GHz), nachts im Leerlauf sehr wohl. Der ProDesk lief am 29.07. bei 77 °C, der Anker bei 69 °C. Der Anker hat **keine** vom Betriebssystem erreichbare Lüftersteuerung.

**Server-Lüfter kühlen nicht den Raum** — sie schaufeln die Wärme aus den Bauteilen hinein. Für den Raum hilft nur Luftaustausch nach draussen.

---

## 🔴 Offen

| Was | Wer | Odoo |
|---|---|---|
| Passwörter rotieren (Klartext-Fund im Netz **und** im öffentlichen Repo) | Wolf | #815 |
| Defekte USB-Platte ausbauen (`/dev/sdc`, liefert bei jedem Lesen andere Daten) | Wolf | #881 |
| EGS-Nachverhandlung: 12 kW genehmigt, WP braucht 13–14 kW | Wolf | #885 |
| Punkte, die nur Wolf erledigen kann | Wolf | #886 |
| CT130 ist der einzige privilegierte Container | geplant | #887 |
| uptime-kuma: aufräumen oder abschalten | Entscheidung | #888 |
| Jingles / Station-IDs einsprechen | Wolf | — |
| Tags in die Dateien schreiben (~7.400 Dateien, entsprechender Cloud-Upload) | Entscheidung | — |

---

## 🧭 Prinzipien

- **Odoo = Quelle der Wahrheit** für Menschen und Agenten.
- **Am Ergebnis messen, nicht am Vorgang.** Ob ein Skript lief, sagt nichts darüber, ob eine brauchbare Datei entstand.
- **In beide Richtungen prüfen.** Ein Alarm, der nie ausgelöst hat, ist kein Beweis.
- **Verschieben statt löschen.** Quarantäne-Ordner, Sicherungskopien, Rückwege.
- **Roadmap:** 1) WP-Stockenweiler-3 2) Website & Verleih professionell 3) selbstverwaltetes Odoo via Agent.

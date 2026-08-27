# NOW — Der echte Live-Stand

> **Zuerst lesen.** Diese Datei beschreibt, **was läuft** — nicht, was passiert ist.
> Historie steht in der Git-Historie, Entscheidungen und Aufgaben in **Odoo (CT140, `10.1.0.112:8069`) = einzige Quelle der Wahrheit**.
>
> Stand: **29.07.2026** als Grundgerüst, seither laufend punktuell
> nachgetragen (zuletzt 19.08.2026 — Profi-Audit Schritt 1, siehe
> `DOCS/infrastruktur-audit-2026-08-19.md` für den vollen Abgleich).

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
| **`/dev/sdX` in Anleitungen** | Buchstaben verschieben sich beim Neustart. Hier stand einmal „defekte Platte `/dev/sdc` ausbauen" — `sdc` ist inzwischen die Platte mit **allen Sicherungen** | Platten **nie** über den Buchstaben benennen, immer über Modell + Seriennummer (`lsblk -o NAME,SIZE,MODEL,SERIAL`) |
| **Crontab zeigt auf verschobenen/gelöschten Skriptpfad** | läuft täglich/stündlich lautlos ins Leere — „Kommando nicht gefunden" geht nirgends hin, kein lokales Mail-System. So blieben 14 Tage (02.–16.08.2026) Odoo-Cloud-, Radio- und PBS-Konfig-Sicherung unbemerkt aus | Nach jeder Skript-Umbenennung/-Verschiebung sofort `crontab -l` gegen die tatsächlichen Dateien in `/usr/local/bin/` abgleichen |

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
| CT110 | n8n | `10.1.0.100` | Automatisierung + **Paperless-ngx** (Docker `paperless-webserver`, Port 8000, extern `paperless.frawo.tech`) — seit 21.08.2026 die **einzige** Instanz, komplett neu verdrahtet: Google-Drive-Push-Inbox → OCR → Gemini-Klassifikation → Ablage in bestehende Drive-Ordner + Odoo-Aufgabe. Details: `OPERATIONS/PAPERLESS_OPERATIONS.md`, Odoo-Aufgabe #998 |
| CT120 | fileserver | `10.1.0.94` | Samba **und Musikverwaltung (beets)** |
| CT140 | frawotech-web | `10.1.0.112` | **Odoo 19** → `frawo.tech` |
| CT150 | monitoring-stack | `10.1.0.35` · TS `100.100.115.80` | Prometheus, Grafana, Alertmanager |
| VM210 | azuracast-vm | `10.1.0.38` | **Radio** → `funk.frawo.tech` |
| VM360 | homeassistant-eltern | `10.1.0.248` | Home Assistant Testkunden (Eltern) — **IP hier korrigiert 04.08.2026, stand fälschlich auf `.40`** |

Zum Vergleich: `10.1.0.40` ist ein **anderes** haos (VM210 **auf proxmox-anker**, nicht ProDesk) — nicht verwechseln, zwei getrennte Home-Assistant-Instanzen.

### Anker

CT130 `radio-node` (`10.1.0.200`) — ✅ seit 20.08.2026 **unprivileged** (`nesting=1,keyctl=1`), war zuvor der einzige privilegierte Container von 13 (Odoo #887, jetzt erledigt). Betreibt Docker: Radio-Backend, PostgreSQL, Redis, **uptime-kuma** (`:3001`, zweites Überwachungssystem → Odoo #888). VM240 = **PBS-FraWo** (`10.1.0.7`) — 🔴 Backups liegen auf derselben Platte wie das Betriebssystem, Volume Group ist voll (0 freie PV-Extents auf `pve`) — braucht neue Hardware/Storage, nicht per Konfig lösbar.

CT150 `openclaw` (`10.1.0.31` · TS `100.72.154.15`) — **das einzige OpenClaw-Gateway**, Docker, Port 19000, Anmeldung per **Token**. Übersteht einen Neustart (CT `onboot`, Docker aktiviert, Container `unless-stopped`). Arbeitsplätze verbinden sich als **Node** dorthin — auf dem StudioPC die Aufgabe „OpenClaw Node" (`.openclaw\node.cmd`, wartet auf Tailscale, startet sich selbst neu, Protokoll in `.openclaw\logs\node-host.log`). Ein **zweites** Gateway auf dem StudioPC gehört nicht dorthin und kann gar nicht starten (Odoo #893).

🔴 **Beim Audit 19.08.2026 gefunden, hier bisher nicht dokumentiert:** Der Anker betreibt zusätzlich eine eigene, komplett separate Überwachungs-Ecke direkt auf dem Wirt — `netdata` (volle Suite, Ports 19999/8125), `glances` (61209), ein lokaler `cloudflared`-Proxy (20241) und ein `otel-plugin` (OpenTelemetry, 4317). Verhältnis zur Prometheus/Grafana-Kette auf dem ProDesk ungeklärt — noch nicht untersucht, wer das wozu eingerichtet hat. Ausserdem zwei nirgends erwähnte Netzwerk-Freigaben: `/mnt/wolf-ee` (NFS, Anker → ProDesk) und `/mnt/frawo-library` (CIFS, zeigt auf dieselbe `//10.1.0.94/radio`-Freigabe wie VM210) — Zweck unklar.

---

## 🏠 Alopri-Anbindung (Eltern, Stockenweiler) — neu 04.08.2026

Standort-Kopplung zwischen Rothkreuz und dem **Heimnetz der Eltern** (Fritzbox, `192.168.178.0/24`, WLAN "alopriwlan" — **nicht** dasselbe Netz wie der Flo-verwaltete ESXi/`frawo-docker-1` unter `10.30.8.0/24`, siehe Stockenweiler-Uplink-Notiz weiter unten).

**Aufbau:** WireGuard-Site-to-Site auf **CT106** (`10.1.0.239`), zweites Interface `wg1` neben dem bestehenden `wg0` (StudioPC-Fernzugang, unverändert). `wg1` **wählt sich aktiv nach draußen** zur MyFRITZ-Adresse der Eltern-Fritzbox (`yourparty.tech:59156`) — **keine neue Portweiterleitung am Rothkreuz-Gateway nötig**, passt zur bestehenden Regel „keine Portweiterleitung, alles von innen aufgebaut". Grund: das Rothkreuz-Gateway hängt hinter einer weiteren Vodafone-Box (Doppel-NAT, WAN-IP ist selbst schon `192.168.2.x`) — von dort wäre Port-Forwarding ohnehin brüchig gewesen.

Route `192.168.178.0/24` → nächster Sprung `10.1.0.239` liegt als statische Route auf dem UCG.

**Freigegeben (Least Privilege, in `wg1.conf` PostUp/PostDown, CT106):**
| Von | Nach | Zweck |
|---|---|---|
| `10.1.0.248` (HA-Eltern) | ganzes `192.168.178.0/24` | Smart-Home-Steuerung, volle Sicht |
| `192.168.178.153` (Drucker) | `10.1.0.94:445` (Fileserver SMB) | Scan-Ablage, nur dieser eine Port |
| ganzes `192.168.178.0/24` | `10.1.0.239:22` | Wolfs persönlicher Admin-Sprungbrett-Zugang (Standard-INPUT-Policy ist ACCEPT, kein neues Loch) |
| ganzes `192.168.178.0/24` | `10.1.0.100:8000` (Paperless auf CT110) | **Neu 06.08.2026:** Alois soll Dokumente von seinem PC aus erreichen können, nur dieser eine Port |

Alles andere zwischen den Netzen: **DROP** (Catch-all am Ende der `wg1`-Regeln).

**Scan-Ablage** (CT120 Fileserver, Samba-Freigabe `[scans]`, Pfad `/mnt/music/Scans`, existierte als leere Hülle schon vorher): Unterordner `Alois/`, `Heidi/`, `Franz/`, `Wolfgang/` angelegt. Eigener Samba-Nutzer `scanner` (nur Schreibrecht auf `[scans]`, sonst nirgends) — **Passwort liegt NICHT hier im Repo**, muss noch nach Vaultwarden (siehe Offen-Tabelle, analog #815-Konvention).

**Gefundene Geräte im Alopri-Netz (Stand 04.08.2026, per Scan über den Tunnel):** 1 Drucker (`.153`), 15× Shelly-Schalter/Steckdosen (`.61 .62 .64 .65 .72 .73 .78 .152 .171 .178 .189 .191 .193 .195 .198`), 3× Cast-fähige Geräte (`.161 .167 .170`), 1× HPE-Instant-On-Switch/AP (`.184`). Rest (`.119 .182 .185 .192 .173 .199 .214`) unklassifiziert (vermutlich Telefone/Tablets ohne eigenen Dienst).

✅ **Scan → Paperless** (überarbeitet 21.08.2026, erweitert 22.08.2026, siehe `OPERATIONS/PAPERLESS_OPERATIONS.md`): läuft jetzt über CT110 (`10.1.0.100:8000` / `paperless.frawo.tech`). Die Alopri-Scan-Ablage (Samba `[scans]` auf CT120) ist seit 22.08.2026 per systemd-Timer (`frawo-scan-ingest.timer` auf `stock-pve`) direkt an die Paperless-Consume-Pipeline angebunden — Scans in den Ordnern `Alois/`, `Heidi/`, `Franz/`, `Wolfgang/` werden alle 2 Min. abgeholt, mit Personen-Präfix versehen und vollautomatisch per Gemini OCR klassifiziert (Odoo-Aufgabe #1012 erledigt).

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

## 🖥️ StudioPC-Smart-Screen (neu 27.08.2026)

Touchscreen-Kiosk (#1039) und künftig Surface Go zeigen einen **unabhängigen virtuellen zweiten Monitor** des StudioPC — der Fernseher (Monitor 1) bleibt unberührt. Odoo #1097 (Projekt 105) hat den vollen Aufbau; Kurzfassung:

- **UltraVNC** auf StudioPC, virtuelles Display (DDEngine), Passwort gesetzt — Achtung: `createpassword -secure` erzeugt ein Format, das noVNC **nicht** versteht (Fehler „authentication rejected"). Immer **ohne** `-secure`.
- **websockify-Bridge** auf stock-pve (`novnc-studiopc-bridge.service`, Port 6080 → StudioPC LAN-IP `10.1.0.211:5900`), liefert `/opt/novnc` gleich mit aus.
- Host-Firewall stock-pve: 6080 nur für CT140 offen (gleiches Muster wie Paperless-Webhook).
- **Cloudflare:** `studiopc.frawo.tech` → Tunnel „FraWo-RK" → `10.1.0.128:6080`. CSP-Ausnahme (`frame-ancestors`) nur für `home.frawo.tech`/`.de`, damit der Reiter im HA-Kiosk eingebettet werden darf.
- **Cloudflare Access davor** (E-Mail-Einmalcode, nur `w.prinz1101@gmail.com`, 24h-Sitzung) — ohne das wäre die Seite nur durchs VNC-Passwort geschützt gewesen.
- HA-Dashboard `kiosk_dashboard.yaml` (VM210 haos, `10.1.0.40`): neuer Reiter „StudioPC" + Umschalt-Knöpfe (kiosk-mode blendet die normale View-Leiste aus).
- Cloudflare-API-Token `frawo_agent.cloudflare_dns_token` (Odoo `ir.config_parameter`) hat inzwischen auch **Access**-Schreibrechte (Wolf hat das selbst erweitert über die im Token freigegebene „API Tokens Write"-Berechtigung).

**Offen:** UltraVNC-Rules-Auffangregel (`* → Refuse`) fehlt noch · Windows-Firewall-Regel „nur Tailscale" lässt trotzdem LAN durch, Ursache ungeklärt · Surface Go noch nicht eingerichtet, unklares Tailscale-Gerät (`surface-go-frontend` zeigt Linux + 2 Monate inaktiv) · lokal/remote Smart-Routing (Split-Horizon-DNS) von Wolf gewünscht, noch nicht gebaut.

---

## 📻 Radio

🔴→✅ **Sendeplan seit dem 29.07.2026 komplett umgebaut, beim Audit
19.08.2026 entdeckt und hier nachgetragen** (die alte
Zeitfenster-Tabelle unten war komplett veraltet — wer/wann umgebaut
hat, ist noch nicht geklärt). **Kein Zeitplan mehr aktiv**
(`GET /api/station/1/schedule` liefert eine leere Liste) — stattdessen
vier gleichgewichtete Kanäle, die rund um die Uhr gemischt laufen:

| Playlist | Titel | Gewichtung |
|---|---|---|
| Channel 1 — Acoustik & Ambient | 1.299 | 3 |
| Channel 2 — Soft Groove | 3.376 | 3 |
| Channel 3 — Harder Styles | 1.963 | 3 |
| Channel 4 — Roadtrip & Classics | 1.513 | 3 |

Alle vier gleich gewichtet, kein Tageszeit- oder Wochentag-Bezug mehr,
keine separaten DJ-Show-Slots. **Wolf wusste davon nichts** (Stand
19.08.2026, nachgefragt). Verdacht: die parallele Sitzung von heute
arbeitet an einem "yourparty"-Projekt mit AzuraCast-Bezug (Skripte wie
`update_live_radio.py`/`_v2`/`_v3`, `enable_azuracast_streamers.py` im
selben Repo gefunden) und hat vermutlich schon länger am selben Sender
gearbeitet. **Noch nicht geklärt, nicht rückgängig gemacht** — Wolf
klärt das direkt mit der anderen Sitzung.

**Lautheit (Stand 29.07.2026, nicht neu gemessen):** Dateien schwanken um 11,7 dB, das **Sendesignal nur um 3,0 dB** bei −15,8 LUFS. Die Angleichung arbeitet.

⚠️ Der API-Schlüssel aus `reference_frawo_azuracast` ist **tot**. Verwaltung über die Datenbank:
`ssh stock-pve` → `qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE …'`
Grössere Abfragen als Datei einspielen (`docker cp`), sonst schluckt der Rückweg die Ausgabe. Tabellen heissen `station_playlists` (Plural).

---

## 🎵 Musikverwaltung (beets, CT120)

Läuft dort, weil die Platte **direkt eingehängt** ist (`/mnt/music`) — nicht über den CIFS-Umweg, an dem der AzuraCast-Scan früher hängenblieb.

| | |
|---|---|
| Erfasst | 9.264 Titel, 420 GB (Stand 29.07., seither Rekordbox-Import + Radio-Bridge-Uploads dazugekommen — nicht neu gemessen) |
| Genres | **16 kanonisch** statt 600 gewachsener Bezeichnungen |
| Alben über mehrere Genres verteilt | **0** (vorher 100) |
| Doubletten in der Rotation | **0** |

🔴→✅ **19.08.2026:** Die Platte (`/mnt/music_hdd`) war zu **100% voll**
(0 Byte frei) — dadurch scheiterte u. a. die Radio-Bridge (siehe unten).
Ursache: der `Quarantine`-Ordner war unbemerkt auf **1,4 TB**
angewachsen (statt der früher vermerkten "64 GB, 160 Dateien"). Nach
Rücksprache mit Wolf: `Duplicates` (1,1 TB, alle 25.737 Dateien
einzeln gegen die Hauptbibliothek verifiziert) und `Corrupt` (34 GB,
Stichprobe mit `ffmpeg` als wirklich unlesbar bestätigt) komplett
gelöscht. `Unidentified_Research` (324 GB) bewusst **nicht** angefasst
— braucht echte Durchsicht. Platte jetzt nur noch 43% voll.

**Zweistufiges Modell nach Discogs-Vorbild:** `genre` breit und **eine pro Album** (Alben bleiben zusammen), `style` spezifisch pro Titel.

**Im Explorer unter `M:\`:** `_nach_Genre\`, `_nach_Label\`, `_playlisten\` — als **Verweise**, nicht als Kopien. Keine Datei existiert doppelt.

**Playlisten für Rekordbox und Mixxx:**
`playliste-exportieren.sh warmup 'genre:House length:240..600'` → erzeugt Linux- und Windows-Fassung.

**Radio-Bridge (Fernbedienung, Details siehe `deployments/radio_bridge/`):**
Wolf kann als DJ von unterwegs (Handy) Titel in den Eingangsordner
hochladen — Webdienst auf `10.1.0.128:8888` (Token-geschützt), stößt
`beet import` + AzuraCast-Rescan an. War bis 19.08.2026 komplett
undokumentiert (per nmap-Audit gefunden), zwei echte Bugs behoben
(beets' `incremental`-Einstellung blockierte Wiederholungen; die
Erfolgsprüfung passte nicht zu `copy:no/move:no`). Über die echte API
getestet und bestätigt funktionsfähig.

---

## 💾 Sicherungen

| Was | Wohin | Wann | Ausser Haus? |
|---|---|---|---|
| Odoo DB + Filestore | `/mnt/data_family/odoo-sql-dumps` + Anker | stündlich :15 | ✅ |
| Radio (AzuraCast) | `/mnt/data_family/backups/azuracast` + Anker | 03:30 | ✅ |
| **PBS-Konfiguration** | `/mnt/data_family/pbs-config` + Cloud | 03:45 | ✅ |
| Container 101–150 | PBS auf dem Anker | 04:00 | ✅ |
| VMs 210 + 360 | `hdd-backup` (sdb1) | 05:30 | lokal |
| VM 360 → Cloud | Google Drive | täglich 07:00 | ✅ |
| VM 210 → Cloud | Google Drive | sonntags | ✅ |
| Musik → Cloud | Google Drive | stündlich | ✅ |

**DJ-Sticks → Cloud (neu 19.08.2026, ereignisbasiert statt Zeittakt):** Wolf nimmt als DJ mehrere USB-Sticks mit auf Tour. Steckt er einen an den ProDesk, sichert `dj-stick-sync@<Gerät>.service` (ausgelöst per udev-Regel `/etc/udev/rules.d/99-dj-stick.rules`, kein 5-Minuten-Zeittakt mehr) den Inhalt automatisch nach `gdrive:Stockenweiler/dj_sticks/<Name>`. Erkennung läuft über eine unsichtbare Markierungsdatei `.frawo-dj-stick` (bewusst getrennt vom sichtbaren Datenträgernamen, den Wolf frei wählt) — neue Sticks einmalig mit `/usr/local/bin/dj-stick-vorbereiten.sh <Einhängepfad>` vorbereiten. Ersetzt die alte `musicstick-sync.timer`-Lösung (lief alle 5 Min. ins Leere, seit 23.07. nichts mehr synchronisiert, weil das Auto-Einhängen zwischenzeitlich deaktiviert war) — alte Dateien liegen unter `/root/systemd-leichen-backup-20260819/`, nicht gelöscht. `/mnt/musicstick` per NFS nur noch für den StudioPC (`10.1.0.211`) freigegeben, vorher fürs ganze `10.1.0.0/24`-Netz lesbar (unnötig weit, jetzt Least-Privilege). ⚠️ **Noch nicht mit einem echten Stick End-zu-Ende getestet** — beim ersten benutzten Stick prüfen, ob die Sicherung wirklich ankommt.

### Welche Platte ist welche (ProDesk, geprüft 01.08.2026)

Buchstaben verschieben sich — **Seriennummer entscheidet**.

| Gerät | Modell / Seriennummer | Eingebunden | Zustand |
|---|---|---|---|
| `sdc` | **WD Elements 1 TB** · `WD-WXD1A47ATEJL` | `/mnt/data_family` — **alle Sicherungen** | ✅ gesund, 0 Fehler |
| `sdd` | **WD Elements 2 TB** · `WD-WX62E302VF6E` | `/mnt/music_hdd` — Musik | ✅ gesund, 0 Fehler |
| `sdb` | USB Disk 3.0, 58 GB | `/mnt/sdc-ssd` | in Ordnung |
| `sda` | **„VendorCo ProductCode", USB `048d:1234`** | **nirgends** | 🔴 **Fälschung — raus damit** |

🔴 **`sda` ist kein Defekt, sondern eine Fälschung.** Controller *Chipsbank CBM2199*, meldet 982 GB, hat real **~64 GB**: bis 60 GB liest sie stabil, ab 65 GB bei jedem Lesen etwas anderes. Alles darüber Geschriebene war nie gespeichert. **Nicht formatieren, nicht wiederverwenden — wegwerfen.** Erkennbar als das einzige Gerät, das **kein** „WD Elements" ist.

**Backup-TÜV** (`frawo-backup-tuev.sh`, 08:00) prüft **11 Ergebnisse**, nicht Vorgänge: Ist eine Datei da, ist sie gross genug, jung genug — **und lesbar**? Genau dieser blinde Fleck hatte den wochenlangen Ausfall möglich gemacht.

🔴→✅ **16.08.2026:** Crontab auf `pve` zeigte 14 Tage auf gelöschte/falsche Skriptpfade (siehe Fallen-Tabelle oben) — Odoo-Cloud-, Radio- und PBS-Konfig-Sicherung liefen lautlos ins Leere. PBS-Containersicherung (ganze CT140) lief die ganze Zeit durch, akuter Datenverlust war nie gegeben. Crontab repariert (alte Fassung gesichert unter `/root/crontab.backup-20260816`), alle 4 Skripte manuell verifiziert, TÜV meldet wieder **11/11**.

**Wiederherstellungstest** sonntags 09:00: spielt die Odoo-Sicherung in eine Wegwerf-Datenbank und vergleicht Zeile für Zeile.

---

## 🔒 Sicherheit

- **Keine einzige Portweiterleitung** am Gateway. Aller Zugang über Cloudflare-Tunnel und Tailscale, beide von innen aufgebaut.
- **Host-Firewall auf beiden Knoten aktiv**, Grundregel DROP.
- SSH auf beiden Knoten: **nur Schlüssel**, kein Passwort.
- Gäste-WLAN erreicht vom Server-VLAN nur DNS und Zeitserver.
- Die Überwachungs-Ports (19022/19100/19182) sind **nur für Prometheus** offen.
- **19.08.2026:** `fail2ban` (SSH-Schutz) + `rkhunter` (Rootkit-Scanner,
  keine Funde) auf beiden Servern installiert. Alle Pakete + Kernel
  aktualisiert (ProDesk 149, Anker 89), beide sauber neu gestartet und
  voll verifiziert. Details: `DOCS/infrastruktur-audit-2026-08-19.md`.
- **20.08.2026:** Der gestrige Grundzustand ist jetzt **als Ansible-Code
  festgehalten** (`ansible/`, siehe `ansible/README.md`) — SSH-Härtung,
  Firewall-Drift-Schutz, Autostart-Flags, automatische
  Sicherheits-Updates, fail2ban und (nur Anker) Kernel-Panic-Auto-Reboot.
  Auf `stock-pve` **und** `anker-pve` real angewendet, gegen die
  laufenden Dienste geprüft (Website/Radio/Vault/SSH/Firewall nach jedem
  Lauf gesund), keine Ausfallzeit.

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
| **Gefälschten USB-Stick entsorgen** — meldet 982 GB, hat real **64 GB** (siehe unten) | Wolf | #881 |
| EGS-Nachverhandlung: 12 kW genehmigt, WP braucht 13–14 kW | Wolf | #885 |
| Punkte, die nur Wolf erledigen kann | Wolf | #886 |
| CT130 ist der einzige privilegierte Container | geplant | #887 |
| uptime-kuma: aufräumen oder abschalten | Entscheidung | #888 |
| Jingles / Station-IDs einsprechen | Wolf | — |
| Tags in die Dateien schreiben (~7.400 Dateien, entsprechender Cloud-Upload) | Entscheidung | — |
| Feste IP (DHCP-Reservierung) für Alopri-Drucker `.153` auf der Fritzbox | Wolf | — |
| ~~Alopri-Smart-Geräte (15 Shelly, 3 Cast) innerhalb Home-Assistant hinzufügen~~ — **erledigt 06.08.2026**, siehe `artifacts/stockenweiler_inventory/home_assistant_audit_2026-08-06.md` | — | — |
| Scanner-SMB-Passwort (CT120) und Paperless-Zugangsdaten (API-Token, Gemini-Key, Webhook-Geheimnis) nach Vaultwarden übertragen | Wolf | #1010 |
| Paperless: E-Mail-Postfächer (info@/wolf@frawo.tech) per IMAP anbinden — wartet auf Server/Zugangsdaten von Wolf | Wolf | #1008 |
| ~~Alopri-Scan-Ablage (Samba `[scans]` auf CT120) noch nicht an die neue Google-Drive-Paperless-Pipeline angeschlossen~~ — **erledigt 22.08.2026** via `frawo-scan-ingest.timer` | — | #1012 |
| **Flos Server ("frawo-docker-1") ist endgültig weg** (Wolf bestätigt 05.08.2026). Nextcloud, lokale AzuraCast, n8n-Alt, ollama, qdrant liefen dort ebenfalls — Bedarf für Neuaufsetzen jeweils einzeln klären | Wolf | — |

---

## 🧭 Prinzipien

- **Odoo = Quelle der Wahrheit** für Menschen und Agenten.
- **Am Ergebnis messen, nicht am Vorgang.** Ob ein Skript lief, sagt nichts darüber, ob eine brauchbare Datei entstand.
- **In beide Richtungen prüfen.** Ein Alarm, der nie ausgelöst hat, ist kein Beweis.
- **Verschieben statt löschen.** Quarantäne-Ordner, Sicherungskopien, Rückwege.
- **Roadmap:** 1) WP-Stockenweiler-3 2) Website & Verleih professionell 3) selbstverwaltetes Odoo via Agent.

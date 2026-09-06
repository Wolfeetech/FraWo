# NOW — Der echte Live-Stand

> **Zuerst lesen.** Diese Datei beschreibt, **was läuft** — nicht, was passiert ist.
> Historie steht in der Git-Historie, Entscheidungen und Aufgaben in **Odoo (CT140, `10.1.0.112:8069`) = einzige Quelle der Wahrheit**.
>
> Stand: **29.07.2026** als Grundgerüst, seither laufend punktuell
> nachgetragen (zuletzt **23.08.2026** — Infra-Vollprüfung: Sicherungen 11/11,
> Thin-Pool-Lage, Container-`discard`-Lücke, Abschaltung des verwaisten
> `frawo-tech.de`-Tunnels. Audit-Grundlage weiterhin
> `DOCS/infrastruktur-audit-2026-08-19.md`).

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
| **`fstrim -av` auf dem Wirt „räumt auf"** | erreicht die **Container**-Dateisysteme **nicht**. In LXC gelöschte Dateien bleiben dauerhaft im LVM-Thin-Pool belegt, weil die Container ohne `discard` laufen. So hielt CT110 auf dem Anker 90 GB Altlast fest, der Pool stand bei 82,8 % | Für Container `pct fstrim <id>` — läuft jetzt wöchentlich per `/usr/local/bin/frawo-ct-fstrim.sh` (So 04:30, beide Knoten) |
| **`systemctl stop <dienst>` und der Prozess lebt weiter** | derselbe Dienst kann zusätzlich **in einem Container** laufen. Beim Abschalten des `cloudflared` auf dem Anker-Wirt blieb eine zweite Instanz in CT100 aktiv — sichtbar nur, weil `pgrep` danach nochmal geprüft wurde | Nach jedem Stoppen `pgrep -a <name>` gegenprüfen; bei Treffern `cat /proc/<pid>/cgroup` zeigt den Container |
| **Samba `veto files` in `smb.conf` ändern und nur reloaden** | `testparm` zeigt die neue Regel korrekt an, die Freigabe versteckt den Ordner trotzdem **nicht** — auch nach frischer Verbindung/Windows-Neu-Mount. `systemctl status smbd` bleibt dabei unauffällig aktiv | Bei Sichtbarkeits-/Zugriffsregeln (`veto files`, `hide files`, `valid users`) reicht ein Reload nicht immer — `systemctl restart smbd` und danach mit frisch getrenntem Client (`net use X: /delete` + neu verbinden) gegenprüfen |
| **`azuracast_cli azuracast:media:reprocess 1`** | setzt bei **allen** Titeln `mtime = 0` (hier 26.000). `CheckMediaTask` hält die dann für „geändert" und stellt sie **alle 5 Minuten neu** in die Warteschlange — und **leert diese zu Beginn jedes Laufs wieder** (`clearQueue()` als erste Zeile in `run()`). Neue Dateien reiht `processNewFiles()` **ganz zuletzt** ein, hinter ~26.000 Altaufträgen. Der **eine** Worker schafft ~20 Nachrichten/Minute, das Fenster ist 5 Minuten → die letzten ~25.900 werden nie erreicht. **Neue Titel tauchen dadurch ~20 Stunden lang überhaupt nicht auf**, ohne jede Fehlermeldung | Auf dieser Bibliothek **nie** aufrufen. Aufräumen (setzt genau den Wert, den AzuraCast nach erfolgreicher Verarbeitung selbst schreibt, `time()+5`): `UPDATE station_media SET mtime = UNIX_TIMESTAMP()+5 WHERE mtime = 0 AND length > 0;` |
| **Neuer Ordner erscheint nicht im Radio, „Scan hängt"** | fast immer **nicht** der CIFS-Mount, sondern die Warteschlange oben. Gegenprobe 04.09.2026: Massenlesen über die Freigabe schafft **1,7 GB/s**, der komplette Baumdurchlauf (32.879 Dateien) läuft in **113 s** sauber durch. Der Prozess steht nur deshalb minutenlang in `D` (I/O-Wartezustand), weil zusätzlich `UpdateStorageLocationSizesTask` denselben Baum abläuft | Nicht am Mount schrauben. Erst messen: `valkey-cli XLEN messages:media` und `XINFO GROUPS messages:media` (`entries-read` gegen `lag`). Einzelnen Ordner sofort einspielen: seine Einträge im Stream suchen und die Gruppe gezielt davorsetzen — `valkey-cli XGROUP SETID messages:media symfony <ID direkt davor>` (löscht nichts, überspringt nur die Altaufträge) |
| **`beet modify` mit `feld:^wert` als vermeintlichem Regex-Anker** | `^` direkt nach `feld:`/`feld::` wird **nicht** als Regex-Start-Anker gelesen, sondern als **Negations-Präfix der ganzen Bedingung** — `'^album:Beatport 100 Afro House' 'vibe::^$'` traf am 04.09.2026 **alles außer** diesem einen Album (2.976 Falschtreffer statt 181 Richtige) | Negation ist `^feld:wert` **vor** dem Feldnamen. Einen echten Regex-Anfangsanker will man fast nie — Substring (`feld:wert`) oder `feld::wert$` (Endanker) reichen fast immer. Nach jeder neuen Query-Form erst `\| wc -l` gegenprüfen, ob die Trefferzahl plausibel ist, **bevor** `modify` läuft |
| **Komma innerhalb eines `feld::regex`-Werts** | `genre::^Techno,` sieht wie ein Ganzzeichen-Match aus, wird aber **immer** am Komma aufgespalten — auch mit Backslash (`\,` ergibt einen Regex-Parsefehler, das Komma wird schon vorher von beets selbst entfernt). Die dadurch entstehende leere zweite Hälfte ignoriert **jede** andere Bedingung (auch `vibe::^$`) und trifft Titel unabhängig vom aktuellen Tag-Stand. Kostete am 04.09.2026 **5.437 Falschtags** in 4 Schritten eines Batch-Skripts, inkl. Überschreiben bereits korrekter/EXCLUDED-Tags (u.a. komplette Ben-Liebrand-, Job-Jobse-, Classics-of-Form-, Mac-Miller-Cluster zurückgesetzt und neu vergeben) | Komma in Mehrfach-Genre-Strings (`"Techno, Electronic"`) **gar nicht** in die Query aufnehmen — nur der Teil **vor** dem Komma reicht als Präfix-Anker (`genre::^Techno` statt `genre::^Techno,`), das trifft `"Techno, Electronic"` genauso wie reines `"Techno"`. Jede neue Genre-Query zuerst isoliert mit `wc -l` gegen eine plausible Hausnummer prüfen |
| **`frawo-music-ingest.timer` (alle 5 Min.)** | lief seit 26.08.2026 durch, **2.574 von 2.576 Läufen haben 0 Titel** in Master_Library aufgenommen (AcoustID/MusicBrainz-Lookup schlägt aktuell durchgehend fehl, HTTP 400/503). Trotzdem schrieb **jeder** Lauf ~6 Titel nach `Quarantine/Duplicates` und ~2 nach `Quarantine/Corrupt` — dieselben 8 feststeckenden Dateien (stale CIFS-Pfad, `FileNotFoundError` beim Move), aber mit hochgezähltem Dateinamen (`_new_2374` …) statt Fehler zu erkennen. Erklärt das in der Musikserver-Landkarte als größte offene Frage markierte `Quarantine`-Wachstum (439 GB) fast vollständig — **15.445** bzw. **5.161** Quarantäne-Einträge über die Laufzeit. Vermutlich auch die Quelle der geraten-statt-recherchiert BPM/Mood-Werte, die die Radio-Vibe-Kuration überhaupt erst nötig gemacht haben | Am 04.09.2026 gefunden und **gestoppt+disabled** (`systemctl disable --now frawo-music-ingest.timer`, reversibel mit `enable --now`). Vor Wiederaktivierung: BPM/Mood bei fehlgeschlagenem MusicBrainz-Match auf „unbekannt" statt Schätzwert umstellen, stecken gebliebene Batch-Datei erst einzeln klären. **Aufräumen erledigt** (nach Freigabe): `Duplicates` (14.229 Dateien, 448 GB), `Corrupt` (4.724 Dateien, 175 MB) und der gleich mitgefundene `Non_Music`-Ordner (9.700 0‑Byte-Geisterdateien, selber Bug) geleert — Stichprobe vorher gegen `Master_Library` verifiziert (Songs lagen dort längst korrekt vor). `/mnt/music` jetzt **480 GB / 26 % belegt** (vorher 929 GB / 50 %). `Unidentified_Research` (6,2 GB) bewusst unangetastet, braucht echte Durchsicht. Odoo #1268 |
| **Massen-Scan über `/mnt/music` direkt nach großem Löschvorgang** | Ein `find … \| xargs -P4` Lesetest über die ganze Platte meldete am 04.09.2026 **47.528 „kaputte" Dateien** — Panik unnötig: 37.000 davon waren nur Cover-Thumbnails, und von den restlichen ~1.067 „kaputten" Musikdateien waren beim ruhigen Einzeltest **1.001 einwandfrei lesbar**. Paralleles Lesen direkt nach einem Massen-Löschvorgang setzt FUSE/ntfs-3g auf dieser 5400-rpm-Platte kurzzeitig unter Last und erzeugt dadurch selbst I/O-Fehler | Verdacht auf Beschädigung **immer einzeln, ohne Last** nachprüfen (`dd if=… of=/dev/null bs=1M count=1`), nie direkt nach einem Bulk-Löschvorgang pauschal scannen. SMART-Werte (`smartctl -a`) bleiben der verlässlichere erste Check |
| **Sonderzeichen in Ordnernamen gehen beim Kopieren über eine Text-Zwischendatei verloren** | Genre-Ordner wie `Ambient  Experimental` (Slash im Genre-Namen durch Sonderzeichen ersetzt) wurden beim Export der Pfadliste in eine `.txt`-Datei und Wiedereinlesen durch ein normales Leerzeichen ersetzt — das Skript suchte danach am falschen Pfad und meldete „Datei nicht gefunden", obwohl die Datei da war (weitere Ursache der 47.528er-Falschmeldung) | Pfadlisten mit Sonderzeichen nicht durch `grep`/`sed`/Text-Dateien schleusen — direkt mit `os.listdir()`/`find -print0` arbeiten und Python `open(path, 'rb')` statt eines Pfad-Strings aus einer Zwischendatei |
| **OpenClaw-Bot (`@Frawo_bot`) hatte monatelang keinen echten Odoo-Zugriff** | `openclaw mcp probe odoo` meldete `Connection closed` — der gespeicherte `ODOO_API_KEY` war ungültig geworden, der Server fiel intern still auf Passwort-Login zurück (**das funktioniert nur bei manuellem Testaufruf mit vollem Container-Environment**, nicht beim echten Bot-Start, der die MCP-Server-Umgebung isoliert nur mit den in `openclaw.json` hinterlegten `env`-Werten startet — dort steht kein Passwort). `openclaw.json` lag zudem an `/root/.openclaw/openclaw.json` **im Container**, nicht im gleichnamigen Pfad auf dem Host — `cat ~/.openclaw/openclaw.json` auf dem Host zeigt eine andere, veraltete Datei | Neuen API-Key erzeugen (`env['res.users.apikeys']._generate('rpc', 'Name', False)` — vierter Parameter `expiration_date` ist Pflicht), per `openclaw mcp set odoo '{...}'` **im Container** (`docker exec openclaw …`) eintragen, mit `openclaw mcp probe` bestätigen, dann `openclaw mcp reload`. Immer `docker exec openclaw cat ...` statt der Host-Pfade prüfen |
| **Paperless: `paperless_mail.tasks.process_mail_accounts` hängt fest → würgt die ganze Dokumenten-Pipeline ab** | Stratos IMAP-Server schloss die Verbindung vorzeitig (`* BYE Autologout; idle for too long`), weil MailAccount #1 auf Port 993 mit `imap_security = 1` (NONE / unverschlüsselt) lief — Port 993 erfordert zwingend SSL/TLS. Task hing bis zum Celery-Hard-Limit (1800 s) und blockierte `consume_file`. Behoben am 06.09.2026: `imap_security = 2` (SSL) gesetzt. SSL-Handshake läuft in 1,0s durch, Celery blockiert nicht mehr. Echter Postfach-Abruf wartet auf Strato-Postfach/Passwort-Bestätigung (Odoo #1285). |
| **`scripts/tools/sync_odoo_files.py` deployt nur Dateien aus einer festen Liste (`FILES_TO_SYNC`)** | `models/__init__.py` importierte `mail_message.py` bereits, die Datei selbst stand aber nicht in der Liste — ein routinemäßiger Sync von `controllers/main.py` schickte `__init__.py` mit dem aktiven Import, aber nie die zugehörige Datei nach CT140. Legte kurzzeitig das komplette `frawo_agent`-Modul (Radio, Anker-Tracker, Agent-API, Kalender-Teile) lahm. Die Datei war zusätzlich im Repo durch einen Bearbeitungsfehler syntaktisch kaputt (HTML-Entities `&lt;`/`&gt;` statt echter Zeichen, fehlende String-Quotes) — fiel erst beim nächsten Deploy auf, nicht beim Schreiben. Behoben 06.09.2026 (Odoo #1287), `mail_message.py` zur Liste ergänzt | Bei jeder neuen Datei, die `models/__init__.py` importiert: sofort in `FILES_TO_SYNC` aufnehmen — nie den Import committen, ohne die Datei im selben Zug in die Sync-Liste einzutragen. Vor jedem Sync einer `.py`-Datei mit neuem Import lokal `python -m py_compile` gegenprüfen |
| **`openclaw config set …` auf CT150 löst IMMER einen vollständigen Gateway-Reload aus** | Der Reload liest **alle** Schlüssel neu — auch `agents.defaults.model`. Wer nur Telegram/exec härtet, aktiviert damit ein evtl. gerade eingetragenes, kaputtes Modellprofil mit. So am 06.09.2026 Jarvis 5 Minuten stumm geschaltet (Anthropic-Profil: zwei Modellnamen existieren nicht, der Key ist bis 01.10.2026 gesperrt) | Vor jedem `config set` zuerst `openclaw config get agents.defaults.model` prüfen. Funktionierend: `github-copilot/claude-sonnet-5`. Modellnamen nie aus dem Gedächtnis eintragen — Test: `docker exec openclaw openclaw agent --session-id check --message "Antworte nur mit OK"` (ohne `--deliver`) |
| **Odoo-Parameter `frawo_agent.azuracast_api_key` war monatelang tot (403)** | Alles, was in Odoo über diesen Key zu AzuraCast spricht, scheiterte still — u. a. der Skip-Vote (`hate`) der Radio-Seite. Aufgefallen erst beim Bau der Kanal-Demokratie (06.09.2026), weil der neue Client 0 Playlisten bekam | Der funktionierende Key liegt in `deployments/musikverwaltung/rekordbox_sync/.env` (nicht eingecheckt) und jetzt auch wieder im Odoo-Parameter. Bei „AzuraCast antwortet nicht": erst `curl -sk -o /dev/null -w '%{http_code}' -H "X-API-Key: …" https://10.1.0.38/api/station/1/playlists` — 403 heißt Key, nicht Netz |


⚠️ **Nach direkten Datenbank-Änderungen an AzuraCast immer** `azuracast_cli azuracast:radio:restart 1` — sonst merkt liquidsoap nichts. Gilt auch für **neue Playlisten**: Titel und `.m3u` entstehen automatisch, aber liquidsoap kennt die Playlist erst nach dem Neustart (`grep -c -i <name> …/config/liquidsoap.liq` muss > 0 sein).

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
| ~~CT103~~ | ~~npm~~ | ~~`10.1.0.149`~~ | 🗑️ **gelöscht 23.08.2026** — hatte **0 Proxy-Einträge**, einziges Zertifikat für `monitor.yourparty.tech` (Domain tot). Lief 10 Monate ohne Funktion, abgelöst durch die Cloudflare-Tunnel. Rückweg: PBS-Sicherung `pbs-frawo:backup/ct/103/2026-08-23T02:00:29Z`, Konfig unter `/root/ct103.conf.geloescht-20260823` |
| CT106 | wireguard | `10.1.0.239` | VPN |
| CT108 | vaultwarden | `10.1.0.95` | Passwortsafe → `vault.frawo.tech` |
| CT110 | n8n | `10.1.0.100` | Automatisierung + **Paperless-ngx** (Docker `paperless-webserver`, Port 8000, extern `paperless.frawo.tech`) — seit 21.08.2026 die **einzige** Instanz, komplett neu verdrahtet: Google-Drive-Push-Inbox → OCR → Gemini-Klassifikation → Ablage in bestehende Drive-Ordner + Odoo-Aufgabe. Details: `OPERATIONS/PAPERLESS_OPERATIONS.md`, Odoo-Aufgabe #998 |
| CT120 | fileserver | `10.1.0.94` | Samba **und Musikverwaltung (beets)** |
| CT140 | frawotech-web | `10.1.0.112` | **Odoo 19** → `frawo.tech` |
| CT150 | monitoring-stack | `10.1.0.35` · TS `100.100.115.80` | Prometheus, Grafana, Alertmanager |
| VM210 | azuracast-vm | `10.1.0.38` | **Radio** → `funk.frawo.tech` |
| VM360 | homeassistant-eltern | `10.1.0.248` | Home Assistant Testkunden (Eltern) — **IP hier korrigiert 04.08.2026, stand fälschlich auf `.40`** |

Zum Vergleich: `10.1.0.40` ist ein **anderes** haos (VM210 **auf proxmox-anker**, nicht ProDesk) — nicht verwechseln, zwei getrennte Home-Assistant-Instanzen.

**Touchscreen-Kiosk (neu 23.08.2026):** Ein günstiger Touch-Monitor hängt per DP+USB direkt am **stock-pve** (dem HP ProDesk selbst, nicht an anker/Lenovo — das war am 22.08. kurz vertauscht). Lokaler User `kiosk` startet per Autologin auf `tty2` (tty1 bleibt normale Root-Konsole) einen Chromium-Vollbild-Kiosk, der die Home-Assistant-Übersicht `kiosk-frawo` von `10.1.0.40:8123` (VM210 haos auf **anker-pve**) anzeigt — Anzeige-Gerät und Dashboard-Inhalt liegen also bewusst auf zwei verschiedenen Knoten. `xserver-xorg-legacy` + `Xwrapper.config (allowed_users=anybody)` nötig, sonst VT-Berechtigungsfehler. Details/Fortschritt: Odoo-Aufgabe #1039.

### Anker

CT130 `radio-node` (`10.1.0.200`) — ✅ seit 20.08.2026 **unprivileged** (`nesting=1,keyctl=1`), war zuvor der einzige privilegierte Container von 13 (Odoo #887, jetzt erledigt). Betreibt Docker: Radio-Backend, PostgreSQL, Redis, **uptime-kuma** (`:3001`, zweites Überwachungssystem → Odoo #888). VM240 = **PBS-FraWo** (`10.1.0.7`) — 🔴 Backups liegen auf derselben Platte wie das Betriebssystem, Volume Group ist voll (0 freie PV-Extents auf `pve`) — braucht neue Hardware/Storage, nicht per Konfig lösbar.

~~CT110 `storage-node`~~ — 🗑️ **gelöscht 23.08.2026.** War **vollständig leer**: kein laufender Dienst, kein Docker, 7,5 von 98 GB belegt (nur Grundsystem), blockierte aber 100 GB Zuteilung im Thin-Pool. **Rückweg:** `google-drive:backup/vzdump-lxc-110-2026_08_23-04_02_52.tar.zst`, Konfig unter `/root/ct110.conf.geloescht-20260823`.

🔴→✅ **VM211 `azuracast-vm` (Anker) — scharfe Falle entschärft 23.08.2026.** Überbleibsel der Radio-Migration vom 21.08.: gestoppt, aber mit **`onboot: 1`** und **derselben MAC-Adresse `BC:24:11:DE:76:67` wie die produktiv laufende Radio-VM210 auf dem ProDesk**, beide an `vmbr0`. Beim nächsten Neustart des Ankers wäre sie automatisch gestartet → **doppelte MAC im selben Netz → Radioausfall** mit sehr schwer auffindbarem Fehlerbild. Jetzt `onboot: 0` (Konfig gesichert unter `/root/vm211.conf.backup-20260823`). Ihre Platte liegt als 37,5-GB-`.qcow2` auf `stockenweiler-data` (nicht im Thin-Pool) — als frische Rückfall-Kopie bewusst behalten.

CT150 `openclaw` (`10.1.0.31` · TS `100.72.154.15`) — **das einzige OpenClaw-Gateway**, Docker, Port 19000, Anmeldung per **Token**. **Gehärtet 06.09.2026 (Odoo #1319):** Telegram `dmPolicy=pairing`, `allowFrom`/`groupAllowFrom` nur Wolf (`5924907152`), `groupPolicy=allowlist`; `tools.exec.mode=auto` (vorher `full`). `gateway.bind=tailnet` ist gesetzt, aber **wirkungslos** — im host-network-Container fehlt das tailscale-Binary, Port 19000 lauscht weiter auf `0.0.0.0` (einzige Clients: StudioPC über Tailscale + localhost). Offener Vorschlag: Proxmox-Firewall `/etc/pve/firewall/150.fw`, 19000/19001 nur aus `100.64.0.0/10` + loopback. Jarvis liest beim Start nur `workspace/AGENTS.md` — dort hängt seit 06.09. der Abschnitt „FraWo Agenten-Protokoll" mit Verweis auf `AGENTS-PROTOCOL.md` (Master-Kopie; die Sync verstümmelt UTF-8 → `grep -c "???"` muss 0 sein). Backups: `openclaw.json.bak-20260906-hardening`, `AGENTS.md.bak-20260906`, `AGENTS-PROTOCOL.md.bak-20260906`. Übersteht einen Neustart (CT `onboot`, Docker aktiviert, Container `unless-stopped`). Arbeitsplätze verbinden sich als **Node** dorthin — auf dem StudioPC die Aufgabe „OpenClaw Node" (`.openclaw\node.cmd`, wartet auf Tailscale, startet sich selbst neu, Protokoll in `.openclaw\logs\node-host.log`). Ein **zweites** Gateway auf dem StudioPC gehört nicht dorthin und kann gar nicht starten (Odoo #893).

🔴→✅ **Nebenstruktur auf dem Anker — beim Audit 19.08.2026 gemeldet, am 23.08.2026 aufgeklärt:**

| Was | Stand 23.08.2026 |
|---|---|
| `netdata` (19999/8125) | bereits **inaktiv**, kein Autostart — erledigt |
| `otel-plugin` (OpenTelemetry, 4317) | **weg**, Einheit existiert nicht mehr |
| `glances` (61209) | läuft, lauscht aber **nur auf `127.0.0.1`**, ~47 MB — bewusst gelassen, keine Gefahr |
| `cloudflared` | **abgeschaltet** (Wirt **und** CT100), siehe unten |

**Der `cloudflared` war der eigentliche Fund:** Er lief **seit 20.10.2025 durchgehend und doppelt** — einmal auf dem Wirt, einmal im Container CT100 („toolbox"), beide mit derselben Tunnel-Kennung `7ceb61ed…` für die **zweite Domain `frawo-tech.de`** (mit Bindestrich, nicht `frawo.tech`). Die Weiterleitungsziele des Wirt-Tunnels zeigten ins **IoT-Netz** (`10.4.0.21/22/24/26`) — alle vier tot, Altlast aus einer früheren Netzstruktur.

⚠️ **Nicht verwechseln:** Die Produktion läuft über einen **anderen** Tunnel (`add7e967…`, Docker-Container `frawotech-cloudflared-1` in **CT140 auf dem ProDesk**). Die Einträge für `frawo.tech` in der CT100-Konfiguration waren wirkungslose Altlast. Vor dem Abschalten geprüft, danach verifiziert: frawo.tech 200 · funk 302 · vault 200 · paperless 302 — unverändert.

**Ehrliche Einordnung:** Es lag **kein aktives Leck** vor — über den Tunnel floss nichts, die Ziele antworteten nicht. `vault.frawo-tech.de` antwortet weiterhin (200), das läuft aber über die Produktivkette; Vaultwarden ist unter `vault.frawo.tech` ohnehin bewusst öffentlich. Der Nutzen war das Beseitigen einer **geladenen Waffe**: sobald irgendwann etwas unter einer der IoT-Adressen geantwortet hätte, wäre es schlagartig öffentlich gewesen. Konfigurationen gesichert (`/root/cloudflared-config-20260823-vor-abschaltung.yml`, je Wirt und CT100), Cloudflare-DNS **unangetastet** — voll umkehrbar. `odoo.frawo-tech.de` und `cloud.frawo-tech.de` liefern seither 404. Odoo-Aufgabe #1067.

**Die zwei „Freigaben" — am 23.08.2026 aufgeklärt, beide harmlos:**

- `/mnt/wolf-ee` ist **gar keine Netzwerk-Freigabe**, sondern ein lokales Verzeichnis mit 780 KB pip-Zwischenspeicher vom 27.05.2026 (`hs27_root_relief/root-home/.cache/pip`). Damals wurde Platz auf der Systemplatte geschaffen und der Cache hierher verschoben. Wegwerf-Daten, kein fstab-Eintrag.
- `/mnt/frawo-library` (CIFS → `//10.1.0.94/radio`) **scheitert bei jedem Mount-Versuch mit `Permission denied`** — die Zugangsdaten in `/root/.smbcreds` stimmen nicht mehr. Wegen `nofail` meldet der Systemstart das nie. 🔴 **Das ist ein echter Funktionsausfall:** CT100 bindet die Freigabe als `mp0` nach `/srv/media-library/music-network` ein — dem dortigen **Jellyfin fehlt damit seine Musikbibliothek**. Fix braucht die korrekten SMB-Zugangsdaten des Fileservers (CT120).

### 🗑️ CT100 „toolbox" — am 23.08.2026 gelöscht

War der Rest eines aufgegebenen Projekts **„homeserver2027" (hs27)** mit komplett anderer Netzstruktur (`10.4.0.x`, `*.hs27.internal`). Nichts davon bediente die heutige Produktion — im Einzelnen nachgemessen:

| Dienst | Befund |
|---|---|
| `caddy` | proxyte **ausschliesslich** auf tote `10.4.0.x`/hs27-Ziele |
| `adguard` | letzte Anfrage **16.07.2026** — die produktiven sind CT101 ProDesk (`10.1.0.52`, schreibt laufend) und CT101 Anker (`10.1.0.27`) |
| `uptime-kuma` | lief zwar, überwachte aber fast nur tote Ziele; **0 Benachrichtigungen** aktiv, **0 Zugriffe** in 24 h. Die echte Instanz ist CT130 (8 Prüfungen auf die reale Produktion) |
| `openclaw.service` | **Zombie** — systemd meldete „aktiv", antwortete aber nicht; **Ollama war nicht einmal installiert**. Kein Gateway, nur ein Rest des eingestellten Lokal-KI-Versuchs |
| `jellyfin`, `open-webui` | vorab entfernt — open-webui hatte **0 Chats, 0 Benutzer, 0 Dokumente** |

Auch der 10 Monate verwaiste `frawo-tech.de`-Tunnel lief hier. **Rückweg:** Sicherung `google-drive:backup/vzdump-lxc-100-2026_08_23-04_00_17.tar.zst` (7,5 GB, vom Löschtag), Konfig unter `/root/ct100.conf.geloescht-20260823`. Odoo #1068.

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

**Scan-Ablage** (CT120 Fileserver, Samba-Freigabe `[scans]`, Pfad **`/mnt/music/_Dokumente/Scans`** — seit 04.09.2026, vorher `/mnt/music/Scans`): Unterordner `Alois/`, `Heidi/`, `Franz/`, `Wolfgang/` angelegt. Eigener Samba-Nutzer `scanner` (nur Schreibrecht auf `[scans]`, sonst nirgends) — **Passwort liegt NICHT hier im Repo**, muss noch nach Vaultwarden (siehe Offen-Tabelle, analog #815-Konvention).

**Gefundene Geräte im Alopri-Netz (Stand 04.08.2026, per Scan über den Tunnel):** 1 Drucker (`.153`), 15× Shelly-Schalter/Steckdosen (`.61 .62 .64 .65 .72 .73 .78 .152 .171 .178 .189 .191 .193 .195 .198`), 3× Cast-fähige Geräte (`.161 .167 .170`), 1× HPE-Instant-On-Switch/AP (`.184`). Rest (`.119 .182 .185 .192 .173 .199 .214`) unklassifiziert (vermutlich Telefone/Tablets ohne eigenen Dienst).

✅ **Scan → Paperless** (überarbeitet 21.08.2026, erweitert 22.08.2026, siehe `OPERATIONS/PAPERLESS_OPERATIONS.md`): läuft jetzt über CT110 (`10.1.0.100:8000` / `paperless.frawo.tech`). Die Alopri-Scan-Ablage (Samba `[scans]` auf CT120) ist seit 22.08.2026 per systemd-Timer (`frawo-scan-ingest.timer` auf `stock-pve`) direkt an die Paperless-Consume-Pipeline angebunden — Scans in den Ordnern `Alois/`, `Heidi/`, `Franz/`, `Wolfgang/` werden alle 2 Min. abgeholt, mit Personen-Präfix versehen und vollautomatisch per Gemini OCR klassifiziert (Odoo-Aufgabe #1012 erledigt).

⚠️ **Das Ingest-Skript hat den Pfad fest verdrahtet** (`SCAN_BASE` in `/usr/local/bin/frawo-scan-ingest.sh` auf `stock-pve`, **Wirtspfad**, nicht Containerpfad). Beim Umzug der Scan-Ablage am 04.09.2026 lief der Timer dadurch **eine knappe Stunde lang ins Leere — mit Exit-Status 0**, weil das Skript fehlende Personenordner mit `continue` überspringt. Kein Fehler im Log, kein Alarm. Nachgezogen auf `/mnt/music_hdd/_Dokumente/Scans` (Sicherung: `frawo-scan-ingest.sh.backup-20260904`). **Wer die Scan-Ablage verschiebt, muss dieses Skript mitziehen.**

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

| Playlist | ID | Titel (gemessen 04.09.2026) | Gewichtung |
|---|---|---|---|
| Channel 1 — Acoustik & Ambient | 846 | 1.225 | 3 |
| Channel 2 — Soft Groove | 847 | 3.498 | 3 |
| Channel 3 — Harder Styles | 848 | 2.622 | 3 |
| Channel 4 — Roadtrip & Classics | 849 | 1.514 | 3 |
| **Sunrise** (neu 04.09.2026) | 851 | 21 | 3 |

**Wie eine Playlist bestückt wird:** Ordner unter `/mnt/music/Curated_Playlists/<Name>/` mit **Symlinks** (keine Kopien) auf die echten Dateien, dazu eine Zeile in `station_playlist_folders`. Die Symlinks löst **Samba serverseitig** auf — der CIFS-Client in VM210 sieht ganz normale Dateien (`find -type l` dort liefert 0). Danach übernimmt `CheckFolderPlaylistsTask` (alle 5 Min) die Zuordnung automatisch.

Alle vier gleich gewichtet, kein Tageszeit- oder Wochentag-Bezug mehr,
keine separaten DJ-Show-Slots. **Wolf wusste davon nichts** (Stand
19.08.2026, nachgefragt). Verdacht: die parallele Sitzung von heute
arbeitet an einem "yourparty"-Projekt mit AzuraCast-Bezug (Skripte wie
`update_live_radio.py`/`_v2`/`_v3`, `enable_azuracast_streamers.py` im
selben Repo gefunden) und hat vermutlich schon länger am selben Sender
gearbeitet. **Noch nicht geklärt, nicht rückgängig gemacht** — Wolf
klärt das direkt mit der anderen Sitzung.

**Lautheit (Stand 29.07.2026, nicht neu gemessen):** Dateien schwanken um 11,7 dB, das **Sendesignal nur um 3,0 dB** bei −15,8 LUFS. Die Angleichung arbeitet.

### 🎛️ Kanal-Demokratie — live seit 06.09.2026 (Odoo #1300)

Energy-/Chill-Votes auf `frawo.tech/radio` verschieben die Gewichte der vier Kanäle **wirklich** — kollektiv über ein 15-Minuten-Fenster, nicht „wer zuerst klickt". Spec: `DOCS/superpowers/specs/2026-09-06-radio-demokratie-design.md`, Plan: `DOCS/superpowers/plans/2026-09-06-radio-kanal-demokratie-plan.md`.

| Was | Wo |
|---|---|
| Cron `FraWo Radio: Kanal-Gewichte aus Hörer-Votes` (ir.cron #51), alle 5 Min | Odoo CT140, ruft `frawo.radio.vote._cron_apply_vote_weights()` |
| **Notausschalter** | `ir.config_parameter` `frawo_agent.radio_democracy_enabled` — nur exakt `true` schaltet ein; fehlt/anders = aus (fail-closed) |
| Kanal-Zuordnung | `frawo_agent.radio_chill_playlist_ids` = `846,847` (Acoustik&Ambient, Soft Groove) · `frawo_agent.radio_energy_playlist_ids` = `848,849` (Harder Styles, Roadtrip&Classics) |
| Regel | Basis 3, Grenzen 1–6, **max. ±1 Schritt pro Lauf**, Mehrheit ab 2 Stimmen Abstand; ohne Votes wandert alles zurück auf 3 |
| Schreibweg | **AzuraCast-REST-API** (`PUT /api/station/1/playlist/{id}`), Model `frawo.radio.azuracast` — deshalb **kein** `azuracast:radio:restart` nötig |
| Nachweis | jeder Lauf mit Änderung als Eintrag in `frawo.agent.log` („Radio-Demokratie: …", inkl. Rückprobe) |
| Live-Show | `live.is_live` → Seite zeigt Applaus/Feuer/Liebe statt Steuer-Buttons; nichts wird gesteuert |

**Abnahme 06.09.2026, 14:16 UTC:** drei Chill-Testvotes → echter Cron-Lauf → Gewichte von 3/3/3/3 auf `{846: 4, 847: 4, 848: 2, 849: 2}`, Rückprobe ohne Abweichung, Log-Eintrag vorhanden. Testvotes danach entfernt.

**Sterne-Bewertung + Rekordbox-Export (Teil B der Spec)** ist designt, aber noch nicht gebaut — eigener Plan folgt.

⚠️ **Der in Odoo hinterlegte AzuraCast-Key (`frawo_agent.azuracast_api_key`) war bis 06.09.2026 tot** (403 `NotLoggedInException`) — damit war der Skip-Vote (`hate` → AzuraCast-Skip in `controllers/main.py`) unbemerkt außer Funktion. Ersetzt durch den funktionierenden Key aus `deployments/musikverwaltung/rekordbox_sync/.env` (nicht eingecheckt); alter Wert als Parameter `frawo_agent.azuracast_api_key.bak-20260906` in Odoo gesichert. Der Schlüssel aus `reference_frawo_azuracast` bleibt tot. Verwaltung über die Datenbank weiterhin möglich:
`ssh stock-pve` → `qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE …'`
Grössere Abfragen als Datei einspielen (`docker cp`), sonst schluckt der Rückweg die Ausgabe. Tabellen heissen `station_playlists` (Plural).

🟡 **Offen seit 04.09.2026 — ein Befehl, den nur Wolf ausführen kann.** Der versehentliche `azuracast:media:reprocess 1` hat **25.819** Titel auf `mtime = 0` stehen lassen (siehe Fallen-Tabelle). Solange das so ist, blockiert die Altlast weiterhin jeden **neuen** Ordner für ~20 Stunden. Sunrise ist bereits von Hand vorgezogen und läuft, der Rückstand baut sich sonst erst von selbst ab. Aufräumbefehl (danach ist der Scan sofort wieder normal schnell):

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"UPDATE station_media SET mtime = UNIX_TIMESTAMP()+5 WHERE mtime = 0 AND length > 0;\"'"
```

Gefahrlos: `length > 0` trifft nur Titel, deren Metadaten schon ausgelesen sind; die 18 wirklich unverarbeiteten bleiben in der Warteschlange.

---

## 🎵 Musikverwaltung (beets, CT120)

Läuft dort, weil die Platte **direkt eingehängt** ist (`/mnt/music`) — nicht über den CIFS-Umweg, an dem der AzuraCast-Scan früher hängenblieb.

### Samba-Freigaben auf CT120 (Stand 04.09.2026)

| Freigabe | Pfad (Container) | Zweck |
|---|---|---|
| `[music]` = `M:` | `/mnt/music` | **Nur Musik.** Blendet die Dokumentenablage per `veto files = /_Dokumente/` aus |
| `[documents]` | `/mnt/music/_Dokumente` | **Neu 04.09.2026** — Belege, Scans, Odoo-Sicherungen, private Ablage |
| `[scans]` | `/mnt/music/_Dokumente/Scans` | Drucker-Ablage Alopri (Pfad am 04.09. mitgezogen) |
| `[playlists]` | `/mnt/music/_playlisten` | Rekordbox ↔ Sender |
| ~~`[radio]` = `R:`~~ | `/mnt/stick/yourparty.radio` | **Abgeschaltet 04.09.2026** (lag auf der Systemplatte des Wirts, echtes Ausfallrisiko) — Freigabe entfernt, AzuraCast-Referenz vorher sauber ausgehängt |

⚠️ **`M:` ist die ganze Plattenwurzel.** Der Container bekommt `sdb2` als
`mp0: /mnt/music_hdd,mp=/mnt/music` — es gibt auf dieser Platte also **kein
„neben der Musikfreigabe"**. Deshalb liegt die Dokumentenablage physisch
*innerhalb* `/mnt/music` und wird für `M:` nur **ausgeblendet**. Das ist
Absicht, kein Versehen. Sauber trennen liesse sie sich nur mit einem
zweiten Mountpoint (`/mnt/data_family`) — der braucht einen **Neustart von
CT120** und muss warten, bis die beets-Kuratierung ruht.

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

⚠️ **Zwei getrennte Sicherungswege — nicht verwechseln (geklärt 23.08.2026):**

| Wessen Gäste | Wohin | Auftrag |
|---|---|---|
| **ProDesk**-Container | **PBS** auf dem Anker | `28c8fb76…`, 04:00, `storage pbs-frawo` |
| **Anker**-Gäste (101, 130, 150, 210, 300) | **Google Drive** | `daily-all-pbs`, 04:00, `storage google-drive`, `keep-last=3` — am 09.07.2026 bewusst von PBS umgestellt („entlastet PBS") |

🔴 **Falle:** Wer die Anker-Gäste in PBS sucht, findet **nichts** und hält sie fälschlich für ungesichert. Genau das ist am 23.08. passiert. Immer `pvesm list google-drive` gegenprüfen. Verifiziert: alle Anker-Gäste haben je 3 Generationen, frisch vom selben Tag (CT130 11,9 GB, CT150 3,2 GB, VM210, VM300, CT101).

🟡→✅ **Blinder Fleck im TÜV geschlossen (23.08.2026):** Der TÜV prüfte mit `pbs_container` nur die **8 ProDesk**-Container. Die **Anker**-Gäste hätten monatelang ausfallen können, ohne dass 11/11 kippt — inklusive CT130 (Radio-Backend) und CT150 (OpenClaw-Gateway). Neue Prüfung **`anker_gaeste_cloud`** holt per SSH `pvesm list google-drive` vom Anker und verlangt für **jeden** der Gäste 101/130/150/210/300 eine Sicherung von heute oder gestern mit mindestens 50 MB. **TÜV steht jetzt bei 12 Prüfungen.**

Die Alarmierung greift automatisch, weil die Regeln allgemein formuliert sind (`frawo_backup_tuev == 0`). **Gegenprobe gemacht:** mit einer erfundenen Gast-ID fällt die Prüfung korrekt durch und benennt den fehlenden Gast — eine Prüfung, die nicht durchfallen kann, wäre wertlos.

✅ **Vollprüfung 23.08.2026:** Backup-TÜV **11/11**, Cron feuert nachweislich (auch die 03:30- und 03:45-Jobs), PBS räumt sauber auf (Prune 7 Tage / 4 Wochen / 2 Monate, Garbage Collection täglich, letzter Lauf OK, PBS-Platte 55 %), Überwachung intakt (**39 Alarmregeln geladen, 0 fehlerhaft**). Die Thin-Pool-Alarme wurden **per Prometheus-Abfrage gegengeprüft**, nicht nur als Regeldatei gelesen — sie decken tatsächlich **beide** Knoten ab.

### 🟡 Speicherplatz: Thin-Pool-Lage (geprüft 23.08.2026)

| Knoten | Thin-Pool `data` | Volume Group frei | Bewertung |
|---|---|---|---|
| ProDesk | **51,2 %** | 4 MB | unkritisch |
| Anker | **79,0 %** (vorher 82,8 %) | **0** | 🟡 beobachten, Alarm ab 87 % |

**Der Anker ist 2,2-fach überbucht:** 341 GB virtuelle Platten auf einem 157-GB-Pool. Grösster Verbraucher ist **VM240 (PBS, ~39 GB)** — die Sicherungsmaschine liegt auf derselben Platte wie ihr eigenes Betriebssystem. Wächst PBS seine 70-GB-Platte aus, liefe der Pool Richtung 99 % — und ein volllaufender Thin-Pool **beschädigt die VMs**.

**Kein akuter Notfall** (79 %, Alarm bei 87 %), aber der Kurs stimmt nicht. **Echte Lösung braucht zusätzlichen Speicher/Hardware für den Anker** — nicht per Konfiguration lösbar.

⚠️ **Warum der Pool überhaupt schleichend wuchs:** Die LXC-Container laufen **ohne `discard`**, gelöschte Dateien blieben dauerhaft im Pool belegt (siehe Fallen-Tabelle). Seit 23.08.2026 räumt `/usr/local/bin/frawo-ct-fstrim.sh` das **wöchentlich (So 04:30) auf beiden Knoten** auf — protokolliert nach `/var/log/frawo-ct-fstrim.log` inkl. Poolstand, überspringt gestoppte Container. Crontab-Sicherungen: `/root/crontab.backup-20260823-vor-ctfstrim`.
CT120 (Fileserver) meldet dabei „discard not supported" — dessen Platte liegt nicht im Thin-Pool, wird sauber übersprungen. Odoo-Aufgabe #1066.

*Ehrliche Zahl:* `fstrim` meldete beim erstmaligen Aufräumen 149 GB „getrimmt", der echte Poolgewinn betrug aber nur ~6 GB — der Rest war im Pool ohnehin nie belegt. Die gemeldete Trim-Menge ist **kein** Mass für gewonnenen Platz.

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
| ~~`R:` abschalten~~ — **erledigt 04.09.2026**, Restordner am 05.09.2026 entfernt. Verwaiste AzuraCast-`storage_location` (id 9, `network_library`, 253 Medien, von keiner Station/Playlist referenziert) entfernt, danach `[radio]`-Freigabe in `smb.conf` auf CT120 auskommentiert (Sicherung `smb.conf.backup-20260904-radio-retired`), `smbd` neu gestartet. `\\10.1.0.94\radio` antwortet nicht mehr. `/mnt/stick/yourparty.radio` auf der Wirt-Systemplatte war beim Nachschauen nur noch ein leeres Ordnergerüst (28 K, keine echten Dateien mehr) — entfernt, `/` bleibt bei 37 GB frei | — | #1263 |
| **Flos Server ("frawo-docker-1") ist endgültig weg** (Wolf bestätigt 05.08.2026). Nextcloud, lokale AzuraCast, n8n-Alt, ollama, qdrant liefen dort ebenfalls — Bedarf für Neuaufsetzen jeweils einzeln klären | Wolf | — |

---

## 🧭 Prinzipien

- **Odoo = Quelle der Wahrheit** für Menschen und Agenten.
- **Am Ergebnis messen, nicht am Vorgang.** Ob ein Skript lief, sagt nichts darüber, ob eine brauchbare Datei entstand.
- **In beide Richtungen prüfen.** Ein Alarm, der nie ausgelöst hat, ist kein Beweis.
- **Verschieben statt löschen.** Quarantäne-Ordner, Sicherungskopien, Rückwege.
- **Roadmap:** 1) WP-Stockenweiler-3 2) Website & Verleih professionell 3) selbstverwaltetes Odoo via Agent.

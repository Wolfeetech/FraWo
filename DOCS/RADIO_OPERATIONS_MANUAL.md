# 📻 FraWo Funk — Sende- & Betriebshandbuch (SOP & Best Practices)

Dieses Handbuch definiert die Standard Operating Procedures (SOPs), Wartungsroutinen und Best Practices für den reibungslosen, professionellen 24/7-Betrieb von **FraWo Funk — Das Non-Stop Radio vom Bodensee**.

---

## 🏗️ 1. ARCHITEKTUR & PLAYLIST-STRATEGIE (Die Sende-Engine)

Um eine dynamische, abwechslungsreiche und ermüdungsfreie Hörerfahrung zu gewährleisten, läuft die Sende-Engine (Liquidsoap) auf Basis eines gewichteten Rotationssystems mit automatischen Jingle-Einschüben.

### Die 4 aktiven Playlists
1. 🔥 **Heavy Rotation (Gewichtung: 5):**
   * Beinhaltet die aktuellen Top 50 Favoriten und Neuerscheinungen.
   * Wird am häufigsten in den Stream gemischt.
2. 🌊 **Medium Rotation (Gewichtung: 3):**
   * Beinhaltet ca. 200 etablierte Bodensee-Staple-Tracks.
3. 💎 **Classics & Deep Cuts (Gewichtung: 1):**
   * Beinhaltet den Backkatalog (500+ Tracks) für musikalische Tiefe und Überraschungen.
4. 🎙️ **Jingles & Station IDs (Modus: Jingle / Strenge Einschub-Regel):**
   * Beinhaltet Sende-Drops („FraWo Funk – Das Non-Stop Radio vom Bodensee“).
   * **Regel:** Exakt nach jedem **4. Song** wird vollautomatisch ein Jingle eingeflochten, bei dem die Metadaten des vorangegangenen Songs im Player erhalten bleiben.

---

## 📁 2. AUTOMATISCHER INGEST & MUSIKPFLEGE (Best Practice)

Die Musikbibliothek liegt auf der 1 TB großen SSD (`/mnt/music`), auf die simultan über **Samba (`\\10.4.0.233\music`)** und **Navidrome (`http://media.hs27.internal`)** zugegriffen wird.

### SOP: Musik einpflegen & Taggen
Damit das Radio-Dashboard und externe Player (Auto-Displays, Smart Speakers) korrekte Titelbilder und Songnamen anzeigen, ist folgender Workflow bindend:

1. **Dateiformat:** Ausschließlich saubere MP3-Dateien (min. 320 kbps) oder WAV.
2. **Ordner-Zuweisung:** Kopiere neue Tracks in den entsprechenden Unterordner der Samba-Freigabe (z. B. `\music\Rotations\Heavy` oder `\music\Rotations\Medium`).
3. **ID3-Tagging (Pflichtschritt vor dem Senden):**
   * Öffne den Ordner in **Mp3tag** oder **MusicBrainz Picard**.
   * Format: `Künstler - Titel`.
   * Cover-Art: Einbetten von quadratischen JPEG/PNG-Dateien (empfohlen: 800x800 px).
4. **Automatischer Ingest:** AzuraCast überwacht die Verzeichnisse im Hintergrund. Sobald die getaggte Datei im Ordner liegt, wird sie binnen 60 Sekunden vollautomatisch in die Sende-Rotation aufgenommen.

---

## 🎛️ 3. AUDIO-MASTERING & CUE-MANAGEMENT

Jeder Song durchläuft vor der Ausstrahlung in Echtzeit unsere interne Mastering-Kette. Manuelle Eingriffe in die Lautstärke einzelner Dateien sind nicht erforderlich.

* ⚡ **AutoCue (Stille-Erkennung):** Berechnet automatisch Cue-In und Cue-Out. Erkennt leise Intros/Outros und setzt den perfekten Crossfade-Punkt.
* 🎛️ **master_me (Multiband-Mastering):** Ein integrierter DSP-Mastering-Algorithmus (Leveler, EQ, Limiter), der das Sende-Signal kontinuierlich auf pralle, sendefähige **-14 LUFS** normalisiert.

---

## 🚨 4. MONITORING, LOGS & FEHLERBEHEBUNG (Troubleshooting)

Falls es zu Sendeausfällen oder Stottern kommt, folge diesem Diagnose-Protokoll:

### 1. Status der Container prüfen (CT 130)
Logge dich per SSH auf Proxmox Anker ein und prüfe die AzuraCast Docker-Dienste:
```bash
pct exec 130 -- docker ps
pct exec 130 -- docker compose logs --tail 50 web
```

### 2. Liquidsoap / Icecast Restart
Sollte sich ein Stream aufhängen, starte die Sende-Engine über die Konsole neu:
```bash
pct exec 130 -- docker exec azuracast /var/azuracast/www/backend/bin/console azuracast:radio:restart
```

### 3. Caddy Proxy prüfen (CT 100)
Falls `https://funk.frawo-tech.de` oder `http://media.hs27.internal` nicht erreichbar sind, prüfe den Proxy-Container auf CT 100:
```bash
pct exec 100 -- docker compose -f /opt/homeserver2027/stacks/toolbox-network/docker-compose.yml logs --tail 50 caddy
```

---

## 💾 5. BACKUP & RESTORATION SOP

### Automatisierte Backups
* **Pfad:** `/var/azuracast/backups` auf CT 130.
* **Turnus:** Täglich um 04:00 Uhr (Aufbewahrung: 7 Tage).
* **Inhalt:** MariaDB Sendedatenbank, Playlists, Statistiken und Settings (Media-Dateien sind ausgeschlossen und werden über Proxmox / PBS auf Host-Ebene gesichert).

### SOP: Manuelles Backup wiederherstellen
Falls das System migriert oder neu aufgesetzt werden muss:
```bash
pct exec 130 -- docker exec azuracast /var/azuracast/www/backend/bin/console azuracast:restore /var/azuracast/backups/backup.zip
```

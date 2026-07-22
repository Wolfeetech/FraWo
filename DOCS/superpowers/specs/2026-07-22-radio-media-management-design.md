# FraWo Funk — Medienverwaltung nach Radio-Best-Practice (Phase 1: Energie-Fundament)

**Datum:** 2026-07-22
**Status:** Design freigegeben (Wolf), bereit für Umsetzungsplan
**Odoo-Bezug:** #762 (989/945 Tracks ohne Genre), #760/#761 (Dayparts nicht unterscheidbar), #701 (Playlist-Struktur), #764 (API-Key erneuern), #531 (Sendeschema 24/7)

> **Sicherheitshinweis:** Dieses Repo ist öffentlich. KEINE Zugangsdaten (API-Keys, Passwörter, DB-Creds) in dieses Dokument oder Code committen. Zugänge liegen in Vaultwarden bzw. werden zur Laufzeit aus Container-Env/CLI geholt.

## 1. Ziel

FraWo Funk soll als **Hybrid-Sender** laufen: eine vollautomatische Tages-Rotation, die über den Tag hörbar „atmet" (morgens ruhig/warm → mittags groovig → nachmittags treibend → abends Höhepunkt → nachts tief), plus später feste Show-Fenster (Phase 2). Phase 1 baut das **Fundament**: eine Bibliothek, deren Tracks nach objektiver **Energie** sortiert sind, sodass die vorhandenen Tageszeiten-Playlists musikalisch klar unterscheidbar werden — ohne Abhängigkeit von unzuverlässigen Genre-Tags.

## 2. Ist-Zustand (live verifiziert 2026-07-22)

- Station **FraWo Funk** (Station-ID 1) läuft live, 320 kbps, `funk.frawo.tech`, VM210 auf ProDesk (10.1.0.38).
- **2.457 Tracks** indexiert, **81,6 GB**, Storage-Location id 9 = `/var/azuracast/stations/frawo_funk/media/network_library` (= Fileserver-Freigabe `//10.1.0.94/radio`, heute repariert).
- **945 Tracks (38%) ohne Genre**, **1.251 (51%) ohne Album** → Metadaten-Lücke ist die Wurzel der ununterscheidbaren Dayparts.
- **Daypart-Playlists existieren bereits** (nur schlecht befüllt, vermutlich nach Ordner-Prefix): Sunrise (66), Morning Drive (319), Lunch (318), Afternoon (161), Evening (317), Night (244), Deep/Night (837, 55). Dazu: General Rotation (835, Sicherheitsnetz), Rotation (Tag) (836, aus), Shows (Fr/Sa) (838, leer), Wolf_Special_1 (839, leer).
- **API-Key tot** — nur öffentliche Endpunkte (nowplaying) funktionieren. Automatik ist damit blockiert.
- CF-WAF blockt Datei-/Playlist-API über `funk.frawo.tech` → API-Verwaltung **direkt gegen `https://10.1.0.38`** (an Cloudflare vorbei).

## 3. Ansatz (Weg 1: Energie-Fundament)

Statt die 945 fehlenden Genre-Tags mühsam (und unzuverlässig) nachzuschlagen, wird **jeder Track objektiv per Audio-Analyse** bewertet (Tempo + Energie + Klanghelligkeit). Das funktioniert bei getaggten und untaggten Tracks gleichermaßen. Aus dem Energie-Wert folgt die Zuordnung zu den bestehenden Tageszeiten-Playlists. Die Struktur bleibt, nur die Befüllung wird sauber neu gemacht.

## 4. Komponenten & Ablauf

### 4.0 API-Zugang wiederherstellen (Enabler)
Neuen API-Key für die Station erzeugen — via AzuraCast-CLI direkt auf der VM (`qm guest exec 210 -- docker exec azuracast azuracast_cli …` bzw. Web-Admin). Key wird in **Vaultwarden** abgelegt und für die Skripte aus einer lokalen, nicht eingecheckten `.env` gelesen. Alter Key wird revoked. (Odoo #764)

### 4.1 Energie-Analyse (einmaliger Batch)
- **Werkzeug:** Python + `librosa` (+ `ffmpeg`/`audioread` fürs Dekodieren).
- **Pro Track berechnet:** Tempo (BPM), mittlere RMS-Energie (Intensität/Lautheit), Spektral-Centroid (Klanghelligkeit).
- **Energie-Score:** je Merkmal Perzentil-Rang über die gesamte Bibliothek bilden (robust gegen Ausreißer), gewichtet kombinieren (BPM 0,4 · RMS 0,4 · Helligkeit 0,2) → Gesamt-Perzentil → **Tier 1–5** (1=ruhig … 5=treibend).
- **Wo:** auf **StudioPC** (28 Kerne, Analyse parallelisiert via `multiprocessing`), Zugriff auf die Musik über SMB-Mount von `//10.1.0.94/radio`. Bewusst **nicht** auf den Produktions-Servern → keine Last dort. Einmaliger Lauf, geschätzt Minuten bis <1 h.
- **Ausgabe:** eine CSV/JSON-Datei `energy_map.csv` mit `relativer_pfad, bpm, rms, centroid, energy_score, tier`. Kleine Datei, treibt Schritt 4.3.
- **Idempotent/wiederholbar:** Skript kann erneut laufen (z. B. nach Musik-Zuwachs), überschreibt die Map.

### 4.2 Energie → Daypart-Zuordnung (die „Uhr")
Tages-Uhr mit Zuordnung Energie-Tier → Playlist (ein Track darf in 1–2 benachbarten Dayparts liegen, damit Playlists genug Tiefe haben):

| Daypart (Playlist) | Zeitfenster | Energie-Tier |
|---|---|---|
| Deep / Night (837) | 01–05 | 1 (tief/ambient) |
| Sunrise (840) | 05–08 | 1–2 (ruhig/warm) |
| Morning Drive (841) | 08–11 | 2–3 |
| Lunch (842) | 11–14 | 3 (groove) |
| Afternoon (843) | 14–17 | 3–4 |
| Evening (844) | 17–22 | 4–5 (Höhepunkt) |
| Night (845) | 22–01 | 3–4 (Ausklang) |

Zeitfenster sind Startwerte und werden nach dem ersten Hörtest feinjustiert.

### 4.3 Neu-Einsortierung (Schreiben)
- **Vorher sichern (reversibel):** aktuelle Playlist-Zuordnungen exportieren (DB-Dump der Tabelle `station_playlist_media` + Playlist-Metadaten). AzuraCast-DB-Backup ziehen.
- Bestehende Daypart-Playlists leeren und gemäß `energy_map.csv` + Uhr (4.2) neu befüllen.
- **Schreibweg:** AzuraCast-API `PUT /api/station/1/files/batch` (Aktion „playlist") **direkt gegen `https://10.1.0.38`** (CF-WAF-Umgehung), Batch-weise. Zuordnung Track↔Datei über den Medien-Pfad/`id`.
- „General Rotation" (835) bleibt als **Sicherheitsnetz** mit niedrigem Gewicht + `fallback.mp3` armiert (gegen Dead-Air).

### 4.4 Rotation nach Radio-Standard
- **Wiederholungsschutz** in den Stationseinstellungen aktivieren — Startwert: derselbe Titel nicht innerhalb von ~40 Songs, derselbe Künstler nicht innerhalb von ~15 Songs (nach Hörtest justierbar).
- **Terminierung:** die 7 Dayparts nach der Uhr (4.2) schedulen; außerhalb greift General Rotation.
- Playback-Order der Dayparts = `shuffle` (bereits gesetzt), Gewichte so, dass Übergänge weich sind.

## 5. Datenfluss

```
Musik-Dateien (Fileserver //10.1.0.94/radio)
        │  (SMB, read-only)
        ▼
StudioPC: librosa-Analyse (parallel)  ──►  energy_map.csv (Pfad → Tier)
                                                   │
                                                   ▼
                            Zuordnungs-Skript (Uhr 4.2)  ──►  AzuraCast-API (10.1.0.38)
                                                                   │  PUT files/batch (playlist)
                                                                   ▼
                              Daypart-Playlists sauber befüllt  ──►  Liquidsoap sendet nach Zeitplan
```

## 6. Fehlerbehandlung & Sicherheit

- **Kein Dead-Air:** `fallback.mp3` armiert; General Rotation als Netz bleibt aktiv, bis die neuen Dayparts verifiziert sind.
- **Reversibel:** vor jeder Schreibaktion Export der Ist-Zuordnungen + DB-Backup; Rollback-Skript möglich.
- **Live-sicher:** Playlist-Umbau in AzuraCast unterbricht den laufenden Stream nicht; trotzdem bevorzugt zu hörerarmer Zeit ausführen.
- **Keine Secrets im Repo:** Keys/Creds nur aus lokaler `.env`/Vaultwarden/Container-Env.
- **Analyse belastet Produktion nicht** (läuft auf StudioPC, nur lesender SMB-Zugriff).

## 7. Verifikation (Definition of Done Phase 1)

1. Jede Daypart-Playlist hat eine plausible Track-Zahl (kein leerer Slot) und einen **durchschnittlichen Energie-Tier**, der der Uhr entspricht (monoton steigend zum Abend, tief in der Nacht) — per DB-Query nachgewiesen.
2. Stichproben-Hörtest je Daypart bestätigt den Charakter (ruhig morgens, treibend abends).
3. Zeitplan greift: zur jeweiligen Uhrzeit ist die richtige Playlist aktiv (`nowplaying`/Liquidsoap-Log).
4. Wiederholungsschutz aktiv; kein sofortiger Künstler-/Titel-Doppler.
5. Station durchgehend online (kein Dead-Air während des Umbaus).

## 8. Ausdrücklich NICHT in Phase 1 (Scope-Grenzen / YAGNI)

- **Genre-Tags nachpflegen** (die 945) — für energie-basiertes Dayparting nicht nötig. Optional später (Phase 3), evtl. Energie-Tier zusätzlich als Custom-Field/Genre hinterlegen.
- **Show-Fenster / Live-DJ** (Fr/Sa) → **Phase 2**.
- **Automatische Einschleusung neuer Musik** (beets/rclone-Pipeline, Auto-Tagging neuer Tracks) → **Phase 3**.
- **Voting-/Rating-gesteuerte Playlists** (#467/#334/#428) → spätere Phase.
- **Storage-Architektur-Umbau** (Navidrome-Konsolidierung #529) → separat.

## 9. Roadmap (Einordnung)

- **Phase 1 (dieses Dokument):** Energie-Fundament + saubere Daypart-Rotation.
- **Phase 2:** Show-Fenster (feste Slots Fr/Sa, Live-DJ-Broadcast, Override der Auto-Rotation).
- **Phase 3:** Ingestion-Automatik — neue Musik → Analyse → Auto-Einsortierung; optional Genre-/Mood-Backfill.

# Musikserver CT120: Sanierung — Design

**Status:** Entwurf zur Freigabe durch Wolf. **Es wurde nichts verändert.**
Alle Zahlen unten sind am 05.09.2026 auf CT120 **lesend** gemessen.

Gehört zu Odoo-Epic **#1263** („Musikserver (CT120) aufräumen") und
#1268 (gestoppte Ingestion-Pipeline). Ergänzt
`DOCS/MUSIKSERVER_CT120_LANDKARTE.md` (Bestandsaufnahme) um das, was
dort noch fehlte: **die Ursache und den Weg heraus.**

---

## 1. Der eine Satz

Die Musikverwaltung (beets) und die Musikablage (`Master_Library`) sind
seit Wochen **zwei getrennte Welten**: 68 % der Datenbankeinträge zeigen
auf Dateien, die es an der Stelle nicht mehr gibt, und 68 % der echten
Musikdateien kennt die Datenbank nicht. Ursache ist ein selbstgebautes
Einsortier-Programm, das Dateien **an beets vorbei** verschoben hat.

Die gute Nachricht: **die Musik ist da.** 95 % der „verlorenen"
Datenbankeinträge lassen sich der richtigen Datei wieder zuordnen.

---

## 2. Was heute gemessen wurde

### 2.1 Das Ausmaß — nicht mehr geschätzt, gezählt

| Messung | Ergebnis |
|---|---|
| beets-Einträge gesamt | **11.766** |
| davon Pfad zeigt ins Leere | **8.012 (68 %)** |
| davon Pfad ist gültig | 3.754 (32 %) |
| Audiodateien in `Master_Library` | **9.796** |
| davon beets bekannt (exakter Pfad) | 3.165 |
| davon beets **unbekannt** | **6.631 (68 %)** |

Der Stichprobenbefund vom 04.09. („79 von 135 Einträgen bei 16
Künstlern tot") war also kein Ausreißer, sondern **repräsentativ für
die ganze Bibliothek**.

Wohin die toten Pfade zeigen:

| Alter Wurzelordner (existiert nicht mehr) | tote Einträge |
|---|---|
| `/mnt/music/yourparty_Libary/…` | 3.467 |
| `/mnt/music/Ranger_07.26/…` | 2.169 |
| `/mnt/music/radio_library/…` | 1.669 |
| `/mnt/music/Library/…` | 578 |
| `/mnt/music/_AUS_CLOUD_GERETTET_20260728/…` | 116 |
| Rest (`Eurythmics`, `VA`, `Pixel`, `Various Artists`, …) | 13 |

⚠️ **Die naheliegende Reparatur greift nicht.** Die Vermutung aus der
Landkarte war: „nur das Präfix hat sich geändert, die Ordner liegen
jetzt unter `_STAGING_RAW/`". Gegengeprüft: von 8.012 toten Pfaden
lassen sich so **nur 176** auflösen. Der Rest ist echt umgezogen und
umbenannt worden.

### 2.2 Sind die Dateien weg? Nein.

Abgleich der 8.012 toten Einträge gegen alle Dateinamen in
`Master_Library` (normalisiert: Kleinschreibung, Klammerzusätze und
Sonderzeichen entfernt):

| | |
|---|---|
| über den Dateinamen wiederfindbar | **3.701** |
| zusätzlich über Interpret + Titel | **3.906** |
| **kein Treffer** (wirklich fehlend oder ganz anders benannt) | **405 (5 %)** |

**7.607 von 8.012 toten Einträgen haben eine passende Datei in
`Master_Library`.** Das ist keine Datenrettung, das ist ein Umzug, bei
dem niemand die Adressen nachgetragen hat.

⚠️ Die Zuordnung ist nicht überall eindeutig: die 9.771 in diesem Lauf
erfassten Dateien (25 Randformate wie `.opus`/`.wma` waren nicht dabei)
verteilen sich auf nur **8.365 verschiedene Namensschlüssel** — rund
**1.400 Dateien teilen sich also einen Namen mit einer anderen**. Diese
Fälle müssen aufgelöst werden, bevor geschrieben wird (Abschnitt 5.5).

### 2.3 🔴 Die Zeitbombe: was `beet update` jetzt anrichten würde

An **11.764 von 11.766** Einträgen hängen die Kuratierungs-Merkmale
`vibe` und `research_source` aus der laufenden Radio-Recherche. Davon
hängen **8.012 an toten Pfaden.**

`beet update` entfernt Einträge, deren Datei fehlt. Ein einziger Aufruf
würde also **8.012 Titel samt der recherchierten `vibe`-Zuordnung und
Quellenangabe löschen** — die eigentliche Wertschöpfung der letzten
Wochen. Die Warnung stand schon in `NOW.md`; jetzt ist sie beziffert.

➡️ **Bis Phase 3 abgeschlossen ist, darf `beet update` nur mit
`--pretend` laufen.** Ohne Ausnahme.

Weiteres Vermögen in der DB, das ein Neuaufbau vernichten würde:
`style` bei 7.536 Titeln, `acoustid_id` bei 4.346, `mb_trackid` bei
5.253, `bpm` bei 9.719.

### 2.4 Die Ursache: `frawo_ingest.py` fasst beets nicht an

Im gesamten Skript `/usr/local/bin/frawo_ingest.py` steht **kein
einziger `beet`-Aufruf.** Es verschiebt mit `shutil.move` nach
`Master_Library/<Genre>/<Artist>/<Album>/` und schreibt Tags mit
`mutagen`. Die Datenbank erfährt davon nichts.

Damit erklärt sich alles auf einmal:

- **jede** von diesem Skript verschobene Datei wurde zu einer der
  6.631 beets unbekannten Dateien,
- **jeder** zugehörige alte Eintrag wurde zu einem toten Pfad,
- und die Ordnernamen (Abschnitt 2.5) stammen aus derselben Quelle: das
  Skript legt `Master_Library/<MusicBrainz-Tag>/…` an, ungefiltert.

Die 448 GB Quarantäne-Müll (Odoo #1268) waren also nur das **sichtbare**
Symptom. Der stille Schaden war größer.

Konkrete Fehler im Skript, unabhängig davon:

| Stelle | Fehler |
|---|---|
| `safe_move()` | gibt `True` zurück, wenn die Quelle **nicht existiert** — die Statistik meldet Erfolg, wo nichts passiert ist |
| `make_unique_path()` vor dem Move | erzeugt bei jedem Fehlversuch einen neuen hochgezählten Zielnamen (`_new_2374`) statt abzubrechen |
| `get_candidates()` | liefert immer die **ersten 8** Dateien in Verzeichnisreihenfolge. Eine feststeckende Datei blockiert die Warteschlange dauerhaft — 2.576 Läufe an denselben 8 Dateien |
| kein Fehlerzähler | keine Datei wird je als „schon N-mal gescheitert" markiert |
| `infer_mood(bpm)` | leitet eine Stimmung aus einer geschätzten BPM-Zahl ab — genau die erfundenen Daten, die die Radio-Recherche ausgelöst haben |
| Genre = MusicBrainz-Tag, roh | erzeugt Ordner wie `Bpitch Control` (ein Label), `Belgium` (ein Land) |

Der Timer ist seit 04.09. `disabled`/`inactive` — nachgeprüft.

⚠️ **Ein zweiter, schlafender Verschieber existiert:**
`/usr/local/bin/audio_hygiene_engine.py`, aufgerufen von
`frawo-music-watcher.sh`. Gleiche Konstanten, gleiche Ziele
(`Master_Library`, `Quarantine/Duplicates`), ebenfalls ohne
beets-Anbindung. Aktuell startet ihn kein Timer — aber er liegt
scharf da.

### 2.5 🔴 Fehlkonfiguration, die alles Weitere sabotieren würde

```
directory: /mnt/music                       ← falsch
paths.default: $genre/$albumartist/$album%aunique{}/$track $title
```

beets hält **die ganze Plattenwurzel** für seine Bibliothek, nicht
`Master_Library`. Jedes `beet import -m` und jedes `beet move` würde
Dateien nach `/mnt/music/<Genre>/…` schreiben — **neben**
`Master_Library`, direkt in die Wurzel. Genau das ist schon passiert:
in der DB stehen Pfade wie `/mnt/music/Eurythmics/…`,
`/mnt/music/Various Artists/…`, `/mnt/music/VA/…`.

Richtig wäre `directory: /mnt/music/Master_Library`. **Das ist eine
Zeile, und ohne sie ist jede spätere Phase gefährlich.**

### 2.6 Die Ordnerstruktur

`Master_Library` hat **427 Genre-Ordner auf der ersten Ebene**.
Verteilung:

- die **12 größten** halten ~7.600 der 9.796 Dateien
  (`Electronic` 2.800, `House` 2.018, `Techno` 994, `Disco` 700,
  `Electronic;Funk  Soul;Pop` 250, `Trance` 204, `Indie & Wave` 194,
  `Hip Hop` 131, `Electro` 126, `Ambient` 103, `Tech House` 99,
  `Bass` 88)
- **392 Ordner haben weniger als 20 Dateien**, zusammen nur 1.121

Darunter drei Sorten Unrat:

1. **Schreibweisen-Dubletten** — 22 Ordnerpaare, die sich nur durch
   Trennzeichen oder Groß-/Kleinschreibung unterscheiden:
   `Electronic` / `electronic`, `Hip Hop` / `Hip-Hop`,
   `DJ Sets` / `DJ-Sets`, `Electro;Dance` / `Electro; Dance` /
   `Electro Dance`, `Drum And Bass` / `Drum and Bass`, …
2. **Sprach-Dubletten** — `Électronique` (bestätigt: enthält
   `LCD Soundsystem/American Dream (2017)`, dasselbe Album liegt auch
   unter `Electronic/`).
3. **Freitext-Ketten** — `Ambient;Deep House;Downtempo;Electronic;Trip Hop`,
   `Jazz Rap;Abstract Hip Hop;Conscious Hip Hop;Cloud Rap;…`, und ein
   Ordner, dessen Name eine **komplette Beatport-Genreliste** mit über
   200 Zeichen ist.

Zum Vergleich: in den Datei-Tags stehen nur **156** verschiedene
Genre-Angaben. Die Ordnerstruktur ist also **unordentlicher als die
Daten** — sie ist ein Nebenprodukt des Einsortier-Skripts, kein
Abbild der Bibliothek.

### 2.7 Physische Duplikate

| Prüfung | Ergebnis |
|---|---|
| Dateien mit **exakt gleicher Größe** (Vorstufe zu bitgleich) | 215 Dateien in 89 Gruppen, **5,7 GB** |
| 0-Byte-Dateien in `Master_Library` | 15 |
| `.ntfs-3g-*`-Geisterdateien in `Master_Library` | 8.231 (alle 0 Byte, hartverlinkt, kosten keinen Platz) |
| Einträge, die sich einen Pfad teilen (zwei DB-Zeilen, eine Datei) | **312** |

Bitgleiche Duplikate sind also ein **kleines** Problem. Das große sind
Duplikate wie das LCD-Soundsystem-Album: **dieselbe Musik, andere
Kodierung, anderer Name, anderer Ordner** — die findet keine
Größenprüfung, dafür braucht es einen Audio-Fingerabdruck.

### 2.8 Was sonst noch am Weg liegt

- **9.381 Verweise** (Symlinks) in `Curated_Playlists`, davon 9.379
  nach `Master_Library`, **alle absolut**, 4 bereits kaputt.
  ➡️ **Jede Ordnerumbenennung macht alle 9.381 ungültig**, wenn sie
  nicht im selben Zug neu gebaut werden.
- **NTFS-Metadatenschaden, größer als dokumentiert.** Nicht nur
  `radio_library/.albumart`, sondern auch
  `_STAGING_RAW/_archive/broken_job_jobse/*`,
  `_STAGING_RAW/Scans`,
  `_STAGING_RAW/radio_library/Music/Radio/kendal/2020_-_inferno` und
  eine FLAC-Datei in `Inbox/…/Ben Liebrand/Grand 12-Inches 17`. Die
  Platte selbst ist laut SMART gesund — das braucht ein `chkdsk` unter
  Windows.
- **`Inbox`: 17 GB Rückstand** (~724 Dateien), unbearbeitet seit dem
  Stopp der Pipeline.
- **Kein `node_exporter` in CT120.** Auf dem Wirt `stock-pve` läuft
  einer mit `textfile_collector` (den nutzt `music-backup-to-cloud.sh`
  schon für Metriken) — **im Container gibt es keinen**. Deshalb konnte
  das Quarantäne-Wachstum von 448 GB unbemerkt bleiben.
- **Platz ist kein Problem mehr:** 479 GB von 1,9 TB belegt (26 %).
  Es gibt keinen Zeitdruck.

---

## 3. Werkzeug-Inventar — erst prüfen, dann bauen

Wolfs Regel („erst prüfen, ob ein vorhandenes Werkzeug es schon kann")
zuerst angewandt. Ergebnis: **fast alles ist schon da.**

### 3.1 beets kann mehr, als benutzt wird

Installiert: beets 1.6.0 mit `chroma`, `duplicates`, `edit`, `embedart`,
`fetchart`, `fromfilename`, `info`, `lastgenre`, `mbsync`, `missing`,
`replaygain`, `scrub`, `web`.

| Aufgabe im Eigenbau-Skript | beets-Bordmittel, das dasselbe kann |
|---|---|
| AcoustID-Fingerabdruck + Abfrage | `chroma`-Plugin (`beet fingerprint`) — **mit beets' eigenem API-Schlüssel**, nicht dem öffentlichen Testschlüssel `8XaANoOo` aus dem Skript |
| MusicBrainz-Abgleich | im Importer eingebaut, inkl. Ratenbegrenzung |
| „kein Treffer → aus Dateiname übernehmen" (die v5-Rettung) | `fromfilename`-Plugin **plus** `import.quiet_fallback: asis` — **beides ist bereits konfiguriert** |
| Genre setzen | `lastgenre` mit der vorhandenen Whitelist `/etc/beets/genres-frawo.txt` |
| Zielpfad `<Genre>/<Artist>/<Album>` | `paths`-Vorlage |
| Duplikat erkennen und behandeln | `duplicates`-Plugin (`-k`, `-C PROG`, `-F`, `-M`, `-m DEST`, `-t TAG`) |
| Werbemüll aus Tags putzen | `scrub`-Plugin |
| Lautstärkeangleich | `replaygain`-Plugin |
| **Datenbank aktuell halten** | **kann das Skript gar nicht** |

Wichtige Sicherheitsschalter, die es schon gibt und die genutzt werden
müssen: `beet import --pretend`, `beet update --pretend`,
`beet move --pretend`, `beet import -l <Logdatei>` (protokolliert
unzuordenbares Material zur späteren Sichtung), `beet -l <andere.db>`
(gegen eine Zweitdatenbank arbeiten, ohne die echte anzufassen).

### 3.2 Eigene Werkzeuge, die schon existieren und funktionieren

In `/usr/local/bin` auf CT120 liegt eine komplette, am 29.07.2026
gebaute und dokumentierte Werkzeugkiste, die genau diese Sanierung
schon einmal gemacht hat:

| Werkzeug | Was es kann | Bewertung |
|---|---|---|
| `genres-vereinheitlichen.py` | **Das zweistufige Modell ist fertig implementiert.** 16 kanonische Genres, Album-Mehrheitsentscheidung nach Spieldauer gewichtet, Probelauf ohne `--anwenden`, selbstabbildend (ein zweiter Lauf zerstört den ersten nicht — war schon ein Fehler, ist behoben) | ✅ **weiterverwenden** |
| `netzwerkordner-bauen.sh` | baut `_nach_Genre` / `_nach_Label` als **relative** Verweise, keine Kopien | ✅ weiterverwenden, um `_nach_Style` erweitern |
| `doubletten-quarantaene.sh` | Doubletten je Interpret+Titel, **höchste Bitrate gewinnt**, Probelauf ohne `--anwenden`, verschiebt nach `_QUARANTAENE_Doubletten_<Datum>` statt zu löschen. Kennt die 1-kbps-FLAC-Falle der defekten USB-Platte | ✅ weiterverwenden |
| `quarantaene-pruefen.sh` | Quarantäne-Sichtung | ✅ als Wächter einplanen |
| `playliste-exportieren.sh` | beets-Abfrage → Rekordbox/Mixxx-Playlist | ✅ unverändert |
| `tags-putzen.py` | Tag-Bereinigung | ✅ |
| `frawo_ingest.py` + `.v4-bak` | der Verursacher | 🔴 **stilllegen** |
| `audio_hygiene_engine.py` + `frawo-music-watcher.sh` | zweiter, schlafender Verschieber | 🔴 **stilllegen** |
| `professional_music_researcher.py.DEAKTIVIERT-erfindet-daten` | bereits deaktiviert | ✅ archivieren |

**Die 16 kanonischen Genres sind also keine neue Erfindung** — sie
stehen als `GENRE_RANG` in `genres-vereinheitlichen.py`, sind aus der
tatsächlich vorhandenen Musik abgeleitet und in `NOW.md` dokumentiert:

> `DJ-Sets`, `Techno`, `House`, `Trance`, `Bass`, `Disco`,
> `Funk & Soul`, `Indie & Wave`, `Hip Hop`, `Reggae`, `Jazz`, `Rock`,
> `Pop`, `Soundtrack`, `Ambient`, `Electronic`

Und die 15 größten Ordner in `Master_Library` tragen **schon jetzt
genau diese Namen**. Die Arbeit vom 29.07. war richtig — sie ist nur
danach vom Einsortier-Skript wieder zugeschüttet worden.

### 3.3 Wo ein eigenes Werkzeug unvermeidbar ist

Genau **eine** Lücke: beets hat keinen Befehl „hänge diesen
Datenbankeintrag auf eine andere Datei um". Dafür braucht es ein
einmaliges Umzugswerkzeug (Abschnitt 5).

Abgrenzung zu Wolfs Regel: das ist **kein Dauerdienst**, sondern ein
Werkzeug für genau einen Umzug, das danach ins Archiv geht — wie ein
Möbelwagen, nicht wie eine Garage. Und es schreibt **nicht per SQL in
die Datenbank**, sondern über beets' eigene Python-Schnittstelle
(`item.path = …; item.store()`), analog zur Odoo-Lehre „Schreibzugriffe
nur über das ORM, nie roh in die Datenbank".

---

## 4. Frage 2: Reparieren oder ersetzen? — Ersetzen.

### Option A — `frawo_ingest.py` reparieren und wieder anschalten

Machbar. Die sechs Fehler aus 2.4 sind alle behebbar: Rückgabewert von
`safe_move` ernst nehmen, Zielnamen erst nach erfolgreichem Move
vergeben, Fehlerzähler je Datei, BPM/Mood auf „unbekannt" statt raten,
Genre gegen die Whitelist filtern.

**Aber:** danach hat FraWo ein selbstgebautes Programm, das nachbaut,
was beets bereits kann — und es müsste **zusätzlich** noch lernen, die
Datenbank zu pflegen. Der Wartungsaufwand bleibt für immer bei FraWo.
Gemessen an dem Maßstab „reproduzierbar, dokumentiert, betreubar" aus
dem Ziel *System gewerblich anbieten* ist das die schlechteste Variante.

### Option B — Ingestion auf `beet import` umstellen ⭐ **Empfehlung**

beets ersetzt das Skript **ohne Funktionsverlust** (Tabelle in 3.1) und
kann als einziger das entscheidende Mehr: die Datenbank stimmt danach.

Auch nicht neu, sondern bewährt: Die **Radio-Bridge** (`10.1.0.128:8888`,
Wolfs Upload vom Handy) ruft laut `NOW.md` bereits `beet import` auf und
ist „über die echte API getestet und bestätigt funktionsfähig". Es gibt
also schon einen funktionierenden Ingestion-Weg — nur läuft daneben ein
zweiter, kaputter.

Was gebaut werden muss (klein):

1. `directory: /mnt/music/Master_Library` in `/etc/beets/config.yaml`.
2. `import.move: yes` (bisher `copy: no` / `move: no` — deshalb blieb
   alles in `Inbox` liegen). `write: yes` und `incremental: yes` bleiben.
3. `import.resume: ask` → **`resume: no`**. „Fragen" ist im
   unbeaufsichtigten Betrieb ein Hänger.
4. Ein `ExecStart`, das statt des Python-Skripts ruft:
   ```
   /usr/bin/beet import -q -l /var/log/beets-import-untagged.log /mnt/music/Inbox
   ```
   `-q` fragt nie und überspringt Zweifelsfälle, statt zu raten.
   `-l` schreibt sie in eine Liste zur menschlichen Sichtung.
5. **Takt stündlich statt alle 5 Minuten.** Die Inbox füllt sich in
   Wochen, nicht in Minuten.
6. **Sicherheitsnetz mit systemd-Bordmitteln statt Eigenbau-Logik:**
   ```ini
   [Unit]
   StartLimitIntervalSec=6h
   StartLimitBurst=3
   OnFailure=frawo-alarm@%n.service
   [Service]
   RuntimeMaxSec=45min
   ```
   Nach drei Fehlläufen in sechs Stunden **bleibt der Dienst stehen und
   meldet sich**, statt 2.576-mal dasselbe zu versuchen. Genau der
   Fehler, der 448 GB erzeugt hat, ist damit strukturell ausgeschlossen.
7. **Metrik in die vorhandene Monitoring-Konvention** (siehe 9.).

### Option C — Rein manuell

Wolf lädt hoch, ein Mensch importiert bewusst. Für 724 wartende Dateien
zu langsam, aber die richtige Ergänzung für die Zweifelsfälle aus
`-l`-Log — dort landet Underground-Material, das kein Katalog kennt.

### Empfehlung

**B, mit C als Rückfallebene.** `frawo_ingest.py`,
`audio_hygiene_engine.py` und `frawo-music-watcher.sh` werden nach
`/root/musik-werkzeuge-stillgelegt-20260905/` verschoben — **archiviert,
nicht gelöscht**, damit die Entscheidung umkehrbar bleibt.

⚠️ **Der Timer wird erst in Phase 6 scharf geschaltet**, nach der
Pfadreparatur. Sonst wächst der Berg unbekannter Dateien weiter,
während man ihn abträgt.

### Nachtrag zu den API-Fehlern aus #1268

Heute gegengemessen: **MusicBrainz antwortet mit HTTP 200**, ist also
erreichbar. Die dokumentierten 503er waren vermutlich Ratenbegrenzung
oder eine vorübergehende Störung — beets' Importer behandelt beides von
sich aus richtig. Die AcoustID-400er sind **nicht** nachgestellt
(dafür bräuchte es einen echten Fingerabdruck einer echten Datei); 400
ist ein Anfrage-Fehler, kein Ausfall, und weist eher auf einen Fehler im
Eigenbau-Aufruf oder auf den öffentlichen Testschlüssel hin. Das braucht
**keine** Klärung mehr, wenn Option B kommt: beets bringt seinen eigenen
registrierten Schlüssel mit.

---

## 5. Frage 3: Die 8.012 toten Pfade reparieren

### Option A — Datenbank wegwerfen und neu importieren

Schnell und einfach: `Master_Library` einmal komplett neu importieren.

❌ **Abgelehnt.** Kostet `vibe` + `research_source` bei 11.764 Titeln,
`style` bei 7.536, `acoustid_id` bei 4.346, `mb_trackid` bei 5.253,
`bpm` bei 9.719. Also mehrere Wochen Recherchearbeit für eine
Zeitersparnis von Stunden.

### Option B — Einträge auf die richtige Datei umhängen ⭐ **Empfehlung**

Der Eintrag bleibt, nur seine Adresse wird korrigiert. Alles daran
Hängende — Merkmale, Album-Zugehörigkeit, ID — überlebt.

**Ablauf, in dieser Reihenfolge:**

**5.1 Sichern (nicht verhandelbar)**
```bash
# 1) Datenbank
ssh stock-pve "pct exec 120 -- cp -a /var/lib/beets/musik.db \
    /var/lib/beets/musik.db.vor-sanierung-20260905"
# 2) Container-Sicherung anstoßen (die Musikplatte ist Bind-Mount und
#    NICHT in der PBS-Sicherung — die Datenbank aber schon, sie liegt
#    im Container-Dateisystem)
# 3) Referenzzahlen festhalten
ssh stock-pve "pct exec 120 -- beet stats"
```
Die Musikdateien selbst sind über `music-backup-to-cloud.sh` stündlich
nach Google Drive gesichert (`copy`, löscht nie am Ziel).

**5.2 Fingerabdrücke erzeugen — die Grundlage für inhaltliches Matching**

Aktuell haben nur 658 Titel einen `acoustid_fingerprint`, aber schon
4.346 eine `acoustid_id`. Beides ausbauen:
```bash
beet fingerprint          # chroma, füllt acoustid_fingerprint/acoustid_id
```
Läuft nur über Titel, deren Datei erreichbar ist — deckt also die 3.754
gesunden ab. Für die 6.631 beets **unbekannten** Dateien braucht es
denselben Schritt auf der anderen Seite (5.3).

⚠️ **Lastregel:** `beet fingerprint` liest jede Datei komplett. Auf
dieser NTFS-Platte (`fuseblk`, 5400 rpm) **strikt seriell** laufen
lassen, nie parallel — die Platte meldet unter paralleler Last falsche
Ein-/Ausgabefehler. Nachts fahren, Laufzeit mehrere Stunden. Kein
Problem, es blockiert nichts.

**5.3 Die 6.631 unbekannten Dateien erfassen — ohne die echte Datenbank zu berühren**
```bash
beet -l /var/lib/beets/inventur.db import -C -A --set=herkunft=inventur \
     /mnt/music/Master_Library
beet -l /var/lib/beets/inventur.db fingerprint
```
`-C` kopiert nichts, `-A` fragt keinen Katalog, `-l` benutzt eine
**Wegwerf-Zweitdatenbank**. Ergebnis: für jede echte Datei liegen Tags,
Länge und Fingerabdruck vor. Die Produktionsdatenbank bleibt unangetastet
— wenn hier etwas schiefgeht, wird nur eine Datei gelöscht.

**5.4 Zuordnen — Vorschlagsliste, noch nichts schreiben**

Prioritätskette, absteigend nach Verlässlichkeit:

| Stufe | Kriterium | Verlässlichkeit |
|---|---|---|
| 1 | gleiche `acoustid_id` | inhaltlich bewiesen |
| 2 | gleiche `mb_trackid` | Katalog-bewiesen |
| 3 | normalisiert `artist` + `title` **und** Länge ± 2 s | sehr hoch |
| 4 | normalisiert `artist` + `title` (ohne Länge) | hoch |
| 5 | normalisierter Dateiname | mittel |
| — | mehrere Kandidaten auf derselben Stufe | **Vorlage an Wolf, nichts automatisch** |

Ergebnis: drei Listen als CSV — `eindeutig.csv`, `mehrdeutig.csv`,
`ohne_treffer.csv`. **In diesem Schritt wird nichts verändert.**

Erwartung nach der Messung aus 2.2: rund 7.600 eindeutig, rund 400
ohne Treffer, dazwischen die mehrdeutigen aus dem 1.400er-Namensbereich.

**5.5 Zwei-auf-eins auflösen, bevor geschrieben wird**

Wenn mehrere Datenbankeinträge auf dieselbe Datei zeigen sollen
(es gibt heute schon 312 solcher Fälle), wird **nicht** einfach einer
gewählt. Regel — dieselbe, die auch für physische Duplikate gilt
(Abschnitt 6.3):

> **Überlebender** ist der Eintrag mit den meisten belegten Feldern
> (bei Gleichstand: der mit `mb_trackid`). Jedes Feld, das beim
> Überlebenden **leer** ist und bei einem anderen **belegt**, wird
> übernommen. Wo beide belegt sind und sich unterscheiden, gewinnt der
> mit der glaubwürdigeren `research_source` (echte Quellen-URL schlägt
> „Beets-Genre-Tag …"), und der Fall kommt auf eine Prüfliste.

**5.6 Schreiben — über beets, nicht über SQL**
```python
# Skizze; das Umzugswerkzeug arbeitet ausschließlich so:
import beets.library
lib = beets.library.Library('/var/lib/beets/musik.db')
item = lib.get_item(alte_id)
item.path = neuer_pfad.encode('utf-8')
item.store()
```
In Blöcken zu 500, nach jedem Block eine Zwischensicherung der
Datenbank. Abbruch bei der ersten Ausnahme.

**5.7 Nachziehen und prüfen**
```bash
beet update --pretend          # MUSS jetzt 0 fehlende Dateien melden
beet update                    # erst danach, aktualisiert Größe/Bitrate/mtime
beet stats
```
Danach die verbliebenen echten Neuzugänge normal importieren, und die
Verweise neu bauen:
```bash
netzwerkordner-bauen.sh
find /mnt/music/Curated_Playlists -xtype l | wc -l   # muss 0 sein
```

**Abnahmekriterien für Phase 3** (vorher festlegen, hinterher messen):

| | vorher | Ziel |
|---|---|---|
| tote Pfade | 8.012 | **0** (außer den geklärten Restfällen) |
| `vibe`-Merkmale | 11.764 | **≥ 11.764** |
| `research_source`-Merkmale | 11.764 | **≥ 11.764** |
| Dateien in `Master_Library` ohne DB-Eintrag | 6.631 | **0** |
| kaputte Playlist-Verweise | 4 | **0** |

### Option C — Zweitdatenbank wird zur neuen Hauptdatenbank

Statt umzuhängen die Inventur-Datenbank aus 5.3 zur produktiven machen
und die Merkmale hinübertragen. Sauberer Neustart, aber: Album-Gruppen,
IDs und die Zuordnungshistorie brechen, und die Merkmale müssen über
**dieselbe** Zuordnungskette wandern wie in Option B — also derselbe
Aufwand plus Zusatzrisiko.

❌ Nur als Notausgang, falls Option B an zu vielen Mehrdeutigkeiten
scheitert.

---

## 6. Frage 4 + 5: Ordner normalisieren und Duplikate zusammenführen

### 6.1 Die grobe Ebene: 16 (oder 17) Ordner statt 427

Wolfs Vorgabe — **grob nach fein**, wenige Ordner oben — deckt sich mit
dem, was schon existiert. Die 16 kanonischen Genres aus
`genres-vereinheitlichen.py` werden die erste Ebene. Sie tragen die
Radio-Shows aus
`DOCS/superpowers/specs/2026-09-03-radio-playlist-kuration-design.md`
vollständig:

Die Verteilung ist **nicht geschätzt**, sondern heute berechnet: die
Zuordnungsregeln aus `genres-vereinheitlichen.py` wurden auf alle 11.766
Genre-Angaben der Datenbank angewandt.

| Ordner (1. Ebene) | Titel¹ | Speist welche Shows |
|---|---|---|
| `House` | **3.807** | 1 Sunrise · 2 Morning Drive · 4 Afternoon · 5 Evening |
| `Techno` | **1.773** | 5 Evening · 6 Night · 7 Peak-Time-Night |
| `Disco` | **1.194** | 2 Morning Drive · 3 Lunch · 8 Sunday Roadtrip |
| `Electronic` | **1.027** | Auffangbecken + Basis-Rotation |
| `Pop` | 772 | 8 Sunday Roadtrip |
| `Indie & Wave` | 621 | 2 Morning Drive · 3 Lunch |
| `Bass` | 461 | 7 Peak-Time-Night (sonst ausgeschlossen) |
| `Trance` | 354 | 6 Night |
| `Rock` | 252 | 8 Sunday Roadtrip |
| `Ambient` | 209 | 1 Sunrise |
| `Funk & Soul` | 165 | 3 Lunch · 8 Sunday |
| `Hip Hop` | 129 | — |
| `Reggae` | 61 | 3 Lunch · 8 Sunday |
| `Jazz` | 9 | 3 Lunch |
| `Soundtrack` | 2 | — |
| `DJ-Sets` | 0² | 10 DJ-Bridge Sets |
| *(noch offen)* | **930** | siehe unten |

¹ Auf Titelebene gerechnet. Der endgültige Ordner wird **je Album**
nach Mehrheit entschieden (nach Spieldauer gewichtet) — kleine
Abweichungen sind zu erwarten, die Größenordnung stimmt.

² Kein Titel trägt „DJ-Set" im Genre-Tag; die 60 Dateien im heutigen
`DJ-Sets`-Ordner und die 386 als Set/Sendung erkannten Titel aus der
Radio-Recherche (`research_source`: „Länge ≥ 40 Minuten") sind über die
Länge identifiziert, nicht über das Genre. **Vorschlag:** diese Titel in
Phase 4 einmalig per `beet modify` auf `genre=DJ-Sets` setzen, dann
greift die Regel danach von selbst.

Die **930 noch offenen** sind 630 Titel ganz ohne Genre-Angabe plus 300
mit unbrauchbarem Wert (Werbung, Beatport-Kataloge). Für sie entscheidet
die Album-Mehrheit; was danach übrig bleibt, holt `beet lastgenre` gegen
die vorhandene Whitelist — und was auch dann leer bleibt, **bleibt
leer**, statt geraten zu werden.

**❓ Eine Entscheidung für Wolf: `Afro & World` als 17. Ordner?**

Show 9 („Afro House / World") hat 216 fertig getaggte Titel, die heute
in `House` verschwinden (Regel: `afro house` → `House`). Als eigener
Ordner wäre die Show direkt greifbar. Kosten: eine Zeile in
`genres-vereinheitlichen.py` **oberhalb** der House-Regeln — und
`House` verliert 216 Titel. Mein Vorschlag: **ja, aufnehmen**, weil das
Radio-Konzept ohnehin damit arbeitet. Wolf entscheidet.

### 6.2 Die feine Ebene: `style` als Feld, **keine** zweite Ordnerebene

**Empfehlung: die Feinheit lebt im Feld `style`, nicht im Ordnernamen.**

Begründung:

- `style` ist **pro Titel**, `genre` ist **pro Album**. Eine zweite
  Ordnerebene nach Style würde Alben wieder aufsplitten — genau das
  Problem, das Wolf am 29.07. gemeldet hat („ein album wird
  aufgesplittet, weil es verschiedene subgenres hat"). Der Ordnerbaum
  kann nur eine Zugehörigkeit abbilden; ein Feld kann mehrere.
- Für Ordnerpfade wäre eine dritte Ebene ein weiterer Umzug **aller**
  Dateien und damit ein zweites Mal 9.381 Verweise neu bauen.
- Die Feinsicht gibt es schon als **Verweisbaum**, kostenlos:
  `netzwerkordner-bauen.sh` baut heute `_nach_Genre\` und `_nach_Label\`.
  Ein `_nach_Style\` ist dieselbe Schleife mit einem anderen Feld —
  Windows sieht ganz normale Ordner, keine Datei liegt doppelt.
- Und die Playlist-Erzeugung fragt ohnehin Felder ab, nicht Ordner:
  `playliste-exportieren.sh warmup 'style:"Deep House" length:240..600'`.

Ergebnis im Explorer:

```
M:\Master_Library\House\Marlon Hoffstadt\Planet Love (2024)\…   ← grob
M:\_nach_Style\Deep House\…                                     ← fein (Verweise)
M:\_nach_Style\Melodic House & Techno\…
M:\_nach_Genre\House\…                                          ← wie bisher
M:\_nach_Label\Bpitch Control\…                                 ← Label, kein Genre mehr
```

Nebenwirkung, die einen echten Fehler behebt: `Bpitch Control` ist ein
**Label** und steht heute als Genre-Ordner in `Master_Library`. Im
neuen Modell landet es dort, wo es hingehört.

### 6.3 Der Weg dahin, ohne Datenverlust

**Schritt 1 — Rohwert retten, bevor er überschrieben wird.** Für viele
Titel steckt die feine Information heute **nur** im rohen
Genre-String (`Ambient;Deep House;Downtempo;Electronic;Trip Hop`). Vor
jeder Vereinheitlichung wird dieser Wert in ein neues Merkmal
`genre_raw` kopiert:
```bash
# je Titel, über beets, mit Probelauf
beet modify --pretend 'genre_raw=…'
```
Damit ist **jeder** Schritt danach umkehrbar, und die Feinheit ist die
Quelle für `style`.

**Schritt 2 — vereinheitlichen mit dem vorhandenen Werkzeug:**
```bash
genres-vereinheitlichen.py                      # nur anzeigen
genres-vereinheitlichen.py --anwenden           # in die Datenbank
genres-vereinheitlichen.py --anwenden --in-dateien   # auch in die Tags
```

**Schritt 3 — `style` füllen.** 7.536 Titel haben schon einen Style,
die bleiben unangetastet. Für den Rest: erster sinnvoller Teilbegriff
aus `genre_raw`, sonst `beet lastgenre` gegen die vorhandene Whitelist.
Nie raten — was nicht ableitbar ist, bleibt leer.

**Schritt 4 — Dateien physisch umziehen, mit beets:**
```bash
beet move --pretend      # zeigt jeden geplanten Umzug, ändert nichts
beet move                # beets verschiebt UND aktualisiert die Datenbank
```
Das ist der Kern: **kein eigenes Verschiebeprogramm**. beets kennt
Quelle, Ziel und Datenbank und hält alle drei zusammen — genau das, was
`frawo_ingest.py` nicht konnte.

🔴 **Voraussetzungen, sonst richtet dieser Befehl Schaden an:**
`directory` muss auf `Master_Library` zeigen (2.5), und **Phase 3 muss
fertig sein** — sonst zieht beets nur die 3.754 gesunden Titel um und
lässt die anderen 6.000 im alten Zustand liegen.

**Schritt 5 — Verweise neu aufbauen und prüfen:**
```bash
netzwerkordner-bauen.sh                              # _nach_Genre/_nach_Style/_nach_Label
# Curated_Playlists neu erzeugen (absolute Verweise!)
find /mnt/music/Curated_Playlists -xtype l | wc -l   # muss 0 sein
```
Danach AzuraCast-Neueinlesen anstoßen.

### 6.4 Physische Duplikate — drei Sorten, drei Antworten

| Sorte | Erkennung | Werkzeug | Vorgehen |
|---|---|---|---|
| **bitgleich** (215 Dateien / 89 Gruppen / 5,7 GB) | Größe, dann Prüfsumme | `beet duplicates -C 'sha256sum' -F` | zusammenführen, Verlierer nach `_QUARANTAENE_Doubletten_<Datum>` |
| **gleiche Aufnahme, andere Kodierung** (z. B. `Electronic/` vs. `Électronique/` LCD Soundsystem) | Audio-Fingerabdruck | `beet fingerprint`, dann `beet duplicates -k acoustid_id -F` | Bericht ansehen, **dann** zusammenführen |
| **ähnlich, aber nicht gleich** (Remix, Edit, Radio-Fassung) | dieselbe Kette schlägt an, ist aber nicht beweisend | `beet duplicates -k artist -k title -F` | 🔴 **niemals automatisch.** Liste für Wolfs Ohr |

⚠️ **`beet duplicates -M` (`--merge`) ist nicht die ganze Antwort.** Der
Schalter führt Album-Duplikate zusammen; für einzelne Titel behält er
eine Fassung. Wolfs Vorgabe „die Infos beider Kopien mergen" verlangt
den Feld-für-Feld-Abgleich aus 5.5. Der Ablauf ist deshalb:

1. `beet duplicates … -F -p` → Gruppen **auflisten**, nichts tun.
2. Überlebenden bestimmen: **beste Qualität** (verlustfrei vor
   verlustbehaftet, dann Bittiefe, dann Bitrate). ⚠️ Die 1-kbps-FLACs
   von der defekten USB-Platte sind ein bekannter Sonderfall — die
   Regel „höchste Bitrate gewinnt" aus `doubletten-quarantaene.sh`
   fängt ihn korrekt ab.
3. Felder zusammenführen nach der Regel aus 5.5. Konflikte auf die
   Prüfliste, nicht überschreiben.
4. Verlierer **verschieben, nicht löschen** —
   `_QUARANTAENE_Doubletten_<Datum>` unter Beibehaltung des alten
   Pfades, also jederzeit zurückholbar. Die Cloud-Sicherung schließt
   `_QUARANTAENE_*` aus, es entsteht kein Upload.
5. Löschen frühestens nach 30 Tagen und nur auf Wolfs Wort.

Das gilt auch für `Électronique`: der Ordner verschwindet **nicht durch
Löschen**, sondern weil `beet move` seine Titel nach `Electronic`
schreibt. Was danach übrig bleibt, ist ein leerer Ordner.

---

## 7. Frage 6: Reihenfolge, Aufwand, Risiko

| # | Phase | Aufwand | Risiko | Rückholbar? | Wolf nötig? |
|---|---|---|---|---|---|
| **0** | **Sichern + Blutung stoppen:** Datenbank sichern, `frawo_ingest.py` / `audio_hygiene_engine.py` / `frawo-music-watcher.sh` archivieren, **`directory` korrigieren**, Referenzzahlen festhalten | ~30 min | **keins** | ja | nein |
| **1** | **Bestandsaufnahme** (Abschnitt 8), Ergebnis in dieses Dokument | ~1 h | keins (nur lesend) | — | nein |
| **2** | **Ingestion umbauen** (Option B), aber Timer **aus** lassen. Test mit `beet import --pretend` auf 20 Dateien | ~2 h | gering | ja | nein |
| **3** | **Pfadreparatur** (Abschnitt 5): Fingerabdrücke, Inventur, Vorschlagslisten, Umhängen, Prüfen | ~1 Tag, davon mehrere Stunden unbeaufsichtigtes Fingerprinting | **mittel** — die Datenbank wird geschrieben | ja (Sicherung + Blockweise) | ❓ nur für `mehrdeutig.csv` |
| **4** | **Genre-Normalisierung + `beet move`** (Abschnitt 6): 427 → 16/17 Ordner, danach alle Verweise neu | ~1 Tag, plus lange Laufzeit für das physische Verschieben | **hoch** — 9.381 Verweise und die Radio-Rotation hängen daran. Braucht ein Wartungsfenster | ja, aber aufwendig | ✅ Freigabe + Entscheidung `Afro & World` |
| **5** | **Duplikate** (6.4): erst bitgleich, dann Fingerabdruck, Rest als Liste | ~halber Tag | gering (nur verschieben) | ja | ✅ für die dritte Sorte |
| **6** | **Ingestion scharf schalten** + Inbox-Rückstand (724 Dateien) importieren | ~2 h + Laufzeit | gering | ja | nein |
| **7** | **Monitoring** (Abschnitt 9): `node_exporter` in CT120, drei Metriken, Alarme | ~halber Tag | keins | ja | nein |
| **8** | **`chkdsk` gegen den NTFS-Schaden** | Termin | gering, aber Ausfallzeit | — | 🔴 **nur Wolf** (Platte an Windows, CT120 aus) |

**Vorgeschlagene Aufteilung auf Sitzungen:**
Phase 0+1+2 in einer Sitzung (unkritisch, sofort machbar) →
Freigabe → Phase 3 → Zwischenbericht → Freigabe → Phase 4+5 →
Phase 6+7 → Phase 8, wenn Wolf Zeit hat.

**Was ohne Wolf laufen kann** (mit Vorabprüfung und Abnahmekriterien):
Phasen 0, 1, 2, 3 (bis auf die mehrdeutigen Fälle), 6, 7.

**Was Wolfs Blick oder Ohr braucht:**

- `mehrdeutig.csv` aus Phase 3 — welcher von zwei Kandidaten ist gemeint
- die 405 Einträge ohne Treffer — ist die Musik wirklich weg?
- `Afro & World` als 17. Genre — ja oder nein
- die dritte Duplikat-Sorte (Remix vs. Original) — nur per Gehör
- die Vinyl-Digitalisierungs-Mitschnitte in
  `Quarantine/Unidentified_Research` — **bleiben in diesem Plan
  ausdrücklich unangetastet**
- Termin für `chkdsk`

---

## 8. Frage 1: Wie man das Ausmaß misst, ohne die Platte zu ärgern

Die Methode ist bereits erprobt — die Zahlen in Abschnitt 2 stammen
daraus. Sie hält sich an die drei bekannten Fallen dieser Platte:

**Regel 1 — seriell, nie parallel.** Kein `xargs -P`, kein `find |
parallel`. Die Platte (`fuseblk`/ntfs-3g, 5400 rpm) meldet unter
paralleler Last **falsche** Ein-/Ausgabefehler, die bei ruhiger
Einzelprüfung verschwinden. Ein serieller Durchlauf über alle 11.766
Datenbankpfade hat heute **1,8 Sekunden** gebraucht, der Baumdurchlauf
über `Master_Library` **2,4 Sekunden**. Parallelität bringt nichts und
kostet Verlässlichkeit.

**Regel 2 — nie über Textdateien.** Sonderzeichen in Pfaden
(`Ambient  Experimental` mit Ersatzzeichen, `Électronique`, typografische
Apostrophe) gehen beim Umweg über `grep`/`sed`/Zwischendateien verloren.
Heute im Selbstversuch bestätigt: `ls /mnt/music/Master_Library/Électronique`
über SSH scheitert mit `\357\277\275`, derselbe Ordner ist über
`os.listdir()` problemlos erreichbar. Also **direkt mit `os.walk()`**
arbeiten (oder `find -print0`), Pfade als Bytes lesen und mit
`surrogateescape` dekodieren.

**Regel 3 — jeden auffälligen Befund einzeln nachprüfen**, bevor er
gemeldet wird.

Der Messlauf beantwortet vier Fragen und schreibt **nichts**:

1. Wie viele Datenbankpfade existieren nicht? (nach altem Wurzelordner
   aufgeschlüsselt)
2. Wie viele davon ließen sich durch ein reines Präfix-Umschreiben
   retten? (Antwort war: fast keine — deshalb ist die Frage wichtig,
   sie widerlegt die naheliegende Vermutung)
3. Wie viele Dateien in `Master_Library` kennt die Datenbank nicht?
4. Wie viele der toten Einträge finden über Dateiname bzw.
   Interpret + Titel wieder eine Datei?

Als beets-Bordmittel-Gegenprobe, ebenfalls ohne Nebenwirkung:
```bash
beet update --pretend    # zeigt, was beets löschen WÜRDE — nie ohne --pretend
beet stats
beet duplicates --count
beet missing             # unvollständige Alben (andere Frage, aber gratis)
```

Der Messlauf wird **vor und nach jeder Phase** wiederholt. Die Tabelle
in 5.7 ist die Abnahme.

---

## 9. Frage 7: Dass es nicht wieder passiert

Der eigentliche Skandal ist nicht der Fehler, sondern dass er **zehn
Tage und 448 GB lang unbemerkt blieb**. Die Gegenmaßnahmen sind
deshalb zur Hälfte Mess-, nicht Reparaturmaßnahmen.

**9.1 Nur ein Programm bewegt Musikdateien: beets.**
Als Regel in `AGENTS.md` und `NOW.md`, und durchgesetzt dadurch, dass
die Alternativen archiviert sind. Jedes künftige Werkzeug ruft `beet`
auf oder benutzt die beets-Python-Schnittstelle — nie `shutil.move` auf
`/mnt/music`.

**9.2 `node_exporter` in CT120 nachrüsten.** 🔴 **Voraussetzung für
alles Weitere.** Auf dem Wirt `stock-pve` läuft einer mit
`textfile_collector`, im Container **nicht**. Deshalb kann CT120 heute
gar nichts melden. Nachrüsten, in die Prometheus-Ziele auf CT150
aufnehmen — und dabei die bekannte Falle beachten: **Prometheus-Reload
scheitert still**, also `prometheus-neu-laden.sh` benutzen und das
Ziel danach als `up` gegenmessen.

**9.3 Der Wächter gegen tote Pfade** — genau das Problem dieses Plans:
```bash
# täglich, nur lesend
beet update --pretend | grep -c 'file removed'   # → Metrik
```
```
frawo_beets_missing_files <n>
```
Alarm bei `> 0`. Hätte das seit Juli existiert, wäre der Schaden bei
einer Handvoll Einträgen aufgefallen statt bei 8.012.

**9.4 Der Wächter über die Ingestion**, im Muster von
`music-backup-to-cloud.sh` (das schreibt schon so):
```
frawo_music_ingest_last_success_timestamp_seconds <ts>
frawo_music_ingest_imported_total <n>
frawo_music_ingest_failed_total <n>
```
Alarm, wenn 24 h kein Erfolg **oder** `failed` wächst, ohne dass
`imported` wächst. Das ist die Signatur der 2.576 Leerläufe.

**9.5 Der Wächter über die Quarantäne** — `quarantaene-pruefen.sh`
existiert bereits, bekommt einen Timer und eine Metrik:
```
frawo_quarantine_bytes <n>
```
Alarm bei mehr als 5 GB Wachstum pro Tag. Die 448 GB wären nach einem
Tag aufgefallen.

**9.6 Fehlerbudget statt Endlosschleife** — die systemd-Direktiven aus
Abschnitt 4 (`StartLimitBurst`, `OnFailure=`, `RuntimeMaxSec`). Ein
Dienst, der scheitert, **hört auf und meldet sich**. Keine
selbstgeschriebene Wiederholungslogik.

**9.7 Kein zweiter Schreibweg.** AzuraCast liest nur; die Radio-Bridge
ruft bereits `beet import`. Nach dem Archivieren der beiden
Eigenbau-Verschieber gibt es genau **einen** Weg, auf dem Musik in die
Bibliothek kommt.

---

## 10. Was Wolf entscheiden muss

1. **Ingestion:** `frawo_ingest.py` stilllegen und auf `beet import`
   umstellen? *(Empfehlung: ja)*
2. **Pfadreparatur:** Einträge umhängen statt Datenbank neu aufbauen?
   *(Empfehlung: ja — sonst sind ~11.700 recherchierte `vibe`-Einträge
   weg)*
3. **Ordnerstruktur:** 427 → 16 grobe Genre-Ordner, Feinheit im Feld
   `style` plus `_nach_Style\`-Verweisbaum? *(Empfehlung: ja)*
4. **`Afro & World` als 17. Ordner** für Radio-Show 9? *(Empfehlung:
   ja, Wolfs Entscheidung)*
5. **Duplikate:** Verlierer in Quarantäne **verschieben** statt löschen,
   Löschung frühestens nach 30 Tagen? *(Empfehlung: ja)*
6. **`chkdsk`-Termin** für den NTFS-Schaden — braucht Wolf physisch.

---

## 11. Ausdrücklich **nicht** Teil dieses Plans

- `Quarantine/Unidentified_Research` (5,7 GB) — enthält Wolfs eigene
  Vinyl-Digitalisierungs-Mitschnitte. **Nicht anfassen.**
- Die laufende `vibe`/`research_source`-Recherche — läuft parallel
  weiter. ⚠️ Sie schreibt in dieselbe Datenbank; Phase 3 und 4 brauchen
  deshalb ein Fenster, in dem sie ruht.
- `Inbox/yourparty_Libary` — hängt an der laufenden Show-Kuratierung.
- Die 27 GB privaten Fotos in `_Dokumente/Private_Fotos_ungeprueft` —
  eigener Vorgang.
- Die 6,9 GB auf der Wirt-Systemplatte (`/mnt/stick/yourparty.radio`)
  aus der R:-Abschaltung — eigener, kleiner Schritt.
- Verstreute private Handyvideos und Sprachmemos im Musikbaum — werden
  in Phase 1 nebenbei **gezählt**, aber nicht bewegt.

---

## 12. Nachprüfen

Alle Befehle sind **lesend** und können jederzeit ausgeführt werden.

```bash
# Zeigt der Ingest-Timer wirklich nicht mehr?
ssh stock-pve "pct exec 120 -- systemctl is-enabled frawo-music-ingest.timer"   # disabled
ssh stock-pve "pct exec 120 -- systemctl is-active  frawo-music-ingest.timer"   # inactive

# Zeigt beets noch auf die Plattenwurzel statt auf Master_Library?
ssh stock-pve "pct exec 120 -- beet config" | grep -E '^directory|^library'

# Wie viele Einträge würde 'beet update' löschen?  (NIE ohne --pretend)
ssh stock-pve "pct exec 120 -- beet update --pretend" | grep -c 'file removed'

# Wie viele Kuratierungs-Merkmale stehen auf dem Spiel?
#   -> item_attributes: 11.764 x vibe, 11.764 x research_source

# Playlist-Verweise heil?
ssh stock-pve "pct exec 120 -- find /mnt/music/Curated_Playlists -xtype l | wc -l"

# Genre-Ordner auf der ersten Ebene zählen (Sonderzeichen-sicher via python3)
ssh stock-pve "pct exec 120 -- python3 -c \
  'import os;print(len(os.listdir(\"/mnt/music/Master_Library\")))'"

# Läuft ein node_exporter in CT120?  (heute: nein)
ssh stock-pve "pct exec 120 -- ls -d /var/lib/node_exporter/textfile_collector"
```

Der vollständige Messlauf aus Abschnitt 8 wird **nicht** als Datei auf
CT120 abgelegt — er läuft über die Standardeingabe
(`ssh stock-pve "pct exec 120 -- python3 -" < skript.py`) und
hinterlässt nichts auf dem Server.

---

**Erstellt:** 05.09.2026 · Odoo #1263, #1268 ·
alle Zahlen lesend gemessen, nichts verändert.

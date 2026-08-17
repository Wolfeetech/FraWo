# Rekordbox als Kuratier-Zentrale für FraWo Funk — Playlisten-Sync ohne Dateikopien

**Datum:** 2026-08-17
**Status:** Design vorgeschlagen, wartet auf Freigabe (Wolf)
**Odoo-Bezug:** noch zu erstellen — Aufgabe erst nach Design-Freigabe anlegen (Projekt-Konvention)

> **Sicherheitshinweis:** Dieses Repo ist öffentlich. KEINE Zugangsdaten (API-Keys, Passwörter, DB-Creds) in dieses Dokument oder Code committen. Der neue AzuraCast-API-Key liegt in Vaultwarden bzw. wird zur Laufzeit aus einer lokalen, nicht eingecheckten `.env` auf dem StudioPC gelesen.

## 1. Ziel

Wolf soll das Radioprogramm von FraWo Funk **aus Rekordbox heraus kuratieren** können, ohne in AzuraCasts Weboberfläche Playlisten von Hand pflegen zu müssen. Jede Playliste, die Wolf in Rekordbox anlegt/pflegt, soll automatisch — im Hintergrund, ohne dass er etwas dafür tun muss — als gleichnamige Playliste in AzuraCast verfügbar sein, mit demselben Titelbestand. **AzuraCast bleibt der Sender-Betrieb**: wann welche Playliste sendet (Zeitplan/Timetable, z. B. "Show XYZ läuft Freitag 12 Uhr"), entscheidet Wolf weiterhin dort — das wird durch diesen Sync nicht angefasst oder automatisiert.

Harte Anforderung: **keine Datei wird kopiert oder dupliziert.** Rekordbox, beets/CT120 und AzuraCast zeigen am Ende alle auf dieselben physischen Dateien.

## 2. Ist-Zustand (live verifiziert 2026-08-17)

- Musikbibliothek: 9.264 Titel / 420 GB, von `beets` auf CT120 verwaltet (`M:\` auf dem StudioPC = `/mnt/music` in CT120). `beets` fasst per Konfiguration nie Dateien an (`copy: no, move: no`) — genau das gibt uns die stabile Pfadbasis, auf der dieser Sync aufbaut.
- AzuraCast (Station "FraWo Funk", VM210, `10.1.0.38`) läuft live und spielt bereits aus derselben Bibliothek. Der dokumentierte API-Key ist **tot** — aktueller Notbehelf ist direkter MariaDB-Zugriff, den NOW.md selbst als Falle markiert (Spalten-Mehrdeutigkeit bei `storage_location_id`).
- Es existiert bereits ein einseitiger, manuell angestoßener Vorläufer: `deployments/musikverwaltung/playliste-exportieren.sh` (beets-Abfrage → M3U8, Pfad-Übersetzung `/mnt/music` ↔ `M:\`, gedacht für manuellen Rekordbox-Import). Dieses Design ersetzt den manuellen Import durch einen automatischen, nutzt aber dieselbe Pfad-Übersetzungslogik.
- Rekordbox (v7.2.17, StudioPC) wurde heute bereinigt: 516 Titel mit defekter Dateigröße (0 Byte) aus der Sammlung entfernt, Bestand jetzt 7.428 saubere Titel, 7 Playlisten. Datenbank liegt verschlüsselt (SQLCipher) unter `%APPDATA%\Pioneer\rekordbox\master.db`, WAL-Modus aktiv.
- `pyrekordbox` (Python, aktiv gepflegt) kann diese Datenbank lesen — heute bereits erfolgreich eingesetzt (Lesen einer Kopie, sicher auch bei laufendem Rekordbox; Schreiben nur bei geschlossenem Rekordbox getestet).
- Ein zweiter Ordner `M:\Quarantine` (~42.000 Dateien, Datenrettung/Duplikate) ist **nicht Teil dieses Designs** — separate, noch zu erstellende Aufgabe (siehe Abschnitt 8).

## 3. Ansatz

Ein Python-Skript liest periodisch eine **Kopie** von Rekordbox' Datenbank (nie die Live-Datei — das hat sich heute beim Aufräumen als der sichere Weg bestätigt), extrahiert die komplette Playlisten-Struktur samt Titel-Zuordnung, übersetzt die Windows-Pfade in das Format, das AzuraCasts Bibliothek erwartet, und schickt jede Playliste über AzuraCasts **offizielle Import-API** (`POST /api/station/{id}/playlist/{id}/import`, Pfad-Abgleich gegen die längst vorhandene Bibliothek — kein Datei-Upload). Das ersetzt den heutigen Notbehelf über die AzuraCast-Datenbank durch einen unterstützten, versionierten Weg.

## 4. Komponenten & Ablauf

### 4.0 AzuraCast-API-Zugang wiederherstellen (Enabler)
Neuen API-Key für Station "FraWo Funk" erzeugen (Web-Admin oder `azuracast_cli`), alten Key revoken, neuen Key in **Vaultwarden** ablegen und für das Skript aus einer lokalen `.env` auf dem StudioPC lesen (nicht eingecheckt).

### 4.1 Pfad-Zuordnung verifizieren (Enabler — wichtig, bevor irgendwas automatisiert wird)
Bevor das Sync-Skript scharf geschaltet wird: einmal händisch bestätigen, dass `M:\...` (Rekordbox-Sicht) und AzuraCasts Speicherort für Station 1 (`network_library`, laut vorherigem Radio-Design-Dokument `//10.1.0.94/radio`) tatsächlich **dieselbe** Freigabe sind wie `/mnt/music` (beets/CT120-Sicht) — nicht nur ähnlich benannt. Genau diese Art Verwechslung (`storage_location_id`) hat schon einmal zu falschen Ergebnissen geführt (siehe NOW.md-Fallen-Tabelle). Eine Testdatei an bekanntem Pfad reicht als Nachweis.

### 4.2 Sync-Skript (das Kernstück)
- **Wo:** läuft auf dem StudioPC selbst (dort liegt Rekordbox' Datenbank; keine zusätzliche Infrastruktur nötig). Python + `pyrekordbox` + `requests`.
- **Ablauf pro Lauf:**
  1. `master.db` (+ `-wal`/`-shm`) in einen Scratch-Ordner kopieren.
  2. Playlisten-Baum + Titel-Zuordnung + Dateipfade aus der Kopie lesen.
  3. Jeden Pfad von `M:\...` (Backslash) auf den AzuraCast-relativen Pfad übersetzen (gleiche Logik wie `playliste-exportieren.sh`).
  4. Pro Rekordbox-Playliste: existiert in AzuraCast noch keine gleichnamige Playliste, zuerst über AzuraCasts Standard-Playlist-API anlegen; danach über die Import-API (`playlist/{id}/import`) den Titelbestand befüllen bzw. aktualisieren. Die genaue Reihenfolge/Fehlerbehandlung dieser zwei API-Aufrufe ist ein Implementierungsdetail, das im Umsetzungsplan (nächster Schritt) anhand der echten API-Antworten festgelegt wird.
  5. Ergebnis prüfen: Rückmeldung der API auswerten, **tatsächliche** Titelzahl der Playliste in AzuraCast danach abfragen und mit der Quelle vergleichen — nicht nur "Anfrage abgeschickt" als Erfolg werten (siehe Abschnitt 6).
- **Auslöser:** Windows-Aufgabenplanung, alle 15–30 Minuten (Startwert, später justierbar). Zusätzlich ein Doppelklick-Skript für sofortigen manuellen Anstoß, wenn Wolf eine Änderung sofort live sehen will.

### 4.3 Bewertungen (Ratings) — bewusst zurückgestellt
Rekordbox' `Rating`-Feld ist technisch mitgelesen erreichbar, wird in Phase 1 aber **nicht** weiterverarbeitet (siehe Abschnitt 8 — YAGNI, kein aktueller Bedarf belegt).

## 5. Datenfluss

```
Rekordbox (StudioPC, master.db)
        │  (Kopie ziehen, nie live lesen)
        ▼
Sync-Skript: Playlisten + Pfade lesen  ──►  Pfad-Übersetzung (M:\ → AzuraCast-relativ)
                                                   │
                                                   ▼
                                    AzuraCast-API (10.1.0.38)
                                    POST playlist/import (Pfad-Abgleich, keine Kopie)
                                                   │
                                                   ▼
                        Playlisten in AzuraCast verfügbar  ──►  Wolf setzt Zeitplan/Timetable
                                                                  weiterhin manuell in AzuraCast
```

## 6. Fehlerbehandlung & Sicherheit

- **Nie die Live-Datenbank für Lesevorgänge anfassen** — immer Kopie zuerst (heute bereits als sicheres Muster bestätigt).
- **Schreibende Zugriffe auf Rekordbox' Datenbank** (z. B. weitere Aufräum-Aktionen) nur bei geschlossenem Rekordbox — nicht Teil dieses Sync-Skripts, das schreibt nur in Richtung AzuraCast.
- **Am Ergebnis prüfen, nicht am Vorgang:** nach jedem Sync-Lauf die tatsächliche Titelzahl je Playliste in AzuraCast gegenprüfen. Genau das Fehlen dieser Prüfung hat beim Backup-Cron zwei Wochen lang einen stillen Ausfall verdeckt.
- **Kein Dead-Air:** Der Sync verändert nur Playlist-**Inhalte**, nie den Sendeplan selbst — ein fehlerhafter Lauf kann höchstens eine Playliste falsch befüllen, nicht den Sender stumm schalten.
- **Bekannte Grenze:** `pyrekordbox` ist eine inoffizielle, aber aktiv gepflegte Bibliothek. Ein künftiges großes Rekordbox-Update könnte sie kurzzeitig brechen — niedriger, aber nicht null Wartungsaufwand. Fallback: Rekordbox' eigener XML-Export (`Sammlung exportieren`) liest dieselben Daten offiziell, aber nur manuell auslösbar — als dokumentierter Rückfallweg, nicht automatisiert.
- **Keine Secrets im Repo:** API-Key nur in Vaultwarden/lokaler `.env`.

## 7. Verifikation (Definition of Done)

1. Eine in Rekordbox neu angelegte/geänderte Playliste erscheint spätestens nach einem Sync-Zyklus mit identischem Titelbestand in AzuraCast.
2. Der Titelbestand ist über Pfad-Abgleich verknüpft — keine neue Datei auf der Festplatte, keine Verdopplung im Speicherverbrauch.
3. Eine Playliste, die Wolf in Rekordbox löscht, wird beim nächsten Lauf sichtbar erkannt (mindestens geloggt, Verhalten in AzuraCast selbst nach Absprache — löschen oder leeren).
4. Ein manuell ausgelöster Sync-Lauf zeigt in unter einer Minute Ergebnis.
5. Zeitplan/Timetable in AzuraCast bleibt von diesem Sync vollständig unberührt.

## 8. Ausdrücklich NICHT in diesem Design (Scope-Grenzen / YAGNI)

- **Bewertungs-Sync (Ratings)** zwischen Rekordbox und AzuraCast/beets — kein belegter Bedarf, spätere Phase.
- **Automatischer Zeitplan/Timetable** in AzuraCast — bleibt bewusst manuelle Entscheidung von Wolf, nicht Teil der Automatisierung.
- **Rückrichtung** (AzuraCast-Wiedergabehistorie zurück nach Rekordbox) — nicht angefragt.
- **Aufräumen der 42.000 Dateien in `M:\Quarantine`** (Datenrettung/Duplikate) — eigene, noch zu erstellende Aufgabe, thematisch getrennt.
- **Genre-/Tag-Nachpflege** der ~7.400 noch unbearbeiteten Dateien (offener NOW.md-Punkt) — unabhängig von diesem Sync.

## 9. Roadmap (Einordnung)

- **Phase 1 (dieses Dokument):** Playlisten-Sync Rekordbox → AzuraCast, keine Duplikate, API-basiert.
- **Phase 2 (optional, später):** Bewertungs-Sync, falls sich in der Praxis ein echter Bedarf zeigt.
- **Separat, nicht Teil dieser Roadmap:** Quarantäne-Bereinigung (42.000 Dateien), verbleibende Tag-Nachpflege.

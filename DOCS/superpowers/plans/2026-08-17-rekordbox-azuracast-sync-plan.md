# Rekordbox → AzuraCast Playlisten-Sync — Umsetzungsplan

> **Für ausführende Agenten:** ERFORDERLICHE UNTER-SKILL: `superpowers:executing-plans` oder `superpowers:subagent-driven-development`, Aufgabe für Aufgabe. Schritte nutzen Checkbox-Syntax (`- [ ]`).

**Ziel:** Wolf kuratiert das Radioprogramm künftig in Rekordbox statt in AzuraCasts Weboberfläche. Ein Skript auf dem StudioPC synchronisiert Rekordbox-Playlisten automatisch nach AzuraCast — per Pfad-Abgleich, ohne eine einzige Datei zu kopieren. Zuerst wird Rekordbox einmalig mit dem heute live laufenden Sendeprogramm befüllt (Grundausrüstung), danach läuft der Sync dauerhaft in die andere Richtung (Rekordbox → AzuraCast).

**Architektur:** Python-Skripte auf dem StudioPC, `pyrekordbox` für die Rekordbox-Datenbank (immer Kopie lesen, nur bei geschlossenem Rekordbox schreiben — heute bereits bestätigtes sicheres Muster), AzuraCasts REST-API für den Schreibweg nach AzuraCast. Windows-Aufgabenplanung für den wiederkehrenden Lauf.

**Technik:** Python 3.13 + `pyrekordbox` (bereits installiert) + `requests` · AzuraCast REST-API (`https://10.1.0.38`, Station-ID 1 „FraWo Funk") · `deployments/musikverwaltung/playliste-exportieren.sh` als Vorlage für die Pfad-Übersetzung

**Spec:** `DOCS/superpowers/specs/2026-08-17-rekordbox-azuracast-sync-design.md`

## Globale Randbedingungen

- **Nie die Live-`master.db` für Lesevorgänge anfassen** — immer zuerst nach `%TEMP%` kopieren (`master.db`, `master.db-wal`, `master.db-shm`).
- **Schreibend nur bei geschlossenem Rekordbox** (`rekordbox.exe` UND `rekordboxAgent.exe` — heute erlebt, dass der Agent-Prozess separat läuft und mitgeschlossen werden muss).
- **Kein Datei-Upload, keine Kopie** — AzuraCast bekommt nur Pfade, nie Audiodaten.
- **Keine Secrets im Repo.** API-Key nur in Vaultwarden + lokaler `.env` (`deployments/musikverwaltung/rekordbox_sync/.env`, in `.gitignore`).
- **Am Ergebnis prüfen, nicht am Vorgang** — jeder Schreibvorgang nach AzuraCast wird durch einen Lesevorgang gegengeprüft.
- Alle Pfad-Übersetzungen folgen dem Muster aus `playliste-exportieren.sh`: `M:\` (Windows/Rekordbox) ↔ `/mnt/music` (Linux/beets) ↔ AzuraCast-relativer Medienpfad.

---

## Aufgabe 1: AzuraCast-API-Zugang wiederherstellen

**Warum zuerst:** Ohne funktionierenden Key kann kein nachfolgender Schritt gegen die echte API getestet werden.

**Dateien:**
- Erstellen: `deployments/musikverwaltung/rekordbox_sync/.env.example` (Vorlage, ohne echten Key)
- Prüfen/ergänzen: `.gitignore` (Zeile `deployments/musikverwaltung/rekordbox_sync/.env` muss drinstehen)

**Schnittstellen:**
- Liefert: einen funktionierenden `AZURACAST_API_KEY` + `AZURACAST_BASE_URL`, den alle folgenden Aufgaben lesen.

- [ ] **Schritt 1: Verfügbare AzuraCast-CLI-Befehle prüfen**

```sh
ssh stock-pve "qm guest exec 210 -- docker exec azuracast azuracast_cli list" | grep -i api
```
Erwartet: ein Unterbefehl mit „api-key" im Namen (z. B. `azuracast:api-key:generate`). Namen ggf. abweichend — den echten Namen aus der Liste übernehmen.

- [ ] **Schritt 2: Neuen Key für den Admin-Nutzer erzeugen**

```sh
ssh stock-pve "qm guest exec 210 -- docker exec azuracast azuracast_cli <gefundener-befehl> <admin-email>"
```
Erwartet: Ausgabe enthält einen neuen API-Key-String. Falls die CLI keinen Weg anbietet: Web-Admin `https://10.1.0.38/admin/api-keys` nutzen (Login-Daten aus Vaultwarden).

- [ ] **Schritt 3: Key sofort gegen die echte API testen**

```sh
curl -sk -H "X-API-Key: <neuer-key>" https://10.1.0.38/api/station/1/playlists | head -c 500
```
Erwartet: JSON-Array mit Playlist-Objekten (Felder u. a. `id`, `name`, `is_enabled`). Bei Fehler (401/403) Key-Erzeugung wiederholen.

- [ ] **Schritt 4: Key in Vaultwarden ablegen**

Neuer Eintrag „AzuraCast API Key (FraWo Funk)" in Vaultwarden, Feld „API Key" = der Key. Alten toten Key-Eintrag als veraltet markieren, nicht löschen.

- [ ] **Schritt 5: Lokale `.env` + Vorlage anlegen**

`deployments/musikverwaltung/rekordbox_sync/.env`:
```
AZURACAST_BASE_URL=https://10.1.0.38
AZURACAST_STATION_ID=1
AZURACAST_API_KEY=<neuer-key>
```

`deployments/musikverwaltung/rekordbox_sync/.env.example` (im Repo, ohne echten Wert):
```
AZURACAST_BASE_URL=https://10.1.0.38
AZURACAST_STATION_ID=1
AZURACAST_API_KEY=hier-eigenen-key-eintragen
```

- [ ] **Schritt 6: `.gitignore` prüfen**

```sh
grep -q "rekordbox_sync/.env$" .gitignore || echo "deployments/musikverwaltung/rekordbox_sync/.env" >> .gitignore
```

- [ ] **Schritt 7: Commit**

```sh
git add deployments/musikverwaltung/rekordbox_sync/.env.example .gitignore
git commit -m "chore: AzuraCast-API-Zugang fuer Rekordbox-Sync vorbereitet (neuer Key in Vaultwarden)"
```

---

## Aufgabe 2: Pfad-Zuordnung verifizieren

**Warum:** Genau diese Verwechslung (`storage_location_id`) hat im Projekt schon einmal zu falschen Ergebnissen geführt. Einmal nachmessen statt annehmen.

**Schnittstellen:**
- Verbraucht: `AZURACAST_API_KEY` aus Aufgabe 1.
- Liefert: die bestätigte Übersetzungsregel (Präfix-Länge/-Ersetzung), die Aufgabe 3 und 5 direkt verwenden.

- [ ] **Schritt 1: Eine echte, bekannte Datei aus AzuraCast holen**

```sh
curl -sk -H "X-API-Key: <key>" "https://10.1.0.38/api/station/1/files?perPage=1" | python3 -m json.tool
```
Erwartet: ein Objekt mit einem `path`-Feld, z. B. `"path": "House/Artist/Album/Track.flac"`.

- [ ] **Schritt 2: Dieselbe Datei unter `M:\` suchen**

Auf dem StudioPC:
```powershell
Test-Path "M:\Master_Library\House\Artist\Album\Track.flac"
```
Erwartet: `True`. Ordnername ggf. an Aufgabe-2-Schritt-1-Ergebnis anpassen (z. B. `Master_Library\` als Präfix, den AzuraCast selbst nicht mitführt).

- [ ] **Schritt 3: Übersetzungsregel schriftlich festhalten**

In `deployments/musikverwaltung/rekordbox_sync/README.md` (neu anlegen) die bestätigte Regel notieren, z. B.:
```
AzuraCast-Pfad "House/Artist/Album/Track.flac"
   entspricht
Rekordbox-Pfad "M:/Master_Library/House/Artist/Album/Track.flac"
→ Regel: AzuraCast-Pfad = Rekordbox-Pfad ohne "M:/Master_Library/", Backslash zu Slash.
```

- [ ] **Schritt 4: Commit**

```sh
git add deployments/musikverwaltung/rekordbox_sync/README.md
git commit -m "docs: Pfad-Uebersetzungsregel M:\ <-> AzuraCast bestaetigt"
```

---

## Aufgabe 3: Grundausrüstung — aktuelle AzuraCast-Playlisten in Rekordbox anlegen (einmalig)

**Warum an dieser Stelle:** Bootstrap, bevor Rekordbox zur Quelle der Wahrheit wird — sonst startet Wolf mit einer leeren Bibliotheks-Struktur und verliert die heutige Kuration. Nutzt dieselbe Lese-/Schreib-Mechanik, die der dauerhafte Sync später ohnehin braucht.

**Dateien:**
- Erstellen: `deployments/musikverwaltung/rekordbox_sync/seed_rekordbox_from_azuracast.py`
- Test: manueller Lauf + Verifikation (kein automatisierter Test — einmaliges Skript, echte Daten)

**Schnittstellen:**
- Verbraucht: `.env` aus Aufgabe 1, Übersetzungsregel aus Aufgabe 2.
- Produziert: Rekordbox-Playlisten (Top-Level-Ordner „Radio (Import 2026-08-17)"), gefüllt mit den zum Zeitpunkt des Laufs live in AzuraCast aktiven Titeln.

- [ ] **Schritt 1: Skript schreiben**

```python
# deployments/musikverwaltung/rekordbox_sync/seed_rekordbox_from_azuracast.py
"""
Einmaliges Bootstrap: liest die aktuell in AzuraCast aktiven Playlisten
und legt sie mit ihren Titeln in Rekordbox an. Vor dem Lauf muss
Rekordbox (rekordbox.exe UND rekordboxAgent.exe) geschlossen sein.
"""
import os
import sys
from collections import defaultdict

import requests
from dotenv import load_dotenv
from pyrekordbox.db6 import Rekordbox6Database

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

BASE_URL = os.environ["AZURACAST_BASE_URL"]
STATION_ID = os.environ["AZURACAST_STATION_ID"]
API_KEY = os.environ["AZURACAST_API_KEY"]

# Aus Aufgabe 2 bestätigte Regel:
AZURACAST_PREFIX_STRIP = ""  # z.B. leer, falls AzuraCast-Pfad schon relativ zu Master_Library ist
REKORDBOX_ROOT = r"M:\Master_Library"

FOLDER_NAME = "Radio (Import 2026-08-17)"


def fetch_files():
    resp = requests.get(
        f"{BASE_URL}/api/station/{STATION_ID}/files",
        headers={"X-API-Key": API_KEY},
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def azuracast_path_to_rekordbox(az_path: str) -> str:
    rel = az_path
    if AZURACAST_PREFIX_STRIP and rel.startswith(AZURACAST_PREFIX_STRIP):
        rel = rel[len(AZURACAST_PREFIX_STRIP):]
    rel = rel.replace("/", "\\").lstrip("\\")
    return os.path.join(REKORDBOX_ROOT, rel)


def group_by_playlist(files):
    by_playlist = defaultdict(list)
    for f in files:
        rb_path = azuracast_path_to_rekordbox(f["path"])
        for pl in f.get("playlists", []):
            by_playlist[pl["name"]].append(rb_path)
    return by_playlist


def main():
    files = fetch_files()
    by_playlist = group_by_playlist(files)
    if not by_playlist:
        print("Keine Playlisten mit Titeln in AzuraCast gefunden - abgebrochen.")
        sys.exit(1)

    db = Rekordbox6Database()
    folder = db.create_playlist_folder(FOLDER_NAME)

    # Pfad -> Content-Objekt, einmal aufbauen statt pro Titel neu zu suchen
    path_to_content = {c.FolderPath: c for c in db.get_content() if c.FolderPath}

    for name, paths in by_playlist.items():
        pl = db.create_playlist(name, parent=folder)
        added, missing = 0, 0
        for p in paths:
            content = path_to_content.get(p.replace("\\", "/"))
            if content is None:
                missing += 1
                continue
            db.add_to_playlist(pl, content)
            added += 1
        print(f"{name}: {added} Titel uebernommen, {missing} in Rekordbox nicht gefunden")

    db.commit()
    print("Fertig. Rekordbox jetzt wieder oeffnen und Ordner "
          f"'{FOLDER_NAME}' pruefen.")


if __name__ == "__main__":
    main()
```

- [ ] **Schritt 2: Abhängigkeit ergänzen**

```sh
python3 -m pip install python-dotenv
```

- [ ] **Schritt 3: Rekordbox vollständig schließen**

```powershell
Get-Process rekordbox,rekordboxAgent -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Get-Process rekordbox,rekordboxAgent -ErrorAction SilentlyContinue
```
Erwartet: keine Ausgabe (kein laufender Prozess mehr).

- [ ] **Schritt 4: Sicherheitskopie der Live-Datenbank**

```sh
cp -r "$APPDATA/Pioneer/rekordbox" "$APPDATA/Pioneer/rekordbox_backup_vor_seed_$(date +%Y%m%d_%H%M)"
```

- [ ] **Schritt 5: Skript ausführen**

```sh
cd deployments/musikverwaltung/rekordbox_sync
python3 seed_rekordbox_from_azuracast.py
```
Erwartet: pro AzuraCast-Playlist eine Zeile „X Titel übernommen, Y nicht gefunden". Bei vielen „nicht gefunden": Übersetzungsregel aus Aufgabe 2 nochmal prüfen, bevor weitergemacht wird.

- [ ] **Schritt 6: Ergebnis in Rekordbox prüfen**

Rekordbox öffnen, Ordner „Radio (Import 2026-08-17)" ansehen — pro Playlist die Titelzahl mit der AzuraCast-Quelle (Schritt 1-Ausgabe) vergleichen.

- [ ] **Schritt 7: Commit**

```sh
git add deployments/musikverwaltung/rekordbox_sync/seed_rekordbox_from_azuracast.py
git commit -m "feat: einmaliges Bootstrap-Skript AzuraCast-Playlisten -> Rekordbox"
```

---

## Aufgabe 4: Rekordbox-Playlisten sicher auslesen (Kernstück, Leserichtung)

**Dateien:**
- Erstellen: `deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py`
- Test: `deployments/musikverwaltung/rekordbox_sync/test_rekordbox_sync.py`

**Schnittstellen:**
- Produziert: `read_rekordbox_playlists() -> dict[str, list[str]]` — Playlistname → Liste von `M:\...`-Pfaden. Wird von Aufgabe 5 direkt aufgerufen.

- [ ] **Schritt 1: Test schreiben (gegen eine Kopie mit bekanntem Inhalt)**

```python
# deployments/musikverwaltung/rekordbox_sync/test_rekordbox_sync.py
import shutil
import tempfile
import os
from rekordbox_sync import read_rekordbox_playlists, REKORDBOX_LIVE_DIR


def test_read_rekordbox_playlists_returns_existing_playlist():
    result = read_rekordbox_playlists()
    assert isinstance(result, dict)
    # Aus Aufgabe 3 wissen wir: mindestens eine Playlist unter
    # "Radio (Import 2026-08-17)" muss existieren und Titel enthalten.
    all_names = list(result.keys())
    assert len(all_names) > 0
    first_playlist_tracks = result[all_names[0]]
    assert all(p.upper().startswith("M:") for p in first_playlist_tracks)
```

- [ ] **Schritt 2: Test ausführen, Fehlschlag bestätigen**

```sh
cd deployments/musikverwaltung/rekordbox_sync
python3 -m pytest test_rekordbox_sync.py -v
```
Erwartet: FAIL, `ModuleNotFoundError` oder `ImportError: read_rekordbox_playlists`.

- [ ] **Schritt 3: Implementierung**

```python
# deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py
"""Liest Rekordbox-Playlisten sicher aus einer Kopie der Datenbank."""
import os
import shutil
import tempfile

from pyrekordbox.db6 import Rekordbox6Database

REKORDBOX_LIVE_DIR = os.path.expandvars(r"%APPDATA%\Pioneer\rekordbox")


def _copy_live_db(dest_dir: str) -> None:
    for fname in ("master.db", "master.db-wal", "master.db-shm"):
        src = os.path.join(REKORDBOX_LIVE_DIR, fname)
        if os.path.exists(src):
            shutil.copy(src, dest_dir)


def read_rekordbox_playlists() -> dict[str, list[str]]:
    """Playlistname -> Liste von M:\\...-Dateipfaden, aus einer sicheren Kopie gelesen."""
    with tempfile.TemporaryDirectory(prefix="rb_sync_") as tmp:
        _copy_live_db(tmp)
        db = Rekordbox6Database(db_dir=tmp)

        result: dict[str, list[str]] = {}
        for playlist in db.get_playlist():
            # Nur echte Playlisten mit Titeln, keine reinen Ordner
            songs = db.get_playlist_contents(playlist)
            paths = [s.FolderPath for s in songs if s.FolderPath]
            if paths:
                result[playlist.Name] = paths
        return result


if __name__ == "__main__":
    for name, tracks in read_rekordbox_playlists().items():
        print(f"{name}: {len(tracks)} Titel")
```

- [ ] **Schritt 4: Test erneut ausführen**

```sh
python3 -m pytest test_rekordbox_sync.py -v
```
Erwartet: PASS (vorausgesetzt Aufgabe 3 wurde ausgeführt und mindestens eine Playlist mit Titeln existiert).

- [ ] **Schritt 5: Commit**

```sh
git add deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py deployments/musikverwaltung/rekordbox_sync/test_rekordbox_sync.py
git commit -m "feat: sicheres Auslesen der Rekordbox-Playlisten (Kopie-Muster)"
```

---

## Aufgabe 5: Pfad-Übersetzung + Schreiben nach AzuraCast

**Dateien:**
- Ändern: `deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py`
- Ändern: `deployments/musikverwaltung/rekordbox_sync/test_rekordbox_sync.py`

**Schnittstellen:**
- Verbraucht: `read_rekordbox_playlists()` aus Aufgabe 4, Übersetzungsregel aus Aufgabe 2.
- Produziert: `sync_to_azuracast(playlists: dict[str, list[str]]) -> dict[str, dict]` — Playlistname → `{"gesendet": int, "bestaetigt": int}`. Von Aufgabe 6 (Prüfung) und Aufgabe 7 (Scheduler-Aufruf) verwendet.

- [ ] **Schritt 1: Test schreiben (gegen echte, aber sanfte AzuraCast-Anfragen)**

```python
def test_rekordbox_path_to_azuracast_translates_correctly():
    from rekordbox_sync import rekordbox_path_to_azuracast
    result = rekordbox_path_to_azuracast(r"M:\Master_Library\House\Artist\Track.flac")
    assert result == "House/Artist/Track.flac"


def test_sync_creates_or_updates_playlist_and_verifies_count():
    from rekordbox_sync import sync_to_azuracast
    # Nutzt eine harmlose Testplaylist statt einer echten Sende-Playlist
    result = sync_to_azuracast({"Sync-Test-Playlist": [
        r"M:\Master_Library\House\Artist\Track.flac",
    ]})
    assert result["Sync-Test-Playlist"]["gesendet"] == 1
    assert result["Sync-Test-Playlist"]["bestaetigt"] == 1
```

- [ ] **Schritt 2: Test ausführen, Fehlschlag bestätigen**

```sh
python3 -m pytest test_rekordbox_sync.py -v -k translates_correctly
```
Erwartet: FAIL, `ImportError: rekordbox_path_to_azuracast`.

- [ ] **Schritt 3: Implementierung ergänzen**

```python
# Ergänzung in deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py
import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
BASE_URL = os.environ["AZURACAST_BASE_URL"]
STATION_ID = os.environ["AZURACAST_STATION_ID"]
API_KEY = os.environ["AZURACAST_API_KEY"]
HEADERS = {"X-API-Key": API_KEY}

REKORDBOX_ROOT = r"M:\Master_Library"


def rekordbox_path_to_azuracast(rb_path: str) -> str:
    rel = rb_path[len(REKORDBOX_ROOT):] if rb_path.upper().startswith(REKORDBOX_ROOT.upper()) else rb_path
    return rel.replace("\\", "/").lstrip("/")


def _get_or_create_playlist_id(name: str) -> int:
    resp = requests.get(f"{BASE_URL}/api/station/{STATION_ID}/playlists", headers=HEADERS, verify=False, timeout=30)
    resp.raise_for_status()
    for pl in resp.json():
        if pl["name"] == name:
            return pl["id"]

    resp = requests.post(
        f"{BASE_URL}/api/station/{STATION_ID}/playlists",
        headers=HEADERS,
        json={"name": name, "type": "default", "source": "songs", "is_enabled": True},
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def sync_to_azuracast(playlists: dict[str, list[str]]) -> dict[str, dict]:
    results = {}
    for name, rb_paths in playlists.items():
        az_paths = [rekordbox_path_to_azuracast(p) for p in rb_paths]
        m3u = "#EXTM3U\n" + "\n".join(az_paths)

        playlist_id = _get_or_create_playlist_id(name)
        resp = requests.post(
            f"{BASE_URL}/api/station/{STATION_ID}/playlist/{playlist_id}/import",
            headers=HEADERS,
            files={"playlist_file": ("import.m3u", m3u)},
            verify=False,
            timeout=60,
        )
        resp.raise_for_status()

        # Am Ergebnis pruefen, nicht am Vorgang: tatsaechlichen Bestand zurueckholen
        check = requests.get(
            f"{BASE_URL}/api/station/{STATION_ID}/playlist/{playlist_id}",
            headers=HEADERS, verify=False, timeout=30,
        )
        check.raise_for_status()
        bestaetigt = check.json().get("num_songs", 0)

        results[name] = {"gesendet": len(az_paths), "bestaetigt": bestaetigt}
    return results
```

- [ ] **Schritt 4: Tests erneut ausführen**

```sh
python3 -m pytest test_rekordbox_sync.py -v
```
Erwartet: PASS. Bei Abweichung im Feldnamen (z. B. `num_songs` heißt in der echten API anders): tatsächliche Antwort mit `curl` prüfen (siehe Aufgabe 1, Schritt 3) und Feldnamen anpassen — das war im Design als offener Punkt markiert.

- [ ] **Schritt 5: Testplaylist aus AzuraCast wieder entfernen**

```sh
curl -sk -X DELETE -H "X-API-Key: <key>" "https://10.1.0.38/api/station/1/playlist/<id>"
```

- [ ] **Schritt 6: Commit**

```sh
git add deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py deployments/musikverwaltung/rekordbox_sync/test_rekordbox_sync.py
git commit -m "feat: Pfad-Uebersetzung und AzuraCast-Schreibweg mit Ergebnispruefung"
```

---

## Aufgabe 6: Gesamtlauf mit Protokoll

**Dateien:**
- Ändern: `deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py`

**Schnittstellen:**
- Verbraucht: `read_rekordbox_playlists()`, `sync_to_azuracast()`.
- Produziert: `main()` — Kommandozeilen-Einstiegspunkt, von Aufgabe 7 aus der Aufgabenplanung aufgerufen.

- [ ] **Schritt 1: `main()` ergänzen**

```python
# Ergänzung in rekordbox_sync.py
import logging
import sys

LOG_PATH = os.path.join(os.path.dirname(__file__), "sync.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)


def main():
    playlists = read_rekordbox_playlists()
    if not playlists:
        logging.warning("Keine Rekordbox-Playlisten mit Titeln gefunden - nichts zu tun.")
        return 0

    results = sync_to_azuracast(playlists)
    fehler = 0
    for name, r in results.items():
        if r["gesendet"] != r["bestaetigt"]:
            logging.error(f"{name}: {r['gesendet']} gesendet, aber nur {r['bestaetigt']} in AzuraCast bestaetigt")
            fehler += 1
        else:
            logging.info(f"{name}: {r['bestaetigt']} Titel bestaetigt")

    if fehler:
        logging.error(f"{fehler} Playlisten mit Abweichung - siehe oben")
        return 1
    logging.info("Alle Playlisten erfolgreich synchronisiert")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Schritt 2: Manuell laufen lassen**

```sh
cd deployments/musikverwaltung/rekordbox_sync
python3 rekordbox_sync.py
```
Erwartet: Exit-Code 0, `sync.log` enthält für jede Playlist eine „bestaetigt"-Zeile.

- [ ] **Schritt 3: Commit**

```sh
git add deployments/musikverwaltung/rekordbox_sync/rekordbox_sync.py
git commit -m "feat: Gesamtlauf mit Protokoll und Ergebnis-Exitcode"
```

---

## Aufgabe 7: Windows-Aufgabenplanung einrichten

**Dateien:**
- Erstellen: `deployments/musikverwaltung/rekordbox_sync/setup_task.ps1`
- Erstellen: `deployments/musikverwaltung/rekordbox_sync/jetzt_synchronisieren.bat`

**Schnittstellen:**
- Verbraucht: `rekordbox_sync.py` aus Aufgabe 6.

- [ ] **Schritt 1: Wiederkehrende Aufgabe registrieren**

```powershell
# deployments/musikverwaltung/rekordbox_sync/setup_task.ps1
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$action = New-ScheduledTaskAction -Execute "python3" -Argument "rekordbox_sync.py" -WorkingDirectory $scriptDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 20) -RepetitionDuration ([TimeSpan]::MaxValue)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "FraWo-Rekordbox-Sync" -Action $action -Trigger $trigger -Principal $principal -Force
Get-ScheduledTask -TaskName "FraWo-Rekordbox-Sync" | Select-Object TaskName, State
```
Bewusst `RunLevel Limited` (nicht `Highest`) — braucht keine Adminrechte, läuft ohne UAC-Unterbrechung (heute bei HWiNFO als unnötig erkannt, hier von Anfang an richtig gesetzt).

- [ ] **Schritt 2: Ausführen und verifizieren**

```powershell
.\setup_task.ps1
Start-ScheduledTask -TaskName "FraWo-Rekordbox-Sync"
Start-Sleep -Seconds 5
Get-ScheduledTaskInfo -TaskName "FraWo-Rekordbox-Sync" | Select-Object LastRunTime, LastTaskResult
```
Erwartet: `LastTaskResult` = `0`.

- [ ] **Schritt 3: Sofort-Anstoß-Skript für manuelle Läufe**

```bat
@echo off
cd /d "%~dp0"
python3 rekordbox_sync.py
pause
```

- [ ] **Schritt 4: Commit**

```sh
git add deployments/musikverwaltung/rekordbox_sync/setup_task.ps1 deployments/musikverwaltung/rekordbox_sync/jetzt_synchronisieren.bat
git commit -m "feat: automatischer 20-Minuten-Sync + manueller Sofort-Anstoss"
```

---

## Nach Abschluss

- NOW.md um einen Radio-Abschnitt ergänzen: „Playlisten werden aus Rekordbox synchronisiert, Sendeplan bleibt in AzuraCast" — nicht Teil dieses Plans, aber direkt danach fällig (Projekt-Konvention: NOW.md ist die Live-SSOT).
- Odoo-Aufgabe für diesen Plan anlegen (Projekt-Konvention: Vorhaben gehören nach Odoo, nicht nur ins Repo).

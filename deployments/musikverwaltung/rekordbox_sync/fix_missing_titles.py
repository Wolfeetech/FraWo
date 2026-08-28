"""Repariert Rekordbox-Tracks ohne Titel/Interpret/Album/Genre, indem die
bereits korrekten Tags aus der Datei selbst neu eingelesen werden.

Betrifft ausschliesslich Tracks unter M:\\Curated_Playlists (verifiziert:
3319 von 8702 Tracks dort ohne Titel, obwohl die Dateien selbst saubere
Tags haben - reines Rekordbox-Importproblem, kein Datenverlust).

Sicherheit:
- Ohne --commit: reiner Probelauf auf einer Wegwerf-Kopie der Datenbank,
  aendert nichts an der echten Bibliothek.
- Mit --commit: schreibt in die ECHTE Rekordbox-Datenbank. Bricht sofort
  ab, wenn Rekordbox noch laeuft (WAL-Konflikt-Risiko). Legt vorher ein
  Backup von master.db(+wal/shm) an.
"""
import argparse
import os
import shutil
import sys
import tempfile
from datetime import datetime

import psutil
from mutagen import File as MutagenFile
from pyrekordbox.db6 import Rekordbox6Database

REKORDBOX_LIVE_DIR = os.path.expandvars(r"%APPDATA%\Pioneer\rekordbox")
BACKUP_DIR = os.path.expandvars(r"%APPDATA%\Pioneer\rekordbox_backups")


def rekordbox_is_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if (p.info["name"] or "").lower().startswith("rekordbox"):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def read_tags(path: str):
    if not os.path.exists(path):
        return None
    try:
        f = MutagenFile(path, easy=True)
    except Exception:
        return None
    if f is None:
        return None
    return {
        "title": (f.get("title", [None])[0] or "").strip() or None,
        "artist": (f.get("artist", [None])[0] or "").strip() or None,
        "album": (f.get("album", [None])[0] or "").strip() or None,
        "genre": (f.get("genre", [None])[0] or "").strip() or None,
    }


def get_or_create_artist(db, name):
    if not name:
        return None
    row = db.get_artist(Name=name).first()
    if row is not None:
        return row
    return db.add_artist(name)


def get_or_create_album(db, name, artist_row):
    if not name:
        return None
    row = db.get_album(Name=name).first()
    if row is not None:
        return row
    return db.add_album(name, artist=artist_row)


def get_or_create_genre(db, name):
    if not name:
        return None
    row = db.get_genre(Name=name).first()
    if row is not None:
        return row
    return db.add_genre(name)


def run(commit: bool):
    if commit and rekordbox_is_running():
        print("ABBRUCH: Rekordbox laeuft noch. Bitte schliessen und erneut mit --commit starten.")
        sys.exit(1)

    if commit:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = os.path.join(BACKUP_DIR, stamp)
        os.makedirs(dest, exist_ok=True)
        for fname in ("master.db", "master.db-wal", "master.db-shm"):
            src = os.path.join(REKORDBOX_LIVE_DIR, fname)
            if os.path.exists(src):
                shutil.copy(src, dest)
        print(f"Backup angelegt: {dest}")
        db = Rekordbox6Database(db_dir=REKORDBOX_LIVE_DIR)
        _process(db, commit=True)
    else:
        with tempfile.TemporaryDirectory(prefix="rb_fix_dryrun_") as tmp:
            for fname in ("master.db", "master.db-wal", "master.db-shm"):
                src = os.path.join(REKORDBOX_LIVE_DIR, fname)
                if os.path.exists(src):
                    shutil.copy(src, tmp)
            db = Rekordbox6Database(db_dir=tmp)
            _process(db, commit=False)


def _process(db, commit: bool):
    contents = list(db.get_content())
    targets = [
        c for c in contents
        if not (c.Title or "").strip() and "Curated_Playlists" in (c.FolderPath or "")
    ]
    print(f"Zu reparierende Tracks: {len(targets)}")

    repariert = 0
    keine_tags = 0
    datei_fehlt = 0

    for c in targets:
        path = (c.FolderPath or "")
        tags = read_tags(path)
        if tags is None:
            datei_fehlt += 1
            continue
        if not tags["title"]:
            keine_tags += 1
            continue

        c.Title = tags["title"]
        if tags["artist"]:
            artist_row = get_or_create_artist(db, tags["artist"])
            if artist_row is not None:
                c.ArtistID = artist_row.ID
        else:
            artist_row = None
        if tags["album"]:
            album_row = get_or_create_album(db, tags["album"], artist_row)
            if album_row is not None:
                c.AlbumID = album_row.ID
        if tags["genre"]:
            genre_row = get_or_create_genre(db, tags["genre"])
            if genre_row is not None:
                c.GenreID = genre_row.ID

        repariert += 1

    print(f"Erfolgreich vorbereitet: {repariert}")
    print(f"Datei ohne Titel-Tag: {keine_tags}")
    print(f"Datei nicht gefunden: {datei_fehlt}")

    if commit:
        db.commit()
        print("Gespeichert in der echten Rekordbox-Datenbank.")
    else:
        print("PROBELAUF - nichts wurde an der echten Datenbank veraendert.")
        print("Zum wirklich Anwenden: Rekordbox schliessen, dann Skript mit --commit starten.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    run(commit=args.commit)

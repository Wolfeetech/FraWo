"""Entfernt den Playlisten-Ordner "Radio (Import 2026-08-17)" (die vier
kompletten Sendekanäle) wieder aus Rekordbox. Nur die Playlisten-Eintraege
werden geloescht, keine Audiodatei auf der Platte wird angefasst oder
verschoben - Rekordbox referenziert Dateien nur, kopiert sie nie.

Sicherheit: gleiches Muster wie fix_missing_titles.py.
- Ohne --commit: zeigt nur, was geloescht wuerde (Kopie der Datenbank).
- Mit --commit: schreibt in die ECHTE Datenbank. Bricht ab, wenn Rekordbox
  noch laeuft. Legt vorher ein Backup von master.db(+wal/shm) an.
"""
import argparse
import os
import shutil
import sys
import tempfile
from datetime import datetime

import psutil
from pyrekordbox.db6 import Rekordbox6Database

REKORDBOX_LIVE_DIR = os.path.expandvars(r"%APPDATA%\Pioneer\rekordbox")
BACKUP_DIR = os.path.expandvars(r"%APPDATA%\Pioneer\rekordbox_backups")
FOLDER_NAME = "Radio (Import 2026-08-17)"


def rekordbox_is_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if (p.info["name"] or "").lower().startswith("rekordbox"):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def _report(db):
    folder = db.get_playlist(Name=FOLDER_NAME).first()
    if folder is None:
        print(f"Ordner '{FOLDER_NAME}' nicht gefunden - nichts zu tun.")
        return None
    children = list(folder.Children)
    total = 0
    for child in children:
        try:
            n = len(list(child.Songs))
        except Exception:
            n = 0
        total += n
        print(f"  '{child.Name}': {n} Playlist-Eintraege")
    print(f"Ordner '{folder.Name}' + {len(children)} Playlisten, zusammen {total} Eintraege werden geloescht.")
    print("Betroffen sind nur die Playlisten-Zuordnungen in Rekordbox - keine Datei auf M:\\ wird veraendert.")
    return folder


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
        folder = _report(db)
        if folder is None:
            return
        db.delete_playlist(folder)
        db.commit()
        print("Geloescht und gespeichert.")
    else:
        with tempfile.TemporaryDirectory(prefix="rb_remove_dryrun_") as tmp:
            for fname in ("master.db", "master.db-wal", "master.db-shm"):
                src = os.path.join(REKORDBOX_LIVE_DIR, fname)
                if os.path.exists(src):
                    shutil.copy(src, tmp)
            db = Rekordbox6Database(db_dir=tmp)
            _report(db)
        print("PROBELAUF - nichts wurde an der echten Datenbank veraendert.")
        print("Zum wirklich Anwenden: Rekordbox schliessen, dann Skript mit --commit starten.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    run(commit=args.commit)

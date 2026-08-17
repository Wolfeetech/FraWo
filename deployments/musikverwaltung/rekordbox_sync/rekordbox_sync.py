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
            if playlist.is_folder:
                continue
            songs = db.get_playlist_contents(playlist)
            paths = [s.FolderPath.replace("/", "\\") for s in songs if s.FolderPath]
            if paths:
                result[playlist.Name] = paths
        return result


if __name__ == "__main__":
    for name, tracks in read_rekordbox_playlists().items():
        print(f"{name}: {len(tracks)} Titel")

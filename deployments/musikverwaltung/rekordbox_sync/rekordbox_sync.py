"""Liest Rekordbox-Playlisten sicher aus einer Kopie der Datenbank und
synchronisiert sie nach AzuraCast."""
import os
import shutil
import tempfile

import requests
from dotenv import load_dotenv
from pyrekordbox.db6 import Rekordbox6Database

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

REKORDBOX_LIVE_DIR = os.path.expandvars(r"%APPDATA%\Pioneer\rekordbox")

# Bestaetigte Regel (siehe README.md): M:\ ist direkt die Wurzel,
# kein Master_Library-Praefix.
REKORDBOX_ROOT = "M:\\"

BASE_URL = os.environ["AZURACAST_BASE_URL"]
STATION_ID = os.environ["AZURACAST_STATION_ID"]
API_KEY = os.environ["AZURACAST_API_KEY"]
HEADERS = {"X-API-Key": API_KEY}


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


def rekordbox_path_to_azuracast(rb_path: str) -> str:
    """M:\\...-Pfad -> AzuraCast-relativer Pfad (siehe README.md)."""
    if rb_path.upper().startswith(REKORDBOX_ROOT.upper()):
        rel = rb_path[len(REKORDBOX_ROOT):]
    else:
        rel = rb_path
    return rel.replace("\\", "/").lstrip("/")


def _get_or_create_playlist_id(name: str) -> int:
    resp = requests.get(
        f"{BASE_URL}/api/station/{STATION_ID}/playlists",
        headers=HEADERS, verify=False, timeout=30,
    )
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
    """Playlistname -> M:\\...-Pfade nach AzuraCast schreiben, Ergebnis gegenpruefen."""
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

        check = requests.get(
            f"{BASE_URL}/api/station/{STATION_ID}/playlist/{playlist_id}",
            headers=HEADERS, verify=False, timeout=30,
        )
        check.raise_for_status()
        bestaetigt = check.json().get("num_songs", 0)

        results[name] = {"gesendet": len(az_paths), "bestaetigt": bestaetigt}
    return results


if __name__ == "__main__":
    for name, tracks in read_rekordbox_playlists().items():
        print(f"{name}: {len(tracks)} Titel")

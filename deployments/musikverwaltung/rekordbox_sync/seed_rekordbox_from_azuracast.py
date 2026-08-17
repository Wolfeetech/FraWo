"""
Einmaliges Bootstrap: liest die aktuell in AzuraCast aktiven Playlisten
und legt sie mit ihren Titeln in Rekordbox an. Vor dem Lauf muss
Rekordbox (rekordbox.exe UND rekordboxAgent.exe) geschlossen sein.

Pfad-Regel (bestaetigt 2026-08-17, siehe README.md):
  rekordbox_pfad = "M:\\" + azuracast_pfad.replace("/", "\\")

Workaround (siehe README.md): /api/station/{id}/files liefert HTTP 500.
Stattdessen je Playlist die Warteschlange lesen und pro Titel den Pfad
einzeln nachschlagen.
"""
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3
from dotenv import load_dotenv
from pyrekordbox.db6 import Rekordbox6Database

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

BASE_URL = os.environ["AZURACAST_BASE_URL"]
STATION_ID = os.environ["AZURACAST_STATION_ID"]
API_KEY = os.environ["AZURACAST_API_KEY"]
HEADERS = {"X-API-Key": API_KEY}

REKORDBOX_ROOT = "M:\\"  # ein Backslash - bewusst kein Raw-String (r"M:\\" waere zwei)
FOLDER_NAME = "Radio (Import 2026-08-17)"


def azuracast_path_to_rekordbox(az_path: str) -> str:
    return REKORDBOX_ROOT + az_path.replace("/", "\\")


def fetch_playlists():
    resp = requests.get(f"{BASE_URL}/api/station/{STATION_ID}/playlists", headers=HEADERS, verify=False, timeout=30)
    resp.raise_for_status()
    return [p for p in resp.json() if p.get("is_enabled") and p.get("num_songs", 0) > 0]


def fetch_playlist_media_ids(playlist_id: int) -> list[int]:
    resp = requests.get(f"{BASE_URL}/api/station/{STATION_ID}/playlist/{playlist_id}/queue", headers=HEADERS, verify=False, timeout=60)
    resp.raise_for_status()
    return [item["media_id"] for item in resp.json()]


def fetch_file_path(media_id: int) -> tuple[int, str | None]:
    resp = requests.get(f"{BASE_URL}/api/station/{STATION_ID}/file/{media_id}", headers=HEADERS, verify=False, timeout=30)
    if resp.status_code != 200:
        return media_id, None
    return media_id, resp.json().get("path")


def main():
    playlists = fetch_playlists()
    if not playlists:
        print("Keine aktiven AzuraCast-Playlisten mit Titeln gefunden - abgebrochen.")
        sys.exit(1)

    print(f"{len(playlists)} aktive Playlisten gefunden, hole Titel-Zuordnung...")

    playlist_media_ids: dict[str, list[int]] = {}
    all_media_ids: set[int] = set()
    for pl in playlists:
        ids = fetch_playlist_media_ids(pl["id"])
        playlist_media_ids[pl["name"]] = ids
        all_media_ids.update(ids)

    print(f"{len(all_media_ids)} eindeutige Titel insgesamt, loese Pfade parallel auf...")

    path_cache: dict[int, str | None] = {}
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [pool.submit(fetch_file_path, mid) for mid in all_media_ids]
        done = 0
        for fut in as_completed(futures):
            mid, path = fut.result()
            path_cache[mid] = path
            done += 1
            if done % 500 == 0:
                print(f"  ... {done}/{len(all_media_ids)} Pfade aufgeloest")

    by_playlist: dict[str, list[str]] = defaultdict(list)
    for name, media_ids in playlist_media_ids.items():
        for mid in media_ids:
            path = path_cache.get(mid)
            if path:
                by_playlist[name].append(azuracast_path_to_rekordbox(path))
        print(f"  {name}: {len(media_ids)} Titel in AzuraCast, {len(by_playlist[name])} Pfade aufgeloest")

    db = Rekordbox6Database()
    folder = db.create_playlist_folder(FOLDER_NAME)

    # Pfad -> Content-Objekt, einmal aufbauen statt pro Titel neu zu suchen
    path_to_content = {c.FolderPath: c for c in db.get_content() if c.FolderPath}

    print("\nLege Playlisten in Rekordbox an...")
    for name, paths in by_playlist.items():
        pl = db.create_playlist(name, parent=folder)
        added, neu_registriert, missing = 0, 0, 0
        for p in paths:
            key = p.replace("\\", "/")
            content = path_to_content.get(key)
            if content is None:
                if os.path.exists(p):
                    content = db.add_content(p)
                    path_to_content[key] = content
                    neu_registriert += 1
                else:
                    missing += 1
                    continue
            db.add_to_playlist(pl, content)
            added += 1
        print(f"  {name}: {added} Titel uebernommen (davon {neu_registriert} neu in Rekordbox registriert), {missing} Datei fehlt auf der Platte")

    db.commit()
    print(f"\nFertig. Rekordbox jetzt wieder oeffnen und Ordner '{FOLDER_NAME}' pruefen.")


if __name__ == "__main__":
    main()

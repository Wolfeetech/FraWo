"""Stündlicher Export der Publikums-Sterne aus Odoo nach Rekordbox.

Läuft auf dem StudioPC (Windows-Aufgabenplanung). Schreibt NUR, wenn
Rekordbox geschlossen ist (siehe README: Schreiben bei geöffnetem
Rekordbox ist unsicher). Abgleich Titel -> Rekordbox über Title + Artist.Name,
kein AzuraCast-Umweg. Nicht auffindbare Titel werden protokolliert, nie geraten.
"""
import os
import subprocess
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

ODOO_BASE = os.environ.get("FRAWO_ODOO_URL", "https://frawo.tech").rstrip("/")
TOKEN = os.environ.get("FRAWO_AGENT_TOKEN", "")
PROCESS_NAMES = ["rekordbox.exe", "rekordboxAgent.exe"]
FAVORITES_NAME = "🔥 Publikums-Favoriten"
MIN_STARS_FAVORITE = 4


def log(msg):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def rekordbox_running(process_names, tasklist_output=None):
    if tasklist_output is None:
        tasklist_output = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
    low = tasklist_output.lower()
    return any(name.lower() in low for name in process_names)


def fetch_rows():
    r = requests.get(f"{ODOO_BASE}/radio/ratings/export",
                     headers={"X-Agent-Token": TOKEN}, timeout=20)
    r.raise_for_status()
    return r.json()


def _norm(s):
    return (s or "").strip().lower()


def match_content(rows, contents):
    from collections import defaultdict
    index = defaultdict(list)
    for c in contents:
        artist = _norm(getattr(getattr(c, "Artist", None), "Name", ""))
        index[(artist, _norm(getattr(c, "Title", "")))].append(c)
    matches, unmatched = [], []
    for row in rows:
        c_list = index.get((_norm(row.get("artist")), _norm(row.get("title"))))
        if not c_list:
            unmatched.append(row)
        else:
            for c in c_list:
                matches.append((row, c))
    return matches, unmatched


def apply_ratings(db, matches):
    changed = 0
    for row, content in matches:
        target = int(row["stars"])
        if int(getattr(content, "Rating", 0) or 0) != target:
            content.Rating = target
            changed += 1
    return changed


def ensure_favorites_playlist(db, matches, min_stars=MIN_STARS_FAVORITE):
    wanted = [c for row, c in matches if int(row["stars"]) >= min_stars]
    existing = None
    for pl in db.get_playlist():
        if pl.Name == FAVORITES_NAME:
            existing = pl
            break
    if existing is None:
        existing = db.create_playlist(FAVORITES_NAME)
    present = {getattr(sp, "ID", getattr(sp, "ContentID", None)) for sp in db.get_playlist_contents(existing)} if hasattr(db, "get_playlist_contents") else set()
    added = 0
    for c in wanted:
        if c.ID not in present:
            db.add_to_playlist(existing, c)
            added += 1
    return added


def main():
    if not TOKEN:
        log("FRAWO_AGENT_TOKEN fehlt in .env - Abbruch")
        return 2
    if rekordbox_running(PROCESS_NAMES):
        log("Rekordbox läuft - Lauf übersprungen, nächster Versuch in einer Stunde")
        return 0
    rows = fetch_rows()
    log(f"{len(rows)} Titel mit mindestens 2 Bewertungen aus Odoo geholt")
    from pyrekordbox.db6 import Rekordbox6Database
    db = Rekordbox6Database()
    contents = list(db.get_content())
    matches, unmatched = match_content(rows, contents)
    changed = apply_ratings(db, matches)
    added = ensure_favorites_playlist(db, matches)
    db.commit()
    log(f"Rating gesetzt/aktualisiert: {changed} | in Favoriten neu: {added} | nicht gefunden: {len(unmatched)}")
    for row in unmatched:
        log(f"  nicht in Rekordbox: {row['track_id']}")
    log(f"Rückprobe: {len(matches)} Matches in Rekordbox verarbeitet, {len(unmatched)} Titel ohne Treffer")
    return 0


if __name__ == "__main__":
    sys.exit(main())

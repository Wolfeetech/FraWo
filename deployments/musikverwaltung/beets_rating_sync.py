"""Synchronisiert Hörer-Bewertungen aus Odoo in die Beets-Mediathek (CT120).

Liest /radio/ratings/export aus Odoo ab und setzt auf CT120 über SSH
die flexiblen Metadaten-Attribute `crowd_rating` und `votes_count`.
"""
import os
import subprocess
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "rekordbox_sync", ".env"))
if not os.environ.get("FRAWO_AGENT_TOKEN"):
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

ODOO_BASE = os.environ.get("FRAWO_ODOO_URL", "https://frawo.tech").rstrip("/")
TOKEN = os.environ.get("FRAWO_AGENT_TOKEN", "")
PRODESK_HOST = "10.1.0.128"
CT120_ID = "120"


def log(msg):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def fetch_rows():
    r = requests.get(f"{ODOO_BASE}/radio/ratings/export",
                     headers={"X-Agent-Token": TOKEN}, timeout=20)
    r.raise_for_status()
    return r.json()


def sync_to_beets(rows):
    import re, shlex
    if not rows:
        log("Keine bewerteten Tracks zum Synchronisieren vorhanden.")
        return 0

    log(f"Synchronisiere {len(rows)} Titel nach Beets (CT120)...")
    updated = 0
    for row in rows:
        artist = row.get("artist", "").strip()
        title = row.get("title", "").strip()
        stars = int(row.get("stars", 0))
        count = int(row.get("count", 0))

        arg_artist = shlex.quote(f"artist:{artist}")
        arg_title = shlex.quote(f"title:{title}")

        cmd = [
            "ssh", "-o", "BatchMode=yes", f"root@{PRODESK_HOST}",
            f"pct exec {CT120_ID} -- beet modify -y -M -W {arg_artist} {arg_title} crowd_rating={stars} votes_count={count}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if res.returncode == 0 and "Modifying" in res.stdout:
            log(f"  [OK] {row.get('track_id')} -> crowd_rating={stars}, votes_count={count}")
            updated += 1
            continue

        # Fallback to regex query for typographical apostrophes or punctuation variations
        artist_regex = re.escape(artist).replace("'", "['’]")
        title_regex = re.escape(title).replace("'", "['’]")
        arg_artist_rx = shlex.quote(f"artist::{artist_regex}")
        arg_title_rx = shlex.quote(f"title::{title_regex}")
        cmd_rx = [
            "ssh", "-o", "BatchMode=yes", f"root@{PRODESK_HOST}",
            f"pct exec {CT120_ID} -- beet modify -y -M -W {arg_artist_rx} {arg_title_rx} crowd_rating={stars} votes_count={count}"
        ]
        res_rx = subprocess.run(cmd_rx, capture_output=True, text=True, encoding="utf-8")
        if res_rx.returncode == 0 and "Modifying" in res_rx.stdout:
            log(f"  [OK (Regex)] {row.get('track_id')} -> crowd_rating={stars}, votes_count={count}")
            updated += 1
        elif res.returncode == 0:
            # Query succeeded but 0 items matched
            log(f"  [NICHT GEFUNDEN] {row.get('track_id')}: Keine passende Datei in Beets gefunden")
        else:
            err = (res_rx.stderr or res.stderr).strip()
            log(f"  [FEHLER] {row.get('track_id')}: {err}")

    return updated


def main():
    if not TOKEN:
        log("FRAWO_AGENT_TOKEN fehlt in .env - Abbruch")
        return 2

    rows = fetch_rows()
    count = sync_to_beets(rows)
    log(f"Beets-Sync abgeschlossen: {count}/{len(rows)} Titel aktualisiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

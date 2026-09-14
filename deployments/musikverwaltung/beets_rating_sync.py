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
    if not rows:
        log("Keine bewerteten Tracks zum Synchronisieren vorhanden.")
        return 0

    log(f"Synchronisiere {len(rows)} Titel nach Beets (CT120)...")
    updated = 0
    for row in rows:
        artist = row.get("artist", "").replace("'", "\\'")
        title = row.get("title", "").replace("'", "\\'")
        stars = int(row.get("stars", 0))
        count = int(row.get("count", 0))

        cmd = [
            "ssh", "-o", "BatchMode=yes", f"root@{PRODESK_HOST}",
            f"pct exec {CT120_ID} -- beet modify -y 'artist:{artist}' 'title:{title}' crowd_rating={stars} votes_count={count}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if res.returncode == 0:
            log(f"  [OK] {row.get('track_id')} -> crowd_rating={stars}, votes_count={count}")
            updated += 1
        else:
            log(f"  [FEHLER] {row.get('track_id')}: {res.stderr.strip()}")

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

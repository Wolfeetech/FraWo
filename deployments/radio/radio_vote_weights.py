"""
FraWo Funk - Dynamic Track Rotation from Listener Votes & Ratings

Fetches ratings (frawo.radio.rating) and votes (frawo.radio.vote) from Odoo
and updates track weights and queue status in AzuraCast station_playlist_media:
- 5 Stars / High Likes (Tier 1: Power Rotation):
    weight = 1, is_queued = 1 (plays at the very head of the queue)
- 4 Stars / Likes (Tier 2: Elevated Rotation):
    weight = 25, is_queued = 1 (elevated priority)
- Neutral / Unrated (Tier 3: Standard Rotation):
    weight = 100, is_queued = 1
- <= 2 Stars / High Skips (Tier 4: Suppressed / Quarantined):
    weight = 9999, is_queued = 0 (completely suppressed from AutoDJ)
"""
import logging
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "musikverwaltung", "rekordbox_sync", ".env"))
if not os.environ.get("FRAWO_AGENT_TOKEN"):
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

ODOO_BASE = os.environ.get("FRAWO_ODOO_URL", "https://frawo.tech").rstrip("/")
TOKEN = os.environ.get("FRAWO_AGENT_TOKEN", "")
AZURACAST_HOST = "10.1.0.38"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("radio_vote_weights")


def calculate_rotation_tier(
    stars: Optional[float], count: int = 0, likes: int = 0, hates: int = 0
) -> Tuple[int, int, str]:
    """
    Calculates (weight, is_queued, tier_name) for AzuraCast AutoDJ.

    In AzuraCast QueueBuilder, order is determined by:
    `WHERE spm.is_queued = 1 ORDER BY spm.weight ASC`.
    - is_queued = 0 prevents the track from playing altogether.
    - weight = 1 guarantees top queue priority.
    """
    if hates >= 3 or (stars is not None and stars <= 2.2):
        return 9999, 0, "Quarantined"

    if (stars is not None and stars >= 4.5) or (likes >= 3 and hates == 0):
        return 1, 1, "Power Rotation"

    if (stars is not None and stars >= 3.8) or (likes >= 1 and hates == 0):
        return 25, 1, "Elevated Rotation"

    return 100, 1, "Standard Rotation"


def fetch_ratings(odoo_url: str = ODOO_BASE, token: str = TOKEN, min_count: int = 1) -> List[dict]:
    """Fetches rated and voted tracks from Odoo rating export endpoint."""
    url = f"{odoo_url}/radio/ratings/export?min_count={min_count}"
    resp = requests.get(url, headers={"X-Agent-Token": token}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def build_weight_updates(rows: List[dict]) -> List[dict]:
    """Transforms Odoo rows into target track weight and queue objects."""
    updates = []
    for r in rows:
        stars = r.get("stars")
        avg = r.get("average")
        count = r.get("count", 1)
        likes = r.get("likes", 0)
        hates = r.get("hates", 0)

        score_val = avg if avg is not None else stars
        weight, is_queued, tier = calculate_rotation_tier(score_val, count=count, likes=likes, hates=hates)

        updates.append({
            "track_id": r.get("track_id", ""),
            "artist": r.get("artist", "").strip(),
            "title": r.get("title", "").strip(),
            "weight": weight,
            "is_queued": is_queued,
            "tier": tier,
            "stars": score_val,
            "count": count,
            "likes": likes,
            "hates": hates,
        })
    return updates


def apply_weights_to_azuracast(updates: List[dict]) -> int:
    """Updates station_playlist_media weight and is_queued in AzuraCast via SSH."""
    if not updates:
        log.info("No track rotation updates to apply.")
        return 0

    sql_statements = []
    for u in updates:
        art = u["artist"].replace("'", "\\'")
        tit = u["title"].replace("'", "\\'")
        w = int(u["weight"])
        q = int(u["is_queued"])
        sql_statements.append(
            f"UPDATE station_playlist_media spm JOIN station_media sm ON spm.media_id = sm.id "
            f"SET spm.weight = {w}, spm.is_queued = {q} WHERE sm.artist = '{art}' AND sm.title = '{tit}';"
        )

    full_sql = "\n".join(sql_statements)
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
        f"wolfadmin@{AZURACAST_HOST}",
        "sudo docker exec -i azuracast bash -c 'mariadb -u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\"'"
    ]
    res = subprocess.run(cmd, input=full_sql, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode == 0:
        log.info("Successfully updated AutoDJ rotation for %d tracks in AzuraCast.", len(updates))
        return len(updates)
    else:
        log.error("Failed to update AzuraCast weights: %s", res.stderr)
        return 0


def main():
    log.info("Fetching listener ratings from Odoo (%s)...", ODOO_BASE)
    try:
        rows = fetch_ratings()
    except Exception as e:
        log.error("Error fetching ratings from Odoo: %s", e)
        sys.exit(1)

    log.info("Received %d rated/voted tracks from Odoo.", len(rows))
    updates = build_weight_updates(rows)
    for u in updates:
        log.info("  Track: %s - %s | Stars: %s (%d votes) | Likes: %d, Skips: %d -> %s (weight=%d, is_queued=%d)",
                 u['artist'], u['title'], u['stars'], u['count'], u['likes'], u['hates'],
                 u['tier'], u['weight'], u['is_queued'])

    updated = apply_weights_to_azuracast(updates)
    log.info("Done. %d tracks updated in AzuraCast AutoDJ.", updated)


if __name__ == "__main__":
    main()

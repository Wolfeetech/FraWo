"""
FraWo Funk - Dynamic Track Rotation from Listener Votes & Ratings

Fetches ratings (frawo.radio.rating) and votes (frawo.radio.vote) from Odoo
and synchronizes track rotation in AzuraCast:
1. Power Rotation (Playlist 871: '🔥 FraWo Funk — Power Rotation (Hörer-Favoriten)'):
   - Type: once_per_x_songs, play_per_songs = 6 (plays every 6 tracks 24/7 across all shows)
   - Populated with tracks having >= 4.5 stars or >= 3 net likes
2. Quarantining:
   - Tracks with <= 2.2 stars or >= 3 skips/hates are removed from all playlists
     and suppressed (is_queued = 0)
3. Standard/Elevated Rotation:
   - Maintained in curated daypart show playlists
"""
import logging
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

# Try several locations for environment variables
_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(_DIR, "..", "musikverwaltung", "rekordbox_sync", ".env"))
load_dotenv(os.path.join(_DIR, "..", "..", ".env"))

ODOO_BASE = os.environ.get("FRAWO_ODOO_URL", "https://frawo.tech").rstrip("/")
TOKEN = os.environ.get("FRAWO_AGENT_TOKEN") or os.environ.get("ODOO_EXPORT_TOKEN") or ""

if not TOKEN and os.path.exists("/etc/frawo/odoo.env"):
    try:
        with open("/etc/frawo/odoo.env", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k in ("ODOO_EXPORT_TOKEN", "FRAWO_AGENT_TOKEN"):
                        TOKEN = v
                        break
    except Exception:
        pass

AZURACAST_HOST = os.environ.get("AZURACAST_HOST", "10.1.0.38")
POWER_PLAYLIST_ID = 871
POWER_PLAYLIST_NAME = "🔥 FraWo Funk — Power Rotation (Hörer-Favoriten)"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("radio_vote_weights")


def calculate_rotation_tier(
    stars: Optional[float], count: int = 0, likes: int = 0, hates: int = 0
) -> Tuple[int, int, str]:
    """
    Calculates (weight, is_queued, tier_name) for AzuraCast AutoDJ.

    In AzuraCast:
    - is_queued = 0 prevents the track from playing altogether.
    - Tier "Power Rotation" tracks are injected every 6 tracks via Playlist 871 (once_per_x_songs).
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


def execute_mariadb_query(sql: str, host: str = AZURACAST_HOST) -> Tuple[int, str, str]:
    """Executes SQL statements inside AzuraCast MariaDB via SSH."""
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
        f"wolfadmin@{host}",
        "sudo docker exec -i azuracast bash -c 'mariadb -u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\"'"
    ]
    res = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.returncode, res.stdout, res.stderr


def ensure_power_rotation_playlist() -> int:
    """Ensures that the Power Rotation playlist (871) exists in station_playlists."""
    sql = f"""
    INSERT INTO station_playlists (
        id, station_id, name, description, type, is_enabled,
        play_per_songs, play_per_minutes, weight, source,
        include_in_requests, playback_order, remote_url, remote_type,
        is_jingle, play_per_hour_minute, remote_timeout, backend_options,
        include_in_on_demand, avoid_duplicates
    ) VALUES (
        {POWER_PLAYLIST_ID}, 1, '{POWER_PLAYLIST_NAME}',
        'Hörer-Favoriten und 5-Sterne-Titel alle 6 Songs in der Rotation',
        'once_per_x_songs', 1,
        6, 0, 3, 'songs',
        1, 'shuffle', NULL, NULL,
        0, 0, 0, NULL,
        0, 1
    ) ON DUPLICATE KEY UPDATE 
        name = VALUES(name),
        type = VALUES(type),
        is_enabled = VALUES(is_enabled),
        play_per_songs = VALUES(play_per_songs);
    """
    code, _, err = execute_mariadb_query(sql)
    if code != 0:
        log.error("Failed to ensure power rotation playlist: %s", err)
    return POWER_PLAYLIST_ID


def resolve_media_ids(tracks: List[dict]) -> List[Tuple[dict, int]]:
    """Resolves station_media IDs for given track dicts."""
    if not tracks:
        return []
    sql = "SELECT id, artist, title, path FROM station_media;"
    code, out, err = execute_mariadb_query(sql)
    if code != 0:
        log.error("Failed to query station_media: %s", err)
        return []

    media_rows = []
    for line in out.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 4 and parts[0].isdigit():
            media_rows.append({
                "id": int(parts[0]),
                "artist": parts[1].strip().lower(),
                "title": parts[2].strip().lower(),
                "path": parts[3].strip()
            })

    resolved = []
    for t in tracks:
        target_art = t.get("artist", "").strip().lower()
        target_tit = t.get("title", "").strip().lower()
        matched_id = None
        for m in media_rows:
            if m["artist"] == target_art and m["title"] == target_tit:
                matched_id = m["id"]
                break
        if not matched_id and target_tit:
            for m in media_rows:
                if target_tit in m["title"] and (not target_art or target_art in m["artist"]):
                    matched_id = m["id"]
                    break
        if not matched_id and target_tit:
            for m in media_rows:
                if target_tit in m["path"].lower():
                    matched_id = m["id"]
                    break
        if matched_id:
            resolved.append((t, matched_id))
    return resolved


def sync_power_rotation_playlist(power_media_ids: List[int]) -> int:
    """Updates station_playlist_media for playlist 871 atomically."""
    stmts = [
        "START TRANSACTION;",
        f"DELETE FROM station_playlist_media WHERE playlist_id = {POWER_PLAYLIST_ID};"
    ]
    for rank, m_id in enumerate(power_media_ids, start=1):
        stmts.append(
            f"INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued) "
            f"VALUES ({POWER_PLAYLIST_ID}, {m_id}, {rank}, 0, 1);"
        )
    stmts.append("COMMIT;")
    full_sql = "\n".join(stmts)
    code, _, err = execute_mariadb_query(full_sql)
    if code == 0:
        log.info("Successfully updated Power Rotation playlist (%d tracks).", len(power_media_ids))
        return len(power_media_ids)
    else:
        log.error("Failed to sync Power Rotation playlist: %s", err)
        return 0


def quarantine_suppressed_tracks(quarantined_media_ids: List[int]) -> int:
    """Removes quarantined tracks from all active playlists and sets is_queued=0."""
    if not quarantined_media_ids:
        return 0
    ids_str = ",".join(str(i) for i in quarantined_media_ids)
    sql = f"""
    START TRANSACTION;
    DELETE FROM station_playlist_media WHERE media_id IN ({ids_str});
    UPDATE station_playlist_media SET is_queued = 0 WHERE media_id IN ({ids_str});
    COMMIT;
    """
    code, _, err = execute_mariadb_query(sql)
    if code == 0:
        log.info("Quarantined %d tracks from AutoDJ rotation.", len(quarantined_media_ids))
        return len(quarantined_media_ids)
    else:
        log.error("Failed to quarantine tracks: %s", err)
        return 0


def apply_weights_to_azuracast(updates: List[dict]) -> int:
    """
    Full AzuraCast rotation sync:
    1. Ensures Power Rotation playlist (871) exists.
    2. Populates playlist 871 with all Power Rotation tracks (>=4.5 stars).
    3. Quarantines suppressed tracks (<=2.2 stars / >=3 hates) from all playlists.
    4. Updates individual station_playlist_media attributes for backward compatibility.
    """
    if not updates:
        log.info("No track rotation updates to apply.")
        return 0

    ensure_power_rotation_playlist()

    power_tracks = [u for u in updates if u.get("tier") == "Power Rotation"]
    quarantined_tracks = [u for u in updates if u.get("tier") == "Quarantined"]

    resolved_power = resolve_media_ids(power_tracks)
    power_media_ids = [m_id for _, m_id in resolved_power]
    sync_power_rotation_playlist(power_media_ids)

    resolved_quarantine = resolve_media_ids(quarantined_tracks)
    quarantine_media_ids = [m_id for _, m_id in resolved_quarantine]
    if quarantine_media_ids:
        quarantine_suppressed_tracks(quarantine_media_ids)

    # Standard per-track updates for backward compatibility
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
    code, _, err = execute_mariadb_query(full_sql)
    if code == 0:
        log.info("Successfully updated AutoDJ rotation attributes for %d tracks in AzuraCast.", len(updates))
        return len(updates)
    else:
        log.error("Failed to update AzuraCast weights: %s", err)
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

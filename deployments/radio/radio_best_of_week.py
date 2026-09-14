"""
FraWo Funk - Best of the Week / Hörer-Charts Engine

Generates and synchronizes the weekly listener charts playlist in AzuraCast:
1. Fetches listener votes and star ratings from Odoo (radio.rating export endpoint).
2. Calculates chart score based on average stars, total votes, and net likes.
3. Resolves media IDs in AzuraCast station_media.
4. Updates playlist 869 ('⭐ Best of the Week') with ranked tracks (sequential playback order).
5. Ensures Sunday prime-time schedule (18:00 - 20:00 Uhr) in station_schedules.
"""
import logging
import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

# Load credentials from Rekordbox sync or FraWo root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "musikverwaltung", "rekordbox_sync", ".env"))
if not os.environ.get("FRAWO_AGENT_TOKEN"):
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

ODOO_BASE = os.environ.get("FRAWO_ODOO_URL", "https://frawo.tech").rstrip("/")
TOKEN = os.environ.get("FRAWO_AGENT_TOKEN", "")
AZURACAST_HOST = "10.1.0.38"
PLAYLIST_NAME = "⭐ Best of the Week"
DEFAULT_PLAYLIST_ID = 869

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("radio_best_of_week")


def calculate_chart_score(r: dict) -> float:
    """
    Computes a weighted chart score from star ratings and likes/hates.
    Returns negative score for quarantined/disliked tracks.
    """
    avg = r.get("average") if r.get("average") is not None else r.get("stars", 0.0)
    count = r.get("count", 0)
    likes = r.get("likes", 0)
    hates = r.get("hates", 0)

    # Disqualified if disliked or rating <= 2.2
    if hates >= 2 and hates > likes:
        return -999.0
    if avg is not None and avg <= 2.2 and count > 0:
        return -999.0

    base_score = float(avg) if avg else 3.0
    net_votes = float(likes - hates)
    volume_bonus = min(float(count) * 0.2, 1.0)

    # Blend: Base rating (1-5) + net positive reactions bonus + vote count confidence bonus
    return round(base_score + (net_votes * 0.5) + volume_bonus, 3)


def rank_tracks_for_charts(rows: List[dict], min_score: float = 3.5, max_tracks: int = 25) -> List[dict]:
    """
    Filters and ranks tracks by chart score in descending order.
    """
    candidates = []
    for r in rows:
        score = calculate_chart_score(r)
        if score >= min_score:
            item = dict(r)
            item["chart_score"] = score
            candidates.append(item)

    # Sort primarily by chart score DESC, then vote count DESC, then likes DESC
    candidates.sort(key=lambda x: (x["chart_score"], x.get("count", 0), x.get("likes", 0)), reverse=True)
    return candidates[:max_tracks]


def fetch_ratings(odoo_url: str = ODOO_BASE, token: str = TOKEN, min_count: int = 1) -> List[dict]:
    """Fetches rated and voted tracks from Odoo rating export endpoint."""
    url = f"{odoo_url}/radio/ratings/export?min_count={min_count}"
    resp = requests.get(url, headers={"X-Agent-Token": token}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def execute_mariadb_query(sql: str, host: str = AZURACAST_HOST) -> Tuple[int, str, str]:
    """Executes SQL statements inside AzuraCast MariaDB via SSH."""
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
        f"wolfadmin@{host}",
        "sudo docker exec -i azuracast bash -c 'mariadb -u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\"'"
    ]
    res = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.returncode, res.stdout, res.stderr


def ensure_playlist_id() -> int:
    """Returns the playlist ID for '⭐ Best of the Week'."""
    sql = "SELECT id FROM station_playlists WHERE station_id = 1 AND name LIKE '%Best of the Week%' LIMIT 1;"
    code, out, _ = execute_mariadb_query(sql)
    if code == 0 and out.strip():
        lines = [line.strip() for line in out.strip().splitlines() if line.strip().isdigit()]
        if lines:
            return int(lines[0])
    return DEFAULT_PLAYLIST_ID


def resolve_station_media(tracks: List[dict]) -> List[Tuple[dict, int]]:
    """
    Resolves AzuraCast media IDs for each ranked chart track.
    """
    if not tracks:
        return []

    # Fetch all station media to match in memory for robustness
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

        # 1. Exact match artist + title
        for m in media_rows:
            if m["artist"] == target_art and m["title"] == target_tit:
                matched_id = m["id"]
                break

        # 2. Substring or relaxed match if exact not found
        if not matched_id and target_tit:
            for m in media_rows:
                if target_tit in m["title"] and (not target_art or target_art in m["artist"]):
                    matched_id = m["id"]
                    break

        # 3. Match against file path
        if not matched_id and target_tit:
            for m in media_rows:
                if target_tit in m["path"].lower():
                    matched_id = m["id"]
                    break

        if matched_id:
            resolved.append((t, matched_id))
        else:
            log.warning("Could not match chart track in station_media: '%s' - '%s'", t.get("artist"), t.get("title"))

    return resolved


def build_playlist_sync_sql(playlist_id: int, resolved_tracks: List[Tuple[dict, int]]) -> str:
    """
    Builds atomic SQL transaction to replace playlist media in rank order.
    """
    stmts = [
        "START TRANSACTION;",
        f"DELETE FROM station_playlist_media WHERE playlist_id = {playlist_id};"
    ]
    for rank, (track, media_id) in enumerate(resolved_tracks, start=1):
        stmts.append(
            f"INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued) "
            f"VALUES ({playlist_id}, {media_id}, {rank}, 0, 1);"
        )
    stmts.append("COMMIT;")
    return "\n".join(stmts)


def build_schedule_sync_sql(playlist_id: int) -> str:
    """
    Generates SQL to ensure Sunday 18:00 - 20:00 schedule slot for Best of the Week,
    and moves Sunday Evening Warmup to 20:00 - 21:30.
    """
    return f"""
START TRANSACTION;
-- Backup existing schedules if not already backed up
CREATE TABLE IF NOT EXISTS station_schedules_bak_20260915_bestof AS SELECT * FROM station_schedules;

-- 1. Ensure Best of the Week schedule on Sunday (day 7: 18:00 - 20:00)
DELETE FROM station_schedules WHERE playlist_id = {playlist_id} AND days = '7';
INSERT INTO station_schedules (playlist_id, start_time, end_time, start_date, end_date, days, loop_once)
VALUES ({playlist_id}, 1800, 2000, NULL, NULL, '7', 0);

-- 2. Adjust Sunday Evening Warmup (playlist 863) from 1800 to 2000 (ends 2130)
UPDATE station_schedules 
SET start_time = 2000, end_time = 2130 
WHERE playlist_id = 863 AND days = '7';

COMMIT;
"""


def main():
    log.info("Starting FraWo Funk Best-of-the-Week Charts Sync...")
    try:
        ratings = fetch_ratings()
    except Exception as e:
        log.error("Failed to fetch ratings from Odoo: %s", e)
        sys.exit(1)

    log.info("Fetched %d rated tracks from Odoo.", len(ratings))
    chart_tracks = rank_tracks_for_charts(ratings, min_score=3.5, max_tracks=25)
    log.info("Identified %d qualifying chart tracks (min score >= 3.5):", len(chart_tracks))
    for idx, t in enumerate(chart_tracks, start=1):
        log.info("  #%02d | Score: %.2f | Stars: %s (%d votes) | Likes: %d, Skips: %d | %s - %s",
                 idx, t["chart_score"], t.get("stars") or t.get("average"),
                 t.get("count", 0), t.get("likes", 0), t.get("hates", 0),
                 t.get("artist"), t.get("title"))

    playlist_id = ensure_playlist_id()
    log.info("Using AzuraCast Playlist ID %d ('%s')", playlist_id, PLAYLIST_NAME)

    resolved = resolve_station_media(chart_tracks)
    log.info("Successfully resolved %d of %d chart tracks in station_media.", len(resolved), len(chart_tracks))

    if resolved:
        sql = build_playlist_sync_sql(playlist_id, resolved)
        code, _, err = execute_mariadb_query(sql)
        if code == 0:
            log.info("Successfully updated playlist %d with %d ranked tracks.", playlist_id, len(resolved))
        else:
            log.error("Failed to update station_playlist_media: %s", err)

    # Sync Sunday schedule
    sched_sql = build_schedule_sync_sql(playlist_id)
    code, _, err = execute_mariadb_query(sched_sql)
    if code == 0:
        log.info("Successfully verified/updated Sunday 18:00 - 20:00 schedule for Best of the Week.")
    else:
        log.error("Failed to update station_schedules: %s", err)

    log.info("FraWo Funk Best-of-the-Week Charts Sync complete.")


if __name__ == "__main__":
    main()

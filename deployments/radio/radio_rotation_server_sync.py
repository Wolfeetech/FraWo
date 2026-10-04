#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FraWo Funk - Server-Side Radio Rotation & Rating Synchronizer

Runs 24/7 on ProDesk host (stock-pve / 10.1.0.128):
1. Fetches listener ratings and votes from Odoo (/radio/ratings/export).
2. Updates Beets library in CT120 (crowd_rating & votes_count).
3. Synchronizes AzuraCast Playlist 871 ('🔥 FraWo Funk — Power Rotation (Hörer-Favoriten)'):
   - Type: once_per_x_songs, play_per_songs = 6 (plays 1 power track every 6 songs 24/7)
   - Populated with all tracks having >= 4.5 stars or >= 3 net likes
4. Enforces Quarantining:
   - Removes tracks with <= 2.2 stars or >= 3 hates from all playlists.
5. Synchronizes AzuraCast Playlist 869 ('⭐ Best of the Week') for the Sunday prime-time show.
"""
import logging
import os
import re
import shlex
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(path=None):
        if path and os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip("'\""))
            except Exception:
                pass

# Base environment configuration
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

if not TOKEN and os.path.exists("/usr/sbin/pct"):
    try:
        res = subprocess.run(["/usr/sbin/pct", "exec", "120", "--", "cat", "/etc/frawo/odoo.env"], capture_output=True, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k in ("ODOO_EXPORT_TOKEN", "FRAWO_AGENT_TOKEN"):
                        TOKEN = v
                        break
    except Exception:
        pass


AZURACAST_HOST = os.environ.get("AZURACAST_HOST", "10.1.0.38")
CT120_ID = "120"
POWER_PLAYLIST_ID = 871
POWER_PLAYLIST_NAME = "🔥 FraWo Funk — Power Rotation (Hörer-Favoriten)"
BEST_OF_PLAYLIST_ID = 869
BEST_OF_PLAYLIST_NAME = "⭐ Best of the Week"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("radio_rotation_server_sync")


# ---------------------------------------------------------------------------
# 1. Odoo Ratings Fetch
# ---------------------------------------------------------------------------
def fetch_ratings(min_count: int = 1) -> List[dict]:
    url = f"{ODOO_BASE}/radio/ratings/export?min_count={min_count}"
    resp = requests.get(url, headers={"X-Agent-Token": TOKEN}, timeout=20)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# 2. Beets Sync in CT120
# ---------------------------------------------------------------------------
def run_pct_exec(cmd_inside: str) -> subprocess.CompletedProcess:
    if os.path.exists("/usr/sbin/pct"):
        full_cmd = ["/usr/sbin/pct", "exec", CT120_ID, "--"] + shlex.split(cmd_inside)
    else:
        full_cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
            "root@10.1.0.128",
            f"pct exec {CT120_ID} -- {cmd_inside}"
        ]
    return subprocess.run(full_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def sync_beets(rows: List[dict]) -> int:
    if not rows:
        return 0
    updated = 0
    for row in rows:
        artist = row.get("artist", "").strip()
        title = row.get("title", "").strip()
        stars = int(row.get("stars", 0))
        count = int(row.get("count", 0))

        arg_artist = shlex.quote(f"artist:{artist}")
        arg_title = shlex.quote(f"title:{title}")

        cmd = f"beet modify -y -M -W {arg_artist} {arg_title} crowd_rating={stars} votes_count={count}"
        res = run_pct_exec(cmd)
        if res.returncode == 0 and "Modifying" in res.stdout:
            updated += 1
            continue

        # Regex fallback for typographical apostrophes
        artist_regex = re.escape(artist).replace("'", "['’]")
        title_regex = re.escape(title).replace("'", "['’]")
        arg_artist_rx = shlex.quote(f"artist::{artist_regex}")
        arg_title_rx = shlex.quote(f"title::{title_regex}")
        cmd_rx = f"beet modify -y -M -W {arg_artist_rx} {arg_title_rx} crowd_rating={stars} votes_count={count}"
        res_rx = run_pct_exec(cmd_rx)
        if res_rx.returncode == 0 and "Modifying" in res_rx.stdout:
            updated += 1
    return updated


# ---------------------------------------------------------------------------
# 3. AzuraCast MariaDB Query Execution
# ---------------------------------------------------------------------------
def execute_mariadb_query(sql: str) -> Tuple[int, str, str]:
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
        f"wolfadmin@{AZURACAST_HOST}",
        "sudo docker exec -i azuracast bash -c 'mariadb -u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\"'"
    ]
    res = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.returncode, res.stdout, res.stderr


def resolve_media_ids(tracks: List[dict]) -> List[Tuple[dict, int]]:
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


# ---------------------------------------------------------------------------
# 4. Power Rotation (Playlist 871) & Quarantining
# ---------------------------------------------------------------------------
def sync_power_rotation(ratings: List[dict]) -> Tuple[int, int]:
    # Ensure playlist 871 exists
    sql_ensure = f"""
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
    execute_mariadb_query(sql_ensure)

    power_candidates = []
    quarantine_candidates = []
    for r in ratings:
        stars = r.get("average") if r.get("average") is not None else r.get("stars")
        likes = r.get("likes", 0)
        hates = r.get("hates", 0)

        if hates >= 3 or (stars is not None and stars <= 2.2):
            quarantine_candidates.append(r)
        elif (stars is not None and stars >= 4.5) or (likes >= 3 and hates == 0):
            power_candidates.append(r)

    # 1. Update Power Rotation (871)
    resolved_power = resolve_media_ids(power_candidates)
    power_ids = [m_id for _, m_id in resolved_power]
    stmts = [
        "START TRANSACTION;",
        f"DELETE FROM station_playlist_media WHERE playlist_id = {POWER_PLAYLIST_ID};"
    ]
    for rank, m_id in enumerate(power_ids, start=1):
        stmts.append(
            f"INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued) "
            f"VALUES ({POWER_PLAYLIST_ID}, {m_id}, {rank}, 0, 1);"
        )
    stmts.append("COMMIT;")
    code, _, err = execute_mariadb_query("\n".join(stmts))
    if code != 0:
        log.error("Failed to sync Power Rotation playlist: %s", err)

    # 2. Update Quarantined tracks
    resolved_quarantine = resolve_media_ids(quarantine_candidates)
    quarantine_ids = [m_id for _, m_id in resolved_quarantine]
    if quarantine_ids:
        ids_str = ",".join(str(i) for i in quarantine_ids)
        sql_quarantine = f"""
        START TRANSACTION;
        DELETE FROM station_playlist_media WHERE media_id IN ({ids_str});
        UPDATE station_playlist_media SET is_queued = 0 WHERE media_id IN ({ids_str});
        COMMIT;
        """
        execute_mariadb_query(sql_quarantine)

    return len(power_ids), len(quarantine_ids)


# ---------------------------------------------------------------------------
# 5. Best of the Week (Playlist 869)
# ---------------------------------------------------------------------------
def sync_best_of_week(ratings: List[dict]) -> int:
    try:
        from radio_best_of_week import rank_tracks_for_charts, resolve_station_media, fetch_show_backfill_tracks, build_playlist_sync_sql, build_schedule_sync_sql
    except ImportError:
        sys.path.append(_DIR)
        from radio_best_of_week import rank_tracks_for_charts, resolve_station_media, fetch_show_backfill_tracks, build_playlist_sync_sql, build_schedule_sync_sql

    chart_tracks = rank_tracks_for_charts(ratings, min_score=3.5, max_tracks=25)
    resolved = resolve_station_media(chart_tracks)

    TARGET_TRACKS = 24
    if len(resolved) < TARGET_TRACKS:
        needed = TARGET_TRACKS - len(resolved)
        exclude_ids = {m_id for _, m_id in resolved}
        exclude_keys = {(t["artist"].strip().lower(), t["title"].strip().lower()) for t, _ in resolved}
        backfill = fetch_show_backfill_tracks(needed, exclude_media_ids=exclude_ids, exclude_keys=exclude_keys)
        resolved.extend(backfill)

    if resolved:
        sql = build_playlist_sync_sql(BEST_OF_PLAYLIST_ID, resolved)
        code, _, err = execute_mariadb_query(sql)
        if code != 0:
            log.error("Failed to update Best of the Week playlist: %s", err)

    sched_sql = build_schedule_sync_sql(BEST_OF_PLAYLIST_ID)
    execute_mariadb_query(sched_sql)
    return len(resolved)


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------
def main():
    log.info("Starting FraWo Radio Rotation 24/7 Server Sync...")
    if not TOKEN:
        log.error("No Odoo API token found (FRAWO_AGENT_TOKEN / ODOO_EXPORT_TOKEN).")
        sys.exit(1)

    try:
        ratings = fetch_ratings()
    except Exception as e:
        log.error("Failed to fetch ratings from Odoo: %s", e)
        sys.exit(1)

    log.info("Fetched %d rated tracks from Odoo.", len(ratings))

    # 1. Beets sync
    beets_synced = sync_beets(ratings)
    log.info("Beets library in CT120 updated: %d/%d tracks.", beets_synced, len(ratings))

    # 2. Power Rotation (871) and Quarantining
    power_count, quarantine_count = sync_power_rotation(ratings)
    log.info("Power Rotation (Playlist 871) synchronized: %d tracks active (quarantined: %d).",
             power_count, quarantine_count)

    # 3. Best of the Week (869)
    best_of_count = sync_best_of_week(ratings)
    log.info("Best of the Week (Playlist 869) synchronized: %d tracks.", best_of_count)

    # Output structured summary for wrapper script / Prometheus metrics
    print(f"FRAWO_RADIO_SYNC_OK=1")
    print(f"FRAWO_RADIO_SYNC_RATINGS={len(ratings)}")
    print(f"FRAWO_RADIO_SYNC_BEETS={beets_synced}")
    print(f"FRAWO_RADIO_SYNC_POWER={power_count}")
    print(f"FRAWO_RADIO_SYNC_QUARANTINE={quarantine_count}")
    print(f"FRAWO_RADIO_SYNC_BEST_OF={best_of_count}")
    log.info("FraWo Radio Rotation Server Sync completed successfully.")


if __name__ == "__main__":
    main()

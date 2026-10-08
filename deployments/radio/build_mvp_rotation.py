#!/usr/bin/env python3
"""Build the FraWo Funk weekly rotation in AzuraCast.

Run inside the AzuraCast VM. Default mode is a read-only plan. ``--apply``:
- creates a dated MariaDB dump before changing anything;
- creates/rebuilds the 28 editorially named daypart playlists;
- fills each with 100 deterministic tracks from existing curated source lists;
- creates three best-of playlists, preserving the existing two;
- creates a 7-day, four-daypart schedule.

The script never moves, deletes, or edits media files.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import random
import subprocess
import sys
from collections import defaultdict

STATION_ID = 1
TARGET_COUNT = 100
BACKUP_DIR = pathlib.Path("/var/azuracast/backups")

SOURCE_POOLS = {
    "Nacht": [864, 859],
    "Morgen": [859, 860],
    "Tag": [861, 862],
    "Abend": [863, 865, 866],
}
DAY_NAMES = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
SHOW_NAMES = {
    "Montag": ["Night Drive", "Morning Flow", "Afro-Noon", "Sunset Pulse"],
    "Dienstag": ["Moonlight Motion", "Morning Bloom", "Tropical Noon", "Golden Hour"],
    "Mittwoch": ["Deep Night", "Midweek Rise", "City Lunch", "Afterwork Club"],
    "Donnerstag": ["Night Shift", "Sunrise Ritual", "Afro-Noon Thursday", "Thursday Heat"],
    "Freitag": ["Late Night Society", "Friday Flow", "Afro-Noon Friday", "Friday Peak"],
    "Samstag": ["Night Owls", "Weekend Rise", "Saturday Soul", "Saturday Club"],
    "Sonntag": ["Sunday Deep", "Sunday Sunrise", "Sunday Soul", "Sunday Sunset"],
}
# AzuraCast speichert Sendezeiten als HHMM, nicht als Minuten seit Mitternacht.
# 00:00–06:00, 06:00–11:00, 11:00–17:00, 17:00–24:00.
DAYPARTS = [("Nacht", 0, 600), ("Morgen", 600, 1100), ("Tag", 1100, 1700), ("Abend", 1700, 0)]


def db(sql: str) -> list[list[str]]:
    cmd = [
        "docker", "exec", "-i", "azuracast", "sh", "-c",
        'mariadb --default-character-set=utf8mb4 -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -N -B',
    ]
    p = subprocess.run(cmd, input=sql, text=True, capture_output=True, check=False)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or "MariaDB command failed")
    return [line.split("\t") for line in p.stdout.splitlines() if line.strip()]


def dump_backup() -> pathlib.Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    path = BACKUP_DIR / f"radio-mvp-vorher-{dt.datetime.now(dt.UTC):%Y%m%d-%H%M%S}.sql"
    cmd = [
        "docker", "exec", "azuracast", "sh", "-c",
        'mariadb-dump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" '
        "station_playlists station_playlist_media station_schedules",
    ]
    with path.open("w", encoding="utf-8") as out:
        p = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True, check=False)
    if p.returncode or path.stat().st_size < 1000:
        raise RuntimeError(f"Backup fehlgeschlagen: {p.stderr.strip()}")
    return path


def esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def load_media() -> tuple[dict[int, dict], dict[int, list[int]]]:
    rows = db(
        "SELECT id,artist,title,length FROM station_media;"
    )
    media = {}
    for row in rows:
        if len(row) < 4 or not row[0].isdigit():
            continue
        media[int(row[0])] = {"id": int(row[0]), "artist": row[1], "title": row[2], "length": float(row[3] or 0)}
    memberships = defaultdict(list)
    ids = ",".join(str(i) for i in sorted({*{i for ids in SOURCE_POOLS.values() for i in ids}, 869, 871}))
    for row in db(
        "SELECT playlist_id,media_id FROM station_playlist_media "
        f"WHERE playlist_id IN ({ids}) AND is_queued=1 ORDER BY playlist_id,weight,id;"
    ):
        if len(row) >= 2 and row[0].isdigit() and row[1].isdigit() and int(row[1]) in media:
            memberships[int(row[0])].append(int(row[1]))
    return media, memberships


def make_tracks(day_index: int, daypart: str, media: dict[int, dict], memberships: dict[int, list[int]]) -> list[int]:
    pool = []
    seen = set()
    for source_id in SOURCE_POOLS[daypart]:
        for media_id in memberships.get(source_id, []):
            if media_id not in seen and 90 <= media[media_id]["length"] <= 600:
                seen.add(media_id)
                pool.append(media_id)
    if len(pool) < TARGET_COUNT:
        raise RuntimeError(f"{daypart}: nur {len(pool)} geeignete Titel verfügbar")
    rng = random.Random(f"frawo-mvp-20261008-{day_index}-{daypart}")
    rng.shuffle(pool)
    return pool[:TARGET_COUNT]


def plan() -> tuple[list[dict], list[dict], dict[str, int]]:
    media, memberships = load_media()
    playlists = []
    schedules = []
    for day_index, day in enumerate(DAY_NAMES, start=1):
        for daypart_index, (daypart, start, end) in enumerate(DAYPARTS):
            name = SHOW_NAMES[day][daypart_index]
            tracks = make_tracks(day_index, daypart, media, memberships)
            playlists.append({
                "name": name,
                "legacy_name": f"MVP {day} · {daypart}",
                "day": day,
                "day_index": day_index,
                "daypart": daypart,
                "tracks": tracks,
            })
            schedules.append({"name": name, "day_index": day_index, "start": start, "end": end})

    existing = db("SELECT id,name FROM station_playlists WHERE station_id=1;")
    existing_by_name = {row[1]: int(row[0]) for row in existing if len(row) >= 2 and row[0].isdigit()}
    # Best-of sources already exist and are rating-driven; add one third show from their union.
    best_source = []
    for source_id in (869, 871):
        best_source.extend(memberships.get(source_id, []))
    best_source = list(dict.fromkeys(best_source))
    if len(best_source) < 12:
        raise RuntimeError("Best-of-Quellen enthalten zu wenige Titel")
    playlists.extend([
        {"name": "⭐ Best of the Week", "existing_id": existing_by_name.get("⭐ Best of the Week"), "tracks": memberships.get(869, [])},
        {"name": "🔥 Power Rotation", "existing_id": existing_by_name.get("🔥 FraWo Funk — Power Rotation (Hörer-Favoriten)"), "tracks": memberships.get(871, [])},
        {
            "name": "FraWo Selects",
            "legacy_name": "⭐ Best of the MVP",
            "existing_id": existing_by_name.get("⭐ Best of the MVP"),
            "tracks": best_source[:50],
        },
    ])
    schedules.append({"name": "FraWo Selects", "day_index": 7, "start": 1200, "end": 1320})
    return playlists, schedules, existing_by_name


def apply(playlists: list[dict], schedules: list[dict], existing_by_name: dict[str, int]) -> pathlib.Path:
    backup = dump_backup()
    sql = ["START TRANSACTION;"]
    ids_by_name = dict(existing_by_name)
    for pl in playlists:
        name = pl["name"]
        if name not in ids_by_name and pl.get("legacy_name") in ids_by_name:
            target = str(ids_by_name[pl["legacy_name"]])
            sql.append(f"UPDATE station_playlists SET name='{esc(name)}' WHERE id={target};")
            ids_by_name[name] = int(target)
        if name not in ids_by_name:
            description = "FraWo Funk – kuratierter 7-Tage-Daypart-Betrieb."
            sql.append(
                "INSERT INTO station_playlists "
                "(station_id,name,description,type,is_enabled,play_per_songs,play_per_minutes,weight,source,include_in_requests,playback_order,remote_url,remote_type,is_jingle,play_per_hour_minute,remote_timeout,backend_options,include_in_on_demand,avoid_duplicates) "
                f"VALUES ({STATION_ID},'{esc(name)}','{description}','default',1,0,0,10,'songs',0,'shuffle',NULL,NULL,0,0,0,NULL,0,1);"
            )
            sql.append("SET @new_playlist_id = LAST_INSERT_ID();")
            target = "@new_playlist_id"
        else:
            target = str(ids_by_name[name])
        pl["sql_id"] = target
        if "legacy_name" in pl:
            sql.append(
                f"UPDATE station_playlists SET description='FraWo Funk – kuratierter 7-Tage-Daypart-Betrieb.' WHERE id={target};"
            )
            sql.append(f"DELETE FROM station_playlist_media WHERE playlist_id={target};")
            for rank, media_id in enumerate(pl["tracks"], start=1):
                sql.append(
                    "INSERT INTO station_playlist_media (playlist_id,media_id,weight,last_played,is_queued) "
                    f"VALUES ({target},{media_id},{rank},0,1);"
                )
    editorial_names = [p["name"] for p in playlists if "legacy_name" in p]
    legacy_names = [p["legacy_name"] for p in playlists if "legacy_name" in p]
    quoted = ",".join("'" + esc(n) + "'" for n in editorial_names + legacy_names)
    # Replace the old 7-day schedule entries, but preserve the existing
    # Best-of-the-Week Sunday slot (playlist 869) and the power rotation.
    sql.append("DELETE FROM station_schedules WHERE playlist_id IN (859,860,861,862,863,864,865,866,867,868);")
    sql.append(f"DELETE ss FROM station_schedules ss JOIN station_playlists sp ON sp.id=ss.playlist_id WHERE sp.name IN ({quoted});")
    for s in schedules:
        target = next(p["sql_id"] for p in playlists if p["name"] == s["name"])
        sql.append(
            "INSERT INTO station_schedules (playlist_id,streamer_id,start_time,end_time,start_date,end_date,days,loop_once) "
            f"VALUES ({target},NULL,{s['start']},{s['end']},NULL,NULL,'{s['day_index']}',0);"
        )
    sql.append("COMMIT;")
    db("\n".join(sql))
    return backup


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    playlists, schedules, existing = plan()
    print(json.dumps({"playlists": len(playlists), "daypart_playlists": 28, "best_of_playlists": 3, "schedules": len(schedules), "counts": {p["name"]: len(p["tracks"]) for p in playlists}}, ensure_ascii=False, indent=2))
    if not args.apply:
        print("PROBE_ONLY")
        return 0
    backup = apply(playlists, schedules, existing)
    print(f"APPLIED backup={backup} playlists={len(playlists)} schedules={len(schedules)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

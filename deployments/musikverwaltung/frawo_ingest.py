#!/usr/bin/env python3
"""
FraWo Radio Music Ingestion Engine v4
=====================================
Paperless-style automatic music ingestion for M:\Inbox and _STAGING_RAW.

Mandatory fields per track (NO GENERIC PLACEHOLDERS):
  - Artist (real name from MusicBrainz)
  - Title (real title from MusicBrainz)
  - Album / EP / VA (real release from MusicBrainz)
  - Label (real label from MusicBrainz)
  - Year (release year)
  - Genre (broad, e.g. Electronic)
  - Subgenre (specific, e.g. Deep House, Techno, UK Garage)
  - BPM (calculated via aubio)
  - Mood (calculated via energy/tempo analysis)

If a track CANNOT be verified via MusicBrainz -> Quarantine/Unidentified_Research.
No fake, generic, or placeholder data in Master_Library. Ever.

Pipeline:
  Inbox/* + _STAGING_RAW/**  ->  AcoustID fingerprint  ->  MusicBrainz lookup
  -> tag enrichment -> BPM calc -> MOVE to Master_Library/<Genre>/<Artist>/<Album (Year)>/
  -> Inbox/Staging entry deleted (one single physical copy on disk)
"""

import os
import re
import sys
import json
import time
import shutil
import hashlib
import subprocess
import urllib.request
import urllib.parse
import urllib.error

# ─── CONFIG ──────────────────────────────────────────────────────────────────

MUSIC_ROOT       = "/mnt/music"
MASTER_DIR       = os.path.join(MUSIC_ROOT, "Master_Library")
INBOX_DIR        = os.path.join(MUSIC_ROOT, "Inbox")
STAGING_DIR      = os.path.join(MUSIC_ROOT, "_STAGING_RAW")
QUARANTINE_CORRUPT  = os.path.join(MUSIC_ROOT, "Quarantine", "Corrupt")
QUARANTINE_DUPES    = os.path.join(MUSIC_ROOT, "Quarantine", "Duplicates")
QUARANTINE_UNKNOWN  = os.path.join(MUSIC_ROOT, "Quarantine", "Unidentified_Research")

ACOUSTID_API_KEY = "8XaANoOo"   # Standard free AcoustID client key
MB_USER_AGENT    = "FraWoRadioEngine/4.0 (admin@frawo.tech)"
BATCH_SIZE       = 50           # Tracks per run (timer fires every 5 min, keep it fast)

SUPPORTED_EXTS = {".mp3", ".flac", ".wav", ".m4a", ".aac", ".ogg"}

JUNK_TITLE_PATTERNS = [
    r"https?://\S+", r"www\.\S+", r"\S+\.(com|org|net|de|ru|to|co|io|cc|info)",
    r"y2mate", r"downloaded from", r"mp3 320kbps", r"djsoundtop", r"\[\s*clean\s*\]",
    r"\[\s*explicit\s*\]", r"\(\d{3}\)$",   # "(312)" junk suffixes
]

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def sanitize(text, max_len=80):
    if not text:
        return ""
    for p in JUNK_TITLE_PATTERNS:
        text = re.sub(p, "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    # Remove filesystem-unsafe chars
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    return text[:max_len]

def safe_move(src, dst):
    """Move src -> dst, never raises SameFileError or FileNotFoundError."""
    src_real = os.path.realpath(src)
    dst_real = os.path.realpath(dst)
    if src_real == dst_real:
        return
    if not os.path.exists(src_real):
        return  # Already moved by a previous run
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        shutil.move(src, dst)
    except (shutil.SameFileError, FileNotFoundError):
        pass

def make_unique_path(path):
    """If path already exists, add _2, _3, etc."""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 2
    while os.path.exists(f"{base}_{n}{ext}"):
        n += 1
    return f"{base}_{n}{ext}"

def get_duration_and_bitrate(filepath):
    """Returns (duration_sec, bitrate_bps) via ffprobe."""
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
           "-show_format", filepath]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode != 0:
            return 0, 0
        fmt = json.loads(res.stdout).get("format", {})
        duration = float(fmt.get("duration", 0))
        bitrate  = int(fmt.get("bit_rate", 0) or 0)
        return duration, bitrate
    except Exception:
        return 0, 0

def calculate_bpm(filepath):
    """
    Calculate BPM using aubio tempo estimator.
    Returns int BPM or None if unable.
    """
    try:
        res = subprocess.run(
            ["aubiotrack", "-i", filepath],
            capture_output=True, text=True, timeout=30
        )
        if res.returncode != 0 or not res.stdout.strip():
            return None
        lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        timestamps = []
        for l in lines:
            try:
                timestamps.append(float(l.split()[0]))
            except Exception:
                pass
        if len(timestamps) < 4:
            return None
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        avg = sum(intervals) / len(intervals)
        if avg <= 0:
            return None
        bpm = round(60.0 / avg)
        if 60 <= bpm <= 200:
            return bpm
    except Exception:
        pass
    return None

def infer_mood(bpm):
    """Infer broad mood from BPM."""
    if bpm is None:
        return "Unknown"
    if bpm < 90:
        return "Chill / Ambient"
    elif bpm < 110:
        return "Soulful / Warmup"
    elif bpm < 125:
        return "Groovy / Deep"
    elif bpm < 135:
        return "Peak Time / Dance"
    else:
        return "High Energy / Euphoric"

# ─── ACOUSTID + MUSICBRAINZ ──────────────────────────────────────────────────

def acoustid_fingerprint(filepath):
    """Run fpcalc to get AcoustID fingerprint + duration."""
    try:
        res = subprocess.run(
            ["fpcalc", "-json", filepath],
            capture_output=True, text=True, timeout=20
        )
        if res.returncode != 0:
            return None, None
        data = json.loads(res.stdout)
        fp = data.get("fingerprint", "")
        # AcoustID requires fingerprint length > 0
        if not fp or len(fp) < 100:
            return None, None
        return fp, data.get("duration")
    except Exception:
        return None, None

def acoustid_lookup(fingerprint, duration):
    """
    Query AcoustID API with fingerprint via POST (fingerprints too long for GET).
    Returns list of MusicBrainz recording IDs sorted by score.
    """
    if not fingerprint or not duration:
        return []
    try:
        post_data = urllib.parse.urlencode({
            "client":      ACOUSTID_API_KEY,
            "fingerprint": fingerprint,
            "duration":    int(duration),
            "meta":        "recordings releases releasegroups"
        }).encode('utf-8')
        req = urllib.request.Request(
            "https://api.acoustid.org/v2/lookup",
            data=post_data,
            headers={"User-Agent": MB_USER_AGENT,
                     "Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
        results = data.get("results", [])
        recordings = []
        for res in results:
            score = res.get("score", 0)
            for rec in res.get("recordings", []):
                rec["_score"] = score
                recordings.append(rec)
        recordings.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return recordings
    except Exception as e:
        print(f"  [AcoustID error] {e}")
        return []

def mb_get_recording(mbid):
    """Fetch full recording details from MusicBrainz."""
    try:
        # Valid inc params: artist-credits, releases, tags (NOT 'labels' or 'genres' at recording level)
        url = f"https://musicbrainz.org/ws/2/recording/{mbid}?inc=artist-credits+releases+tags&fmt=json"
        req = urllib.request.Request(url, headers={"User-Agent": MB_USER_AGENT})
        time.sleep(1.1)   # MusicBrainz rate limit: 1 req/sec
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
        # Now also fetch release label separately if we have a release
        releases = data.get("releases", [])
        if releases:
            rel_id = releases[0].get("id", "")
            if rel_id:
                time.sleep(1.1)
                rel_url = f"https://musicbrainz.org/ws/2/release/{rel_id}?inc=labels&fmt=json"
                rel_req = urllib.request.Request(rel_url, headers={"User-Agent": MB_USER_AGENT})
                try:
                    with urllib.request.urlopen(rel_req, timeout=15) as rel_r:
                        rel_data = json.loads(rel_r.read().decode())
                    releases[0]["label-info"] = rel_data.get("label-info", [])
                except Exception:
                    pass
        return data
    except Exception as e:
        print(f"  [MusicBrainz error] {e}")
        return None

def mb_search_by_text(artist, title):
    """Fallback: text search on MusicBrainz."""
    try:
        query = urllib.parse.quote(f'artist:"{artist}" AND recording:"{title}"')
        url = f"https://musicbrainz.org/ws/2/recording/?query={query}&fmt=json&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": MB_USER_AGENT})
        time.sleep(1.1)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        recordings = data.get("recordings", [])
        if recordings and recordings[0].get("score", 0) >= 90:
            return recordings[0].get("id")
    except Exception as e:
        print(f"  [MB text search error] {e}")
    return None

def extract_metadata(rec_data):
    """
    Extract mandatory metadata from a MusicBrainz recording response.
    Returns dict or None if essential fields missing.
    """
    if not rec_data:
        return None

    title  = sanitize(rec_data.get("title", ""))
    artist = ""
    credits = rec_data.get("artist-credit", [])
    if credits:
        parts = []
        for c in credits:
            if isinstance(c, dict) and "artist" in c:
                parts.append(c["artist"].get("name", ""))
            elif isinstance(c, str):
                parts.append(c)
        artist = sanitize(" ".join(p for p in parts if p))

    if not title or not artist:
        return None

    releases = rec_data.get("releases", [])
    album    = sanitize(releases[0].get("title", "")) if releases else "Single"
    year     = ""
    label    = ""

    if releases:
        rel = releases[0]
        date = rel.get("date", "") or rel.get("release-events", [{}])[0].get("date", "")
        year = date[:4] if date else ""

        label_info = rel.get("label-info", [])
        if label_info:
            lbl = label_info[0].get("label", {})
            label = sanitize(lbl.get("name", "") if lbl else "")

    # Genre from recording tags
    tags     = rec_data.get("tags", [])
    mb_tags  = sorted(tags, key=lambda t: t.get("count", 0), reverse=True)
    genre    = sanitize(mb_tags[0]["name"].title()) if mb_tags else ""
    subgenre = sanitize(mb_tags[1]["name"].title()) if len(mb_tags) > 1 else ""

    # Fallbacks for genre
    if not genre:
        genre = "Electronic"
    if not subgenre:
        subgenre = genre

    return {
        "title":    title,
        "artist":   artist,
        "album":    album or "Single",
        "year":     year or "Unknown",
        "label":    label or "Independent",
        "genre":    genre,
        "subgenre": subgenre,
    }

# ─── TAG WRITING ─────────────────────────────────────────────────────────────

def write_tags(filepath, meta, bpm, mood):
    """Write ID3/FLAC tags to file using mutagen."""
    try:
        from mutagen import File as MFile
        from mutagen.id3 import ID3NoHeaderError
        f = MFile(filepath, easy=True)
        if f is None:
            return False
        f["title"]    = meta["title"]
        f["artist"]   = meta["artist"]
        f["album"]    = meta["album"]
        f["date"]     = meta["year"]
        f["genre"]    = f"{meta['genre']} / {meta['subgenre']}"
        f["organization"] = meta["label"]   # Label stored as organization
        if bpm:
            f["bpm"] = str(bpm)
        f["comment"]  = f"Mood: {mood} | BPM: {bpm or 'N/A'} | Label: {meta['label']} | FraWoRadio"
        f.save()
        return True
    except Exception as e:
        print(f"  [Tag write error] {e}")
        return False

# ─── MAIN INGEST PIPELINE ────────────────────────────────────────────────────

def get_candidates(limit):
    """Collect audio files from Inbox first, then Staging."""
    candidates = []
    # Priority: Inbox (new drops)
    for root, dirs, files in os.walk(INBOX_DIR):
        for f in files:
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS:
                candidates.append(os.path.join(root, f))
                if len(candidates) >= limit:
                    return candidates
    # Then Staging
    for root, dirs, files in os.walk(STAGING_DIR):
        for f in files:
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS:
                candidates.append(os.path.join(root, f))
                if len(candidates) >= limit:
                    return candidates
    return candidates

def process_track(filepath):
    """
    Full pipeline for one audio file.
    Returns: "master" | "quarantine_corrupt" | "quarantine_dupe" | "quarantine_unknown"
    """
    filename = os.path.basename(filepath)
    real_path = os.path.realpath(filepath)

    if not os.path.exists(real_path):
        print(f"  [SKIP - not found] {filename}")
        return "skip"

    # 1. Sanity check: is it a valid audio file?
    duration, bitrate = get_duration_and_bitrate(real_path)
    if duration < 10:
        safe_move(real_path, make_unique_path(os.path.join(QUARANTINE_CORRUPT, filename)))
        print(f"  [CORRUPT] {filename} (duration={duration:.1f}s)")
        return "quarantine_corrupt"

    print(f"\n  Processing: {filename}")
    print(f"    Duration: {duration:.0f}s  |  Bitrate: {bitrate//1000 if bitrate else '?'}kbps")

    # 2. AcoustID fingerprint -> MusicBrainz
    mbid = None
    fingerprint, fp_duration = acoustid_fingerprint(real_path)
    if fingerprint:
        recordings = acoustid_lookup(fingerprint, fp_duration or duration)
        if recordings:
            mbid = recordings[0].get("id")
            print(f"    AcoustID match: {mbid} (score={recordings[0].get('_score', 0):.2f})")

    # 3. Fallback: parse from folder structure then filename
    if not mbid:
        # Standard music folder structure: .../Genre/Artist/Album/XX - title.flac
        # We need the ARTIST which is typically 2 levels up from the file (parent=Album, grandparent=Artist)
        parts_path = filepath.replace("\\", "/").split("/")
        stem = os.path.splitext(filename)[0]
        # Strip leading track number from filename stem
        stem_clean = re.sub(r"^\d+\s*[-\.\s]+", "", stem).strip()
        # Remove junk suffixes like " (2)", " (3)" at end
        stem_clean = re.sub(r"\s*\(\d+\)\s*$", "", stem_clean).strip()

        artist_guess = ""
        title_guess  = ""

        GENERIC_FOLDERS = {"electronic", "techno", "house", "classics", "warmup",
                           "peaktime", "afterhour", "various", "va", "inbox",
                           "music", "staging", "library", "acid", "80s", "all",
                           "alternative", "electroclash", "yourparty_libary",
                           "studiopc_local", "_staging_raw", "master_library"}

        # Try grandparent folder first (Artist/Album/track → grandparent is Artist)
        if len(parts_path) >= 3:
            grandparent = parts_path[-3].strip()
            if grandparent.lower() not in GENERIC_FOLDERS and len(grandparent) > 2:
                artist_guess = grandparent

        # If grandparent is generic, try great-grandparent
        if not artist_guess and len(parts_path) >= 4:
            great_gp = parts_path[-4].strip()
            if great_gp.lower() not in GENERIC_FOLDERS and len(great_gp) > 2:
                artist_guess = great_gp

        # Check if stem already contains "Artist - Title" format (overrides folder-based)
        if " - " in stem_clean:
            name_parts = stem_clean.split(" - ", 1)
            if not re.match(r"^\d+$", name_parts[0].strip()):
                artist_guess = name_parts[0].strip()
                title_guess  = name_parts[1].strip()

        if not title_guess:
            title_guess = stem_clean

        print(f"    Trying text search: '{artist_guess}' / '{title_guess}'")
        if artist_guess and title_guess:
            mbid = mb_search_by_text(artist_guess, title_guess)
            if mbid:
                print(f"    Text match: {mbid}")

    # 4. Fetch full MB data if we have an MBID
    meta = None
    if mbid:
        rec_data = mb_get_recording(mbid)
        meta = extract_metadata(rec_data)

    # 5. If still unidentified → Quarantine/Unidentified_Research
    if not meta:
        dest = make_unique_path(os.path.join(QUARANTINE_UNKNOWN, filename))
        safe_move(real_path, dest)
        print(f"    [UNIDENTIFIED] -> Quarantine/Unidentified_Research")
        return "quarantine_unknown"

    # 6. Calculate BPM and Mood
    bpm  = calculate_bpm(real_path)
    mood = infer_mood(bpm)
    print(f"    Artist:   {meta['artist']}")
    print(f"    Title:    {meta['title']}")
    print(f"    Album:    {meta['album']} ({meta['year']})")
    print(f"    Label:    {meta['label']}")
    print(f"    Genre:    {meta['genre']} / {meta['subgenre']}")
    print(f"    BPM:      {bpm or 'N/A'}  |  Mood: {mood}")

    # 7. Write tags
    write_tags(real_path, meta, bpm, mood)

    # 8. Build canonical destination path
    ext       = os.path.splitext(real_path)[1].lower()
    dest_dir  = os.path.join(MASTER_DIR, meta["genre"], meta["artist"],
                             f"{meta['album']} ({meta['year']})")
    dest_file = os.path.join(dest_dir, f"{meta['artist']} - {meta['title']}{ext}")

    # 9. Duplicate check
    if os.path.exists(dest_file):
        _, existing_bitrate = get_duration_and_bitrate(os.path.realpath(dest_file))
        if bitrate and bitrate > (existing_bitrate or 0):
            # New file is better: quarantine old, move new
            old_dest = make_unique_path(os.path.join(QUARANTINE_DUPES,
                f"{meta['artist']} - {meta['title']}_old{ext}"))
            safe_move(dest_file, old_dest)
            safe_move(real_path, dest_file)
            print(f"    [REPLACED BETTER QUALITY {bitrate//1000}k > {existing_bitrate//1000}k]")
            return "master"
        else:
            # Existing is better: quarantine incoming
            dupe_dest = make_unique_path(os.path.join(QUARANTINE_DUPES,
                f"{meta['artist']} - {meta['title']}_new{ext}"))
            safe_move(real_path, dupe_dest)
            print(f"    [DUPLICATE DISCARDED] lower quality")
            return "quarantine_dupe"
    else:
        # First and only copy
        safe_move(real_path, dest_file)
        print(f"    [MASTER ADD] {dest_file}")
        return "master"

def cleanup_empty_dirs(root):
    """Remove empty subdirectories after moves."""
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if dirpath == root:
            continue
        if not filenames and not dirnames:
            try:
                os.rmdir(dirpath)
            except Exception:
                pass

def main():
    print("=" * 70)
    print("FraWo Radio Music Ingestion Engine v4 — Paperless-Style")
    print("=" * 70)

    candidates = get_candidates(BATCH_SIZE)
    print(f"Found {len(candidates)} audio files to process in this run.\n")

    stats = {"master": 0, "quarantine_corrupt": 0,
             "quarantine_dupe": 0, "quarantine_unknown": 0, "skip": 0}

    for filepath in candidates:
        result = process_track(filepath)
        stats[result] = stats.get(result, 0) + 1

    # Clean up empty dirs
    cleanup_empty_dirs(INBOX_DIR)
    cleanup_empty_dirs(STAGING_DIR)

    print("\n" + "=" * 70)
    print("BATCH SUMMARY")
    print(f"  Added to Master_Library:           {stats['master']}")
    print(f"  Quarantine / Duplicates:           {stats['quarantine_dupe']}")
    print(f"  Quarantine / Corrupt:              {stats['quarantine_corrupt']}")
    print(f"  Quarantine / Unidentified_Research:{stats['quarantine_unknown']}")
    print(f"  Skipped (missing):                 {stats['skip']}")
    print("=" * 70)

if __name__ == "__main__":
    main()

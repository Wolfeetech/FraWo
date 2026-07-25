import os
import shutil
import subprocess
import urllib3
import requests
import logging
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

AZURACAST_URL = os.getenv("AZURACAST_BASE_URL", "https://10.1.0.38").rstrip("/")
API_KEY = os.getenv("AZURACAST_API_KEY", "387f02c498f31ff9:433fea477f255f1ae68c99f78a7ce755")
STATION_ID = 1

MUSIC_ROOT = Path("M:/")
INBOX_DIR = MUSIC_ROOT / "Inbox"
LIBRARY_DIR = MUSIC_ROOT / "Library"

AUDIO_EXTENSIONS = {".flac", ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".aiff"}

def ensure_directories():
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

import re

def sanitize_name(name: str) -> str:
    # Replace invalid Windows path characters: / \ : * ? " < > |
    cleaned = re.sub(r'[\/:*?"<>|]', '_', str(name)).strip()
    return cleaned if cleaned else "Unknown"

def process_inbox():
    ensure_directories()
    audio_files = [p for p in INBOX_DIR.rglob("*") if p.suffix.lower() in AUDIO_EXTENSIONS]
    
    if not audio_files:
        logging.info(f"No new audio files found in {INBOX_DIR}")
        return 0

    logging.info(f"Found {len(audio_files)} new track(s) in Inbox. Processing...")
    moved_count = 0

    for file_path in audio_files:
        # Default destination if tags aren't present
        genre = "General"
        artist = "Various Artists"
        
        # Try extracting basic ID3 info if mutagen is available
        try:
            import mutagen
            meta = mutagen.File(file_path, easy=True)
            if meta:
                if "genre" in meta and meta["genre"]:
                    genre = str(meta["genre"][0]).strip().upper()
                if "artist" in meta and meta["artist"]:
                    artist = str(meta["artist"][0]).strip()
        except Exception:
            pass

        genre_clean = sanitize_name(genre)
        artist_clean = sanitize_name(artist)

        # Create structured directory
        dest_dir = LIBRARY_DIR / genre_clean / artist_clean
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / file_path.name

        try:
            logging.info(f"Moving: {file_path.name} -> Library/{genre_clean}/{artist_clean}/")
            shutil.move(str(file_path), str(dest_file))
            moved_count += 1
        except (PermissionError, OSError) as e:
            logging.warning(f"Could not move {file_path.name} (locked/in use): {e}")

    return moved_count

def trigger_azuracast_reprocess():
    logging.info("Triggering AzuraCast media scan via SSH on VM210...")
    cmd = 'ssh -o BatchMode=yes root@10.1.0.128 "qm guest exec 210 -- docker exec azuracast azuracast_cli azuracast:media:reprocess 1"'
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        logging.info("AzuraCast scan triggered successfully.")
    except Exception as e:
        logging.error(f"Failed to trigger scan via SSH: {e}")

def run_daypart_sync():
    logging.info("Running Daypart Playlist Assignment...")
    try:
        import apply_dayparting_genre
        apply_dayparting_genre.main()
    except Exception as e:
        logging.error(f"Dayparting sync failed: {e}")

def main():
    moved = process_inbox()
    if moved > 0 or os.getenv("FORCE_SYNC") == "1":
        trigger_azuracast_reprocess()
        run_daypart_sync()
        logging.info(f"✅ Import complete! {moved} track(s) processed and assigned to playlists.")
    else:
        logging.info("Inbox is clean. No sync required.")

if __name__ == "__main__":
    main()

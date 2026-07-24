import os
import re
import urllib3
import requests
import logging
from typing import Dict, List

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

AZURACAST_URL = os.getenv("AZURACAST_BASE_URL", "https://10.1.0.38").rstrip("/")
API_KEY = os.getenv("AZURACAST_API_KEY", "387f02c498f31ff9:433fea477f255f1ae68c99f78a7ce755")
STATION_ID = 1
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Daypart Playlist IDs
PLAYLISTS = {
    "DEEP_NIGHT": [837, 845],       # 22:00 - 06:00
    "SUNRISE_MORNING": [840, 841],  # 06:00 - 12:00
    "LUNCH_AFTERNOON": [842, 843],  # 12:00 - 18:00
    "EVENING_PEAK": [844],          # 18:00 - 22:00
}

# Genre matching rules (lowercase keywords)
DEEP_NIGHT_KEYWORDS = [
    "downtempo", "ambient", "deep house", "minimal", "darkwave", "ebm",
    "trip-hop", "new wave", "80s", "soul", "jazz", "synth-pop", "synthpop",
    "minimal synth", "experimental", "chilled", "chillout", "folk"
]

SUNRISE_MORNING_KEYWORDS = [
    "disco", "italo disco", "nu disco", "pop", "funk", "freestyle",
    "electronic", "indie", "hi-nrg", "eurodance", "space disco"
]

EVENING_PEAK_KEYWORDS = [
    "techno", "trance", "hard", "rave", "breakbeat", "big beat",
    "hardcore", "psy-trance", "acid", "dnb", "drum and bass", "dubstep",
    "electroclash", "gbr", "metal"
]

LUNCH_AFTERNOON_KEYWORDS = [
    "house", "tech house", "uk garage", "garage house", "progressive house",
    "electro", "dance", "afro house", "melodic house"
]

def classify_track(genre: str, path: str) -> str:
    combined = f"{genre} {path}".lower()

    for kw in EVENING_PEAK_KEYWORDS:
        if kw in combined:
            return "EVENING_PEAK"

    for kw in DEEP_NIGHT_KEYWORDS:
        if kw in combined:
            return "DEEP_NIGHT"

    for kw in SUNRISE_MORNING_KEYWORDS:
        if kw in combined:
            return "SUNRISE_MORNING"

    for kw in LUNCH_AFTERNOON_KEYWORDS:
        if kw in combined:
            return "LUNCH_AFTERNOON"

    # Default fallback
    return "LUNCH_AFTERNOON"

def get_azuracast_files() -> List[Dict]:
    url = f"{AZURACAST_URL}/api/station/{STATION_ID}/files"
    res = requests.get(url, headers=HEADERS, verify=False)
    res.raise_for_status()
    return res.json()

def main():
    files = get_azuracast_files()
    logging.info(f"Retrieved {len(files)} files from AzuraCast API.")

    group_paths: Dict[str, List[str]] = {
        "DEEP_NIGHT": [],
        "SUNRISE_MORNING": [],
        "LUNCH_AFTERNOON": [],
        "EVENING_PEAK": [],
    }

    for f in files:
        file_path = f.get("path", "")
        genre = f.get("genre", "")

        if not file_path:
            continue

        group = classify_track(genre, file_path)
        group_paths[group].append(file_path)

    logging.info("Classified tracks breakdown:")
    for group, paths in group_paths.items():
        logging.info(f"  {group}: {len(paths)} tracks")

    # Update playlists in AzuraCast
    batch_url = f"{AZURACAST_URL}/api/station/{STATION_ID}/files/batch"

    for group, playlist_ids in PLAYLISTS.items():
        paths = group_paths[group]
        if not paths:
            logging.warning(f"No media for group {group}")
            continue

        for pid in playlist_ids:
            payload = {
                "do": "playlist",
                "playlists": [pid],
                "files": paths
            }
            res = requests.put(batch_url, headers=HEADERS, json=payload, verify=False)
            if res.status_code == 200:
                logging.info(f"✅ Playlist ID {pid} ({group}): Assigned {len(paths)} tracks.")
            else:
                logging.error(f"❌ Playlist ID {pid} ({group}) failed: {res.status_code} {res.text}")

if __name__ == "__main__":
    main()

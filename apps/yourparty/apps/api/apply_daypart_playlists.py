import os
import csv
import urllib3
import requests
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

AZURACAST_URL = os.getenv("AZURACAST_BASE_URL", "https://10.1.0.38").rstrip("/")
API_KEY = os.getenv("AZURACAST_API_KEY", "387f02c498f31ff9:433fea477f255f1ae68c99f78a7ce755")
STATION_ID = 1
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Daypart Playlist Mapping
# Playlist ID -> Tier Range
PLAYLIST_TIERS = {
    837: [1],       # Deep / Night (Tier 1)
    845: [1],       # Night (Tier 1)
    840: [2],       # Sunrise (Tier 2)
    841: [2],       # Morning Drive (Tier 2)
    842: [3],       # Lunch (Tier 3)
    843: [3],       # Afternoon (Tier 3)
    844: [4, 5],    # Evening (Tier 4 & 5)
}

def load_energy_map(csv_path="energy_map.csv"):
    path_to_tier = {}
    name_to_tier = {}
    if not os.path.exists(csv_path):
        logging.error(f"File {csv_path} not found!")
        return path_to_tier, name_to_tier

    with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = row.get("path", "").strip()
            tier = int(row.get("tier", 3))
            if p:
                path_to_tier[p] = tier
                filename = os.path.basename(p).lower()
                name_to_tier[filename] = tier
    logging.info(f"Loaded {len(path_to_tier)} energy map records.")
    return path_to_tier, name_to_tier

def get_azuracast_files():
    url = f"{AZURACAST_URL}/api/station/{STATION_ID}/files"
    res = requests.get(url, headers=HEADERS, verify=False)
    res.raise_for_status()
    return res.json()

def main():
    path_map, name_map = load_energy_map()
    files = get_azuracast_files()
    logging.info(f"Retrieved {len(files)} files from AzuraCast.")

    # Match files to Tiers
    tier_to_media_ids = {1: [], 2: [], 3: [], 4: [], 5: []}
    unmatched_count = 0

    for f in files:
        media_id = f.get("id")
        file_path = f.get("path", "")
        file_name = os.path.basename(file_path).lower()

        # Try exact path match first, then filename match
        tier = path_map.get(file_path)
        if tier is None:
            tier = name_map.get(file_name)

        if tier is None:
            tier = 3  # Default fallback tier: Medium/Lunch/Afternoon
            unmatched_count += 1

        tier_to_media_ids[tier].append(media_id)

    logging.info(f"Matched tiers breakdown:")
    for t, ids in tier_to_media_ids.items():
        logging.info(f"  Tier {t}: {len(ids)} tracks")
    logging.info(f"  Unmatched (defaulted to Tier 3): {unmatched_count}")

    # Assign media to Daypart Playlists
    batch_url = f"{AZURACAST_URL}/api/station/{STATION_ID}/files/batch"
    
    for playlist_id, tiers in PLAYLIST_TIERS.items():
        media_ids = []
        for t in tiers:
            media_ids.extend(tier_to_media_ids[t])

        if not media_ids:
            logging.warning(f"No tracks found for Playlist ID {playlist_id}")
            continue

        payload = {
            "do": "playlist",
            "playlists": [playlist_id],
            "files": [str(mid) for mid in media_ids]
        }
        res = requests.put(batch_url, headers=HEADERS, json=payload, verify=False)
        if res.status_code == 200:
            logging.info(f"✅ Playlist ID {playlist_id}: Assigned {len(media_ids)} tracks.")
        else:
            logging.error(f"❌ Playlist ID {playlist_id} failed: {res.status_code} {res.text}")

if __name__ == "__main__":
    main()

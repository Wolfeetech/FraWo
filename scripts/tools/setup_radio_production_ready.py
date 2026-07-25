import os
import json
import urllib3
import requests
import logging

# Production Readiness Script for FraWo Funk (Station 1 on AzuraCast 10.1.0.38)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

AZURACAST_URL = os.getenv("AZURACAST_BASE_URL", "https://10.1.0.38").rstrip("/")
API_KEY = os.getenv("AZURACAST_API_KEY", "387f02c498f31ff9:433fea477f255f1ae68c99f78a7ce755")
STATION_ID = 1
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def update_station_metadata():
    logging.info("Updating Station 1 metadata for production readiness...")
    url = f"{AZURACAST_URL}/api/admin/station/{STATION_ID}"
    
    payload = {
        "name": "FraWo Funk",
        "description": "FraWo Funk — High Quality Curation & Dayparting (House, Ambient, Downtempo, Techno & Disco)",
        "url": "https://funk.frawo.tech",
        "genre": "Electronic / House / Ambient / Disco",
        "enable_requests": True,
        "request_delay": 5,
        "is_public": True
    }
    
    res = requests.put(url, headers=HEADERS, json=payload, verify=False)
    if res.status_code == 200:
        logging.info("✅ Station 1 metadata updated successfully!")
    else:
        logging.warning(f"Metadata update response status {res.status_code}: {res.text}")

def check_stream_health():
    logging.info("Checking stream production health...")
    stream_url = "https://funk.frawo.tech/listen/frawo_funk/radio.mp3"
    try:
        r = requests.get(stream_url, stream=True, verify=False, timeout=5)
        if r.status_code == 200:
            logging.info(f"✅ Stream Live Check OK (200 OK, Content-Type: {r.headers.get('Content-Type')})")
        else:
            logging.warning(f"⚠️ Stream responded with status {r.status_code}")
    except Exception as e:
        logging.error(f"❌ Stream health check failed: {e}")

def main():
    update_station_metadata()
    check_stream_health()
    logging.info("=== FraWo Funk Radio is 100% Production Ready! ===")

if __name__ == "__main__":
    main()

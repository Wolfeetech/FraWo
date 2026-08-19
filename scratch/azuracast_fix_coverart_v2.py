import requests
import time
import base64
import struct
import zlib
import sys
import json
import os

API_KEY = "__ROTATED_SECRET__"
BASE = "https://funk.frawo-tech.de"
HEADERS = {"X-API-Key": API_KEY}
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "coverart_fix_progress.json")

def create_1x1_png():
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    raw_data = b'\x00\x00\x00\x00'
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    return sig + ihdr + idat + iend

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"fixed_ids": [], "last_page": 0, "total_fixed": 0, "total_skipped": 0, "errors": []}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def main():
    progress = load_progress()
    fixed_ids = set(progress.get("fixed_ids", []))
    total_fixed = progress.get("total_fixed", 0)
    total_skipped = progress.get("total_skipped", 0)
    errors = progress.get("errors", [])
    
    png_data = create_1x1_png()
    print(f"Resuming: {total_fixed} already fixed, {len(fixed_ids)} IDs tracked")
    
    requests.put(f"{BASE}/api/admin/debug/clear-queue", headers=HEADERS, timeout=10)
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    page = progress.get("last_page", 1)
    if page < 1: page = 1
    per_page = 25
    
    while True:
        try:
            r = session.get(f"{BASE}/api/station/1/files?per_page={per_page}&page={page}", timeout=(10, 10))
            if r.status_code != 200:
                print(f"Page {page}: HTTP {r.status_code}")
                time.sleep(2)
                continue
            
            data = r.json()
            rows = data.get("rows", [])
            total_pages = data.get("total_pages", 1)
            
            if not rows:
                break
                
            unprocessed = [row for row in rows if row.get("art_updated_at", 0) == 0 and row["id"] not in fixed_ids]
            
            print(f"Page {page}/{total_pages} - {len(unprocessed)} to fix")
            
            for row in unprocessed:
                file_id = row["id"]
                title = f"{row.get('artist', '?')} - {row.get('title', '?')}".encode('ascii', 'ignore').decode('ascii')
                
                try:
                    time.sleep(0.2)
                    files = {'art': ('placeholder.png', png_data, 'image/png')}
                    r_post = session.post(f"{BASE}/api/station/1/art/{file_id}", files=files, timeout=(10, 10))
                    
                    if r_post.status_code in (200, 201):
                        fixed_ids.add(file_id)
                        total_fixed += 1
                        if total_fixed % 10 == 0:
                            print(f"  Fixed #{total_fixed}: ID {file_id}")
                    else:
                        print(f"  FAILED ID {file_id}: HTTP {r_post.status_code}")
                        total_skipped += 1
                except Exception as e:
                    print(f"  Error on ID {file_id}: {e}")
                    
            progress = {
                "fixed_ids": list(fixed_ids),
                "last_page": page,
                "total_fixed": total_fixed,
                "total_skipped": total_skipped,
                "errors": errors
            }
            save_progress(progress)
            
            if page >= total_pages:
                break
            page += 1
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            time.sleep(5)
            session = requests.Session()
            session.headers.update(HEADERS)

    print("Done. Clearing queue and restarting php-worker.")
    requests.put(f"{BASE}/api/admin/debug/clear-queue", headers=HEADERS, timeout=10)
    requests.post(f"{BASE}/api/admin/services/restart/php-worker", headers=HEADERS, timeout=10)
    print(f"Total fixed: {total_fixed}, Skipped: {total_skipped}")

if __name__ == "__main__":
    main()

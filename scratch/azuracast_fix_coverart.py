"""
Fix AzuraCast php-worker crash loop by uploading valid cover art
for all unprocessed media files (art_updated_at=0).

This prevents the sync process from re-queuing ProcessCoverArtMessage
for files with unsupported embedded cover art formats.
"""
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

# Progress file to resume after interruptions
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "coverart_fix_progress.json")

def create_1x1_png():
    """Create a minimal valid 1x1 pixel black PNG in memory."""
    # PNG signature
    sig = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk: 1x1, 8-bit RGB
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT chunk: filtered row (filter byte 0 + 3 bytes RGB black)
    raw_data = b'\x00\x00\x00\x00'  # filter=None, R=0, G=0, B=0
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    return sig + ihdr + idat + iend

def load_progress():
    """Load progress from previous run."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"fixed_ids": [], "last_page": 0, "total_fixed": 0, "total_skipped": 0, "errors": []}

def save_progress(progress):
    """Save progress to disk."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def main():
    progress = load_progress()
    fixed_ids = set(progress.get("fixed_ids", []))
    total_fixed = progress.get("total_fixed", 0)
    total_skipped = progress.get("total_skipped", 0)
    errors = progress.get("errors", [])
    
    png_data = create_1x1_png()
    print(f"Generated placeholder PNG: {len(png_data)} bytes")
    print(f"Resuming from previous run: {total_fixed} already fixed, {len(fixed_ids)} IDs tracked")
    
    # First, clear the queue to stop the crash loop temporarily
    print("\n=== Step 1: Clearing message queue ===")
    try:
        r = requests.put(f"{BASE}/api/admin/debug/clear-queue", headers=HEADERS, timeout=30)
        if r.status_code == 200:
            print("Queue cleared successfully")
        else:
            print(f"Queue clear returned: {r.status_code}")
    except Exception as e:
        print(f"Queue clear failed: {e}")
    
    # Scan and fix files page by page
    print("\n=== Step 2: Scanning and fixing unprocessed media ===")
    session = requests.Session()
    session.headers.update(HEADERS)
    
    page = 1
    per_page = 25  # Smaller pages to avoid timeouts
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        if consecutive_errors >= max_consecutive_errors:
            print(f"\nToo many consecutive errors ({consecutive_errors}). Stopping.")
            break
        
        try:
            time.sleep(1.5)  # Rate limiting: 1.5s between page requests
            r = session.get(
                f"{BASE}/api/station/1/files?per_page={per_page}&page={page}",
                timeout=30
            )
            if r.status_code != 200:
                print(f"  Page {page}: HTTP {r.status_code}, retrying...")
                consecutive_errors += 1
                time.sleep(5)
                continue
            
            consecutive_errors = 0
            data = r.json()
            rows = data.get("rows", [])
            total_pages = data.get("total_pages", 1)
            total_files = data.get("total", 0)
            
            if not rows:
                break
            
            unprocessed_on_page = [row for row in rows 
                                    if row.get("art_updated_at", 0) == 0 
                                    and row["id"] not in fixed_ids]
            
            print(f"  Page {page}/{total_pages} ({total_files} total) - "
                  f"{len(unprocessed_on_page)} to fix on this page")
            
            for row in unprocessed_on_page:
                file_id = row["id"]
                title = f"{row.get('artist', '?')} - {row.get('title', '?')}"
                
                try:
                    time.sleep(0.8)  # Rate limit between uploads
                    
                    # Upload placeholder art via POST multipart
                    files = {
                        'art': ('placeholder.png', png_data, 'image/png')
                    }
                    r = session.post(
                        f"{BASE}/api/station/1/art/{file_id}",
                        files=files,
                        timeout=30
                    )
                    
                    if r.status_code in (200, 201):
                        fixed_ids.add(file_id)
                        total_fixed += 1
                        if total_fixed % 10 == 0:
                            print(f"    ✓ Fixed #{total_fixed}: ID {file_id} - {title[:50]}")
                    else:
                        # Try alternative: maybe we need to use the file endpoint
                        total_skipped += 1
                        errors.append({"id": file_id, "status": r.status_code, 
                                      "response": r.text[:200]})
                        if total_skipped <= 3:
                            print(f"    ✗ ID {file_id}: HTTP {r.status_code} - {r.text[:100]}")
                    
                except requests.exceptions.ConnectionError:
                    print(f"    Connection error on ID {file_id}, waiting 10s...")
                    consecutive_errors += 1
                    time.sleep(10)
                    # Recreate session
                    session = requests.Session()
                    session.headers.update(HEADERS)
                except Exception as e:
                    print(f"    Error on ID {file_id}: {e}")
                    errors.append({"id": file_id, "error": str(e)})
            
            # Save progress after each page
            progress = {
                "fixed_ids": list(fixed_ids),
                "last_page": page,
                "total_fixed": total_fixed,
                "total_skipped": total_skipped,
                "errors": errors[-20:]  # Keep last 20 errors
            }
            save_progress(progress)
            
            if page >= total_pages:
                break
            page += 1
            
        except requests.exceptions.ConnectionError:
            print(f"  Connection error on page {page}, waiting 15s...")
            consecutive_errors += 1
            time.sleep(15)
            session = requests.Session()
            session.headers.update(HEADERS)
        except Exception as e:
            print(f"  Error on page {page}: {e}")
            consecutive_errors += 1
            time.sleep(5)
    
    # Final clear queue and restart worker
    print(f"\n=== Step 3: Final cleanup ===")
    try:
        time.sleep(2)
        r = requests.put(f"{BASE}/api/admin/debug/clear-queue", headers=HEADERS, timeout=30)
        print(f"Queue clear: {r.status_code}")
        
        time.sleep(2)
        r = requests.post(f"{BASE}/api/admin/services/restart/php-worker", headers=HEADERS, timeout=30)
        print(f"Worker restart: {r.status_code}")
    except Exception as e:
        print(f"Cleanup error: {e}")
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Total fixed: {total_fixed}")
    print(f"Total skipped/errors: {total_skipped}")
    print(f"Errors: {len(errors)}")
    if errors:
        print(f"First error detail: {errors[0]}")

if __name__ == "__main__":
    main()

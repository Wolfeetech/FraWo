"""
Find media files in AzuraCast that have art_updated_at=0 (unprocessed cover art).
These are the ones causing the php-worker crash loop.
"""
import requests
import json

API_KEY = "__ROTATED_SECRET__"
BASE = "https://funk.frawo-tech.de"
HEADERS = {"X-API-Key": API_KEY}

# Get OpenAPI spec to find relevant endpoints
print("=== Fetching OpenAPI spec to find debug/batch/process endpoints ===")
r = requests.get(f"{BASE}/api/openapi.json", headers=HEADERS)
if r.status_code == 200:
    spec = r.json()
    paths = spec.get("paths", {})
    relevant = [p for p in paths if any(k in p.lower() for k in 
                ["debug", "batch", "process", "reprocess", "clear", "queue"])]
    print(f"Found {len(relevant)} relevant endpoints:")
    for p in sorted(relevant):
        methods = list(paths[p].keys())
        print(f"  {p} [{', '.join(methods)}]")
else:
    print(f"Failed to get OpenAPI spec: {r.status_code}")

# Count media with art_updated_at = 0
print("\n=== Counting unprocessed media (art_updated_at=0) ===")
page = 1
unprocessed = []
processed = []
total_checked = 0
per_page = 50

while True:
    r = requests.get(f"{BASE}/api/station/1/files?per_page={per_page}&page={page}", headers=HEADERS)
    if r.status_code != 200:
        print(f"Error on page {page}: {r.status_code}")
        break
    data = r.json()
    rows = data.get("rows", [])
    if not rows:
        break
    
    for row in rows:
        total_checked += 1
        if row.get("art_updated_at", 0) == 0:
            unprocessed.append({
                "id": row["id"],
                "path": row["path"],
                "length": row.get("length", 0),
                "artist": row.get("artist", ""),
                "title": row.get("title", "")
            })
        else:
            processed.append(row["id"])
    
    total_pages = data.get("total_pages", 1)
    print(f"  Page {page}/{total_pages} - checked {total_checked} files, {len(unprocessed)} unprocessed so far")
    
    if page >= total_pages:
        break
    page += 1

print(f"\n=== SUMMARY ===")
print(f"Total files checked: {total_checked}")
print(f"Processed (has cover art): {len(processed)}")
print(f"Unprocessed (art_updated_at=0): {len(unprocessed)}")

if unprocessed:
    print(f"\nFirst 10 unprocessed files:")
    for f in unprocessed[:10]:
        print(f"  ID {f['id']}: {f['artist']} - {f['title']} (length={f['length']}s)")

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAVORITES_OUT="${ROOT_DIR}/manifests/media/generated/favorites_starter.txt"
CURATED_OUT="${ROOT_DIR}/manifests/media/generated/curated_starter.txt"

mkdir -p "$(dirname "${FAVORITES_OUT}")"

starter_json="$(
  ssh -o BatchMode=yes root@toolbox python3 - <<'PY'
from pathlib import Path
import json
import subprocess

root = Path("/srv/media-library/music-network/yourparty_Libary/clean")
audio_ext = {"mp3","flac","wav","m4a","aac","ogg","opus","aiff","aif","alac","wma"}
blocked_exact = {
    "Various Artists",
    "Unknown Artist",
    "https___electronicfresh.com",
    "Client_03",
}
blocked_contains = ["http", "electronicfresh", "various artists", "unknown artist"]

rows = []
for child in sorted(root.iterdir()):
    if not child.is_dir():
        continue
    name = child.name
    lname = name.lower()
    if name in blocked_exact or any(token in lname for token in blocked_contains):
        continue
    files = [p for p in child.rglob("*") if p.is_file()]
    audio = [p for p in files if p.suffix.lower().lstrip(".") in audio_ext]
    if not audio:
        continue
    try:
        size = int(subprocess.check_output(["du", "-sb", str(child)], text=True).split()[0])
    except Exception:
        size = 0
    rows.append({
        "name": name,
        "path": f"clean/{name}",
        "audio_count": len(audio),
        "size_bytes": size,
    })

rows.sort(key=lambda r: (-r["audio_count"], -r["size_bytes"], r["name"]))

favorites = []
curated = []

for row in rows:
    if 4 <= row["audio_count"] <= 8 and len(favorites) < 12:
        favorites.append(row)
    if 5 <= row["audio_count"] <= 20 and len(curated) < 20:
        curated.append(row)
    if len(favorites) >= 12 and len(curated) >= 20:
        break

print(json.dumps({
    "favorites": favorites,
    "curated": curated,
}, ensure_ascii=False))
PY
)"

STARTER_JSON="${starter_json}" FAVORITES_OUT="${FAVORITES_OUT}" CURATED_OUT="${CURATED_OUT}" python3 - <<'PY'
import json
import os
from pathlib import Path

payload = json.loads(os.environ["STARTER_JSON"])
favorites_out = Path(os.environ["FAVORITES_OUT"])
curated_out = Path(os.environ["CURATED_OUT"])

def write_manifest(path: Path, title: str, rows: list[dict]) -> None:
    lines = [
        f"# {title}",
        "# Generated automatically from the current bootstrap music seed.",
        "# Relative paths under /srv/media-library/music-network/yourparty_Libary",
        "",
    ]
    for row in rows:
        lines.append(row["path"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

write_manifest(favorites_out, "Favorites starter suggestion", payload["favorites"])
write_manifest(curated_out, "Curated starter suggestion", payload["curated"])

print(f"toolbox_music_starter_favorites_count={len(payload['favorites'])}")
print(f"toolbox_music_starter_curated_count={len(payload['curated'])}")
print("toolbox_music_starter_favorites=" + ";".join(row["path"] for row in payload["favorites"]))
print("toolbox_music_starter_curated=" + ";".join(row["path"] for row in payload["curated"]))
print("toolbox_music_starter_favorites_manifest=" + str(favorites_out))
print("toolbox_music_starter_curated_manifest=" + str(curated_out))
print("toolbox_music_starter_generation_ready=yes")
print("recommendation=review_generated_starter_manifests_then_copy_into_live_manifests_if_desired")
PY

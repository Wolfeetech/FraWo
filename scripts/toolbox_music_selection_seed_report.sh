#!/usr/bin/env bash
set -euo pipefail

ssh -o BatchMode=yes root@toolbox python3 - <<'PY'
from pathlib import Path
import subprocess

bootstrap = Path("/srv/media-library/music/bootstrap-radio-usb")
candidate_roots = [
    bootstrap / "clean",
    bootstrap / "Contents",
    bootstrap / "Music Locker Radio - Palms Trax (Mixed)",
]

def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())

def size_bytes(path: Path) -> int:
    try:
        out = subprocess.check_output(["du", "-sb", str(path)], text=True).split()[0]
        return int(out)
    except Exception:
        return 0

rows = []
for root in candidate_roots:
    if not root.exists():
        continue
    if root.is_dir():
        children = sorted(root.iterdir())
    else:
        children = [root]
    for child in children:
        if not child.exists():
            continue
        rel = child.relative_to(bootstrap)
        files = count_files(child) if child.is_dir() else 1
        if files == 0:
            continue
        rows.append((size_bytes(child), files, rel.as_posix()))

rows.sort(reverse=True)
top = rows[:25]

print(f"toolbox_music_seed_candidate_count={len(rows)}")
print("toolbox_music_seed_top_candidates=" + ";".join(
    f"{rel}|files={files}|bytes={size}" for size, files, rel in top
))

if top:
    print("toolbox_music_seed_report_ready=yes")
    print("recommendation=use_top_candidates_to_fill_favorites_and_curated_manifests")
else:
    print("toolbox_music_seed_report_ready=no")
    print("recommendation=wait_for_bootstrap_music_seed")
PY

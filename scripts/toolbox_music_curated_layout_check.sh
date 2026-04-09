#!/usr/bin/env bash
set -euo pipefail

ssh -o BatchMode=yes root@toolbox python3 - <<'PY'
from pathlib import Path

root = Path("/srv/media-library/music")
paths = {
    "network": Path("/srv/media-library/music-network/yourparty_Libary"),
    "curated": root / "curated",
    "favorites": root / "favorites",
    "inbox": root / "inbox",
}
quarantine = Path("/srv/media-library/quarantine/bootstrap-review")

def file_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())

def symlink_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_symlink())

def dir_state(path: Path) -> str:
    return "present" if path.exists() else "missing"

for key, path in paths.items():
    print(f"toolbox_music_layout_{key}_state={dir_state(path)}")
    print(f"toolbox_music_layout_{key}_file_count={file_count(path)}")
    print(f"toolbox_music_layout_{key}_symlink_count={symlink_count(path)}")

print(f"toolbox_music_layout_quarantine_state={dir_state(quarantine)}")
print(f"toolbox_music_layout_quarantine_file_count={file_count(quarantine)}")
print(f"toolbox_music_layout_quarantine_symlink_count={symlink_count(quarantine)}")

network_files = file_count(paths["network"])
curated_files = file_count(paths["curated"])
favorites_files = file_count(paths["favorites"])
curated_links = symlink_count(paths["curated"])
favorites_links = symlink_count(paths["favorites"])

if network_files > 0 and (curated_files > 0 or curated_links > 0 or favorites_files > 0 or favorites_links > 0):
    print("toolbox_music_curated_layout_ready=yes")
    print("recommendation=starter_selection_is_live_refine_favorites_and_curated_over_time")
elif network_files > 0 and curated_files == 0 and favorites_files == 0 and curated_links == 0 and favorites_links == 0:
    print("toolbox_music_curated_layout_ready=yes")
    print("recommendation=begin_first_curated_and_favorites_selection_from_network_media_seed")
else:
    print("toolbox_music_curated_layout_ready=no")
    print("recommendation=wait_for_network_media_seed")
PY

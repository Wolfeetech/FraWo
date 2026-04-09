#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAVORITES_MANIFEST="${ROOT_DIR}/manifests/media/favorites_paths.txt"
CURATED_MANIFEST="${ROOT_DIR}/manifests/media/curated_paths.txt"

selection_json="$(
  FAVORITES_MANIFEST="${FAVORITES_MANIFEST}" CURATED_MANIFEST="${CURATED_MANIFEST}" python3 - <<'PY'
import json
import os
from pathlib import Path

def load_manifest(path_str: str):
    path = Path(path_str)
    if not path.exists():
        return []
    entries = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries

payload = {
    "favorites": load_manifest(os.environ["FAVORITES_MANIFEST"]),
    "curated": load_manifest(os.environ["CURATED_MANIFEST"]),
}
print(json.dumps(payload))
PY
)"

selection_json_b64="$(
  SELECTION_JSON="${selection_json}" python3 - <<'PY'
import base64
import os

print(base64.b64encode(os.environ["SELECTION_JSON"].encode("utf-8")).decode("ascii"))
PY
)"

ssh -o BatchMode=yes root@toolbox "SELECTION_JSON_B64='${selection_json_b64}' python3 -" <<'PY'
import base64
import json
import os
from pathlib import Path

selection = json.loads(base64.b64decode(os.environ["SELECTION_JSON_B64"]).decode("utf-8"))
bootstrap_root = Path("/srv/media-library/music-network/yourparty_Libary")
dest_roots = {
    "favorites": Path("/srv/media-library/music/favorites"),
    "curated": Path("/srv/media-library/music/curated"),
}
state_path = Path("/srv/media-library/music/.selection_state.json")

for path in dest_roots.values():
    path.mkdir(parents=True, exist_ok=True)

if state_path.exists():
    try:
        previous = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        previous = {"favorites": [], "curated": []}
else:
    previous = {"favorites": [], "curated": []}

removed = []
created = []
missing = []
conflicts = []

def prune_empty_dirs(root: Path):
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()

for bucket, dest_root in dest_roots.items():
    desired = set(selection.get(bucket, []))
    old = set(previous.get(bucket, []))

    for rel in sorted(old - desired):
        target = dest_root / rel
        if target.is_symlink():
            target.unlink()
            removed.append(f"{bucket}:{rel}")

    prune_empty_dirs(dest_root)

    for rel in sorted(desired):
        src = bootstrap_root / rel
        dst = dest_root / rel
        if not src.exists():
            missing.append(f"{bucket}:{rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() or dst.is_symlink():
            if dst.is_symlink():
                current = os.readlink(dst)
                if current == str(src):
                    continue
                dst.unlink()
            else:
                conflicts.append(f"{bucket}:{rel}")
                continue
        dst.symlink_to(src)
        created.append(f"{bucket}:{rel}")

state_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")

print(f"toolbox_music_selection_favorites_requested={len(selection.get('favorites', []))}")
print(f"toolbox_music_selection_curated_requested={len(selection.get('curated', []))}")
print(f"toolbox_music_selection_created_count={len(created)}")
print(f"toolbox_music_selection_removed_count={len(removed)}")
print(f"toolbox_music_selection_missing_count={len(missing)}")
print(f"toolbox_music_selection_conflict_count={len(conflicts)}")
print(f"toolbox_music_selection_sample_created={';'.join(created[:20])}")
print(f"toolbox_music_selection_sample_removed={';'.join(removed[:20])}")
print(f"toolbox_music_selection_sample_missing={';'.join(missing[:20])}")
print(f"toolbox_music_selection_sample_conflicts={';'.join(conflicts[:20])}")

if not missing and not conflicts:
    print("toolbox_music_selection_sync_ready=yes")
    if selection.get("favorites") or selection.get("curated"):
        print("recommendation=refresh_jellyfin_and_validate_curated_views")
    else:
        print("recommendation=edit_manifests_then_sync_first_favorites_and_curated_selection")
else:
    print("toolbox_music_selection_sync_ready=no")
    print("recommendation=fix_missing_or_conflicting_manifest_paths_before_selection_rollout")
PY

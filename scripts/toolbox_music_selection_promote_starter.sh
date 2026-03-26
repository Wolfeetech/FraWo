#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEN_DIR="${ROOT_DIR}/manifests/media/generated"
LIVE_DIR="${ROOT_DIR}/manifests/media"

copy_manifest() {
  local src="$1"
  local dest="$2"
  local title="$3"
  python3 - "$src" "$dest" "$title" <<'PY'
from pathlib import Path
import sys

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
title = sys.argv[3]

if not src.exists():
    raise SystemExit(f"missing generated manifest: {src}")

entries = []
for raw in src.read_text(encoding="utf-8", errors="replace").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    entries.append(line)

header = [
    f"# {title}",
    "# Promoted from the generated starter manifest.",
    "# Relative paths under /srv/media-library/music-network/yourparty_Libary",
    "",
]
dest.write_text("\n".join(header + entries) + "\n", encoding="utf-8")
print(f"{dest}={len(entries)}")
PY
}

copy_manifest "${GEN_DIR}/favorites_starter.txt" "${LIVE_DIR}/favorites_paths.txt" "Favorites live manifest"
copy_manifest "${GEN_DIR}/curated_starter.txt" "${LIVE_DIR}/curated_paths.txt" "Curated live manifest"

echo "toolbox_music_selection_promote_starter_ready=yes"
echo "recommendation=run_toolbox_music_selection_sync_to_materialize_starter_selection"

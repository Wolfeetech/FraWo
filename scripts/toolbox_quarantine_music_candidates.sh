#!/usr/bin/env bash
set -euo pipefail

ssh -o BatchMode=yes root@toolbox python3 - <<'PY'
from pathlib import Path
import shutil

music_root = Path("/srv/media-library/music-network/yourparty_Libary")
quarantine_root = Path("/srv/media-library/quarantine/bootstrap-review")
exclude_file = Path("/etc/homeserver2027/media-sync-excludes.txt")

allowed_audio = {
    "mp3", "flac", "wav", "m4a", "aac", "ogg", "opus", "aiff", "aif", "alac", "wma"
}
allowed_sidecar = {
    "jpg", "jpeg", "png", "gif", "webp", "nfo", "m3u", "m3u8", "pls", "txt", "log", "cue", "pdf"
}

music_root.mkdir(parents=True, exist_ok=True)
quarantine_root.mkdir(parents=True, exist_ok=True)
exclude_file.parent.mkdir(parents=True, exist_ok=True)
exclude_file.touch(exist_ok=True)

existing = {
    line.strip()
    for line in exclude_file.read_text(encoding="utf-8", errors="replace").splitlines()
    if line.strip() and not line.strip().startswith("#")
}

all_files = [p for p in music_root.rglob("*") if p.is_file()]
suspicious = []
for path in all_files:
    suffix = path.suffix.lower().lstrip(".")
    if suffix in allowed_audio or suffix in allowed_sidecar:
        continue
    suspicious.append(path)

moved = []
recorded = []

for src in suspicious:
    rel = src.relative_to(music_root)
    rel_text = rel.as_posix()
    target = quarantine_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.move(str(src), str(target))
        moved.append(f"{src} -> {target}")
    if rel_text not in existing:
        existing.add(rel_text)
        recorded.append(rel_text)

exclude_file.write_text(
    "# Excluded from Pi-to-toolbox bootstrap sync because the files were quarantined for review.\n"
    + "\n".join(sorted(existing))
    + ("\n" if existing else ""),
    encoding="utf-8",
)

print(f"toolbox_music_quarantine_moved_count={len(moved)}")
print(f"toolbox_music_quarantine_recorded_excludes={len(recorded)}")
print(f"toolbox_music_quarantine_exclude_file={exclude_file}")
print(f"toolbox_music_quarantine_root={quarantine_root}")
print(f"toolbox_music_quarantine_sample_moves={';'.join(moved[:20])}")

if moved or recorded:
    print("toolbox_music_quarantine_ready=yes")
    print("recommendation=redeploy_media_sync_then_continue_curated_music_rollout")
else:
    print("toolbox_music_quarantine_ready=yes")
    print("recommendation=no_new_suspicious_files_to_quarantine")
PY

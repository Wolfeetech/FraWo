#!/usr/bin/env bash
set -euo pipefail

ssh -o BatchMode=yes root@toolbox python3 - <<'PY'
from pathlib import Path

music_root = Path("/srv/media-library/music/bootstrap-radio-usb")
quarantine_root = Path("/srv/media-library/quarantine/bootstrap-review")

allowed_audio = {
    "mp3", "flac", "wav", "m4a", "aac", "ogg", "opus", "aiff", "aif", "alac", "wma"
}
allowed_sidecar = {
    "jpg", "jpeg", "png", "gif", "webp", "nfo", "m3u", "m3u8", "pls", "txt", "log", "cue", "pdf"
}

all_files = [p for p in music_root.rglob("*") if p.is_file()] if music_root.exists() else []
suspicious = []
sidecars = []

for path in all_files:
    suffix = path.suffix.lower().lstrip(".")
    if suffix in allowed_audio:
        continue
    if suffix in allowed_sidecar:
        sidecars.append(path)
        continue
    suspicious.append(path)

def proposed_target(src: Path) -> str:
    relative = src.relative_to(music_root)
    return str(quarantine_root / relative)

sample_moves = [f"{src} -> {proposed_target(src)}" for src in suspicious[:20]]
sample_sidecars = [str(p) for p in sidecars[:20]]

print(f"toolbox_music_curation_candidate_count={len(suspicious)}")
print(f"toolbox_music_curation_sidecar_count={len(sidecars)}")
print(f"toolbox_music_curation_quarantine_root={quarantine_root}")
print(f"toolbox_music_curation_sample_moves={';'.join(sample_moves)}")
print(f"toolbox_music_curation_sample_sidecars={';'.join(sample_sidecars)}")

if suspicious:
    print("toolbox_music_curation_candidates_ready=yes")
    print("recommendation=quarantine_suspicious_files_before_curated_music_rollout")
else:
    print("toolbox_music_curation_candidates_ready=yes")
    print("recommendation=keep_sidecars_and_continue_curated_music_rollout")
PY

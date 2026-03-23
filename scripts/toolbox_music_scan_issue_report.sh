#!/usr/bin/env bash
set -euo pipefail

ssh -o BatchMode=yes root@toolbox python3 - <<'PY'
from collections import Counter
from pathlib import Path

music_root = Path("/srv/media-library/music")
log_root = Path("/srv/jellyfin/config/log")

allowed_audio = {
    "mp3", "flac", "wav", "m4a", "aac", "ogg", "opus", "aiff", "aif", "alac", "wma"
}
allowed_sidecar = {
    "jpg", "jpeg", "png", "gif", "webp", "nfo", "m3u", "m3u8", "pls", "txt", "log", "cue", "pdf"
}

all_files = [p for p in music_root.rglob("*") if p.is_file()] if music_root.exists() else []
ext_counter = Counter()
non_audio = []
suspicious = []

for path in all_files:
    suffix = path.suffix.lower().lstrip(".")
    ext_counter[suffix or "[no_ext]"] += 1
    if suffix in allowed_audio:
        continue
    if suffix in allowed_sidecar:
        non_audio.append(path)
        continue
    suspicious.append(path)

log_text = ""
ffprobe_failures = 0
if log_root.exists():
    logs = sorted(log_root.glob("log_*.log"))
    if logs:
        tail_log = logs[-1]
        try:
            log_text = tail_log.read_text(encoding="utf-8", errors="replace")
        except Exception:
            log_text = ""
        ffprobe_failures = log_text.count("ffprobe failed - streams and format are both null")

permj5 = [str(p) for p in all_files if p.name.endswith(".peRmj5")]
sample_suspicious = [str(p) for p in suspicious[:20]]
sample_non_audio = [str(p) for p in non_audio[:20]]

top_ext = ",".join(f"{ext}={count}" for ext, count in ext_counter.most_common(12))
print(f"toolbox_music_scan_total_files={len(all_files)}")
print(f"toolbox_music_scan_ffprobe_failure_count={ffprobe_failures}")
print(f"toolbox_music_scan_non_audio_file_count={len(non_audio)}")
print(f"toolbox_music_scan_suspicious_file_count={len(suspicious)}")
print(f"toolbox_music_scan_permj5_count={len(permj5)}")
print(f"toolbox_music_scan_top_extensions={top_ext}")
print(f"toolbox_music_scan_sample_suspicious={';'.join(sample_suspicious)}")
print(f"toolbox_music_scan_sample_non_audio={';'.join(sample_non_audio)}")
print(f"toolbox_music_scan_sample_permj5={';'.join(permj5[:20])}")

if ffprobe_failures == 0 and len(suspicious) == 0:
    print("toolbox_music_scan_issue_report_ready=yes")
    print("recommendation=music_library_scan_is_clean")
elif len(suspicious) == 0:
    print("toolbox_music_scan_issue_report_ready=yes")
    print("recommendation=no_current_quarantine_candidates_keep_historical_ffprobe_warnings_in_mind")
else:
    print("toolbox_music_scan_issue_report_ready=yes")
    print("recommendation=review_ffprobe_failures_and_suspicious_music_files_before_curated_rollout")
PY

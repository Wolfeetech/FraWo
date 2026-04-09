import os
import subprocess
import json
from pathlib import Path

SOURCE_ROOT = "/srv/media-library/music-network/yourparty_Libary"
OUTPUT_FILE = "/srv/media-library/music_metadata_harvest.json"
LOG_FILE = "/srv/media-library/music_harvest.log"

def get_metadata(file_path):
    try:
        cmd = [
            "ffprobe", 
            "-v", "quiet", 
            "-print_format", "json", 
            "-show_format", 
            "-show_streams", 
            str(file_path)
        ]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}

def harvest():
    files = []
    for root, _, filenames in os.walk(SOURCE_ROOT):
        for f in filenames:
            if f.lower().endswith(('.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.aif', '.aiff')):
                files.append(os.path.join(root, f))
    
    total = len(files)
    with open(LOG_FILE, "w") as log:
        log.write(f"Starting harvest of {total} files...\n")
    
    results = []
    for i, f in enumerate(files):
        meta = get_metadata(f)
        rel_path = os.path.relpath(f, SOURCE_ROOT)
        
        format_info = meta.get("format", {})
        tags = format_info.get("tags", {})
        
        if not tags and meta.get("streams"):
            for s in meta["streams"]:
                if s.get("tags"):
                    tags = s["tags"]
                    break
        
        entry = {
            "path": rel_path,
            "abs_path": f,
            "size": os.path.getsize(f),
            "bitrate": format_info.get("bit_rate"),
            "duration": format_info.get("duration"),
            "artist": tags.get("artist") or tags.get("ARTIST"),
            "album": tags.get("album") or tags.get("ALBUM"),
            "title": tags.get("title") or tags.get("TITLE"),
            "comment": tags.get("comment") or tags.get("COMMENT"),
            "tags": tags
        }
        
        results.append(entry)
        
        if (i + 1) % 100 == 0:
            msg = f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)\n"
            with open(LOG_FILE, "a") as log:
                log.write(msg)
            # Intermediate save
            with open(OUTPUT_FILE, "w") as f_out:
                json.dump(results, f_out, indent=2)

    with open(OUTPUT_FILE, "w") as f_out:
        json.dump(results, f_out, indent=2)
    with open(LOG_FILE, "a") as log:
        log.write("Harvest complete.\n")

if __name__ == '__main__':
    harvest()

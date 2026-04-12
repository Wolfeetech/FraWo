import os, subprocess, json
SOURCE_ROOT = "/srv/media-library/music-network/yourparty_Libary"
OUTPUT_FILE = "/srv/media-library/music_metadata_harvest.json"
def harvest():
    files = [os.path.join(r, f) for r, _, fs in os.walk(SOURCE_ROOT) for f in fs if f.lower().endswith(('.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.aif', '.aiff'))]
    results = []
    print(f"Harvesting {len(files)} files...")
    for i, f in enumerate(files):
        try:
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", f]
            meta = json.loads(subprocess.check_output(cmd).decode('utf-8'))
            results.append({"path": os.path.relpath(f, SOURCE_ROOT), "meta": meta})
        except: pass
        if (i+1) % 500 == 0: print(f"Progress: {i+1}")
    with open(OUTPUT_FILE, "w") as f_out: json.dump(results, f_out, indent=2)
if __name__ == '__main__': harvest()

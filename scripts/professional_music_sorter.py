#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import shutil
import mutagen
import re

sys.stdout.reconfigure(encoding='utf-8')

def get_tag(tags, keys):
    for key in keys:
        if key in tags:
            val = tags[key]
            if isinstance(val, list) and val:
                return val[0]
            return str(val)
    return None

def sanitize_filename(name):
    # Remove invalid chars for windows/linux
    invalid = '<>:"/\\|?*'
    for c in invalid:
        name = name.replace(c, '_')
    return name.strip()

def parse_filename(filename):
    parts = filename.split(" - ")
    if len(parts) >= 2:
        artist = parts[0].strip()
        title = " - ".join(parts[1:]).strip()
        
        # Remove date from artist if present
        artist = re.sub(r"^\d{4}-\d{2}-\d{2}\s+", "", artist)
        
        # Remove label from title if present
        title = re.sub(r"\s+\[.*\]$", "", title)
        
        return artist, title
    
    return None, None

def sort_music(source_dir, target_dir):
    source = Path(source_dir)
    target = Path(target_dir)
    
    needs_tagging = target / "_Needs_Tagging"
    sorted_dir = target / "_Sorted"
    
    needs_tagging.mkdir(parents=True, exist_ok=True)
    sorted_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Scanning {source}...")
    
    for file_path in source.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.mp3', '.flac', '.wav', '.m4a', '.aac']:
            print(f"Processing: {file_path.name.encode('ascii', 'backslashreplace').decode('ascii')}")
            try:
                audio = mutagen.File(file_path)
                if audio is None:
                    print(f"  Could not read tags (unsupported or corrupt): {file_path.name!r}")
                    shutil.copy(file_path, needs_tagging / file_path.name)
                    continue
                
                tags = audio.tags
                if tags is None:
                    print(f"  No tags found: {file_path.name!r}")
                    shutil.copy(file_path, needs_tagging / file_path.name)
                    continue
                
                # Try to get Artist, Title, Genre
                artist = get_tag(tags, ['artist', 'ARTIST', 'TPE1'])
                title = get_tag(tags, ['title', 'TITLE', 'TIT2'])
                genre = get_tag(tags, ['genre', 'GENRE', 'TCON'])
                
                if not artist or not title:
                    print(f"  Missing Artist or Title in tags. Trying filename fallback for: {file_path.stem!r}")
                    artist, title = parse_filename(file_path.stem)
                    print(f"  Fallback result: Artist: {artist!r}, Title: {title!r}")
                    if not artist or not title:
                        print(f"  Fallback failed. Moving to needs_tagging.")
                        shutil.copy(file_path, needs_tagging / file_path.name)
                        continue
                    print(f"  Fallback succeeded: {artist} - {title}")
                
                genre = sanitize_filename(genre or "Unknown_Genre")
                artist = sanitize_filename(artist)
                title = sanitize_filename(title)
                
                # Professional naming: Artist - Title.ext
                new_filename = f"{artist} - {title}{file_path.suffix}"
                
                # Professional structure: Genre/Artist/
                dest_dir = sorted_dir / genre / artist
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                dest_path = dest_dir / new_filename
                
                if dest_path.exists():
                    print(f"  Duplicate target path: {dest_path.name!r}. Skipping or appending ID.")
                    # In a professional system, we might check file hashes or append a unique ID.
                    # Here we just append a counter.
                    counter = 1
                    while dest_path.exists():
                        new_filename = f"{artist} - {title}_{counter}{file_path.suffix}"
                        dest_path = dest_dir / new_filename
                        counter += 1
                
                print(f"  Moving to: {dest_path!r}")
                # We use copy instead of move to be safe during testing!
                shutil.copy(file_path, dest_path)
                
            except Exception as e:
                print(f"  Error processing {file_path.name!r}: {e!r}")
                shutil.copy(file_path, needs_tagging / file_path.name)

def main():
    if len(sys.argv) < 3:
        print("Usage: python professional_music_sorter.py <source_dir> <target_dir>")
        print("Example: python professional_music_sorter.py C:\\Users\\StudioPC\\Music\\Nicotine C:\\Users\\StudioPC\\Music\\Sorted")
        return 1
        
    source = sys.argv[1]
    target = sys.argv[2]
    
    sort_music(source, target)
    print("Sorting completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

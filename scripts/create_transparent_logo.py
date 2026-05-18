#!/usr/bin/env python3
"""Create transparent logo from 1.png"""
from PIL import Image
from pathlib import Path

source_path = Path(r'C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\brand_assets\1.png')
dest_path = Path(r'C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\brand_assets\logo_transparent.png')

if not source_path.exists():
    print(f"[FAIL] Source file not found: {source_path}")
    exit(1)

img = Image.open(source_path).convert('RGBA')
data = img.getdata()

newData = []
for item in data:
    # item is a tuple (R, G, B, A)
    # If it is close to white, make it transparent
    if item[0] > 220 and item[1] > 220 and item[2] > 220:
        newData.append((0, 0, 0, 0)) # Transparent
    else:
        newData.append(item) # Keep original color!

img.putdata(newData)
img.save(dest_path, "PNG")

print(f"[OK] Transparent logo saved to {dest_path}")

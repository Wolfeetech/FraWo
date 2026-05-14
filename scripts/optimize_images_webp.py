#!/usr/bin/env python3
"""Optimize FraWo images and create WebP versions"""
import os, sys, xmlrpc.client, base64
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

# Image IDs from status doc
IMAGES = {
    993: {'name': 'hero-bodensee.jpg', 'usage': 'Hero section'},
    994: {'name': 'service-ton.jpg', 'usage': 'unused'},
    995: {'name': 'service-stage.jpg', 'usage': 'Stage Service card + Projects'},
    996: {'name': 'sonderbau-holz.jpg', 'usage': 'Sonderbauten card + Projects'},
    997: {'name': 'rave-on-sup.jpg', 'usage': 'Projects section'},
    998: {'name': 'buehne-traverse.jpg', 'usage': 'Über Uns section'},
    999: {'name': 'fussballdart.jpg', 'usage': 'Verleih card'},
    1000: {'name': 'mikrofon-ton.jpg', 'usage': 'Licht & Ton card'},
}

def optimize_image(image_data, max_width=1920, quality=85):
    """Optimize image: resize if needed, compress"""
    try:
        img = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # Resize if too large
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"    Resized to {max_width}×{new_height}")

        # Save as JPEG
        output_jpg = io.BytesIO()
        img.save(output_jpg, format='JPEG', quality=quality, optimize=True)
        jpg_data = output_jpg.getvalue()
        jpg_size = len(jpg_data)

        # Save as WebP
        output_webp = io.BytesIO()
        img.save(output_webp, format='WEBP', quality=quality, method=6)
        webp_data = output_webp.getvalue()
        webp_size = len(webp_data)

        print(f"    JPG: {jpg_size/1024:.1f}KB | WebP: {webp_size/1024:.1f}KB (saved {(1-webp_size/jpg_size)*100:.1f}%)")

        return jpg_data, webp_data

    except Exception as e:
        print(f"    [ERROR] Optimization failed: {e}")
        return None, None

def main():
    """Download, optimize, and re-upload images"""

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        sys.exit(1)

    print(f"[OK] Authenticated (UID: {uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    for img_id, info in IMAGES.items():
        if info['usage'] == 'unused':
            print(f"\n[SKIP] Image {img_id} ({info['name']}) - unused")
            continue

        print(f"\n[*] Processing Image {img_id}: {info['name']}")
        print(f"    Usage: {info['usage']}")

        try:
            # Download current image
            attachment = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.attachment', 'read',
                [[img_id], ['datas', 'name', 'mimetype']]
            )

            if not attachment:
                print(f"    [ERROR] Image not found!")
                continue

            attachment = attachment[0]
            original_data = base64.b64decode(attachment['datas'])
            original_size = len(original_data)
            print(f"    Original: {original_size/1024:.1f}KB")

            # Optimize
            jpg_data, webp_data = optimize_image(original_data)

            if not jpg_data:
                print(f"    [ERROR] Optimization failed!")
                continue

            # Update existing JPG (optimized)
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.attachment', 'write',
                [[img_id], {
                    'datas': base64.b64encode(jpg_data).decode('utf-8'),
                }]
            )
            print(f"    [OK] Updated optimized JPG (ID: {img_id})")

            # Create WebP version
            webp_name = info['name'].replace('.jpg', '.webp')
            webp_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.attachment', 'create',
                [{
                    'name': webp_name,
                    'type': 'binary',
                    'datas': base64.b64encode(webp_data).decode('utf-8'),
                    'mimetype': 'image/webp',
                    'public': True,
                    'res_model': 'ir.ui.view',
                }]
            )
            print(f"    [OK] Created WebP version (ID: {webp_id})")

        except Exception as e:
            print(f"    [ERROR] {e}")
            continue

    print("\n[OK] Image optimization complete!")
    print("\nNext steps:")
    print("1. Update HTML to use <picture> element with WebP + JPG fallback")
    print("2. Test website performance")

if __name__ == '__main__':
    try:
        from PIL import Image
    except ImportError:
        print("[FAIL] PIL (Pillow) not installed!")
        print("Install with: pip install Pillow")
        sys.exit(1)

    main()

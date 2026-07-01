#!/usr/bin/env python3
"""Crop rigg image to remove extras at bottom"""
import os, sys, xmlrpc.client, base64
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

IMAGE_ID = 998  # buehne-traverse.jpg

def crop_image(image_data, crop_bottom_percent=20):
    """Crop bottom 20% of image to remove extras"""
    try:
        img = Image.open(io.BytesIO(image_data))

        width, height = img.size
        crop_pixels = int(height * crop_bottom_percent / 100)

        # Crop: left, top, right, bottom
        # Remove bottom portion
        cropped = img.crop((0, 0, width, height - crop_pixels))

        print(f"    Original size: {width}×{height}")
        print(f"    Cropped {crop_pixels}px from bottom ({crop_bottom_percent}%)")
        print(f"    New size: {cropped.width}×{cropped.height}")

        # Save as JPEG
        output_jpg = io.BytesIO()
        cropped.save(output_jpg, format='JPEG', quality=85, optimize=True)
        jpg_data = output_jpg.getvalue()

        # Save as WebP
        output_webp = io.BytesIO()
        cropped.save(output_webp, format='WEBP', quality=85, method=6)
        webp_data = output_webp.getvalue()

        return jpg_data, webp_data

    except Exception as e:
        print(f"    [ERROR] Cropping failed: {e}")
        return None, None

def main():
    """Download, crop, and re-upload rigg image"""

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        sys.exit(1)

    print(f"[OK] Authenticated (UID: {uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print(f"\n[*] Processing Image {IMAGE_ID}: buehne-traverse.jpg")
    print(f"    Removing extras/komparsen from bottom...")

    try:
        # Download current image
        attachment = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'read',
            [[IMAGE_ID], ['datas', 'name']]
        )

        if not attachment:
            print(f"    [ERROR] Image not found!")
            sys.exit(1)

        attachment = attachment[0]
        original_data = base64.b64decode(attachment['datas'])

        # Crop image
        jpg_data, webp_data = crop_image(original_data, crop_bottom_percent=25)

        if not jpg_data:
            print(f"    [ERROR] Cropping failed!")
            sys.exit(1)

        # Update existing JPG
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'write',
            [[IMAGE_ID], {
                'datas': base64.b64encode(jpg_data).decode('utf-8'),
            }]
        )
        print(f"    [OK] Updated cropped JPG (ID: {IMAGE_ID})")

        # Update WebP version (ID: 1007)
        webp_id = 1007
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'write',
            [[webp_id], {
                'datas': base64.b64encode(webp_data).decode('utf-8'),
            }]
        )
        print(f"    [OK] Updated cropped WebP (ID: {webp_id})")

    except Exception as e:
        print(f"    [ERROR] {e}")
        sys.exit(1)

    print("\n[OK] Image cropped successfully!")
    print("Komparsen at bottom removed, focus on Franz on rigg.")

if __name__ == '__main__':
    try:
        from PIL import Image
    except ImportError:
        print("[FAIL] PIL (Pillow) not installed!")
        sys.exit(1)

    main()

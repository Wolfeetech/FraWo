#!/usr/bin/env python3
"""Upload New Images to Odoo"""
import os, sys, base64, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

images = {
    'PXL_20260418_131357817.jpg': 'Fußballdart 3x5m Verleih',
    'PXL_20260507_095849011.PORTRAIT.jpg': 'Mikrofon Tontechnik Studio',
}

downloads_dir = Path.home() / 'Downloads'

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

uploaded = {}

for filename, name in images.items():
    filepath = downloads_dir / filename

    with open(filepath, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Create ir.attachment
    attachment_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.attachment', 'create', [{
        'name': name,
        'type': 'binary',
        'datas': image_data,
        'res_model': 'ir.ui.view',
        'mimetype': 'image/jpeg',
        'public': True,
    }])

    uploaded[filename] = attachment_id
    print(f"[OK] {filename} -> ID:{attachment_id}")

print(f"\n[OK] {len(uploaded)} images uploaded")
print("\nOdoo Image URLs:")
for fname, aid in uploaded.items():
    print(f"  /web/image/{aid}/{fname}")

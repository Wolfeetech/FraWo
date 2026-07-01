#!/usr/bin/env python3
"""Upload Images to Odoo"""
import os, sys, base64, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_RPC_URL', os.getenv('ODOO_URL', 'http://10.1.0.112:8069'))
ODOO_DB = os.getenv('ODOO_RPC_DB', os.getenv('ODOO_DB', 'FraWo_GbR'))
ODOO_USER = os.getenv('ODOO_RPC_USER', os.getenv('ODOO_USER'))
ODOO_SECRET = os.getenv('ODOO_RPC_API_KEY')

if not all([ODOO_URL, ODOO_DB, ODOO_USER, ODOO_SECRET]):
    raise SystemExit("Missing ODOO_RPC_URL/ODOO_RPC_DB/ODOO_RPC_USER/ODOO_RPC_API_KEY")

images = {
    'hero-bodensee.jpg': 'Bodensee Beach Event',
    'service-ton.jpg': 'Line Array Setup Bodensee',
    'service-stage.jpg': 'Live Event Stage',
    'sonderbau-holz.jpg': 'Holzkonstruktion Sonderbau',
    'rave-on-sup.jpg': 'Rave on SUP Bodensee',
    'buehne-traverse.jpg': 'Bühnenaufbau Traverse',
}

img_dir = Path.home() / 'Downloads' / 'FraWo_Website_Images'

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_SECRET, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

uploaded = {}

for filename, name in images.items():
    filepath = img_dir / filename

    with open(filepath, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Create ir.attachment
    attachment_id = models.execute_kw(ODOO_DB, uid, ODOO_SECRET, 'ir.attachment', 'create', [{
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

#!/usr/bin/env python3
"""Upload real attached images to Odoo"""
import os, sys, base64, xmlrpc.client
from pathlib import Path

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

dirpath = Path(r'C:\Users\StudioPC\.gemini\antigravity\brain\3e87f07a-f13e-4c85-baf6-2bde80e7f0fa')

filenames = [
    'media__1779088600750.jpg',
    'media__1779088604043.jpg'
]

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

for filename in filenames:
    filepath = dirpath / filename
    if not filepath.exists():
        print(f"[WARN] File not found: {filename}")
        continue
        
    with open(filepath, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    attachment_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.attachment', 'create', [{
        'name': f'Real Image {filename[-10:-4]}',
        'type': 'binary',
        'datas': image_data,
        'res_model': 'ir.ui.view',
        'mimetype': 'image/jpeg',
        'public': True,
    }])

    print(f"[OK] {filename} -> ID:{attachment_id}")

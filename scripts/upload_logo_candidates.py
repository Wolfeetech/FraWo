#!/usr/bin/env python3
"""Upload logo candidates from brand_assets to Odoo"""
import os, sys, base64, xmlrpc.client
from pathlib import Path

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

dirpath = Path(r'C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\brand_assets')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

for i in range(1, 7):
    filename = f'{i}.png'
    filepath = dirpath / filename
    if not filepath.exists():
        print(f"[WARN] File not found: {filename}")
        continue
        
    with open(filepath, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    attachment_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.attachment', 'create', [{
        'name': f'Logo Candidate {i}',
        'type': 'binary',
        'datas': image_data,
        'res_model': 'ir.ui.view',
        'mimetype': 'image/png',
        'public': True,
    }])

    print(f"[OK] {filename} -> ID:{attachment_id}")

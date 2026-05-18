#!/usr/bin/env python3
"""Upload ATEM Image to Odoo"""
import os, sys, base64, xmlrpc.client
from pathlib import Path

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

filename = 'media__1779089269428.jpg'
filepath = Path(r'C:\Users\StudioPC\.gemini\antigravity\brain\3e87f07a-f13e-4c85-baf6-2bde80e7f0fa') / filename

if not filepath.exists():
    print(f"[ERROR] File not found: {filepath}")
    sys.exit(1)

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

with open(filepath, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Create ir.attachment
attachment_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.attachment', 'create', [{
    'name': 'ATEM Switcher Streaming',
    'type': 'binary',
    'datas': image_data,
    'res_model': 'ir.ui.view',
    'mimetype': 'image/jpeg',
    'public': True,
}])

print(f"[OK] {filename} -> ID:{attachment_id}")
print(f"Odoo Image URL: /web/image/{attachment_id}/{filename}")

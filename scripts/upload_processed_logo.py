#!/usr/bin/env python3
"""Upload processed transparent logo to Odoo"""
import os, sys, base64, xmlrpc.client
from pathlib import Path

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

filepath = Path(r'C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\brand_assets\logo_transparent.png')

if not filepath.exists():
    print(f"[FAIL] File not found: {filepath}")
    exit(1)

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

with open(filepath, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

attachment_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.attachment', 'create', [{
    'name': 'Logo Transparent White',
    'type': 'binary',
    'datas': image_data,
    'res_model': 'ir.ui.view',
    'mimetype': 'image/png',
    'public': True,
}])

print(f"[OK] Logo uploaded -> ID:{attachment_id}")

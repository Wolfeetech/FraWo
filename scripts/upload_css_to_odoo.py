#!/usr/bin/env python3
"""Upload CSS to Odoo Website"""
import os, sys, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_RPC_URL', os.getenv('ODOO_URL', 'http://10.1.0.112:8069'))
ODOO_DB = os.getenv('ODOO_RPC_DB', os.getenv('ODOO_DB', 'FraWo_GbR'))
ODOO_USER = os.getenv('ODOO_RPC_USER', os.getenv('ODOO_USER'))
ODOO_SECRET = os.getenv('ODOO_RPC_API_KEY')

if not all([ODOO_URL, ODOO_DB, ODOO_USER, ODOO_SECRET]):
    raise SystemExit("Missing ODOO_RPC_URL/ODOO_RPC_DB/ODOO_RPC_USER/ODOO_RPC_API_KEY")

css_path = Path(__file__).parent.parent / 'Codex' / 'website' / 'frawo_custom_css.css'

with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_SECRET, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Find website
websites = models.execute_kw(ODOO_DB, uid, ODOO_SECRET, 'website', 'search_read', [[]], {'fields': ['id', 'name'], 'limit': 1})
website_id = websites[0]['id']

# Wrap CSS in style tag
css_wrapped = f"<style>\n{css_content}\n</style>"

# Update website custom code
models.execute_kw(ODOO_DB, uid, ODOO_SECRET, 'website', 'write', [[website_id], {'custom_code_head': css_wrapped}])

print(f"[OK] CSS uploaded to website {website_id}")

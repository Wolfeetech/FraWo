# -*- coding: utf-8 -*-
import sys
import xmlrpc.client
import json
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search for the view containing the legacy text
legacy_view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [
    [('arch_db', 'ilike', '%Eventtechnik%'), ('active', '=', True)]
])

# Search for header/footer variants
nav_view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [
    ['|', ('key', 'ilike', 'header_standard'), ('key', 'ilike', 'footer_standard'), ('active', '=', True), ('website_id', '=', 1)]
])

results = {
    "legacy_views": models.execute_kw(db, uid, password, 'ir.ui.view', 'read', [legacy_view_ids], {'fields': ['id', 'key', 'name']}),
    "nav_views": models.execute_kw(db, uid, password, 'ir.ui.view', 'read', [nav_view_ids], {'fields': ['id', 'key', 'name']})
}

print(json.dumps(results, indent=2))

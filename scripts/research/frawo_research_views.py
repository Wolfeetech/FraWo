# -*- coding: utf-8 -*-
import xmlrpc.client
import json

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

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

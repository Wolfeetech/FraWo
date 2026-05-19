import os
import xmlrpc.client

URL = os.getenv('ODOO_RPC_URL', 'http://10.4.0.22:8069')
DB = os.getenv('ODOO_RPC_DB', 'FraWo_GbR')
USER = os.getenv('ODOO_RPC_USER', 'admin@frawo-tech.de')
PASSWORD = os.getenv('ODOO_RPC_PASSWORD', 'Anker')

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USER, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

pages = models.execute_kw(DB, uid, PASSWORD, 'website.page', 'search_read', 
    [[['url', '=', '/']]], {'fields': ['id', 'name', 'is_published', 'url']})

if pages:
    page = pages[0]
    print('Found homepage:', page['name'], 'ID:', page['id'], 'Published:', page['is_published'])
    if not page['is_published']:
        models.execute_kw(DB, uid, PASSWORD, 'website.page', 'write', [[page['id']], {'is_published': True}])
        print('Homepage was unpublished. It is now PUBLISHED! ✅')
    else:
        print('Homepage was already published. ✅')
else:
    print('Homepage (/) not found!')

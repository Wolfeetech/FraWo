import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '11Vaudeville!!' # From the .env file!
ODOO_DB = 'FraWo_GbR'

print("[*] Connecting to Odoo at", ODOO_URL)
try:
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if uid:
        print("[OK] Authenticated successfully! UID:", uid)
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        # Just a quick search to verify it works
        partners = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[]], {'limit': 5}
        )
        print("[OK] Connected and fetched partners:", partners)
    else:
        print("[FAIL] Authentication failed")
except Exception as e:
    print("[ERROR]", e)

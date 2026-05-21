import xmlrpc.client
import os

ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    try:
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            print("[FAIL] Authentication failed!")
            return
        print("[OK] Authenticated successfully, UID:", uid)
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Read ALL system parameters
        params = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.config_parameter', 'search_read',
            [[]],
            {'fields': ['key', 'value']}
        )
        print("\n--- All System Parameters ---")
        for p in params:
            print(f"{p['key']}: {p['value']}")

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

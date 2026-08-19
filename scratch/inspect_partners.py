import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

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
        
        # Read partner ID 9 and 14
        partners = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [[['id', 'in', [9, 14]]]],
            {'fields': ['id', 'name', 'email', 'parent_id']}
        )
        print("\n--- Partners Info ---")
        for p in partners:
            print(f"Partner ID {p['id']}: {p['name']} (Email: {p['email']})")

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

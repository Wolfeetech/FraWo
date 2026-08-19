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
        
        # 1. Search in ir.config_parameter
        print("\n[*] Searching in ir.config_parameter...")
        params = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.config_parameter', 'search_read',
            [[['value', 'like', 'notifications']]],
            {'fields': ['key', 'value']}
        )
        for p in params:
            print(f"ir.config_parameter: {p['key']} = {p['value']}")
            
        # 2. Search in res.partner
        print("\n[*] Searching in res.partner...")
        partners = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [[['email', 'like', 'notifications']]],
            {'fields': ['id', 'name', 'email']}
        )
        for pt in partners:
            print(f"res.partner ID {pt['id']}: {pt['name']} = {pt['email']}")
            
        # 3. Search in res.company
        print("\n[*] Searching in res.company...")
        companies = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.company', 'search_read',
            [[['email', 'like', 'notifications']]],
            {'fields': ['id', 'name', 'email']}
        )
        for cp in companies:
            print(f"res.company ID {cp['id']}: {cp['name']} = {cp['email']}")
            
        # 4. Search in res.users
        print("\n[*] Searching in res.users...")
        users = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search_read',
            [[['login', 'like', 'notifications']]],
            {'fields': ['id', 'login', 'name']}
        )
        for us in users:
            print(f"res.users ID {us['id']}: {us['login']} = {us['name']}")

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

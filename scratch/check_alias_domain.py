import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112:8069'
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
        
        # Check if mail.alias.domain model exists
        try:
            fields = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.alias.domain', 'fields_get',
                [],
                {'attributes': ['type']}
            )
            print("[OK] mail.alias.domain model exists! Fields:", list(fields.keys()))
            
            # Search and read records
            records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.alias.domain', 'search_read',
                [[]],
                {}
            )
            print("\n--- mail.alias.domain Records ---")
            for r in records:
                print(r)
        except Exception as e:
            print("[INFO] mail.alias.domain model does NOT exist or failed to query:", e)

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

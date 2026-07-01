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
        
        view_id = 2000
        print(f"[*] Deactivating ir.ui.view with ID {view_id} (website.frawo_radio_footer)...")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.ui.view', 'write',
            [[view_id], {'active': False}]
        )
        print("[OK] View website.frawo_radio_footer has been deactivated!")
        
        # Clear cache to make sure the change propagates
        try:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.qweb', 'clear_caches', [])
            print("[OK] Odoo caches cleared successfully!")
        except Exception as cache_err:
            print("[WARN] Cache clearing failed, might require manual reload:", cache_err)
            
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

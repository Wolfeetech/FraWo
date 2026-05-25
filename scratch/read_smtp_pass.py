import xmlrpc.client
import os

ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

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
        
        # Try to read smtp_pass from ir.mail_server ID 1
        res = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.mail_server', 'search_read',
            [[['id', '=', 1]]],
            {'fields': ['id', 'smtp_user', 'smtp_pass']}
        )
        print(f"Read result: {res}")
            
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

import xmlrpc.client

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Read mail.message ID 1605
    msg = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.message', 'read',
        [[1605]],
        {'fields': ['id', 'email_from', 'reply_to', 'author_id']}
    )[0]
    
    print("\n--- mail.message ID 1605 ---")
    for k, v in sorted(msg.items()):
        print(f"  {k}: {v}")

if __name__ == '__main__':
    main()

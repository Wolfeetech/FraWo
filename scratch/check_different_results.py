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
    
    # Query IDs 312 to 316
    mail_ids = [312, 313, 314, 315, 316]
    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[['id', 'in', mail_ids]]],
        {'fields': ['id', 'state', 'failure_reason', 'email_from']}
    )
    
    print("\n--- Results of From Address Tests ---")
    for m in mails:
        print(f"Mail ID {m['id']}:")
        print(f"  email_from: {m['email_from']}")
        print(f"  state: {m['state']}")
        print(f"  failure_reason: {m['failure_reason']}")
        print("-" * 30)

if __name__ == '__main__':
    main()

import xmlrpc.client

ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

def safe_str(val):
    if isinstance(val, str):
        return val.encode('ascii', errors='replace').decode('ascii')
    return str(val)

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Let's inspect the mail record 307 in detail
    mail = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'read',
        [[307]],
        {}
    )[0]
    
    print("\n--- Mail 307 Detailed Fields ---")
    for k, v in sorted(mail.items()):
        if k not in ['body_html', 'body', 'body_content']:
            print(f"{k}: {safe_str(v)}")
            
if __name__ == '__main__':
    main()

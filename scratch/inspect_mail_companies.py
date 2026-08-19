import xmlrpc.client

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

def safe_str(val):
    if isinstance(val, str):
        return val.encode('ascii', errors='replace').decode('ascii')
    return str(val)

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Read ir.mail_server ID 1 fully
    server = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.mail_server', 'read',
        [[1]],
        {}
    )[0]
    
    print("\n--- ir.mail_server ID 1 ---")
    for k, v in sorted(server.items()):
        if k != 'smtp_pass':
            print(f"  {k}: {safe_str(v)}")
            
    # Read mail 307 and 311 companies and mail_server_ids
    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'read',
        [[307, 311]],
        {'fields': ['id', 'mail_server_id', 'email_from', 'email_to', 'state', 'failure_reason']}
    )
    
    print("\n--- Mail Records ---")
    for m in mails:
        print(f"Mail ID {m['id']}:")
        print(f"  email_from: {safe_str(m['email_from'])}")
        print(f"  email_to: {safe_str(m['email_to'])}")
        print(f"  mail_server_id: {safe_str(m['mail_server_id'])}")
        print(f"  state: {safe_str(m['state'])}")
        print(f"  failure_reason: {safe_str(m['failure_reason'])}")

if __name__ == '__main__':
    main()

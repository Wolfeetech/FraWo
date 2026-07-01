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
    
    # Let's see if we can call _find_mail_server via execute_kw
    senders = [
        'webmaster@frawo-tech.de',
        'wolf@frawo-tech.de',
        'info@frawo-tech.de',
        'notifications@frawo-tech.de',
        'bounce@frawo-tech.de'
    ]
    
    print("\n--- Testing _find_mail_server via RPC ---")
    for s in senders:
        try:
            # Call _find_mail_server
            res = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.mail_server', '_find_mail_server',
                [s]
            )
            print(f"Sender: {s} -> Server ID: {res}")
        except Exception as e:
            print(f"Sender: {s} -> Failed to call _find_mail_server: {e}")

if __name__ == '__main__':
    main()

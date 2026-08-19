import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    try:
        # Get list of databases
        try:
            dbs = common.list()
            print("[OK] Available Databases:", dbs)
        except Exception as list_err:
            print("[WARN] List databases not allowed:", list_err)
            dbs = ['FraWo_GbR', 'FraWo_Live']
            
        for db in dbs:
            print(f"\n--- Checking DB: {db} ---")
            try:
                uid = common.authenticate(db, ODOO_USER, ODOO_PASSWORD, {})
                if uid:
                    print(f"[OK] Authenticated on {db}, UID: {uid}")
                    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
                    
                    # Search for mail servers
                    mail_servers = models.execute_kw(
                        db, uid, ODOO_PASSWORD,
                        'ir.mail_server', 'search_read',
                        [[]],
                        {'fields': ['id', 'name', 'smtp_host', 'smtp_port', 'smtp_user', 'from_filter', 'active']}
                    )
                    print(f"Mail Servers: {mail_servers}")
                    
                    # Search for failed mails
                    failed_messages = models.execute_kw(
                        db, uid, ODOO_PASSWORD,
                        'mail.mail', 'search_read',
                        [[['state', '=', 'exception']]],
                        {'fields': ['id', 'subject', 'email_to', 'email_from', 'failure_reason'], 'limit': 3}
                    )
                    print(f"Failed Messages in {db}:")
                    for m in failed_messages:
                        print(f"  ID: {m['id']} | Subject: {m['subject']} | To: {m['email_to']} | From: {m['email_from']}")
                        print(f"  Failure: {m['failure_reason']}")
                else:
                    print(f"[FAIL] Authentication failed on {db}")
            except Exception as db_err:
                print(f"[ERROR] Failed checking DB {db}: {db_err}")
                
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

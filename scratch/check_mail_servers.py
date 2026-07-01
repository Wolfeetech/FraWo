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
        
        # Search for all outgoing mail servers
        mail_servers = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.mail_server', 'search_read',
            [[]],
            {'fields': ['id', 'name', 'smtp_host', 'smtp_port', 'smtp_user', 'smtp_encryption', 'sequence', 'active']}
        )
        
        print("\n--- Outgoing Mail Servers ---")
        if not mail_servers:
            print("No outgoing mail servers configured!")
        for server in mail_servers:
            print(f"ID: {server['id']}")
            print(f"Name: {server['name']}")
            print(f"Host: {server['smtp_host']}:{server['smtp_port']}")
            print(f"User: {server['smtp_user']}")
            print(f"Encryption: {server['smtp_encryption']}")
            print(f"Sequence: {server['sequence']}")
            print(f"Active: {server['active']}")
            print("-" * 30)
            
            # Let's see if we can trigger a test connection via Odoo models
            try:
                # Odoo ir.mail_server has a method 'test_connection_button' or 'test_connection'
                # Let's try calling 'test_connection' or just see if we can read the password (usually protected, but let's check)
                print(f"[*] Testing connection for server {server['id']}...")
                res = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.mail_server', 'test_connection',
                    [[server['id']]]
                )
                print(f"[RESULT] Test Connection: {res}")
            except Exception as test_err:
                print(f"[WARN] Connection test failed or method not found: {test_err}")
                
        # Let's also check failed mail messages
        failed_messages = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['state', '=', 'exception']]],
            {'fields': ['id', 'subject', 'email_to', 'failure_reason', 'state'], 'limit': 5}
        )
        print("\n--- Failed Mail Messages (Exceptions) ---")
        if not failed_messages:
            print("No failed mail messages in exception state.")
        for msg in failed_messages:
            print(f"ID: {msg['id']}")
            print(f"To: {msg['email_to']}")
            print(f"Subject: {msg['subject']}")
            print(f"Failure Reason: {msg['failure_reason']}")
            print("-" * 30)
            
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

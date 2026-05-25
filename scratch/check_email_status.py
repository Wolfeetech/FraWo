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
        
        # Check specific mail ID 307
        msg = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', '=', 307]]],
            {'fields': ['id', 'state', 'failure_reason', 'email_from', 'email_to']}
        )
        if msg:
            print("\n--- Mail ID 307 Status ---")
            print(f"State: {msg[0]['state']}")
            print(f"From: {msg[0]['email_from']}")
            print(f"To: {msg[0]['email_to']}")
            print(f"Failure Reason: {msg[0]['failure_reason']}")
            print("-" * 30)

        # Check all failed mail messages (exceptions)
        failed_messages = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['state', '=', 'exception']]],
            {'fields': ['id', 'subject', 'email_to', 'email_from', 'failure_reason'], 'limit': 5}
        )
        print("\n--- Current Failed Mail Messages (Exceptions) ---")
        if not failed_messages:
            print("No failed mail messages in exception state!")
        for m in failed_messages:
            print(f"ID: {m['id']} | Subject: {m['subject']} | To: {m['email_to']} | From: {m['email_from']}")
            print(f"Failure Reason: {m['failure_reason']}")
            print("-" * 30)

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

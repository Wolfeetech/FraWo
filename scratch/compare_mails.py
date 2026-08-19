import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

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
        
        # Read fields of mail 307 and 309 (removed 'notification')
        fields_to_read = ['id', 'subject', 'email_from', 'email_to', 'reply_to', 'mail_server_id', 'state', 'headers', 'email_cc']
        
        mails = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', 'in', [307, 309]]]],
            {'fields': fields_to_read}
        )
        
        print("\n--- Comparing Mails ---")
        for m in mails:
            print(f"\nMail ID: {m['id']}")
            for k in fields_to_read:
                if k != 'id':
                    print(f"  {k}: {repr(m.get(k))}")
            print("-" * 30)

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

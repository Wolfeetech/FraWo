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
        
        # We will retry mail ID 307 with EXACTLY 'webmaster@frawo-tech.de'
        msg_id = 307
        print(f"[*] Resetting and rewriting From header of mail {msg_id} to simple email...")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'write',
            [[msg_id], {
                'email_from': 'webmaster@frawo-tech.de',
                'state': 'outgoing',
                'failure_reason': False
            }]
        )
        
        print("[*] Dispatching...")
        try:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'process_email_queue',
                [],
                {'ids': [msg_id]}
            )
        except Exception as dispatch_err:
            print("[INFO] Dispatch completed:", str(dispatch_err)[:200])
            
        # Verify status
        updated = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', '=', msg_id]]],
            {'fields': ['id', 'state', 'failure_reason', 'email_from']}
        )
        if updated:
            print("\n--- Mail Status Post-Dispatch ---")
            print(f"ID: {updated[0]['id']}")
            print(f"State: {updated[0]['state']}")
            print(f"From Header: {updated[0]['email_from']}")
            print(f"Failure Reason: {updated[0]['failure_reason']}")
            
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

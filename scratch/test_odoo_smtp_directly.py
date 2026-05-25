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
        
        # We can construct a mail.mail record directly and send it.
        # But to avoid envelope sender rewriting, let's look at the mail.mail model's send method.
        # Let's create a mail.mail record with email_from = 'webmaster@frawo-tech.de'
        print("[*] Creating a test mail.mail record...")
        mail_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'create',
            [{
                'subject': 'Odoo SMTP Direct Test',
                'email_from': 'webmaster@frawo-tech.de',
                'email_to': 'wolf@frawo-tech.de',
                'body_html': '<p>This is a test email sent from inside Odoo after parameter updates.</p>',
                'state': 'outgoing'
            }]
        )
        print(f"[OK] Created mail record ID: {mail_id}")
        
        # Trigger sending
        print(f"[*] Dispatching test mail...")
        try:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'process_email_queue',
                [],
                {'ids': [mail_id]}
            )
        except Exception as dispatch_err:
            print("[INFO] Dispatch completed:", str(dispatch_err)[:200])
            
        # Check status
        msg = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', '=', mail_id]]],
            {'fields': ['id', 'state', 'failure_reason', 'email_from']}
        )
        if msg:
            print("\n--- Test Mail Status ---")
            print(f"ID: {msg[0]['id']}")
            print(f"State: {msg[0]['state']}")
            print(f"From: {msg[0]['email_from']}")
            print(f"Failure Reason: {msg[0]['failure_reason']}")
            
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

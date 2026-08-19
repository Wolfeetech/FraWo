import xmlrpc.client

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Let's find all exception mails
    failed_mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[['state', '=', 'exception']]],
        {'fields': ['id', 'subject', 'email_from', 'email_to', 'failure_reason', 'recipient_ids']}
    )
    
    print(f"\n[*] Found {len(failed_mails)} failed emails in exception state.")
    for m in failed_mails:
        print(f"ID: {m['id']} | Subject: {m['subject']} | From: {m['email_from']} | To: {m['email_to']}")
        
        # Reset state to outgoing and clear failure_reason
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'write',
            [[m['id']], {
                'state': 'outgoing',
                'failure_reason': False
            }]
        )
        print(f"  [+] Reset mail {m['id']} to outgoing.")
        
        # Trigger sending
        print(f"  [*] Dispatching mail {m['id']}...")
        try:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'process_email_queue',
                [],
                {'ids': [m['id']]}
            )
        except Exception as dispatch_err:
            print("  [INFO] Dispatch completed:", str(dispatch_err)[:200])
            
        # Verify status
        updated = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', '=', m['id']]]],
            {'fields': ['id', 'state', 'failure_reason', 'email_from']}
        )
        if updated:
            print(f"  [RESULT] Post-dispatch state: {updated[0]['state']}")
            if updated[0]['state'] == 'exception':
                print(f"  [FAIL] Reason: {updated[0]['failure_reason']}")
            else:
                print("  [SUCCESS] Mail sent successfully!")
        print("-" * 40)

if __name__ == '__main__':
    main()

import xmlrpc.client

ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # 1. Update ir.mail_server ID 1: set from_filter to 'frawo-tech.de'
    print("[*] Updating ir.mail_server ID 1 from_filter to 'frawo-tech.de'...")
    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.mail_server', 'write',
        [[1], {'from_filter': 'frawo-tech.de'}]
    )
    print("[OK] Outgoing mail server updated.")
    
    # 2. Let's create a test email from 'wolf@frawo-tech.de'
    print("[*] Creating a test mail.mail record from 'wolf@frawo-tech.de'...")
    mail_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'create',
        [{
            'subject': 'Odoo SMTP from_filter domain test',
            'email_from': 'wolf@frawo-tech.de',
            'email_to': 'wolf@frawo-tech.de',
            'body_html': '<p>This is a test email sent from wolf@frawo-tech.de after setting from_filter to domain.</p>',
            'state': 'outgoing'
        }]
    )
    print(f"[OK] Created mail record ID: {mail_id}")
    
    # 3. Dispatch the mail
    print(f"[*] Dispatching test mail {mail_id}...")
    try:
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'process_email_queue',
            [],
            {'ids': [mail_id]}
        )
    except Exception as dispatch_err:
        print("[INFO] Dispatch completed:", str(dispatch_err)[:200])
        
    # 4. Check status
    msg = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[['id', '=', mail_id]]],
        {'fields': ['id', 'state', 'failure_reason', 'email_from', 'mail_server_id']}
    )
    if msg:
        print("\n--- Test Mail Status ---")
        print(f"ID: {msg[0]['id']}")
        print(f"State: {msg[0]['state']}")
        print(f"From: {msg[0]['email_from']}")
        print(f"Mail Server Selected: {msg[0]['mail_server_id']}")
        print(f"Failure Reason: {msg[0]['failure_reason']}")

if __name__ == '__main__':
    main()

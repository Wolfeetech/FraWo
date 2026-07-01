import xmlrpc.client

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

def copy_and_send(mail_id, new_to, models, uid):
    print(f"\n[*] Copying mail ID {mail_id} to new clean mail for {new_to}...")
    
    # Read the failed mail
    mail = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'read',
        [[mail_id]],
        {}
    )[0]
    
    # Create clean copy
    new_mail_data = {
        'subject': mail['subject'],
        'email_from': 'info@frawo-tech.de',
        'email_to': new_to,
        'body_html': mail['body_html'],
        'state': 'outgoing',
        'attachment_ids': mail['attachment_ids'],
        'reply_to': 'info@frawo-tech.de'
    }
    
    new_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'create',
        [new_mail_data]
    )
    print(f"  [+] Created new clean mail record ID: {new_id}")
    
    # Dispatch
    print(f"  [*] Dispatching mail ID {new_id}...")
    try:
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'process_email_queue',
            [],
            {'ids': [new_id]}
        )
    except Exception as dispatch_err:
        print("  [INFO] Dispatch completed:", str(dispatch_err)[:200])
        
    # Verify status
    updated = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'read',
        [[new_id]],
        {'fields': ['id', 'state', 'failure_reason']}
    )[0]
    
    print(f"  [RESULT] Post-dispatch state: {updated['state']}")
    if updated['state'] == 'sent':
        print("  [SUCCESS] Email sent successfully!")
        return True
    else:
        print(f"  [FAIL] Reason: {updated['failure_reason']}")
        return False

def main():
    print("[*] Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Copy and send Offer S00007 (Mail 160)
    copy_and_send(160, 'luki@bodensee-veranstaltungstechnik.de', models, uid)
    
    # Copy and send Order confirmation S00007 (Mail 307)
    copy_and_send(307, 'luki@bodensee-veranstaltungstechnik.de', models, uid)
    
    # Copy and send Invoice INV/2026/00006 (Mail 159)
    copy_and_send(159, '1-vorstand@trommlerzug-lindau.de', models, uid)

if __name__ == '__main__':
    main()

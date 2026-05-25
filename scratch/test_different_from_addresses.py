import xmlrpc.client
import time

ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

def test_from(email_from):
    print(f"\n[*] Testing Odoo sending with From: '{email_from}'...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    try:
        mail_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'create',
            [{
                'subject': f'Odoo From Test: {email_from}',
                'email_from': email_from,
                'email_to': 'wolf@frawo-tech.de',
                'body_html': f'<p>Test email with From: {email_from}</p>',
                'state': 'outgoing'
            }]
        )
        print(f"  [+] Created mail record ID: {mail_id}")
        
        # Dispatch
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'process_email_queue',
            [],
            {'ids': [mail_id]}
        )
        print("  [*] Dispatched.")
        
        # Check
        msg = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'read',
            [[mail_id]],
            {'fields': ['id', 'state', 'failure_reason', 'email_from']}
        )[0]
        
        print(f"  [RESULT] State: {msg['state']}")
        print(f"  [RESULT] Failure Reason: {msg['failure_reason']}")
        return msg['state'] == 'sent'
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    senders = [
        'webmaster@frawo-tech.de',
        'wolf@frawo-tech.de',
        'info@frawo-tech.de',
        'notifications@frawo-tech.de',
        'bounce@frawo-tech.de'
    ]
    for s in senders:
        test_from(s)

if __name__ == '__main__':
    main()

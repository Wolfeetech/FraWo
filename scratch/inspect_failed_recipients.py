import xmlrpc.client

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

def main():
    print("[*] Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    mail_ids = [307, 160, 159]
    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'read',
        [mail_ids],
        {'fields': ['id', 'subject', 'body_html', 'email_from', 'email_to', 'recipient_ids', 'attachment_ids']}
    )
    
    for m in mails:
        print(f"\nFailed Mail ID: {m['id']}")
        print(f"  Subject: {m['subject']}")
        print(f"  From: {m['email_from']}")
        print(f"  To: {m['email_to']}")
        print(f"  Recipient IDs: {m['recipient_ids']}")
        
        # Get actual recipient email addresses
        recipient_emails = []
        if m['email_to']:
            recipient_emails.append(m['email_to'])
        elif m['recipient_ids']:
            partners = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [m['recipient_ids']],
                {'fields': ['email', 'name']}
            )
            for p in partners:
                if p['email']:
                    recipient_emails.append(p['email'])
                print(f"    Recipient Partner {p['id']}: {p['name']} (Email: {p['email']})")
                
        print(f"  Resolved Recipient Emails: {recipient_emails}")

if __name__ == '__main__':
    main()

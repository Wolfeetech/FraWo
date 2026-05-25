import xmlrpc.client
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

urgent_ids = [366, 367, 368]

for mail_id in urgent_ids:
    print(f"Duplicating and sending content for mail {mail_id}...")
    
    # Read the original mail
    mail_data_list = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[mail_id]], {'fields': ['subject', 'body_html', 'email_to', 'recipient_ids', 'attachment_ids']})
    
    if not mail_data_list:
        print(f"Mail {mail_id} not found!")
        continue
        
    mail_data = mail_data_list[0]
    
    # Create a new mail with forced sender
    new_mail_vals = {
        'subject': mail_data['subject'],
        'body_html': mail_data['body_html'],
        'email_from': 'webmaster@frawo-tech.de',
        'reply_to': 'webmaster@frawo-tech.de',
        'email_to': mail_data['email_to'],
        'recipient_ids': [(6, 0, mail_data['recipient_ids'])],
        'attachment_ids': [(6, 0, mail_data['attachment_ids'])],
        'mail_server_id': 1, # Force the working Strato server
        'auto_delete': False
    }
    
    new_mail_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'create', [new_mail_vals])
    print(f"Created new mail {new_mail_id} from {mail_id}")
    
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [[new_mail_id]])
        print(f"Successfully sent new mail {new_mail_id}!")
    except Exception as e:
        print(f"Failed to send new mail {new_mail_id}: {e}")
        
    status = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[new_mail_id]], {'fields': ['state', 'failure_reason']})
    print(f"Status after send for new mail {new_mail_id}: {status}")


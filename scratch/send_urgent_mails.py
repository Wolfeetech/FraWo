import xmlrpc.client
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

urgent_ids = [366, 367, 368]

for mail_id in urgent_ids:
    print(f"Attempting to send mail {mail_id}...")
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [[mail_id]])
        print(f"Successfully sent mail {mail_id}!")
    except Exception as e:
        print(f"Failed to send mail {mail_id}: {e}")
        
    # Read back the state and failure reason
    status = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[mail_id]], {'fields': ['state', 'failure_reason']})
    print(f"Status after send for {mail_id}: {status}")


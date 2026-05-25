import xmlrpc.client
import os
import base64
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

urgent_ids = [366, 368]

for mail_id in urgent_ids:
    mail = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[mail_id]], {'fields': ['subject', 'attachment_ids']})
    if mail and mail[0].get('attachment_ids'):
        attachments = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.attachment', 'read', [mail[0]['attachment_ids']], {'fields': ['name', 'datas']})
        for att in attachments:
            file_path = os.path.join(r"C:\Users\StudioPC\Desktop", att['name'])
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(att['datas']))
            print(f"Saved {att['name']} to Desktop! (Subject: {mail[0]['subject']})")


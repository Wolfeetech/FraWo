import xmlrpc.client
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
users = ['wolf@frawo-tech.de', 'franz@frawo-tech.de']
passwords = ['__ROTATED_SECRET__', '__ROTATED_SECRET__']
dbs = ['FraWo_GbR', 'FraWo_Live']

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')

for db in dbs:
    for user in users:
        for pwd in passwords:
            try:
                uid = common.authenticate(db, user, pwd, {})
                if uid:
                    print(f"[SUCCESS] DB={db} | USER={user} | PASSWORD={pwd} -> UID={uid}")
                else:
                    print(f"[FAILED] DB={db} | USER={user} | PASSWORD={pwd}")
            except Exception as e:
                print(f"[ERROR] DB={db} | USER={user} | PASSWORD={pwd} -> {str(e)[:100]}")

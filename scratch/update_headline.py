import xmlrpc.client
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

existing_view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search_read', [[('key', '=', 'website.frawo_radio_page')]], {'fields': ['arch']})
if existing_view:
    arch = existing_view[0]['arch']
    
    # Replace THE UNDERGROUND with FRAWO FUNK
    arch = arch.replace('<h1 class="title-frawo">THE</h1>', '<h1 class="title-frawo">FRAWO</h1>')
    arch = arch.replace('<h1 class="title-funk">UNDERGROUND</h1>', '<h1 class="title-funk">FUNK</h1>')
    
    # Optional: also remove "UNDERGROUND" from the marquee
    arch = arch.replace('+++ UNDERGROUND ELECTRONIC +++', '+++ ELECTRONIC MUSIC +++')
    
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [existing_view[0]['id'], {'arch': arch}])
    print("SUCCESS: Reverted headline to FRAWO FUNK.")
else:
    print("ERROR: View not found!")

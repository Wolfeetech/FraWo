import xmlrpc.client
import os
import base64
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
    # Replace the old login section
    old_section = """<a href="/web/login?redirect=/frawo-funk" class="btn-community mb-2">VIP Login</a>
                                <div class="text-center mt-3">
                                    <a href="/web/signup?redirect=/frawo-funk" style="color: #888; font-size: 12px; text-decoration: none;">Noch kein Account? Registrieren</a>
                                </div>"""
    
    new_section = """<div class="d-flex flex-column gap-2">
                                    <a href="/web/signup?redirect=/frawo-funk" class="btn-community" style="background: linear-gradient(135deg, #10B981, #059669); box-shadow: 0 4px 15px rgba(16,185,129,0.4);">Kostenlos Registrieren</a>
                                    <a href="/web/login?redirect=/frawo-funk" class="btn-community mt-2" style="background: transparent; border: 1px solid #8B5CF6; box-shadow: none;">VIP Login</a>
                                </div>"""
    
    arch = arch.replace(old_section, new_section)
    
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [existing_view[0]['id'], {'arch': arch}])
    print("SUCCESS: Updated Radio page with prominent Sign Up button.")
else:
    print("ERROR: View 'website.frawo_radio_page' not found!")

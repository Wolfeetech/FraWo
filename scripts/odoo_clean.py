import xmlrpc.client
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

from odoo_env import resolve_connection


DEFAULT_URL = 'http://10.1.0.22:8069'
DEFAULT_DB = 'FraWo_GbR'
DEFAULT_USER = 'wolf@frawo-tech.de'

try:
    settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    common = xmlrpc.client.ServerProxy(f'{settings.url}/xmlrpc/2/common')
    uid = common.authenticate(settings.db, settings.user, settings.secret, {})
    models = xmlrpc.client.ServerProxy(f'{settings.url}/xmlrpc/2/object')

    home_ids = models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'search', [[['key', '=', 'website.homepage']]])
    if home_ids:
        arch = '<?xml version="1.0"?>\n<t name="Homepage" t-name="website.homepage">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty"/>\n    </t>\n</t>'
        models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'write', [home_ids, {'arch_db': arch}])
        print('Homepage restored.')

    contact_ids = models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'search', [[['key', 'ilike', 'contactus']]])
    if contact_ids:
        arch_c = '<?xml version="1.0"?>\n<t name="Contact us" t-name="website.contactus">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty"/>\n    </t>\n</t>'
        models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'write', [contact_ids, {'arch_db': arch_c}])
        print('Contact page restored.')

    print('Rollback Complete.')
except Exception as e:
    print('Error:', e)

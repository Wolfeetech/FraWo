import sys
import xmlrpc.client
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://localhost:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object')

home = '''<t name=&quot;Home&quot; t-name=&quot;website.homepage&quot;></t>'''
print('uid:', uid)
print('done')

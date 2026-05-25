import xmlrpc.client
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Close Password Task (213)
done_stage = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search', [[('name', 'ilike', 'Erledigt')]])
done_stage_id = done_stage[0]

models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[213], {'stage_id': done_stage_id}])
# Close Radio DNS Task (158)
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[158], {'stage_id': done_stage_id}])

# Fetch details for 161
task161 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'read', [[161]], {'fields': ['name', 'description']})
print("Task 161:", task161)

# Fetch details for 178 (AzuraCast Branding)
task178 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'read', [[178]], {'fields': ['name', 'description']})
print("Task 178:", task178)

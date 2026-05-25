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

# Find "Erledigt" stage ID
stages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search_read', [[('name', '=', 'Erledigt')]], {'fields': ['id']})
if not stages:
    print("Stage 'Erledigt' not found.")
    exit(1)
done_stage_id = stages[0]['id']

# Mark Tasks 83 and 140 as done
tasks_to_update = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search', [[('id', 'in', [83, 140])]])
if tasks_to_update:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [tasks_to_update, {'stage_id': done_stage_id}])
    print(f"Marked tasks {tasks_to_update} as Erledigt.")
else:
    print("Tasks 83 and 140 not found.")

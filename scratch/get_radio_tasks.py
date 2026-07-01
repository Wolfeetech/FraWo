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

project_name = "Phase 5: Radio Ecosystem (AzuraCast)"
projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[('name', '=', project_name)]], {'fields': ['id', 'name']})

if projects:
    project_id = projects[0]['id']
    print(f"Project ID: {project_id} - {projects[0]['name']}")
    
    tasks = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.task', 'search_read',
        [[('project_id', '=', project_id)]],
        {'fields': ['id', 'name', 'stage_id', 'description']}
    )
    
    print("\nTasks found:")
    for t in tasks:
        stage = t['stage_id'][1] if t['stage_id'] else 'No Stage'
        print(f"- Task ID: {t['id']} | Name: {t['name']} | Stage: {stage}")
        print(f"  Description: {t['description'][:150]}...")
else:
    print(f"Project '{project_name}' not found.")

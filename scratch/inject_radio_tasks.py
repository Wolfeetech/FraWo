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

# Check if project exists, else create it
project_name = "Phase 5: Radio Ecosystem (AzuraCast)"
projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[('name', '=', project_name)]], {'fields': ['id']})

if not projects:
    project_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'create', [{'name': project_name}])
else:
    project_id = projects[0]['id']

# Define tasks from updated implementation plan
tasks = [
    {
        'name': 'Epic 1: Basic Integration & Smart Upload',
        'description': 'AzuraCast: Ziel-Ordner (z.B. /media/Nightshift, /media/Primetime) anlegen und mit den Playlists verknüpfen. StudioPC: Python-Upload-Skript schreiben, das den Ordner _Sorted ausliest, ID3-Tags prüft und die Dateien gezielt in die AzuraCast-Ordner pusht.',
        'project_id': project_id
    },
    {
        'name': 'Epic 2: Odoo User Sync (Die Brücke)',
        'description': 'Odoo DJ-Benutzer -> AzuraCast Streamer-Account synchronisieren.',
        'project_id': project_id
    },
    {
        'name': 'Epic 3: Interactive Frontend (Herz/Scheiße)',
        'description': 'Hörer-Feedback-Buttons im FraWo Funk Player integrieren. Die Klicks verändern in Echtzeit das Playlist-Gewicht (Weight) des Tracks in AzuraCast über die API.',
        'project_id': project_id
    }
]

# Check existing tasks to avoid duplicates or update them
existing_tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[('project_id', '=', project_id)]], {'fields': ['name', 'id']})
existing_names = {t['name']: t['id'] for t in existing_tasks}

for t in tasks:
    if t['name'] not in existing_names:
        task_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'create', [t])
        print(f"Created Task: {t['name']}")
    else:
        # Update description of existing tasks
        task_id = existing_names[t['name']]
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[task_id], {'description': t['description']}])
        print(f"Updated Task: {t['name']}")

print("Successfully synced Radio Ecosystem tasks to Odoo SSOT.")

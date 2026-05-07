# -*- coding: utf-8 -*-
import sys
import xmlrpc.client
import json
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 1. Get Projects
projects = models.execute_kw(db, uid, password, 'project.project', 'search_read', [[]], {'fields': ['id', 'name']})

# 2. Get Stages (to find "Done")
stages = models.execute_kw(db, uid, password, 'project.task.type', 'search_read', [[]], {'fields': ['id', 'name']})

# 3. Get Tasks
tasks = models.execute_kw(db, uid, password, 'project.task', 'search_read', [[('active', '=', True)]], {'fields': ['id', 'name', 'project_id', 'stage_id']})

results = {
    "projects": projects,
    "stages": stages,
    "tasks": tasks
}

print(json.dumps(results, indent=2))

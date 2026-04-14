# -*- coding: utf-8 -*-
import xmlrpc.client
import json

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

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

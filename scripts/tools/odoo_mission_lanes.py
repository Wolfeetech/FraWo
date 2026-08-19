import xmlrpc.client
import os

url = 'http://10.1.0.112:8069'
db = 'FraWo_GbR'
pw = '__ROTATED_SECRET__'
user = 'wolf@frawo.tech'

print('Authenticating with Odoo...')
uid = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common').authenticate(db, user, pw, {})
print(f'UID is: {uid}')
if not uid:
    print('LOGIN FAILED! Check credentials or DB name.')
    exit(1)
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def execute(model, method, *args, **kwargs):
    return models.execute_kw(db, uid, pw, model, method, args, kwargs)

# 1. Ensure Mission Lanes (Projects) exist
lanes = ['Heritage', 'Website', 'Security', 'Stockenweiler', 'Infrastructure']
project_ids = {}

print('\n--- 1. Ensuring Mission Lanes ---')
for lane in lanes:
    existing = execute('project.project', 'search_read', [[('name', '=', lane)]], {'fields': ['id', 'name'], 'limit': 1})
    if existing:
        project_ids[lane] = existing[0]['id']
        print(f'Lane already exists: {lane} (ID: {project_ids[lane]})')
    else:
        new_id = execute('project.project', 'create', [{'name': lane}])
        project_ids[lane] = new_id
        print(f'Created Lane: {lane} (ID: {new_id})')

# 2. Reclaim Tasks (Auto-sort based on keywords)
print('\n--- 2. Reclaiming Tasks ---')
tasks = execute('project.task', 'search_read', [[]], {'fields': ['id', 'name', 'description', 'project_id']})
print(f'Found {len(tasks)} tasks in total.')

keywords = {
    'Heritage': ['archiv', 'kassette', 'digitalisierung', 'heritage', 'tape', 'vinyl', 'schallplatte', 'historie'],
    'Website': ['website', 'tech', 'radio-player', 'seo', 'domain', 'hosting', 'odoo', 'web', 'portal', 'caddy', 'player'],
    'Security': ['security', 'passwort', 'vaultwarden', 'backup', 'firewall', 'vpn', 'adguard', 'sicherheit', 'auth'],
    'Stockenweiler': ['stockenweiler', 'prinz', 'med-el', 'ci', 'hörgerät', 'tv', 'kasse', 'mutter', 'vater', 'alois', 'dsp'],
    'Infrastructure': ['proxmox', 'pve', 'lxc', 'docker', 'nas', 'storage', 'switch', 'wlan', 'unifi', 'azuracast', 'server', 'netzwerk', 'tailscale', 'smb', 'cifs']
}

moved_count = 0
for task in tasks:
    task_id = task['id']
    name = (task.get('name') or '').lower()
    desc = (task.get('description') or '').lower()
    current_proj_id = task.get('project_id')
    current_proj_id = current_proj_id[0] if current_proj_id else None

    # Check if task is already in one of the 5 mission lanes
    if current_proj_id in project_ids.values():
        continue

    # Determine best lane based on keywords
    best_lane = None
    for lane, words in keywords.items():
        if any(word in name or word in desc for word in words):
            best_lane = lane
            break
    
    if not best_lane:
        # Default to Infrastructure if we can't figure it out, or leave it
        best_lane = 'Infrastructure'

    new_proj_id = project_ids[best_lane]
    execute('project.task', 'write', [[task_id], {'project_id': new_proj_id}])
    print(f'Moved task "{task.get("name", "Unnamed")}" -> {best_lane}')
    moved_count += 1

print(f'\nKonsolidierung abgeschlossen! {moved_count} Aufgaben wurden in Mission Lanes einsortiert.')

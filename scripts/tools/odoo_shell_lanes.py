Project = env['project.project']
Task = env['project.task']

lanes = ['01_Operations', '02_Radio_Broadcasting', '03_Heritage_Digitization', '04_Infrastructure_Sec', '05_Client_Projects']
project_ids = {}

print('--- 1. Ensuring Mission Lanes ---')
for lane in lanes:
    existing = Project.search([('name', '=', lane)], limit=1)
    if existing:
        project_ids[lane] = existing.id
        print(f'Lane already exists: {lane} (ID: {existing.id})')
    else:
        new_proj = Project.create({'name': lane})
        project_ids[lane] = new_proj.id
        print(f'Created Lane: {lane} (ID: {new_proj.id})')
        env.cr.commit()

print('\n--- 2. Reclaiming Tasks ---')
tasks = Task.search([])
print(f'Found {len(tasks)} tasks in total.')

keywords = {
    '01_Operations': ['website', 'tech', 'odoo', 'web', 'portal', 'caddy', 'betrieb', 'management', 'kasse', 'rechnung', 'auftrag', 'planung'],
    '02_Radio_Broadcasting': ['radio-player', 'player', 'radio', 'funk', 'azuracast', 'stream', 'rotation', 'playlist', 'sendung'],
    '03_Heritage_Digitization': ['archiv', 'kassette', 'digitalisierung', 'heritage', 'tape', 'vinyl', 'schallplatte', 'historie', 'band'],
    '04_Infrastructure_Sec': ['security', 'passwort', 'vaultwarden', 'backup', 'firewall', 'vpn', 'adguard', 'sicherheit', 'auth', 'proxmox', 'pve', 'lxc', 'docker', 'nas', 'storage', 'switch', 'wlan', 'unifi', 'server', 'netzwerk', 'tailscale', 'smb', 'cifs'],
    '05_Client_Projects': ['stockenweiler', 'prinz', 'med-el', 'ci', 'hörgerät', 'tv', 'mutter', 'vater', 'alois', 'dsp', 'installation', 'fostex']
}

moved_count = 0
for task in tasks:
    if task.project_id.id in project_ids.values():
        continue

    name = (task.name or '').lower()
    desc = ''
    if hasattr(task, 'description') and task.description:
        desc = str(task.description).lower()

    best_lane = None
    for lane, words in keywords.items():
        if any(word in name or word in desc for word in words):
            best_lane = lane
            break
    
    if not best_lane:
        best_lane = '01_Operations'

    new_proj_id = project_ids[best_lane]
    task.write({'project_id': new_proj_id})
    print(f'Moved task "{task.name}" -> {best_lane}')
    moved_count += 1

env.cr.commit()
print(f'\nKonsolidierung abgeschlossen! {moved_count} Aufgaben wurden in Mission Lanes einsortiert.')

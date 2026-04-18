import json

INPUT_FILE = '/tmp/odoo_migration_data.json'
WOLF_ID = 6

# Mapping Strategy from Plan
MAPPING = {
    # Project Name keywords to Target Project IDs in FraWo_GbR
    "Masterplan": 1,
    "FraWo Homeserver 2027": 1,
    "Heritage": 2,
    "Founding": 2,
    "Website": 3,
    "Public Edge": 3,
    "Security": 4,
    "PBS": 4,
    "Stockenweiler": 5,
}

# 1. Ensure Archive Project exists
Project = env['project.project']
archive = Project.search([('name', 'ilike', 'Archive')], limit=1)
if not archive:
    print("Creating Lane Z: Archive / Legacy...")
    archive = Project.create({
        'name': 'Lane Z: Archive / Legacy',
        'active': True,
        'company_id': 1,
    })
print(f"Archive Project ID: {archive.id}")

with open(INPUT_FILE, 'r') as f:
    data = json.load(f)

print(f"Starting injection of {len(data)} tasks...")

count = 0
for t in data:
    p_name = t['project_name']
    
    # Determine target project ID
    target_p_id = archive.id # Default to Archive
    for keyword, tid in MAPPING.items():
        if keyword.lower() in p_name.lower():
            target_p_id = tid
            break
            
    print(f"Migrating '{t['task_name']}' from '{p_name}' -> Target Project {target_p_id}")
    
    # Create the task via ORM
    # Odoo 17: user_id -> user_ids (M2M)
    # Odoo 17: state is the field name for kanban state / task state
    env['project.task'].create({
        'name': t['task_name'],
        'description': t['description'],
        'project_id': target_p_id,
        'user_ids': [WOLF_ID], 
        'priority': t['priority'] if t['priority'] in ['0', '1'] else '0',
        'state': t['state'] if t['state'] in ['01_in_progress', '1_done', '03_approved', '02_changes_requested', '04_waiting_normal'] else '01_in_progress',
        'company_id': 1,
    })
    count += 1

env.cr.commit()
print(f"Successfully injected {count} tasks into FraWo_GbR.")

# Odoo Shell Script to Sync Board and Set Language to German
import json

PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"

# German Stage Names
STAGES_SPEC = [
    {"name": "📝 Backlog", "sequence": 10},
    {"name": "⚙️ Planung", "sequence": 20},
    {"name": "🚀 In Arbeit", "sequence": 30},
    {"name": "🛑 Blockiert", "sequence": 40},
    {"name": "✅ Erledigt", "sequence": 50},
]

TASK_MAP = {
    "post_restore_backup_proof": "Post-Restore Backup Proof (ssd2tb)",
    "vm_firewall_hardening_reapply": "VM Firewall Hardening (VM 210/220)",
    "pve_host_exposure_audit": "PVE Host Exposure Audit",
    "ct100_storage_migration": "CT 100 Migration auf ssd2tb",
    "split_dns_finalization": "Split-DNS Finalisierung",
    "public_edge_https_release": "Website Release (HTTPS)",
    "radio_node_recovery": "Radio Node Recovery",
    "wolfstudiopc_admin_path": "StudioPC Admin Path",
    "stockenweiler_preparation": "Stockenweiler Vorbereitung",
    "haos_usb_path": "HAOS Zigbee/USB Passthrough",
    "pbs_guarded_rebuild": "PBS Guarded Rebuild",
    "windows_gui_updates_closeout": "Workstation Updates (GUI)",
    "workspace_drift_guard": "Workspace Drift Guard",
    "github_main_branch_protection": "GitHub Branch Protection",
    "nextcloud_desktop_https_callback": "Nextcloud Desktop HTTPS Fix",
    "odoo_project_ssot_sync": "Odoo Project SSOT Sync",
    "odoo_sender_email_for_document_mail": "Odoo E-Mail Absender Fix",
    "odoo_acl_res_users_log": "Odoo ACL res.users.log",
    "radio_frontdoor_backend": "Radio Backend (AzuraCast)",
    "ha_eltern_dashboard": "HA Eltern Dashboard",
    "website_access_protection": "Website Access Protection",
}

# 1. Set Language
print("Setting language to German for Wolf and Admin...")
users = env['res.users'].search([('login', 'in', ['admin', 'wolf@frawo-tech.de'])])
for user in users:
    user.lang = 'de_DE'
print(f"Language set for {len(users)} users.")

# 2. Ensure Project
project = env['project.project'].search([('name', 'ilike', 'Masterplan')], limit=1)
if project:
    project.name = PROJECT_NAME
else:
    project = env['project.project'].create({'name': PROJECT_NAME})
print(f"Project: {project.name}")

# 3. Ensure Stages
print("Syncing stages...")
for spec in STAGES_SPEC:
    stage = env['project.task.type'].search([('name', '=', spec['name'])], limit=1)
    if not stage:
        stage = env['project.task.type'].create({
            'name': spec['name'],
            'sequence': spec['sequence'],
            'project_ids': [(4, project.id)]
        })
    else:
        stage.write({
            'sequence': spec['sequence'],
            'project_ids': [(4, project.id)]
        })

# 4. Sync Tasks (Simplified check as we don't have easy file access here)
# We use the TASK_MAP to ensure these tasks exist in the project.
existing_tasks = env['project.task'].search([('project_id', '=', project.id)])
existing_names = {t.name for t in existing_tasks}

for task_id, german_name in TASK_MAP.items():
    if german_name not in existing_names:
        env['project.task'].create({
            'name': german_name,
            'project_id': project.id,
            'description': f"Loose end from SSOT: {task_id}"
        })
        print(f"Created task: {german_name}")

env.cr.commit()
print("Odoo Board Sync Complete.")

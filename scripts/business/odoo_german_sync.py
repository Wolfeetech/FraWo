from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from odoo_rpc_client import connect, OdooSession

# Canonical Project Name in German
PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"

# German Stage Names
STAGES = [
    {"name": "📝 Backlog", "sequence": 10},
    {"name": "⚙️ Planung", "sequence": 20},
    {"name": "🚀 In Arbeit", "sequence": 30},
    {"name": "🛑 Blockiert", "sequence": 40},
    {"name": "✅ Erledigt", "sequence": 50},
]

# Task Mapping (English ID -> German Name)
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

def sync_board():
    print("--- Odoo German Sync & Board Update ---")
    
    # 1. Connect to Odoo
    try:
        # Forcing admin/admin for initial sync
        os.environ["ODOO_RPC_PASSWORD"] = "admin"
        session = connect(default_user="admin", prompt_for_username=False)
        print(f"Verbunden mit {session.url} (DB: {session.db})")
    except Exception as e:
        print(f"Fehler bei der Verbindung: {e}")
        sys.exit(1)

    # 2. Set Language to German for active users
    print("Setze Sprache auf Deutsch für Wolf und Admin...")
    user_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', 'in', ['admin', 'wolf@frawo-tech.de']]]])
    if user_ids:
        session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'write', [user_ids, {'lang': 'de_DE'}])
        print(f"Sprache für {len(user_ids)} Benutzer auf de_DE gesetzt.")

    # 3. Ensure Project exists
    project_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', 'ilike', 'Masterplan']]])
    if project_ids:
        project_id = project_ids[0]
        session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [[project_id], {'name': PROJECT_NAME}])
        print(f"Projekt gefunden und aktualisiert: {PROJECT_NAME}")
    else:
        project_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{'name': PROJECT_NAME}])
        print(f"Projekt neu angelegt: {PROJECT_NAME}")

    # 4. Ensure Stages exist
    print("Synchronisiere Spalten (Stages)...")
    stage_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task.type', 'search_read', [[]], {'fields': ['name', 'id']})
    stage_map = {s['name']: s['id'] for s in stage_ids}
    
    for stage_spec in STAGES:
        if stage_spec['name'] not in stage_map:
            new_stage_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task.type', 'create', [{
                'name': stage_spec['name'],
                'sequence': stage_spec['sequence'],
                'project_ids': [(4, project_id)]
            }])
            stage_map[stage_spec['name']] = new_stage_id
            print(f"Spalte erstellt: {stage_spec['name']}")
        else:
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.task.type', 'write', [[stage_map[stage_spec['name']]], {
                'sequence': stage_spec['sequence'],
                'project_ids': [(4, project_id)]
            }])

    # 5. Load tasks from current_plan.json
    plan_path = Path(__file__).resolve().parents[2] / "manifests" / "work_lanes" / "current_plan.json"
    if plan_path.exists():
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
            plan_tasks = plan.get("tasks", [])
    else:
        plan_tasks = []
        print("Warnung: current_plan.json nicht gefunden.")

    # 6. Load tasks from todo.md (simplified)
    # For now we use the TASK_MAP as the list of tasks to ensure are present.
    
    # 7. Upsert Tasks
    print("Synchronisiere Aufgaben...")
    existing_tasks = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search_read', [[['project_id', '=', project_id]]], {'fields': ['name']})
    existing_task_names = {t['name'] for t in existing_tasks}

    # Combine tasks from plan and map
    for task_id_key, german_name in TASK_MAP.items():
        if german_name not in existing_task_names:
            # Find matching plan task for description
            plan_task = next((t for t in plan_tasks if t['id'] == task_id_key), None)
            description = ""
            if plan_task:
                description = f"<p><strong>Ziel:</strong> {plan_task.get('goal', '')}</p>"
                if plan_task.get('done_when'):
                    description += f"<p><strong>Erledigt wenn:</strong> {plan_task.get('done_when')}</p>"
            
            # Determine stage
            target_stage = "📝 Backlog"
            if plan_task:
                status = plan_task.get('status', '')
                if status == 'active': target_stage = "🚀 In Arbeit"
                elif status == 'blocked': target_stage = "🛑 Blockiert"
                elif status == 'done': target_stage = "✅ Erledigt"
                elif status == 'watch': target_stage = "⚙️ Planung"

            session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'create', [{
                'name': german_name,
                'project_id': project_id,
                'stage_id': stage_map.get(target_stage),
                'description': description
            }])
            print(f"Aufgabe erstellt: {german_name}")
    
    print("\n--- Sync abgeschlossen! ---")

if __name__ == "__main__":
    sync_board()

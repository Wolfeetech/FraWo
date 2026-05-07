#!/usr/bin/env python3
"""
Sync FraWo Cleanup Actions to Odoo Project Board
=================================================
Syncs all cleanup tasks completed today to Odoo as project tasks.
"""

import xmlrpc.client
import os
from datetime import datetime

# Odoo Configuration
ODOO_URL = os.getenv("ODOO_URL", "http://10.1.0.22:8069")
ODOO_DB = os.getenv("ODOO_DB", "FraWo_GbR")
ODOO_USER = os.getenv("ODOO_USER", "wolf@frawo-tech.de")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "Wolf2024!Frawo")

# Cleanup tasks completed today
CLEANUP_TASKS = [
    {
        "name": "[CLEANUP] WORKSPACE Duplicate gelöscht (80MB freed)",
        "description": "✅ Duplikat C:\\WORKSPACE\\FraWo entfernt - nur noch OneDrive als SSOT",
        "status": "done",
        "priority": "1"
    },
    {
        "name": "[CLEANUP] Alte Remediation Scripts archiviert",
        "description": "✅ frawo_final*.py und frawo_update*.py nach /scripts/archive/remediations_april_2026/ verschoben",
        "status": "done",
        "priority": "1"
    },
    {
        "name": "[CLEANUP] Research Scripts archiviert",
        "description": "✅ Alle 19 Research-Scripts nach /scripts/archive/research_q1_2026/ verschoben",
        "status": "done",
        "priority": "1"
    },
    {
        "name": "[CLEANUP] Logo-Dateien ins Repo integriert",
        "description": "✅ 6 PNG-Dateien von Downloads nach /brand_assets/logo_iterations/ verschoben",
        "status": "done",
        "priority": "2"
    },
    {
        "name": "[CLEANUP] Temporary Files gelöscht",
        "description": "✅ b64_temp.txt, temp_missing_report.md, frawo_radio_player_temp.html entfernt",
        "status": "done",
        "priority": "2"
    },
    {
        "name": "[CLEANUP] Gemini AI Cache bereinigt",
        "description": "✅ 109 FraWo-bezogene Cache-Dateien aus .gemini/antigravity/brain gelöscht",
        "status": "done",
        "priority": "2"
    },
    {
        "name": "[SSOT] Single Source of Truth etabliert",
        "description": """✅ FraWo SSOT definiert:
- AKTIV: C:\\Users\\StudioPC\\OneDrive\\Dokumente\\GitHub\\FraWo (Main Repo)
- ARCHIV: /scripts/archive/ (strukturiert nach Datum/Kategorie)
- CLEANUP: ~80MB+ Speicher freigegeben
- STRUKTUR: Alte Scripts kategorisiert, Duplikate eliminiert""",
        "status": "done",
        "priority": "0"
    }
]

def connect_odoo():
    """Connect to Odoo and return authenticated session."""
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

        if not uid:
            print(f"❌ Authentication failed for {ODOO_USER}")
            return None, None

        print(f"✅ Connected to Odoo as {ODOO_USER} (UID: {uid})")
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        return uid, models

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None, None

def get_or_create_project(uid, models):
    """Get or create FraWo Masterplan project."""
    try:
        # Search for existing project
        project_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'project.project', 'search',
            [[['name', 'ilike', 'FraWo Masterplan']]]
        )

        if project_ids:
            print(f"✅ Found existing project (ID: {project_ids[0]})")
            return project_ids[0]

        # Create new project
        project_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'project.project', 'create',
            [{
                'name': 'FraWo Masterplan - Codebase Cleanup',
                'description': 'Single Source of Truth establishment and technical debt cleanup'
            }]
        )
        print(f"✅ Created new project (ID: {project_id})")
        return project_id

    except Exception as e:
        print(f"❌ Project error: {e}")
        return None

def sync_cleanup_tasks(uid, models, project_id):
    """Sync cleanup tasks to Odoo."""
    synced_count = 0

    for task in CLEANUP_TASKS:
        try:
            # Check if task already exists
            existing = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'project.task', 'search',
                [[['name', '=', task['name']], ['project_id', '=', project_id]]]
            )

            task_data = {
                'name': task['name'],
                'description': task['description'],
                'project_id': project_id,
                'priority': task['priority'],
                'date_deadline': datetime.now().strftime('%Y-%m-%d'),
            }

            # Mark as done if status is 'done'
            if task['status'] == 'done':
                # Get 'Done' stage
                stage_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'project.task.type', 'search',
                    [[['name', 'ilike', 'done']]]
                )
                if stage_ids:
                    task_data['stage_id'] = stage_ids[0]

            if existing:
                # Update existing task
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'project.task', 'write',
                    [[existing[0]], task_data]
                )
                print(f"✅ Updated: {task['name']}")
            else:
                # Create new task
                task_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'project.task', 'create',
                    [task_data]
                )
                print(f"✅ Created: {task['name']} (ID: {task_id})")

            synced_count += 1

        except Exception as e:
            print(f"❌ Error syncing '{task['name']}': {e}")

    return synced_count

def main():
    print("\n" + "="*60)
    print("FraWo Cleanup -> Odoo Project Board Sync")
    print("="*60 + "\n")

    # Connect to Odoo
    uid, models = connect_odoo()
    if not uid:
        print("\n❌ Failed to connect to Odoo. Tasks NOT synced.")
        print("💡 Odoo might be offline. Run this script later when Odoo is available.\n")
        return

    # Get or create project
    project_id = get_or_create_project(uid, models)
    if not project_id:
        print("\n❌ Failed to get/create project. Tasks NOT synced.\n")
        return

    # Sync cleanup tasks
    print(f"\n📋 Syncing {len(CLEANUP_TASKS)} cleanup tasks...\n")
    synced = sync_cleanup_tasks(uid, models, project_id)

    print("\n" + "="*60)
    print(f"✅ Sync complete! {synced}/{len(CLEANUP_TASKS)} tasks synced to Odoo")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
FRAWO Homeserver 2027 — Odoo Project Management Best Practice Optimizer
=======================================================================
Konsolidiert die fragmentierten Projekte in ein zentrales Masterplan-Projekt.
Erstellt professionelle Workflow-Stages und setzt Lane-Tags.

Ziele:
1. Ein zentrales Projekt "🚀 Homeserver 2027: Masterplan"
2. Stages: Backlog, Planung, In Arbeit, Blockiert, Erledigt
3. Tags: Lane A-E
4. Migration & Cleanup
"""

import xmlrpc.client
import sys

URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

def main():
    print("🚀 Odoo Best Practice Optimizer — Start...")
    
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    try:
        uid = common.authenticate(DB, USER, PASS, {})
        if not uid:
            print("❌ Fehler: Authentifizierung fehlgeschlagen.")
            return
        print(f"✅ Eingeloggt als UID {uid}")
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        return

    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    # 1. Zentrales Projekt erstellen
    project_name = "🚀 Homeserver 2027: Masterplan"
    existing_project = models.execute_kw(DB, uid, PASS, 'project.project', 'search', [[('name', '=', project_name)]])
    
    if existing_project:
        master_project_id = existing_project[0]
        print(f"♻️  Master-Projekt existiert bereits (ID {master_project_id})")
    else:
        master_project_id = models.execute_kw(DB, uid, PASS, 'project.project', 'create', [{
            'name': project_name,
            'description': "Zentrale Single Source of Truth für die gesamte Homeserver 2027 Infrastruktur.",
            'privacy_visibility': 'employees', # Sichtbar für alle internen User (wie Franz)
        }])
        print(f"✅ Master-Projekt angelegt (ID {master_project_id})")

    # 2. Workflow-Stages (project.task.type) anlegen
    # Hinweis: In Odoo 11+ bis 17 sind Stages meist projektübergreifend ODER projektgebunden.
    stages = [
        {'name': '📝 Backlog', 'sequence': 10},
        {'name': '⚙️ Planung & Vorbereitung', 'sequence': 20},
        {'name': '🚀 In Arbeit', 'sequence': 30},
        {'name': '🛑 Blockiert', 'sequence': 40},
        {'name': '✅ Erledigt', 'sequence': 50},
    ]
    
    stage_id_map = {}
    for stage_def in stages:
        existing_stage = models.execute_kw(DB, uid, PASS, 'project.task.type', 'search', [[('name', '=', stage_def['name'])]])
        if existing_stage:
            stage_id = existing_stage[0]
            # Sicherstellen, dass die Stage dem Projekt zugeordnet ist
            models.execute_kw(DB, uid, PASS, 'project.task.type', 'write', [[stage_id], {'project_ids': [(4, master_project_id)]}])
        else:
            stage_id = models.execute_kw(DB, uid, PASS, 'project.task.type', 'create', [{
                'name': stage_def['name'],
                'sequence': stage_def['sequence'],
                'project_ids': [(4, master_project_id)]
            }])
        stage_id_map[stage_def['name']] = stage_id
        print(f"✅ Stage bereit: {stage_def['name']}")

    # 3. Tags (project.tags) anlegen
    lane_tags = {
        'Lane A': 'Lane A: MVP 🏗️',
        'Lane B': 'Lane B: Website 🌐',
        'Lane C': 'Lane C: Infra 🛡️',
        'Lane D': 'Lane D: Stockenweiler 🏠',
        'Lane E': 'Lane E: Radio & Media 📻'
    }
    
    tag_id_map = {}
    for lane, tag_name in lane_tags.items():
        existing_tag = models.execute_kw(DB, uid, PASS, 'project.tags', 'search', [[('name', '=', tag_name)]])
        if existing_tag:
            tag_id = existing_tag[0]
        else:
            tag_id = models.execute_kw(DB, uid, PASS, 'project.tags', 'create', [{'name': tag_name}])
        tag_id_map[lane] = tag_id
        print(f"✅ Tag bereit: {tag_name}")

    # 4. Tasks finden und migrieren
    source_project_names = [
        "🏗️ Homeserver 2027: MVP Closeout (Lane A)",
        "🌐 Homeserver 2027: Website Release (Lane B)",
        "🛡️ Homeserver 2027: Security & Infra (Lane C)",
        "🏠 Homeserver 2027: Stockenweiler (Lane D)",
        "📻 Homeserver 2027: Radio & Media (Lane E)"
    ]
    
    source_project_ids = models.execute_kw(DB, uid, PASS, 'project.project', 'search', [[('name', 'in', source_project_names)]])
    
    tasks = models.execute_kw(DB, uid, PASS, 'project.task', 'search_read', 
        [[('project_id', 'in', source_project_ids)]], 
        {'fields': ['name', 'description', 'project_id', 'user_ids', 'priority', 'tag_ids']}
    )
    
    print(f"📦 Optimiere {len(tasks)} Tasks...")
    for task in tasks:
        parent_project = models.execute_kw(DB, uid, PASS, 'project.project', 'read', [task['project_id'][0]], {'fields': ['name']})
        parent_name = parent_project[0]['name']
        
        # Bestimme Lane-Tag
        target_lane = None
        for lane in lane_tags.keys():
            if lane in parent_name:
                target_lane = lane
                break
        
        # Bestimme initiale Stage (Status Quo)
        # Wenn Task in Description "ERLEDIGT" oder "Häkchen [x]" hat -> Erledigt
        # Wenn "Blocked" -> Blockiert
        target_stage_name = '📝 Backlog'
        desc = task['description'] or ""
        if "ERLEDIGT" in desc.upper() or "[x]" in desc:
            target_stage_name = '✅ Erledigt'
        elif "Blocked" in desc or "🛑" in desc:
            target_stage_name = '🛑 Blockiert'
        
        update_data = {
            'project_id': master_project_id,
            'stage_id': stage_id_map[target_stage_name],
            'tag_ids': [(4, tag_id_map[target_lane])] if target_lane else []
        }
        
        # Odoo 17 priority is "0" or "1" (star)
        models.execute_kw(DB, uid, PASS, 'project.task', 'write', [[task['id']], update_data])
        print(f"   🚚 Migriert: {task['name']} -> {target_stage_name}")

    # 5. Cleanup: Alte Projekte löschen
    print("🧹 Cleanup: Lösche fragmentierte Projekte...")
    for p_id in source_project_ids:
        models.execute_kw(DB, uid, PASS, 'project.project', 'unlink', [[p_id]])
        print(f"   🗑️  Gelöscht: Projekt ID {p_id}")

    print("\n" + "="*60)
    print("🎉 Odoo Best Practice Struktur ist jetzt LIVE!")
    print("📍 Projekt: " + project_name)
    print("📍 Workflow: Backlog -> Planung -> In Arbeit -> Blockiert -> Erledigt")
    print("="*60)

if __name__ == "__main__":
    main()

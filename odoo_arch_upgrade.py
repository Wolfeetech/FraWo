#!/usr/bin/env python3
"""
FRAWO Homeserver 2027 — Odoo Architecture Upgrade
=================================================
1. Erstellt User "Agent" (agent@frawo-tech.de)
2. Konsolidiert Infra & Roadmap Projekte (12, 13) in den Masterplan (21)
3. Erstellt Automation Stage & Tags
"""

import xmlrpc.client
import sys

URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

def main():
    print("🏗️ Odoo Architecture Upgrade — Start...")
    
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
    
    # --- 1. User 'Agent' anlegen ---
    print("\n👤 Erstelle User 'Agent'...")
    existing_agent = models.execute_kw(DB, uid, PASS, 'res.users', 'search', [[('login', '=', 'agent@frawo-tech.de')]])
    if existing_agent:
        agent_uid = existing_agent[0]
        print(f"   ♻️  Agent existiert bereits (UID {agent_uid})")
    else:
        # User anlegen (Passwort ist zweitrangig da er nur für API/Zuweisung genutzt wird)
        agent_uid = models.execute_kw(DB, uid, PASS, 'res.users', 'create', [{
            'name': '🤖 Agent',
            'login': 'agent@frawo-tech.de',
            'email': 'agent@frawo-tech.de',
            'notification_type': 'email',
            'groups_id': [(6, 0, [1, 2])] # Standard Internal User / Portal (abhängig vom System)
        }])
        print(f"   ✅ Agent angelegt (UID {agent_uid})")

    # --- 2. Master-Projekt finden ---
    existing_project = models.execute_kw(DB, uid, PASS, 'project.project', 'search', [[('name', '=', '🚀 Homeserver 2027: Masterplan')]])
    if not existing_project:
        print("❌ Fehler: Masterprojekt nicht gefunden!")
        return
    master_project_id = existing_project[0]

    # --- 3. Automation Stage anlegen ---
    print("\n⚙️  Erstelle Automation Stage...")
    automation_stage_name = '🤖 Automatisierung'
    existing_stage = models.execute_kw(DB, uid, PASS, 'project.task.type', 'search', [[('name', '=', automation_stage_name)]])
    if existing_stage:
        automation_stage_id = existing_stage[0]
        # Zuordnen
        models.execute_kw(DB, uid, PASS, 'project.task.type', 'write', [[automation_stage_id], {'project_ids': [(4, master_project_id)]}])
    else:
        automation_stage_id = models.execute_kw(DB, uid, PASS, 'project.task.type', 'create', [{
            'name': automation_stage_name,
            'sequence': 35, # Zwischen 'In Arbeit' und 'Done'
            'project_ids': [(4, master_project_id)]
        }])
    print(f"   ✅ Stage bereit (ID {automation_stage_id})")

    # --- 4. Tags anlegen ---
    print("\n🏷️  Erstelle Automation Tags...")
    tag_names = ['OCR: Beleg', 'INV: Rechnung']
    tag_ids = {}
    for t_name in tag_names:
        exist_tag = models.execute_kw(DB, uid, PASS, 'project.tags', 'search', [[('name', '=', t_name)]])
        if exist_tag:
            tag_ids[t_name] = exist_tag[0]
        else:
            tag_ids[t_name] = models.execute_kw(DB, uid, PASS, 'project.tags', 'create', [{'name': t_name}])
        print(f"   ✅ Tag: {t_name}")

    # --- 5. Full-Merge (12 & 13) ---
    print("\n📦 Full-Merge: Migriere Infra & Roadmap...")
    source_project_ids = [12, 13]
    tasks = models.execute_kw(DB, uid, PASS, 'project.task', 'search_read', [[('project_id', 'in', source_project_ids)]], {'fields': ['name', 'description', 'user_ids', 'project_id']})
    
    # Bestehende Tags im Master finden
    infra_tag = models.execute_kw(DB, uid, PASS, 'project.tags', 'search', [[('name', '=', 'Lane C: Infra 🛡️')]])
    roadmap_tag = models.execute_kw(DB, uid, PASS, 'project.tags', 'search', [[('name', '=', 'Lane B: Website 🌐')]]) # Vereinfachung

    for task in tasks:
        # Bestimmte Lane-Tags basierend auf altem Projekt
        new_tags = []
        if task['project_id'][0] == 12: new_tags = infra_tag
        if task['project_id'][0] == 13: new_tags = roadmap_tag

        models.execute_kw(DB, uid, PASS, 'project.task', 'write', [[task['id']], {
            'project_id': master_project_id,
            'tag_ids': [(4, tid) for tid in new_tags]
        }])
        print(f"   🚚 Verschoben: {task['name']}")

    # --- 6. Cleanup ---
    print("\n🧹 Cleanup: Entferne alte Projekte...")
    for p_id in source_project_ids:
        try:
            models.execute_kw(DB, uid, PASS, 'project.project', 'unlink', [[p_id]])
            print(f"   🗑️  Gelöscht: ID {p_id}")
        except Exception:
            print(f"   ⚠️  ID {p_id} konnte nicht gelöscht werden (vielleicht schon weg oder geschützt)")

    print("\n" + "="*60)
    print("🎉 Odoo Architektur-Upgrade abgeschlossen!")
    print(f"👤 User 'Agent' (agent@frawo-tech.de) ist bereit.")
    print(f"🤖 Stage 'Automatisierung' ist aktiv.")
    print("="*60)

if __name__ == "__main__":
    main()

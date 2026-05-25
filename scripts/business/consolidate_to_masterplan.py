import os
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath('.'))

from scripts.business.odoo_rpc_client import connect

CANONICAL_PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"
WOLF_LOGIN = "wolf@frawo-tech.de"
FRANZ_LOGIN = "franz@frawo-tech.de"
AGENT_LOGIN = "agent@frawo-tech.de"

# Stages mapping
STAGE_SPECS = [
    {"name": "📝 Backlog", "sequence": 10},
    {"name": "⚙️ Planung & Vorbereitung", "sequence": 20},
    {"name": "🚀 In Arbeit", "sequence": 30},
    {"name": "🤖 Automatisierung", "sequence": 35},
    {"name": "🛑 Blockiert", "sequence": 40},
    {"name": "✅ Erledigt", "sequence": 50},
]

# Lane tag mapping
LANE_TAG_NAMES = {
    "lane_a": "Lane A: MVP",
    "lane_b": "Lane B: Website",
    "lane_c": "Lane C: Infra",
    "lane_d": "Lane D: Stockenweiler",
    "lane_e": "Lane E: Radio & Media",
    "villa": "Villa Bienert",
    "anker": "Anker Lounge",
    "gbr": "FraWo GbR",
    "agent_tag": "🤖 Agent",
    "wolf_tag": "👤 Wolf",
    "franz_tag": "👤 Franz",
}

def clean_title(name):
    # Strip any existing prefixes to avoid duplicate prefixes
    cleaned = re.sub(r'^\[(🤖 AGENT|👤 WOLF|👤 FRANZ)\]\s*', '', name)
    return cleaned.strip()

def main():
    print("Starte globale Odoo-Konsolidierung ins Masterprojekt...")
    session = connect(default_user=WOLF_LOGIN, prompt_for_username=False)
    print(f"Verbunden mit Odoo ({session.url}) | DB: {session.db}")

    # 1. Finde oder erstelle das Masterplan-Projekt
    project_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.project', 'search',
        [[['name', 'ilike', 'Masterplan']]]
    )
    if not project_ids:
        print("Erstelle neues Masterplan-Projekt...")
        master_project_id = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'create',
            [{'name': CANONICAL_PROJECT_NAME, 'privacy_visibility': 'employees'}]
        )
    else:
        master_project_id = project_ids[0]
        # Ensure it has the correct canonical name
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'write',
            [[master_project_id], {'name': CANONICAL_PROJECT_NAME, 'active': True}]
        )
        print(f"Masterplan-Projekt gefunden (ID: {master_project_id})")

    # 2. Finde oder erstelle die kanonischen Stages für das Masterprojekt
    stage_lookup = {}
    for spec in STAGE_SPECS:
        stage_ids = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task.type', 'search',
            [[['name', '=', spec['name']]]]
        )
        if not stage_ids:
            print(f"Erstelle Stage: {spec['name']}")
            stage_id = session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.task.type', 'create',
                [{'name': spec['name'], 'sequence': spec['sequence'], 'project_ids': [(4, master_project_id)]}]
            )
        else:
            stage_id = stage_ids[0]
            # Link to our master project if not already linked
            session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.task.type', 'write',
                [[stage_id], {'project_ids': [(4, master_project_id)]}]
            )
        stage_lookup[spec['name']] = stage_id

    # 3. Finde oder erstelle Lane Tags
    tag_lookup = {}
    for key, tag_name in LANE_TAG_NAMES.items():
        tag_ids = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.tags', 'search',
            [[['name', '=', tag_name]]]
        )
        if not tag_ids:
            print(f"Erstelle Tag: {tag_name}")
            tag_id = session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.tags', 'create',
                [{'name': tag_name}]
            )
        else:
            tag_id = tag_ids[0]
        tag_lookup[key] = tag_id

    # 4. Finde Benutzer-IDs
    user_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'res.users', 'search',
        [[['login', 'in', [WOLF_LOGIN, FRANZ_LOGIN, AGENT_LOGIN]]]]
    )
    users = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'res.users', 'read',
        [user_ids, ['login', 'id']]
    )
    user_map = {u['login']: u['id'] for u in users}
    
    wolf_id = user_map.get(WOLF_LOGIN)
    franz_id = user_map.get(FRANZ_LOGIN)
    agent_id = user_map.get(AGENT_LOGIN)
    
    print(f"Benutzer-IDs aufgelöst: Wolf={wolf_id}, Franz={franz_id}, Agent={agent_id}")

    # 5. Hole alle Projekte, um deren Namen für das Tagging zu kennen
    projects = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.project', 'search_read',
        [[]],
        {'fields': ['id', 'name']}
    )
    project_map = {p['id']: p['name'] for p in projects}
    print(f"Gefundene Projekte in Odoo: {list(project_map.values())}")

    # 6. Hole alle Aufgaben (Tasks)
    tasks = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task', 'search_read',
        [[]], # get all tasks (active=True by default)
        {'fields': ['id', 'name', 'project_id', 'stage_id', 'user_ids', 'tag_ids', 'description']}
    )
    print(f"Hole {len(tasks)} Aufgaben aus Odoo...")

    # We define keywords to map owners and tags
    agent_keywords = [
        'caddy', 'dns', 'nginx', 'ssl', 'certificate', 'tailscale', 'wireguard', 
        'firewall', 'network', 'routing', 'monitoring', 'influx', 'telegraf', 
        'pbs', 'backup', 'rclone', 'git', 'openclaw', 'automation', 'docker', 
        'script', 'smtp', 'mail', 'css', 'webp', 'images', 'seo', 'xml-rpc', 
        'sync', 'api', 'cloudflare', 'head', 'brotli', 'compression', 'performance',
        'quality', 'qlity'
    ]
    
    franz_keywords = [
        'villa', 'dji', 'obs', 'growbox', 'growBox', 'growbox ii', 'stream', 
        'patchplan video', 'patchplan audio', 'signalplan', 'audio', 'video', 
        'platten', 'schallplatten', 'sortieren', 'studio'
    ]

    wolf_keywords = [
        'notar', 'finanzamt', 'gbr', 'vertrag', 'unterschrift', 'quonto', 
        'vollmacht', 'abfluss', 'badewanne', 'wasserhahn', 'gästetoilette', 
        'küche', 'schrank', 'wohnzimmer', 'pc start', 'stockenweiler einschalten', 
        'power-on', 'vor ort', 'gästetoilette / wc', 'badewanne - wasserhahn', 
        'schrank (unter der treppe)', 'abfluss'
    ]

    moved_count = 0
    updated_count = 0

    for task in tasks:
        # Skip the documentation task itself
        if "System-Dokumentation & SSOT" in task['name']:
            continue
            
        orig_proj_id = task['project_id'][0] if task['project_id'] else None
        orig_proj_name = task['project_id'][1] if task['project_id'] else ""
        
        # Decide tags based on original project name
        tags_to_add = []
        
        if "Lane A" in orig_proj_name or "Heritage" in orig_proj_name:
            tags_to_add.append(tag_lookup['lane_a'])
        elif "Lane B" in orig_proj_name or "Website" in orig_proj_name:
            tags_to_add.append(tag_lookup['lane_b'])
        elif "Lane C" in orig_proj_name or "Security" in orig_proj_name or "PBS" in orig_proj_name:
            tags_to_add.append(tag_lookup['lane_c'])
        elif "Lane D" in orig_proj_name or "Stockenweiler" in orig_proj_name:
            tags_to_add.append(tag_lookup['lane_d'])
        elif "Lane E" in orig_proj_name or "Radio" in orig_proj_name or "Media" in orig_proj_name:
            tags_to_add.append(tag_lookup['lane_e'])
        elif "Villa" in orig_proj_name:
            tags_to_add.append(tag_lookup['villa'])
        elif "Anker" in orig_proj_name:
            tags_to_add.append(tag_lookup['anker'])
        elif "GbR" in orig_proj_name:
            tags_to_add.append(tag_lookup['gbr'])
            
        task_name_lower = task['name'].lower()
        task_desc_lower = (task['description'] or '').lower()
        
        # Determine owner & prefix
        owner_id = None
        prefix = ""
        owner_tag = None
        
        # Apply keyword matching
        is_agent = any(k in task_name_lower or k in task_desc_lower for k in agent_keywords)
        is_franz = any(k in task_name_lower or k in task_desc_lower for k in franz_keywords)
        is_wolf = any(k in task_name_lower or k in task_desc_lower for k in wolf_keywords)
        
        if is_agent and not is_wolf:
            owner_id = agent_id
            prefix = "[🤖 AGENT]"
            owner_tag = tag_lookup['agent_tag']
        elif is_franz:
            owner_id = franz_id
            prefix = "[👤 FRANZ]"
            owner_tag = tag_lookup['franz_tag']
        else:
            # Default to Wolf for physical or business things, or keeping original if it's Wolf
            owner_id = wolf_id
            prefix = "[👤 WOLF]"
            owner_tag = tag_lookup['wolf_tag']
            
        if owner_tag:
            tags_to_add.append(owner_tag)

        # Merge existing tags
        existing_tags = [t for t in task['tag_ids']] if 'tag_ids' in task else []
        for t in tags_to_add:
            if t not in existing_tags:
                existing_tags.append(t)
                
        # Resolve stage mapping
        orig_stage_name = task['stage_id'][1] if task['stage_id'] else ""
        target_stage_id = None
        
        # If it's a known completed task, set stage to Erledigt
        completed_keywords = ['erledigt', 'abgeschlossen', 'verified', 'proof', 'done', 'success']
        blocked_keywords = ['blockiert', 'blocked', 'offline']
        
        if any(k in task_name_lower for k in completed_keywords):
            target_stage_id = stage_lookup['✅ Erledigt']
        elif any(k in task_name_lower or k in task_desc_lower for k in blocked_keywords) or ("Stockenweiler" in task['name'] and "Power" not in task['name']):
            # Stockenweiler-dependent tasks are blocked while server is offline
            target_stage_id = stage_lookup['🛑 Blockiert']
        elif "Planung" in orig_stage_name or "Vorbereitung" in orig_stage_name:
            target_stage_id = stage_lookup['⚙️ Planung & Vorbereitung']
        elif "Arbeit" in orig_stage_name or "Today" in orig_stage_name:
            target_stage_id = stage_lookup['🚀 In Arbeit']
        elif "Dringend" in orig_stage_name:
            target_stage_id = stage_lookup['🚀 In Arbeit']
        else:
            # If stage is empty or doesn't map, put it in backlog or planung based on status
            target_stage_id = stage_lookup['⚙️ Planung & Vorbereitung']

        # Construct updates
        raw_name = clean_title(task['name'])
        new_name = f"{prefix} {raw_name}"
        
        updates = {}
        if task['name'] != new_name:
            updates['name'] = new_name
            
        if orig_proj_id != master_project_id:
            updates['project_id'] = master_project_id
            moved_count += 1
            
        if target_stage_id and (not task['stage_id'] or task['stage_id'][0] != target_stage_id):
            updates['stage_id'] = target_stage_id
            
        # Update user_ids (assignee)
        desired_users = [owner_id] if owner_id else []
        actual_users = task['user_ids'] if 'user_ids' in task else []
        if sorted(actual_users) != sorted(desired_users):
            updates['user_ids'] = [(6, 0, desired_users)]
            
        # Update tags
        actual_tags = task['tag_ids'] if 'tag_ids' in task else []
        if sorted(actual_tags) != sorted(existing_tags):
            updates['tag_ids'] = [(6, 0, existing_tags)]

        # If there are updates, write them to Odoo!
        if updates:
            print(f"Aktualisiere Task #{task['id']} -> {new_name}: {list(updates.keys())}")
            session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.task', 'write',
                [[task['id']], updates]
            )
            updated_count += 1

    # 7. Speziellen Task für Stockenweiler Power-On erstellen
    stockenweiler_power_on_name = "[👤 WOLF] 🔌 Stockenweiler PVE physisch einschalten (Rothkreuz vor Ort)"
    stock_task_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task', 'search',
        [[['project_id', '=', master_project_id], ['name', 'ilike', 'Stockenweiler PVE physisch einschalten']]]
    )
    
    stock_desc = (
        "<h3><strong>🚨 DRINGENDE PHYSISCHE AKTION ERFORDERLICH</strong></h3>"
        "<p>Der Proxmox Backup Server / PVE Host in Stockenweiler (100.91.20.116 / 192.168.178.25) ist offline.</p>"
        "<ul>"
        "<li><strong>Aktion:</strong> Bitte fahre den Server vor Ort in Rothkreuz physisch hoch!</li>"
        "<li><strong>Betroffene Dienste:</strong> AzuraCast VM 210, HA Eltern VM 360, AdGuard CT 101, Vaultwarden CT 108.</li>"
        "<li><strong>Blockierte Tasks:</strong> Alle Radio-Tests (Lane E) und Support-Brücken (Lane D) sind blockiert, bis dieser Task erledigt ist.</li>"
        "</ul>"
        "<p>👉 <em>Sobald der Server läuft und über Tailscale pingbar ist, diesen Task auf ✅ Erledigt setzen.</em></p>"
    )
    
    stock_payload = {
        'name': stockenweiler_power_on_name,
        'project_id': master_project_id,
        'stage_id': stage_lookup['🚀 In Arbeit'],
        'user_ids': [(6, 0, [wolf_id])],
        'tag_ids': [(6, 0, [tag_lookup['lane_d'], tag_lookup['wolf_tag']])],
        'description': stock_desc
    }
    
    if not stock_task_ids:
        print("Erstelle Task für Stockenweiler physisches Power-On...")
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'create',
            [stock_payload]
        )
    else:
        print("Stockenweiler Power-On Task existiert bereits. Aktualisiere...")
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'write',
            [[stock_task_ids[0]], stock_payload]
        )

    # 8. Archiviere alle anderen Projekte, um die UI sauber zu machen!
    for p_id, p_name in project_map.items():
        if p_id != master_project_id:
            print(f"Archiviere Projekt: {p_name} (ID: {p_id})")
            session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.project', 'write',
                [[p_id], {'active': False}]
            )

    print("\n--- Konsolidierungs-Statistik ---")
    print(f"Aufgaben verschoben: {moved_count}")
    print(f"Aufgaben aktualisiert: {updated_count}")
    print("Die Konsolidierung war erfolgreich! Odoo ist nun das absolute SSOT-Board.")

if __name__ == "__main__":
    main()

import xmlrpc.client
import getpass
import sys

# --- KONFIGURATION ---
URL = "http://10.1.0.22:8069" 
DB = "FraWo_GbR"
DEFAULT_USER = "w.prinz1101@gmail.com"
PROJECT_NAME = "Private Networking (Masterplan)"

def sync():
    print("🔹 Odoo Advanced Masterplan Sync 🔹")
    print(f"Ziel: {URL} | Projekt: '{PROJECT_NAME}'")
    
    username = input(f"Odoo Login (Enter für '{DEFAULT_USER}'): ") or DEFAULT_USER
    password = getpass.getpass("Odoo Passwort: ")

    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, username, password, {})
        if not uid:
            print("❌ Fehler: Authentifizierung fehlgeschlagen.")
            return
        
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        print("✅ Verbindung steht.")

        # 1. Project Handling
        project_ids = models.execute_kw(DB, uid, password, 'project.project', 'search', [[('name', '=', PROJECT_NAME)]])
        if not project_ids:
            print(f"➕ Erstelle Projekt: '{PROJECT_NAME}'")
            project_id = models.execute_kw(DB, uid, password, 'project.project', 'create', [{'name': PROJECT_NAME}])
        else:
            project_id = project_ids[0]

        # 2. Tags Handling
        tags = ['Infrastructure', 'Security', 'Audit', 'MVP']
        tag_map = {}
        for tag_name in tags:
            existing = models.execute_kw(DB, uid, password, 'project.tags', 'search', [[('name', '=', tag_name)]])
            if not existing:
                t_id = models.execute_kw(DB, uid, password, 'project.tags', 'create', [{'name': tag_name}])
            else:
                t_id = existing[0]
            tag_map[tag_name] = t_id

        # 3. User Handling (Wolfi)
        user_ids = models.execute_kw(DB, uid, password, 'res.users', 'search', [[('name', 'ilike', 'Wolf')]])
        wolfi_id = user_ids[0] if user_ids else uid

        # 4. Tasks Definition
        tasks_to_sync = [
            {
                'name': '🔑 Vaultwarden Recovery-Material verifizieren',
                'description': '<ul><li>[ ] Zwei getrennte physische Offline-Kopien sicherstellen.</li></ul>',
                'project_id': project_id,
                'user_ids': [wolfi_id],
                'tag_ids': [tag_map['Security'], tag_map['MVP']],
                'priority': '1' # High
            },
            {
                'name': '📱 Geräte-Rollout abnehmen (Surface & iPhone)',
                'description': '<ul><li>[ ] Franz Endgeräte im Alltagspfad verifizieren.</li></ul>',
                'project_id': project_id,
                'user_ids': [wolfi_id],
                'tag_ids': [tag_map['Infrastructure']],
                'priority': '0' # Normal
            },
            {
                'name': '🌐 Tailscale Route freigeben (10.1.0.0/24)',
                'description': '<ul><li>[ ] Approve Route in Tailscale Admin Panel.</li></ul>',
                'project_id': project_id,
                'user_ids': [wolfi_id],
                'tag_ids': [tag_map['Infrastructure'], tag_map['Security']],
                'priority': '1'
            },
            {
                'name': '🌍 Tailscale Split-DNS (hs27.internal)',
                'description': '<ul><li>[ ] Nameserver 10.1.0.20 hinzufügen.</li></ul>',
                'project_id': project_id,
                'user_ids': [wolfi_id],
                'tag_ids': [tag_map['Infrastructure']],
                'priority': '1'
            }
        ]

        # 5. Sync Loop with Deduplication
        print("🚀 Synchronisiere Aufgaben...")
        for task_data in tasks_to_sync:
            existing_task = models.execute_kw(DB, uid, password, 'project.task', 'search', [[('name', '=', task_data['name']), ('project_id', '=', project_id)]])
            if existing_task:
                print(f"🟡 Überspringe (existiert bereits): {task_data['name']}")
                continue
            
            t_id = models.execute_kw(DB, uid, password, 'project.task', 'create', [task_data])
            print(f"✅ Erstellt: {task_data['name']} (ID: {t_id})")

        print("\n🎉 Odoo-Sync erfolgreich abgeschlossen!")

    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")

if __name__ == "__main__":
    sync()

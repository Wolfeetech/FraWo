"""
Odoo SSOT Sync — verbindet via Standard-XMLRPC, kein odoo_rpc_client nötig.
Setzt Board-Spalten auf Deutsch und synchronisiert Projekt-Tasks mit todo.md.
"""
import xmlrpc.client
import sys
import os

URL      = os.environ.get("ODOO_URL", "http://odoo.hs27.internal")
DB       = os.environ.get("ODOO_DB", "FraWo_GbR")
USER     = os.environ.get("ODOO_USER", "admin")
PASSWORD = os.environ.get("ODOO_PASSWORD", "admin")

PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"

STAGES = [
    {"name": "📝 Backlog",    "sequence": 10},
    {"name": "⚙️ Planung",   "sequence": 20},
    {"name": "🚀 In Arbeit", "sequence": 30},
    {"name": "🛑 Blockiert", "sequence": 40},
    {"name": "✅ Erledigt",  "sequence": 50},
]

TASK_MAP = {
    "post_restore_backup_proof":            "Post-Restore Backup Proof (ssd2tb)",
    "vm_firewall_hardening_reapply":        "VM Firewall Hardening (VM 210/220)",
    "pve_host_exposure_audit":              "PVE Host Exposure Audit",
    "ct100_storage_migration":              "CT 100 Migration auf ssd2tb",
    "split_dns_finalization":               "Split-DNS Finalisierung",
    "public_edge_https_release":            "Website Release (HTTPS)",
    "workspace_drift_guard":                "Workspace Drift Guard",
    "github_main_branch_protection":        "GitHub Branch Protection",
    "nextcloud_desktop_https_callback":     "Nextcloud Desktop HTTPS Fix",
    "odoo_project_ssot_sync":               "Odoo Project SSOT Sync",
    "odoo_sender_email_for_document_mail":  "Odoo E-Mail Absender Fix",
    "odoo_acl_res_users_log":               "Odoo ACL res.users.log",
    "radio_frontdoor_backend":              "Radio Backend (AzuraCast)",
    "ha_eltern_dashboard":                  "HA Eltern Dashboard",
    "pbs_guarded_rebuild":                  "PBS Rebuild",
    "wolf_admin_pc_ssh_key":                "wolf-admin-pc SSH-Key deployen",
}

def main():
    print(f"=== Odoo SSOT Sync -> {URL} / {DB} ===")

    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    try:
        uid = common.authenticate(DB, USER, PASSWORD, {})
    except Exception as e:
        print(f"FEHLER Verbindung: {e}")
        sys.exit(1)

    if not uid:
        print("FEHLER: Authentifizierung fehlgeschlagen (falsches Passwort?)")
        sys.exit(1)

    print(f"  Verbunden als uid={uid}")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    def execute(model, method, *args, **kw):
        return models.execute_kw(DB, uid, PASSWORD, model, method, list(args), kw)

    # 1. Sprache auf Deutsch setzen
    print("\n1. Sprache → de_DE")
    user_ids = execute('res.users', 'search', [['login', 'in', ['admin', 'wolf@frawo-tech.de']]])
    if user_ids:
        execute('res.users', 'write', user_ids, {'lang': 'de_DE'})
        print(f"   {len(user_ids)} Benutzer auf de_DE gesetzt.")

    # 2. Projekt finden oder anlegen
    print(f"\n2. Projekt: {PROJECT_NAME}")
    proj_ids = execute('project.project', 'search', [['name', '=', PROJECT_NAME]])
    if not proj_ids:
        proj_id = execute('project.project', 'create', {'name': PROJECT_NAME})
        print(f"   Projekt angelegt (id={proj_id})")
    else:
        proj_id = proj_ids[0]
        print(f"   Projekt gefunden (id={proj_id})")

    # 3. Board-Spalten (Stages) synchronisieren
    print("\n3. Board-Spalten")
    for stage in STAGES:
        existing = execute('project.task.type', 'search',
                           [['name', '=', stage['name']], ['project_ids', 'in', [proj_id]]])
        if not existing:
            sid = execute('project.task.type', 'create',
                          {'name': stage['name'], 'sequence': stage['sequence'],
                           'project_ids': [(4, proj_id)]})
            print(f"   + {stage['name']} (id={sid})")
        else:
            execute('project.task.type', 'write', existing, {'sequence': stage['sequence']})
            print(f"   ✓ {stage['name']}")

    # 4. Backlog-Stage als Default
    backlog = execute('project.task.type', 'search',
                      [['name', '=', '📝 Backlog'], ['project_ids', 'in', [proj_id]]])
    backlog_id = backlog[0] if backlog else None

    # 5. Tasks sicherstellen
    print("\n4. Tasks")
    for key, german_name in TASK_MAP.items():
        existing = execute('project.task', 'search',
                           [['project_id', '=', proj_id], ['name', '=', german_name]])
        if not existing:
            task_data = {'name': german_name, 'project_id': proj_id}
            if backlog_id:
                task_data['stage_id'] = backlog_id
            tid = execute('project.task', 'create', task_data)
            print(f"   + {german_name} (id={tid})")
        else:
            print(f"   ✓ {german_name}")

    print("\n=== Sync abgeschlossen ===")

if __name__ == '__main__':
    main()

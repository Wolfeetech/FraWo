from odoo_rpc_client import connect


print("Odoo Visibility Sync (Road to Production)")

session = connect(
    default_user="wolf@frawo-tech.de",
    prompt_for_username=True,
)
print(f"Verbinde zu {session.url} (DB: {session.db})...")
print("Authentifizierung erfolgreich!")

user_ids = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "res.users",
    "search",
    [[("name", "ilike", "Wolf")]],
)
assigned_user = user_ids[0] if user_ids else session.uid

tasks = [
    {
        "name": "Vaultwarden Recovery-Material verifizieren",
        "description": "<ul><li>[ ] Zwei getrennte physische Offline-Kopien des Vaultwarden-Zugriffs sicherstellen.</li></ul><p><strong>Zuweisung:</strong> Wolf</p>",
        "user_ids": [assigned_user],
    },
    {
        "name": "Geraete-Rollout abnehmen (Franz Surface & iPhone)",
        "description": "<ul><li>[ ] 2FA-Pfad des verlorenen Smartphones wiederherstellen</li><li>[ ] Franz Surface Laptop im echten Alltagspfad pruefen</li><li>[ ] Franz iPhone im echten Alltagspfad pruefen</li></ul><p><strong>Zuweisung:</strong> Wolf</p>",
        "user_ids": [assigned_user],
    },
    {
        "name": "Tailscale Route freigeben (10.1.0.0/24)",
        "description": "<ul><li>[ ] In login.tailscale.com/admin/machines die Route fuer toolbox approven</li></ul><p><strong>Zuweisung:</strong> Wolf</p>",
        "user_ids": [assigned_user],
    },
    {
        "name": "Tailscale Split-DNS aktualisieren",
        "description": "<ul><li>[ ] Nameserver 10.1.0.20 fuer hs27.internal im Tailnet hinterlegen</li></ul><p><strong>Zuweisung:</strong> Wolf</p>",
        "user_ids": [assigned_user],
    },
]

print("Lade 4 Aufgaben in Odoo hoch...")
for task in tasks:
    try:
        task_id = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task",
            "create",
            [task],
        )
        print(f"Aufgabe angelegt: {task['name']} (ID: {task_id})")
    except Exception as exc:
        print(f"Fehler bei '{task['name']}': {exc}")

print("Alles erledigt! Die Aufgaben sind im Projektmanagement importiert.")

import xmlrpc.client
import getpass
import sys

URL = "http://10.1.0.22:8069" # Interner direkter Odoo Pfad
DB = "FraWo_GbR"
USER = "w.prinz1101@gmail.com" # Oder admin, bitte anpassen, falls abweichend!

print("🔹 Odoo Visibility Sync (Road to Production) 🔹")
print(f"Verbinde zu {URL} (DB: {DB})...")

username = input(f"Odoo Login-E-Mail (Enter für '{USER}'): ") or USER
password = getpass.getpass("Odoo Passwort: ")

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
try:
    uid = common.authenticate(DB, username, password, {})
    if not uid:
        print("❌ Login fehlgeschlagen! Falsches Passwort.")
        sys.exit(1)
    print("✅ Authentifizierung erfolgreich!")
except Exception as e:
    print(f"❌ Verbindungsfehler: {e}")
    sys.exit(1)

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))

# Suche die ID von Wolfi
try:
    user_ids = models.execute_kw(DB, uid, password, 'res.users', 'search', [[('name', 'ilike', 'Wolf')]])
    assigned_user = user_ids[0] if user_ids else uid
except Exception:
    assigned_user = uid

tasks = [
    {
        'name': '🔑 Vaultwarden Recovery-Material verifizieren',
        'description': '<ul><li>[ ] Zwei getrennte physische Offline-Kopien (Papier etc.) des Vaultwarden-Zugriffs sicherstellen.</li></ul><p><strong>Zuweisung:</strong> Wolfi</p>',
        'user_ids': [assigned_user]
    },
    {
        'name': '📱 Geräte-Rollout abnehmen (Franz Surface & iPhone)',
        'description': '<ul><li>[ ] 2FA-Pfad des verlorenen Smartphones wiederherstellen</li><li>[ ] Franz "Surface Laptop" im echten Alltagspfad (inkl. 2FA) prüfen</li><li>[ ] Franz "iPhone" im echten Alltagspfad prüfen</li></ul><p><strong>Zuweisung:</strong> Wolfi</p>',
        'user_ids': [assigned_user]
    },
    {
        'name': '🌐 Tailscale Route freigeben (10.1.0.0/24)',
        'description': '<ul><li>[ ] In login.tailscale.com/admin/machines die Warnung bei <strong>toolbox</strong> anklicken</li><li>[ ] Route 10.1.0.0/24 auf <strong>Approve</strong> setzen</li></ul><p><strong>Zuweisung:</strong> Wolfi</p>',
        'user_ids': [assigned_user]
    },
    {
        'name': '🌍 Tailscale Split-DNS aktualisieren',
        'description': '<ul><li>[ ] In login.tailscale.com/admin/dns "Add nameserver -> Custom"</li><li>[ ] IP: 10.1.0.20</li><li>[ ] Restrict to domain: hs27.internal</li></ul><p><strong>Zuweisung:</strong> Wolfi</p>',
        'user_ids': [assigned_user]
    }
]

print("🚀 Lade 4 Aufgaben aus der OPERATOR_TODO_QUEUE in Odoo hoch...")
for task in tasks:
    try:
        task_id = models.execute_kw(DB, uid, password, 'project.task', 'create', [task])
        print(f"✅ Aufgabe angelegt: {task['name']} (ID: {task_id})")
    except Exception as e:
        print(f"❌ Fehler bei '{task['name']}': {e}")

print("🎉 Alles erledigt! Die Aufgaben sind im Projektmanagement importiert.")

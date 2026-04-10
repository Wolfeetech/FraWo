import xmlrpc.client
import getpass
import sys
import os

URL = "http://100.99.206.128:8444"
DB = "postgres"  
USER = "wolf@frawo-tech.de"  # The admin email defined in Vaultwarden for Odoo MVP

print("--- Odoo Projekt Map Sync: Lane C (Security/Infra) ---")
print(f"Verbinde zu {URL}...")

usernames = ["admin", "wolf@frawo-tech.de"]
db_names = ["FraWo_GbR", "odoo", "postgres", "homeserver"]
password = os.environ.get("ODOO_PASSWORD")

if not password:
    print("FEHLER: ODOO_PASSWORD Umgebungsvariable nicht gesetzt.")
    sys.exit(1)

uid = None
active_db = None
active_user = None

for user in usernames:
    for db in db_names:
        print(f"Versuche: User '{user}' auf DB '{db}'...")
        try:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
            uid = common.authenticate(db, user, password, {})
            if uid:
                print(f"BINGO! Login erfolgreich: User '{user}', DB '{db}'")
                active_db = db
                active_user = user
                break
        except Exception as e:
            # Skip errors that just mean "not here"
            continue
    if uid:
        break

if not uid:
    print("Login fehlgeschlagen. Keine gueltige Kombination aus User/DB gefunden.")
    sys.exit(1)

db_name = active_db
username = active_user
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))

tasks = [
    {
        'name': '[DONE] Phase 4: VLAN 101 Migration & DNS Recovery',
        'description': """
        <ul>
            <li>[x] Alle Core-VMs (Nextcloud, Odoo, Paperless, HA) sind in VLAN 101 (10.1.0.x) migriert.</li>
            <li>[x] DNS-Interception der EasyBox via AdGuard Home DoH umgangen.</li>
            <li>[x] Dokumentation (Masterplan, Live-Context, VM-Audit) aktualisiert.</li>
        </ul>
        """
    },
    {
        'name': '[Lane B] Website Release Gate & Public Edge',
        'description': """
        <ul>
            <li>[ ] STRATO DNS-Einträge für Public-Projekte vorbereiten.</li>
            <li>[ ] Caddy-Zertifikats-Automatisierung für externe Domains.</li>
            <li>[ ] Security-Sperre für interne Admin-Panels verifizieren.</li>
        </ul>
        """
    }
]

for task_data in tasks:
    try:
        task_id = models.execute_kw(db_name, uid, password, 'project.task', 'create', [task_data])
        print(f"Aufgabe '{task_data['name']}' erfolgreich in Odoo angelegt! (ID: {task_id})")
    except Exception as e:
        print(f"Fehler beim Erstellen: {e}")

print("Schau jetzt auf dein Odoo Kanboard und verlagere die aktiven Lanes.")

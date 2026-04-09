import xmlrpc.client
import getpass
import sys

URL = "http://odoo.hs27.internal"
DB = "postgres"  
USER = "wolf@frawo-tech.de"  # The admin email defined in Vaultwarden for Odoo MVP

print("🔹 Odoo Projekt Map Sync: Lane C (Security/Infra) 🔹")
print(f"Verbinde zu {URL}...")

db_name = DB
username = input(f"Benutzername (Enter für '{USER}'): ") or USER
password = getpass.getpass("Odoo Admin Passwort: ")

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
try:
    uid = common.authenticate(db_name, username, password, {})
    if not uid:
        print("❌ Login fehlgeschlagen! Falsches Passwort.")
        sys.exit(1)
    print("✅ Login erfolgreich!")
except Exception as e:
    print(f"❌ Verbindungsfehler: {e}")
    sys.exit(1)

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))

tasks = [
    {
        'name': '🚀 [Lane C] Tailscale Route Approval (10.1.0.0/24)',
        'description': """
        <ul>
            <li>[ ] In <a href="https://login.tailscale.com/admin/machines">Tailscale Admin</a> die beworbene Route 10.1.0.0/24 bei <b>toolbox</b> approven.</li>
            <li>[ ] Route springt auf active</li>
            <li>[ ] Nach Freigabe die KI anweisen "tailscale status verifizieren"</li>
        </ul>
        """
    },
    {
        'name': '🚀 [Lane C] Tailscale Split DNS Update',
        'description': """
        <ul>
            <li>[ ] In <a href="https://login.tailscale.com/admin/dns">Tailscale DNS</a> den restricted Nameserver fuer 'hs27.internal' und 'frawo-tech.de' auf <b>10.1.0.20</b> umstellen.</li>
            <li>[ ] Remote-Clients erreichen portal, ha, odoo via internen Domainnamen.</li>
            <li>[ ] KI anweisen "DNS Check abschließen"</li>
        </ul>
        """
    }
]

for task_data in tasks:
    try:
        task_id = models.execute_kw(db_name, uid, password, 'project.task', 'create', [task_data])
        print(f"🎉 Aufgabe '{task_data['name']}' erfolgreich in Odoo angelegt! (ID: {task_id})")
    except Exception as e:
        print(f"❌ Fehler beim Erstellen: {e}")

print("👉 Schau jetzt auf dein Odoo Kanboard und verlagere die aktiven Lanes.")

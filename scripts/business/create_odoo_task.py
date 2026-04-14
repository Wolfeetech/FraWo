import xmlrpc.client
import getpass
import sys

URL = "http://odoo.hs27.internal"
DB = "postgres"  # Common default, might also be odoo depending on setup
USER = "admin"   # Adjust as necessary

print("🔹 Odoo To-Do WOW-Moment Generator 🔹")
print(f"Verbinde zu {URL}...")

db_name = input(f"Datenbankname (Enter für '{DB}'): ") or DB
username = input(f"Benutzername (Enter für '{USER}'): ") or USER
password = getpass.getpass("Odoo Passwort: ")

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
try:
    uid = common.authenticate(db_name, username, password, {})
    if not uid:
        print("❌ Login fehlgeschlagen! Falsches Passwort oder DB.")
        sys.exit(1)
    print("✅ Authentifizierung erfolgreich!")
except Exception as e:
    print(f"❌ Verbindungsfehler: {e}")
    sys.exit(1)

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))

task_data = {
    'name': '🚀 Endgeräte Franz onboarden (WOW Moment)',
    'description': """
    <ul>
        <li>[ ] Surface Go aushändigen und Passwörter testen</li>
        <li>[ ] Nextcloud Mail-App Testnachricht in Paperless prüfen</li>
        <li>[ ] AnyDesk-ID verifizieren & Erstverbindung vom Studio PC aufbauen</li>
        <li>[ ] Das neue FRAWO-Portal als Startseite im Browser auf dem Kiosk-Tablet fixieren</li>
    </ul>
    """
}

# In Odoo, To-Dos and tasks are tracked in project.task
try:
    task_id = models.execute_kw(db_name, uid, password, 'project.task', 'create', [task_data])
    print(f"🎉 WOW Moment: Aufgabe erfolgreich in Odoo angelegt! (ID: {task_id})")
    print("👉 Schau in dein Odoo Whiteboard / To-Dos rein!")
except Exception as e:
    print(f"❌ Fehler beim Erstellen der Aufgabe: {e}")
    print("💡 Falls 'project.task' nicht existiert, nutze bitte die CSV/manuelle Integration.")

from odoo_rpc_client import connect
import sys

user = "wolf@frawo-tech.de"
try:
    print(f"Verifiziere Credentials fuer {user}...")
    session = connect(default_user=user)
    print("✅ Authentifizierung erfolgreich!")
    # Test read
    projects = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.project', 'search_count', [[]]
    )
    print(f"Verbindung steht. Projekte gefunden: {projects}")
except Exception as e:
    print(f"❌ Fehler: {e}")
    sys.exit(1)

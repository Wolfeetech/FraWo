import sys
import os
from pathlib import Path

# Add paths
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "scripts"))
sys.path.append(str(ROOT / "scripts" / "business"))

from odoo_rpc_client import connect

user = "admin"
os.environ["ODOO_RPC_PASSWORD"] = "admin"

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

import sys
import xmlrpc.client
from pathlib import Path

# Odoo Connection Parameters
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

from odoo_env import resolve_connection


DEFAULT_URL = "http://10.1.0.22:8069"
DEFAULT_DB = "FraWo_Live"
DEFAULT_USER = "admin"

# HOMEPAGE CONTENT (Simplified XML-RPC safe)
HOMEPAGE_ARCH = '''<?xml version="1.0"?>
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
            <div class="frawo-homepage">
              <section class="frawo-hero" style="padding:120px 0; background:#090b0a; color:white; text-align:center;">
                <div class="container">
                  <h1 style="font-size:5rem; color:#b0ff00; font-family:sans-serif;">Planung, Betrieb,<br/>digitale Begleitung.</h1>
                  <p style="font-size:1.5rem; color:#8a948e;">Macher statt Blabla. Fuerr das Event, das Netzwerk und die digitale Organisation.</p>
                  <a href="/contactus" style="display:inline-block; margin-top:40px; padding:20px 40px; background:#b0ff00; color:black; text-decoration:none; font-weight:bold;">Projekt anreissen</a>
                </div>
              </section>
            </div>
        </div>
    </t>
</t>'''

def deploy():
    settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    print(f"Connecting to Odoo at {settings.url}...")
    try:
        common = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/common")
        uid = common.authenticate(settings.db, settings.user, settings.secret, {})
        if not uid:
            print("Authentication failed!")
            return
        
        models = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/object")
        
        # Find all website homepage views
        view_ids = models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'search', [[['key', '=', 'website.homepage']]])
        print(f"Found views: {view_ids}")
        
        for vid in view_ids:
            models.execute_kw(settings.db, uid, settings.secret, 'ir.ui.view', 'write', [[vid], {'arch_db': HOMEPAGE_ARCH}])
            print(f"Updated view {vid}")

        print("\nSUCCESS: Design forced onto all layers.")

    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    deploy()

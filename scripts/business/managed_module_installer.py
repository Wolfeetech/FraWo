import os
import xmlrpc.client
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_Live"
ODOO_USER = "admin"
ODOO_PASS = "admin"

def install_project_module():
    print(f"Connecting to {ODOO_DB} to install 'project' module...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    try:
        session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
        
        # 1. Search for 'project' module
        module_ids = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'ir.module.module', 'search',
            [[['name', '=', 'project']]]
        )
        
        if not module_ids:
            print("Error: Could not find 'project' module in Odoo records.")
            return

        # 2. Trigger Installation
        print(f"Triggering immediate installation of module ID: {module_ids[0]}...")
        result = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'ir.module.module', 'button_immediate_install',
            [module_ids]
        )
        print("Success: Project module installation triggered. Service will now restart/rebuild.")
        
    except Exception as e:
        print(f"Failed to install module: {e}")

if __name__ == "__main__":
    install_project_module()

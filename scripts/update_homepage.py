#!/usr/bin/env python3
import os
import sys
import xmlrpc.client
from pathlib import Path

def main():
    # Load credentials from .env
    env_file = Path("C:/Users/StudioPC/.ai-tools-shared/.env")
    if env_file.exists():
        for line in open(env_file):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

    url = os.getenv("ODOO_URL", "http://10.1.0.112:8069")
    db = os.getenv("ODOO_DB_GBR", "FraWo_GbR")
    user = os.getenv("ODOO_USER", "wolf@frawo-tech.de")
    pw = os.getenv("ODOO_PASSWORD", "Wolf2024!Frawo")

    print(f"Connecting to {url}...")
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, user, pw, {})
        if not uid:
            print("Auth failed")
            return 1
        print(f"Auth OK, UID: {uid}")

        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
        
        # Read homepage
        pages = models.execute_kw(
            db, uid, pw,
            'website.page', 'search_read',
            [[['url', '=', '/']]],
            {'fields': ['id', 'arch']}
        )

        if not pages:
            print("Homepage not found.")
            return 1

        page = pages[0]
        arch = page['arch']

        # Define the target string and replacement
        target = '<a href="https://funk.frawo-tech.de" class="fw-btn-ghost btn mt-3">Zu FraWo Funk →</a>'
        
        replacement = """<div class="mt-4" style="max-width: 400px; margin: 0 auto;">
          <iframe src="https://funk.frawo-tech.de/public/frawo_funk?theme=dark" frameborder="0" allowtransparency="true" style="width: 100%; min-height: 150px; border: 0;"></iframe>
        </div>
        <a href="https://funk.frawo-tech.de" class="fw-btn-ghost btn mt-3">Vollbild Player →</a>"""

        if target not in arch:
            print("Target string not found in homepage architecture.")
            # Let's try to find it with different spacing or just look for the radio section
            if 'fw-radio-cta' in arch:
                print("Found 'fw-radio-cta' section, but link text differs. Aborting for safety.")
            else:
                print("Radio section not found.")
            return 1

        print("Target found. Performing replacement...")
        new_arch = arch.replace(target, replacement)

        # Write back
        result = models.execute_kw(
            db, uid, pw,
            'website.page', 'write',
            [[page['id']], {'arch': new_arch}]
        )

        if result:
            print(f"Successfully updated homepage (ID: {page['id']})")
        else:
            print("Failed to update homepage.")

    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

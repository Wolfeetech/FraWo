#!/usr/bin/env python3
import os
import sys
import xmlrpc.client
from pathlib import Path
import base64

def main():
    # Load credentials from .env
    env_file = Path("C:/Users/StudioPC/.ai-tools-shared/.env")
    if env_file.exists():
        for line in open(env_file):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

    url = os.getenv("ODOO_URL", "http://10.4.0.22:8069")
    db = os.getenv("ODOO_DB_GBR", "FraWo_GbR")
    user = os.getenv("ODOO_USER", "wolf@frawo-tech.de")
    pw = os.getenv("ODOO_PASSWORD", "Wolf2024!Frawo")

    logo_path = Path("brand_assets/1.png")
    if not logo_path.exists():
        print(f"Logo file not found at {logo_path}")
        return 1

    print(f"Reading logo {logo_path}...")
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode('utf-8')

    print(f"Connecting to {url}...")
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, user, pw, {})
        if not uid:
            print("Auth failed")
            return 1
        print(f"Auth OK, UID: {uid}")

        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
        
        # Get current company
        companies = models.execute_kw(
            db, uid, pw,
            'res.company', 'search_read',
            [[]],
            {'fields': ['id', 'name']}
        )

        if not companies:
            print("No companies found.")
            return 1

        company = companies[0]
        print(f"Found Company: {company['name']} (ID: {company['id']})")

        # Update logo
        print("Uploading logo...")
        result = models.execute_kw(
            db, uid, pw,
            'res.company', 'write',
            [[company['id']], {'logo': logo_data}]
        )

        if result:
            print(f"Successfully updated logo for company {company['name']}")
        else:
            print("Failed to update logo.")

    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

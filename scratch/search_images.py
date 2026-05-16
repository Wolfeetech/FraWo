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

    url = os.getenv("ODOO_URL", "http://10.4.0.22:8069")
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
        
        # Search for attachments that are images
        images = models.execute_kw(
            db, uid, pw,
            'ir.attachment', 'search_read',
            [[['mimetype', '=like', 'image/%']]],
            {'fields': ['id', 'name', 'mimetype', 'create_date'], 'order': 'create_date desc'}
        )

        print(f"Found {len(images)} images in Odoo:")
        for img in images:
            print(f"ID: {img['id']} | Name: {img['name']} | Type: {img['mimetype']} | Date: {img['create_date']}")

    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

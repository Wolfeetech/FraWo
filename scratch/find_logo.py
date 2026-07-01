#!/usr/bin/env python3
import os
import xmlrpc.client
from pathlib import Path

def main():
    url = "http://10.1.0.112:8069"
    db = "FraWo_GbR"
    user = "wolf@frawo-tech.de"
    pw = "Wolf2024!Frawo"

    print(f"Connecting to {url}...")
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, user, pw, {})
        if not uid:
            print("Auth failed")
            return 1
        print(f"Auth OK, UID: {uid}")

        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
        
        # Search for attachments with 'logo' in name
        images = models.execute_kw(
            db, uid, pw,
            'ir.attachment', 'search_read',
            [[['mimetype', '=like', 'image/%'], ['name', 'ilike', 'logo']]],
            {'fields': ['id', 'name', 'mimetype', 'create_date'], 'order': 'create_date desc'}
        )

        print(f"\nFound {len(images)} images with 'logo':")
        for img in images:
            print(f"ID: {img['id']} | Name: {img['name']} | Type: {img['mimetype']} | Date: {img['create_date']}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())

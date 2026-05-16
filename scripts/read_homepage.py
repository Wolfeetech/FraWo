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
        
        # Search for homepage
        pages = models.execute_kw(
            db, uid, pw,
            'website.page', 'search_read',
            [[['url', '=', '/']]],
            {'fields': ['id', 'name', 'arch', 'url']}
        )

        if not pages:
            print("Homepage not found by URL '/'")
            # Try searching by name
            pages = models.execute_kw(
                db, uid, pw,
                'website.page', 'search_read',
                [[['name', 'ilike', 'home']]],
                {'fields': ['id', 'name', 'arch', 'url']}
            )

        if pages:
            for p in pages:
                print(f"Found Page ID: {p['id']}, Name: {p['name']}, URL: {p['url']}")
                print("Content Preview (first 500 chars):")
                print(p['arch'][:500] if p['arch'] else "No content")
                print("-" * 40)
                
                # Save full content to a file for inspection
                with open(f"scratch/homepage_arch_{p['id']}.html", "w", encoding="utf-8") as f:
                    f.write(p['arch'] or "")
                print(f"Saved full content to scratch/homepage_arch_{p['id']}.html")
        else:
            print("No pages found.")

    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

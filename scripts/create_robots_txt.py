#!/usr/bin/env python3
"""Create and upload robots.txt to FraWo Website"""
import os, sys, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

ROBOTS_TXT = """User-agent: *
Allow: /

# Sitemaps
Sitemap: https://www.frawo-tech.de/sitemap.xml

# Block admin areas
Disallow: /web/
Disallow: /admin/
Disallow: /my/

# Allow images and CSS
Allow: /web/image/
Allow: /web/content/

# Crawl delay (be nice to smaller servers)
Crawl-delay: 1
"""

def create_robots_txt():
    """Upload robots.txt to Odoo static files"""

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        sys.exit(1)

    print(f"[OK] Authenticated (UID: {uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Check if robots.txt already exists
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.attachment', 'search_read',
        [[['name', '=', 'robots.txt'], ['url', '=', '/robots.txt']]],
        {'fields': ['id', 'name', 'url']}
    )

    if existing:
        print(f"[*] Found existing robots.txt (ID: {existing[0]['id']})")
        # Update existing
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'write',
            [[existing[0]['id']], {
                'datas': ROBOTS_TXT.encode('utf-8'),
                'mimetype': 'text/plain',
            }]
        )
        print("[OK] Updated robots.txt")
    else:
        # Create new
        import base64
        attachment_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'create',
            [{
                'name': 'robots.txt',
                'type': 'binary',
                'datas': base64.b64encode(ROBOTS_TXT.encode('utf-8')).decode('utf-8'),
                'mimetype': 'text/plain',
                'url': '/robots.txt',
                'public': True,
            }]
        )
        print(f"[OK] Created robots.txt (ID: {attachment_id})")

    print("\n[*] Content:")
    print(ROBOTS_TXT)

if __name__ == '__main__':
    create_robots_txt()

#!/usr/bin/env python3
"""Generate and upload sitemap.xml for FraWo Website"""
import os, sys, xmlrpc.client, base64
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

def generate_sitemap():
    """Generate sitemap.xml from Odoo pages"""

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        sys.exit(1)

    print(f"[OK] Authenticated (UID: {uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Get all published pages
    pages = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'website.page', 'search_read',
        [[['website_published', '=', True]]],
        {'fields': ['url', 'write_date']}
    )

    print(f"[*] Found {len(pages)} published pages")

    # Build sitemap XML
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        url = page['url']
        if not url:
            continue

        # Convert Odoo timestamp to W3C Datetime format
        write_date = page.get('write_date', datetime.now().isoformat())
        if isinstance(write_date, str):
            # Parse Odoo datetime format: "2026-05-14 12:30:45"
            try:
                dt = datetime.fromisoformat(write_date.replace(' ', 'T'))
                lastmod = dt.strftime('%Y-%m-%d')
            except:
                lastmod = datetime.now().strftime('%Y-%m-%d')
        else:
            lastmod = datetime.now().strftime('%Y-%m-%d')

        # Priority: homepage highest, others lower
        priority = '1.0' if url == '/' else '0.8'

        # Change frequency
        changefreq = 'weekly' if url == '/' else 'monthly'

        sitemap += f'  <url>\n'
        sitemap += f'    <loc>https://www.frawo-tech.de{url}</loc>\n'
        sitemap += f'    <lastmod>{lastmod}</lastmod>\n'
        sitemap += f'    <changefreq>{changefreq}</changefreq>\n'
        sitemap += f'    <priority>{priority}</priority>\n'
        sitemap += f'  </url>\n'

    sitemap += '</urlset>\n'

    print("[*] Generated sitemap.xml")
    print(f"\n{sitemap}")

    # Check if sitemap.xml already exists
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.attachment', 'search_read',
        [[['name', '=', 'sitemap.xml'], ['url', '=', '/sitemap.xml']]],
        {'fields': ['id', 'name', 'url']}
    )

    sitemap_b64 = base64.b64encode(sitemap.encode('utf-8')).decode('utf-8')

    if existing:
        print(f"[*] Found existing sitemap.xml (ID: {existing[0]['id']})")
        # Update existing
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'write',
            [[existing[0]['id']], {
                'datas': sitemap_b64,
                'mimetype': 'application/xml',
            }]
        )
        print("[OK] Updated sitemap.xml")
    else:
        # Create new
        attachment_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'create',
            [{
                'name': 'sitemap.xml',
                'type': 'binary',
                'datas': sitemap_b64,
                'mimetype': 'application/xml',
                'url': '/sitemap.xml',
                'public': True,
            }]
        )
        print(f"[OK] Created sitemap.xml (ID: {attachment_id})")

    print("\n[*] Sitemap available at: https://www.frawo-tech.de/sitemap.xml")
    print("[*] Submit to Google Search Console: https://search.google.com/search-console")

if __name__ == '__main__':
    generate_sitemap()

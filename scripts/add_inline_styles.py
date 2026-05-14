#!/usr/bin/env python3
"""Add inline styles directly to service cards to override everything"""
import os, sys, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

# Ultra-compact CSS that MUST override everything
OVERRIDE_CSS = """
<style id="frawo-override">
/* NUCLEAR OPTION - Override everything with max specificity */
.fw-services .fw-service-card,
.fw-service-card.fw-service-card-bg,
section.fw-services .col-lg-6 .fw-service-card {
  padding: 1rem 1.25rem !important;
  min-height: 240px !important;
  margin: 0 !important;
}

.fw-service-card .fw-h3,
.fw-service-card h3.fw-h3 {
  margin-bottom: 0.5rem !important;
  margin-top: 0 !important;
}

.fw-service-card .fw-service-desc,
.fw-service-card p.fw-service-desc {
  margin-bottom: 0.5rem !important;
  margin-top: 0 !important;
}

.fw-service-card .fw-service-list,
.fw-service-card ul.fw-service-list {
  margin: 0 0 0.75rem 0 !important;
  padding: 0 !important;
}

.fw-service-card .fw-service-list li,
.fw-service-card ul.fw-service-list li {
  padding: 0.15rem 0 0.15rem 1.25rem !important;
  margin: 0 !important;
  line-height: 1.4 !important;
}

/* Referenzen ultra-compact */
.fw-referenzen .fw-ref-item,
.fw-ref-item {
  padding: 1.5rem 1rem !important;
  min-height: 120px !important;
}

/* Section spacing */
section.fw-services,
section.fw-referenzen,
section.fw-projects,
section.fw-about {
  padding: 60px 0 !important;
}

.fw-section-header {
  margin-bottom: 40px !important;
}
</style>
"""

def main():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Auth failed!")
        sys.exit(1)

    print(f"[OK] Authenticated (UID: {uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Get website
    websites = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website', 'search_read', [[]], {'fields': ['id', 'custom_code_head'], 'limit': 1})

    if websites:
        website = websites[0]
        current_head = website['custom_code_head'] or ''

        # Remove old override if exists
        if '<style id="frawo-override">' in current_head:
            start = current_head.find('<style id="frawo-override">')
            end = current_head.find('</style>', start) + 8
            current_head = current_head[:start] + current_head[end:]

        # Add new override at the END (highest priority)
        updated_head = current_head + "\n" + OVERRIDE_CSS

        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website', 'write', [[website['id']], {'custom_code_head': updated_head}])

        print("[OK] Nuclear override styles added!")
        print("[*] These styles will override EVERYTHING with max specificity")

if __name__ == '__main__':
    main()

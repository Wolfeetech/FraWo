# -*- coding: utf-8 -*-
import xmlrpc.client

url = "http://10.1.0.22:8069"
db = "FraWo_GbR"
username = "wolf@frawo-tech.de"
password = "Wolf2024!Frawo"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# NUCLEAR CSS - No more white screen
nuclear_css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root { 
  --fw-bg: #0a0a0a !important; 
  --fw-text: #f0f0f0 !important; 
}

/* Force dark background on EVERY possible container */
html, body, #wrapwrap, main, #wrap, 
.oe_structure, section, .container, .row, .col-lg-6, .col-12,
.navbar, .navbar-collapse, .footer, #footer, .o_footer {
  background-color: #0a0a0a !important;
  background: #0a0a0a !important;
  color: #f0f0f0 !important;
  opacity: 1 !important;
  visibility: visible !important;
  display: block !important;
}

/* Typography */
* { font-family: 'Inter', sans-serif !important; }

/* Header Glassmorphism */
header#top {
  background: rgba(10, 10, 10, 0.8) !important;
  backdrop-filter: blur(15px) !important;
  -webkit-backdrop-filter: blur(15px) !important;
  border-bottom: 1px solid rgba(255,255,255,0.1) !important;
}

/* Hide Odoo watermarks */
.o_footer_copyright, .o_brand_promotion { display: none !important; }

/* Link Colors */
a { color: #a855f7 !important; }
a.btn { color: inherit !important; }
</style>"""

print("Applying Nuclear CSS...")
models.execute_kw(db, uid, password, 'website', 'write', [[1], {
    'custom_code_head': nuclear_css,
    'homepage_id': models.execute_kw(db, uid, password, 'website.page', 'search', [[['url', '=', '/']]])[0]
}])

# Fix Favicon to HTTPS
print("Fixing Favicon...")
models.execute_kw(db, uid, password, 'website', 'write', [[1], {'favicon': False}]) # Reset to default if needed, or provide base64

print("Syncing final task status...")
project = models.execute_kw(db, uid, password, 'project.project', 'search', [[['name', '=', 'FraWo Website v3.5 & Infrastructure']]])
if project:
    models.execute_kw(db, uid, password, 'project.task', 'create', [{
        'name': 'Verify Website Visibility (Manual Check)',
        'project_id': project[0],
        'description': 'Confirmed global CSS injection and forced dark layout. Verification pending.'
    }])

print("NUCLEAR_FIX_DONE")

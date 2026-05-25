import os
import sys
import xmlrpc.client

ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

print("[*] Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    print("[FAIL] Auth failed")
    sys.exit(1)

print(f"[OK] Auth OK (UID:{uid})")
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# 1. Check installed modules
print("\n=== Checking installed modules ===")
modules = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'ir.module.module', 'search_read',
    [[['name', 'in', ['crm', 'website', 'website_crm', 'website_form']], ['state', '=', 'installed']]],
    {'fields': ['name', 'state', 'summary']}
)
for m in modules:
    print(f"Module: {m['name']} | State: {m['state']} | Summary: {m['summary']}")

# 2. Check if crm.lead website form is allowed/configured
print("\n=== Checking website form models ===")
# In Odoo, model forms are allowed by website.form.model or website_form_label, or standard security config.
# Let's search for ir.model configurations related to website form
lead_model = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'ir.model', 'search_read',
    [[['model', '=', 'crm.lead']]],
    {'fields': ['name', 'model', 'website_form_access', 'website_form_label']}
)
print(f"crm.lead Model Info: {lead_model}")

# 3. Check Odoo CRM leads
print("\n=== Checking recent CRM leads ===")
leads = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'crm.lead', 'search_read',
    [[]],
    {'fields': ['id', 'name', 'contact_name', 'email_from', 'phone', 'description', 'create_date'], 'limit': 5}
)
for l in leads:
    print(f"Lead ID {l['id']}: {l['name']} | Contact: {l['contact_name']} | Email: {l['email_from']} | Date: {l['create_date']}")

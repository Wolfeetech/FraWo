import xmlrpc.client
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# 1. Update Company Layout and Footer
# Find layout "Clean" or "Boxed" (usually view_id in ir.ui.view with key web.external_layout_clean)
layout_views = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search_read', [[('key', 'ilike', 'external_layout_clean')]], {'fields': ['id']})
layout_id = layout_views[0]['id'] if layout_views else False

company = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'search_read', [[]], {'limit': 1})[0]
cid = company['id']

footer_text = "FraWo GbR | Rothkreuz 14, 88138 Weißensberg\nGeschäftsführer: Wolfgang Prinz & Franz Bienert\nIBAN: DE99 9999 9999 9999 9999 99 | BIC: XXXXXXXX\nSteuernummer: 123/456/7890 | USt-IdNr.: DE123456789"

vals = {
    'report_footer': footer_text,
    'company_registry': 'GbR',
}
if layout_id:
    vals['external_report_layout_id'] = layout_id

models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'write', [[cid], vals])
print("Company layout and footer updated.")

# 2. Create Test Customer
partner_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'search', [[('name', '=', 'FraWo Testkunde')]])
if not partner_ids:
    partner_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'create', [{
        'name': 'FraWo Testkunde',
        'is_company': True,
        'email': 'test@frawo-tech.de'
    }])
    print("Test customer created.")
else:
    partner_id = partner_ids[0]
    print("Test customer already exists.")

# 3. Create a Test Invoice (account.move)
# Need an income account
accounts = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'account.account', 'search_read', [[('account_type', '=', 'income')]], {'limit': 1, 'fields': ['id']})
income_account_id = accounts[0]['id'] if accounts else False

invoice_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'account.move', 'create', [{
    'move_type': 'out_invoice',
    'partner_id': partner_id,
    'invoice_date': '2026-05-21',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Beratungsleistung / IT Service (Test)',
            'quantity': 1,
            'price_unit': 150.00,
            'account_id': income_account_id
        })
    ]
}])

# Post the invoice
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'account.move', 'action_post', [[invoice_id]])
print(f"Test Invoice created and posted. Move ID: {invoice_id}")

# 4. Close Task 161
done_stage = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search', [[('name', 'ilike', 'Erledigt')]])
if done_stage:
    done_stage_id = done_stage[0]
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'message_post', [161], {'body': 'Rechnungs-Workflow inkl. CI-Layout, Footer (mit Platzhaltern) und Testrechnung erfolgreich eingerichtet.'})
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[161], {'stage_id': done_stage_id, 'state': '1_done'}])
    print("Task 161 closed.")

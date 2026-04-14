import xmlrpc.client
URL = 'http://10.1.0.22:8069'
DB = 'FraWo_GbR'
USER = 'wolf@frawo-tech.de'
PASSWORD = 'OD-Wolf-2026!'

try:
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

    home_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', '=', 'website.homepage']]])
    if home_ids:
        arch = '<?xml version="1.0"?>\n<t name="Homepage" t-name="website.homepage">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty"/>\n    </t>\n</t>'
        models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [home_ids, {'arch_db': arch}])
        print('Homepage restored.')

    contact_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', 'ilike', 'contactus']]])
    if contact_ids:
        arch_c = '<?xml version="1.0"?>\n<t name="Contact us" t-name="website.contactus">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty"/>\n    </t>\n</t>'
        models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [contact_ids, {'arch_db': arch_c}])
        print('Contact page restored.')

    print('Rollback Complete.')
except Exception as e:
    print('Error:', e)

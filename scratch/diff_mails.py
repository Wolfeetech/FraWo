import xmlrpc.client

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

def safe_repr(val):
    if isinstance(val, str):
        return val.encode('ascii', errors='replace').decode('ascii')
    return repr(val)

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    fields_def = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'fields_get',
        [],
        {'attributes': ['type']}
    )
    
    excluded_fields = {'body_html', 'body', 'attachment_ids', 'body_content'}
    fields_to_read = [f for f, attr in fields_def.items() if attr['type'] not in ['binary', 'one2many'] and f not in excluded_fields]
    
    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[['id', 'in', [307, 310]]]],
        {'fields': fields_to_read}
    )
    
    mail_map = {m['id']: m for m in mails}
    m307 = mail_map.get(307, {})
    m310 = mail_map.get(310, {})
    
    print("\n--- DIFFERENCES BETWEEN 307 (FAIL) and 310 (SUCCESS) ---")
    for f in sorted(fields_to_read):
        v307 = m307.get(f)
        v310 = m310.get(f)
        if v307 != v310:
            print(f"Field: {f}")
            print(f"  307 (FAIL)   : {safe_repr(v307)}")
            print(f"  310 (SUCCESS): {safe_repr(v310)}")
            print("-" * 40)

if __name__ == '__main__':
    main()

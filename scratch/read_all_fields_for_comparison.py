import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

def safe_str(val):
    if isinstance(val, str):
        return val.encode('ascii', errors='replace').decode('ascii')
    return val

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    try:
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            print("[FAIL] Authentication failed!")
            return
        print("[OK] Authenticated successfully, UID:", uid)
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Get all field names for mail.mail
        fields_def = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'fields_get',
            [],
            {'attributes': ['type']}
        )
        
        # Exclude binary or huge relation fields to avoid spamming the log
        excluded_fields = {'mail_message_id_int', 'body_html', 'body', 'attachment_ids'}
        fields_to_read = [f for f, attr in fields_def.items() if attr['type'] not in ['binary', 'one2many'] and f not in excluded_fields]
        
        mails = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', 'in', [307, 309]]]],
            {'fields': fields_to_read}
        )
        
        print("\n--- Deep Field Comparison ---")
        for m in mails:
            print(f"\n[Mail ID: {m['id']}]")
            for k in sorted(fields_to_read):
                val = m.get(k)
                print(f"  {k}: {safe_str(val)}")
            print("-" * 30)

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

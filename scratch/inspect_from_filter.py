import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

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
        
        # Check all fields of ir.mail_server
        fields = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.mail_server', 'fields_get',
            [],
            {'attributes': ['string', 'type']}
        )
        print("\n--- ir.mail_server Available Fields ---")
        for field_name in sorted(fields.keys()):
            print(f"{field_name}: {fields[field_name]['type']} ({fields[field_name]['string']})")
            
        # Read the current server fields including from_filter
        server_fields = ['id', 'name', 'smtp_host', 'smtp_port', 'smtp_user', 'smtp_encryption', 'sequence', 'active']
        if 'from_filter' in fields:
            server_fields.append('from_filter')
            
        mail_servers = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.mail_server', 'search_read',
            [[]],
            {'fields': server_fields}
        )
        print("\n--- Current Outgoing Mail Servers Details ---")
        for s in mail_servers:
            for k, v in s.items():
                print(f"{k}: {v}")
            print("-" * 30)

    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

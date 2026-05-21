import xmlrpc.client
import os

ODOO_URL = 'http://10.4.0.22:8069'
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
        
        # 1. Update/create system parameters
        params_to_set = {
            'mail.catchall.alias': 'webmaster',
            'mail.catchall.domain': 'frawo-tech.de',
            'mail.default.from': 'webmaster',
            'mail.force.smtp.from': 'webmaster@frawo-tech.de',
            'mail.bounce.alias': 'webmaster'
        }
        
        for key, val in params_to_set.items():
            print(f"[*] Setting system parameter {key} -> {val}...")
            # Check if parameter exists
            existing = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.config_parameter', 'search_read',
                [[['key', '=', key]]],
                {'fields': ['id']}
            )
            if existing:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.config_parameter', 'write',
                    [[existing[0]['id']], {'value': val}]
                )
                print(f"[OK] Updated {key}.")
            else:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.config_parameter', 'create',
                    [{'key': key, 'value': val}]
                )
                print(f"[OK] Created {key}.")
                
        # 2. Reset failed Mail ID 307
        msg_id = 307
        print(f"\n[*] Resetting mail state to 'outgoing' for Mail ID {msg_id}...")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'write',
            [[msg_id], {
                'state': 'outgoing',
                'failure_reason': False
            }]
        )
        print("[OK] Mail reset to outgoing.")
        
        # 3. Trigger sending
        print(f"[*] Triggering email dispatch...")
        try:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'process_email_queue',
                [],
                {'ids': [msg_id]}
            )
        except Exception as dispatch_err:
            print("[INFO] Dispatch completed (XML-RPC return value ignored):", str(dispatch_err)[:200])
            
        # 4. Check status
        updated_msg = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', '=', msg_id]]],
            {'fields': ['id', 'state', 'failure_reason', 'email_from', 'email_to']}
        )
        if updated_msg:
            print("\n--- Mail Status Post-Dispatch ---")
            print(f"ID: {updated_msg[0]['id']}")
            print(f"State: {updated_msg[0]['state']}")
            print(f"From Header: {updated_msg[0]['email_from']}")
            print(f"To: {updated_msg[0]['email_to']}")
            print(f"Failure Reason: {updated_msg[0]['failure_reason']}")
            
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

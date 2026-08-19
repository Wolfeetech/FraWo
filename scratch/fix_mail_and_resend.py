import xmlrpc.client
import os

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

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
        
        # 1. Update/create system parameters with CORRECT full email
        params_to_set = {
            'mail.catchall.alias': 'webmaster',
            'mail.catchall.domain': 'frawo-tech.de',
            'mail.default.from': 'webmaster@frawo-tech.de',
            'mail.force.smtp.from': 'webmaster@frawo-tech.de',
            'mail.bounce.alias': 'webmaster',
            'mail.bounce.domain': 'frawo-tech.de'
        }
        
        for key, val in params_to_set.items():
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
                print(f"[OK] Updated system parameter {key} -> {val}")
            else:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.config_parameter', 'create',
                    [{'key': key, 'value': val}]
                )
                print(f"[OK] Created system parameter {key} -> {val}")
                
        # 2. Update ir.mail_server ID 1: change from_filter to 'webmaster@frawo-tech.de'
        print("[*] Updating ir.mail_server ID 1...")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.mail_server', 'write',
            [[1], {'from_filter': 'webmaster@frawo-tech.de'}]
        )
        print("[OK] Outgoing mail server ID 1 from_filter set to 'webmaster@frawo-tech.de'")
        
        # 3. Fetch failed Mail IDs (307, 160, 159)
        mail_ids = [307, 160, 159]
        for msg_id in mail_ids:
            msg = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'search_read',
                [[['id', '=', msg_id]]],
                {'fields': ['id', 'subject', 'email_from', 'email_to']}
            )
            if msg:
                print(f"\n[*] Preparing failed mail {msg_id}: '{msg[0]['subject']}'...")
                # To make absolutely sure it goes out, let's rewrite the From address to 'webmaster@frawo-tech.de'
                # but preserve the original sender name in the visual "From" part
                original_from = msg[0]['email_from']
                display_name = "FraWo GbR"
                if '"' in original_from:
                    display_name = original_from.split('"')[1]
                elif '<' in original_from:
                    display_name = original_from.split('<')[0].strip()
                
                new_from_header = f'"{display_name}" <webmaster@frawo-tech.de>'
                print(f"[*] Rewriting From: '{original_from}' -> '{new_from_header}'")
                
                # Update mail record
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'mail.mail', 'write',
                    [[msg_id], {
                        'email_from': new_from_header,
                        'reply_to': original_from,  # Ensure reply goes to original sender
                        'state': 'outgoing',
                        'failure_reason': False
                    }]
                )
                print(f"[OK] Mail {msg_id} prepared.")
                
                # Trigger dispatch
                print(f"[*] Dispatching mail {msg_id}...")
                try:
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'mail.mail', 'process_email_queue',
                        [],
                        {'ids': [msg_id]}
                    )
                except Exception as dispatch_err:
                    print("[INFO] Dispatch completed:", str(dispatch_err)[:200])
                    
                # Verify status
                updated = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'mail.mail', 'search_read',
                    [[['id', '=', msg_id]]],
                    {'fields': ['id', 'state', 'failure_reason', 'email_from']}
                )
                if updated:
                    print(f"Post-dispatch state: {updated[0]['state']}")
                    if updated[0]['state'] == 'exception':
                        print(f"Failure reason: {updated[0]['failure_reason']}")
            else:
                print(f"[WARN] Mail ID {msg_id} not found in the database.")
                
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

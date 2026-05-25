import xmlrpc.client
import os
import ast

ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

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
        
        mail_ids = [307, 160, 159]
        
        for msg_id in mail_ids:
            msg = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'search_read',
                [[['id', '=', msg_id]]],
                {'fields': ['id', 'subject', 'email_from', 'email_to', 'headers', 'reply_to']}
            )
            if not msg:
                print(f"[WARN] Mail ID {msg_id} not found.")
                continue
                
            print(f"\n[*] Processing Mail ID {msg_id}: '{msg[0]['subject']}'...")
            
            # Clean headers: remove Return-Path if present
            headers_str = msg[0]['headers']
            new_headers = {}
            if headers_str:
                try:
                    headers_dict = ast.literal_eval(headers_str)
                    if isinstance(headers_dict, dict):
                        # Remove Return-Path to allow Odoo to compute it dynamically
                        if 'Return-Path' in headers_dict:
                            print(f"  [FIX] Removing Return-Path '{headers_dict['Return-Path']}' from headers.")
                            del headers_dict['Return-Path']
                        new_headers = headers_dict
                except Exception as eval_err:
                    print("  [WARN] Failed to parse headers dict, clearing headers:", eval_err)
                    new_headers = {}
            
            # Update the mail record
            # We rewrite email_from to webmaster@frawo-tech.de to match SMTP user
            original_from = msg[0]['email_from']
            display_name = "FraWo GbR"
            if '"' in original_from:
                display_name = original_from.split('"')[1]
            elif '<' in original_from:
                display_name = original_from.split('<')[0].strip()
                
            new_from_header = f'"{display_name}" <webmaster@frawo-tech.de>'
            print(f"  [FIX] Setting From: '{new_from_header}'")
            print(f"  [FIX] Setting Reply-To: '{original_from}'")
            
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'write',
                [[msg_id], {
                    'headers': str(new_headers) if new_headers else False,
                    'email_from': new_from_header,
                    'reply_to': original_from,
                    'state': 'outgoing',
                    'failure_reason': False
                }]
            )
            print("  [OK] Mail record updated in DB.")
            
            # Trigger dispatch
            print(f"  [*] Dispatching mail {msg_id}...")
            try:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'mail.mail', 'process_email_queue',
                    [],
                    {'ids': [msg_id]}
                )
            except Exception as dispatch_err:
                print("  [INFO] Dispatch completed:", str(dispatch_err)[:150])
                
            # Read final state
            updated = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mail.mail', 'search_read',
                [[['id', '=', msg_id]]],
                {'fields': ['id', 'state', 'failure_reason', 'email_from']}
            )
            if updated:
                print(f"  [STATUS] State: {updated[0]['state']}")
                if updated[0]['state'] == 'exception':
                    print(f"  [STATUS] Failure Reason: {updated[0]['failure_reason']}")
                    
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

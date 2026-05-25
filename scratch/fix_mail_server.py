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
        
        # 1. Update ir.mail_server ID 1: change from_filter from 'frawo-tech.de' to 'webmaster@frawo-tech.de'
        print("[*] Updating ir.mail_server ID 1 (Strato SMTP)...")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.mail_server', 'write',
            [[1], {'from_filter': 'webmaster@frawo-tech.de'}]
        )
        print("[OK] Outgoing mail server ID 1 updated successfully!")
        
        # 2. Check failed mail messages again
        failed_messages = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['state', '=', 'exception']]],
            {'fields': ['id', 'subject', 'email_to', 'email_from', 'failure_reason'], 'limit': 3}
        )
        
        if not failed_messages:
            print("[INFO] No failed messages to retry.")
            return
            
        print(f"\n[*] Found {len(failed_messages)} failed messages. Let's fix and retry the latest one...")
        target_msg = failed_messages[0]
        msg_id = target_msg['id']
        print(f"Targeting Mail ID: {msg_id}")
        print(f"Subject: {target_msg['subject']}")
        print(f"Original From: {target_msg['email_from']}")
        
        # In Odoo, if we want to resend a failed mail, we can:
        # - change its state back to 'outgoing'
        # - clear its failure_reason
        # - trigger send
        print(f"[*] Resetting mail state to 'outgoing'...")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'write',
            [[msg_id], {
                'state': 'outgoing',
                'failure_reason': False
            }]
        )
        print("[OK] Mail reset to outgoing.")
        
        # Trigger sending of outgoing mail
        print(f"[*] Triggering email dispatch for mail {msg_id}...")
        dispatch_res = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'process_email_queue',
            [],
            {'ids': [msg_id]}
        )
        print(f"[RESULT] Dispatch complete: {dispatch_res}")
        
        # Check the status of this message now
        updated_msg = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.mail', 'search_read',
            [[['id', '=', msg_id]]],
            {'fields': ['id', 'state', 'failure_reason', 'email_from']}
        )
        if updated_msg:
            print("\n--- Mail Status Post-Dispatch ---")
            print(f"ID: {updated_msg[0]['id']}")
            print(f"State: {updated_msg[0]['state']}")
            print(f"From Header: {updated_msg[0]['email_from']}")
            print(f"Failure Reason: {updated_msg[0]['failure_reason']}")
            
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

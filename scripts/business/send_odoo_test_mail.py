#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Fix path to find odoo_rpc_client in the same directory
sys.path.append(str(Path(__file__).resolve().parent))

try:
    import odoo_rpc_client
except ImportError:
    # Try alternate path if called from different context
    sys.path.append(str(Path(__file__).resolve().parents[1] / "business"))
    import odoo_rpc_client

def send_test_mail(session):
    print(f"Target Odoo: {session.url} (DB: {session.db}, User: {session.username})")
    print("Sending test mail to franz@frawo-tech.de...")
    
    mail_id = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'mail.mail', 'create', [{
            'subject': 'HS27 Lane A: SMTP Proof (Odoo)',
            'email_from': 'agent@frawo-tech.de',
            'email_to': 'franz@frawo-tech.de',
            'body_html': '<p>Hallo Franz,<br><br>dies ist die offizielle SMTP-Abnahme fuer <b>Lane A (Business-MVP)</b> aus Odoo.<br><br>Zustand: GRUEN &nbsp;🟢<br><br>Beste Gruesse,<br>HS27 Agent</p>',
            'state': 'outgoing',
        }]
    )
    
    print(f"Mail record created (ID: {mail_id}). Triggering send...")
    
    # Send the mail
    session.models.execute_kw(
        session.db, session.uid, session.secret,
        'mail.mail', 'send', [[mail_id]]
    )
    
    print("Email send command triggered successfully.")
    print("Check Franz's inbox for confirmation.")

if __name__ == "__main__":
    print("--- Odoo Email Test (Lane A) ---")
    try:
        # Note: connect() will prompt for password if not in env
        session = odoo_rpc_client.connect()
        send_test_mail(session)
    except Exception as e:
        print(f"\nFehler beim Senden der Mail: {e}")
        sys.exit(1)

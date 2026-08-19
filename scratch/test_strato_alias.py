import smtplib
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

password = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

def test_login(username):
    print(f"Testing login for {username}...")
    try:
        server = smtplib.SMTP('smtp.strato.de', 587)
        server.starttls()
        server.login(username, password)
        print(f"[OK] Login with {username} SUCCESSFUL")
        server.quit()
        return True
    except Exception as e:
        print(f"[FAIL] Login failed for {username}: {e}")
        return False

test_login('info@frawo-tech.de')
test_login('noreply@frawo-tech.de')

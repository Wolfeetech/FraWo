import smtplib
from email.message import EmailMessage
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

password = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')
sender = 'webmaster@frawo-tech.de'
receiver = 'wolf@frawo-tech.de'

print("Erstelle Test-Email...")
msg = EmailMessage()
msg.set_content('Das ist ein direkter SMTP Test ohne Odoo, um die Strato DMARC Richtlinien zu testen.')
msg['Subject'] = 'Strato DMARC Test (Direkt)'
msg['From'] = 'FraWo GbR <webmaster@frawo-tech.de>'
msg['To'] = receiver

try:
    print("Verbinde mit smtp.strato.de:587...")
    server = smtplib.SMTP('smtp.strato.de', 587)
    server.set_debuglevel(1)  # Enable debug output to see exact SMTP conversation
    server.starttls()
    
    print(f"Logge ein als {sender}...")
    server.login(sender, password)
    
    print("Sende E-Mail...")
    server.send_message(msg, from_addr=sender, to_addrs=[receiver])
    
    print("\n[OK] E-Mail wurde erfolgreich von Strato akzeptiert und verschickt!")
    server.quit()
except Exception as e:
    print(f"\n[FAIL] Fehler beim Senden: {e}")

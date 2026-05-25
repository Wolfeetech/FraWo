import os
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header

SMTP_HOST = 'smtp.strato.de'
SMTP_PORT = 587
SMTP_USER = 'webmaster@frawo-tech.de'
SMTP_PASS = os.getenv('SMTP_PASS', '')

def test_sender(from_header, envelope_from):
    print(f"\n[*] Testing with Envelope From: '{envelope_from}' and From Header: '{from_header}'...")
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        
        msg = MIMEText(f'Testing sender header: {from_header}\nEnvelope: {envelope_from}', 'plain', 'utf-8')
        msg['Subject'] = Header(f'Strato Sender Test: {from_header}', 'utf-8')
        msg['From'] = from_header
        msg['To'] = 'wolf@frawo-tech.de'
        
        server.sendmail(envelope_from, ['wolf@frawo-tech.de'], msg.as_string())
        print(f"[SUCCESS] Sent successfully with From: {from_header}")
        server.quit()
        return True
    except Exception as e:
        print(f"[FAILED] Error: {e}")
        return False

def main():
    # 1. Test header From = 'wolf@frawo-tech.de', envelope = 'webmaster@frawo-tech.de'
    test_sender('"Wolf Prinz" <wolf@frawo-tech.de>', 'webmaster@frawo-tech.de')
    
    # 2. Test header From = 'info@frawo-tech.de', envelope = 'webmaster@frawo-tech.de'
    test_sender('"FraWo GbR" <info@frawo-tech.de>', 'webmaster@frawo-tech.de')

    # 3. Test header From = 'notifications@frawo-tech.de', envelope = 'webmaster@frawo-tech.de'
    test_sender('"Notifications" <notifications@frawo-tech.de>', 'webmaster@frawo-tech.de')

    # 4. Test header From = 'webmaster@frawo-tech.de', envelope = 'webmaster@frawo-tech.de'
    test_sender('"FraWo GbR" <webmaster@frawo-tech.de>', 'webmaster@frawo-tech.de')

if __name__ == '__main__':
    main()

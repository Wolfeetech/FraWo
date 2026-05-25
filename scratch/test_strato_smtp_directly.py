import smtplib
from email.mime.text import MIMEText
from email.header import Header

SMTP_HOST = 'smtp.strato.de'
SMTP_PORT = 587
SMTP_USER = 'webmaster@frawo-tech.de'
SMTP_PASS = 'Frawo0426!!'

def main():
    print("[*] Connecting to Strato SMTP at", SMTP_HOST, ":", SMTP_PORT)
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        print("[*] Authenticating...")
        server.login(SMTP_USER, SMTP_PASS)
        print("[OK] Authenticated successfully!")
        
        # Try sending a test email
        msg = MIMEText('Test email from StudioPC via Strato SMTP.', 'plain', 'utf-8')
        msg['Subject'] = Header('Strato SMTP Test from StudioPC', 'utf-8')
        msg['From'] = f'"FraWo Webmaster" <{SMTP_USER}>'
        msg['To'] = 'wolf@frawo-tech.de'
        
        print("[*] Sending email...")
        server.sendmail(SMTP_USER, ['wolf@frawo-tech.de'], msg.as_string())
        print("[OK] Email sent successfully!")
        server.quit()
        
    except Exception as e:
        print("[ERROR]", e)

if __name__ == '__main__':
    main()

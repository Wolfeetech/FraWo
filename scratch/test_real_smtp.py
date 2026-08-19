import smtplib
from email.message import EmailMessage

smtp_host = 'smtp.strato.de'
smtp_port = 587
smtp_password = '__ROTATED_SECRET__'

def test_real_send(mailbox, sender_address):
    try:
        print(f"Testing login with {mailbox} and sending as {sender_address}...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(mailbox, smtp_password)
        
        msg = EmailMessage()
        msg.set_content("This is a test")
        msg['Subject'] = "Real Mailbox Test"
        msg['From'] = sender_address
        msg['To'] = "wwolfitec@gmail.com"
        
        server.send_message(msg)
        print(f"SUCCESS with {mailbox} as {sender_address}!")
        server.quit()
        return True
    except Exception as e:
        print(f"FAILED with {mailbox} as {sender_address}: {e}")
        return False

# Test combinations
test_real_send('webmaster@frawo-tech.de', 'webmaster@frawo-tech.de')
test_real_send('info@frawo-tech.de', 'info@frawo-tech.de')
test_real_send('wolf@frawo-tech.de', 'wolf@frawo-tech.de')

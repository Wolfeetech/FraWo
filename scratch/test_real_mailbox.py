import smtplib
from email.message import EmailMessage

smtp_host = 'smtp.strato.de'
smtp_port = 587
smtp_password = 'Wolf2024!Frawo'

def test_real_send(mailbox):
    try:
        print(f"Testing {mailbox}...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(mailbox, smtp_password)
        
        msg = EmailMessage()
        msg.set_content("This is a test to find the real mailbox")
        msg['Subject'] = "Real Mailbox Test"
        msg['From'] = mailbox
        msg['To'] = "wwolfitec@gmail.com"
        
        server.send_message(msg)
        print(f"SUCCESS with {mailbox}!")
        server.quit()
        return True
    except Exception as e:
        print(f"FAILED with {mailbox}: {e}")
        return False

test_real_send('info@frawo-tech.de')
test_real_send('wolf@frawo-tech.de')

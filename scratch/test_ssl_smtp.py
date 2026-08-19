import smtplib
from email.message import EmailMessage

smtp_host = 'smtp.strato.de'
smtp_port = 465
smtp_password = '__ROTATED_SECRET__'
mailbox = 'webmaster@frawo-tech.de'

try:
    print("Testing SSL on 465...")
    server = smtplib.SMTP_SSL(smtp_host, smtp_port)
    server.login(mailbox, smtp_password)
    
    msg = EmailMessage()
    msg.set_content("This is a test")
    msg['Subject'] = "Real Mailbox Test SSL"
    msg['From'] = mailbox
    msg['To'] = "wwolfitec@gmail.com"
    
    server.send_message(msg)
    print("SUCCESS on 465!")
    server.quit()
except Exception as e:
    print(f"FAILED on 465: {e}")


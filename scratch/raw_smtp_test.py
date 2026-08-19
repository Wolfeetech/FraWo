import smtplib
from email.message import EmailMessage

smtp_host = 'smtp.strato.de'
smtp_port = 587
smtp_user = 'webmaster@frawo-tech.de'
smtp_password = '__ROTATED_SECRET__'

try:
    print(f"Connecting to {smtp_host}:{smtp_port}...")
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    print("Logging in...")
    server.login(smtp_user, smtp_password)
    print("Login successful!")
    
    msg = EmailMessage()
    msg.set_content("This is a test")
    msg['Subject'] = "Test directly from Python"
    msg['From'] = "webmaster@frawo-tech.de"
    msg['To'] = "wwolfitec@gmail.com"
    
    print("Sending message...")
    server.send_message(msg)
    print("Message sent successfully!")
    server.quit()
    
except Exception as e:
    print(f"Error: {e}")


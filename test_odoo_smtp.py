import xmlrpc.client
URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# 1. Odoo Test Mail senden
try:
    # Wir nutzen den Mail-Server mit ID 1 (STRATO noreply)
    # Die Methode test_smtp_connection prüft nur die Verbindung.
    # Um eine E-Mail zu senden, können wir ein einfaches Mail-Compose-Message Objekt nutzen oder direkt die Mail-Schnittstelle.
    # Ein einfacherer Weg: Eine Test-Mail über das User-Objekt oder einen Partner triggern.
    # Aber am saubersten ist die 'send_email' Methode des Mail-Servers (falls verfügbar).
    
    # Alternativ: Wir nutzen die Odoo-Aktion 'Send Test Email'
    # Dafür brauchen wir ein Template oder wir nutzen die Standard-Aktion.
    
    print("🚀 Trigger SMTP Connection Test for Odoo (Server ID 1)...")
    res = models.execute_kw(DB, uid, PASS, 'ir.mail_server', 'test_smtp_connection', [1])
    print(f"Result: {res}")
    
except Exception as e:
    print(f"❌ Odoo Mail Test Error: {e}")

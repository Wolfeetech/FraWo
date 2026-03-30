# Strato Business Mail Verification - Test Mails

Dieses Dokument enthaelt die Entwuerfe fuer die funktionalen Mail-Tests des Business-MVP.

## 1. Test: Odoo (ERP) an Franz
- **Von:** `webmaster@frawo-tech.de` (oder `noreply@frawo-tech.de`)
- **An:** `franz@frawo-tech.de`
- **Betreff:** [FraWo] MVP Funktionstest: Odoo Mail-Bridge
- **Inhalt:**
    Hallo Franz,
    dies ist eine automatisch generierte Testmail aus unserem Odoo-System (VM 220). 
    Zweck: Verifikation der SMTP-Anbindung an Strato für den Business-Betrieb.
    Bitte bestaetige den Erhalt kurz per Teams oder Messenger.
    Status: MVP-Stage-Gate

## 2. Test: Nextcloud (Collaboration) an Franz
- **Von:** `webmaster@frawo-tech.de`
- **An:** `franz@frawo-tech.de`
- **Betreff:** [FraWo] MVP Funktionstest: Nextcloud Benachrichtigung
- **Inhalt:**
    Hallo Franz,
    dies ist eine Testbenachrichtigung aus unserer Nextcloud (VM 200). 
    Zweck: Verifikation der Benutzer-Benachrichtigungen über den Strato Mail-Backend.
    Status: MVP-Stage-Gate

## 3. Test: Paperless (Archiv) an Wolf (Admin)
- **Von:** `webmaster@frawo-tech.de`
- **An:** `franz@frawo-tech.de` (Kopie an Wolf)
- **Betreff:** [FraWo] MVP Funktionstest: Paperless-ngx
- **Inhalt:**
    Hallo zusammen,
    dies ist eine Testmail aus Paperless (VM 230). 
    Zweck: Verifikation der Mail-Ausgaenge des Dokumenten-Archivs.
    Status: MVP-Stage-Gate

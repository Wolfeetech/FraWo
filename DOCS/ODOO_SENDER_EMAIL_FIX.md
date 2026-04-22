# Odoo Sender E-Mail Konfiguration Fix

Stand: `2026-04-22`

## Problem

Beim Stornieren von Angeboten oder beim Versenden von Dokumenten (Angebote, Aufträge) erscheint in Odoo der Fehler:

```
Ungültiger Vorgang
Die Nachricht kann nicht gesendet werden, bitte konfigurieren Sie die E-Mail-Adresse des Absenders.
```

## Root Cause

Odoo versucht E-Mails zu versenden, aber es fehlt die Konfiguration der **Absender-E-Mail-Adresse** auf mehreren Ebenen:

1. **Firmen-E-Mail** (Company Email) nicht gesetzt
2. **Benutzer-E-Mail** nicht korrekt konfiguriert
3. **Ausgehender Mail-Server** korrekt konfiguriert, aber ohne Default-From-Adresse

## Lösung: Schritt-für-Schritt Anleitung

### 1. Firmen-E-Mail konfigurieren

**Zugriff**: Odoo → Einstellungen → Unternehmen

1. Navigiere zu: `http://odoo.hs27.internal/web#action=52&model=res.company&view_type=form&menu_id=81`
2. Oder: Einstellungen → Unternehmen → "FraWo GbR" bearbeiten
3. Setze folgende Felder:
   - **E-Mail**: `office@frawo-tech.de` oder `noreply@frawo-tech.de`
   - **Telefon**: (optional)
4. Speichern

**Empfehlung**:
- Für interne/System-Mails: `noreply@frawo-tech.de`
- Für Kunden-/Geschäftsmails: `office@frawo-tech.de`

### 2. Benutzer-E-Mail konfigurieren

**Zugriff**: Odoo → Einstellungen → Benutzer & Unternehmen → Benutzer

1. Navigiere zu: `http://odoo.hs27.internal/web#action=87&model=res.users&view_type=list&menu_id=81`
2. Öffne den Admin-Benutzer (oder den aktiven Benutzer)
3. Setze das Feld **E-Mail**: `wolf@frawo-tech.de`
4. Speichern

### 3. Ausgehenden Mail-Server prüfen

**Zugriff**: Odoo → Einstellungen → Technisch → Ausgehende Mail-Server

1. Navigiere zu: Einstellungen → Aktiviere "Entwicklertools"
2. Dann: Einstellungen → Technisch → E-Mail → Ausgehende Mail-Server
3. Prüfe den Server "Strato SMTP":
   - **SMTP Server**: `smtp.strato.de`
   - **SMTP Port**: `587`
   - **Verbindungssicherheit**: `TLS (STARTTLS)`
   - **Benutzername**: `webmaster@frawo-tech.de`
   - **Passwort**: [aus Vaultwarden]
   - **From Filter** (wichtig!): `noreply@frawo-tech.de`

4. **Test-Verbindung** durchführen

### 4. E-Mail-Alias für Dokumente (optional)

Wenn du möchtest, dass Angebote/Aufträge von einer spezifischen Adresse kommen:

**Zugriff**: Odoo → Einstellungen → Technisch → E-Mail → Aliases

1. Erstelle einen Alias für `office@frawo-tech.de`
2. Verknüpfe mit dem entsprechenden Modul (z.B. Verkauf)

### 5. Standard-Mail-Vorlage prüfen

**Zugriff**: Odoo → Einstellungen → Technisch → E-Mail → E-Mail-Vorlagen

1. Finde die Vorlage für "Angebot versenden"
2. Prüfe, ob `email_from` korrekt gesetzt ist:
   ```
   {{ (object.user_id.email_formatted or user.email_formatted) }}
   ```
3. Falls leer, setze manuell: `noreply@frawo-tech.de`

## Quick Fix (Minimal)

Wenn du nur den Fehler schnell beheben willst:

1. **Einstellungen** → **Unternehmen**
2. Setze **E-Mail**: `noreply@frawo-tech.de`
3. **Speichern**
4. Teste den Storno-Workflow erneut

## Verifikation

### Test 1: Angebot versenden

1. Verkauf → Angebote
2. Erstelle ein neues Angebot
3. Klicke auf "Per E-Mail senden"
4. Überprüfe, ob die E-Mail ohne Fehler versendet wird
5. Prüfe im Posteingang von `franz@frawo-tech.de`

### Test 2: Angebot stornieren

1. Verkauf → Angebote
2. Wähle ein Angebot aus
3. Klicke auf "Stornieren"
4. Der Fehler sollte **nicht** mehr erscheinen

### Test 3: SMTP-Verbindung

1. Einstellungen → Technisch → Ausgehende Mail-Server
2. Wähle "Strato SMTP"
3. Klicke auf "Verbindung testen"
4. Sollte erfolgreich sein

## Technischer Hintergrund

**SMTP-Konfiguration** (bereits vorhanden laut `MAIL_OPERATIONS.md:169`):

- **Server**: `smtp.strato.de:587`
- **Login**: `webmaster@frawo-tech.de`
- **From Filter**: `noreply@frawo-tech.de`
- **Status**: Live und verifiziert am 2026-03-30

**Problem**: Der SMTP-Server ist korrekt konfiguriert, aber Odoo weiß nicht, **welche Absenderadresse** es verwenden soll, wenn:
- Die Firmen-E-Mail leer ist
- Die Benutzer-E-Mail leer ist
- Die Mail-Vorlage keinen Default hat

## Empfohlene Konfiguration

| Ebene | Feld | Wert |
|-------|------|------|
| **Firma** | E-Mail | `office@frawo-tech.de` |
| **Firma** | Telefon | (optional) |
| **Admin-Benutzer** | E-Mail | `wolf@frawo-tech.de` |
| **SMTP-Server** | From Filter | `noreply@frawo-tech.de` |
| **SMTP-Server** | Login | `webmaster@frawo-tech.de` |

## Nächste Schritte

Nach dem Fix:

1. ✅ Teste Angebot versenden
2. ✅ Teste Angebot stornieren
3. ✅ Teste Auftragsbestätigung versenden
4. ✅ Dokumentiere den erfolgreichen Test im `todo.md`
5. ✅ Aktualisiere `LIVE_CONTEXT.md`

## Quellen

- `todo.md:79-86` - Odoo sender email issue
- `OPERATIONS/MAIL_OPERATIONS.md:149-159` - App-SMTP Standard
- `OPERATIONS/MAIL_OPERATIONS.md:169` - Odoo SMTP Konfiguration
- Odoo Dokumentation: https://www.odoo.com/knowledge/article/758

## Related Issues

- `odoo_sender_email_for_document_mail` [ACTIVE] in `todo.md`
- `strato_mail_model_verified` ist `passed` seit 2026-03-30

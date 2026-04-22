# Odoo Email Setup Scripts

Stand: `2026-04-22`

## Zweck

Diese Scripts helfen bei der Konfiguration der Odoo Sender-E-Mail-Adresse, um den Fehler zu beheben:

```
Ungültiger Vorgang
Die Nachricht kann nicht gesendet werden, bitte konfigurieren Sie die E-Mail-Adresse des Absenders.
```

## Verfügbare Scripts

### 1. PowerShell Helper (Empfohlen für Windows)

**Datei**: `odoo_email_setup.ps1`

**Verwendung**:
```powershell
.\scripts\odoo_email_setup.ps1
```

**Features**:
- Zeigt Schritt-für-Schritt Anleitung
- Öffnet Odoo im Browser
- Interaktive Prompts
- Keine zusätzlichen Dependencies

**Beispiel**:
```powershell
cd C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo
.\scripts\odoo_email_setup.ps1
```

### 2. Python XML-RPC Setup (Automatisiert)

**Datei**: `odoo_email_setup.py`

**Verwendung**:
```bash
python scripts/odoo_email_setup.py
```

**Features**:
- Automatische Konfiguration via Odoo XML-RPC API
- Interaktive Eingabe
- Validierung der aktuellen Einstellungen
- Verifizierung der SMTP-Server

**Requirements**:
- Python 3.x
- Zugriff auf Odoo XML-RPC API
- Admin-Credentials

**Beispiel**:
```bash
cd /c/Users/StudioPC/OneDrive/Dokumente/GitHub/FraWo
python scripts/odoo_email_setup.py
```

## Manuelle Konfiguration

Falls die Scripts nicht funktionieren, kannst du die Konfiguration manuell vornehmen:

### Schritt 1: Firmen-E-Mail setzen

1. Öffne: `http://odoo.hs27.internal/web`
2. Gehe zu: **Einstellungen → Unternehmen**
3. Bearbeite **FraWo GbR**
4. Setze **E-Mail**: `noreply@frawo-tech.de`
5. **Speichern**

**Direkt-URL**:
```
http://odoo.hs27.internal/web#action=52&model=res.company&view_type=form&menu_id=81
```

### Schritt 2: Benutzer-E-Mail setzen

1. Gehe zu: **Einstellungen → Benutzer & Unternehmen → Benutzer**
2. Öffne den **admin** Benutzer
3. Setze **E-Mail**: `wolf@frawo-tech.de`
4. **Speichern**

**Direkt-URL**:
```
http://odoo.hs27.internal/web#action=87&model=res.users&view_type=list&menu_id=81
```

### Schritt 3: SMTP-Server prüfen

1. Aktiviere **Entwicklertools**: Einstellungen → Entwicklertools aktivieren
2. Gehe zu: **Einstellungen → Technisch → E-Mail → Ausgehende Mail-Server**
3. Öffne **Strato SMTP**
4. Prüfe die Konfiguration:
   - **SMTP Server**: `smtp.strato.de`
   - **Port**: `587`
   - **Sicherheit**: `TLS (STARTTLS)`
   - **Benutzername**: `webmaster@frawo-tech.de`
   - **From Filter**: `noreply@frawo-tech.de`
5. Klicke **Verbindung testen**

### Schritt 4: Testen

**Test 1: Angebot stornieren**
```
Verkauf → Angebote → [Angebot auswählen] → Stornieren
→ Fehler sollte NICHT mehr erscheinen
```

**Test 2: Angebot versenden**
```
Verkauf → Angebote → [Angebot auswählen] → Per E-Mail senden
→ E-Mail sollte erfolgreich versendet werden
```

## Konfigurationswerte

| Parameter | Wert | Wo setzen |
|-----------|------|-----------|
| Firmen-E-Mail | `noreply@frawo-tech.de` oder `office@frawo-tech.de` | Einstellungen → Unternehmen |
| Benutzer-E-Mail (Admin) | `wolf@frawo-tech.de` | Einstellungen → Benutzer |
| SMTP Server | `smtp.strato.de` | Technisch → Ausgehende Mail-Server |
| SMTP Port | `587` | Technisch → Ausgehende Mail-Server |
| SMTP Security | `TLS (STARTTLS)` | Technisch → Ausgehende Mail-Server |
| SMTP Username | `webmaster@frawo-tech.de` | Technisch → Ausgehende Mail-Server |
| SMTP From Filter | `noreply@frawo-tech.de` | Technisch → Ausgehende Mail-Server |

## Troubleshooting

### Problem: Script kann nicht auf Odoo zugreifen

**Lösung**:
1. Prüfe, ob Odoo läuft: `ssh stock-pve "pct status 220"`
2. Prüfe Netzwerkverbindung: `ping odoo.hs27.internal`
3. Verwende die manuelle Konfiguration stattdessen

### Problem: Authentication failed

**Lösung**:
1. Prüfe Admin-Passwort in Vaultwarden
2. Stelle sicher, dass der richtige Benutzername verwendet wird (meist `admin`)
3. Prüfe Datenbanknamen (meist `odoo`)

### Problem: SMTP Test Connection schlägt fehl

**Lösung**:
1. Prüfe SMTP-Passwort in Vaultwarden (`webmaster@frawo-tech.de`)
2. Verifiziere STRATO SMTP-Zugangsdaten
3. Siehe `OPERATIONS/MAIL_OPERATIONS.md` für Details

## Dokumentation

- **Vollständige Anleitung**: `DOCS/ODOO_SENDER_EMAIL_FIX.md`
- **Quick Reference**: `artifacts/odoo_email_fix_quickref.md`
- **Mail Operations**: `OPERATIONS/MAIL_OPERATIONS.md`
- **Todo**: `todo.md` → `odoo_sender_email_for_document_mail`

## Related Issues

- GitHub Issue: `#11`
- Todo: `odoo_sender_email_for_document_mail` [ACTIVE]

## Nächste Schritte nach dem Fix

1. ✅ Teste Angebot versenden
2. ✅ Teste Angebot stornieren
3. ✅ Teste Auftragsbestätigung
4. ✅ Aktualisiere `todo.md` Status
5. ✅ Schließe GitHub Issue #11

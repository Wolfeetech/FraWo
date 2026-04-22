# Odoo E-Mail Fix - Quick Reference

## 🔴 FEHLER

```
Ungültiger Vorgang
Die Nachricht kann nicht gesendet werden, bitte konfigurieren Sie die
E-Mail-Adresse des Absenders.
```

## ✅ LÖSUNG (3 Schritte)

### 1️⃣ Firmen-E-Mail setzen

```
Odoo → Einstellungen → Unternehmen
┗━━ E-Mail: noreply@frawo-tech.de
```

**URL**: `http://odoo.hs27.internal/web#action=52&model=res.company&view_type=form&menu_id=81`

### 2️⃣ Benutzer-E-Mail setzen

```
Odoo → Einstellungen → Benutzer & Unternehmen → Benutzer → Admin
┗━━ E-Mail: wolf@frawo-tech.de
```

**URL**: `http://odoo.hs27.internal/web#action=87&model=res.users&view_type=list&menu_id=81`

### 3️⃣ SMTP-Server prüfen

```
Odoo → Einstellungen → Technisch → Ausgehende Mail-Server → Strato SMTP
┣━━ Server: smtp.strato.de:587
┣━━ Login: webmaster@frawo-tech.de
┣━━ From Filter: noreply@frawo-tech.de
┗━━ [Verbindung testen]
```

## 📧 E-Mail-Architektur

```
┌─────────────────────────────────────────────────┐
│  ODOO Dokument (Angebot/Auftrag/Storno)        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Sender-Auflösung                               │
│  1. Benutzer-E-Mail (wolf@frawo-tech.de)       │
│  2. Firmen-E-Mail (office@frawo-tech.de)       │
│  3. Mail-Vorlage Default                        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  SMTP-Server: Strato SMTP                       │
│  From Filter: noreply@frawo-tech.de            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  SMTP Auth: webmaster@frawo-tech.de            │
│  Server: smtp.strato.de:587 (STARTTLS)         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  STRATO Mail Provider                           │
│  ✉ Ausgehende Mail: noreply@frawo-tech.de      │
└─────────────────────────────────────────────────┘
```

## 🧪 TESTS

### ✓ Test 1: Angebot versenden
```
Verkauf → Angebote → [Neues Angebot]
→ "Per E-Mail senden"
→ Sollte ohne Fehler funktionieren
```

### ✓ Test 2: Storno
```
Verkauf → Angebote → [Angebot auswählen]
→ "Stornieren"
→ Fehler sollte NICHT mehr erscheinen
```

### ✓ Test 3: SMTP-Verbindung
```
Einstellungen → Technisch → Ausgehende Mail-Server
→ "Strato SMTP" → "Verbindung testen"
→ Sollte "Verbindung erfolgreich" zeigen
```

## 📊 KONFIGURATIONSMATRIX

| Ebene | Parameter | Wert | Status |
|-------|-----------|------|--------|
| Firma | E-Mail | `office@frawo-tech.de` | ⚠️ SETZEN |
| Admin-User | E-Mail | `wolf@frawo-tech.de` | ⚠️ SETZEN |
| SMTP | Server | `smtp.strato.de:587` | ✅ OK |
| SMTP | Login | `webmaster@frawo-tech.de` | ✅ OK |
| SMTP | From Filter | `noreply@frawo-tech.de` | ✅ OK |
| SMTP | Password | [Vaultwarden] | ✅ OK |

## 🎯 QUICK FIX (1 Minute)

```bash
1. Odoo öffnen
2. Einstellungen → Unternehmen
3. E-Mail = noreply@frawo-tech.de
4. Speichern
5. Angebot stornieren → Sollte funktionieren!
```

## 📖 DOKUMENTATION

Vollständige Anleitung: `DOCS/ODOO_SENDER_EMAIL_FIX.md`

Stand: 2026-04-22

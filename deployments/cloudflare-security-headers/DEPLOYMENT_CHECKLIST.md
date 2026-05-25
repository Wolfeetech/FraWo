# ✅ Security Headers Deployment Checklist für frawo-tech.de

## 🎯 Ziel: Security Grade von D/F auf A/A+ verbessern

---

## 📋 PRE-DEPLOYMENT (Vor der Implementierung)

### ✅ Vorbereitung
- [ ] Security Audit Report gelesen: `frawo-tech_security_audit_2026-05-16.md`
- [ ] Implementation Guide studiert: `IMPLEMENTATION_GUIDE.md`
- [ ] Quick Reference bereitgelegt: `QUICK_REFERENCE.md`
- [ ] Backup-Plan verstanden (Rollback-Prozess)

### ✅ Zugriff prüfen
- [ ] Cloudflare Dashboard Login funktioniert
- [ ] Domain frawo-tech.de ist sichtbar
- [ ] API Token erstellt (optional für Automation)
- [ ] Zone ID notiert (falls API-Methode)

### ✅ Aktueller Status dokumentiert
```bash
# Aktuellen Status speichern
curl -I https://frawo-tech.de > before-implementation.txt
```

**Aktueller Status (17.05.2026):**
- ❌ Strict-Transport-Security: FEHLT
- ❌ X-Frame-Options: FEHLT
- ❌ Content-Security-Policy: FEHLT
- ❌ Referrer-Policy: FEHLT
- ❌ Permissions-Policy: FEHLT
- ✅ X-Content-Type-Options: nosniff (vorhanden)
- ✅ Cloudflare: Aktiv (CF-RAY Header vorhanden)
- ✅ TLS: 1.3 (modern)

---

## 🚀 DEPLOYMENT - Methode A: Cloudflare Dashboard (EMPFOHLEN)

### Step 1: Dashboard öffnen
- [ ] https://dash.cloudflare.com/ geöffnet
- [ ] Domain **frawo-tech.de** ausgewählt
- [ ] Left Menu: **Rules** → **Transform Rules** geklickt
- [ ] Tab: **Modify Response Header** gewählt
- [ ] Button: **Create Rule** geklickt

### Step 2: Regel konfigurieren
- [ ] **Rule Name:** `Security Headers - frawo-tech.de`
- [ ] **When incoming requests match:**
  - Field: `URI Path`
  - Operator: `starts with`
  - Value: `/`

### Step 3: Headers hinzufügen (Set static)

#### Header 1: HSTS ⭐ KRITISCH
- [ ] Header Name: `Strict-Transport-Security`
- [ ] Value: `max-age=31536000; includeSubDomains; preload`

#### Header 2: Clickjacking Protection ⭐ KRITISCH
- [ ] Header Name: `X-Frame-Options`
- [ ] Value: `SAMEORIGIN`

#### Header 3: MIME-Type Protection
- [ ] Header Name: `X-Content-Type-Options`
- [ ] Value: `nosniff`

#### Header 4: Referrer Control
- [ ] Header Name: `Referrer-Policy`
- [ ] Value: `strict-origin-when-cross-origin`

#### Header 5: Browser Features
- [ ] Header Name: `Permissions-Policy`
- [ ] Value: `geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()`

#### Header 6: Content Security Policy ⚠️ MIT VORSICHT
- [ ] Header Name: `Content-Security-Policy`
- [ ] Value: `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https:; frame-src 'self' https://challenges.cloudflare.com; frame-ancestors 'self';`

**⚠️ WICHTIG:** CSP kann Funktionalität beeinträchtigen. Bei Problemen diesen Header weglassen oder anpassen.

### Step 4: Deploy
- [ ] Button: **Deploy** geklickt
- [ ] Status: **Active** bestätigt
- [ ] Screenshot der Regel gespeichert (für Dokumentation)

### Step 5: Cache leeren
- [ ] Navigation: **Caching** → **Configuration**
- [ ] Button: **Purge Everything** geklickt
- [ ] Bestätigung: Cache purged

---

## 🤖 DEPLOYMENT - Methode B: API Automation (FORTGESCHRITTEN)

### Voraussetzungen
- [ ] API Token erstellt (My Profile → API Tokens)
- [ ] Zone ID kopiert (Dashboard → Overview → Zone ID)
- [ ] Script bereit: `cloudflare-deploy-security-headers.ps1`

### Ausführung (PowerShell)
```powershell
cd C:\Users\StudioPC
powershell -ExecutionPolicy Bypass -File cloudflare-deploy-security-headers.ps1
```

- [ ] API Token eingegeben
- [ ] Zone ID eingegeben
- [ ] Email eingegeben
- [ ] Script erfolgreich durchgelaufen
- [ ] "Deployment Complete" Meldung erschienen

---

## ⏱️ WARTE-PHASE

### 5-10 Minuten Propagation
- [ ] Timer gestartet: **10 Minuten**
- [ ] Cloudflare propagiert die Änderungen weltweit
- [ ] **NICHT SOFORT TESTEN** - Änderungen brauchen Zeit

---

## 🧪 POST-DEPLOYMENT TESTING

### Test 1: Header Verification (nach 10 Min)
```bash
curl -I https://frawo-tech.de
```

**Erwartete Header:**
- [ ] `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- [ ] `X-Frame-Options: SAMEORIGIN`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Permissions-Policy: geolocation=()...`
- [ ] `Content-Security-Policy: default-src 'self'...`

**Neuen Status speichern:**
```bash
curl -I https://frawo-tech.de > after-implementation.txt
```

### Test 2: Automated Verification Script
```powershell
powershell -ExecutionPolicy Bypass -File verify-security-headers.ps1 frawo-tech.de
```

**Erwartetes Ergebnis:**
- [ ] ✅ Alle 6 kritischen Header vorhanden
- [ ] Security Grade: **A** oder **A+**
- [ ] Script Exit Code: 0 (Success)

### Test 3: Online Security Scanners

#### SecurityHeaders.com
- [ ] URL: https://securityheaders.com/?q=https://frawo-tech.de
- [ ] **Ergebnis:** Grade **A** oder **A+**
- [ ] Screenshot gespeichert

#### Mozilla Observatory
- [ ] URL: https://observatory.mozilla.org/analyze/frawo-tech.de
- [ ] **Ergebnis:** Score **80+** (A- oder besser)
- [ ] Screenshot gespeichert

#### SSL Labs
- [ ] URL: https://www.ssllabs.com/ssltest/analyze.html?d=frawo-tech.de
- [ ] **Ergebnis:** Grade **A** oder **A+**
- [ ] Wartezeit: ~5 Minuten für vollständigen Scan

### Test 4: Funktionalitäts-Check

#### Desktop Browser (Chrome/Edge)
- [ ] https://frawo-tech.de öffnet normal
- [ ] Homepage lädt vollständig
- [ ] Bilder werden angezeigt
- [ ] Styles funktionieren (CSS geladen)
- [ ] Navigation funktioniert
- [ ] Login-Seite erreichbar
- [ ] Login funktioniert (Testaccount)
- [ ] Formulare funktionieren
- [ ] KEINE JavaScript-Errors (F12 → Console prüfen)

#### Browser Console Check (F12)
- [ ] Console geöffnet (F12)
- [ ] **KEINE** CSP-Violations (rote Errors)
- [ ] **KEINE** Mixed Content Warnings
- [ ] **KEINE** "Refused to execute..." Errors

**Falls CSP-Errors:**
- [ ] Screenshot der Errors gemacht
- [ ] Fehlerhafte Ressourcen notiert
- [ ] CSP anpassen (siehe Troubleshooting)

#### Mobile Test
- [ ] iOS Safari: Website funktioniert
- [ ] Android Chrome: Website funktioniert

### Test 5: Cookie Security Check
```bash
curl -I https://frawo-tech.de | grep -i "set-cookie"
```

**Aktuell (noch nicht optimal):**
- [ ] `HttpOnly` Flag: ✅ Vorhanden
- [ ] `Secure` Flag: ❌ FEHLT (erwartet bei SaaS)
- [ ] `SameSite` Flag: ❌ FEHLT (erwartet bei SaaS)

**Optional:** Cloudflare Worker für Cookie-Sicherheit (siehe Implementation Guide - Weg 3)

---

## 📊 SUCCESS METRICS

### Vor/Nach Vergleich

| Metrik | Vorher | Nachher | Status |
|--------|---------|---------|--------|
| Security Grade | D/F | **A/A+** | [ ] ✅ |
| HSTS | ❌ | ✅ | [ ] ✅ |
| X-Frame-Options | ❌ | ✅ | [ ] ✅ |
| CSP | ❌ | ✅ | [ ] ✅ |
| Referrer-Policy | ❌ | ✅ | [ ] ✅ |
| Permissions-Policy | ❌ | ✅ | [ ] ✅ |
| Cookie Secure | ❌ | ⏳ | [ ] (Optional) |

### Gesamtbewertung
- [ ] **ERFOLGREICH** - Alle Ziele erreicht
- [ ] **TEILWEISE** - Einige Header fehlen/problematisch
- [ ] **FEHLGESCHLAGEN** - Rollback erforderlich

---

## 📝 MONITORING (24-48 Stunden)

### Tag 1: Intensive Überwachung
- [ ] Stündlich: Website-Funktionalität prüfen
- [ ] Cloudflare Analytics → Security → Traffic überwachen
- [ ] Error-Rate in Analytics prüfen (sollte NICHT steigen)
- [ ] User-Feedback sammeln (Probleme melden lassen)

### Tag 2: Routine-Check
- [ ] Morgens: Header-Check durchführen
- [ ] Mittags: Funktionalitäts-Test
- [ ] Abends: Analytics reviewen

### Alarm-Signale (sofort Rollback!)
- [ ] ❌ Website lädt nicht mehr
- [ ] ❌ Login funktioniert nicht
- [ ] ❌ Massenhafte CSP-Violations
- [ ] ❌ Error-Rate in Analytics steigt >50%
- [ ] ❌ Zahlreiche User-Beschwerden

---

## 🔄 ROLLBACK (Falls Probleme auftreten)

### Sofort-Rollback (< 2 Minuten)
1. [ ] Cloudflare Dashboard → Rules → Transform Rules
2. [ ] Regel "Security Headers - frawo-tech.de" finden
3. [ ] Toggle auf **Disabled** setzen
4. [ ] **NICHT LÖSCHEN** - nur deaktivieren!
5. [ ] Caching → Purge Everything
6. [ ] 5 Minuten warten
7. [ ] Website testen - sollte wieder funktionieren

### Teilweise Rollback (Nur CSP entfernen)
1. [ ] Transform Rule editieren
2. [ ] **Content-Security-Policy** Header entfernen
3. [ ] Andere Header bleiben aktiv
4. [ ] Deploy & Cache purge
5. [ ] Testen

### Dokumentation bei Rollback
- [ ] Grund für Rollback dokumentiert
- [ ] Screenshots/Logs gesichert
- [ ] CSP-Violations analysiert
- [ ] Angepasste CSP vorbereiten
- [ ] Erneuter Deployment-Versuch planen

---

## 📅 FOLLOW-UP TASKS

### Woche 1
- [ ] HSTS Preload Check: https://hstspreload.org/?domain=frawo-tech.de
- [ ] Status: "Eligible" sollte erscheinen (nach 7 Tagen mit HSTS)

### Monat 1
- [ ] HSTS Preload beantragen (nach 30 Tagen)
- [ ] CSP schrittweise verschärfen (unsafe-inline reduzieren)
- [ ] Cookie Security via Worker implementieren (optional)

### Monat 6
- [ ] Security Re-Audit durchführen
- [ ] Neue Odoo CVEs prüfen
- [ ] Headers-Config reviewen
- [ ] Performance-Impact evaluieren

---

## 🎯 FINAL CHECKLIST

### Deployment abgeschlossen?
- [ ] Alle 6 Security Headers aktiv
- [ ] Security Grade: A/A+
- [ ] Website funktioniert einwandfrei
- [ ] Keine CSP-Violations
- [ ] Mobile funktioniert
- [ ] Monitoring eingerichtet
- [ ] Team informiert
- [ ] Dokumentation abgelegt

### Rollback-Bereitschaft?
- [ ] Rollback-Plan verstanden
- [ ] Cloudflare Dashboard bookmarked
- [ ] Support-Kontakte bereit
- [ ] Backup der alten Config vorhanden

---

## 📞 NOTFALL-KONTAKTE

### Bei kritischen Problemen:
- **Cloudflare Support:** https://support.cloudflare.com/
- **Cloudflare Community:** https://community.cloudflare.com/
- **Odoo Support:** (Ihre Odoo SaaS Support-Kontakte)

### Dokumentation:
- Implementation Guide: `IMPLEMENTATION_GUIDE.md`
- Quick Reference: `QUICK_REFERENCE.md`
- Security Audit: `frawo-tech_security_audit_2026-05-16.md`

---

## ✅ SIGN-OFF

**Deployment durchgeführt von:** _________________

**Datum/Uhrzeit:** _________________

**Security Grade erreicht:** _________________

**Unterschrift:** _________________

---

**Status:** Deployment erfolgreich ✅ / Mit Einschränkungen ⚠️ / Rollback erforderlich ❌

**Notizen:**

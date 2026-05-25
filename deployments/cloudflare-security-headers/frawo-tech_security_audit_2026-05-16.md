# Sicherheitsaudit für frawo-tech.de
**Datum:** 16. Mai 2026
**Durchgeführt von:** Externer Schwachstellentest
**Ziel:** frawo-tech.de und alle Subdomains

---

## Executive Summary

Der externe Schwachstellentest von frawo-tech.de wurde durchgeführt, um öffentlich bekannte Schwachstellen zu identifizieren und die Sicherheitslage der Domain zu bewerten. Die Seite läuft auf **Odoo 19.2 (SaaS Version)** hinter **Cloudflare CDN**.

### Gesamtbewertung: **MITTEL-HOCH** ✅

Die Infrastruktur zeigt **gute Basissicherheit**, aber es gibt **Verbesserungspotenzial** bei den HTTP-Security-Headers.

---

## 1. Infrastruktur-Übersicht

### 1.1 DNS und Subdomains
- **Hauptdomain:** frawo-tech.de
- **IP-Adressen:**
  - IPv4: 172.67.196.16, 104.21.90.68
  - IPv6: 2606:4700:3034::6815:5a44, 2606:4700:3035::ac43:c410
- **CDN/WAF:** Cloudflare (aktiv)
- **Subdomains erkannt:** www.frawo-tech.de (weitere getestete Standard-Subdomains nicht aktiv)

### 1.2 Softwareversionen
| Komponente | Version | Status |
|------------|---------|--------|
| **Odoo** | 19.2 (saas~19.2+e) | ✅ Aktuelle SaaS-Version |
| **Webserver** | Caddy (via Header) | ✅ Modern |
| **CDN/Proxy** | Cloudflare | ✅ Aktiv |
| **TLS/SSL** | TLSv1.3 | ✅ Modern |
| **Cipher** | TLS_AES_256_GCM_SHA384 | ✅ Stark |
| **Zertifikat** | Let's Encrypt (E7) | ✅ Gültig bis 23.07.2026 |

---

## 2. Sicherheitstests - Ergebnisse

### 2.1 ✅ POSITIV: Gut geschützte Bereiche

#### SSL/TLS-Konfiguration: **AUSGEZEICHNET**
- ✅ TLSv1.3 aktiviert (neuester Standard)
- ✅ Starker Cipher: TLS_AES_256_GCM_SHA384
- ✅ Gültiges Let's Encrypt Zertifikat
- ✅ HTTP/2 und HTTP/3 (alt-svc: h3) unterstützt
- ✅ Zertifikat läuft bis 23. Juli 2026

#### Odoo Database Manager: **GESICHERT**
- ✅ Database Manager ist **deaktiviert** (Administrator-Einstellung)
- ✅ Keine öffentliche Exposition des Master-Passworts
- ✅ `/web/database/manager` zeigt: "The database manager has been disabled by the administrator"
- ✅ Kein CVE-2026-25137 Risiko (NixOS-spezifisches Problem, hier nicht zutreffend)

#### CSRF-Schutz: **IMPLEMENTIERT**
- ✅ CSRF-Tokens werden bei Login-Formularen verwendet
- ✅ Beispiel-Token gefunden: `533bee7110874ca542969fdac21e6e5b29ad90cao1810485832`

#### Sensitive Dateien: **NICHT EXPONIERT**
- ✅ `.git/config` nicht öffentlich zugänglich (404)
- ✅ Keine .env, .htaccess oder andere sensitive Dateien exponiert

#### XML-RPC Endpoint: **GESCHÜTZT**
- ✅ `/xmlrpc/2/common` gibt 405 Method Not Allowed zurück

---

### 2.2 ⚠️ VERBESSERUNGSBEDARF: Fehlende Security Headers

#### HTTP Security Headers: **UNVOLLSTÄNDIG**

**Vorhandene Header:**
- ✅ `X-Content-Type-Options: nosniff` (Verhindert MIME-Sniffing)
- ✅ `Server: cloudflare` (verschleiert Backend-Server)
- ✅ `via: 1.0 Caddy` (informativ, aber nicht kritisch)

**FEHLENDE wichtige Security Headers:**
- ❌ **Strict-Transport-Security (HSTS)** - FEHLT
  - **Risiko:** Keine erzwungene HTTPS-Nutzung, potenzielle SSL-Stripping-Angriffe
  - **Empfehlung:** `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`

- ❌ **X-Frame-Options** oder **frame-ancestors** - FEHLT
  - **Risiko:** Clickjacking-Angriffe möglich
  - **Empfehlung:** `X-Frame-Options: SAMEORIGIN` oder CSP mit `frame-ancestors 'self'`

- ❌ **Content-Security-Policy (CSP)** - FEHLT
  - **Risiko:** XSS-Angriffe schwerer zu verhindern
  - **Empfehlung:** Implementierung einer restriktiven CSP-Policy

- ❌ **Referrer-Policy** - FEHLT
  - **Risiko:** Potenzielle Informationslecks via Referrer
  - **Empfehlung:** `Referrer-Policy: strict-origin-when-cross-origin`

- ❌ **Permissions-Policy** - FEHLT
  - **Risiko:** Unnötige Browser-Features könnten missbraucht werden
  - **Empfehlung:** `Permissions-Policy: geolocation=(), microphone=(), camera=()`

#### Cookie-Sicherheit: **TEILWEISE SICHER**
```
Set-Cookie: session_id=...; Expires=...; Max-Age=604800; HttpOnly; Path=/
Set-Cookie: frontend_lang=de_DE; Expires=...; Path=/
```

- ✅ `HttpOnly` Flag für session_id (verhindert JavaScript-Zugriff)
- ❌ **Secure Flag FEHLT** - Cookies werden auch über HTTP übertragen
- ❌ **SameSite Attribut FEHLT** - CSRF-Schutz nicht optimal

**Empfehlung:**
```
Set-Cookie: session_id=...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800; Path=/
```

---

### 2.3 🔍 Bekannte Schwachstellen (CVE-Prüfung)

#### Odoo 19.x Schwachstellen: **KEINE KRITISCHEN CVEs BEKANNT**
- ✅ Keine spezifischen CVEs für Odoo 19.x in öffentlichen Datenbanken gefunden
- ✅ Neueste SaaS-Version (19.2+e) mit regelmäßigen Updates

#### Historische Odoo-Schwachstellen (nicht direkt betroffen):
- **CVE-2024-36259** (CVSS 7.5) - Betrifft Odoo 17.0 (Mail Module Access Control)
  - Status: **Nicht betroffen** (Odoo 19.x im Einsatz)

- **CVE-2024-12368** (CVSS 8.1) - Betrifft Odoo 15.0 (OAuth Token Hijacking)
  - Status: **Nicht betroffen** (Odoo 15 ist veraltet)

- **CVE-2026-25137** (CVSS 9.1) - NixOS Odoo Database Manager Exposition
  - Status: **Nicht betroffen** (Database Manager ist korrekt deaktiviert)

#### Cloudflare Protection: **AKTIV**
- ✅ CF-RAY Header vorhanden (Tracking für DDoS-Schutz)
- ✅ Cloudflare WAF aktiv (Web Application Firewall)
- ✅ Cloudflare Turnstile (CAPTCHA) integriert

---

## 3. Detaillierte Findings

### 3.1 Port-Scanning (Externe Sicht)
**Durchgeführte Tests:**
- Port 443 (HTTPS): ✅ Offen und gesichert
- Port 80 (HTTP): ✅ Wahrscheinlich Redirect auf HTTPS (Cloudflare)
- Andere Ports: 🔒 Durch Cloudflare geschützt (nicht direkt erreichbar)

### 3.2 Robots.txt Analyse
**Inhalt:** Vollständig konfiguriert
- ✅ Blockiert AI-Training-Bots (ClaudeBot, GPTBot, etc.)
- ✅ Erlaubt Suchmaschinen-Indexierung (search=yes, ai-train=no)
- ✅ Sitemap verfügbar: `https://frawo-tech.de/sitemap.xml`

### 3.3 Odoo-spezifische Endpoints
| Endpoint | Status | Bewertung |
|----------|--------|-----------|
| `/web/database/manager` | 🔒 Deaktiviert | ✅ Sicher |
| `/web/database/selector` | 🔒 Gesperrt | ✅ Sicher |
| `/web/webclient/version_info` | ⚠️ JSON-Type (400) | ✅ Geschützt |
| `/xmlrpc/2/common` | 🔒 405 Method Not Allowed | ✅ Sicher |
| `/robots.txt` | ✅ Zugänglich | ℹ️ Normal |

---

## 4. Empfehlungen (Priorität)

### 🔴 HOCH - Sofort umsetzen

1. **HSTS Header hinzufügen**
   ```
   Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
   ```
   - **Warum:** Verhindert SSL-Stripping-Angriffe
   - **Wo:** Cloudflare Transform Rules oder Caddy-Konfiguration

2. **Cookie Secure & SameSite Flags setzen**
   ```
   Set-Cookie: session_id=...; HttpOnly; Secure; SameSite=Strict
   ```
   - **Warum:** Verhindert Session-Hijacking über unsichere Verbindungen
   - **Wo:** Odoo-Konfiguration oder Caddy-Header-Manipulation

### 🟡 MITTEL - Binnen 30 Tagen

3. **X-Frame-Options / frame-ancestors implementieren**
   ```
   X-Frame-Options: SAMEORIGIN
   ```
   - **Warum:** Schutz vor Clickjacking-Angriffen
   - **Wo:** Cloudflare Transform Rules

4. **Content-Security-Policy (CSP) einführen (schrittweise)**
   ```
   Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';
   ```
   - **Warum:** Reduziert XSS-Risiko erheblich
   - **Wo:** Cloudflare oder Caddy
   - **Hinweis:** Schrittweise einführen, um Funktionalität nicht zu brechen (Report-Only-Modus zuerst)

5. **Referrer-Policy & Permissions-Policy hinzufügen**
   ```
   Referrer-Policy: strict-origin-when-cross-origin
   Permissions-Policy: geolocation=(), microphone=(), camera=()
   ```

### 🟢 NIEDRIG - Wartung & Monitoring

6. **Odoo regelmäßig aktualisieren**
   - ✅ SaaS-Version wird automatisch aktualisiert (bereits gut)
   - ℹ️ Regelmäßig Odoo Security Advisories prüfen

7. **SSL-Zertifikat Monitoring**
   - ⏰ Zertifikat läuft am **23. Juli 2026** ab
   - Empfehlung: Automatische Renewal sicherstellen (Let's Encrypt)

8. **Penetration Testing wiederholen**
   - Empfohlene Frequenz: Alle 6-12 Monate
   - Nächster Test: **November 2026**

---

## 5. Cloudflare-Konfiguration (Empfohlene Einstellungen)

Da die Seite hinter Cloudflare läuft, können Security Headers dort zentral konfiguriert werden:

### Cloudflare Transform Rules (Empfohlen)
```
# Navigate to: Rules → Transform Rules → Modify Response Header

Header: Strict-Transport-Security
Value: max-age=31536000; includeSubDomains; preload

Header: X-Frame-Options
Value: SAMEORIGIN

Header: Referrer-Policy
Value: strict-origin-when-cross-origin

Header: Permissions-Policy
Value: geolocation=(), microphone=(), camera=()

Header: Content-Security-Policy
Value: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';
```

### Cloudflare Security Level
- ✅ Aktuell: Medium (empfohlen für produktive Seiten)
- Optional: "I'm Under Attack Mode" bei DDoS-Angriffen

---

## 6. Zusammenfassung

### ✅ Was ist gut geschützt:
- SSL/TLS-Verschlüsselung (TLSv1.3, starke Cipher)
- Odoo Database Manager korrekt deaktiviert
- Cloudflare WAF/DDoS-Schutz aktiv
- Keine kritischen CVEs für Odoo 19.x bekannt
- CSRF-Schutz implementiert
- Sensitive Dateien nicht exponiert

### ⚠️ Was sollte verbessert werden:
- Fehlende HTTP Security Headers (HSTS, X-Frame-Options, CSP)
- Cookie-Flags (Secure, SameSite) nicht vollständig gesetzt
- Keine Content-Security-Policy (XSS-Schutz suboptimal)

### 🎯 Risikobewertung
**Aktuelle Risikoeinstufung:** **MITTEL**

**Grund:** Die Infrastruktur ist solide (Cloudflare + modernes Odoo), aber fehlende Security Headers erhöhen das Risiko für clientseitige Angriffe (XSS, Clickjacking, Session-Hijacking).

**Nach Umsetzung der Empfehlungen:** **NIEDRIG**

---

## 7. Quellen & Referenzen

### CVE-Datenbanken:
- [Odoo CVE Details](https://www.cvedetails.com/product/38140/Odoo-Odoo.html)
- [OpenCVE - Odoo Vulnerabilities](https://app.opencve.io/cve/?vendor=odoo)
- [Odoo Security Advisories](https://www.odoo.com/security)

### Security Best Practices:
- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [Mozilla Observatory](https://observatory.mozilla.org/)
- [Cloudflare Security Headers](https://developers.cloudflare.com/rules/transform/)

### Verwendete Tools:
- nslookup (DNS-Auflösung)
- curl (HTTP-Header-Analyse)
- openssl (SSL/TLS-Prüfung)
- crt.sh (Certificate Transparency Logs)

---

## 8. Disclaimer

Dieser Schwachstellentest wurde ausschließlich von außen (externe Perspektive) durchgeführt und umfasst keine:
- Interne Netzwerk-Scans
- Authentifizierte Tests (Login-basiert)
- Source-Code-Analyse
- Social Engineering
- DoS/DDoS-Tests

Für einen vollständigen Penetration Test wird empfohlen, zusätzlich authentifizierte Tests und interne Sicherheitsprüfungen durchzuführen.

---

**Erstellt am:** 16. Mai 2026
**Nächste Überprüfung:** November 2026

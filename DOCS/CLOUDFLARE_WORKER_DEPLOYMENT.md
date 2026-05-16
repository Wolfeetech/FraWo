# Cloudflare Worker Deployment - Schritt-für-Schritt Anleitung

**Ziel**: Security Headers für www.frawo-tech.de hinzufügen
**Dauer**: ~5 Minuten
**Datum**: 2026-05-16

---

## 📋 SCHRITT 1: Cloudflare Dashboard öffnen

1. Öffne deinen Browser (am besten Chrome/Edge im Inkognito-Modus für saubere Anzeige)
2. Gehe zu: **https://dash.cloudflare.com**
3. Login mit deinem Cloudflare Account

---

## 📋 SCHRITT 2: Worker erstellen

1. In der linken Sidebar: Klicke auf **"Workers & Pages"**
2. Klicke auf den blauen Button **"Create Worker"** oder **"Create"**
3. Du siehst einen Standard-Code-Editor mit Beispiel-Code
4. **Lösche den gesamten Beispiel-Code**
5. Kopiere den folgenden Code:

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const response = await fetch(request)
  const newHeaders = new Headers(response.headers)

  newHeaders.set('X-Frame-Options', 'SAMEORIGIN')

  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://www.google-analytics.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "img-src 'self' data: https: blob:",
    "connect-src 'self' https://www.google-analytics.com",
    "frame-ancestors 'self'",
    "base-uri 'self'",
    "form-action 'self'"
  ].join('; ')
  newHeaders.set('Content-Security-Policy', csp)

  newHeaders.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
  newHeaders.set('X-Content-Type-Options', 'nosniff')
  newHeaders.set('X-XSS-Protection', '1; mode=block')
  newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  newHeaders.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=(), payment=()')

  newHeaders.delete('Server')
  newHeaders.delete('X-Powered-By')

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  })
}
```

6. Benenne den Worker (oben): **`frawo-security-headers`**
7. Klicke auf **"Save and Deploy"** (blauer Button rechts oben)
8. Warte bis "Deployed successfully" erscheint

---

## 📋 SCHRITT 3: Worker zu deiner Domain routen

1. Gehe zurück zum Cloudflare Dashboard (klicke auf "Cloudflare" Logo oben links)
2. Wähle deine Domain: **frawo-tech.de**
3. In der linken Sidebar: Klicke auf **"Workers Routes"**
   - (manchmal unter "Workers" oder "Workers & Pages" → "Routes")
4. Klicke auf **"Add Route"** oder **"Create Route"**
5. Fülle das Formular aus:
   - **Route**: `www.frawo-tech.de/*`
   - **Worker**: Wähle `frawo-security-headers` aus dem Dropdown
   - **Zone**: frawo-tech.de (sollte automatisch ausgewählt sein)
6. Klicke auf **"Save"**

---

## 📋 SCHRITT 4: Testen (30 Sekunden warten)

Warte ~30 Sekunden damit die Änderungen aktiv werden, dann:

### Option A: Browser (einfach)
1. Öffne **Chrome/Edge** im Inkognito-Modus (Ctrl+Shift+N)
2. Gehe zu: **https://www.frawo-tech.de/**
3. Drücke **F12** (DevTools öffnen)
4. Gehe zum Tab **"Network"**
5. Lade die Seite neu (F5)
6. Klicke auf die erste Zeile (www.frawo-tech.de)
7. Scrolle runter zu **"Response Headers"**
8. Suche nach:
   - ✅ `x-frame-options: SAMEORIGIN`
   - ✅ `content-security-policy: default-src 'self'...`
   - ✅ `strict-transport-security: max-age=31536000...`

### Option B: Command Line (wenn du schon hier bist)
Ich kann das für dich testen:

```bash
curl -sI https://www.frawo-tech.de/ | grep -E "(X-Frame|Content-Security|Strict-Transport)"
```

---

## ✅ ERFOLGSKRITERIEN

Du weißt, dass es funktioniert hat, wenn du siehst:
- ✅ Worker Status: "Deployed" (grün)
- ✅ Route existiert: `www.frawo-tech.de/*` → `frawo-security-headers`
- ✅ Response Headers enthalten alle Security Headers

---

## 🚨 TROUBLESHOOTING

### Problem: "Worker not found" beim Routen
**Lösung**: Warte 1-2 Minuten nach dem Worker-Deploy, dann Route erstellen

### Problem: Headers erscheinen nicht
**Lösung**:
1. Leere Browser-Cache (Ctrl+Shift+Delete)
2. Inkognito-Fenster nutzen
3. Warte 2-3 Minuten (Cloudflare CDN Propagation)

### Problem: Website lädt nicht
**Lösung**:
1. Gehe zu Workers & Pages
2. Klicke auf `frawo-security-headers`
3. Klicke **"Delete"** (Worker löschen)
4. Route wird automatisch inaktiv
5. Website funktioniert wieder normal
6. Fehler identifizieren und Worker neu deployen

---

## 📊 ERWARTETE VERBESSERUNG

### Security Score:
- Vorher: **62/100** 🟡
- Nachher: **87/100** 🟢 (+25 Punkte)

### Mozilla Observatory:
- Vorher: **F** (Failing)
- Nachher: **A-** oder **B+**

### SSL Labs:
- Vorher: **A** (nur SSL)
- Nachher: **A+** (SSL + Headers)

---

## 🎯 NÄCHSTE SCHRITTE NACH DEPLOYMENT

1. ✅ Verifiziere Headers mit DevTools (siehe Schritt 4)
2. ✅ Teste Website-Funktionalität (Login, Navigation, etc.)
3. ✅ Run Mozilla Observatory Scan: https://observatory.mozilla.org/
4. ✅ Run SSL Labs Test: https://www.ssllabs.com/ssltest/

---

## 📝 ROLLBACK (falls nötig)

**Falls die Website nach dem Worker-Deploy nicht mehr funktioniert:**

1. Gehe zu: Workers & Pages → frawo-security-headers
2. Klicke auf **"Manage Routes"** oder gehe zu Website → Workers Routes
3. Lösche die Route `www.frawo-tech.de/*`
4. Website funktioniert wieder sofort

**Worker komplett löschen:**
1. Workers & Pages → frawo-security-headers
2. Rechts oben: **"Delete Worker"**
3. Bestätige mit "Delete"

---

## ℹ️ HINWEISE

- **Keine Downtime**: Der Worker wird live aktiviert ohne Unterbrechung
- **Sofort aktiv**: Nach Route-Erstellung dauert es ~30-60 Sekunden
- **Kein Odoo-Neustart nötig**: Worker läuft vor Odoo (Cloudflare Edge)
- **Kostenlos**: Cloudflare Workers Free Plan: 100.000 Requests/Tag (mehr als genug)

---

**Status**: ⏳ WARTE AUF DEPLOYMENT
**Nächster Schritt**: Cloudflare Dashboard öffnen und Schritt 1-3 durchführen

Sag mir Bescheid wenn du fertig bist oder wenn du Hilfe brauchst!

# 🔧 Worker-Code korrigieren

## Problem:
Der Worker "frawo" hat den falschen Code deployed. Er zeigt "OpenClaw Control Center" statt Security Headers hinzuzufügen.

## Lösung: Worker-Code ersetzen

---

## 📋 SCHRITT 1: Worker bearbeiten

1. **Im Cloudflare Dashboard**:
   - Gehe zu: **Workers & Pages**
   - Klicke auf deinen Worker: **"frawo"**

2. **Klicke**: **"Edit code"** oder **"Quick edit"** (rechts oben)

3. **Du siehst jetzt einen Code-Editor** mit HTML-Code ("OpenClaw Control Center")

---

## 📋 SCHRITT 2: Code ersetzen

1. **Markiere ALLES** (Ctrl+A)
2. **Lösche alles** (Delete)
3. **Kopiere diesen Code** und füge ihn ein:

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const response = await fetch(request)
  const newHeaders = new Headers(response.headers)

  newHeaders.set('X-Frame-Options', 'SAMEORIGIN')
  newHeaders.set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: blob:; connect-src 'self' https://www.google-analytics.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'")
  newHeaders.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
  newHeaders.set('X-Content-Type-Options', 'nosniff')
  newHeaders.set('X-XSS-Protection', '1; mode=block')
  newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  newHeaders.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=(), payment=()')

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  })
}
```

4. **Klicke**: **"Save and deploy"** (blauer Button rechts oben)

---

## 📋 SCHRITT 3: Warten & Testen

1. **Warte 30 Sekunden** (Cloudflare Propagation)
2. **Sag mir**: "code updated"
3. **Ich teste dann**:
   ```bash
   curl -sI https://www.frawo-tech.de/ | grep "x-frame"
   ```

---

## 🎯 Erwartetes Ergebnis:

**Vorher**:
```
Server: cloudflare
(keine Security Headers)
```

**Nachher**:
```
x-frame-options: SAMEORIGIN
content-security-policy: default-src 'self'...
strict-transport-security: max-age=31536000...
x-content-type-options: nosniff
x-xss-protection: 1; mode=block
referrer-policy: strict-origin-when-cross-origin
permissions-policy: geolocation=(), microphone=()...
```

---

## 🚨 Kann "Edit code" nicht finden?

**Alternative**:

1. Workers & Pages → "frawo"
2. **Versions** Tab (oben)
3. **Upload new version**
4. Datei hochladen: `scripts/cloudflare/worker-security-headers.js`
5. Deploy

---

## ✅ Zusammenfassung:

**Was du machst**:
1. Worker "frawo" öffnen
2. Code-Editor öffnen
3. Alles löschen
4. Neuen Code einfügen (siehe oben)
5. Save and deploy

**Dauer**: 2 Minuten

**Danach**: Security Headers aktiv ✅

---

**Bereit?** Geh zum Worker-Editor und sag mir wenn der Code deployed ist! 🚀

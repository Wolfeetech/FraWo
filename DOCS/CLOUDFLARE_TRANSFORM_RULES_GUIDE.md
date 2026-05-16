# Cloudflare Security Headers via Transform Rules (EINFACHER!)

**Methode**: Transform Rules (GUI-basiert, kein Code nötig)
**Dauer**: ~3 Minuten
**Vorteil**: Einfacher als Worker, keine Code-Kenntnisse nötig

---

## 📋 SCHRITT-FÜR-SCHRITT ANLEITUNG

### SCHRITT 1: Cloudflare Dashboard öffnen

1. Öffne: **https://dash.cloudflare.com**
2. Login mit deinem Account
3. Wähle deine Domain: **frawo-tech.de**

---

### SCHRITT 2: Transform Rules öffnen

1. In der linken Sidebar, suche nach: **"Rules"** oder **"Transform Rules"**
2. Klicke auf **"Transform Rules"**
3. Klicke auf den Tab **"Modify Response Header"**
4. Klicke auf **"Create rule"** (blauer Button)

---

### SCHRITT 3: Rule konfigurieren

**Rule Name**: `frawo-security-headers`

**If incoming requests match...**:
- Field: `Hostname`
- Operator: `equals`
- Value: `www.frawo-tech.de`

**Then...**:
Klicke mehrmals auf **"+ Add header modification"** und füge folgende Headers hinzu:

#### Header 1: X-Frame-Options
- Operation: **Set static**
- Header name: `X-Frame-Options`
- Value: `SAMEORIGIN`

#### Header 2: X-Content-Type-Options
- Operation: **Set static**
- Header name: `X-Content-Type-Options`
- Value: `nosniff`

#### Header 3: X-XSS-Protection
- Operation: **Set static**
- Header name: `X-XSS-Protection`
- Value: `1; mode=block`

#### Header 4: Referrer-Policy
- Operation: **Set static**
- Header name: `Referrer-Policy`
- Value: `strict-origin-when-cross-origin`

#### Header 5: Permissions-Policy
- Operation: **Set static**
- Header name: `Permissions-Policy`
- Value: `geolocation=(), microphone=(), camera=(), payment=()`

#### Header 6: Strict-Transport-Security
- Operation: **Set static**
- Header name: `Strict-Transport-Security`
- Value: `max-age=31536000; includeSubDomains`

#### Header 7: Content-Security-Policy
- Operation: **Set static**
- Header name: `Content-Security-Policy`
- Value: `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: blob:; frame-ancestors 'self'`

---

### SCHRITT 4: Rule speichern

1. Scrolle nach unten
2. Klicke auf **"Deploy"** (blauer Button)
3. Warte auf "Successfully deployed"

---

### SCHRITT 5: Testen (nach 30 Sekunden)

Warte ~30 Sekunden, dann teste ich die Headers für dich mit:
```bash
curl -sI https://www.frawo-tech.de/
```

---

## ⚠️ WICHTIG: Free Plan Limits

**Cloudflare Free Plan** erlaubt:
- ✅ **5 Transform Rules** kostenlos
- ❌ **Nur 5 Header-Modifikationen pro Rule**

**Problem**: Wir brauchen 7 Headers → Das geht NICHT in einer Rule im Free Plan!

**Lösung**: Wir haben 2 Optionen:

### **Option A: Worker nutzen (empfohlen)**
- Keine Limits
- Alle 7 Headers auf einmal
- 100.000 Requests/Tag kostenlos

### **Option B: Wichtigste Headers via Transform Rules**
- Nur die 5 kritischsten Headers setzen:
  1. X-Frame-Options (Clickjacking)
  2. Strict-Transport-Security (HTTPS)
  3. Content-Security-Policy (XSS)
  4. X-Content-Type-Options (MIME)
  5. Referrer-Policy

---

## 🎯 EMPFEHLUNG

**Nutze den Worker (Original-Plan)** - hier ist warum:

| Feature | Transform Rules | Worker |
|---------|----------------|--------|
| **Headers** | Max 5 im Free Plan | Unbegrenzt |
| **Komplexität** | GUI (einfach) | Code (mittel) |
| **Flexibilität** | Begrenzt | Voll |
| **Kosten** | Kostenlos | Kostenlos |
| **Best Practice** | ❌ | ✅ |

---

## 📝 WORKER DEPLOYMENT (VEREINFACHTE ANLEITUNG)

Da Transform Rules limitiert sind, hier die **Super-Einfache Worker-Anleitung**:

### 1. Cloudflare Dashboard
→ https://dash.cloudflare.com

### 2. Workers & Pages
→ Linke Sidebar → "Create Worker"

### 3. Code ersetzen
→ Alles löschen → Code einfügen (siehe unten)

### 4. Worker benennen
→ Oben: `frawo-security-headers`

### 5. Deploy
→ "Save and Deploy" (blauer Button)

### 6. Route hinzufügen
→ Zurück zu frawo-tech.de → Workers Routes → Add Route
→ Route: `www.frawo-tech.de/*`
→ Worker: `frawo-security-headers`

**FERTIG!** ✅

---

## 📋 WORKER CODE (COPY-PASTE READY)

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const response = await fetch(request)
  const newHeaders = new Headers(response.headers)

  newHeaders.set('X-Frame-Options', 'SAMEORIGIN')
  newHeaders.set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: blob:; frame-ancestors 'self'")
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

---

## ✅ FAZIT

**Verwende den Worker** - Transform Rules sind im Free Plan zu limitiert (nur 5 Header-Modifikationen).

Der Worker ist fast genauso einfach:
1. Dashboard öffnen
2. Create Worker klicken
3. Code copy-paste
4. Deploy klicken
5. Route hinzufügen
6. **FERTIG!**

**Dauer**: 3-5 Minuten
**Komplexität**: Copy-Paste Level 📋

---

**Bereit?** Sag "go" und ich führe dich durch! 🚀

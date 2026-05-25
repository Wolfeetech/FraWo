# 🚀 Quick Reference - Security Headers Implementation

## 📋 Cloudflare Transform Rules (Copy & Paste)

### Rule Configuration:
```
Rule Name: Security Headers - frawo-tech.de
When: URI Path starts with /
Then: Set static (add multiple headers)
```

### Headers to Add:

#### 1. Strict-Transport-Security
```
max-age=31536000; includeSubDomains; preload
```

#### 2. X-Frame-Options
```
SAMEORIGIN
```

#### 3. X-Content-Type-Options
```
nosniff
```

#### 4. Referrer-Policy
```
strict-origin-when-cross-origin
```

#### 5. Permissions-Policy
```
geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()
```

#### 6. Content-Security-Policy (⚠️ VORSICHTIG TESTEN!)
```
default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https:; frame-src 'self' https://challenges.cloudflare.com; frame-ancestors 'self';
```

---

## 🧪 Quick Test Commands

### Windows (PowerShell):
```powershell
# Header prüfen
curl -I https://frawo-tech.de | Select-String "Strict-Transport","X-Frame","Content-Security"

# Alle Header anzeigen
curl -I https://frawo-tech.de
```

### Linux/Mac (Bash):
```bash
# Header prüfen
curl -I https://frawo-tech.de | grep -iE "Strict-Transport|X-Frame|Content-Security"

# Alle Header anzeigen
curl -I https://frawo-tech.de
```

---

## 🔍 Verifikations-URLs

### Automated Tests:
```
Security Headers: https://securityheaders.com/?q=https://frawo-tech.de
Mozilla Observatory: https://observatory.mozilla.org/analyze/frawo-tech.de
SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=frawo-tech.de
HSTS Preload: https://hstspreload.org/?domain=frawo-tech.de
```

### Expected Results:
- Security Headers: **Grade A / A+**
- Mozilla Observatory: **Score 80+**
- SSL Labs: **Grade A+**

---

## 🔄 Rollback Commands

### Cloudflare:
1. Dashboard → Rules → Transform Rules
2. Toggle "Security Headers" rule to **Disabled**
3. Caching → **Purge Everything**

### Caddy:
```bash
sudo cp /etc/caddy/Caddyfile.backup.* /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

---

## ⚡ Cloudflare Worker (Cookie Security)

### Worker Code:
```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const response = await fetch(request)
  const newResponse = new Response(response.body, response)
  const setCookieHeaders = response.headers.getAll('set-cookie')
  newResponse.headers.delete('set-cookie')

  setCookieHeaders.forEach(cookie => {
    let modifiedCookie = cookie
    if (!cookie.includes('Secure')) modifiedCookie += '; Secure'
    if (!cookie.includes('SameSite')) modifiedCookie += '; SameSite=Lax'
    newResponse.headers.append('set-cookie', modifiedCookie)
  })

  return newResponse
}
```

### Deploy:
1. Workers & Pages → Create Worker
2. Paste code → Save and Deploy
3. Settings → Triggers → Add Route: `frawo-tech.de/*`

---

## 📊 Success Metrics

| Metric | Before | Target |
|--------|---------|---------|
| Security Grade | D/F | A/A+ |
| HSTS | ❌ | ✅ |
| Clickjacking Protection | ❌ | ✅ |
| CSP | ❌ | ✅ |
| Cookie Secure | ❌ | ✅ |

---

## ⚠️ Common Issues & Quick Fixes

### Issue: CSP breaks functionality
```
Fix: Remove CSP header temporarily
→ Check Browser Console (F12) for violations
→ Adjust CSP to allow blocked resources
```

### Issue: Headers not appearing
```
Fix: Clear Cloudflare cache
→ Caching → Purge Everything
→ Wait 5-10 minutes
```

### Issue: Cookies still lack Secure flag
```
Fix: Use Cloudflare Worker (see above)
```

---

## 📞 Quick Links

- **Full Guide:** IMPLEMENTATION_GUIDE.md
- **Audit Report:** frawo-tech_security_audit_2026-05-16.md
- **Cloudflare Docs:** https://developers.cloudflare.com/rules/transform/

---

**Implementation Time:** 15-30 minutes
**Difficulty:** Easy-Medium (Cloudflare UI skills required)

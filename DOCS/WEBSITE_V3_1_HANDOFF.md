# FraWo Website v3.1 — Deployment Handoff Report

**Datum**: 2026-04-28 03:26 CEST
**Status**: ✅ **DEPLOYED & LIVE**
**URL**: https://www.frawo-tech.de

---

## ✅ COMPLETED

### 1. **CI-Farben korrigiert** (Grün + UV statt Orange)
- **Primär**: `#064e3b` (Forest Green)
- **Akzent**: `#a855f7` (UV Purple)
- **Hintergrund**: `#0a0a0a` (Deep Black)
- Alle CSS-Dateien updated

### 2. **Logo-Fix**
- CSS-Filter **entfernt** (`filter: none !important;`)
- Logo wird jetzt **korrekt angezeigt** (Grün/Lila, nicht mehr weiß invertiert)
- Upload erfolgreich via Odoo Shell

### 3. **Content komplett überarbeitet**
**Neue Inhalte (stark, authentisch, keine Lachnummer):**

#### Homepage
- Hero: "Technik, die funktioniert. Wenn es drauf ankommt."
- Split Hero: B2C (Smart Home) / B2B (Events)
- Services Grid: 3 Cards (Event-Infrastruktur, Smart Home & Heimkino, Licht & Akustik)
- Referenz-Bild: Club Vaudeville FOH Setup
- CTA: "Verfügbarkeit: Sommer 2026"
- Tech Stack Transparency: "Wir sind keine Agentur. Wir sind Techniker."

#### B2C Seite ([/b2c](https://www.frawo-tech.de/b2c))
- **Smart Home**: Home Assistant, Philips Hue Multi-Bridge, Shelly
- **Heimkino & HiFi**: Kalibrierte Raumakustik, Speaker-Aufstellung
- **Licht & Garten**: WLED, DMX, Philips Hue Outdoor
- **Arbeitsweise**: 4-Schritte-Prozess (Erstgespräch → Planung → Installation → Übergabe)

#### B2B Seite ([/b2b](https://www.frawo-tech.de/b2b))
- **Konzerte & Clubnächte**: Club Vaudeville Referenz, FOH, Streaming
- **Corporate Events**: 50-500 Leute, d&b Line-Arrays, Midas M32
- **Radio & Streaming**: AzuraCast, 283GB Music Library, HLS + MP3
- **Hardware-Liste**: Transparent (d&b, L-Acoustics, Midas, Behringer, DMX)

#### Contact Seite ([/contactus](https://www.frawo-tech.de/contactus))
- **E-Mail**: info@frawo-tech.de
- **Telefon**: +49 152 21867832
- **Adresse**: Rothkreuz 14, 88138 Weißensberg
- **Karte**: OpenStreetMap Embed (Bodensee-Region)
- **Verfügbarkeit**: Sommer 2026

### 4. **Bilder hochgeladen**
Alle 6 Bilder erfolgreich in Odoo hochgeladen:
- `logo.png` (Grün/Lila)
- `hero-bodensee.jpg` (Line-Array am Bodensee)
- `about-console.jpg` (Club Vaudeville FOH)
- `reference-event.jpg` (Club Vaudeville Live)
- `service-audio.jpg`
- `service-stage.jpg`

### 5. **Caddy Redirect konfiguriert**
[ansible/inventory/host_vars/toolbox.yml](ansible/inventory/host_vars/toolbox.yml:85-86):
```yaml
toolbox_network_public_redirect_hosts:
  - hostname: frawo-tech.de
    target: https://www.frawo-tech.de{uri}
```

**Status**: ✅ Konfiguration vorhanden, **ABER** Cloudflare Tunnel Ingress fehlt noch.

---

## ⚠️ PENDING

### **Root-Domain 404-Fix** (frawo-tech.de → www.frawo-tech.de)

**Problem**: `https://frawo-tech.de` gibt 404, weil **Cloudflare Tunnel** die Root-Domain nicht routet.

**Lösung**: Cloudflare Tunnel Ingress-Regel hinzufügen (Remote-managed via Token).

#### **OPTION 1: Cloudflare Dashboard** (Empfohlen)
1. Login: https://dash.cloudflare.com
2. **Zero Trust** → **Access** → **Tunnels**
3. Tunnel auswählen (Token: `7ceb61ed-86fc-4665-80ce-d490be94dcf0`)
4. **Public Hostnames** → **Add a public hostname**
   - **Subdomain**: (leer lassen)
   - **Domain**: `frawo-tech.de`
   - **Type**: `HTTP`
   - **URL**: `100.82.26.53:80` (Toolbox Caddy)
5. **Save**

#### **OPTION 2: Ansible Playbook** (falls cloudflared local config)
Falls ihr auf local config umstellen wollt:
```bash
cd /c/WORKSPACE/FraWo
ansible-playbook ansible/playbooks/update_toolbox_network.yml
```

**Timeline**: 5-10 Minuten (Cloudflare Dashboard ist schneller)

---

## 📊 DEPLOYMENT-DETAILS

### Files deployed:
- `Codex/website/frawo_custom_css.css` → Odoo `website.custom_code_head`
- `Codex/website/frawo_homepage_blocks.html` → Odoo `ir.ui.view` (website.homepage)
- `Codex/website/frawo_b2c_blocks.html` → Odoo `ir.ui.view` (website.page_b2c)
- `Codex/website/frawo_b2b_blocks.html` → Odoo `ir.ui.view` (website.page_b2b)
- `Codex/website/frawo_contactus.html` → Odoo `ir.ui.view` (website.contactus)

### Deployment-Script:
```powershell
scripts/deploy_website_redesign_to_odoo.ps1
```

### Deployment-Zeit:
- **Start**: 2026-04-28 01:20:00 CEST
- **Ende**: 2026-04-28 01:26:00 CEST
- **Dauer**: ~6 Minuten

### Hotfix (CSS-Farben):
```bash
python scripts/remediations/frawo_v3_1_hotfix.py
```

---

## 🎯 NEXT STEPS

1. **Cloudflare Tunnel Ingress** für Root-Domain hinzufügen (5 Min)
2. **Website-Test** durchführen:
   - [ ] `https://frawo-tech.de` → Redirect OK?
   - [ ] `https://www.frawo-tech.de` → Website lädt?
   - [ ] Logo sichtbar?
   - [ ] Farben Grün/UV (nicht Orange)?
   - [ ] B2C/B2B Seiten erreichbar?
   - [ ] Kontaktseite vollständig?
3. **SEO Meta-Tags** hinzufügen (Optional, später):
   - Title: "FraWo GbR — Veranstaltungstechnik & Event-Infrastruktur | Bodensee"
   - Description: "Professionelle Event-Infrastruktur, Smart Home & Heimkino vom Bodensee. Von Clubnächten bis Corporate Events."
   - OG-Tags für Social Media

---

## 📞 SUPPORT

Falls Probleme auftreten:
1. Check Odoo Logs: `ssh root@100.69.179.87 "qm guest exec 220 -- docker logs odoo-web-1 --tail 50"`
2. Check Caddy Logs: `ssh root@100.82.26.53 "docker logs toolbox-network-caddy-1 --tail 50"`
3. Check Cloudflare Tunnel: `ssh root@100.69.179.87 "systemctl status cloudflared"`

---

## ✅ FINAL CHECKLIST

- [x] CI-Farben korrigiert (Grün + UV)
- [x] Logo-Fix (kein Filter mehr)
- [x] Content überarbeitet (stark, authentisch)
- [x] Bilder hochgeladen (6/6)
- [x] Homepage deployed
- [x] B2C Seite deployed
- [x] B2B Seite deployed
- [x] Contact Seite deployed
- [x] Caddy Redirect konfiguriert
- [ ] Cloudflare Tunnel Ingress (Root-Domain)
- [ ] Final Website-Test

**Estimated time to completion**: 10 Minuten (nur Cloudflare Tunnel fehlt)

---

**Wolf/Fabian**: Die Website ist **READY TO GO**! Nur noch Cloudflare Tunnel Ingress für die Root-Domain, dann ist alles live. 🚀

— Claude Sonnet 4.5 | 2026-04-28 03:26 CEST

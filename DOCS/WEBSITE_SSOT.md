# Website Single Source of Truth (SSOT)

**Letztes Update**: 2026-05-19
**Aktueller Status**: ✅ **LIVE**
**URL**: [https://www.frawo-tech.de](https://www.frawo-tech.de)
**Version**: v4 "Optimized"

---

## 🏗️ Architektur & Technologie
- **Plattform**: Odoo 17 (VM 220)
- **Frontend-Stil**: NTS-inspired, High-Contrast, Editorial.
- **Design-Elemente**:
  - Dark Mode (`#0a0a0a`)
  - Accent Colors: Forest Green (`#064e3b`) & UV Purple (`#a855f7`)
  - Font: **Inter**
  - Layout: Grid-basiert, 1px Borders, native Scroll-Animationen (Fade-In).
- **Ingress**: Cloudflare Proxy -> Toolbox (Caddy Proxy/Redirect) -> Odoo.
- **Formulare**: Nativer Odoo Form Builder mit CSRF-Token Security (`/website/form/`).

---

## 📄 Seitenstruktur
- `/` (Homepage): Hero (Links-bündig), Split B2C/B2B, Service Grid, Verfügbarkeit.
- `/b2c`: Smart Home, Heimkino, Licht, Prozess.
- `/b2b`: Konzerte, Corporate Events, Radio/Streaming, Hardware (Custom KMT PA, Digitalmixer).
- `/contactus`: Dynamisches Kontaktformular (Leads gehen direkt ins CRM).

---

## ✅ Erreichte Meilensteine (Stand 2026-05-19)
- [x] Design-Migration auf v4 (Optimized, CI-Farben).
- [x] Kontrast global via CSS-Overrides gefixt (`#f5f5f5` Text, `#ffffff` Headings).
- [x] Hardware-Specs bereinigt (Custom KMT PA, Digital Mixing Consoles).
- [x] SEO & Meta-Tags implementiert (Title, Description).
- [x] Radio Player Integration ("FraWo Funk") als Sticky Footer.
- [x] Kontaktformular-Security (CSRF) & Routing ins Odoo CRM.
- [x] Cloudflare Security (IP-Maskierung, Port 8069-Schutz).
- [x] Postausgangsserver (SMTP Strato) in Odoo konfiguriert (Senden wieder möglich).
- [x] Odoo-Masterplan Tasks aktualisiert (Lane B -> Erledigt).

---

## 🎯 Offene Aufgaben (Next Steps)
### 1. Odoo CRM & Mail-Automation (Prio 1)
- [ ] Posteingangsserver (IMAP) in Odoo einrichten (für `info@frawo-tech.de`).
- [ ] Automatische Kundenanlage (Customer) bei neuen E-Mail-Leads.
- [ ] Benutzerrechte & Rollenverteilung in Odoo schärfen (Wolf vs. Franz).

### 2. Nextcloud & Azurecast Backend (Prio 2)
- [ ] Cloudflare Tunnels für `cloud.frawo-tech.de` und `radio.frawo-tech.de` sauber einrichten.
- [ ] Musikverwaltung synchronisieren.

---

## 🛠️ Deployment-Prozess (Automatisierung)
Die Website wird primär über automatisierte Skripte verwaltet. 
- Alle Source-Dateien liegen in `Codex/website/`.
- Alte Entwürfe sind archiviert in `Codex/website/archive_v3/`.
- **Deployment Skripte**:
  - `scripts/deploy_homepage_from_file.py`: Pusht Homepage + Radio-Player.
  - `scripts/deploy_b2b_b2c.py`: Pusht B2C/B2B Views.
  - `scripts/upload_css_to_odoo.py`: Pusht die `frawo_custom_css.css`.

---

## 📊 Odoo Projekt-Synchronisierung
Die operativen Aufgaben werden in Odoo im Projekt **"🚀 Homeserver 2027: Masterplan"** verwaltet.
- Der Task `[Lane B] Website & Public Activation` ist abgeschlossen (✅ Erledigt).
- **Das Projekt ist das einzige und finale SSOT für Projektmanagement.**

---

## 📞 Support & Debugging
- **Odoo Login (Extern)**: `https://www.frawo-tech.de/web/login`
- **Cloudflare**: [dash.cloudflare.com](https://dash.cloudflare.com)

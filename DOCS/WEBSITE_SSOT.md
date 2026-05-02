# Website Single Source of Truth (SSOT)

**Letztes Update**: 2026-04-30
**Aktueller Status**: ✅ **LIVE**
**URL**: [https://www.frawo-tech.de](https://www.frawo-tech.de)
**Version**: v3.5 "Ultra Minimal"

---

## 🏗️ Architektur & Technologie
- **Plattform**: Odoo 17 (VM 220)
- **Frontend-Stil**: NTS-inspired, Ultra-Minimal, Editorial.
- **Design-Elemente**:
  - Dark Mode (`#0a0a0a`)
  - Accent Colors: Forest Green (`#064e3b`) & UV Purple (`#a855f7`)
  - Font: **Inter**
  - Layout: 1px Borders, Grid-basiert.
- **Ingress**: Cloudflare Tunnel -> Toolbox (Caddy Proxy/Redirect) -> Odoo.

---

## 📄 Seitenstruktur
- `/` (Homepage): Hero, Split B2C/B2B, Service Grid, Verfügbarkeit.
- `/b2c`: Smart Home, Heimkino, Licht, Prozess.
- `/b2b`: Konzerte, Corporate Events, Radio/Streaming, Hardware.
- `/contactus`: Kontaktinformationen, Karte, Verfügbarkeit.

---

## ✅ Erreichte Meilensteine (Stand 2026-04-30)
- [x] Design-Migration auf v3.5 (NTS-Style).
- [x] CI-Farben (Grün/Lila) korrekt implementiert.
- [x] Logo-Fix (Größe, mix-blend-mode).
- [x] Content-Überarbeitung (Fakten statt Floskeln).
- [x] Erreichbarkeit via HTTPS (www.frawo-tech.de).
- [x] Caddy Redirect für Root-Domain (frawo-tech.de).

---

## 🎯 Offene Aufgaben (Next Steps)
### 1. SEO & Meta-Tags (Priorität 1)
- [ ] **Meta Description** hinzufügen.
- [ ] **OG:Description** & **OG:URL** (HTTPS) korrigieren.
- [ ] **H2-Überschriften** strukturieren (aktuell nur H1 und H3).

### 2. Rechtliches & Compliance (Priorität 2)
- [ ] **Impressum** Seite erstellen/verlinken.
- [ ] **Datenschutz** Seite erstellen/verlinken.

### 3. Performance & Content (Priorität 3)
- [ ] **JSON-LD Structured Data** (Organization, LocalBusiness).
- [ ] **Gzip/Brotli Compression** prüfen (Proxy-Level).
- [ ] **Bilder-Optimierung** (WebP).
- [ ] **Radio Player** Integration (Sticky Footer).

---

## 🛠️ Deployment-Prozess (Automatisierung)
Die Website wird primär über automatisierte Skripte verwaltet. Manuelle Änderungen im Odoo-Backend sollten auf das Nötigste beschränkt bleiben (WYSIWYG-Content).

- **CSS-Injektion**: Erfolgt via `website.custom_code_head` (XML-RPC).
- **HTML-Blocks**: Werden in das `arch`-Feld der Homepage-View injiziert.
- **Skripte**:
  - `scripts/deploy_v3_5_final.ps1`: Gesamtes Deployment (CSS + HTML).
  - `scripts/remediations/website_seo_boost.py`: SEO-Optimierung (Meta-Tags, Base URL).

---

## 📊 Odoo Projekt-Synchronisierung
Die operativen Aufgaben werden in Odoo im Projekt **"FraWo Website v3.5 & Infrastructure"** gespiegelt.

- **Sync-Logik**: `scripts/remediations/odoo_project_sync.py` (via `odoo shell`).
- **Abgleich**: Die Tasks entsprechen der Odoo-Projektwahrheit; `current_plan.json` bleibt nur ein Lane-Snapshot.
- **Status-Tracking**: Meilensteine in Odoo werden automatisch aktualisiert, wenn Skripte erfolgreich durchlaufen.

---

## 📞 Support & Debugging
- **Odoo Logs**: `ssh root@100.69.179.87 "qm guest exec 220 -- docker logs odoo-web-1 --tail 50"`
- **Caddy Logs**: `ssh root@100.82.26.53 "docker logs toolbox-network-caddy-1 --tail 50"`
- **Cloudflare**: [dash.cloudflare.com](https://dash.cloudflare.com) (Token: `7ceb61ed-86fc-4665-80ce-d490be94dcf0`)

---

## 🗑️ Dokumenten-Cleanup (Consolidated)
Folgende Dateien wurden als veraltet markiert oder in dieses SSOT überführt:
- `DOCS/WEBSITE_V3_1_HANDOFF.md` (gelöscht)
- `DOCS/WEBSITE_V3_FINAL_SUMMARY.md` (gelöscht)
- `DOCS/ODOO_DEPLOYMENT_ANLEITUNG_V3.5.md` (überführt)
- `DOCS/Task_Archive/CLAUDE_WEBSITE_HOSTING_HANDOFF.md` (gelöscht)

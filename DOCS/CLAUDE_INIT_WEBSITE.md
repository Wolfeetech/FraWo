# Claude Init Prompt - FraWo Website SEO & Best Practices

## Deine Aufgabe
Du bist ausschließlich für **frawo-tech.de Website** zuständig.
Gemini kümmert sich parallel um **FraWo Funk (Radio)**.

## Offizieller Scope

- Claude Code arbeitet in diesem Repo offiziell an Website, Odoo-Content, SEO und kuratierten Business-Syncs.
- Claude Code fuehrt keine direkten Default-Eingriffe an PVE, Firewall, Routing oder Multi-DB-Odoo-Migrationen.
- Wenn Website-Arbeit eine Infra-Aenderung erfordert, wird ein Handoff an Codex oder den Operator formuliert.

## Aktueller Status

### Website Stack
- **CMS**: Odoo 17 Website Builder (10.4.0.22:8069, DB: FraWo_GbR)
- **Live**: https://www.frawo-tech.de
- **Design**: kabaus.at-inspiriert + NTS Radio Minimal + FraWo CI
- **Letztes Deployment**: 2026-05-14 (Content-Simplification)

### Fertiggestellt ✅
- Hero Section mit CI-konformem Layout
- 4 Service Cards (2×2 Grid, einheitlich)
- Referenzen-Grid (4×2)
- Projekte-Sektion (3×1, hover-overlays)
- Über Uns (Wolf + Franz)
- Radio CTA (Link zu funk.frawo-tech.de)
- Footer (Odoo Copyright hidden)
- DSGVO: Impressum + Datenschutz

### Deployment Scripts
```
scripts/deploy_new_homepage.py       # Homepage HTML
scripts/upload_css_to_odoo.py        # CSS Upload
scripts/generate_legal_pages.py      # Impressum/Datenschutz
scripts/upload_images_to_odoo.py     # Bilder (IDs 993-1000)
```

## Deine Ziele (Reihenfolge)

### 1. SEO Basics
- [ ] Meta Title: "FraWo Veranstaltungstechnik Bodensee | Licht & Ton"
- [ ] Meta Description: Prägnant, Keyword-optimiert (150-160 Zeichen)
- [ ] Canonical URL setzen
- [ ] Open Graph Tags (og:title, og:description, og:image)
- [ ] robots.txt prüfen/erstellen
- [ ] sitemap.xml generieren

### 2. Performance Optimization
- [ ] Bilder komprimieren (WebP wo möglich)
- [ ] Lazy Loading für Images
- [ ] CSS Minification prüfen
- [ ] Google PageSpeed Insights Score >90

### 3. Accessibility (a11y)
- [ ] Alt-Texte für alle Bilder optimieren
- [ ] Heading-Hierarchie prüfen (H1 → H2 → H3)
- [ ] Kontrast-Ratio prüfen (WCAG AA)
- [ ] Keyboard-Navigation testen
- [ ] ARIA-Labels wo nötig

### 4. Schema.org Markup
- [ ] LocalBusiness Schema (Rothkreuz 14, Weissensberg)
- [ ] Service Schema (Licht & Ton, Verleih, etc.)
- [ ] Organization Schema
- [ ] BreadcrumbList für Navigation

### 5. Content-Optimierung
- [ ] Keyword-Density prüfen ("Veranstaltungstechnik Bodensee")
- [ ] LSI Keywords integrieren
- [ ] Call-to-Actions optimieren
- [ ] Internal Linking Strategy

### 6. Mobile Optimization
- [ ] Responsive Breakpoints testen (768px, 991px)
- [ ] Touch-Targets min. 48×48px
- [ ] Font-Sizes lesbar auf Mobile
- [ ] Navigation auf Mobile optimieren

### 7. Tracking & Analytics
- [ ] Google Analytics 4 Setup (falls gewünscht)
- [ ] Google Search Console Integration
- [ ] Cookie-Banner DSGVO-konform (falls Tracking)

## Wichtige Infos

### FraWo CI Colors
```css
:root {
  --fw-bg: #0a0a0a;
  --fw-text: #e0e0e0;
  --fw-text-dim: #888888;
  --fw-text-dimmer: #555555;
  --fw-border: #1a1a1a;
  --fw-uv: #a855f7;
  --fw-forest: #0d4d4d;
}
```

### Credentials
```
~/.ai-tools-shared/.env
ODOO_RPC_URL=http://10.4.0.22:8069
ODOO_RPC_DB=FraWo_GbR
ODOO_RPC_USER=...
ODOO_RPC_API_KEY=...
```

### DO NOT TOUCH
- ❌ Radio-Setup (funk.frawo-tech.de)
- ❌ `/DOCS/RADIO_*` Files
- ❌ Proxmox/Infrastructure außer dokumentiertem Handoff
- ❌ Secret-Bootstrap oder Credential-Rotation

### User-Feedback-Style
- "weniger reden mehr sagen"
- "kein AI-Geschwätz"
- Keine selbst-abwertenden Texte
- Direkt, ehrlich, professionell
- Keine Emojis (außer explizit gewünscht)

## Design-Referenzen

### kabaus.at
- Grid-Layout (1px borders)
- Professional spacing (120px sections)
- Minimale Animationen
- Clear hierarchy

### NTS Radio
- Ultra-minimal
- Dark theme (#0a0a0a)
- Subtle borders
- Monospace-freundlich

## Erfolg =
✅ Google PageSpeed >90 (Mobile + Desktop)
✅ Alle SEO-Basics implementiert
✅ Schema.org Markup validiert
✅ WCAG AA konform
✅ Google Search Console indexiert

## Wichtige Dateien
```
Codex/website/frawo_custom_css.css           # Main CSS
scripts/deploy_new_homepage.py               # Homepage Deployment
DOCS/FRAWO_CI_GUIDELINES.md                  # CI Spec
DOCS/FRAWO_SERVICES_REAL.md                  # Service-Definitionen
```

---

**Start hier:** Meta Tags + Schema.org Markup implementieren.

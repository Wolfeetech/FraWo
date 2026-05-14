# FraWo Website Redesign - Umsetzungsplan

**Erstellt:** 2026-05-13
**Design-Konzept:** [DESIGN_CONCEPT_KABAUS_NTS.md](DESIGN_CONCEPT_KABAUS_NTS.md)
**Ziel:** kabaus.at Ästhetik + NTS Radio Touch in Odoo

---

## 🎯 ÜBERBLICK

### Was wird gemacht?
Komplettes Redesign der frawo-tech.de Website mit:
- **kabaus.at-Stil:** Minimalistisch, professionell, B2B-fokussiert
- **NTS Radio Touch:** Sticky Audio Player, monochrom-elegant
- **Custom Odoo Theme:** Keine Standard-Bootstrap-Optik mehr

### Warum?
- Aktuell: Generic Bootstrap-Look
- Neu: Einzigartiges, professionelles Branding
- Radio-Integration als Alleinstellungsmerkmal

---

## 📋 PHASEN-ÜBERSICHT

| Phase | Dauer | Tasks | Priority |
|-------|-------|-------|----------|
| **Phase 1: Foundation** | 1-2 Tage | Farben, Fonts, Base-Styles | 🔴 KRITISCH |
| **Phase 2: Layout** | 2-3 Tage | Header, Hero, Grid-System | 🔴 KRITISCH |
| **Phase 3: Components** | 2-3 Tage | Cards, Buttons, Icons | 🟡 WICHTIG |
| **Phase 4: Radio** | 1 Tag | Sticky Player, Integration | 🟡 WICHTIG |
| **Phase 5: Content** | 1-2 Tage | Texte, Bilder, Testimonials | 🟢 NORMAL |
| **Phase 6: Polish** | 1 Tag | Animationen, Testing, QA | 🟢 NORMAL |

**Gesamt:** ~8-12 Tage

---

## 🛠️ PHASE 1: FOUNDATION (1-2 Tage)

### 1.1 CSS Custom Properties erstellen

**Datei:** `website_frawo_theme/static/src/css/variables.css`

```css
:root {
  /* === COLORS === */
  --frawo-black: #000000;
  --frawo-white: #FFFFFF;
  --frawo-gray-dark: #1a1a1a;
  --frawo-gray-mid: #555555;
  --frawo-gray-light: #888888;
  --frawo-purple: #a855f7;
  --frawo-orange: #ff6b35;
  --frawo-blue: #0066cc;

  /* === TYPOGRAPHY === */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  --font-size-2xl: 36px;
  --font-size-3xl: 48px;

  /* === SPACING === */
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 32px;
  --spacing-lg: 64px;
  --spacing-xl: 128px;

  /* === BORDERS === */
  --border-color: #e0e0e0;
  --border-color-dark: #1a1a1a;
  --border-radius: 4px;

  /* === SHADOWS === */
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);

  /* === TRANSITIONS === */
  --transition-fast: 0.2s ease;
  --transition-medium: 0.3s ease;
  --transition-slow: 0.6s ease;

  /* === Z-INDEX === */
  --z-header: 1000;
  --z-modal: 2000;
  --z-radio-player: 9999;
}
```

### 1.2 Inter Font einbinden

**Datei:** `website_frawo_theme/static/src/css/fonts.css`

```css
/* Inter Font from Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: var(--font-primary);
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--frawo-gray-dark);
  background: var(--frawo-white);
}

/* Heading Hierarchy */
h1 {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: var(--frawo-black);
}

h2 {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.3;
  color: var(--frawo-black);
}

h3 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  line-height: 1.4;
  color: var(--frawo-black);
}

h4 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  line-height: 1.4;
  color: var(--frawo-black);
}

p {
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--frawo-gray-mid);
}
```

### 1.3 Reset & Base Styles

**Datei:** `website_frawo_theme/static/src/css/base.css`

```css
/* Box-sizing reset */
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* Remove default margins */
body, h1, h2, h3, h4, h5, h6, p, ul, ol {
  margin: 0;
  padding: 0;
}

/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

@media (max-width: 767px) {
  .container {
    padding: 0 var(--spacing-sm);
  }
}

/* Section Spacing */
.section {
  padding: var(--spacing-lg) 0;
}

.section-lg {
  padding: var(--spacing-xl) 0;
}

@media (max-width: 767px) {
  .section { padding: var(--spacing-md) 0; }
  .section-lg { padding: var(--spacing-lg) 0; }
}
```

### 1.4 Odoo Manifest

**Datei:** `website_frawo_theme/__manifest__.py`

```python
{
    'name': 'FraWo Website Theme',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Custom theme with kabaus.at + NTS Radio styling',
    'description': """
        FraWo Website Theme
        ===================
        - Minimalistic, professional design
        - kabaus.at inspired layout
        - NTS Radio integrated player
        - Custom components and snippets
    """,
    'author': 'FraWo GbR',
    'website': 'https://www.frawo-tech.de',
    'depends': ['website'],
    'data': [
        'views/templates.xml',
        'views/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # CSS
            'website_frawo_theme/static/src/css/variables.css',
            'website_frawo_theme/static/src/css/fonts.css',
            'website_frawo_theme/static/src/css/base.css',
            'website_frawo_theme/static/src/css/components.css',
            'website_frawo_theme/static/src/css/header.css',
            'website_frawo_theme/static/src/css/footer.css',
            'website_frawo_theme/static/src/css/radio-player.css',
            # JS
            'website_frawo_theme/static/src/js/radio-player.js',
            'website_frawo_theme/static/src/js/animations.js',
        ],
    },
    'installable': True,
    'application': False,
}
```

---

## 🏗️ PHASE 2: LAYOUT (2-3 Tage)

### 2.1 Header (kabaus-Stil)

**Datei:** `website_frawo_theme/views/templates.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <!-- Custom Header -->
  <template id="custom_header" inherit_id="website.layout" name="FraWo Header">
    <xpath expr="//header" position="replace">
      <header class="frawo-header">
        <div class="container">
          <nav class="frawo-nav">
            <div class="frawo-nav-left">
              <a href="#leistungen">Leistungen</a>
              <a href="#referenzen">Referenzen</a>
            </div>

            <a href="/" class="frawo-logo">
              <img src="/web/image/website/1/logo" alt="FraWo GbR"/>
            </a>

            <div class="frawo-nav-right">
              <a href="/radio">Radio</a>
              <a href="/blog">Blog</a>
              <a href="/contactus">Kontakt</a>
            </div>
          </nav>
        </div>
      </header>
    </xpath>
  </template>
</odoo>
```

**CSS:** `website_frawo_theme/static/src/css/header.css`

```css
.frawo-header {
  background: var(--frawo-black);
  position: sticky;
  top: 0;
  z-index: var(--z-header);
  border-bottom: 1px solid var(--border-color-dark);
}

.frawo-nav {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: var(--spacing-sm) 0;
  gap: var(--spacing-md);
}

.frawo-nav-left,
.frawo-nav-right {
  display: flex;
  gap: var(--spacing-md);
}

.frawo-nav-right {
  justify-content: flex-end;
}

.frawo-nav a {
  color: var(--frawo-white);
  text-decoration: none;
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.frawo-nav a:hover {
  color: var(--frawo-orange);
}

.frawo-logo img {
  max-height: 40px;
  width: auto;
}

/* Mobile */
@media (max-width: 768px) {
  .frawo-nav {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .frawo-nav-left,
  .frawo-nav-right {
    justify-content: center;
    flex-wrap: wrap;
  }
}
```

### 2.2 Hero Section

**Snippet:** `website_frawo_theme/views/snippets.xml`

```xml
<template id="snippet_frawo_hero" name="FraWo Hero">
  <section class="frawo-hero section-lg">
    <div class="container">
      <h1 class="frawo-hero-title">Von der Idee zur IT-Lösung</h1>

      <div class="frawo-hero-process">
        <div class="process-step">
          <svg class="process-icon"><!-- Konzept Icon --></svg>
          <span>Konzeption</span>
        </div>
        <svg class="process-arrow">→</svg>
        <div class="process-step">
          <svg class="process-icon"><!-- Planung Icon --></svg>
          <span>Planung</span>
        </div>
        <svg class="process-arrow">→</svg>
        <div class="process-step">
          <svg class="process-icon"><!-- Tech Icon --></svg>
          <span>Umsetzung</span>
        </div>
        <svg class="process-arrow">→</svg>
        <div class="process-step">
          <svg class="process-icon"><!-- Check Icon --></svg>
          <span>Support</span>
        </div>
      </div>

      <a href="/contactus" class="btn-primary">Projekt starten</a>
    </div>
  </section>
</template>
```

**CSS:**

```css
.frawo-hero {
  background: var(--frawo-white);
  text-align: center;
}

.frawo-hero-title {
  margin-bottom: var(--spacing-lg);
}

.frawo-hero-process {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.process-icon {
  width: 64px;
  height: 64px;
  color: var(--frawo-gray-dark);
}

.process-arrow {
  font-size: 32px;
  color: var(--frawo-gray-light);
}

@media (max-width: 768px) {
  .frawo-hero-process {
    flex-direction: column;
  }
  .process-arrow {
    transform: rotate(90deg);
  }
}
```

### 2.3 Services Grid (4-Karten)

```xml
<template id="snippet_frawo_services" name="FraWo Services Grid">
  <section class="frawo-services section">
    <div class="container">
      <h2 class="section-title">Unsere Leistungen</h2>

      <div class="services-grid">
        <div class="service-card">
          <svg class="service-icon"><!-- Web Icon --></svg>
          <h3>Web Development</h3>
          <p>Moderne Webanwendungen mit Fokus auf Performance und UX.</p>
          <a href="/services/web" class="service-link">Mehr erfahren →</a>
        </div>

        <div class="service-card">
          <svg class="service-icon"><!-- Server Icon --></svg>
          <h3>Infrastruktur</h3>
          <p>Proxmox, Docker, Kubernetes - Ihre IT-Umgebung professionell betreut.</p>
          <a href="/services/infra" class="service-link">Mehr erfahren →</a>
        </div>

        <div class="service-card">
          <svg class="service-icon"><!-- Radio Icon --></svg>
          <h3>Radio Streaming</h3>
          <p>AzuraCast-Setup, Icecast-Relays, kuratierte Playlists.</p>
          <a href="/radio" class="service-link">Mehr erfahren →</a>
        </div>

        <div class="service-card">
          <svg class="service-icon"><!-- Automation Icon --></svg>
          <h3>Automation</h3>
          <p>n8n Workflows, CI/CD Pipelines, Prozessoptimierung.</p>
          <a href="/services/automation" class="service-link">Mehr erfahren →</a>
        </div>
      </div>
    </div>
  </section>
</template>
```

**CSS:** `website_frawo_theme/static/src/css/components.css`

```css
.services-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.service-card {
  background: var(--frawo-white);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
  transition: all var(--transition-medium);
}

.service-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-4px);
}

.service-icon {
  width: 48px;
  height: 48px;
  color: var(--frawo-orange);
  margin-bottom: var(--spacing-sm);
}

.service-card h3 {
  margin-bottom: var(--spacing-xs);
}

.service-card p {
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.service-link {
  display: inline-block;
  color: var(--frawo-orange);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  transition: color var(--transition-fast);
}

.service-link:hover {
  color: var(--frawo-black);
}

/* Responsive */
@media (max-width: 1023px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .services-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## 🎵 PHASE 3: RADIO PLAYER (1 Tag)

### 3.1 Sticky Footer Player (NTS-Stil)

**Template:**

```xml
<template id="radio_player_sticky" inherit_id="website.layout" name="FraWo Radio Player">
  <xpath expr="//body" position="inside">
    <div class="frawo-radio-player" id="frawo-radio-player" style="display: none;">
      <div class="container">
        <div class="radio-player-inner">
          <div class="radio-station">FraWo Funk</div>

          <div class="radio-status" id="radio-status">
            <span class="status-text">Coming Soon</span>
          </div>

          <div class="radio-controls">
            <button class="radio-btn" id="radio-play-btn" disabled="disabled">
              <svg><!-- Play Icon --></svg>
            </button>
            <button class="radio-btn" id="radio-pause-btn" style="display: none;">
              <svg><!-- Pause Icon --></svg>
            </button>

            <div class="radio-volume" id="radio-volume">
              <div class="radio-volume-fill" id="radio-volume-fill"></div>
            </div>
          </div>

          <button class="radio-close" id="radio-close-btn">&times;</button>
        </div>
      </div>
    </div>
  </xpath>
</template>
```

**CSS:** `website_frawo_theme/static/src/css/radio-player.css`

```css
.frawo-radio-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--frawo-black);
  border-top: 1px solid var(--border-color-dark);
  z-index: var(--z-radio-player);
  padding: var(--spacing-sm) 0;
}

.radio-player-inner {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: var(--spacing-md);
  align-items: center;
}

.radio-station {
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--frawo-gray-light);
  font-weight: 500;
}

.radio-status {
  font-size: var(--font-size-sm);
  color: var(--frawo-gray-mid);
}

.radio-status.live {
  color: var(--frawo-purple);
}

.radio-status.live::before {
  content: "●";
  margin-right: 0.5em;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.radio-controls {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.radio-btn {
  background: transparent;
  border: 1px solid var(--border-color-dark);
  color: var(--frawo-gray-light);
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.radio-btn:hover {
  border-color: var(--frawo-gray-light);
  color: var(--frawo-white);
}

.radio-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.radio-volume {
  width: 80px;
  height: 2px;
  background: var(--border-color-dark);
  position: relative;
  cursor: pointer;
}

.radio-volume-fill {
  height: 100%;
  background: var(--frawo-gray-light);
  width: 70%;
  transition: width 0.1s ease;
}

.radio-close {
  background: none;
  border: none;
  color: var(--frawo-gray-mid);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  line-height: 1;
  transition: color var(--transition-fast);
}

.radio-close:hover {
  color: var(--frawo-gray-light);
}

/* Mobile */
@media (max-width: 768px) {
  .radio-player-inner {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
    text-align: center;
  }

  .radio-controls {
    justify-content: center;
  }
}
```

**JavaScript:** (Kopiere aus existierendem `frawo_radio_player.html`)

---

## 🎨 PHASE 4: COMPONENTS & POLISH (2-3 Tage)

### 4.1 Buttons

**CSS:**

```css
/* Primary Button (Orange) */
.btn-primary {
  display: inline-block;
  background: var(--frawo-orange);
  color: var(--frawo-white);
  padding: 16px 32px;
  border: none;
  border-radius: var(--border-radius);
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background: #e55a2b;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
  transform: translateY(-2px);
}

/* Secondary Button (Outline) */
.btn-secondary {
  background: transparent;
  color: var(--frawo-black);
  border: 1px solid var(--frawo-black);
  /* rest same as primary */
}

.btn-secondary:hover {
  background: var(--frawo-black);
  color: var(--frawo-white);
}
```

### 4.2 Footer

```xml
<template id="custom_footer" inherit_id="website.layout" name="FraWo Footer">
  <xpath expr="//footer" position="replace">
    <footer class="frawo-footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-col">
            <h4>FraWo GbR</h4>
            <p>Stockenweiler 7<br/>88662 Überlingen<br/>Deutschland</p>
            <div class="footer-contact">
              <a href="mailto:info@frawo-tech.de">
                <svg><!-- Mail Icon --></svg>
                info@frawo-tech.de
              </a>
              <a href="tel:+4975519479870">
                <svg><!-- Phone Icon --></svg>
                +49 (0) 7551 947 9870
              </a>
            </div>
          </div>

          <div class="footer-col">
            <h4>Leistungen</h4>
            <ul>
              <li><a href="/services/web">Web Development</a></li>
              <li><a href="/services/infra">Infrastruktur</a></li>
              <li><a href="/radio">Radio Streaming</a></li>
              <li><a href="/services/automation">Automation</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Rechtliches</h4>
            <ul>
              <li><a href="/impressum">Impressum</a></li>
              <li><a href="/datenschutz">Datenschutz</a></li>
              <li><a href="/agb">AGB</a></li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  </xpath>
</template>
```

**CSS:**

```css
.frawo-footer {
  background: var(--frawo-black);
  color: var(--frawo-gray-light);
  padding: var(--spacing-lg) 0;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}

.footer-col h4 {
  color: var(--frawo-white);
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-base);
}

.footer-col p {
  font-size: var(--font-size-sm);
  line-height: 1.8;
  color: var(--frawo-gray-light);
}

.footer-col ul {
  list-style: none;
}

.footer-col ul li {
  margin-bottom: var(--spacing-xs);
}

.footer-col a {
  color: var(--frawo-gray-light);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: color var(--transition-fast);
}

.footer-col a:hover {
  color: var(--frawo-orange);
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}
```

---

## 🚀 DEPLOYMENT-SCHRITTE

### 1. Theme installieren

```bash
# Auf Odoo-Server
cd /opt/odoo/addons
git clone <repo> website_frawo_theme

# Odoo neustarten
sudo systemctl restart odoo
```

### 2. Theme aktivieren

```
Odoo → Website → Konfiguration → Themes
→ FraWo Website Theme installieren
```

### 3. Snippets einfügen

```
Website → Edit → Building Blocks
→ "FraWo Hero" einfügen
→ "FraWo Services Grid" einfügen
→ "FraWo Radio Player" einfügen (automatisch)
```

### 4. Testen

- ✅ Desktop (Chrome, Firefox, Safari)
- ✅ Tablet (iPad)
- ✅ Mobile (iPhone, Android)
- ✅ Radio Player funktioniert
- ✅ Alle Links funktionieren

---

## 📋 CHECKLISTE

### Foundation ✅
- [ ] CSS Custom Properties (`variables.css`)
- [ ] Inter Font eingebunden (`fonts.css`)
- [ ] Base Styles (`base.css`)
- [ ] Odoo Manifest (`__manifest__.py`)

### Layout ✅
- [ ] Header (kabaus-Stil) (`header.css`, `templates.xml`)
- [ ] Hero Section (`snippets.xml`)
- [ ] Services Grid (4 Cards)
- [ ] Footer (`templates.xml`, `footer.css`)

### Components ✅
- [ ] Buttons (Primary/Secondary)
- [ ] Service Cards
- [ ] Icons (SVG Set)
- [ ] Process Flow Icons

### Radio Player ✅
- [ ] Sticky Footer Player (`radio-player.css`)
- [ ] JavaScript Integration (`radio-player.js`)
- [ ] Live Status mit Puls-Animation
- [ ] Volume Control
- [ ] Mobile-optimiert

### Content ✅
- [ ] Texte aktualisiert
- [ ] Bilder optimiert (WebP)
- [ ] SEO Meta Tags
- [ ] Impressum/Datenschutz verlinkt

### Testing ✅
- [ ] Cross-Browser (Chrome, Firefox, Safari)
- [ ] Responsive (Mobile, Tablet, Desktop)
- [ ] Performance (<2s Ladezeit)
- [ ] Accessibility (WCAG AA)
- [ ] Radio Player funktioniert

---

## 🎯 ERFOLGS-METRIKEN

**Design ist "Live" wenn:**
- ✅ kabaus.at Ästhetik erkennbar (10/10 Ähnlichkeit)
- ✅ NTS Radio Player funktioniert (Sticky, responsive)
- ✅ Alle 4 Services sichtbar (Grid-Layout)
- ✅ Mobile-optimiert (Touch-friendly)
- ✅ Ladezeit <2s (Google PageSpeed >90)
- ✅ Keine Bootstrap-Standard-Optik mehr

---

**Nächster Schritt:** Phase 1 starten - Foundation erstellen! 🚀

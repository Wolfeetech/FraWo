# FraWo Website - Design-Konzept (kabaus.at + NTS Radio Touch)

**Erstellt:** 2026-05-13
**Inspiriert von:** kabaus.at (B2B Professionalität) + NTS Radio (Audio-First UX)
**Ziel:** Modernes, minimalistisches Design mit Radio-Integration

---

## 🎨 DESIGN-PHILOSOPHIE

**kabaus.at = B2B Professionalität:**
- Klare Struktur "Von Idee zur Umsetzung"
- Großzügiger Whitespace
- Sachliche, vertrauenswürdige Ästhetik

**NTS Radio = Audio-First Experience:**
- Minimales, monochrom-elegantes Interface
- Persistent Audio Player (sticky)
- Discovery über kuratorische Elemente

**FraWo Fusion:**
> "Professionelle IT-Services mit Radio-Seele"

---

## 🎯 FARBSCHEMA

### Primary Palette (von kabaus.at inspiriert)
```css
--frawo-black: #000000;        /* Basis, Header, Footer */
--frawo-white: #FFFFFF;        /* Content-Background */
--frawo-gray-dark: #1a1a1a;   /* Subtle Borders */
--frawo-gray-mid: #555555;    /* Secondary Text */
--frawo-gray-light: #888888;  /* Tertiary, Icons */
```

### Accent Colors (für Radio & CTAs)
```css
--frawo-purple: #a855f7;      /* Radio Live-Status (von NTS) */
--frawo-orange: #ff6b35;      /* CTA Buttons, Links (von kabaus) */
--frawo-blue: #0066cc;        /* Alternative CTAs */
```

### Anwendung
- **Header/Footer:** Schwarz (#000) mit weißem Text
- **Hero:** Weiß mit schwarzem Text
- **Sections:** Alternierend weiß/hellgrau (#f5f5f5)
- **Radio Player:** Schwarz mit Purple-Akzent (#a855f7)
- **Buttons:** Orange (#ff6b35) für Primary, Outline für Secondary

---

## 📐 LAYOUT-STRUKTUR

### Header (kabaus-Stil)
```
┌─────────────────────────────────────────────────┐
│  [Logo]    Leistungen  Referenzen  Radio  Blog │  ← Symmetrisch, zentral
│                      [FraWo GbR]                 │
│                     Kontakt                      │
└─────────────────────────────────────────────────┘
```

**Specs:**
- Background: `#000`
- Text: `#fff`, Hover: `#ff6b35`
- Logo zentral, Navigation links/rechts
- Sticky on scroll (z-index: 1000)

---

### Hero Section (kabaus meets NTS)
```
┌─────────────────────────────────────────────────┐
│                                                  │
│          Von der Idee zur IT-Lösung             │  ← H1, groß
│                                                  │
│   [Icon: Konzept] → [Icon: Tech] → [Icon: ✓]   │  ← Process Flow
│                                                  │
│         [CTA: Projekt starten]                   │  ← Orange Button
│                                                  │
└─────────────────────────────────────────────────┘
```

**Specs:**
- Padding: `80px 0`
- H1: `48px`, `font-weight: 700`, `letter-spacing: -0.02em`
- Icons: SVG, `64x64`, `#1a1a1a`
- CTA: Orange, `padding: 16px 32px`

---

### Services Section (kabaus 4-Karten-Layout)
```
┌────────┬────────┬────────┬────────┐
│ Icon   │ Icon   │ Icon   │ Icon   │
│ Web    │ Infra  │ Radio  │ Auto   │
│ Dev    │ Mgmt   │ Stream │ Mgmt   │
│        │        │        │        │
│ [→]    │ [→]    │ [→]    │ [→]    │
└────────┴────────┴────────┴────────┘
```

**Specs:**
- Grid: `4 Columns`, Gap: `32px`
- Cards: `border: 1px solid #e0e0e0`, `padding: 32px`
- Hover: `box-shadow: 0 4px 12px rgba(0,0,0,0.08)`
- Icon: `48x48`, Orange
- Title: `20px`, `font-weight: 600`
- Body: `14px`, `#555`

**Responsive:**
- Desktop: 4 Columns
- Tablet: 2 Columns
- Mobile: 1 Column

---

### Radio Integration (NTS-Inspiration)

**Sticky Footer Player:**
```
┌─────────────────────────────────────────────────┐
│ FraWo Funk  |  ● LIVE  |  [▶] [Volume] [✕]    │
└─────────────────────────────────────────────────┘
```

**Position:** `position: fixed; bottom: 0; z-index: 9999`

**Specs:**
- Background: `#000`
- Border-top: `1px solid #1a1a1a`
- Text: `#888`, Accent: `#a855f7` (Live)
- Controls: Minimalistisch, outline-buttons
- Height: `64px` (Desktop), `auto` (Mobile)

**States:**
1. **Closed:** Komplett ausgeblendet
2. **Paused:** "Coming Soon" / Track-Info
3. **Playing:** "● LIVE" mit Puls-Animation

---

### Footer (kabaus-Struktur)
```
┌─────────────────────────────────────────────────┐
│  FraWo GbR                    Leistungen         │
│  Stockenweiler 7              Referenzen         │
│  88662 Überlingen             Radio              │
│                                                  │
│  [Mail] info@frawo-tech.de    Impressum         │
│  [Tel]  +49 7551 947 9870     Datenschutz       │
│                               AGB                │
└─────────────────────────────────────────────────┘
```

**Specs:**
- Background: `#000`
- Text: `#888`, Links: `#fff` (Hover: `#ff6b35`)
- Padding: `64px 0`
- Icons: SVG, `16x16`

---

## 🖋️ TYPOGRAFIE

### Font-Stack
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont,
                'Segoe UI', sans-serif;
--font-display: 'Inter', sans-serif;
```

### Hierarchy
```css
/* Headlines */
h1: 48px / 700 / -0.02em  /* Hero */
h2: 36px / 700 / -0.01em  /* Section Titles */
h3: 24px / 600 / 0        /* Card Titles */
h4: 18px / 600 / 0        /* Sub-Titles */

/* Body */
p:  16px / 400 / 1.6      /* Normal Text */
small: 14px / 400 / 1.5   /* Meta, Captions */
```

### Verwendung
- **kabaus-Touch:** Uppercase für Labels (`font-size: 12px; letter-spacing: 0.15em`)
- **NTS-Touch:** Monospaced für Timestamps/Status (optional)

---

## 🎭 UI-KOMPONENTEN

### Buttons

**Primary (Orange):**
```css
.btn-primary {
  background: #ff6b35;
  color: #fff;
  padding: 16px 32px;
  border: none;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #e55a2b;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}
```

**Secondary (Outline):**
```css
.btn-secondary {
  background: transparent;
  color: #1a1a1a;
  border: 1px solid #1a1a1a;
  padding: 16px 32px;
  /* ... rest wie primary */
}

.btn-secondary:hover {
  background: #1a1a1a;
  color: #fff;
}
```

---

### Cards (kabaus-Stil)

```css
.service-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  padding: 32px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.service-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-4px);
}

.service-card-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  color: #ff6b35;
}

.service-card-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1a1a1a;
}

.service-card-body {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
}

.service-card-link {
  display: inline-block;
  margin-top: 16px;
  font-size: 14px;
  color: #ff6b35;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
}
```

---

### Icons (kabaus Process-Flow)

**4-Schritte Visualisierung:**
```
Konzeption → Planung → Umsetzung → Support
   [💡]        [📋]       [⚙️]       [✓]
```

**Icon-Set (SVG):**
- Konsistente Strichstärke: `2px`
- Größe: `64x64` (Hero), `48x48` (Cards)
- Farbe: `#1a1a1a` (Standard), `#ff6b35` (Accent)
- Stil: Minimalistisch, Outline

---

## 📱 RESPONSIVE DESIGN

### Breakpoints
```css
/* Mobile First */
$mobile: 0-767px     /* 1 Column */
$tablet: 768-1023px  /* 2 Columns */
$desktop: 1024px+    /* 4 Columns */
```

### Grid-System (kabaus-ähnlich)
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
}

@media (max-width: 1023px) {
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 767px) {
  .grid-4 { grid-template-columns: 1fr; }
  .container { padding: 0 16px; }
}
```

---

## 🎬 ANIMATIONEN & INTERAKTIONEN

### Hover-Effekte (kabaus-subtil)
```css
/* Cards */
transition: transform 0.3s ease, box-shadow 0.3s ease;
transform: translateY(-4px);

/* Buttons */
transition: all 0.2s ease;
box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);

/* Links */
transition: color 0.2s ease;
```

### Scroll-Animationen
```css
/* Fade-in on scroll (optional) */
.fade-in-section {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.fade-in-section.is-visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Radio Player Pulse (NTS-Stil)
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.live-indicator {
  animation: pulse 2s infinite;
}
```

---

## 🖼️ BILDSPRACHE

### kabaus-Inspiration:
- **Kundenfotos:** Authentisch, Portraits
- **Prozess-Icons:** SVG, minimalistisch
- **Hero-Bilder:** Optional, mit Overlay

### NTS-Inspiration:
- **Show-Thumbnails:** Quadratisch (1:1), hochwertig
- **Artist-Photos:** Schwarz-Weiß oder Monochrom
- **Album-Art:** Als Grid-Element

### FraWo-Anwendung:
1. **Hero:** Optional Hintergrundbild (z.B. Serverraum) mit dunklem Overlay
2. **Services:** Icons statt Fotos (konsistenter)
3. **Referenzen:** Logos (schwarz-weiß, opacity: 0.6)
4. **Team:** Portraits (kreisförmig, 200x200)
5. **Radio:** Waveform-Visualisierung (optional)

---

## 📋 SEITENSTRUKTUR

### Homepage (kabaus-Layout)

```
┌─────────────────────────┐
│ Header (Sticky)         │
├─────────────────────────┤
│ Hero Section            │  ← Von Idee zur Lösung
│ - Headline              │
│ - Process Icons         │
│ - CTA Button            │
├─────────────────────────┤
│ Services Grid (4 Cards) │  ← Web, Infra, Radio, Auto
│ - Icon                  │
│ - Title                 │
│ - Description           │
│ - Link                  │
├─────────────────────────┤
│ Radio Highlight         │  ← Spezielles Feature
│ - Beschreibung          │
│ - Embedded Player       │
│ - funk.frawo-tech.de    │
├─────────────────────────┤
│ Testimonials (Carousel) │  ← kabaus-Stil
│ - Kundenzitat           │
│ - Portrait              │
│ - Navigation            │
├─────────────────────────┤
│ Contact CTA             │  ← Simple Section
│ - Headline              │
│ - Button                │
├─────────────────────────┤
│ Footer                  │
├─────────────────────────┤
│ Radio Player (Sticky)   │  ← NTS-Stil, fixed bottom
└─────────────────────────┘
```

---

## 🛠️ TECHNISCHE UMSETZUNG IN ODOO

### CSS-Custom-Properties
```css
:root {
  /* Colors */
  --frawo-black: #000000;
  --frawo-white: #FFFFFF;
  --frawo-gray-dark: #1a1a1a;
  --frawo-gray-mid: #555555;
  --frawo-gray-light: #888888;
  --frawo-purple: #a855f7;
  --frawo-orange: #ff6b35;

  /* Typography */
  --font-primary: 'Inter', sans-serif;

  /* Spacing */
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 32px;
  --spacing-lg: 64px;
  --spacing-xl: 128px;

  /* Borders */
  --border-color: #e0e0e0;
  --border-radius: 4px;

  /* Transitions */
  --transition-fast: 0.2s ease;
  --transition-medium: 0.3s ease;
  --transition-slow: 0.6s ease;
}
```

### Odoo Integration

**1. Theme erstellen:**
```xml
<!-- website_theme_frawo/views/templates.xml -->
<template id="custom_header" inherit_id="website.layout">
  <xpath expr="//header" position="replace">
    <header class="frawo-header">
      <!-- Header HTML -->
    </header>
  </xpath>
</template>
```

**2. Custom CSS einbinden:**
```xml
<!-- website_theme_frawo/__manifest__.py -->
'assets': {
  'web.assets_frontend': [
    'website_theme_frawo/static/src/css/frawo-theme.css',
    'website_theme_frawo/static/src/js/radio-player.js',
  ],
}
```

**3. Building Blocks:**
```python
# Odoo Website Builder Snippets
- frawo_hero (Hero Section)
- frawo_services_grid (4-Karten-Layout)
- frawo_radio_highlight (Radio Feature)
- frawo_testimonial_carousel (Kundenzitate)
- frawo_contact_cta (Contact Section)
```

---

## 🎯 IMPLEMENTIERUNGS-PRIORITÄT

### Phase 1: Foundation (1-2 Tage)
- ✅ Farbschema definieren (CSS Custom Props)
- ✅ Typografie einrichten (Inter Font)
- ✅ Header/Footer redesign (kabaus-Stil)
- ✅ Button-Styles (Primary/Secondary)

### Phase 2: Core Layout (2-3 Tage)
- 🔄 Hero Section mit Process-Icons
- 🔄 Services Grid (4 Cards)
- 🔄 Responsive Grid-System
- 🔄 Card-Hover-Effekte

### Phase 3: Radio Integration (1 Tag)
- 🔄 Sticky Footer Player (NTS-Stil)
- 🔄 Live-Status mit Puls-Animation
- 🔄 Volume-Control
- 🔄 Mobile-optimiert

### Phase 4: Content & Polish (1-2 Tage)
- 🔄 Testimonial Carousel
- 🔄 Radio Highlight Section
- 🔄 Icons (SVG Set)
- 🔄 Animationen & Transitions
- 🔄 Cross-Browser Testing

---

## 📊 VERGLEICH: Vorher → Nachher

| Aspekt | Aktuell | Neu (kabaus + NTS) |
|--------|---------|---------------------|
| **Stil** | Generic Bootstrap | Minimalistisch, Custom |
| **Farben** | Bunt, Bootstrap | Monochrom + Orange/Purple |
| **Layout** | Standard-Grid | kabaus 4-Karten-Konzept |
| **Radio** | Nicht vorhanden | NTS Sticky Footer Player |
| **Typography** | System-Fonts | Inter, Hierarchie |
| **Whitespace** | Mittel | Großzügig (kabaus) |
| **Animationen** | Basic | Subtile Hover-Effekte |
| **Mobile** | Responsive | Optimiert, Touch-friendly |

---

## 🎨 DESIGN-MOCKUP (Text-Repräsentation)

```
╔═══════════════════════════════════════════════════════╗
║  [Logo]   Leistungen  Referenzen  Radio  Blog  Kontakt ║  ← Header
╠═══════════════════════════════════════════════════════╣
║                                                          ║
║           Von der Idee zur IT-Lösung                    ║  ← Hero
║                                                          ║
║       [💡] → [📋] → [⚙️] → [✓]                         ║
║                                                          ║
║              [Projekt starten]                           ║
║                                                          ║
╠═══════════════════════════════════════════════════════╣
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ║
║  │   [🌐]    │ │   [💻]    │ │   [📡]    │ │   [🤖]    │ ║  ← Services
║  │ Web Dev   │ │ Infrastr. │ │ Radio     │ │ Automat.  │ ║
║  │          │ │          │ │          │ │          │ ║
║  │ [→]       │ │ [→]       │ │ [→]       │ │ [→]       │ ║
║  └──────────┘ └──────────┘ └──────────┘ └──────────┘ ║
╠═══════════════════════════════════════════════════════╣
║       🎵 FraWo Funk - Dein IT-Radio-Stream             ║  ← Radio Promo
║                                                          ║
║       [Embedded Player Vorschau]                         ║
║                                                          ║
║       → funk.frawo-tech.de                              ║
╠═══════════════════════════════════════════════════════╣
║  FraWo GbR          │  Leistungen  │  [Mail]           ║  ← Footer
║  Stockenweiler 7    │  Referenzen  │  [Tel]            ║
║  88662 Überlingen   │  Impressum   │  [GitHub]         ║
╠═══════════════════════════════════════════════════════╣
║ FraWo Funk  |  ● LIVE  |  [▶] [━━━━] [✕]              ║  ← Sticky Player
╚═══════════════════════════════════════════════════════╝
```

---

## ✅ ERFOLGS-KRITERIEN

**Design ist "fertig" wenn:**
- ✅ kabaus-Ästhetik erkennbar (Whitespace, Struktur, Icons)
- ✅ NTS Radio-Touch integriert (Sticky Player, Minimalism)
- ✅ Mobile-optimiert (Touch-friendly, responsive)
- ✅ Schnelle Ladezeiten (<2s)
- ✅ Accessibility (WCAG AA)
- ✅ Cross-Browser kompatibel (Chrome, Firefox, Safari)

---

**Nächste Schritte:** Siehe [Umsetzungsplan](#) (folgt)

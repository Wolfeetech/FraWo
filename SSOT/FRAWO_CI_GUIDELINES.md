# FraWo GbR - Corporate Identity Guidelines

**Version:** 2.0 (Updated 2026-05-13)
**Basierend auf:** Logo + frawo_custom_css.css v3.5
**Stil:** Ultra Minimal (NTS-Inspired)

---

## 🎨 FARBEN (OFFIZIELLE CI)

### Logo-Farben

**Primär: Dunkelgrün (Forest)**
```
FraWo Logo Text: #0d4d4d (Dunkelgrün/Petrol)
Verwendung: Logo, Hauptmarke
```

**Sekundär: Purple (UV)**
```
"Smart Media & Event": #a855f7 (Leuchtend Purple/UV)
Verwendung: Tagline, Akzente, Radio Live-Status
```

### Website-Farbschema (v3.5 - NTS-Inspired)

**Background & Surfaces:**
```css
--fw-bg: #0a0a0a;          /* Haupt-Background (fast schwarz) */
--fw-surface: #0a0a0a;     /* Alternativ identisch */
--fw-border: #1a1a1a;      /* Subtle borders, dividers */
```

**Text-Hierarchie:**
```css
--fw-text: #e0e0e0;        /* Primary text (hell-grau) */
--fw-text-dim: #888888;    /* Secondary text (mittel-grau) */
--fw-text-dimmer: #555555; /* Tertiary text (dunkel-grau) */
```

**Akzente:**
```css
--fw-uv: #a855f7;          /* Purple/UV - Aus Logo! */
--fw-forest: #0d4d4d;      /* Dunkelgrün - Logo-Grün */
```

**Buttons:**
```css
Primary Button Background: #e0e0e0 (hell-grau)
Primary Button Text: #0a0a0a (schwarz)
Ghost Button Border: #1a1a1a (dunkel-grau)
Ghost Button Text: #888888 (mittel-grau)
```

---

## 🖼️ LOGO

### Varianten

**Standard (Farbe):**
- FraWo: Dunkelgrün (#0d4d4d)
- Smart Media & Event: Purple (#a855f7)
- W.Prinz & F.Bienert GbR: Schwarz (#000)
- Background: Hell (Weiß/Beige)

**Dark Mode (Website):**
- FraWo: Kann hell werden (#e0e0e0) auf dunklem BG
- Smart Media & Event: Purple (#a855f7) bleibt
- Oder: Komplettes Logo in weiß mit opacity

**Minimal (NTS-Stil):**
- Nur "FraWo" Text, ultra-klein (18px height)
- Opacity: 0.7 (normal), 1.0 (hover)
- mix-blend-mode: screen

### Logo-Platzierung
- **Header:** Zentral, klein, subtle (18px height)
- **Footer:** Mittel-groß, linksbündig
- **Print:** Standard-Größe mit Tagline

### Abstände
- Minimum Clear Space: 1× Logo-Höhe rundum
- Keine anderen Elemente im Clear Space

---

## 📐 TYPOGRAFIE

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**Verwendung:**
- **Inter:** Alle Website-Texte
- **Gewichte:** 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold)

### Hierarchie

**Headlines:**
```css
H1: font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    color: #e0e0e0;

H2: font-size: clamp(1.75rem, 3.5vw, 2.5rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.2;
    color: #e0e0e0;

H3: font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #e0e0e0;
```

**Body Text:**
```css
Lead/Intro: font-size: 1.05rem;
            line-height: 1.7;
            color: #888888;

Normal:     font-size: 1rem;
            line-height: 1.6;
            color: #888888;

Small:      font-size: 0.9rem;
            line-height: 1.7;
            color: #888888;
```

**Labels/Meta:**
```css
Eyebrow:    font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: #555555;

Nav Links:  font-size: 0.85rem;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #888888;
```

---

## 🎭 UI-KOMPONENTEN

### Buttons

**Primary (Light on Dark):**
```css
background: #e0e0e0;
color: #0a0a0a;
border: none;
border-radius: 0;  /* Sharp corners! */
padding: 14px 28px;
font-weight: 500;
font-size: 0.8rem;
text-transform: uppercase;
letter-spacing: 0.1em;
transition: opacity 0.2s ease;

:hover {
  opacity: 0.9;
}
```

**Ghost (Outline):**
```css
background: transparent;
color: #888888;
border: 1px solid #1a1a1a;
border-radius: 0;
padding: 14px 28px;
font-weight: 500;
font-size: 0.8rem;
text-transform: uppercase;
letter-spacing: 0.1em;
transition: all 0.2s ease;

:hover {
  border-color: #e0e0e0;
  color: #e0e0e0;
}
```

**Link (Minimal):**
```css
color: #888888;
font-size: 0.8rem;
text-transform: uppercase;
letter-spacing: 0.1em;
transition: color 0.2s ease;

:hover {
  color: #e0e0e0;
}
```

### Cards/Boxes

**Minimal Box:**
```css
background: #0a0a0a;
border: 1px solid #1a1a1a;
padding: 2.5rem;
/* NO border-radius, NO shadow */
```

**Grid Item:**
```css
/* Grid with 1px gaps */
display: grid;
gap: 1px;
background: #1a1a1a;  /* Gap color */

.item {
  background: #0a0a0a;
  padding: 2.5rem;
}
```

### Borders & Dividers

**Section Dividers:**
```css
border-top: 1px solid #1a1a1a;
border-bottom: 1px solid #1a1a1a;
```

**Subtle Lines:**
```css
border: 1px solid #1a1a1a;
```

**NO:**
- Keine Box-Shadows (außer für Overlays wie Modals)
- Keine Border-Radius
- Keine Gradients

---

## 🖼️ BILDSPRACHE

### Stil
- **Authentisch:** Echte Fotos, keine Stock-Images
- **Monochrom:** Bevorzugt schwarz-weiß oder Duotone
- **Kontrast:** Starke Hell/Dunkel-Kontraste
- **Farbakzente:** Optional mit Purple (#a855f7) Overlay

### Treatment
```css
/* Bild-Container */
border: 1px solid #1a1a1a;
overflow: hidden;
background: #0a0a0a;

/* Bild */
width: 100%;
height: auto;
display: block;
/* Optional: filter: grayscale(100%); */
```

### Einsatzbereiche
- **Hero:** Großformatig, mit Text-Overlay
- **Referenzen:** Kunde-Logos (grayscale, opacity: 0.6)
- **Equipment:** Produkt-Fotos mit klarem BG
- **Team:** Portraits (optional kreisrund, aber bevorzugt rechteckig)

---

## 📏 SPACING & LAYOUT

### Container
```css
max-width: 1200px;
margin: 0 auto;
padding: 0 2rem;

@media (max-width: 768px) {
  padding: 0 1rem;
}
```

### Section Padding
```css
Standard:  padding: 80px 0;
Tight:     padding: 50px 0;
Hero:      padding: 100px 0 80px;

@media (max-width: 768px) {
  Standard: padding: 50px 0;
  Hero: padding: 60px 0;
}
```

### Grid Gaps
```css
Large:  gap: 4rem;
Medium: gap: 2rem;
Small:  gap: 1rem;
Pixel:  gap: 1px;  /* Für Grid-Borders */
```

### Spacing Scale
```
xs:  8px
sm:  16px
md:  32px
lg:  64px
xl:  128px
```

---

## 🎬 ANIMATIONEN & TRANSITIONS

### Standard Transitions
```css
Fast:   0.15s ease
Medium: 0.2s ease
Slow:   0.3s ease
```

### Hover-Effekte
```css
/* Opacity Change (Buttons, Images) */
transition: opacity 0.2s ease;
:hover { opacity: 0.9; }

/* Color Change (Links, Text) */
transition: color 0.15s ease;
:hover { color: #e0e0e0; }

/* Border Change (Ghost Buttons) */
transition: all 0.2s ease;
:hover { border-color: #e0e0e0; }
```

### NO Animations
- Keine Slide-Ins
- Keine Fade-Ins (außer Page-Load)
- Keine Bounce-Effekte
- Keine Parallax
- **Ausnahme:** Radio Visualizer (Bars Bounce)

---

## 📱 RESPONSIVE BREAKPOINTS

```css
Mobile:     0 - 767px
Tablet:     768px - 1023px
Desktop:    1024px+
Large:      1440px+
```

### Mobile-First Approach
```css
/* Base styles = Mobile */
.element { ... }

/* Tablet up */
@media (min-width: 768px) { ... }

/* Desktop up */
@media (min-width: 1024px) { ... }
```

---

## 🎵 RADIO PLAYER (Special Component)

### Colors
```css
Background: rgba(10, 10, 10, 0.9) + backdrop-filter: blur(10px);
Border: 1px solid #1a1a1a (top only);
Text: #888888;
Accent: #a855f7 (Live-Status, Visualizer);
```

### Visualizer Animation
```css
.fw-radio-bar {
  width: 3px;
  background: #a855f7;
  animation: fw-bounce 0.8s ease-in-out infinite;
}

@keyframes fw-bounce {
  0%, 100% { height: 5px; }
  50% { height: 15px; }
}
```

### Position
```css
position: fixed;
bottom: 0;
left: 0;
right: 0;
z-index: 9999;
```

---

## ✅ DO's & DON'Ts

### ✅ DO:
- Großzügiger Whitespace
- Klare Hierarchie (Text-Größen)
- Minimalistische Ästhetik
- Sharp corners (border-radius: 0)
- Subtle borders (#1a1a1a)
- Uppercase für Labels/Nav
- Inter Font durchgängig
- Purple (#a855f7) für Akzente
- Dunkelgrün (#0d4d4d) für Branding-Momente

### ❌ DON'T:
- Bunte Farben außer Purple & Green
- Box-Shadows (außer Overlays)
- Border-Radius
- Gradients
- Animierte Buttons/CTAs
- Zu viele Schriftgrößen
- Stock-Photos
- Bootstrap-Standard-Optik

---

## 🎯 BRAND VOICE & TONE

### Attribute
- **Professionell** aber nicht steif
- **Technisch** aber nicht nerdig
- **Lokal** und greifbar
- **Pragmatisch** statt fancy
- **Ehrlich** und transparent

### Sprache
- **Du** (Website, Social Media)
- **Sie** (B2B-Angebote, Rechnungen)
- Kurze Sätze
- Aktive Formulierung
- Tech-Begriffe OK, aber erklärt

### Beispiele
✅ "Beste Lösung. Nicht teuerste."
✅ "Vom Bodensee. Für Events."
✅ "IHK-geprüft. Lokal verfügbar."

❌ "Wir sind Ihr Partner für..."
❌ "Innovative Lösungen im Bereich..."
❌ "Ganzheitliche Dienstleistungen..."

---

## 📋 CHECKLISTE: CI-KONFORM?

**Farben:**
- [ ] Background: #0a0a0a
- [ ] Text: #e0e0e0, #888888, #555555
- [ ] Borders: #1a1a1a
- [ ] Akzente: #a855f7 (Purple), #0d4d4d (Green)
- [ ] KEINE anderen Farben verwendet

**Typografie:**
- [ ] Inter Font
- [ ] Hierarchie klar (H1 > H2 > Body)
- [ ] Uppercase für Labels/Nav
- [ ] Letter-spacing bei Uppercase (0.1em - 0.15em)

**Layout:**
- [ ] Container max-width: 1200px
- [ ] Großzügiger Whitespace (padding: 80px 0)
- [ ] Klare Sections mit 1px borders

**Komponenten:**
- [ ] Buttons ohne border-radius
- [ ] Primary Button: Hell auf Dunkel
- [ ] Ghost Button: Outline, subtle
- [ ] Keine Shadows (außer Overlays)

**Bildsprache:**
- [ ] Authentische Fotos (keine Stock-Images)
- [ ] Bevorzugt Monochrom/Duotone
- [ ] Border: 1px solid #1a1a1a

**Animationen:**
- [ ] Nur subtle Transitions (0.15s - 0.3s)
- [ ] Hover: opacity/color change
- [ ] KEINE Slide-Ins/Bounce

---

## 📦 ASSETS

### Logo-Dateien
```
lifeboat/assets/logo.png         - Standard (Farbe)
lifeboat/assets/logo-white.png   - Weiß (für dunkle BGs) - TBD
lifeboat/assets/logo-minimal.svg - Nur "FraWo" Text - TBD
```

### Fonts
```
Google Fonts: Inter (400, 500, 600, 700)
URL: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap
```

### CSS
```
frawo_custom_css.css v3.5 - Vollständiges Design-System
```

---

**Version:** 2.0
**Letzte Änderung:** 2026-05-13
**Maintainer:** FraWo GbR (Wolf & Franz)

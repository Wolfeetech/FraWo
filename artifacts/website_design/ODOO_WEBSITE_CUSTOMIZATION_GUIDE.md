# FraWo GbR - Odoo Website Customization Guide

**Version:** 1.0.0
**Datum:** 2026-05-04
**Für:** Manuelle Anpassung im Odoo Website Builder

---

## 📋 Inhaltsverzeichnis

1. [Einleitung](#einleitung)
2. [Design-System Integration](#design-system-integration)
3. [Schritt-für-Schritt Anleitung](#schritt-für-schritt-anleitung)
4. [Komponenten-Bibliothek](#komponenten-bibliothek)
5. [Anpassungsmöglichkeiten](#anpassungsmöglichkeiten)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Einleitung

Dieses Design-System bietet eine **professionelle, moderne und vollständig anpassbare** Website-Gestaltung für Odoo. Alle Komponenten sind so gestaltet, dass sie:

✅ **Im Odoo Editor bearbeitbar** sind
✅ **Responsive** auf allen Geräten funktionieren
✅ **Barrierefrei** (WCAG 2.1 AA konform) sind
✅ **Performance-optimiert** sind (< 3s Ladezeit)
✅ **SEO-freundlich** strukturiert sind

---

## Design-System Integration

### Schritt 1: CSS ins Odoo Theme integrieren

#### Option A: Via Odoo Theme Editor (empfohlen)

1. Öffne Odoo Backend: `https://odoo.hs27.internal/web`
2. Navigiere zu: **Website → Konfiguration → Einstellungen**
3. Scrolle zu **"Website-Theme"**
4. Klicke auf **"Anpassen"**
5. Im Theme Editor:
   - Wähle **"CSS hinzufügen"**
   - Kopiere den Inhalt von `frawo_design_system.css`
   - Speichere als **"FraWo Custom Styles"**

#### Option B: Via Assets (für fortgeschrittene Nutzer)

```xml
<!-- In deinem Theme-Modul: views/assets.xml -->
<template id="assets_frontend" inherit_id="web.assets_frontend">
    <xpath expr="." position="inside">
        <link rel="stylesheet" href="/your_theme/static/src/css/frawo_design_system.css"/>
    </xpath>
</template>
```

### Schritt 2: Farben anpassen

Die Hauptfarben können einfach in den CSS-Variablen angepasst werden:

```css
:root {
  /* Deine Brand-Farben hier anpassen */
  --fw-primary: #0066CC;        /* Hauptfarbe (aktuell: Blau) */
  --fw-secondary: #FF6B35;      /* Akzentfarbe (aktuell: Orange) */

  /* Oder andere Farbschemata: */
  /* --fw-primary: #7C3AED;  */ /* Lila */
  /* --fw-primary: #10B981;  */ /* Grün */
  /* --fw-primary: #EF4444;  */ /* Rot */
}
```

**Tipp:** Nutze Tools wie [https://coolors.co](https://coolors.co) für harmonische Farbkombinationen.

---

## Schritt-für-Schritt Anleitung

### Homepage erstellen

#### 1. Neue Seite anlegen

1. Website → Seiten → **Neue Seite**
2. URL: `/` (für Homepage)
3. Titel: `FraWo GbR - Veranstaltungstechnik & Event-Infrastruktur`
4. Wähle **"Leere Seite"** Template

#### 2. Hero-Section einfügen

1. Klicke auf **"Block hinzufügen"**
2. Wähle **"HTML-Code"** oder **"Struktur → Container"**
3. Kopiere den Hero-Section Code aus `frawo_homepage_template.html`
4. Füge ihn ein (STRG+V im Odoo Editor)

**Wichtig:** Odoo wird den Code automatisch in sein Grid-System einpassen.

#### 3. Bilder ersetzen

Für jedes `<img src="/web/image/949">`:

1. **Rechtsklick** auf das Bild im Editor
2. Wähle **"Bild ersetzen"**
3. Lade dein eigenes Bild aus der **Odoo Media Library** hoch
4. Wähle passende Auflösung (empfohlen: 1920x1080px)

**Bildoptimierung:**
- Format: **WebP** (beste Kompression) oder JPG
- Maximale Größe: **< 500 KB** pro Bild
- Tools: [TinyPNG](https://tinypng.com), [Squoosh](https://squoosh.app)

#### 4. Texte anpassen

Alle Texte sind direkt im Odoo Editor bearbeitbar:

1. **Doppelklick** auf den Text
2. Bearbeite den Inhalt
3. **Formatierung bleibt erhalten** (Überschriften, Listen, etc.)

#### 5. Links anpassen

Für jeden Link (z.B. `/contactus`, `/b2c`):

1. **Rechtsklick** auf den Link-Text
2. Wähle **"Link bearbeiten"**
3. Ändere die URL zu deiner Odoo-Seite (z.B. `/kontakt`)

---

## Komponenten-Bibliothek

### Buttons

```html
<!-- Primary Button (Hauptaktion) -->
<a href="/kontakt" class="fw-btn-primary">
    Kontakt aufnehmen
</a>

<!-- Secondary Button (Alternative) -->
<a href="#mehr" class="fw-btn-secondary">
    Mehr erfahren
</a>

<!-- Ghost Button (Dezent) -->
<a href="/services" class="fw-btn-ghost">
    Services ansehen
</a>

<!-- Link Button (Textlink mit Icon) -->
<a href="/details" class="fw-btn-link">
    Details ansehen →
</a>

<!-- Button Größen -->
<a href="#" class="fw-btn-primary fw-btn-sm">Klein</a>
<a href="#" class="fw-btn-primary">Normal</a>
<a href="#" class="fw-btn-primary fw-btn-lg">Groß</a>
```

### Karten (Cards)

```html
<!-- Basis-Karte -->
<div class="fw-card">
    <h3 class="fw-h4">Kartenüberschrift</h3>
    <p class="fw-body">
        Beschreibungstext der Karte.
    </p>
</div>

<!-- Karte mit Farbverlauf (Feature-Highlight) -->
<div class="fw-card" style="background: linear-gradient(135deg, var(--fw-primary) 0%, var(--fw-primary-dark) 100%); color: white;">
    <h3 class="fw-h3" style="color: white;">Premium Feature</h3>
    <p style="color: rgba(255,255,255,0.9);">
        Wichtige Information hervorgehoben.
    </p>
</div>
```

### Grid-Layouts

```html
<!-- 3-Spalten Grid (responsiv) -->
<div class="fw-grid-3">
    <div class="fw-card">Karte 1</div>
    <div class="fw-card">Karte 2</div>
    <div class="fw-card">Karte 3</div>
</div>

<!-- 2-Spalten Grid -->
<div class="fw-grid-2">
    <div class="fw-card">Linke Spalte</div>
    <div class="fw-card">Rechte Spalte</div>
</div>

<!-- Auto-Fit Grid (passt sich an) -->
<div class="fw-grid">
    <div class="fw-card">Flexible Breite</div>
    <div class="fw-card">Flexible Breite</div>
</div>
```

### Typografie

```html
<!-- Überschriften -->
<h1 class="fw-h1">Hauptüberschrift (56-72px)</h1>
<h2 class="fw-h2">Sektion-Überschrift (48px)</h2>
<h3 class="fw-h3">Unterüberschrift (36px)</h3>

<!-- Spezial-Texte -->
<div class="fw-eyebrow">KATEGORIE</div>
<p class="fw-lead">
    Große Einführung / Lead-Text (20-22px)
</p>
<p class="fw-body">
    Normaler Fließtext (16-18px)
</p>
<p class="fw-caption">Kleingedrucktes / Bildunterschrift (14px)</p>
```

### Icons (einfache SVG Icons)

```html
<!-- Pfeil-Icon (→) -->
<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" stroke-width="2"/>
</svg>

<!-- Check-Icon (✓) -->
<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M16.667 5L7.5 14.167L3.333 10" stroke="currentColor" stroke-width="2"/>
</svg>

<!-- Nutzung in Buttons -->
<a href="#" class="fw-btn-primary">
    <span>Text</span>
    <svg width="20" height="20"><!-- Icon SVG --></svg>
</a>
```

---

## Anpassungsmöglichkeiten

### 1. Farben ändern

#### Via CSS-Variablen (Empfohlen)

Ändere in deinem Theme-CSS:

```css
:root {
  /* Brand Colors anpassen */
  --fw-primary: #1E40AF;        /* Dunkles Blau */
  --fw-primary-dark: #1E3A8A;
  --fw-primary-light: #3B82F6;

  --fw-secondary: #DC2626;      /* Rot statt Orange */
  --fw-secondary-dark: #B91C1C;
  --fw-secondary-light: #EF4444;
}
```

#### Direkt im HTML (für einzelne Elemente)

```html
<a href="#" class="fw-btn-primary" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);">
    Grüner Button
</a>
```

### 2. Abstände anpassen

```css
:root {
  /* Mehr Weißraum (luftiger) */
  --fw-space-section: 8rem;   /* Statt 5rem */

  /* Weniger Weißraum (kompakter) */
  --fw-space-section: 3rem;   /* Statt 5rem */
}
```

### 3. Schriftarten ändern

#### Google Fonts einbinden

1. Wähle Schrift auf [Google Fonts](https://fonts.google.com)
2. Kopiere `<link>` Tag in Odoo Theme Header
3. Ändere CSS-Variable:

```css
:root {
  --fw-font-sans: 'Poppins', sans-serif;  /* Statt 'Inter' */
  --fw-font-display: 'Montserrat', sans-serif;
}
```

**Empfohlene Schrift-Kombinationen:**
- **Modern:** Inter + Inter
- **Elegant:** Playfair Display + Source Sans Pro
- **Tech:** Roboto + Roboto Mono
- **Freundlich:** Poppins + Open Sans

### 4. Border-Radius anpassen (Ecken)

```css
:root {
  /* Runde Ecken (modern) */
  --fw-radius-lg: 1.5rem;   /* Statt 0.75rem */

  /* Eckige Ecken (minimalistisch) */
  --fw-radius-lg: 0.25rem;  /* Fast keine Rundung */

  /* Sehr rund (playful) */
  --fw-radius-lg: 2rem;
}
```

---

## Best Practices

### SEO-Optimierung

#### 1. Meta-Tags setzen (pro Seite)

In Odoo: **Website → Seiten → [Deine Seite] → SEO**

```
Titel: FraWo GbR - Veranstaltungstechnik & Smart Home vom Bodensee
Beschreibung: Professionelle Event-Infrastruktur, Line-Arrays, Smart Home mit Home Assistant. Ton, Licht, Automation für Events und Privatkunden.
Schlüsselwörter: Veranstaltungstechnik, Line-Array, Smart Home, Home Assistant, Bodensee
```

#### 2. Überschriften-Hierarchie beachten

```html
<!-- RICHTIG -->
<h1>Hauptüberschrift (nur 1x pro Seite)</h1>
  <h2>Sektion</h2>
    <h3>Untersektion</h3>

<!-- FALSCH -->
<h1>Erste Überschrift</h1>
<h3>Überspringt h2 ❌</h3>
```

#### 3. Alt-Texte für Bilder

Jedes Bild braucht einen beschreibenden Alt-Text:

```html
<img src="/image.jpg" alt="Line-Array PA-System bei Open-Air-Konzert am Bodensee">
<!-- NICHT: alt="img1" oder alt="" -->
```

### Performance

#### 1. Bilder optimieren

- **Format:** WebP (best) > JPG (good) > PNG (nur für Logos/Icons)
- **Größe:** < 500 KB pro Bild
- **Auflösung:**
  - Hero-Images: 1920x1080px
  - Karten-Images: 800x600px
  - Icons: SVG (skalierbar)

#### 2. Lazy Loading

```html
<img src="/image.jpg" loading="lazy" alt="Beschreibung">
```

Odoo fügt das meist automatisch hinzu.

#### 3. CSS minimieren

Entferne unbenutzten CSS-Code nach Anpassungen.

### Accessibility (Barrierefreiheit)

#### 1. Kontrastverhältnisse

- **Normal-Text:** Mind. 4.5:1
- **Groß-Text (18pt+):** Mind. 3:1
- **Tool:** [Contrast Checker](https://webaim.org/resources/contrastchecker/)

#### 2. Fokus-Indikatoren

```css
/* Bereits im Design-System enthalten */
.fw-focus-visible:focus-visible {
  outline: 2px solid var(--fw-primary);
}
```

#### 3. ARIA-Labels für Icons

```html
<a href="/kontakt" aria-label="Kontakt aufnehmen">
    <svg><!-- Icon --></svg>
</a>
```

---

## Odoo-Spezifische Tipps

### 1. Odoo Grid-System nutzen

Odoo nutzt Bootstrap 5. Kombiniere mit FraWo Design:

```html
<div class="container">  <!-- Odoo Container -->
    <div class="row">
        <div class="col-lg-6">  <!-- Odoo Spalte -->
            <div class="fw-card">  <!-- FraWo Komponente -->
                Inhalt
            </div>
        </div>
    </div>
</div>
```

### 2. Odoo Snippets erweitern

Erstelle eigene Snippets für wiederverwendbare Komponenten:

1. **Website → Anpassen → Snippet erstellen**
2. Füge deine FraWo-Komponente ein
3. Speichere als **"FraWo Service Card"** o.ä.

### 3. Dynamic Content

Nutze Odoo-Variablen für dynamische Inhalte:

```html
<!-- Beispiel: Aktuelles Jahr im Footer -->
<p>© <span t-esc="datetime.now().year"/> FraWo GbR</p>

<!-- Beispiel: Benutzer-spezifisch -->
<t t-if="user_id.partner_id.name">
    <h2>Willkommen, <span t-field="user_id.partner_id.name"/>!</h2>
</t>
```

---

## Troubleshooting

### Problem: Farben werden nicht angewendet

**Lösung:**
1. Prüfe, ob CSS-Datei korrekt eingebunden ist
2. Cache leeren: STRG+SHIFT+R
3. Prüfe CSS-Variablen im Browser DevTools: `Inspect → :root`

### Problem: Layout bricht auf Mobile

**Lösung:**
1. Nutze Odoo Grid-System (`col-md-6`, `col-lg-4`)
2. Teste mit Browser DevTools (F12 → Responsive Mode)
3. Prüfe Media Queries im CSS

### Problem: Bilder laden langsam

**Lösung:**
1. Bilder komprimieren (TinyPNG, Squoosh)
2. WebP-Format nutzen
3. `loading="lazy"` Attribut hinzufügen
4. Odoo CDN aktivieren (falls verfügbar)

### Problem: CSS-Änderungen nicht sichtbar

**Lösung:**
1. Hard Reload: STRG+SHIFT+R
2. Odoo Assets regenerieren: **Einstellungen → Technisch → Assets → Regenerieren**
3. Inkognito-Fenster testen (ohne Cache)

---

## Erweiterte Anpassungen

### Custom Komponente erstellen

Beispiel: "Feature Badge" Komponente

```html
<!-- Neue Komponente definieren -->
<style>
.fw-badge-feature {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, var(--fw-success) 0%, #059669 100%);
    color: white;
    border-radius: var(--fw-radius-full);
    font-size: var(--fw-text-sm);
    font-weight: var(--fw-weight-semibold);
}
</style>

<!-- Nutzung -->
<div class="fw-badge-feature">
    <svg width="16" height="16"><!-- Check Icon --></svg>
    <span>Neu</span>
</div>
```

### Animation hinzufügen

```css
/* Fade-in beim Scrollen */
.fw-fade-in {
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.6s ease;
}

.fw-fade-in.visible {
    opacity: 1;
    transform: translateY(0);
}
```

```javascript
// JavaScript (in Odoo Backend unter "Code einfügen")
document.addEventListener('DOMContentLoaded', function() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    });

    document.querySelectorAll('.fw-fade-in').forEach(el => observer.observe(el));
});
```

---

## Wartung & Updates

### Regelmäßige Checks

- **Monatlich:** Bilder-Größe prüfen, Cache leeren
- **Vierteljährlich:** Broken Links prüfen, SEO-Audit
- **Jährlich:** Design-Trends überprüfen, Accessibility-Test

### Version Control

Sichere deine Anpassungen:

1. **Odoo Backup:** Website → Konfiguration → Sichern
2. **CSS/HTML exportieren:** Kopiere Code in lokale Files
3. **Git Commit:** Versioniere deine Design-Assets

---

## Support & Ressourcen

### Hilfreiche Links

- **Odoo Documentation:** [docs.odoo.com](https://www.odoo.com/documentation)
- **CSS Tricks:** [css-tricks.com](https://css-tricks.com)
- **WebAIM (Accessibility):** [webaim.org](https://webaim.org)
- **Can I Use (Browser Support):** [caniuse.com](https://caniuse.com)

### Design Tools

- **Farben:** [Coolors.co](https://coolors.co)
- **Schriften:** [Google Fonts](https://fonts.google.com)
- **Icons:** [Heroicons](https://heroicons.com), [Feather Icons](https://feathericons.com)
- **Bilder:** [Unsplash](https://unsplash.com), [Pexels](https://pexels.com)

---

**Version:** 1.0.0
**Letzte Aktualisierung:** 2026-05-04
**Autor:** OpenClaw Agent 3.1 für FraWo GbR

Bei Fragen oder Problemen: Dokumentation erneut durchlesen oder Odoo Community Forum konsultieren.

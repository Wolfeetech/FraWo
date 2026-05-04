# FraWo Website Design - Quick Reference

**Schnellzugriff für häufige Aufgaben**

---

## 🚀 Schnellstart (5 Minuten)

1. **CSS einbinden:**
   - Öffne `frawo_design_system.css`
   - Kopiere ALLES (STRG+A, STRG+C)
   - Odoo: Website → Einstellungen → Theme → CSS hinzufügen
   - Einfügen & Speichern

2. **Farben anpassen:**
   - Suche in CSS nach `:root {`
   - Ändere `--fw-primary` und `--fw-secondary`
   - Speichern → Fertig!

3. **Erste Sektion einfügen:**
   - Öffne `frawo_homepage_template.html`
   - Kopiere eine `<section>` (z.B. Hero)
   - Odoo Editor: Block hinzufügen → HTML-Code
   - Einfügen → Bilder & Texte anpassen

---

## 📻 Radio Player (NEU!)

### Quick Installation

1. **Kopiere Code:** Öffne `frawo_radio_player_sticky.html` und kopiere alles
2. **In Odoo:** Website → Theme → Footer → HTML bearbeiten → Code einfügen
3. **Stream-URLs anpassen:** Suche nach `data-stream="..."` und ersetze mit deinen URLs
4. **Fertig!** Player erscheint sticky am unteren Bildschirmrand

**Features:**
- ✅ Sticky Bottom Player (immer sichtbar)
- ✅ Multi-Station Support
- ✅ Now Playing Info (AzuraCast API)
- ✅ Volume Control
- ✅ Mobile-optimiert
- ✅ Collapsible (minimieren/maximieren)

**Details:** Siehe `RADIO_PLAYER_GUIDE.md`

---

## 🎨 Farben ändern (Copy & Paste)

```css
/* In Odoo Theme-CSS einfügen: */

/* BLAU (Standard) */
:root {
  --fw-primary: #0066CC;
  --fw-secondary: #FF6B35;
}

/* GRÜN */
:root {
  --fw-primary: #10B981;
  --fw-secondary: #F59E0B;
}

/* LILA */
:root {
  --fw-primary: #7C3AED;
  --fw-secondary: #EC4899;
}

/* ROT */
:root {
  --fw-primary: #DC2626;
  --fw-secondary: #F97316;
}
```

---

## 📝 Komponenten Copy & Paste

### Button (Primary)
```html
<a href="/kontakt" class="fw-btn-primary">
    Kontakt aufnehmen
</a>
```

### Button (Ghost)
```html
<a href="/services" class="fw-btn-ghost">
    Mehr erfahren
</a>
```

### Service-Karte
```html
<div class="fw-card">
    <h3 class="fw-h4">Service-Titel</h3>
    <p class="fw-body">
        Beschreibung des Services.
    </p>
    <a href="/details" class="fw-btn-link">Details →</a>
</div>
```

### 3-Spalten Grid
```html
<div class="fw-grid-3">
    <div class="fw-card">Karte 1</div>
    <div class="fw-card">Karte 2</div>
    <div class="fw-card">Karte 3</div>
</div>
```

### Hero-Section (minimal)
```html
<section class="fw-hero">
    <div class="container">
        <div class="fw-eyebrow">FraWo GbR</div>
        <h1 class="fw-h1">Deine Überschrift</h1>
        <p class="fw-lead">Dein Einleitungstext.</p>
        <a href="/kontakt" class="fw-btn-primary">Call-to-Action</a>
    </div>
</section>
```

---

## 🖼️ Bilder optimieren

### Empfohlene Größen

| Verwendung | Auflösung | Format | Max. Größe |
|------------|-----------|--------|-----------|
| Hero-Image | 1920x1080 | WebP/JPG | 500 KB |
| Karten-Image | 800x600 | WebP/JPG | 300 KB |
| Logo | 400x400 | PNG/SVG | 50 KB |
| Icon | - | SVG | 5 KB |

### Tools

- **Komprimierung:** [TinyPNG.com](https://tinypng.com)
- **Format-Konvertierung:** [Squoosh.app](https://squoosh.app)
- **SVG-Optimierung:** [SVGOMG.net](https://jakearchibald.github.io/svgomg/)

---

## 📱 Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 768px) {
    /* Deine Anpassungen */
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
    /* Deine Anpassungen */
}

/* Desktop */
@media (min-width: 1025px) {
    /* Deine Anpassungen */
}
```

---

## 🔧 Häufige Anpassungen

### Abstände vergrößern
```css
:root {
  --fw-space-section: 8rem;  /* Statt 5rem */
}
```

### Schrift ändern
```css
:root {
  --fw-font-sans: 'Poppins', sans-serif;
}
```

### Ecken runder machen
```css
:root {
  --fw-radius-lg: 1.5rem;  /* Statt 0.75rem */
}
```

---

## ✅ Checkliste vor Go-Live

### Website Basics
- [ ] Alle Bilder komprimiert (< 500 KB)
- [ ] Alt-Texte für alle Bilder gesetzt
- [ ] Links funktionieren (keine 404)
- [ ] Mobile-Ansicht getestet
- [ ] SEO-Meta-Tags gesetzt (Titel, Description)
- [ ] Kontaktformular getestet
- [ ] Google Analytics eingebunden (optional)
- [ ] Cookie-Banner eingerichtet (DSGVO)
- [ ] Impressum & Datenschutz vorhanden

### Radio Player (falls aktiviert)
- [ ] Stream-URLs aktualisiert und getestet
- [ ] AzuraCast API erreichbar
- [ ] Now Playing funktioniert
- [ ] Mobile-Test (iOS + Android)
- [ ] Lautstärke-Regelung funktioniert

---

## 🆘 Troubleshooting

| Problem | Lösung |
|---------|--------|
| Farben nicht sichtbar | Cache leeren (STRG+SHIFT+R) |
| Layout bricht auf Mobile | Odoo Grid nutzen (`col-lg-6`) |
| CSS wird nicht geladen | Assets regenerieren (Odoo Backend) |
| Bilder laden langsam | Bilder komprimieren |
| Radio Player lädt nicht | Stream-URL prüfen, CORS aktivieren |
| Player überdeckt Content | `body { padding-bottom: 80px; }` |

---

## 📞 Quick-Links

- **Radio Player Guide:** `RADIO_PLAYER_GUIDE.md` 📻 **NEU!**
- **Vollständige Anleitung:** `ODOO_WEBSITE_CUSTOMIZATION_GUIDE.md`
- **Design-System CSS:** `frawo_design_system.css`
- **Homepage Template:** `frawo_homepage_template.html`

---

**Tipp:** Bookmark diese Datei für schnellen Zugriff! 🔖

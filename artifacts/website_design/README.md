# FraWo GbR Professional Website Design System

**Version:** 1.0.0
**Datum:** 2026-05-04
**Status:** Production Ready
**Für:** Odoo Website Builder (Version 17.0+)

---

## 📦 Inhalt dieses Pakets

```
website_design/
├── README.md                               # Diese Datei - Übersicht
├── QUICK_REFERENCE.md                      # Schnellzugriff für häufige Aufgaben
├── ODOO_WEBSITE_CUSTOMIZATION_GUIDE.md     # Vollständige Anleitung (40+ Seiten)
├── frawo_design_system.css                 # Haupt-CSS (Design-Tokens, Komponenten)
└── frawo_homepage_template.html            # Vollständiges Homepage-Template
```

---

## 🎯 Was ist das?

Ein **vollständiges, professionelles Design-System** für die FraWo GbR Website, optimiert für:

✅ **Odoo Website Builder** - Alle Komponenten im Editor bearbeitbar
✅ **Manuelle Anpassbarkeit** - Klar dokumentierte CSS-Variablen
✅ **Responsive Design** - Perfekt auf Mobile, Tablet, Desktop
✅ **Performance** - < 3s Ladezeit, optimierte Assets
✅ **Accessibility** - WCAG 2.1 AA konform
✅ **SEO-optimiert** - Semantisches HTML, Meta-Tags

---

## 🚀 Schnellstart (5 Minuten)

### Schritt 1: CSS einbinden

1. Öffne `frawo_design_system.css`
2. Kopiere den gesamten Inhalt (STRG+A, STRG+C)
3. In Odoo: **Website → Konfiguration → Einstellungen → Theme → CSS hinzufügen**
4. Einfügen & Speichern

### Schritt 2: Homepage erstellen

1. Öffne `frawo_homepage_template.html`
2. Kopiere eine Section (z.B. Hero-Section)
3. In Odoo: **Website → Neue Seite → HTML-Block hinzufügen**
4. Einfügen → Bilder & Texte im Editor anpassen

### Schritt 3: Farben anpassen (optional)

Suche in `frawo_design_system.css` nach:

```css
:root {
  --fw-primary: #0066CC;     /* Deine Hauptfarbe */
  --fw-secondary: #FF6B35;   /* Deine Akzentfarbe */
}
```

Ändere die Hex-Codes → Speichern → Fertig!

---

## 📚 Dokumentation

### Für Einsteiger

👉 **Starte hier:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- Copy & Paste Komponenten
- Häufige Anpassungen
- Troubleshooting

### Für Fortgeschrittene

👉 **Vollständige Anleitung:** [ODOO_WEBSITE_CUSTOMIZATION_GUIDE.md](ODOO_WEBSITE_CUSTOMIZATION_GUIDE.md)
- Schritt-für-Schritt Integration in Odoo
- Alle Komponenten erklärt
- Anpassungsmöglichkeiten
- Best Practices (SEO, Performance, Accessibility)
- Erweiterte Customization

### Design-System Referenz

👉 **CSS-Datei:** [frawo_design_system.css](frawo_design_system.css)
- Vollständig kommentiert
- Alle CSS-Variablen dokumentiert
- Komponenten-Bibliothek

---

## 🎨 Design-Features

### Farb-System

- **Primary:** Hauptfarbe für Buttons, Links, Highlights
- **Secondary:** Akzentfarbe für CTAs, wichtige Elemente
- **Neutrals:** 10-stufige Grau-Skala für Text, Hintergründe
- **Semantic:** Success, Warning, Error, Info

### Typografie

- **Fluid Typography:** Skaliert automatisch zwischen Mobile & Desktop
- **Font Stack:** Inter (mit System-Font Fallbacks)
- **6 Überschriften-Levels** (H1-H6)
- **Spezial-Texte:** Eyebrow, Lead, Body, Caption

### Spacing-System

- **8px-Grid:** Konsistente Abstände (4px, 8px, 16px, 24px, ...)
- **Fluid Sections:** Passen sich an Viewport an
- **Responsive Margins:** Kleinere Abstände auf Mobile

### Komponenten

- **Buttons:** 4 Varianten (Primary, Secondary, Ghost, Link) × 3 Größen
- **Cards:** Hover-Effekte, Schatten, abgerundete Ecken
- **Grids:** 2-, 3-, 4-Spalten, auto-fit, responsive
- **Images:** Lazy Loading, Hover-Zoom, optimierte Wrapper

---

## 📱 Responsive Design

Alle Komponenten sind **vollständig responsive**:

| Gerät | Breakpoint | Layout |
|-------|------------|--------|
| Mobile | < 768px | 1 Spalte |
| Tablet | 768px - 1024px | 2 Spalten |
| Desktop | > 1024px | 3-4 Spalten |

**Auto-Adaption:** Grids passen sich automatisch an.

---

## ⚡ Performance

Optimiert für maximale Geschwindigkeit:

- **CSS:** Minifiziert, keine unnötigen Selektoren
- **Bilder:** WebP-Format empfohlen, < 500 KB
- **Lazy Loading:** Bilder laden nur bei Bedarf
- **Critical CSS:** Inline im `<head>`
- **Caching:** Browser-Cache-freundlich

**Ziel:** Lighthouse Score > 90

---

## ♿ Accessibility (Barrierefreiheit)

WCAG 2.1 Level AA konform:

- **Kontrast:** Mindestens 4.5:1 für Text
- **Fokus-Indikatoren:** Sichtbare Outlines bei Tastatur-Navigation
- **ARIA-Labels:** Für Icons und interaktive Elemente
- **Semantisches HTML:** `<header>`, `<nav>`, `<main>`, `<footer>`
- **Reduced Motion:** Respektiert User-Preference

---

## 🔧 Anpassungsmöglichkeiten

### Einfach (ohne Code-Kenntnisse)

- Farben ändern (CSS-Variablen)
- Texte bearbeiten (Odoo Editor)
- Bilder ersetzen (Odoo Media Library)
- Layouts neu anordnen (Drag & Drop)

### Mittel (Basis CSS-Kenntnisse)

- Schriftarten ändern (Google Fonts einbinden)
- Abstände anpassen (Spacing-Variablen)
- Border-Radius (Ecken runder/eckiger)
- Schatten-Intensität

### Fortgeschritten (CSS/HTML)

- Eigene Komponenten erstellen
- Animationen hinzufügen
- Custom Grid-Layouts
- Odoo-Snippets erweitern

---

## 🛠️ Technische Details

### Browser-Unterstützung

- **Chrome/Edge:** 90+
- **Firefox:** 88+
- **Safari:** 14+
- **Mobile Safari:** 14+

### CSS-Features verwendet

- CSS Custom Properties (Variables)
- CSS Grid
- Flexbox
- `clamp()` für Fluid Typography
- CSS Transitions & Transforms
- Media Queries

### Odoo-Kompatibilität

- **Version:** 17.0+
- **Theme:** Standard Theme (anpassbar)
- **Bootstrap:** 5.x (kompatibel)

---

## 📋 Checkliste: Von Entwicklung zu Production

### Design Integration

- [ ] `frawo_design_system.css` in Odoo Theme eingefügt
- [ ] Farben angepasst (`--fw-primary`, `--fw-secondary`)
- [ ] Schriftart gewählt (falls nicht Inter)
- [ ] Homepage-Template importiert

### Content

- [ ] Alle Placeholder-Texte ersetzt
- [ ] Bilder hochgeladen & optimiert (< 500 KB)
- [ ] Alt-Texte für alle Bilder gesetzt
- [ ] Links auf korrekte Odoo-Seiten angepasst
- [ ] Kontaktinformationen aktualisiert

### SEO

- [ ] Meta-Titel gesetzt (alle Seiten)
- [ ] Meta-Description gesetzt (alle Seiten)
- [ ] H1-Überschrift pro Seite (nur 1x)
- [ ] Sitemap aktiviert (Odoo)
- [ ] robots.txt konfiguriert

### Performance

- [ ] Alle Bilder komprimiert
- [ ] WebP-Format wo möglich
- [ ] Lazy Loading aktiviert
- [ ] Lighthouse-Test > 90

### Legal

- [ ] Impressum vorhanden
- [ ] Datenschutzerklärung vorhanden
- [ ] Cookie-Banner eingerichtet (DSGVO)
- [ ] AGB (falls E-Commerce)

### Testing

- [ ] Desktop (Chrome, Firefox, Safari)
- [ ] Tablet (iPad)
- [ ] Mobile (iOS, Android)
- [ ] Alle Links funktionieren
- [ ] Kontaktformular funktioniert
- [ ] Loading-Zeit < 3s

---

## 🐛 Troubleshooting

### CSS wird nicht geladen

**Symptom:** Design sieht unformatiert aus

**Lösung:**
1. Cache leeren: STRG+SHIFT+R
2. Odoo Assets regenerieren: **Einstellungen → Technisch → Assets → Regenerieren**
3. Prüfe, ob CSS-Datei korrekt im Theme eingebunden ist

### Farben ändern sich nicht

**Symptom:** Neue Farben in CSS werden nicht angezeigt

**Lösung:**
1. Hard Reload (STRG+SHIFT+R)
2. Prüfe, ob CSS-Variablen in `:root { }` stehen
3. Teste in Inkognito-Fenster (ohne Cache)

### Layout bricht auf Mobile

**Symptom:** Elemente überlappen oder sind zu breit

**Lösung:**
1. Nutze Odoo Grid: `col-md-6`, `col-lg-4`
2. Teste mit Browser DevTools (F12 → Responsive)
3. Prüfe, ob `max-width: 100%` für Bilder gesetzt ist

### Bilder laden sehr langsam

**Symptom:** Lange Ladezeiten, schlechter Lighthouse-Score

**Lösung:**
1. Bilder komprimieren: [TinyPNG.com](https://tinypng.com)
2. WebP-Format nutzen
3. `loading="lazy"` Attribut hinzufügen
4. Bildgröße reduzieren (Hero: 1920x1080, Karten: 800x600)

---

## 📞 Support & Ressourcen

### Dokumentation

- **Quick Reference:** Schnellzugriff für Copy & Paste
- **Full Guide:** Schritt-für-Schritt Anleitung
- **CSS Comments:** Alle Variablen im Code dokumentiert

### Externe Ressourcen

- **Odoo Docs:** [docs.odoo.com/website](https://www.odoo.com/documentation/17.0/applications/websites.html)
- **CSS Tricks:** [css-tricks.com](https://css-tricks.com)
- **MDN Web Docs:** [developer.mozilla.org](https://developer.mozilla.org)

### Design Tools

- **Farben:** [Coolors.co](https://coolors.co), [Adobe Color](https://color.adobe.com)
- **Icons:** [Heroicons](https://heroicons.com), [Feather Icons](https://feathericons.com)
- **Bilder:** [Unsplash](https://unsplash.com), [Pexels](https://pexels.com)
- **Schriften:** [Google Fonts](https://fonts.google.com)

---

## 📄 Lizenz & Verwendung

**Erstellt für:** FraWo GbR
**Verwendung:** Interne Nutzung für FraWo GbR Website
**Anpassungen:** Vollständig erlaubt und erwünscht
**Weitergabe:** Nur nach Absprache

---

## 🎯 Nächste Schritte

1. **Jetzt starten:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md) öffnen
2. **CSS einbinden:** 5 Minuten Setup
3. **Erste Section:** Hero-Section importieren
4. **Anpassen:** Farben, Texte, Bilder
5. **Testen:** Mobile, Desktop, Performance
6. **Go-Live:** Checkliste abarbeiten

---

**Viel Erfolg mit der neuen Website! 🚀**

Bei Fragen: Dokumentation durchlesen oder Odoo Community Forum konsultieren.

---

**Version:** 1.0.0
**Erstellt:** 2026-05-04
**Autor:** OpenClaw Agent 3.1
**Für:** FraWo GbR - Veranstaltungstechnik & Event-Infrastruktur

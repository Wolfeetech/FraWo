# FraWo Website v3.5 — Deployment-Anleitung für Odoo

**Datum**: 2026-04-28
**Status**: Ready to Deploy
**Ziel**: Website v3.5 Ultra-Minimal im Odoo-Editor erstellen

---

## ✅ Was du bekommst

Nach diesem Deployment kannst du:

1. ✅ **Bilder austauschen** — einfach auf Bild klicken → "Replace"
2. ✅ **Text bearbeiten** — einfach draufklicken und lostippen
3. ✅ **Sections hinzufügen/löschen** — Drag & Drop im Odoo-Editor
4. ✅ **Alles im WYSIWYG-Editor anpassen** — kein Code mehr nötig
5. ✅ **Radio Player** — Sticky Footer mit FraWo Funk (Coming Soon)

---

## 📋 Deployment-Schritte

### **Schritt 1: Globale CSS einfügen (Header, Footer, Fonts)**

1. Gehe zu **https://www.frawo-tech.de** und logge dich ein
2. Klicke oben auf **"Website"** → **"Configuration"** → **"Settings"**
3. Scrolle runter zu **"Custom Code"**
4. Öffne die Datei `ODOO_GLOBAL_CSS_V3.5.css`
5. Kopiere den **GESAMTEN Inhalt** (Strg+A, Strg+C)
6. Füge ihn in **"Head Code"** ein (Strg+V)
7. Klicke auf **"Save"**

**Was passiert:**
- Header wird transparent (kein Background)
- Logo wird klein (18px) mit mix-blend-mode
- Inter Font wird geladen
- Footer wird minimal

---

### **Schritt 2: Homepage erstellen (Content + Radio Player)**

1. Klicke oben auf **"Website"** → **"Pages"**
2. Suche die **Homepage** (URL: `/`)
   - Wenn sie existiert: Klicke darauf
   - Wenn nicht: Klicke auf **"New"** und setze URL auf `/`
3. Klicke auf **"Edit"** (oben rechts)
4. Klicke auf **"HTML/XML Editor"** (Code-Symbol `</>` in der Toolbar)
5. **LÖSCHE ALLES** im Editor (Strg+A, Delete)
6. Öffne die Datei `ODOO_HOMEPAGE_V3.5_READY_TO_USE.html`
7. Kopiere den **GESAMTEN Inhalt** (Strg+A, Strg+C)
8. Füge ihn in den Odoo-Editor ein (Strg+V)
9. Klicke auf **"Save"**
10. Klicke auf **"Publish"** (oben rechts, grüner Button)

**Was passiert:**
- Komplette Homepage mit allen Sections
- Radio Player im Sticky Footer
- Alle Bilder verlinkt (du kannst sie austauschen)

---

### **Schritt 3: Bilder hochladen**

Die Homepage referenziert diese Bilder:

- `/web/image/hero-bodensee.jpg` — Hero-Bild (Line-Array am Bodensee)
- `/web/image/reference-event.jpg` — Referenz-Bild (FOH Woodstockenweiler)

**Bilder hochladen:**

1. Klicke im Odoo-Editor auf ein **Bild**
2. Klicke auf **"Replace"**
3. Wähle **"Upload an image"**
4. Lade dein Bild hoch
5. Fertig! Das Bild wird sofort ersetzt

**Tipp:** Du kannst auch im WYSIWYG-Editor einfach auf Bilder klicken und ersetzen.

---

### **Schritt 4: Testen**

1. Gehe zu **https://www.frawo-tech.de**
2. Prüfe:
   - ✅ Header ist transparent (kein Background)
   - ✅ Logo ist klein (18px)
   - ✅ Font ist "Inter" (nicht "Outfit")
   - ✅ Radio Player ist im Sticky Footer (unten fixiert)
   - ✅ Grid-Layout mit 1px Borders
   - ✅ Alles NTS-minimal

3. **Falls etwas nicht stimmt:**
   - Leere Browser-Cache (Strg+F5)
   - Warte 1-2 Minuten (Odoo cacht manchmal)
   - Prüfe, ob Globale CSS korrekt eingefügt ist

---

## 🎨 Ab jetzt: Alles im Odoo-Editor bearbeiten

### **Wie du Text änderst:**

1. Gehe auf die Seite
2. Klicke auf **"Edit"** (oben rechts)
3. Klicke auf den Text, den du ändern willst
4. Tippe einfach los
5. Klicke auf **"Save"**

### **Wie du Bilder austauschst:**

1. Klicke im Editor auf das **Bild**
2. Klicke auf **"Replace"**
3. Wähle **"Upload an image"** oder **"Choose from existing"**
4. Wähle dein Bild
5. Klicke auf **"Save"**

### **Wie du Sections hinzufügst:**

1. Klicke im Editor auf **"Blocks"** (links in der Sidebar)
2. Wähle ein **Block-Template** (z.B. "Text", "Image", "Grid")
3. Ziehe es per **Drag & Drop** auf die Seite
4. Passe es an
5. Klicke auf **"Save"**

### **Wie du Sections löschst:**

1. Hover über die **Section**
2. Klicke auf das **Papierkorb-Symbol** (oben rechts)
3. Bestätige mit **"Delete"**
4. Klicke auf **"Save"**

---

## 🚀 Fertig!

Jetzt hast du:

- ✅ **Vollständig editierbare Website** im Odoo-Editor
- ✅ **NTS-inspired Design** (ultra-minimal, clean)
- ✅ **Radio Player** im Sticky Footer
- ✅ **Kein Python-Deployment mehr nötig**

**Bei Fragen:**
Einfach im Odoo-Editor rumspielen! Es ist alles WYSIWYG, du siehst sofort, was du änderst.

---

## 📁 Dateien

- [ODOO_GLOBAL_CSS_V3.5.css](ODOO_GLOBAL_CSS_V3.5.css) — Globale CSS (Header, Footer, Fonts)
- [ODOO_HOMEPAGE_V3.5_READY_TO_USE.html](ODOO_HOMEPAGE_V3.5_READY_TO_USE.html) — Homepage Content
- [ODOO_DEPLOYMENT_ANLEITUNG_V3.5.md](ODOO_DEPLOYMENT_ANLEITUNG_V3.5.md) — Diese Anleitung

---

— Claude Sonnet 4.5 | 2026-04-28 13:45 CEST

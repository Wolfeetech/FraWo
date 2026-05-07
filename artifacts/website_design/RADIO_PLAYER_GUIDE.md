# FraWo Radio Player - Integration Guide

**Sticky Bottom Radio Player für Odoo Website**

---

## 📻 Übersicht

Der FraWo Radio Player ist ein vollständig funktionsfähiger, sticky Radio-Player, der am unteren Bildschirmrand befestigt ist und nahtlos mit dem FraWo Design System integriert.

### Features

- ✅ **Sticky Position:** Bleibt immer sichtbar am unteren Bildschirmrand
- ✅ **Collapsible:** Minimiert/Maximiert auf Knopfdruck
- ✅ **Multi-Station:** Unterstützt mehrere Radio-Sender
- ✅ **Now Playing:** Zeigt aktuell laufenden Song an (mit AzuraCast API)
- ✅ **Volume Control:** Lautstärke-Regelung
- ✅ **Touch-Optimized:** Funktioniert perfekt auf Mobile/Tablet
- ✅ **Responsive:** Passt sich an alle Bildschirmgrößen an
- ✅ **Design System Integration:** Nutzt alle CSS-Variablen des FraWo Design Systems
- ✅ **Accessibility:** ARIA-Labels, Keyboard-Navigation

---

## 🚀 Quick Start (5 Minuten)

### 1. Voraussetzungen

Stellen Sie sicher, dass das **FraWo Design System CSS** bereits in Ihrer Odoo-Website eingebunden ist:
- `frawo_design_system.css` muss im Theme geladen sein
- CSS-Variablen (`:root`) müssen verfügbar sein

### 2. Installation

**Schritt 1: HTML hinzufügen**

1. Öffne `frawo_radio_player_sticky.html`
2. Kopiere den **kompletten Code** (STRG+A, STRG+C)
3. In Odoo:
   - **Option A (Footer):** Website → Einstellungen → Theme → Footer → HTML bearbeiten → Code einfügen
   - **Option B (Building Block):** Website Editor → Block hinzufügen → HTML → Code einfügen

**Schritt 2: Stream-URLs anpassen**

Suche im Code nach den `data-stream` Attributen und ersetze sie mit deinen echten AzuraCast URLs:

```html
<!-- VORHER (Beispiel) -->
<button class="fw-radio-station"
    data-stream="https://radio.hs27.internal/listen/frawo_bodensee/stream"
    data-name="FraWo Bodensee">

<!-- NACHHER (deine URL) -->
<button class="fw-radio-station"
    data-stream="https://deine-azuracast-url.de/listen/dein_sender/stream"
    data-name="Dein Sender Name">
```

**Schritt 3: Testen**

- Öffne deine Website
- Klicke auf den Radio-Player am unteren Bildschirmrand
- Wähle einen Sender aus
- Drücke Play

✅ **Fertig!**

---

## 🎨 Anpassungen

### Farben ändern

Der Player nutzt die CSS-Variablen des Design Systems. Ändere die Farben im Theme-CSS:

```css
:root {
  --fw-primary: #0066CC;        /* Hauptfarbe (Gradient Start) */
  --fw-primary-dark: #004B99;   /* Dunkle Variante (Gradient Ende) */
}
```

Der Player passt sich **automatisch** an!

### Sender hinzufügen/entfernen

Kopiere einen Sender-Button und passe die Werte an:

```html
<button class="fw-radio-station"
    data-stream="https://radio.example.com/listen/new_station/stream"
    data-name="Neuer Sender"
    onclick="fwRadioSelectStation(this)">
    <div class="fw-station-icon">🎵</div>
    <div class="fw-station-info">
        <div class="fw-station-name">Neuer Sender</div>
        <div class="fw-station-genre">Deine Genre-Beschreibung</div>
    </div>
    <div class="fw-station-status">
        <span class="fw-status-badge"></span>
    </div>
</button>
```

**Icon Emojis:**
- 🌊 Chill/Lounge
- ⚡ Hardstyle/Techno
- ☁️ Ambient/Relax
- 🎵 Pop/Mainstream
- 🎸 Rock/Metal
- 🎹 Electronic
- 🎤 Hip-Hop/Rap

### Position anpassen

Der Player ist standardmäßig am **unteren Bildschirmrand** fixiert. Um ihn oben zu platzieren:

```css
.fw-radio-sticky {
  bottom: auto;
  top: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);  /* Schatten nach unten */
}
```

### Z-Index anpassen

Falls der Player von anderen Elementen überdeckt wird:

```css
.fw-radio-sticky {
  z-index: 9999;  /* Sehr hoher Wert */
}
```

---

## 🔧 Erweiterte Konfiguration

### Now Playing API (AzuraCast)

Der Player kann automatisch Song-Informationen von AzuraCast abrufen.

**Standard-Intervall:** 30 Sekunden

**Anpassen:**

```javascript
// Im <script>-Bereich suchen:
setInterval(fwRadioUpdateNowPlaying, 30000);  // 30 Sekunden

// Ändern auf z.B. 10 Sekunden:
setInterval(fwRadioUpdateNowPlaying, 10000);
```

**API-Endpunkt:**

Der Code versucht automatisch, die Now Playing Info von:
```
https://deine-url.com/listen/sender/nowplaying
```

Stelle sicher, dass deine AzuraCast API öffentlich zugänglich ist!

### Automatisches Abspielen

Um einen Sender beim Laden der Seite automatisch zu starten:

```javascript
// Am Ende von fwRadioInit() hinzufügen:
document.addEventListener('DOMContentLoaded', function() {
    fwRadioInit();

    // Auto-play ersten Sender
    const firstStation = document.querySelector('.fw-radio-station');
    if (firstStation) {
        fwRadioSelectStation(firstStation);
    }
});
```

**⚠️ Warnung:** Viele Browser blockieren automatisches Abspielen von Audio. Nutze dies nur mit User-Interaction!

### Lautstärke-Standard ändern

```javascript
// In fwRadioInit() suchen:
fwAudio.volume = 0.7;  // 70% Standard

// Ändern auf z.B. 50%:
fwAudio.volume = 0.5;
```

### Minimiert starten

Standardmäßig ist der Player minimiert. Um ihn erweitert zu starten:

```javascript
// Am Ende von fwRadioInit() hinzufügen:
fwIsExpanded = false;  // true für erweitert
fwRadioToggleExpand();
```

---

## 📱 Mobile Optimierung

Der Player ist bereits vollständig mobile-optimiert, aber hier sind einige Tipps:

### Touch-Target-Größe

Alle Buttons sind mindestens **36x36px** (empfohlen: 44x44px):

```css
.fw-radio-btn-mini {
  width: 44px;   /* Statt 36px */
  height: 44px;
}
```

### Mobile: Sender-Liste vertikal

Standardmäßig werden Sender auf Mobile untereinander angezeigt:

```css
@media (max-width: 768px) {
  .fw-radio-stations {
    grid-template-columns: 1fr;  /* Eine Spalte */
  }
}
```

### Mobile: Now Playing ausblenden

Die "Now Playing"-Info wird auf Mobile automatisch in der Mini-Bar ausgeblendet:

```css
@media (max-width: 768px) {
  .fw-radio-mini-nowplaying {
    display: none;
  }
}
```

---

## 🎯 Integration mit Odoo Theme

### Variante 1: Footer (Empfohlen)

**Vorteil:** Auf allen Seiten sichtbar

1. Odoo Backend → Website → Einstellungen
2. Theme → Footer bearbeiten
3. HTML-Code am Ende einfügen
4. Speichern

### Variante 2: Building Block

**Vorteil:** Flexibel platzierbar

1. Website Editor öffnen
2. Block hinzufügen → HTML
3. Code einfügen
4. Block ganz unten auf der Seite platzieren

### Variante 3: Custom Snippet

**Vorteil:** Wiederverwendbar

1. Erstelle ein neues Snippet in Odoo
2. Füge den Code hinzu
3. Speichere als "FraWo Radio Player"
4. Nutze das Snippet auf allen Seiten

---

## 🔍 Troubleshooting

| Problem | Ursache | Lösung |
|---------|---------|--------|
| **Player nicht sichtbar** | Z-Index zu niedrig | `z-index: 9999` setzen |
| **Stream lädt nicht** | Falsche URL oder CORS | URL prüfen, CORS-Header auf Server setzen |
| **Now Playing nicht aktualisiert** | API nicht erreichbar | AzuraCast API-Zugriff prüfen |
| **Buttons zu klein auf Mobile** | Touch-Target zu klein | Button-Größe auf min. 44px erhöhen |
| **Player überdeckt Content** | Kein Padding am Body | `body { padding-bottom: 80px; }` |
| **Farben passen nicht** | CSS-Variablen fehlen | Design System CSS einbinden |
| **JavaScript-Fehler** | Code unvollständig kopiert | Gesamten Code nochmal kopieren |

### Content wird überdeckt

Wenn der Player Content am Seitenende überdeckt, füge Padding hinzu:

```css
body {
  padding-bottom: 80px;  /* Höhe des Players */
}

/* Oder nur für collapsed state: */
body {
  padding-bottom: 60px;
}
```

### CORS-Fehler bei Stream

Falls der Stream nicht lädt (CORS-Fehler in Browser-Konsole):

**Lösung:** AzuraCast Server muss CORS-Header senden:

```
Access-Control-Allow-Origin: *
```

Siehe: [AzuraCast CORS Dokumentation](https://docs.azuracast.com/)

### Performance-Optimierung

Falls die Seite langsam lädt:

1. **Lazy Loading:** Lade den Player erst nach Page-Load:

```javascript
window.addEventListener('load', function() {
    fwRadioInit();
});
```

2. **CDN nutzen:** Hoste Audio-Streams auf CDN
3. **Polling reduzieren:** Now Playing nur alle 60 Sekunden abrufen

---

## 🎨 Styling-Optionen

### Transparenter Hintergrund

```css
.fw-radio-sticky {
  background: rgba(0, 102, 204, 0.9);  /* 90% opacity */
  backdrop-filter: blur(10px);          /* Blur-Effekt */
}
```

### Animationen anpassen

```css
.fw-radio-sticky {
  transition: all 0.5s ease;  /* Langsamer (statt 0.3s) */
}
```

### Schatten ändern

```css
.fw-radio-sticky {
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.3);  /* Stärker */
}
```

---

## 📊 Browser-Kompatibilität

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 80+ | ✅ Voll |
| Firefox | 75+ | ✅ Voll |
| Safari | 13+ | ✅ Voll |
| Edge | 80+ | ✅ Voll |
| Opera | 67+ | ✅ Voll |
| IE 11 | - | ❌ Nicht unterstützt |

**Empfehlung:** Zeige eine Warnung für IE11-Nutzer an.

---

## 🔐 Sicherheit

### XSS-Schutz

Der Player ist sicher gegen XSS-Angriffe, aber:

- ⚠️ **Nie** User-Input direkt in `innerHTML` einfügen
- ✅ Nutze `textContent` für dynamische Texte

### Content Security Policy (CSP)

Falls CSP aktiviert ist, erlaube:

```
Content-Security-Policy:
  media-src https://deine-radio-url.de;
  connect-src https://deine-radio-url.de;
```

---

## 📈 Analytics

### Google Analytics Events

Tracke Player-Interaktionen:

```javascript
function fwRadioSelectStation(btn) {
    // ... existing code ...

    // GA4 Event
    gtag('event', 'radio_station_select', {
        'station_name': stationName
    });
}

function fwRadioPlayPause() {
    // ... existing code ...

    // GA4 Event
    gtag('event', fwAudio.paused ? 'radio_pause' : 'radio_play');
}
```

---

## ✅ Pre-Launch Checklist

- [ ] Design System CSS ist eingebunden
- [ ] Alle Stream-URLs sind aktualisiert
- [ ] Stream-URLs wurden getestet
- [ ] AzuraCast API ist öffentlich erreichbar
- [ ] Now Playing funktioniert
- [ ] Mobile-Ansicht getestet (iOS + Android)
- [ ] Alle Buttons funktionieren
- [ ] Lautstärke-Regelung funktioniert
- [ ] Player überdeckt keinen wichtigen Content
- [ ] CORS-Header sind korrekt gesetzt
- [ ] Browser-Kompatibilität getestet
- [ ] Analytics-Events eingerichtet (optional)

---

## 🚀 Go-Live

1. ✅ Alle Tests abgeschlossen
2. 📋 Backup der Website erstellen
3. 🔧 Player-Code in Production einfügen
4. 🧪 Final-Test auf Live-Website
5. 📊 Analytics prüfen (erste 24h)
6. 🎉 Launch!

---

## 📞 Support & Weitere Infos

- **Design System:** `frawo_design_system.css`
- **Quick Reference:** `QUICK_REFERENCE.md`
- **Homepage Template:** `frawo_homepage_template.html`
- **Full Guide:** `ODOO_WEBSITE_CUSTOMIZATION_GUIDE.md`

---

**Viel Erfolg mit dem FraWo Radio Player! 🎵**

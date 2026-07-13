# FRAWO_CI_GUIDELINES — Corporate Identity (KANONISCH)
**Version: 3.0 · Status: VERBINDLICH (von Wolf freigegeben 2026-07-12) · ersetzt CI v2.0 (Mai 2026) vollständig.**
**Quelle: Deep-Research Mobile-Agent · geprüft & verifiziert von Claude 2026-07-12 (siehe Anhang A).**

> **Für ALLE Agenten (Antigravity, Jarvis/openclaw, Claude Code) und Menschen verbindlich.** Jede Gestaltung (Web, Odoo-Templates, HA-Dashboards, Social, Print, Fahrzeuge) und jeder öffentliche Text wird VOR Umsetzung gegen dieses Dokument geprüft. Kanonischer Spiegel in Odoo: **Task 97**. Widerspricht eine ältere Quelle (v2.0, Live-Look v4.1, alte Memory-Angaben) — **v3.0 gewinnt.**

## 1. Markenkern & Positionierung

Die FraWo GbR operiert an der Schnittstelle zwischen digitaler Netzwerkpräzision, moderner Medientechnik und traditioneller handwerklicher Solidität. Strategische Positionierung: **„Pragmatisches Neo-Handwerk"** — Bits, Bytes und DMX-Protokolle verschmelzen mit Holz, Stahl und Zimmermannskunst. Leitgedanke: **„Das Beste aus dem machen, was du hast"** — ehrlich, transparent, lokal in der Bodenseeregion (Lindau, Vorarlberg, Oberschwaben) verankert.

Die CI vereint sechs heterogene Geschäftsfelder unter einem Dach: verlässlich für Kommunen/Firmenkunden, „einer von uns" für die Technik-/DIY-Community, subkulturell glaubwürdig beim Beach-Rave.

### 1.1 Marktumfeld / Differenzierung
- **VT:** Zwischen polierten Großagenturen (Moser Event Plus: „State-of-the-Art", elitär) und Party-Verleihern (Bestvent, Sebass) besetzt FraWo die Mitte: IHK-Professionalität + raue, authentische „Macher"-Mentalität. Differenzierung durch Reduktion.
- **Smart Home:** Regionale Anbieter (e-team, Elektro Hildebrand, Elektro Götze) = proprietär (KNX/Loxone), steriles Weiß, Luxus. FraWo = lokal/offen (Home Assistant, Shelly), cloudfrei, reparierbar — code-naher Technologiepartner im „Dark Mode".
- **Lautsprecher/Akustik:** Zwischen High-End-Manufakturen (Avantgarde Acoustic, Grelka) und Heimkino-Ausstattern: FraWo = Werkstoff Holz im Kontrast zur technischen Platine.

### 1.2 Markenwerte
| Markenwert | Definition | Visuelle Übersetzung |
|---|---|---|
| **Radikale Pragmatik** | Form folgt Funktion. Cloudfrei, reparierbar, langlebig. Kein Overselling. | Keine Schatten/Verläufe/Glas. Strikte Raster, Editorial-Stil. |
| **Technologische Bodenständigkeit** | Digitale Expertise + physisches Handwerk. | Dunkle Themes + warme Werkstatt-Fotografie (Holz, Staub, Metall). |
| **Ehrliche Transparenz** | Offene Kalkulation, Limits, Prozesse. Augenhöhe. | Hohe Lesbarkeit, klare Typo (Inter), strukturierte Tabellen, Du-Ansprache. |

## 2. Farbsystem

Grün (Waldgrün) = Natur/Beständigkeit/Holzhandwerk (Akustik, Smart Home, Gardening). Violett = Energie/Neon/DMX/Digital (Event, Radio).
**Esoterik-Falle vermeiden:** NIEMALS weiche Übergänge, organische Schwünge oder Verläufe zwischen Grün und Violett. Einsatz streng blockhaft, kantig, getrennt durch Negativraum.

### 2.1 Primärfarben (Brand Core)
| Name | HEX | RGB | CMYK | Verwendung | Kontrast auf Void |
|---|---|---|---|---|---|
| **FraWo Forest** | `#004030` | 0,64,48 | 90,30,80,70 | Logo-Basis, große Print-Flächen. Zimmermannshandwerk, Beständigkeit. | 1.67:1 — **NIE als Text auf dunkel!** |
| **FraWo Violet** | `#a050f0` | 160,80,240 | 45,75,0,0 | Logo-Akzent, primäre CTA-Farbe (Buttons, Icons, Linien). Event + Radio. | 4.62:1 (AA, Text ok) |
| **Active Violet** | `#9d4edd` | 157,78,221 | 48,78,0,0 | NUR interaktive Zustände (Hover, Focus, Active). | 4.31:1 (UI-Komponenten ok, kein Fließtext) |

### 2.2 Neutralfarben
| Name | HEX | Verwendung | Rating |
|---|---|---|---|
| **Deep Void** | `#0a0a0a` | Globaler Web-BG, Flightcase-/Gehäuse-Lackierung | Basis Screen |
| **Spruce Surface** | `#141816` | Cards, Modals, HA-Dashboards (minimaler Grünanteil) | Basis Elemente |
| **Lumen Text** | `#e8e8e8` | Fließtext/Headlines auf dunkel (blendfrei) | 16.16:1 AAA |
| **Muted Sage** | `#98a29e` | Sekundärtext, Metadaten, deaktiv, Tabellenränder | 7.54:1 AAA |
| **Invoice Paper** | `#f9fbfb` | Print: Rechnungen, Lieferscheine, Verträge | Basis Print |
| **Invoice Ink** | `#0d1110` | Text auf Paper | 18.30:1 AAA |
| Border | `#2a2e2c` | Trennlinien, Card-Borders (aus CSS-Set) | — |

### 2.3 Statusfarben (Dashboards/Monitoring)
| Name | HEX | Verwendung | Kontrast auf Surface (verifiziert) |
|---|---|---|---|
| System Online | `#2ecc71` | Aktiv, Verbunden, Play, Pegel | 8.5:1 (AA) |
| System Alert | `#e63946` | Fehler, Offline, dringende Warnung | **4.3:1 — nur für Icons/Badges/große Schrift, nicht Fließtext** |
| System Warn | `#f39c12` | Warnung, Update, Laden, Transition | 8.2:1 (AA) |

## 3. Typografie
**Inter** (400/500/600/700) = einzige Hausschrift, Web + Print.

### 3.1 Web/Screen (16px Base, Major Third 1.250)
| Element | Weight | Größe | LH | LS | Einsatz |
|---|---|---|---|---|---|
| Display/H1 | 700 | 2.441rem (39px) | 1.1 | -0.02em | Hero, Einstiege |
| H2 | 600 | 1.953rem (31px) | 1.2 | -0.01em | Sektionen |
| H3 | 600 | 1.563rem (25px) | 1.3 | 0 | Modals, Card-Titel |
| Lead/H4 | 500 | 1.25rem (20px) | 1.4 | 0 | Einleitungen |
| Body | 400 | 1rem (16px) | 1.6 | +0.01em | Fließtext |
| UI Labels | 500 | 0.813rem (13px) | 1.5 | +0.03em | Nav, Badges, Tabellenköpfe (Uppercase) |

> **Offen (Welle-1-Entscheidung):** Display/H1 = 39px ist für Hero-Sektionen zurückhaltend (Live aktuell bis ~88px). Empfehlung: zusätzliche „Display-XL"-Stufe definieren (z. B. `clamp(39px, 6vw, 64px)`, Weight 700), sonst wirkt die Startseite nach dem Flach-Umbau leer.

### 3.2 Print (Odoo-Templates, Briefbögen)
| Element | Weight | Größe | Einsatz |
|---|---|---|---|
| H1 Document | 700 | 24pt | Belegart („RECHNUNG") |
| H2 Section | 600 | 14pt | Adressblöcke, Projekte |
| Body/Table | 400 | 10pt | Artikel, Mengen, Preise |
| Footer/Legal | 400 | 8pt | Bank, AGB, Steuernr. |

## 4. Logo-Regeln
- **Schutzraum:** Höhe des „F" aus „FraWo" — nichts darf hineinragen.
- **Mindestgröße:** Web ≥120px Breite; Print ≥30mm. Darunter: Icon-Variante.
- **Hintergründe:** Auf Void/Surface: Original-CI-Farben, Sub-Claim in Lumen. Auf unruhigen Fotos/Video: monochrom Weiß. Auf Rechnungen: vollflächig Deep Void (kein farbiges Logo im B2B-Print).

| Don't | Begründung |
|---|---|
| Farb-Invertierung (violette Fläche, grüner Akzent) | Grün = Fundament/Holz, Violett = Akzent/Technik |
| Drop-Shadows & Glows | Verletzt Radikale Pragmatik / Flat |
| Claim künstlich vergrößern | Zerstört Balance |
| Foto-Störhintergründe ohne Dark-Overlay | Unleserlich |

### 4.1 To-do Asset-Exporte
- [ ] frawo_logo_full_darkmode.svg (Web/Screen)
- [ ] frawo_logo_full_lightmode.eps (Print/Odoo)
- [ ] frawo_logo_monochrome_white.png (Video/OBS)
- [ ] frawo_logo_monochrome_black.pdf (Laser-Gravur/Fräsen)
- [ ] frawo_icon_only.svg (Social Profilbilder)
- [ ] frawo_favicon_32x32.ico + 180x180_apple_touch.png

## 5. Formsprache: VERBINDLICHE ENTSCHEIDUNG
**Strikt flach, scharfe Kanten (0px Radius), keine Glas-Effekte, keine Schatten, keine Verläufe** („Editorial-Stil"/Brutalismus, aus v2.0).

Begründung: 1) Markenpassung — Holz, Traversen, Racks, Flightcases sind kantig/präzise/industriell; Glassmorphism = generisches App-Startup. 2) Plattform-Konsistenz — Glas/Blur existiert nicht im Druck, ruckelt auf Wand-Tablets (HA-Dashboards); Farben+Kanten funktionieren überall. 3) Zielgruppen — DIY-Community und B2B wollen Informationsdichte und Funktionalität („hier wird gearbeitet, nicht dekoriert").

## 6. Komponenten (CSS Custom Properties — verbindlich für Web, Radio-Player, Odoo, HA-Themes)
```css
:root {
  /* Core Color Variables */
  --fw-bg: #0a0a0a;
  --fw-surface: #141816;
  --fw-primary: #004030;
  --fw-accent: #a050f0;
  --fw-accent-hover: #9d4edd;
  --fw-text-main: #e8e8e8;
  --fw-text-muted: #98a29e;
  --fw-border: #2a2e2c;

  /* Typography & Shape */
  --fw-font-family: 'Inter', sans-serif;
  --fw-radius: 0px; /* Strikt kantige Vorgabe */

  /* Buttons */
  --fw-btn-padding: 0.75rem 1.5rem;
  --fw-btn-bg: var(--fw-accent);
  --fw-btn-color: #ffffff;
  --fw-btn-border: 1px solid transparent;
  --fw-btn-transition: background-color 0.2s ease;

  /* Cards & Surfaces */
  --fw-card-bg: var(--fw-surface);
  --fw-card-border: 1px solid var(--fw-border);
  --fw-card-padding: 1.5rem;
  --fw-card-shadow: none; /* Keine Drop-Shadows */

  /* Inputs & Forms */
  --fw-input-bg: var(--fw-bg);
  --fw-input-border: 1px solid var(--fw-border);
  --fw-input-color: var(--fw-text-main);
  --fw-input-focus: 2px solid var(--fw-accent);

  /* Tables (Equipment-Listen) */
  --fw-table-border: 1px solid var(--fw-border);
  --fw-table-header-bg: var(--fw-primary);
  --fw-table-header-color: #ffffff;
}

.fw-button {
  background: var(--fw-btn-bg); color: var(--fw-btn-color);
  border-radius: var(--fw-radius); font-family: var(--fw-font-family);
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
  font-size: 0.875rem; padding: var(--fw-btn-padding);
  border: var(--fw-btn-border); cursor: pointer; transition: var(--fw-btn-transition);
}
.fw-button:hover, .fw-button:focus { background: var(--fw-accent-hover); outline: none; }
.fw-card { background: var(--fw-card-bg); border: var(--fw-card-border); border-radius: var(--fw-radius); padding: var(--fw-card-padding); }
.fw-badge { background: var(--fw-primary); color: #fff; padding: 0.25rem 0.5rem; font-size: 0.75rem; font-weight: 500; border-radius: var(--fw-radius); letter-spacing: 0.03em; }
```

## 7. Bildsprache
- **Kein Stock, kein künstliches Lächeln.** Fokus: Technik, Material, Struktur, echter Arbeitsprozess.
- **Licht:** Low-Key mit Praxislicht (LED-Spots, DMX, Smart-Home-Panels, Werkstattlampen).
- **Perspektive:** Wechsel aus extremen Makros (Holzmaserung, Kabelbinder, Lötstellen) und weiten Totalen (Traversen-Setups, Bodensee-Locations). Goldener Schnitt, technische Symmetrie.
- **Illustration:** AUSSCHLIESSLICH technische Blueprint-Linienzeichnungen, 1–2px, FraWo Violett auf Deep Void. Keine Piktogramme/kindliche Vektorgrafik.

### 7.1 Shotlist (15 Pflichtmotive)
1. **VT** Das saubere FOH: aufgeräumtes Pult, Blick auf violette leere Bühne
2. **VT** Bodensee-Rave: „Rave on SUP"-Totale in der Dämmerung
3. **Verleih** Flightcase-Makro: Metallecken, Butterfly-Verschlüsse
4. **Verleih** Fußball-Dart in Aktion (Größenkontrast zu Person)
5. **Smart Home** Tablet bündig in Holzwand eingelassen, dunkles HA-Interface
6. **Smart Home** Offener Technikschrank: parallele Kabel, leuchtende Shelly-Hutschienen
7. **Smart Home** Gedimmtes Wohnzimmer + physischer reduzierter Schalter (Makro)
8. **Akustik** Werkstatt-Staub: Franz an der Tischkreissäge, warmes Gegenlicht
9. **Akustik** Holz trifft HiFi: Maserung vs. schwarze Membran (Makro)
10. **Akustik** Geometrische Akustikpaneele im Streiflicht
11. **Gardening** Das Möbelstück: geschlossener Holzschrank als Designermöbel
12. **Gardening** Das System innen: Edelstahl-Hydroponik, Basilikum/Kräuter unter LED — KEINE Cannabis-Assoziation
13. **Gardening** Automations-Detail: Bodenfeuchte-Sensor + gefräster Wassertank (Makro)
14. **Radio** On Air: Großmembran-Mikro, rotes „ON AIR", violettes Ambiente
15. **Team** Wolf & Franz in schwarzer Arbeitskleidung vorm Werkstatttor, ehrlich, kein Posen

## 8. Tonalität, Wording & KCanG

**Durchgehend DU** — auch bei Kommunen und Firmenkunden. Ton: kompetent, direkt, lösungsorientiert, null Marketing-Floskeln. Fachbegriffe (DMX, MQTT, DALI, Zigbee) erwünscht.

### 8.1 KCanG §6 (Indoor Gardening) — JURISTISCH BINDEND
Werbeverbot für Cannabis + Anbauvereinigungen, weit ausgelegt (auch mittelbare Anreize, „auffällige Farbgestaltung", Szene-Vokabular). Bußgeld bis 30.000 €. Auch unbewurzelte Stecklinge = reguliert.
→ Segment-Ausrichtung öffentlich NUR: Kräuter, Microgreens, Küchengemüse. Bezeichnungen: „Smart Grow System", „Automatisierter Pflanzenschrank", „Hydroponik-Lösung".
→ **VERBOTEN öffentlich:** Hanfblätter, Neon-Grün-Ästhetik, „Weed", „Ertrag", „Growbox", „Homegrow", „Steckling", „Bud".
→ ℹ️ Das interne Odoo-Projekt „GrowBox" (P3, ID 19) ist als interne Doku davon nicht betroffen — öffentlich das Wort nie verwenden.

### 8.2 Wording (richtig / falsch)
| FraWo (richtig) | Marketing (falsch) |
|---|---|
| „Wir bauen Traversen und Anlagen, die halten. Keine halben Sachen." | „Wir realisieren Ihre unvergesslichen Event-Träume auf höchstem Niveau." |
| „Dein Smart Home. Deine Daten. Alles läuft lokal ohne Cloud-Zwang." | „Erleben Sie die magische Welt des IoT aus der Cloud." |
| „Transparente Technik-Pakete ab 50 Personen — inkl. Aufbau, ohne versteckte Kosten." | „Miete dir unsere krasse Anlage für fette Beats." |
| „Maßgefertigte Holzgehäuse direkt aus unserer Werkstatt in Weißensberg." | „Premium-Gehäuse im exquisiten Manufaktur-Design." |
| „Smart Grow Systems für die automatisierte Kultivierung von frischen Küchenkräutern." | „Wir bauen dir die perfekte Growbox für deinen diskreten Homegrow." |
| „FraWo Funk: Musik, Moods und Technik-Talk. Direkt vom Bodensee." | „Hör den krassesten Radiosender der Region." |
| „Fehler im System? Hier ist die technische Dokumentation für dein HA-Dashboard." | „Ups, da ist wohl was schiefgelaufen 🙊" |
| „Hier findest du alle Mietpreise. Transparent kalkuliert." | „Fordern Sie jetzt Ihr unverbindliches Angebot an!" |
| „Holz, Strom und Netzwerk — wir verbinden, was zusammengehört." | „Synergetische Cross-Media-Lösungen für maximale Effizienz." |
| „Für frische Kräuter und Microgreens, direkt aus dem Möbelstück im Wohnzimmer." | „Züchte deine Pflanzen mit maximalem Ertrag und fetten Blüten." |

## 9. Anwendungs-Mockups (Definitionen)
- **Website-Header:** Void-BG, flache Nav ohne Radius/Schatten, Menü in Lumen, Hover = scharfer 2px-Unterstrich in Violet. Hero = FOH-Foto mit Dark-Overlay + kantige H1.
- **Rechnungen (Odoo):** Invoice Paper BG, Invoice Ink Typo, schwarzes Logo. Tabellen-Header FraWo Forest mit weißer Schrift, Ränder Muted Sage, kantig. [ANNAHME: PDF/A4]
- **E-Mail-Signatur:** strikt textbasiert (Arial/Helvetica-Fallback), keine Banner, winziges SVG-Logo, Gliederung mit `|`, Links in Violett.
- **Instagram:** BG überwiegend FraWo Forest, sichtbares 1px-Grid, Fotos rechteckig ohne Radius, Erkennungszeichen: kleines violettes Quadrat unten rechts.
- **Radio-Player:** Blau/Orange KOMPLETT löschen. Terminal-Interface auf Void, quadratischer Play-Button in Violet, Volume = scharfe 1px-Linie, Pegel in System Online.
- **Fahrzeug:** [ANNAHME: Kastenwagen] Schwarz matt/Anthrazit, Logo groß in Forest, Claim weiß, Hecktüren = Geschäftsfelder als Typo-Liste, URL in Violett. Keine Foto-Folierung.

## 10. Migrationsplan (3 Wellen)
**Welle 1 — Digital (sofort) · Odoo-Task 489:** frawo.tech: alle Radien 12px→0px, alle Schatten/Glas-Effekte löschen, BG konsequent #0a0a0a, Typo-Skala kalibrieren. funk.frawo.tech: Blau/Orange → Violett/Void, eckige UI. Social-Profile: Logo-Icon, Du-Bio, Tabu-Wörter raus.
**Welle 2 — Backoffice (Woche 2–4) · Odoo-Task 197:** Odoo QWeb-Templates (Rechnung/Lieferschein/Angebot/Packliste) aufs Invoice-Print-Theme, Tabellen-Header Forest. E-Mail-Signaturen Wolf+Franz. Visitenkarten (schwarz-matt, Soft-Touch, violetter Farbschnitt).
**Welle 3 — Physisch (Woche 5–8) · Odoo-Task 197:** HA-YAML-Themes (Kunden + Vorführ-Objekte). Workwear (schwarz, kleiner Forest/Violett-Stick links, keine Rückenprints). Fahrzeuge & Flightcases umbekleben, Sprühschablonen/Brennstempel für Werkstatt.

## 11. Do & Don't
**DOs:** 0px-Radius überall · Trennung nur durch 1px-Border oder Volltonflächen · WCAG 2.2 AA einhalten (Forest NIE als Text auf dunkel) · sauberes Kabelmanagement zeigen · Preise/Limits transparent · Radio-Abweichler eingliedern · technische Tiefe (MQTT/DMX/DALI/Zigbee) · Holz mit warmem Gegenlicht · kurze aktive Sätze, Du-Form · Gardening strikt neutral (Kräuter/Microgreens).
**DON'Ts:** Kein Glassmorphism/Blur/weiche Schatten · kein Buzzword-Denglisch · keinerlei Cannabis-Assoziation (KCanG §6!) · kein Clipart/Corporate Memphis · NIE Forest+Violett in Verläufen mischen · nicht siezen · keine Stock-Fotos · nur Inter (nie Serif/Script/Comic) · Logo nie als Wasserzeichen · Dark Mode für Screens, helles Theme NUR Print.

---

## Anhang A: Verifikation (Claude, 2026-07-12)
Alle Farb-, Kontrast- und Logo-Angaben nachgerechnet (WCAG 2.2 relative Luminanz):
- ✅ Logo-Farbmessung bestätigt: Logo besteht real aus ~#004030 (84 %) + ~#a050f0 (6 %).
- ✅ Primär-/Neutralfarben-Kontraste: alle Claims exakt korrekt (1.67 / 4.62 / 4.31 / 16.16 / 7.54 / 18.30).
- ⚠️ Statusfarben-Claims abweichend (real): Online 8.5:1 (besser als behauptet), Warn 8.2:1 (besser), **Alert #e63946 nur 4.3:1 auf Surface** → Regel: Alert nur für Icons/Badges/große Schrift, nicht für normalen Fließtext.
- ⚠️ H1 39px ist für Hero-Sektionen sehr zurückhaltend (aktuell live: bis ~88px). Empfehlung bei Umsetzung Welle 1: zusätzliche „Display XL"-Stufe definieren, sonst wirkt die Startseite nach dem Umbau leer.
- ℹ️ Widerspruch zu Alt-Bestand: Live-Website v4.1 (Glas, 12px, Verläufe, Grün-Akzent #4ade80 auf /indoor-gardening) verstößt gegen v3.0 → wird mit Welle 1 migriert (Odoo-Task 489).

---
**Änderungshistorie**
- **v3.0 (2026-07-12):** Vollständige Neufassung. Farbkern auf gemessene Logo-Farben Forest `#004030` + Violet `#a050f0` umgestellt (vorher v2.0: `#0d4d4d` + `#a855f7`). Strikt flach/0px als verbindliche Entscheidung, KCanG-Wording, 3-Wellen-Migration. Ersetzt v2.0 (2026-05-13) vollständig.
- **v2.0 (2026-05-13):** NTS-inspiriertes Ultra-Minimal (archiviert, obsolet).

**Maintainer:** FraWo GbR (Wolf & Franz) · **Spiegel:** Odoo Task 97

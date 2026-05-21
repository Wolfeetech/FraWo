# FraWo Funk (Radio) - Corporate Identity (CI)

Dieses Dokument definiert die visuellen Leitlinien für das Webradio **FraWo Funk**, um sicherzustellen, dass die Marke konsistent und professionell auftritt. Das Design fügt sich nahtlos in die Haupt-CI von **FraWo GbR** ein, besitzt aber einen eigenen, dynamischen "Underground Electronic"-Charakter.

## 1. Markenidentität
- **Name:** FraWo Funk
- **Slogan:** "Tauchen Sie ein in die klangliche Architektur von FraWo."
- **Stilrichtung:** Underground Electronic, Brutalist, Neon, Glassmorphism, Premium.
- **Kernwerte:** Audiophile Qualität, Automatisierung (The Machine), Community-Driven, Kompromisslos.

## 2. Farbpalette

Das Radio nutzt ein **Dark-Mode-First** Design, um die Neon-Farben zum Leuchten zu bringen.

| Name | Hex-Code | Verwendung |
| :--- | :--- | :--- |
| **Deep Space Black** | `#050505` | Haupt-Hintergrund, Rahmen. |
| **Glass Grey** | `rgba(20, 20, 20, 0.4)` | Panels, Container, Glassmorphism-Effekte. |
| **Emerald Green** | `#10B981` | Primäre Akzentfarbe, "ON AIR" Indikator, Call-to-Action Buttons (z.B. Play). |
| **Electric Violet** | `#8B5CF6` | Sekundäre Akzentfarbe, Links, leichtere Frequenz-Balken im Visualizer, Marquee-Text. |
| **Dark Violet** | `#4c1d95` | Hintergrund der inaktiven Visualizer-Balken. |
| **Pure White** | `#FFFFFF` | Primärer Text (Headlines, Body). |
| **Muted Silver** | `#AAAAAA` | Sekundärer Text (Beschreibungen, Metadaten). |

## 3. Typografie

Als Hausschrift für FraWo Funk wird **Outfit** (Google Fonts) verwendet. Sie bietet eine moderne, geometrische und extrem lesbare Ästhetik.

- **Headlines (H1, Player-Titel):** 
  - Schriftart: `Outfit`
  - Gewicht: `900 (Black)`
  - Stil: Uppercase, enges Letter-Spacing (`-2px`).
  - Besonderheit: Verwendung von Text-Outlines (`-webkit-text-stroke`) in Emerald Green und Gradient-Fills.

- **Body Text:**
  - Schriftart: `Outfit`
  - Gewicht: `300 (Light)` oder `500 (Medium)`
  - Zeilenhöhe: `1.6`

- **Marquee / Laufschrift:**
  - Schriftart: `Outfit`
  - Gewicht: `800 (ExtraBold)`
  - Stil: Uppercase, weites Letter-Spacing (`4px`).

## 4. Logo

Das Logo liegt im Workspace unter `brand_assets/frawo_funk_logo.png`.
Es vereint einen leicht futuristischen Schriftzug mit Soundwellen/Viny-Elementen in unseren Hausfarben Grün und Violett auf schwarzem Grund.

- **Einsatz:** Favicon, Watermark im Stream, Social Media Profilbild, Odoo Website-Header (Radio Subpage).

## 5. UI/UX Elemente & Animationen
- **Glassmorphism:** Panels verwenden `backdrop-filter: blur(20px)` mit leicht transparenten Hintergründen und Rändern (`rgba(255,255,255,0.05)`).
- **Hover States:** Elemente skalieren beim Hover leicht (`transform: translateY(-5px)` oder `scale(1.1)`) und werfen verstärkte Schatten in den CI-Farben.
- **Visualizer:** Balken im Frequenzband reagieren in Echtzeit auf die Audio-Signale. Höhen über 80% schlagen in *Emerald Green* aus, mittlere in *Electric Violet*.
- **Pulsing Glow:** Wichtige Brand-Elemente (wie der Schriftzug "Funk" oder der "ON AIR" Dot) verwenden Endlosschleifen-Animationen (`@keyframes pulse-glow`, `@keyframes blink`), um Lebendigkeit zu suggerieren.

## 6. Community & Naming Conventions
- Gast-Hörer werden als "The Underground" bezeichnet.
- Eingeloggte Hörer erhalten "VIP Access".
- Der Auto-DJ trägt den Titel "The Machine".

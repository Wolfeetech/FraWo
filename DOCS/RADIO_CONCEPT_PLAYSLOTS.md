# Radio FraWo: Sendeplan & Content-Konzept

Dieses Dokument beschreibt das Konzept für die Programmgestaltung (Playslots) und die Content-Templates für das Radio FraWo, um einen professionellen Sendebetrieb nach Best Practices zu ermöglichen.

> [!NOTE]
> Dieses Konzept dient als Vorlage (Template) und kann im AzuraCast-System implementiert werden, sobald die Infrastruktur produktiv ist.

---

## 📅 1. Sendeplan (Playslots)

Ein professioneller Radiosender arbeitet mit festen Formaten und Sendezeiten. Hier ist ein Vorschlag für ein ausgewogenes Tagesprogramm:

| Uhrzeit | Sendung | Musikfarbe / Inhalt | Moderation |
| :--- | :--- | :--- | :--- |
| **06:00 - 10:00** | **FraWo Morning Show** | Upbeat, Hits, Wetter, Kurznachrichten | Moderiert / Live |
| **10:00 - 14:00** | **At Work / Midday** | Entspannte Pop- & Deep-House-Tracks, Tipps | Automagisch / Voice-Tracking |
| **14:00 - 18:00** | **Drive Time / Feierabend** | Energiegeladen, aktuelle Hits, Wochenend-Tipps | Moderiert / Live |
| **18:00 - 22:00** | **Special Interest / DJ Mixes** | Wechselnde Genres (z.B. Tech-House, Classic Rock, Indie) | DJ-Sets / Aufzeichnungen |
| **22:00 - 06:00** | **Night Flight** | Chillout, Ambient, Deep Melodic | Vollautomatisiert |

---

## 📁 2. Content-Kategorien (Templates)

Damit das Programm nicht monoton wirkt, muss die Playlist in AzuraCast aus verschiedenen "Töpfen" (Playlists) gefüttert werden.

### 🎵 A. Musik-Töpfe (Rotations)
- **A-Rotation (Power):** Die aktuellsten 20-30 Top-Hits. (Häufigkeit: Alle 2-3 Stunden).
- **B-Rotation (Recurrents):** Hits der letzten Monate. (Häufigkeit: Alle 4-5 Stunden).
- **C-Rotation (Gold):** Klassiker (80er, 90er, 2000er). (Häufigkeit: Als Streumaterial).
- **Newcomer/Specials:** Gezielte Förderung oder Genre-Tracks.

### 📣 B. Verpackung (Jingles & Sweeper)
- **Station ID (Opener):** "Du hörst Radio FraWo - Dein Sound für..." (Länge: 5-10 Sek). *Sollte alle 15 Minuten laufen.*
- **Sweeper:** Kurze Übergänge zwischen Songs ohne Musikbett. *Sollte zwischen 2-3 Songs laufen.*
- **Promo:** Ankündigung von Spezialsendungen. *Sollte 1x pro Stunde laufen.*

---

## 🛠️ 3. Technische Umsetzung in AzuraCast

Sobald das System läuft, werden diese Töpfe wie folgt eingerichtet:
1. **Playlists anlegen:** Für jede Kategorie (A-Rot, B-Rot, Station IDs) eine eigene Playlist erstellen.
2. **Gewichtung (Weights):** Der A-Rotation ein hohes Gewicht geben (z.B. 10), der C-Rotation ein niedriges (z.B. 2).
3. **Zeitpläne (Schedules):** Die Playlists für "Special Interest" und "Night Flight" zeitgesteuert aktivieren.

---

## 🚀 Nächste Schritte

1. **Infrastruktur stabilisieren:** Sobald VM 210 produktiv ist, setzen wir dieses Schema um.
2. **Audio-Material sammeln:** Jingles und Sweeper produzieren (oder via KI generieren lassen!).
3. **Website-Integration:** Erst wenn dieser Sendeplan läuft, binden wir den Stream mit den passenden Metadaten auf der Website ein.

---
*Erstellt durch Antigravity (OpenClaw) im Auftrag von FraWo.*

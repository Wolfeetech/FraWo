# FraWo Funk – redaktioneller Pool-Audit

Stand: 2026-10-10. Read-only-Auswertung der gesicherten Pool-Auswahl und AzuraCast-Playlistdaten.

## Ergebnis

Die technische Schedule-Prüfung ist bestanden. Dieser Audit bewertet nur Poolzusammenstellung, Künstlerwiederholungen, Genre-Lücken und Überschneidungen; er verändert keine Medien oder Sendepläne.

| Pool | Titel | Laufzeit | Künstler-Wiederholungen | Genre leer |
|---|---:|---:|---:|---:|
| Friday Peak — House & Tech House | 30 | 2.77 h | 1 | 0 |
| Friday Techno Drive | 25 | 2.49 h | 0 | 0 |
| Friday Disco Drive | 34 | 3.68 h | 2 | 0 |
| Afro Noon — Global Pulse | 31 | 3.02 h | 1 | 0 |
| Morning Bloom — Bright Flow | 35 | 3.60 h | 0 | 0 |
| City Lunch — Soul & Groove | 35 | 3.82 h | 0 | 0 |
| Deep Night — Hypnotic Drift | 35 | 3.23 h | 3 | 0 |
| Sunrise Ritual — Calm Motion | 35 | 3.44 h | 1 | 0 |
| Weekend Rise — Daylight Groove | 35 | 3.64 h | 1 | 0 |
| Tropical Noon — Sun & Soul | 35 | 3.98 h | 0 | 0 |
| Golden Hour — Velvet Sunset | 35 | 3.85 h | 1 | 0 |
| Afterwork Club — Warm Up | 35 | 3.37 h | 1 | 0 |
| Saturday Soul — Salsoul | 35 | 4.07 h | 1 | 0 |
| Sunday Deep — Deep Focus | 35 | 3.41 h | 1 | 0 |
| Night Drive — Midnight Motion | 35 | 3.35 h | 0 | 0 |
| Friday Flow — Indie Pulse | 35 | 3.59 h | 1 | 0 |
| Thursday Heat — Club Heat | 35 | 3.28 h | 0 | 0 |
| Sunday Sunset — Sunday Glow | 35 | 4.07 h | 2 | 0 |

## Auffällige Künstler-Wiederholungen

- **Friday Peak — House & Tech House:** GRIT. (2)
- **Friday Disco Drive:** Sharon Redd (3)
- **Afro Noon — Global Pulse:** Chemical Surf (2)
- **Deep Night — Hypnotic Drift:** Enrico Riva (3), Ciril (2)
- **Sunrise Ritual — Calm Motion:** Roza Terenzi (2)
- **Weekend Rise — Daylight Groove:** Eder Tobes (2)
- **Golden Hour — Velvet Sunset:** Mr. Flagio (2)
- **Afterwork Club — Warm Up:** Jay Lumen (2)
- **Saturday Soul — Salsoul:** Herbie Hancock (2)
- **Sunday Deep — Deep Focus:** Ciril (2)
- **Friday Flow — Indie Pulse:** Caitto (2)
- **Sunday Sunset — Sunday Glow:** Sister Sledge (2), T-Connection (2)

## Cross-Pool-Überschneidungen

- 11 Titel gemeinsam: `Deep Night — Hypnotic Drift` / `Sunday Deep — Deep Focus`
- 10 Titel gemeinsam: `Sunday Deep — Deep Focus` / `Night Drive — Midnight Motion`
- 8 Titel gemeinsam: `Morning Bloom — Bright Flow` / `Sunrise Ritual — Calm Motion`
- 8 Titel gemeinsam: `City Lunch — Soul & Groove` / `Tropical Noon — Sun & Soul`
- 7 Titel gemeinsam: `Deep Night — Hypnotic Drift` / `Night Drive — Midnight Motion`
- 5 Titel gemeinsam: `Sunrise Ritual — Calm Motion` / `Weekend Rise — Daylight Groove`
- 5 Titel gemeinsam: `Friday Disco Drive` / `Sunday Sunset — Sunday Glow`
- 5 Titel gemeinsam: `City Lunch — Soul & Groove` / `Saturday Soul — Salsoul`
- 5 Titel gemeinsam: `Afterwork Club — Warm Up` / `Thursday Heat — Club Heat`
- 4 Titel gemeinsam: `Tropical Noon — Sun & Soul` / `Saturday Soul — Salsoul`
- 4 Titel gemeinsam: `Sunrise Ritual — Calm Motion` / `Friday Flow — Indie Pulse`
- 4 Titel gemeinsam: `Morning Bloom — Bright Flow` / `Weekend Rise — Daylight Groove`
- 4 Titel gemeinsam: `Golden Hour — Velvet Sunset` / `Sunday Sunset — Sunday Glow`
- 3 Titel gemeinsam: `Morning Bloom — Bright Flow` / `Friday Flow — Indie Pulse`
- 3 Titel gemeinsam: `Friday Peak — House & Tech House` / `Thursday Heat — Club Heat`
- 3 Titel gemeinsam: `Friday Peak — House & Tech House` / `Afterwork Club — Warm Up`
- 2 Titel gemeinsam: `Friday Disco Drive` / `Golden Hour — Velvet Sunset`
- 1 Titel gemeinsam: `Weekend Rise — Daylight Groove` / `Friday Flow — Indie Pulse`
- 1 Titel gemeinsam: `Friday Techno Drive` / `Afterwork Club — Warm Up`

## Bewertung

- `avoid_duplicates=true` ist für die Mood-Pools aktiv. Das verhindert Titel-Dopplungen innerhalb der Playlist, ersetzt aber keine globale Künstler-Sperrzeit.
- Genreleere Titel bleiben ausgeschlossen bzw. dokumentiert; es wurden keine Genres geraten.
- BPM, Loudness und Übergangstauglichkeit sind im gesicherten API-Export nicht vorhanden. Dafür bleibt ein separater read-only Audioanalyse-Lauf erforderlich.

## Nächster sicherer Schritt

1. BPM/Loudness/Peak und Codec read-only aus den tatsächlichen Dateien ermitteln.
2. Künstler-/Titel-Abstände über eine mehrtägige Queue-Simulation prüfen.
3. Erst danach redaktionelle Rotationseinstellungen verändern.

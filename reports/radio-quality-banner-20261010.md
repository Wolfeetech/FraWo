# FraWo Funk – Qualitäts-Hinweis korrigiert

Stand: 2026-10-10.

## Anlass

Der große Qualitäts-Hinweis auf der Radioseite zeigte pauschal `320K HD`, obwohl Mobilgeräte jetzt HLS/AAC adaptiv verwenden und bei Bedarf auf 192-kbit/s-MP3 zurückfallen.

## Änderung

Der nicht verwendete Qualitäts-Umschalter wurde aus der öffentlichen Ansicht entfernt und durch einen kleinen, nicht klickbaren Informationshinweis ersetzt:

- Desktop: `DESKTOP: MP3 320K`
- Mobil: `MOBIL: AAC ADAPTIV`

Der Tooltip erklärt zusätzlich den MP3-Fallback für inkompatible Browser.

## Live-Nachweis

- Öffentliche Radioseite: HTTP 200
- Qualitätsanzeige ist kein `<button>` mehr, sondern ein `<span>`.
- Emulierter Android-Chrome zeigt: `MOBIL: AAC ADAPTIV`.
- Desktop-Chrome zeigt: `DESKTOP: MP3 320K`.
- Die alte sichtbare 320K-Schaltfläche ist nicht mehr vorhanden.

Der vollständige Stand der Odoo-View 3353 vor der Änderung liegt unter `backups/radio-view-3353-pre-quality-banner-20261010.raw`.

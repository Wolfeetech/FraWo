# Workflow & Handbuch: Zentrale Musikverwaltung & Musik-Import (FraWo Funk)

> **Verbindliches Standard Operating Procedure (SOP) für Operatoren (Wolf, Franz, KI-Agenten)**  
> **SSOT Speicherort:** CT120 Fileserver (`10.1.0.94`), angebunden als `M:` (`\\10.1.0.94\music`) & `R:` (`\\10.1.0.94\radio`).

---

## 🎯 Übersicht der Architektur

Die Musikverwaltung von FraWo ist zentralisiert und hierarchisch aufgebaut:

```text
[ CT120 Fileserver (10.1.0.94) ]
   ├── M:\music\ (Netzlaufwerk M:)
   │    ├── Inbox\                    <-- Dropzone für neu gekaufte/heruntergeladene Musik
   │    └── Library\                  <-- Master-Archiv (nach Genre & Künstler strukturiert)
   │         ├── 80S; NEW WAVE\
   │         ├── ACID; TECHNO\
   │         ├── DISCO\
   │         └── HOUSE\
   └── R:\radio\ (Netzlaufwerk R:)     <-- AzuraCast Live-Medien & Playlists
```

---

## 🚀 3-Schritte-Workflow: Neue Musik einpflegen

### Schritt 1: Neue Musik in die Dropzone legen
1. Neue Musikeinkäufe (z.B. von Bandcamp, Beatport, Thomann, Rippings) herunterladen.
2. Die Audiodateien (`.flac`, `.mp3`, `.wav`, `.m4a`) auf dem StudioPC in den Ordner **`M:\Inbox\`** kopieren.

---

### Schritt 2: Import-Skript starten (Ein-Klick)
Auf dem StudioPC die PowerShell öffnen und folgendes Skript ausführen (oder Shortcut auf dem Desktop nutzen):

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\StudioPC\FraWo\scripts\tools\Import-NewMusic.ps1"
```

**Was das Skript automatisch erledigt:**
1. **Metadaten-Analyse:** Liest Interpret, Titel und Genre/BPM aus den neuen Dateien aus.
2. **Bibliotheks-Einsortierung:** Verschiebt die Dateien aus `M:\Inbox\` sauber nach `M:\Library\<Genre>\<Künstler>\`.
3. **AzuraCast Medienscan:** Stößt auf VM210 (`10.1.0.38`) den Medienscan an (`azuracast:media:reprocess 1`).
4. **Dayparting-Zuordnung:** Weist die neuen Tracks automatisch der passenden Tageszeiten-Playlist zu.

---

### Schritt 3: Automatische Playlist-Verteilung (Dayparting)

Die Tracks werden anhand ihrer Genres & Energie-Metrik automatisch wie folgt verteilt:

| Tageszeit Block | Uhrzeit | Playlist Name | AzuraCast ID | Enthaltene Genres / Mappings |
|-----------------|---------|---------------|--------------|------------------------------|
| **DEEP_NIGHT** | 22:00 – 06:00 | Deep / Night & Night | `837` & `845` | Downtempo, Ambient, Deep House, Minimal, Darkwave, Trip-Hop, Soul, Jazz |
| **SUNRISE_MORNING** | 06:00 – 12:00 | Sunrise & Morning Drive | `840` & `841` | Disco, Nu Disco, Italo Disco, Pop, Funk, Freestyle, Synthpop, Electronic |
| **LUNCH_AFTERNOON** | 12:00 – 18:00 | Lunch & Afternoon | `842` & `843` | House, Tech House, Garage House, UK Garage, Progressive House, Afro House |
| **EVENING_PEAK** | 18:00 – 22:00 | Evening | `844` | Techno, Trance, Hard Dance, Electro, Breakbeat, Big Beat, Rave, EBM |

---

## 🛠️ Manuelle Verifikation & Notfall-Befehle

Falls nach einem Import manuell nachgeprüft werden soll:

- **Medienscan manuell auslösen (ProDesk SSH):**
  ```bash
  ssh root@10.1.0.128 "qm guest exec 210 -- docker exec azuracast azuracast_cli azuracast:media:reprocess 1"
  ```
- **Playlist-Neu-Zuordnung manuell erzwingen (StudioPC):**
  ```powershell
  python3 C:\Users\StudioPC\FraWo\apps\yourparty\apps\api\apply_dayparting_genre.py
  ```
- **Live-Stream prüfen:**
  `https://10.1.0.38/listen/frawo_funk/radio.mp3`

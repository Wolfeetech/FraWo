# Radio-Redaktionsseite im Portal (v1: Eichung + Prüfliste) — Design

**Status:** Entwurf zur Freigabe durch Wolf. Noch nichts gebaut.
**Odoo:** #1090 · **Baut auf:** `2026-09-30-frawo-funk-musikredaktion-design.md` (Abschnitt 7, Schritt 3)

## 1. Zweck

Wolf will die Energie-Eichung (≈ 50 Titel, 1–5) und später die Prüfliste der
Redaktion (`widerspruch`/`unklar`) **am Handy, beim Hören nebenbei** erledigen
(Entscheidung 30.09.: „Warten auf die Portal-Seite“ statt Playlist + Tabelle).
Keine technische Oberfläche, ein Titel pro Bildschirm, große Knöpfe.

## 2. Was die Seite kann (v1)

1. **Eichung** — spielt eine 30-s-Hörprobe aus der Mitte des Titels, Wolf tippt
   **1 · 2 · 3 · 4 · 5** (ruhig → Peak) oder **„überspringen“**. Nächster Titel
   kommt automatisch. Fortschritt „17 / 50“.
2. **Prüfliste** — gleiche Ansicht für Titel mit `widerspruch`/`unklar`:
   Hörprobe + die gefundenen Quellen-Vorschläge als Knöpfe (z. B. „Deep House
   (Beatport)“ · „Disco (Discogs)“) + „keins davon“ + Energie 1–5.

Nicht in v1: laufenden Sendetitel bewerten, Titel zwischen Sendungen schieben,
Suche. Kommt als v2, wenn v1 im Alltag trägt.

## 3. Aufbau

| Teil | Wo | Aufgabe |
|---|---|---|
| **Hörproben-Erzeuger** | CT120 (Musikserver), Skript im Repo `deployments/musikredaktion/hoerproben.py` | schneidet mit `ffmpeg` 30 s ab Titelmitte → MP3 128 kbit/s (~0,5 MB), nur für die Titel auf der jeweiligen Liste |
| **Ablage der Hörproben** | Odoo, als Anhang (`ir.attachment`) an einem Datensatz `frawo.radio.pruefung` | Odoo prüft den Login; nichts von der Bibliothek wird öffentlich |
| **Seite** | Modul `frawo_agent`, Route `/radio/redaktion`, nur angemeldete Nutzer der Gruppe „Radio-Redaktion“ (Wolf) | Handy-Ansicht, `<audio>` + Knöpfe, speichert per JSON-Aufruf |
| **Rückweg in die Bibliothek** | CT120, `rueckschreiben.py` (nachts, Teil der Redaktion) | holt Wolfs Urteile aus Odoo und schreibt sie per beets-Schnittstelle (`energie`, `genre`/`style`, `redaktion=belegt`, `quelle_* = "Wolf <Datum>"`) |

**Warum Hörproben statt direkt vom Sender:** Getestet 30.09.: Odoo erreicht
AzuraCast (`/api/station/1/file/<id>/play`, Schlüssel gültig), aber der Sender
liefert **immer die ganze Datei** (keine Teilbereiche) — bei FLAC 30–50 MB je
Titel, fürs Handy untauglich. Hörproben sind klein, sofort da und vom Sender
unabhängig.

**Datenmodell `frawo.radio.pruefung`:** `beets_id`, `artist`, `title`, `art`
(`eichung`|`pruefliste`), `vorschlaege` (JSON: Quelle, Genre, Stil, URL),
`energie` (1–5, leer), `entscheidung` (gewählter Vorschlag / „keins“),
`status` (`offen`|`erledigt`|`uebersprungen`), `erledigt_am`, Anhang = Hörprobe.
Nach dem Rückschreiben wird die Hörprobe gelöscht (Speicher bleibt klein).

## 4. Eichliste (50 Titel)

Nicht zufällig, sondern **über die Messwerte gestreut**: je 10 Titel aus fünf
Bereichen (Tempo × Dynamik × Beatport-Stil), damit jede Energiestufe
Beispiele hat. Nur Titel mit echter Datei und gültiger Messung.

## 5. Fehler und Grenzen

- Titel ohne Datei oder mit Messfehler kommen nicht auf die Liste.
- Hörprobe lässt sich nicht erzeugen (defekte Datei) → Titel wird übersprungen
  und in einer Liste vermerkt, nicht stillschweigend verschluckt.
- Doppelter Tipp (Netzaussetzer) → das Speichern ist idempotent je Datensatz.
- Kein Autoplay-Zwang: Handy-Browser verlangen einen Tipp zum Start; danach
  spielt die Seite automatisch weiter.

## 6. Abnahme

- Wolf bewertet 50 Titel am Handy in ≤ 20 Minuten ohne Hilfe.
- Die 50 Urteile stehen danach in beets (`energie`, `quelle_energie="Wolf 2026-…"`).
- Aus den Urteilen werden die Mess-Schwellen gesetzt; Kontrolle: ≥ 80 % der
  50 Titel landen mit der Formel in Wolfs Stufe ±1.

## 7. Offene Punkte für Wolf

1. Passt „ein Titel pro Bildschirm, 30 s ab Mitte, Knöpfe 1–5“?
2. Soll Franz die Seite auch nutzen dürfen (zweite Meinung) — oder nur Wolf?

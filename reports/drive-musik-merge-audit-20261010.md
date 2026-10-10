# Drive-Musikbestandsprüfung — 2026-10-10

## Ergebnis

Der vorhandene globale Drive-Export umfasst 105.280 Dateien und ist als Arbeitsgrundlage vorhanden, aber die Klassifikation darf nicht direkt als Importliste verwendet werden.

- Rohbestand: 105.280 Dateien
- als `musik` klassifiziert: 63.514 Dateien
- tatsächliche Audio-Endungen nach read-only Gegenprüfung: **19.094 Dateien**
- Audio-Volumen nach Manifestgrößen: rund **719,4 GB**
- Verteilung der Audio-Dateien:
  - `FraWo_Musik`: 17.372
  - `Soulseek Downloads`: 1.188
  - `FraWo_Radio_Library`: 534
- Kandidaten mit gleichem Namen: 531
- Audio-Dateien unter 1 MB: 304

## Befund zur vorhandenen Klassifikation

Die Gruppe `musik` enthält neben Audiodateien auch Coverbilder und weitere Dateien aus Musikordnern. Deshalb sind die 63.514 Einträge kein belastbarer Audio-Importumfang. Der vollständige Drive-Merge darf erst nach einer technischen Audio-Prüfung erfolgen: echte Endung, Dateigröße, Lesbarkeit, Dauer, Metadaten und Fingerprint.

Der vorhandene komprimierte Inventar-Export ist außerdem vorzeitig abgeschnitten (`Compressed file ended before the end-of-stream marker`). Für die weitere Arbeit wird daher der lesbare JSON-Klassifikationsbestand verwendet; ein neuer vollständiger Export ist vor jedem globalen Abgleich erforderlich.

## Sicherheitsstatus

- Keine Drive-Datei verschoben, gelöscht oder in den Papierkorb gelegt.
- Keine Radio-Datei verändert.
- Keine Import- oder Massenbereinigung ausgelöst.

## Nächster Schritt in #1929

Einen vollständigen, lesbaren Drive-Audioindex neu erzeugen und danach die Audio-Dateien gegen die kanonische `Master_Library` über Fingerprint, Dauer und Metadaten abgleichen. Erst daraus entsteht eine belastbare Import-/Dublettenliste.

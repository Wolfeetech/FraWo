-- FraWo Funk — Playlisten bereinigen
-- Angelegt 29.07.2026 nach der Bestandsaufnahme der Bibliothek.
--
-- WICHTIG: Es werden KEINE Musikdateien gelöscht. Diese Datei ändert nur,
-- welche Dateien in den Playlisten stehen. Alles bleibt auf der Platte und
-- lässt sich jederzeit wieder zuweisen.
--
-- Sicherung der Zuordnungen vorher:
--   /tmp/playlist-zuordnung-20260729.tsv im Container (6514 Zeilen)
--   Zurückspielen: die drei Spalten sind playlist_id, media_id, weight
--
-- ---------------------------------------------------------------------------
-- WAS BEHOBEN WIRD
-- ---------------------------------------------------------------------------
--
-- 1. Kaputte Dateien in der Rotation
--    1703 Dateien der Bibliothek haben Länge 0 — sie sind unlesbar oder
--    abgebrochen. Fünf davon stehen in Playlisten. Liquidsoap überspringt sie,
--    aber jeder Übersprung ist eine Lücke im Programm.
--
-- 2. Bruchstücke in der Rotation
--    153 Playlist-Einträge sind kürzer als eine Minute. Zwischen zwei Titeln
--    plötzlich ein 40-Sekunden-Fragment klingt nach Panne, nicht nach Sender.
--
-- 3. Doubletten — der eigentliche Hammer
--    6227 der 6514 Playlist-Einträge sind Titel, die in der Bibliothek
--    mehrfach als Datei vorliegen. AzuraCasts Wiederholungssperre arbeitet
--    pro DATEI, nicht pro TITEL. Derselbe Song kann daher zweimal in einer
--    Stunde laufen, und das System hält sich dabei für korrekt.
--
--    Für einen Hörer ist das der auffälligste Unterschied zu einem
--    Profi-Sender: Man erkennt sofort, wenn sich etwas wiederholt.
--
--    Behalten wird jeweils die LÄNGSTE Fassung. Bei einer Bibliothek mit
--    9,2 Minuten Durchschnittslänge ist das die vollständige Version; die
--    kürzeren sind meist beschnittene Doppel oder Vorschau-Schnipsel.

-- ---------------------------------------------------------------------------
-- Vorher-Stand festhalten
-- ---------------------------------------------------------------------------
SELECT 'VORHER' AS zeitpunkt, COUNT(*) AS eintraege_in_playlisten
FROM station_playlist_media;

-- ---------------------------------------------------------------------------
-- Schritt 1: Kaputte Dateien und Bruchstücke aus den Playlisten nehmen
-- ---------------------------------------------------------------------------
DELETE pm FROM station_playlist_media pm
JOIN station_media m ON m.id = pm.media_id
WHERE m.length < 60;

SELECT 'nach Schritt 1' AS zeitpunkt, COUNT(*) AS eintraege_in_playlisten
FROM station_playlist_media;

-- ---------------------------------------------------------------------------
-- Schritt 2: Doubletten je Playlist auf eine Fassung reduzieren
-- ---------------------------------------------------------------------------
-- Die innere Abfrage sucht je Playlist und je Künstler/Titel-Paar den Eintrag
-- mit der längsten Spieldauer. Alles andere fliegt aus der Playlist.
-- Der doppelte Unterabfrage-Bau ist nötig, weil MariaDB dieselbe Tabelle
-- nicht gleichzeitig lesen und beschreiben kann.
DELETE pm FROM station_playlist_media pm
WHERE pm.id NOT IN (
  SELECT behalten FROM (
    SELECT SUBSTRING_INDEX(
             GROUP_CONCAT(pm2.id ORDER BY m2.length DESC, pm2.id ASC), ',', 1
           ) AS behalten
    FROM station_playlist_media pm2
    JOIN station_media m2 ON m2.id = pm2.media_id
    GROUP BY pm2.playlist_id,
             LOWER(TRIM(COALESCE(m2.artist,''))),
             LOWER(TRIM(COALESCE(m2.title,'')))
  ) AS t
);

SELECT 'NACHHER' AS zeitpunkt, COUNT(*) AS eintraege_in_playlisten
FROM station_playlist_media;

-- ---------------------------------------------------------------------------
-- Ergebnis je Playlist
-- ---------------------------------------------------------------------------
SELECT p.name AS playlist,
       p.is_enabled AS aktiv,
       COUNT(pm.id) AS titel
FROM station_playlists p
LEFT JOIN station_playlist_media pm ON pm.playlist_id = p.id
WHERE p.station_id = 1
GROUP BY p.id
ORDER BY p.weight DESC;

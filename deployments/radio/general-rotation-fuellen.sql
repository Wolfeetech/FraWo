-- FraWo Funk — Sicherheitsnetz „General Rotation" wiederherstellen
-- Angelegt 29.07.2026.
--
-- WARUM DAS WICHTIG IST
-- „General Rotation" (id 835) hat Gewicht 1 und keinen Sendeplan. Sie ist
-- damit das Auffangnetz: Sie spielt nur dann, wenn keine der geplanten
-- Playlisten etwas liefert. Sie war LEER.
--
-- Genau diese Konstellation hat am 22.06.2026 zum Sendeausfall geführt —
-- liquidsoap meldete „Queue is empty!", weil aktivierte Playlisten ohne
-- Inhalt existierten und nichts einsprang.
--
-- Zusätzlich löst es ein zweites Problem: Von 23.167 Titeln der Bibliothek
-- waren nur 5.395 überhaupt einer Playlist zugewiesen. Über drei Viertel der
-- Musik lief nie.
--
-- WAS AUFGENOMMEN WIRD
--   - je Künstler/Titel-Paar genau EINE Datei, und zwar die längste
--     (bei 9,2 Minuten Durchschnitt ist das die vollständige Fassung)
--   - nichts unter einer Minute (Bruchstücke, kaputte Dateien mit Länge 0)
--
-- Rückweg: DELETE FROM station_playlist_media WHERE playlist_id = 835;

SELECT 'vorher in General Rotation' AS was, COUNT(*) AS anzahl
FROM station_playlist_media WHERE playlist_id = 835;

-- Erst leeren, dann neu befuellen. Sonst blieben die Eintraege stehen, die
-- auf den Ordner "Duplicates" zeigen — der Ausschluss unten wirkt nur auf
-- das, was neu hinzukommt.
DELETE FROM station_playlist_media WHERE playlist_id = 835;

INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 835, k.behalten, 1, 0, 0
FROM (
  SELECT CAST(
           SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY length DESC, id ASC), ',', 1)
         AS UNSIGNED) AS behalten
  FROM station_media
  WHERE storage_location_id = (SELECT media_storage_location_id FROM station WHERE id = 1)
    AND length >= 60
    -- Der Ordner "Duplicates" bleibt aussen vor, siehe kuration-tagesablauf.sql
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k
LEFT JOIN station_playlist_media vorhanden
       ON vorhanden.playlist_id = 835 AND vorhanden.media_id = k.behalten
WHERE vorhanden.id IS NULL;

SELECT 'nachher in General Rotation' AS was, COUNT(*) AS anzahl
FROM station_playlist_media WHERE playlist_id = 835;

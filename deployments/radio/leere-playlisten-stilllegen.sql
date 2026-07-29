-- FraWo Funk — leere Playlisten stilllegen
-- Angelegt 29.07.2026.
--
-- Eine aktivierte Playlist ohne Inhalt ist gefährlicher, als sie aussieht:
-- Genau diese Konstellation hat am 22.06.2026 den Sendeausfall verursacht
-- (liquidsoap: „Queue is empty!"). Sie steht ausserdem im Sendeplan und
-- verdrängt dort andere Playlisten, ohne selbst etwas liefern zu können.
--
-- Betroffen sind:
--   Shows (Fr/Sa)     Gewicht 8 — die HÖCHSTE Priorität, und leer
--   Deep / Night      Gewicht 4, 22–06 Uhr
--   Sunrise           06–09 Uhr
--   Lunch             12–14 Uhr
--   Wolf_Special_1
--
-- Was danach passiert: In diesen Zeitfenstern greift „General Rotation"
-- (Gewicht 1, kein Sendeplan) mit ihren 8340 eindeutigen Titeln. Das Programm
-- ist damit durchgehend versorgt.
--
-- Das ist die technische Reparatur, NICHT die redaktionelle Lösung. Damit die
-- Tagesstruktur wirklich stattfindet, müssen diese Playlisten befüllt werden —
-- das ist eine inhaltliche Entscheidung und keine Aufgabe für ein Skript.
--
-- „General Rotation" (835) ist ausdrücklich ausgenommen: Sie soll auch dann
-- aktiviert bleiben, wenn sie einmal leer sein sollte, weil sie das
-- Auffangnetz ist.
--
-- Rückweg: UPDATE station_playlists SET is_enabled=1 WHERE id IN (838,837,840,842,839);

UPDATE station_playlists p
SET p.is_enabled = 0
WHERE p.station_id = 1
  AND p.id <> 835
  AND (SELECT COUNT(*) FROM station_playlist_media m WHERE m.playlist_id = p.id) = 0;

SELECT p.name          AS playlist,
       p.is_enabled    AS aktiv,
       p.weight        AS gewicht,
       COUNT(pm.id)    AS titel
FROM station_playlists p
LEFT JOIN station_playlist_media pm ON pm.playlist_id = p.id
WHERE p.station_id = 1
GROUP BY p.id
ORDER BY p.weight DESC;

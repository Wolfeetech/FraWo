-- FraWo Funk — Kuration und Tagesablauf
-- Angelegt 29.07.2026.
--
-- ===========================================================================
-- GRUNDGEDANKE
-- ===========================================================================
-- Ein Sendetag hat einen Energieverlauf. Morgens weckt man niemanden mit
-- Peaktime-Techno, und um 22 Uhr will niemand Italo-Disco. Genau das
-- unterscheidet einen Sender von einer Playlist auf Zufall.
--
-- Die Bibliothek gibt das her: 18.453 Titel tragen ein Genre. Daraus lässt
-- sich ein echter Tagesablauf bauen.
--
-- ===========================================================================
-- DREI REGELN, DIE ÜBERALL GELTEN
-- ===========================================================================
--
-- 1. CHAR_LENGTH(genre) <= 40
--    Viele Dateien tragen im Genre-Feld den kompletten Beatport-Katalog
--    ("house, techno (peak time / driving), trance (main floor), hard
--    dance…" — über 200 Zeichen). Solche Einträge würden bei JEDER Suche
--    treffen und die Kuration wertlos machen. Nur kurze, echte Genres zählen.
--
-- 2. Je Künstler und Titel genau EINE Datei, und zwar die längste.
--    Die Wiederholungssperre von AzuraCast arbeitet pro Datei, nicht pro
--    Titel — ohne diese Regel läuft derselbe Song zweimal in einer Stunde.
--
--    NACHGETRAGEN 29.07.2026 — Vorrang für Dateien AUSSERHALB des Ordners
--    "Ranger_07.26/Duplicates". Dort liegen 1800 Dateien mit 64 GB, von denen
--    eine Stichprobe von 400 Titeln zu 398 auch anderswo vorhanden war.
--
--    Der Ordner enthält nachweislich beschädigte Kopien: "Kendal - Intacto"
--    liegt dort elfmal, alle exakt 6:16 lang und als FLAC deklariert, aber
--    mit 946, 585, 562, 305, 269, 205, 76, 16 und 14 kbps. Eine FLAC-Datei
--    mit 14 kbps kann es nicht geben — FLAC ist verlustfrei, 6:16 müssten
--    rund 900 kbps sein. Das ist das Muster der defekten USB-Platte aus
--    Odoo #881, die "bei jedem Lesen andere Daten liefert".
--
--    1042 Playlist-Einträge zeigten in diesen Ordner. Mit dieser Regel
--    wandern sie auf die intakten Fassungen, ohne dass ein Titel verloren
--    geht. Erst danach kann der Ordner weggeräumt werden.
--
-- 3. Längenfenster je Sendeplatz.
--    Ein 40-Sekunden-Fragment klingt nach Panne, ein 86-Minuten-DJ-Set
--    mittags nach Versehen. Beides hat seinen Platz — nur nicht überall.
--
-- ===========================================================================
-- DER SENDETAG
-- ===========================================================================
--   06–09  Sunrise         ruhig, melodisch, tief          4–15 min
--   09–12  Morning Drive   groovig, hell, nicht fordernd   3–12 min
--   12–14  Lunch           freundlich, Disco, Funk         3–10 min
--   14–18  Afternoon       baut auf, Tech House            4–15 min
--   18–22  Evening         Peaktime                        4–15 min
--   22–06  Night           tief, hypnotisch, lang          6–40 min
--   Fr/Sa ab 22  Shows     komplette DJ-Sets               ab 20 min
--
-- Rückweg: /tmp/playlist-zuordnung-20260729.tsv im Container enthält den
-- Stand von vorher (playlist_id, media_id, weight).

-- KORREKTUR 29.07.2026: Die Spalte heisst media_storage_location_id. Die
-- fruehere Fassung schrieb "SELECT storage_location_id FROM station" - diese
-- Spalte gibt es dort nicht, MariaDB bezog sie stillschweigend auf die
-- AEUSSERE Tabelle. Die Bedingung war damit immer wahr, und es wurden beide
-- Speicherorte vermischt. Station 1 nutzt ausschliesslich Speicherort 7.
SET @loc = (SELECT media_storage_location_id FROM station WHERE id = 1);

-- Playlist-Eintraege entfernen, die auf den ungenutzten Speicherort 9 zeigen.
-- Diese Dateien kann die Station gar nicht abspielen.
DELETE pm FROM station_playlist_media pm
JOIN station_media m ON m.id = pm.media_id
WHERE m.storage_location_id <> @loc;

-- ---------------------------------------------------------------------------
-- 06–09  SUNRISE — aufwachen, nicht aufschrecken
-- ---------------------------------------------------------------------------
DELETE FROM station_playlist_media WHERE playlist_id = 840;
INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 840, k.id, 1, 0, 0 FROM (
  SELECT CAST(SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY (path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)) DESC, length DESC, id ASC), ',', 1) AS UNSIGNED) AS id
  FROM station_media
  WHERE storage_location_id = @loc
    -- Der Ordner "Duplicates" bleibt komplett aussen vor: 1800 Dateien,
    -- 64 GB, davon eine Stichprobe von 400 Titeln zu 398 auch anderswo
    -- vorhanden - und darunter nachweislich beschaedigte Kopien von der
    -- defekten Platte (Odoo #881). Eine blosse Vorrangregel reichte nicht,
    -- weil sie nur innerhalb jeder Genre-Abfrage wirkt.
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
    AND length BETWEEN 240 AND 900
    AND CHAR_LENGTH(COALESCE(genre,'')) <= 40
    AND (   LOWER(genre) LIKE '%deep house%'
         OR LOWER(genre) LIKE '%melodic house%'
         OR LOWER(genre) LIKE '%organic house%'
         OR LOWER(genre) LIKE '%downtempo%'
         OR LOWER(genre) LIKE '%chill%'
         OR LOWER(genre) LIKE '%ambient%'
         OR LOWER(genre) LIKE '%afro house%'
         OR LOWER(genre) LIKE '%progressive house%')
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%hard%'
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%peak time%'
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%psy%'
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k;

-- ---------------------------------------------------------------------------
-- 09–12  MORNING DRIVE — Groove, aber nichts Forderndes
-- ---------------------------------------------------------------------------
DELETE FROM station_playlist_media WHERE playlist_id = 841;
INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 841, k.id, 1, 0, 0 FROM (
  SELECT CAST(SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY (path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)) DESC, length DESC, id ASC), ',', 1) AS UNSIGNED) AS id
  FROM station_media
  WHERE storage_location_id = @loc
    -- Der Ordner "Duplicates" bleibt komplett aussen vor: 1800 Dateien,
    -- 64 GB, davon eine Stichprobe von 400 Titeln zu 398 auch anderswo
    -- vorhanden - und darunter nachweislich beschaedigte Kopien von der
    -- defekten Platte (Odoo #881). Eine blosse Vorrangregel reichte nicht,
    -- weil sie nur innerhalb jeder Genre-Abfrage wirkt.
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
    AND length BETWEEN 180 AND 720
    AND CHAR_LENGTH(COALESCE(genre,'')) <= 40
    AND (   LOWER(genre) = 'house'
         OR LOWER(genre) LIKE '%jackin%'
         OR LOWER(genre) LIKE '%nu disco%'
         OR LOWER(genre) LIKE '%indie dance%'
         OR LOWER(genre) LIKE '%funk%'
         OR LOWER(genre) LIKE '%soul%'
         OR LOWER(genre) LIKE '%disco%')
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%hard%'
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%peak time%'
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k;

-- ---------------------------------------------------------------------------
-- 12–14  LUNCH — hell und freundlich, kurze Stücke
-- ---------------------------------------------------------------------------
DELETE FROM station_playlist_media WHERE playlist_id = 842;
INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 842, k.id, 1, 0, 0 FROM (
  SELECT CAST(SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY (path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)) DESC, length DESC, id ASC), ',', 1) AS UNSIGNED) AS id
  FROM station_media
  WHERE storage_location_id = @loc
    -- Der Ordner "Duplicates" bleibt komplett aussen vor: 1800 Dateien,
    -- 64 GB, davon eine Stichprobe von 400 Titeln zu 398 auch anderswo
    -- vorhanden - und darunter nachweislich beschaedigte Kopien von der
    -- defekten Platte (Odoo #881). Eine blosse Vorrangregel reichte nicht,
    -- weil sie nur innerhalb jeder Genre-Abfrage wirkt.
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
    AND length BETWEEN 180 AND 600
    AND CHAR_LENGTH(COALESCE(genre,'')) <= 40
    AND (   LOWER(genre) LIKE '%disco%'
         OR LOWER(genre) LIKE '%funk%'
         OR LOWER(genre) LIKE '%soul%'
         OR LOWER(genre) LIKE '%synthpop%'
         OR LOWER(genre) LIKE '%new wave%'
         OR LOWER(genre) LIKE '%jackin%')
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%techno%'
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%hard%'
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k;

-- ---------------------------------------------------------------------------
-- 14–18  AFTERNOON — baut auf
-- ---------------------------------------------------------------------------
DELETE FROM station_playlist_media WHERE playlist_id = 843;
INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 843, k.id, 1, 0, 0 FROM (
  SELECT CAST(SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY (path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)) DESC, length DESC, id ASC), ',', 1) AS UNSIGNED) AS id
  FROM station_media
  WHERE storage_location_id = @loc
    -- Der Ordner "Duplicates" bleibt komplett aussen vor: 1800 Dateien,
    -- 64 GB, davon eine Stichprobe von 400 Titeln zu 398 auch anderswo
    -- vorhanden - und darunter nachweislich beschaedigte Kopien von der
    -- defekten Platte (Odoo #881). Eine blosse Vorrangregel reichte nicht,
    -- weil sie nur innerhalb jeder Genre-Abfrage wirkt.
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
    AND length BETWEEN 240 AND 900
    AND CHAR_LENGTH(COALESCE(genre,'')) <= 40
    AND (   LOWER(genre) LIKE '%tech house%'
         OR LOWER(genre) LIKE '%minimal%'
         OR LOWER(genre) LIKE '%afro house%'
         OR LOWER(genre) LIKE '%indie dance%'
         OR LOWER(genre) = 'house'
         OR LOWER(genre) LIKE '%electro%')
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%hard%'
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k;

-- ---------------------------------------------------------------------------
-- 18–22  EVENING — Peaktime
-- ---------------------------------------------------------------------------
DELETE FROM station_playlist_media WHERE playlist_id = 844;
INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 844, k.id, 1, 0, 0 FROM (
  SELECT CAST(SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY (path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)) DESC, length DESC, id ASC), ',', 1) AS UNSIGNED) AS id
  FROM station_media
  WHERE storage_location_id = @loc
    -- Der Ordner "Duplicates" bleibt komplett aussen vor: 1800 Dateien,
    -- 64 GB, davon eine Stichprobe von 400 Titeln zu 398 auch anderswo
    -- vorhanden - und darunter nachweislich beschaedigte Kopien von der
    -- defekten Platte (Odoo #881). Eine blosse Vorrangregel reichte nicht,
    -- weil sie nur innerhalb jeder Genre-Abfrage wirkt.
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
    AND length BETWEEN 240 AND 900
    AND CHAR_LENGTH(COALESCE(genre,'')) <= 40
    AND (   LOWER(genre) LIKE '%peak time%'
         OR LOWER(genre) LIKE '%bass house%'
         OR LOWER(genre) LIKE '%hard techno%'
         OR LOWER(genre) LIKE '%tech house%'
         OR LOWER(genre) LIKE '%trance%'
         OR LOWER(genre) = 'techno'
         OR LOWER(genre) LIKE '%electro%'
         OR LOWER(genre) LIKE '%dance%')
    AND LOWER(COALESCE(genre,'')) NOT LIKE '%downtempo%'
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k;

-- ---------------------------------------------------------------------------
-- 22–06  NIGHT — tief, hypnotisch, lange Stücke erlaubt
-- ---------------------------------------------------------------------------
DELETE FROM station_playlist_media WHERE playlist_id = 845;
INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 845, k.id, 1, 0, 0 FROM (
  SELECT CAST(SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY (path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)) DESC, length DESC, id ASC), ',', 1) AS UNSIGNED) AS id
  FROM station_media
  WHERE storage_location_id = @loc
    -- Der Ordner "Duplicates" bleibt komplett aussen vor: 1800 Dateien,
    -- 64 GB, davon eine Stichprobe von 400 Titeln zu 398 auch anderswo
    -- vorhanden - und darunter nachweislich beschaedigte Kopien von der
    -- defekten Platte (Odoo #881). Eine blosse Vorrangregel reichte nicht,
    -- weil sie nur innerhalb jeder Genre-Abfrage wirkt.
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
    AND length BETWEEN 360 AND 2400
    AND CHAR_LENGTH(COALESCE(genre,'')) <= 40
    AND (   LOWER(genre) LIKE '%raw%'
         OR LOWER(genre) LIKE '%hypnotic%'
         OR LOWER(genre) LIKE '%minimal%'
         OR LOWER(genre) LIKE '%progressive%'
         OR LOWER(genre) LIKE '%deep house%'
         OR LOWER(genre) LIKE '%psy%'
         OR LOWER(genre) LIKE '%drum & bass%'
         OR LOWER(genre) = 'techno'
         OR LOWER(genre) = 'electronic'
         OR LOWER(genre) LIKE '%trance%')
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k;

-- ---------------------------------------------------------------------------
-- Fr/Sa ab 22 Uhr  SHOWS — die kompletten DJ-Sets
-- ---------------------------------------------------------------------------
-- Der eigentliche Fund: In der Bibliothek liegen 98 vollständige DJ-Sets mit
-- durchschnittlich 86 Minuten. Der Sendeplatz dafür war reserviert und leer.
-- Das ist Wochenendprogramm, das seit Monaten ungenutzt herumlag.
DELETE FROM station_playlist_media WHERE playlist_id = 838;
INSERT INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT 838, k.id, 1, 0, 0 FROM (
  SELECT CAST(SUBSTRING_INDEX(GROUP_CONCAT(id ORDER BY (path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)) DESC, length DESC, id ASC), ',', 1) AS UNSIGNED) AS id
  FROM station_media
  WHERE storage_location_id = @loc
    -- Der Ordner "Duplicates" bleibt komplett aussen vor: 1800 Dateien,
    -- 64 GB, davon eine Stichprobe von 400 Titeln zu 398 auch anderswo
    -- vorhanden - und darunter nachweislich beschaedigte Kopien von der
    -- defekten Platte (Odoo #881). Eine blosse Vorrangregel reichte nicht,
    -- weil sie nur innerhalb jeder Genre-Abfrage wirkt.
    AND path NOT LIKE char(37,68,117,112,108,105,99,97,116,101,115,37)
    AND path NOT LIKE char(37,95,81,85,65,82,65,78,84,65,69,78,69,95,37)
    AND length >= 1200
    AND (LOWER(COALESCE(genre,'')) LIKE '%dj set%' OR length >= 2400)
  GROUP BY LOWER(TRIM(COALESCE(artist,''))), LOWER(TRIM(COALESCE(title,'')))
) k;

-- ---------------------------------------------------------------------------
-- Playlisten wieder aktivieren, sofern sie jetzt Inhalt haben
-- ---------------------------------------------------------------------------
UPDATE station_playlists p
SET p.is_enabled = 1
WHERE p.station_id = 1
  AND p.id IN (838, 840, 841, 842, 843, 844, 845)
  AND (SELECT COUNT(*) FROM station_playlist_media m WHERE m.playlist_id = p.id) > 0;

-- ---------------------------------------------------------------------------
-- Ergebnis
-- ---------------------------------------------------------------------------
SELECT p.name                                   AS sendeplatz,
       p.is_enabled                             AS aktiv,
       COUNT(pm.id)                             AS titel,
       ROUND(SUM(m.length)/3600, 1)             AS stunden_material,
       ROUND(AVG(m.length)/60, 1)               AS schnitt_min
FROM station_playlists p
LEFT JOIN station_playlist_media pm ON pm.playlist_id = p.id
LEFT JOIN station_media m ON m.id = pm.media_id
WHERE p.station_id = 1
GROUP BY p.id
ORDER BY p.weight DESC, p.name;

-- Einmal-Skript, angewendet am 14.09.2026 (Antigravity, Odoo #1261).
-- Stellt AzuraCast Station 1 von den alten Misch-Kanaelen auf das
-- 24/7-Dayparting mit 10 kuratierten Shows um.
--
-- Lag urspruenglich lose im Wurzelverzeichnis der Musikplatte
-- (/mnt/music, Laufwerk M:) und wurde am 14.09.2026 hierher verschoben
-- (Claude) - Deployment-Skripte gehoeren ins Repo, nicht auf eine Medienfreigabe.
--
-- WICHTIG: Die alten Playlists 846-855 werden nur DEAKTIVIERT, nicht
-- geloescht. Ihre Symlink-Ordner unter /mnt/music/Curated_Playlists/
-- (Ch1-Ch4, Sunrise) sind deshalb bewusst stehen geblieben - sie sind
-- der Rueckweg, falls das Dayparting zurueckgenommen werden soll.
--
-- Nach Aenderungen an der AzuraCast-Datenbank immer:
--   azuracast_cli azuracast:radio:restart 1

-- 1. Deaktiviere alte Misch-Playlists
UPDATE station_playlists SET is_enabled = 0 WHERE id IN (846, 847, 848, 849, 851, 852, 853, 854, 855);
DELETE FROM station_schedules WHERE playlist_id IN (846, 847, 848, 849, 851, 852, 853, 854, 855);

-- 2. Bestehende Shows bereinigen falls schon vorhanden
DELETE FROM station_schedules WHERE playlist_id IN (SELECT id FROM station_playlists WHERE name IN (
  '01 Sunrise', '02 Morning Drive', '03 Lunch Groove', '04 Afternoon Flow',
  '05 Evening Warmup', '06 Deep Night', '07 Peak Time Club', '08 Sunday Roadtrip',
  '09 Afro World', '10 DJ Sets'
));
DELETE FROM station_playlist_folders WHERE playlist_id IN (SELECT id FROM station_playlists WHERE name IN (
  '01 Sunrise', '02 Morning Drive', '03 Lunch Groove', '04 Afternoon Flow',
  '05 Evening Warmup', '06 Deep Night', '07 Peak Time Club', '08 Sunday Roadtrip',
  '09 Afro World', '10 DJ Sets'
));
DELETE FROM station_playlist_media WHERE playlist_id IN (SELECT id FROM station_playlists WHERE name IN (
  '01 Sunrise', '02 Morning Drive', '03 Lunch Groove', '04 Afternoon Flow',
  '05 Evening Warmup', '06 Deep Night', '07 Peak Time Club', '08 Sunday Roadtrip',
  '09 Afro World', '10 DJ Sets'
));
DELETE FROM station_playlists WHERE station_id = 1 AND name IN (
  '01 Sunrise', '02 Morning Drive', '03 Lunch Groove', '04 Afternoon Flow',
  '05 Evening Warmup', '06 Deep Night', '07 Peak Time Club', '08 Sunday Roadtrip',
  '09 Afro World', '10 DJ Sets'
);

-- 3. Die 10 Shows anlegen
INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '01 Sunrise', 'Ambient, Chillout, Morning Meditation (06:00-09:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p01 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '02 Morning Drive', 'Nu Disco, Disco House, Uplifting Indie Dance (09:00-12:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p02 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '03 Lunch Groove', 'Funk, Soul, Neo-Soul, Lo-Fi, Soft Grooves (12:00-14:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p03 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '04 Afternoon Flow', 'Deep House, Melodic Techno, Flow State Focus (14:00-18:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p04 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '05 Evening Warmup', 'Tech House, Driving House, Club Warmup (18:00-22:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p05 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '06 Deep Night', 'Hypnotic Minimal, Deep Dub Techno, Night Flow (22:00-06:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p06 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '07 Peak Time Club', 'Peak-Time Rave & High Energy Techno (Fr & Sa 22:00-02:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p07 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '08 Sunday Roadtrip', 'Soul, Funk, Vintage Classics & Roadtrip (So 10:00-18:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p08 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '09 Afro World', 'Afro House, Latin Percussion, Organic Global Beats (Mi 18:00-22:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p09 = LAST_INSERT_ID();

INSERT INTO station_playlists (station_id, name, description, type, source, playback_order, weight, is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute, include_in_requests, include_in_on_demand, is_jingle, remote_timeout, avoid_duplicates, backend_options)
VALUES (1, '10 DJ Sets', 'Continuous Mix Sets >= 35 Min (Sa 20:00-22:00)', 'default', 'songs', 'shuffle', 5, 1, 0, 0, 0, 1, 0, 0, 0, 1, '');
SET @p10 = LAST_INSERT_ID();

-- 4. Ordner in station_playlist_folders eintragen
INSERT INTO station_playlist_folders (station_id, playlist_id, path) VALUES
(1, @p01, 'Curated_Playlists/01_Sunrise'),
(1, @p02, 'Curated_Playlists/02_Morning_Drive'),
(1, @p03, 'Curated_Playlists/03_Lunch_Groove'),
(1, @p04, 'Curated_Playlists/04_Afternoon_Flow'),
(1, @p05, 'Curated_Playlists/05_Evening_Warmup'),
(1, @p06, 'Curated_Playlists/06_Deep_Night'),
(1, @p07, 'Curated_Playlists/07_Peak_Time_Club'),
(1, @p08, 'Curated_Playlists/08_Sunday_Roadtrip'),
(1, @p09, 'Curated_Playlists/09_Afro_World'),
(1, @p10, 'Curated_Playlists/10_DJ_Sets');

-- 5. L??ckenlosen 24/7 Sendeplan hinterlegen
INSERT INTO station_schedules (playlist_id, start_time, end_time, days, loop_once) VALUES
-- 01 Sunrise: Mo-Fr 06:00-09:00, Sa 06:00-10:00, So 06:00-10:00
(@p01, 600, 900, '1,2,3,4,5', 0),
(@p01, 600, 1000, '6,7', 0),

-- 02 Morning Drive: Mo-Fr 09:00-12:00
(@p02, 900, 1200, '1,2,3,4,5', 0),

-- 03 Lunch Groove: Mo-Fr 12:00-14:00
(@p03, 1200, 1400, '1,2,3,4,5', 0),

-- 04 Afternoon Flow: Mo-Fr 14:00-18:00, Sa 10:00-20:00
(@p04, 1400, 1800, '1,2,3,4,5', 0),
(@p04, 1000, 2000, '6', 0),

-- 05 Evening Warmup: Mo,Di,Do,Fr 18:00-22:00, So 18:00-22:00
(@p05, 1800, 2200, '1,2,4,5', 0),
(@p05, 1800, 2200, '7', 0),

-- 09 Afro World: Mi 18:00-22:00
(@p09, 1800, 2200, '3', 0),

-- 06 Deep Night: So-Do 22:00-06:00, Sa/So Fr??hmorgen 02:00-06:00
(@p06, 2200, 600, '7,1,2,3,4', 0),
(@p06, 200, 600, '6,7', 0),

-- 07 Peak Time Club: Fr/Sa 22:00-02:00
(@p07, 2200, 200, '5,6', 0),

-- 08 Sunday Roadtrip: So 10:00-18:00
(@p08, 1000, 1800, '7', 0),

-- 10 DJ Sets: Sa 20:00-22:00
(@p10, 2000, 2200, '6', 0);

-- 6. Sofortige Zuordnung der bereits in station_media vorhandenen Titel
INSERT IGNORE INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT @p01, id, 1, 0, 0 FROM station_media WHERE path LIKE 'Curated_Playlists/01_Sunrise/%' AND storage_location_id = 7;

INSERT IGNORE INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT @p02, id, 1, 0, 0 FROM station_media WHERE path LIKE 'Curated_Playlists/02_Morning_Drive/%' AND storage_location_id = 7;

INSERT IGNORE INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT @p03, id, 1, 0, 0 FROM station_media WHERE path LIKE 'Curated_Playlists/03_Lunch_Groove/%' AND storage_location_id = 7;

INSERT IGNORE INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT @p04, id, 1, 0, 0 FROM station_media WHERE path LIKE 'Curated_Playlists/04_Afternoon_Flow/%' AND storage_location_id = 7;

INSERT IGNORE INTO station_playlist_media (playlist_id, media_id, weight, last_played, is_queued)
SELECT @p05, id, 1, 0, 0 FROM station_media WHERE path LIKE 'Curated_Playlists/05_Evening_Warmup/%' AND storage_location_id = 7;

-- FraWo Funk — Lautstärke angleichen
-- Angelegt 29.07.2026.
--
-- ===========================================================================
-- DAS PROBLEM, GEMESSEN
-- ===========================================================================
-- Stichprobe von 18 Titeln aus der Bibliothek, gemessen mit ffmpeg nach
-- EBU R128 (derselbe Standard, nach dem Spotify und der Rundfunk arbeiten):
--
--   Leiseste Titel:  -18,3 LUFS
--   Lauteste Titel:   -6,6 LUFS
--   Median:           -9,1 LUFS
--   SPANNE:           11,7 dB
--
-- 11,7 dB sind sehr deutlich hörbar. Das ist der Moment, in dem der Gast zum
-- Lautstärkeregler greift — das auffälligste Erkennungszeichen einer
-- Bastellösung.
--
-- (Ein Ausreisser bei -70 LUFS ist eine praktisch stumme Datei. Solche
-- Dateien gehören aussortiert, nicht angeglichen.)
--
-- ===========================================================================
-- WARUM DIESER WEG UND NICHT DER NAHELIEGENDE
-- ===========================================================================
-- Der übliche Weg wäre, die Lautheit in die Musikdateien zu schreiben
-- (ReplayGain-Tags). Das hat hier einen teuren Haken:
--
--   Die Musik wird stündlich per rclone nach Google Drive gesichert. Werden
--   Tags geschrieben, ändern sich alle 12.157 Dateien — und rclone lädt
--   567 GB neu hoch. Bei der gemessenen Geschwindigkeit sind das rund
--   78 Stunden Dauerlast, während der die Sicherung ausser Haus unvollständig
--   wäre.
--
-- Die Alternative wäre eine dynamische Pegelregelung im Sendeweg. Davon rät
-- die Liquidsoap-Dokumentation ausdrücklich ab ("can go as far as creating
-- saturation"), weil so eine Automatik bei Musik pumpt.
--
-- Es gibt einen dritten Weg: Liquidsoap 2.4 kann die Lautheit beim Abspielen
-- SELBST berechnen, wenn sie nicht in der Datei steht:
--
--   enable_replaygain_metadata(compute=true)
--     "This resolver will process any file decoded by Liquidsoap and add a
--      replaygain_track_gain metadata when this value could be computed."
--
-- Damit bekommen wir titelweise Angleichung — den guten Weg — ohne eine
-- einzige Datei anzufassen und ohne Upload. AzuraCast hat dafür einen
-- eigenen Schalter, es braucht also keinen eingeschleusten Code, der den
-- Sender lahmlegen könnte.
--
-- ===========================================================================
-- ZU BEOBACHTEN
-- ===========================================================================
-- Das Berechnen kostet Rechenzeit: Jede Datei muss dafür einmal dekodiert
-- werden. VM 210 ist gedrosselt (cpulimit=2). Die Warteschlange bereitet drei
-- Titel im Voraus vor, es ist also Luft — aber die Prozessorlast gehört nach
-- dem Einschalten geprüft. Steigt sie dauerhaft an die Grenze, ist der
-- Rückweg unten der richtige Schritt.
--
-- Rückweg:
--   UPDATE station SET backend_config = JSON_SET(backend_config,
--     '$.enable_replaygain_metadata', false) WHERE id = 1;
--   danach: azuracast_cli azuracast:radio:restart 1

SELECT 'vorher' AS stand,
       JSON_UNQUOTE(JSON_EXTRACT(backend_config, '$.enable_replaygain_metadata')) AS lautheit_angleichen
FROM station WHERE id = 1;

UPDATE station
SET backend_config = JSON_SET(backend_config, '$.enable_replaygain_metadata', TRUE)
WHERE id = 1;

SELECT 'nachher' AS stand,
       JSON_UNQUOTE(JSON_EXTRACT(backend_config, '$.enable_replaygain_metadata')) AS lautheit_angleichen
FROM station WHERE id = 1;

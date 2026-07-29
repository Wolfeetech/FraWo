-- FraWo Funk — Text, den der Hörer sieht
-- Angelegt 29.07.2026.
--
-- ===========================================================================
-- WARUM
-- ===========================================================================
-- 1. In der Senderbeschreibung stand ein kaputtes Zeichen:
--       "FraWo Funk â High Quality Curation & Dayparting"
--    Das ist ein Gedankenstrich, der als UTF-8 geschrieben und als Latin-1
--    gelesen wurde. Es steht im Sender-Eintrag, geht also an jeden Player
--    und auf die öffentliche Seite. So etwas fällt sofort auf.
--
--    Deshalb hier ausdrücklich SET NAMES utf8mb4 — sonst schreibt man den
--    Fehler beim Reparieren gleich wieder hinein.
--
-- 2. Die Beschreibung war ausserdem eine technische Aufzählung
--    ("High Quality Curation & Dayparting"). Das ist Fachsprache und sagt
--    einem Hörer nichts. Sie beschreibt jetzt, was tatsächlich läuft — und
--    das stimmt seit heute auch: Die Tagesstruktur ist real, nicht nur
--    geplant.
--
-- 3. Für den Fall, dass der Sender einmal nicht läuft, gab es keinen Text.
--    Dann steht dort nur eine Voreinstellung auf Englisch.

SET NAMES utf8mb4;

UPDATE station SET
  description = 'House, Disco und Techno rund um die Uhr — kuratiert nach Tageszeit. Ruhig und melodisch am Morgen, groovig über Mittag, treibend am Abend, tief in der Nacht. Freitags und samstags ab 22 Uhr laufen komplette DJ-Sets.',
  genre       = 'House · Disco · Techno · Deep'
WHERE id = 1;

-- Offline-Text in die Marken-Konfiguration schreiben, ohne die vorhandene
-- eigene Gestaltung zu verlieren: JSON_SET ändert nur diesen einen Schlüssel.
UPDATE station
SET branding_config = JSON_SET(
      COALESCE(NULLIF(branding_config, ''), '{}'),
      '$.offline_text',
      'FraWo Funk ist gerade nicht auf Sendung. Wir sind gleich wieder da.'
    )
WHERE id = 1;

SELECT name        AS sender,
       description AS beschreibung,
       genre       AS genres,
       JSON_UNQUOTE(JSON_EXTRACT(branding_config, '$.offline_text')) AS offline_text
FROM station WHERE id = 1;

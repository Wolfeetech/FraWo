-- Einmal-Skript, angewendet am 14.09.2026 (Antigravity, Odoo #1261).
-- Setzt die oeffentliche Senderbeschreibung passend zum neuen Dayparting.
-- Ersetzt inhaltlich das aeltere senderbeschreibung.sql.
--
-- Lag lose im Wurzelverzeichnis der Musikplatte und wurde am 14.09.2026
-- hierher verschoben (Claude).
--
-- Hinweis: Der live gesetzte Text weicht inzwischen leicht ab
-- ("Eigene Studio-Infrastruktur, Bodensee.") - dieses Skript ist also
-- Dokumentation des Stands, nicht die Quelle der Wahrheit.

UPDATE station SET description = 'FraWo Funk ??? 24/7 handkuratierte Musikshows im st??ndlichen Dayparting: Von Sunrise Ambient ??ber Disco House und Deep Flow bis Peak-Time Club & DJ-Sets. Kein Algorithmus, keine Werbung, eigene Studio-Infrastruktur.' WHERE id = 1;

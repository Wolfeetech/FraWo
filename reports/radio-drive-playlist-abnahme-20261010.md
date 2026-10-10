# FraWo Funk — Drive-/Playlist-Radioabnahme — 2026-10-10

## Live-Abnahme

- AzuraCast Station 1 nach der Playlist-Übernahme neu gestartet.
- Öffentlicher Now-Playing-Endpunkt: HTTP 200; gültige Ausspielung mit Artist, Titel, Album und Genre.
- Öffentlicher Stream: HTTP 206 auf Range-Anforderung, `audio/mpeg`, 1 MiB Nutzdaten, gültige MP3-Synchronbytes.
- Öffentlicher Sendeplan `/radio/schedule`: HTTP 200, 28 wiederkehrende Einträge für Montag bis Sonntag, täglich ohne Überschneidung und ohne Lücken.
- Aktuelle AzuraCast-Rücklesung: 19.868 Medien, 70 Playlist-Datensätze, 70 Queue-Readbacks ohne API-Fehler, 7.335 Queue-Einträge und 3.951 eindeutig zugeordnete Medien.
- Aktivierte sendende Playlisten haben keine leere Queue. Die vier Medien mit `length=0` bleiben außerhalb der Rotation; sie wurden nicht gelöscht. Die Testdatei und zwei betroffene Tigerblind-Dateien bleiben damit sicher aus der Ausstrahlung heraus.

## Playlist-/Sendeplanänderung

- Die vorhandene 7-Tage-Struktur wurde auf 28 redaktionelle Tages- und Zeitfenster bereinigt: Night Drive, Morning Flow, Afro-Noon, Sunset Pulse sowie die entsprechenden Dienstag–Sonntag-Familien.
- 28 Tages-/Zeitfenster wurden mit je 100 technisch geeigneten Titeln aus den bestehenden geprüften Quellen neu aufgebaut; zusätzlich bestehen `⭐ Best of the Week`, `🔥 Power Rotation` und `FraWo Selects` als sendefähige Pools.
- Alte konkurrierende Varianten mit Zusätzen wie `— Midnight Motion`, `— Deep Focus` oder `— Warm Up` wurden aus dem aktiven Wochenplan entfernt.
- Best-of- und Selects-Pools bleiben verfügbar, erzeugen aber keinen parallelen Zeitplan. Dadurch bleibt der öffentliche Wochenplan lücken- und überschneidungsfrei.
- Für den Datenbankumbau wurden mehrere vollständige AzuraCast-Sicherungen unter `/var/azuracast/backups/radio-mvp-vorher-20261010-*.sql` erzeugt.

## Noch nicht als abgeschlossen gewertet

Der separate rekursive Drive-Audioabgleich läuft noch, weil der Drive-Bestand sehr groß ist. Die Radioseite und die aktiven Playlisten sind bereits live geprüft; die globale Quelle-zu-AzuraCast-Paritätsprüfung bleibt offen, bis der laufende Drive-Lauf seinen Abschlussmarker geschrieben hat.

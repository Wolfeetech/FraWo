# FraWo Funk – Audio-/Browser-Wiedergabeprüfung

Stand: 2026-10-10.

## Befund

Der öffentliche Stream selbst liefert technisch sauber:

- MP3, Stereo, 44,1 kHz, 320 kbit/s
- 60 Sekunden durchgehende FFmpeg-Aufnahme vom echten öffentlichen Stream
- 2.401.745 Bytes für 60,003 Sekunden
- keine FFmpeg-Dekodierfehler
- HTTP 200 mit `audio/mpeg`, `ice-audio-info: channels=2;samplerate=44100;bitrate=320`

Eine Serverüberlastung oder ein kaputter MP3-Stream ist damit nicht nachgewiesen.

## Gefundene Browser-Ursache

Die Radioseite hatte zwei getrennte Audiowege:

1. den globalen Dauerplayer mit `new Audio()`;
2. zusätzlich ein eigenes `<audio id="frawo-live-stream">` mit einer zweiten Wiedergabelogik.

Der zweite Player hatte keine robuste Wiederverbindung bei `stalled`, `waiting`, `abort` oder `emptied`. Dadurch konnte der Browser die Wiedergabe beenden, während die Oberfläche weiter einen scheinbar aktiven Player zeigte.

## Korrektur

- Das zweite Audio-Element und seine separate Wiedergabelogik wurden aus der live ausgelieferten Radioansicht entfernt.
- Die Radio-Steuerung verwendet jetzt ausschließlich `window.fwAudio`.
- Der globale Player baut bei Netzwerk-/Stream-Unterbrechungen automatisch eine neue Verbindung auf:
  - `error`
  - `stalled`
  - `waiting`
  - `abort`
  - `emptied`
- Wiederverbindung mit wachsender Wartezeit bis maximal 15 Sekunden.
- Manuelles Stoppen cancelt die Wiederverbindung korrekt.
- Cache-Buster verhindert, dass der Browser eine kaputte alte Verbindung wiederverwendet.

## Live-Nachweis

Nach dem Deploy:

- `/radio`: HTTP 200
- ausgeliefertes HTML: 0 `<audio>`-Elemente der alten Radioansicht
- `radioAudio` nicht mehr vorhanden
- globaler Reconnect-Code `fw_reconnect` vorhanden
- `window.fwAudio` im echten Browser vorhanden
- Stream-Header weiterhin 44,1 kHz / 320 kbit/s

## Mobile-Anpassung

Die Störung trat laut Betreiber nur am Handy auf. Deshalb wurde zusätzlich eine mobile Schonstrecke aktiviert:

- Mobilgeräte und schmale Ansichten verwenden `radio_light` mit 192 kbit/s.
- Desktop bleibt bei `radio.mp3` mit 320 kbit/s.
- Die Web-Audio-Tonanalyse wird mobil abgeschaltet; der Ton läuft direkt über das Audio-Element. Das vermeidet zusätzliche Web-Audio-/Bluetooth-Resampling-Probleme.
- Der automatische Reconnect bleibt auch mobil aktiv.
- Der 192-kbit/s-Stream wurde separat mit FFmpeg 30 Sekunden dekodiert: fehlerfrei.

Im emulierten Android-Chrome-Browser blieb die Wiedergabe nach zehn Sekunden aktiv; die Radioseite enthält kein zweites `<audio>`-Element mehr.

## Endgültige Pause-/Weiter-Ursache

Der Ereignistest im emulierten Android-Chrome hat die Schleife sichtbar gemacht:

- initiales `emptied` beim ersten Setzen der Streamquelle
- danach `waiting`/`stalled` beim normalen mobilen Pufferverhalten
- der alte Code behandelte `emptied` bzw. `stalled` als Abbruch und startete alle wenigen Sekunden eine neue Verbindung

Korrektur:

- `emptied` startet keinen Reconnect mehr.
- `waiting` und `stalled` bleiben passive Pufferereignisse.
- Nur echte `error`-/`abort`-Ereignisse dürfen neu verbinden.
- Interne Reconnect-Vorgänge sind gegen eigene `pause`-/`emptied`-Ereignisse geschützt.
- Android-Chrome nutzt MP3; natives HLS bleibt auf iPhone/iPad-Safari begrenzt.

Nach dem Live-Fix blieb der Android-Test 30 Sekunden im Wiedergabestatus und erzeugte keine künstlichen neuen `play`-/`emptied`-Folgen mehr.


Der HLS-Weg hat ein normales `waiting`-Ereignis beim Nachladen eines Segments zu aggressiv als Streamabbruch behandelt. Dadurch konnte der eigene Reconnect den Player unnötig pausieren und neu starten.

Korrektur:

- `waiting` löst keinen sofortigen Reconnect mehr aus.
- `stalled`/`waiting` werden erst nach zehn Sekunden ohne ausreichende Daten als echter Stall bewertet.
- `playing` und `timeupdate` löschen den Stall-Timer sofort.
- Ein manueller Stopp löscht alle offenen Reconnect-Timer.
- `error`, `abort` und echte `emptied`-Fehler bleiben weiterhin abgesichert.

Damit soll der normale HLS-Segmentwechsel nicht mehr als Pause/Weiter-Schleife sichtbar werden.


Der 192-kbit/s-MP3-Stream war technisch fehlerfrei, die Abbrüche am Handy bestanden aber weiter. Deshalb nutzt die mobile Wiedergabe jetzt zuerst den verfügbaren HLS-Livestream:

- Master: `https://funk.frawo.tech/hls/frawo_funk/live.m3u8`
- AAC-Varianten: ca. 106, 141 und 352 kbit/s
- Browser ohne native HLS-Unterstützung fallen automatisch auf `radio_light` zurück.
- Desktop bleibt beim direkten 320-kbit/s-MP3.

HLS wurde öffentlich mit HTTP 200 gelesen und per FFmpeg 30 Sekunden ohne Fehler dekodiert. Im emulierten Android-Chrome blieb der Player nach zehn Sekunden im Wiedergabestatus aktiv.

Die Samplerate wurde nicht blind verändert. Der öffentliche MP3-Stream ist für Webradio technisch normal mit 44,1 kHz. Der aktuelle Nachweis spricht zuerst für ein Browser-/Player-Problem, nicht für eine belegte Serverüberlastung oder einen fehlerhaften Resampler. Eine Umstellung auf 48 kHz wäre erst nach einem direkten Vergleichstest mit einer kontrollierten Quelle sinnvoll.

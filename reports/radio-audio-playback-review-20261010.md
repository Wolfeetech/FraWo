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

## Entscheidung zu 44,1 vs. 48 kHz

Die Samplerate wurde nicht blind verändert. Der öffentliche MP3-Stream ist für Webradio technisch normal mit 44,1 kHz. Der aktuelle Nachweis spricht zuerst für ein Browser-/Player-Problem, nicht für eine belegte Serverüberlastung oder einen fehlerhaften Resampler. Eine Umstellung auf 48 kHz wäre erst nach einem direkten Vergleichstest mit einer kontrollierten Quelle sinnvoll.

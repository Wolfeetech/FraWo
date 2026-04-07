# Nextcloud Operations

## Zweck

Nextcloud ist die Benutzerablage, Kollaborationsoberflaeche und der definierte Dokumenteneingang fuer den Paperless-Workflow.

## Zugriff

- intern: `http://cloud.hs27.internal`
- direkt: `http://192.168.2.21`

## Aktueller Betriebsstand

- `wolf` und `franz` sind die normalen Benutzerpfade
- `frontend` bleibt ein bewusst eingeschraenkter Shared-Pfad
- `Paperless/Eingang` bleibt der kanonische Scan- und Upload-Zielordner
- SMTP ist geschrieben und der Baseline-Check ist gruen
- sichtbare Testmail steht noch aus

## Normalbetrieb

- persoenliche Nutzung ueber `wolf` und `franz`
- keine Admin-Konten fuer Alltag
- Uploads zuerst in Nextcloud, danach kontrolliert weiter in Paperless

## Taegliche Checks

- Login funktioniert
- Upload und Download funktionieren
- `Paperless/Eingang` ist nutzbar
- Freigaben und Grundfunktionen laufen sauber
- SMTP- und Systemmails nur ueber den definierten Mailpfad

## Bekannte Restpunkte

- sichtbare Testmail aus Nextcloud
- `frontend` nur fuer klar definierte Shared-Flows nutzen

## Nie Tun

- kein Shared-Admin als Alltagskonto
- keine wilden Speicherpfad- oder Datenverzeichnis-Experimente im Live-Betrieb
- keinen alternativen Dokumenteneingang ausserhalb des definierten Nextcloud-Pfads erfinden

## Eskalation

- bei Dokumentenproblemen zuerst Login, Upload und `Paperless/Eingang` pruefen
- danach erst Bridge oder Paperless selbst untersuchen

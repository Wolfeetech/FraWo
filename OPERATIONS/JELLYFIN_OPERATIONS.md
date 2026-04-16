# Jellyfin Operations

## Zweck

Jellyfin ist der interne Medienserver fuer Musik und spaeter weitere Medien.

## Zugriff

- LAN mit internem DNS: `http://media.hs27.internal`
- LAN direkt ohne DNS: `http://192.168.2.20:8096`
- mobil ueber `Tailscale`: `http://100.99.206.128:8449`

## Wichtig

- fuer neue Clients immer die Basis-URL eintragen, nicht `/web`
- derzeit kein `https://media.hs27.internal` verwenden
- wenn `media.hs27.internal` auf dem Geraet nicht aufloest, direkt die IP oder den Tailscale-Pfad nutzen
- fuer TVs ist `http://192.168.2.20:8096` der sichere Standardpfad

## Aktueller Betriebsstand

- SMB-Bibliothek ist die produktive Medienquelle
- die TV-Verbindung funktioniert wieder
- der letzte funktionierende TV-Test lief ueber `Wolf`
- `TV Wohnzimmer` bleibt das gemeinsame Zielprofil.

### Passwort-Management: TV Wohnzimmer
- **Status:** Passwort muss gesetzt werden.
- **Vorgehensweise:**
  1. Als Administrator in Jellyfin einloggen.
  2. Dashboard > Benutzer > `TV Wohnzimmer` auswählen.
  3. Passwort auf den Standardwert für den Haushalt setzen.
  4. Am TV-Client (192.168.2.20:8096) mit dem neuen Passwort anmelden.

## Normalbetrieb

- Benutzerprofile `Wolf`, `Franz`, `TV Wohnzimmer` getrennt halten
- neue Clients bewusst hinzufuegen
- bei DNS-Problemen nicht auf Portal- oder `/web`-Pfade ausweichen

## Taegliche Checks

- UI erreichbar
- Bibliothek sichtbar
- Wiedergabe auf Testclient funktioniert
- keine Rueckfaelle auf alte lokale Bootstrap-Pfade
- TV-Clients verbinden weiter ueber die direkte LAN-Adresse, wenn DNS fehlt

## Nie Tun

- keine Medien wieder lokal am Toolbox-Container verteilen
- keine unkontrollierten Scan- oder Pfadwechsel im Live-Betrieb
- TV-Client nicht auf `https://media.hs27.internal` oder `/web` konfigurieren

## Eskalation

- bei fehlenden Medien zuerst SMB-Sichtbarkeit und Bind-Mount pruefen
- bei TV-Problemen zuerst die Server-URL auf `http://192.168.2.20:8096` zuruecksetzen

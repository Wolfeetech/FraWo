# Raspberry Pi Resource Allocation Plan

## Zweck

Dieses Dokument beschreibt den verifizierten Ressourcenstand des `radio-node` und das konservative Low-Ressource-Zielprofil fuer den produktiven internen AzuraCast-Betrieb auf dem aktuell kleinen Raspberry-Pi-Setup.

## Verifizierter Ist-Stand

Live-Probe vom `2026-03-19` auf `radio-node`:

- Host: `radio-node`
- OS: `Ubuntu 22.04.5 LTS`
- Kernel: `5.15.0-1061-raspi`
- Architektur: `arm64`
- CPU: `4` Kerne
- RAM gesamt: `1889112 KiB` (`~1.8 GiB`)
- RAM verfuegbar zum Messzeitpunkt: `~658 MiB`
- Swap: `2 GiB`, davon nur `~32 MiB` belegt
- Rootfs frei: `~21 GiB`
- AzuraCast-Container-RAM im Leerlauf direkt nach Erstdeploy: `~448 MiB`
- AzuraCast-Updater-RAM im Leerlauf: `~4 MiB`
- Docker-Limits: aktuell bewusst **keine** harten CPU-/RAM-Limits auf Container-Ebene

## Zielprofil

Dieses System ist kein "viele Stationen / viele Listener / viele DSP-Ketten"-Host, sondern ein konservativer interner Einstiegs-Node.

- Profilname: `pi4_2gb_single_station_low_resource`
- Ziel-Lastmodell:
  - `1` Station aktiv
  - zunaechst keine parallelen Zusatzstationen
  - keine aggressiven Audio-Post-Processing-Ketten
  - kein AutoCue-Initialscan auf grosser Bibliothek
  - kein ReplayGain-On-the-Fly auf unvorbereiteten Dateien
- Verteilungsziel:
  - `~350-450 MiB` Host + Cache + SSH/Tailscale/Docker-Grundlast
  - `~500-900 MiB` AzuraCast steady-state Budget
  - `2 GiB` Swap als Sicherheitsnetz fuer Peaks, nicht als Dauerleistungspfad
  - `>15 GiB` freier Rootfs-Puffer fuer Images, Logs und temporaere Importarbeit

## Hostseitige Best-Practice-Verteilung

### Bereits umgesetzt

- `2 GiB` Swapfile aktiv
- Docker `userland-proxy` deaktiviert
- dedizierte Verzeichnisse:
  - `/var/azuracast`
  - `/srv/radio-library`
  - `/srv/radio-assets`

### Hostseitige Tuning-Ziele

- `COMPOSE_HTTP_TIMEOUT=900`
  - begruendung: langsame Pull-/Recreate-Phasen auf ARM duerfen nicht an zu knappen CLI-Zeitfenstern scheitern
- `PHP_FPM_MAX_CHILDREN=2`
  - begruendung: konservative Web-Worker-Zahl fuer ein kleines internes Setup
- `NOW_PLAYING_DELAY_TIME=15`
  - begruendung: etwas weniger Polling-Last als das Default-Verhalten
- `NOW_PLAYING_MAX_CONCURRENT_PROCESSES=1`
  - begruendung: fuer genau dieses kleine Ein-Station-Setup reicht eine serielle Verarbeitung
- `ENABLE_WEB_UPDATER=false`
  - begruendung: Updates sollen kontrolliert ueber die dokumentierten Docker-/IaC-Pfade laufen, nicht spontan aus der Weboberflaeche

## Was bewusst **nicht** gesetzt wird

- keine harten Docker-RAM-Limits fuer `azuracast`
  - begruendung: auf einem `~2 GiB`-Host fuehren zu knappe Container-Limits eher zu unnötigen OOM-/Restart-Mustern als zu echter Stabilitaet
- keine CPU-Pinning-/NanoCPU-Limits
  - begruendung: fuer diesen kleinen Host ist einfache Lastverteilung besser als kuenstliche harte Grenzen
- keine globale Portbereich-Verkleinerung vor echtem Stations-Design
  - begruendung: spart praktisch keine relevanten Ressourcen und macht den spaeteren Ausbau unnötig unflexibel

## Unmittelbare Post-Setup-Regeln in AzuraCast

Diese Punkte sind laut offizieller AzuraCast-Optimierungsdoku auf kleinen Hosts die wichtigsten Stellschrauben und bleiben nach dem Web-Setup Pflicht:

1. `ReplayGain` nicht on-the-fly rechnen lassen.
2. `Audio Post-Processing` zunaechst deaktiviert lassen.
3. `AutoCue` zunaechst deaktiviert lassen oder erst nach vorbereiteter Bibliothek aktivieren.
4. `Playback History` bewusst klein halten.
5. Medien spaeter ueber den dedizierten `RadioLibrary`-/`RadioAssets`-Pfad anbinden statt die Root-Disk vollzuschreiben.

## Definition of Done fuer den Pi

Der Pi gilt als sauber dimensioniert, wenn:

- der Host im Leerlauf noch einen klaren Puffer hat
- AzuraCast stabil ohne Swap-Dauerlast laeuft
- genau eine Station intern sauber spielt
- die ersten Medienimporte nicht zu OOM-/Restart-Mustern fuehren
- die Weboberflaeche und der Stream ohne spuerbare Hanger reagieren

## Quellen

- AzuraCast Docker Installation:
  - https://www.azuracast.com/docs/getting-started/installation/docker/
- AzuraCast Settings / Environment Variables:
  - https://www.azuracast.com/docs/getting-started/settings/
- AzuraCast Optimizing:
  - https://www.azuracast.com/docs/help/optimizing/

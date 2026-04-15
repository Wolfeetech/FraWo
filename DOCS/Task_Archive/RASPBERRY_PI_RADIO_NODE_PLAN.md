# Raspberry Pi Radio Node Plan

## Zweck

Dieses Dokument beschreibt den professionelle Zielpfad fuer den spaeteren `Raspberry Pi 4` als dedizierten internen Radio-Node mit `AzuraCast`.

## Zielbild

- Rolle: `radio-node`
- Hardware: `Raspberry Pi 4`
- Primardienst: `AzuraCast`
- Betriebsmodus: intern zuerst, spaeter optional Public Edge
- Standort im Netz: LAN an Easy Box heute, spaeter unveraendert hinter `UCG-Ultra`

## Architekturentscheidungen

1. `AzuraCast` laeuft nicht als strategischer Dauerdienst auf `CT 100`, sondern auf dem dedizierten Pi.
2. Ziel-OS ist `Ubuntu Server 22.04.5 LTS ARM64` fuer Raspberry Pi.
3. Startmedium ist die vorhandene `32 GB` SD-Karte; fuer laengeren Dauerbetrieb bleibt `USB-SSD preferred`.
4. Der Pi ist ein dedizierter Radio-Node, kein allgemeiner Docker-Sammelhost.
5. Die Musikbasis kommt zunaechst vom direkt am Pi steckenden USB-Medium und spaeter optional von einem zentralen Medienpfad:
   - aktueller Live-Pfad: USB-Medium `76E8-CACF` unter `/srv/radio-library/music-usb/yourparty.radio`
   - `RadioLibrary` = kuratierter Songbestand fuer AzuraCast
   - `RadioAssets` = Jingles, IDs, vorbereitete Sendungen
6. `Jellyfin` oder `Plex` teilen sich spaeter nur die Dateibasis, nicht die AzuraCast-Logik.
7. Kein oeffentlicher Stream-Rollout, solange Domain, Edge und TLS nicht sauber stehen.

## OS- und Bootstrap-Standard

- Image: `ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz`
- SSH bei Erststart aktivieren
- Hostname-Ziel: `radio-node`
- Tailscale-Client frueh mitziehen
- feste DHCP-Reservierung vor produktivem Einsatz
- Basishaertung:
  - automatische Security-Updates
  - Zeitsync
  - kein unnoetiger lokaler Webserver
  - nur benoetigte Docker- und AzuraCast-Komponenten

## Betriebsstandard

- Internes Ziel:
  - `radio.hs27.internal`
- Fernzugriff:
  - primaer Tailscale
  - kein offener Admin-Zugang ins Internet
- Storage:
  - lokales OS auf SD/SSD
  - aktueller Musikbestand ueber direktes USB-Medium am Pi
  - spaeter optional dedizierter Netz-Mount statt lokaler USB-Quelle
- Update-Strategie:
  - dokumentierter Docker-/Compose-Pfad
  - vor groesseren AzuraCast-Aenderungen Backup des Host-Configs

## Integrationsreihenfolge

1. SD-Karte flashen
2. direkt danach den vorbereiteten First-Boot-Seed auf die Boot-Partition schreiben
3. Pi booten und LAN-IP sowie MAC erfassen
4. den vorbereiteten Remote-Bootstrap laufen lassen
5. DHCP-Reservierung setzen
6. Tailscale joinen
7. Medienquellen festziehen
8. AzuraCast intern deployen
9. `radio.hs27.internal` intern auf den Pi umschalten
10. erste Station anlegen und das Low-Ressource-Profil anwenden
11. USB- oder Netz-Musikquelle in die Station integrieren und echten Sendebetrieb pruefen
12. Public Radio spaeter nur ueber die Public-Edge-Phase

## Acceptance

- Pi ist per SSH und Tailscale stabil erreichbar
- Hostname und feste IP sind dokumentiert
- AzuraCast startet reproduzierbar
- `radio.hs27.internal` liefert intern erfolgreich und zeigt jetzt auf die AzuraCast-Login-Seite
- die erste Station spielt intern verifizierbar Audio
- kein oeffentlich erreichbares Admin-UI

## Aktueller Vorbereitungsstand

- Raspberry-Pi-Image liegt lokal vor und ist verifiziert
- Zielmedium `/dev/mmcblk0` ist identifiziert
- First-Boot-Seed fuer `radio-node` ist jetzt vorbereitet:
  - Hostname `radio-node`
  - Admin-User `wolf`
  - SSH-Key des ZenBook-Operators
  - DHCP auf `eth0`
- der Seed ist auf der aktuell gesteckten SD-Karte bereits geschrieben
- Playbook `ansible/playbooks/bootstrap_raspberry_pi_radio.yml` ist jetzt der kanonische Post-Boot-Pfad
- erster Boot ist erfolgreich:
  - Hostname `radio-node`
  - aktuelle LAN-IP `192.168.2.155`
  - SSH erreichbar
  - `docker`, `tailscaled` und `sshd` laufen
  - `ansible`-Ping ist erfolgreich
- Tailscale ist jetzt vollstaendig joined und `Running`
- Low-resource Host-Prep fuer AzuraCast ist bereits umgesetzt:
  - `docker compose` ist verfuegbar
  - `2 GiB` Swapfile aktiv
  - `/srv/radio-library` und `/srv/radio-assets` existieren
  - Docker `userland-proxy` ist deaktiviert
  - offizielles AzuraCast-Utility-Script liegt unter `/var/azuracast/docker.sh`
  - Readiness-Check meldet jetzt `rpi_radio_ready_for_azuracast=yes`
- Low-resource Runtime-Tuning ist jetzt ebenfalls live:
  - `COMPOSE_HTTP_TIMEOUT=900`
  - `PHP_FPM_MAX_CHILDREN=2`
  - `NOW_PLAYING_DELAY_TIME=15`
  - `NOW_PLAYING_MAX_CONCURRENT_PROCESSES=1`
  - `ENABLE_WEB_UPDATER=false`
  - Ressourcenbudget verifiziert ueber `RPI_RESOURCE_ALLOCATION_PLAN.md`
- Hostseitiges Medienlayout ist jetzt vorbereitet:
  - `RadioLibrary` unter `/srv/radio-library`
    - `incoming`
    - `music`
    - `playlists`
  - `RadioAssets` unter `/srv/radio-assets`
    - `ids`
    - `jingles`
    - `shows`
    - `staging`
    - `sweepers`
  - README-Dateien auf dem Pi dokumentieren die Betriebsregel und den spaeteren Netz-Mount-Pfad
- AzuraCast ist jetzt intern deployed:
  - Container `azuracast` und `azuracast_updater` laufen
  - direkter Pi-Check liefert `HTTP 302` auf `/login`
  - die Status-API liefert `HTTP 200`
  - `radio.hs27.internal` ist ueber die Toolbox jetzt auf den Pi umgeschaltet
  - die erste Station `FraWo - Funk` mit Shortcode `frawo-funk` ist jetzt angelegt
  - der aktuelle Song wird ueber `GET /api/nowplaying` geliefert
- direkt angeschlossene USB-Musikquelle ist jetzt integriert:
  - USB-Dateisystem `exfat`
  - UUID `76E8-CACF`
  - Mountpoint `/srv/radio-library/music-usb`
  - Quellordner `/srv/radio-library/music-usb/yourparty.radio`
  - Rollendatei unter `/srv/radio-library/music-usb/README_FRAWO_LIBRARY_ROLE.txt`
  - Host- und Container-Sicht sehen aktuell `2120` Dateien
  - `station_media` und `station_playlist_media` werden jetzt aus dieser Quelle befuellt
  - der aktuelle Arbeitsstand ist `internal_live_with_usb_music`, nicht `public_ready`

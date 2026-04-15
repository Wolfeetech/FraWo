# Shared Storage Architecture Plan

## Ziel

Eine zentrale Dateibasis fuer Dokumente und Medien. Keine dauerhafte Parallelhaltung mehr zwischen Pi, Toolbox, Nextcloud und Paperless.

## Verbindlicher Standard

- Storage-Node: `CT 110 storage-node`
- Host/IP: `192.168.2.30`
- Medien-Share: `\192.168.2.30\Media`
- kanonische Musikbibliothek: `\192.168.2.30\Media\yourparty_Libary`
- Dokumenten-Share: `\192.168.2.30\Documents`
- Protokoll-Standard fuer Clients: `SMB/CIFS`
- `NFS` bleibt optional fuer spaetere Linux-only Optimierungen, ist aber nicht mehr der Prim?rpfad fuer das Radiosystem.

## Warum SMB hier der richtige Prim?rpfad ist

- Windows-Clients brauchen einen nativen `UNC`-Pfad.
- AzuraCast auf dem Pi und Jellyfin auf der Toolbox koennen denselben Share per `CIFS` mounten.
- Der Storage-Node ist bereits live und die Shares sind angelegt.
- Damit gibt es einen klaren gemeinsamen Zielort statt USB-Zwischenpfad plus Toolbox-Bootstrap-Kopie.

## Zielbild je Dienst

### Jellyfin (`CT 100 toolbox`)
- nutzt wegen unprivilegiertem LXC keinen direkten Container-CIFS-Mount
- mountet `//192.168.2.30/Media` hostseitig auf Proxmox nach `/mnt/hs27-media`
- bindet diesen Host-Mount per `mp0` nach `/srv/media-library/music-network` in `CT 100` ein
- nutzt als kanonische Musikquelle `/srv/media-library/music-network/yourparty_Libary`
- beh?lt lokale Arbeitsverzeichnisse fuer `curated`, `favorites`, `inbox` und `quarantine`

### AzuraCast (`raspberry_pi_radio`)
- mountet `//192.168.2.30/Media` nach `/srv/radio-library/music-network`
- bindet `/srv/radio-library/music-network/yourparty_Libary` in die Station `frawo-funk`
- der alte USB-Pfad ist nur noch Legacy-Fallback, nicht mehr produktiver Zielpfad

### Nextcloud / Paperless
- nutzen `\192.168.2.30\Documents` als gemeinsamen Dokumentenpfad
- operative Migration bleibt ein eigener Schritt, aber die Zielarchitektur ist damit klar

## Verbindliche Ablagestruktur

### Media
- `\192.168.2.30\Media\yourparty_Libary\clean`
- `\192.168.2.30\Media\yourparty_Libary\curated`
- `\192.168.2.30\Media\yourparty_Libary\favorites`
- `\192.168.2.30\Media\yourparty_Libary\incoming`
- `\192.168.2.30\Media\yourparty_Libary\quarantine`

### Documents
- `\192.168.2.30\Documents\paperless-archive`
- `\192.168.2.30\Documents\nextcloud-drop`
- `\192.168.2.30\Documents\shared`

## Operativer Cutover

1. Storage-Node als kanonischen Dateipfad festziehen.
2. Toolbox auf hostseitigen SMB-Mount plus Bind-Mount umstellen.
3. Raspberry Pi auf SMB-Mount umstellen.
4. Jellyfin- und AzuraCast-Pfade gegen denselben Share pruefen.
5. Danach alte USB-/Bootstrap-/Rsync-Zwischenpfade aus dem produktiven Betrieb nehmen.

## Done-Kriterien

- `\192.168.2.30\Media\yourparty_Libary` ist les- und schreibbar
- Jellyfin sieht Dateien ueber den SMB-Mount
- AzuraCast sieht dieselben Dateien ueber den SMB-Mount
- `frawo-funk` importiert aus dem SMB-Pfad
- der produktive Betrieb haengt nicht mehr an `music-usb` oder `bootstrap-radio-usb`

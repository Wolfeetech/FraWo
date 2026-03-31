# Storage Node Operations

## Zweck

`CT 110 storage-node` ist die zentrale Source of Truth fuer gemeinsame Medien- und spaeter Dokumentenpfade.

## Zugriff

- IP: `192.168.2.30`
- SMB: `\\192.168.2.30\Media` und `\\192.168.2.30\Documents`
- kanonischer Musikpfad: `\\192.168.2.30\Media\yourparty_Libary`

## Normalbetrieb

- SMB bleibt der produktive Standardpfad
- Medien nicht wieder auf lokale USB-Zwischenpfade verteilen
- Schreibrechte nur bewusst erweitern
- direkter `SSH`-Zugang im Container bleibt bewusst deaktiviert
- `Samba` bindet nur noch an `127.0.0.1` und `192.168.2.30`

## T?gliche Checks

- Share erreichbar
- `yourparty_Libary` sichtbar
- Jellyfin und AzuraCast sehen denselben Bestand
- keine Read-Only- oder Dateisystemfehler

## Nie tun

- nicht wieder auf alte USB-Quellen zurueckfallen
- nicht als VM-Disk-Storage missbrauchen
- `SSH` im Container nicht wieder als Dauer-Managementpfad oeffnen
- `SMB` nicht wieder auf `0.0.0.0` oder globale IPv6 oeffnen

## Eskalation

- bei Mount- oder Sichtbarkeitsproblemen zuerst SMB, Mounts und Host-Bind-Mounts pr?fen

## Nachhaltiger Reapply-Pfad

- Repo-Reparatur und Drift-Korrektur laufen jetzt ueber:
  - `python scripts/apply_storage_node_network_baseline.py`
- der Reapply-Pfad schreibt `smb.conf`, startet `smbd/nmbd` neu und deaktiviert direkten `SSH` im Container wieder
- der aktuelle Re-Audit fuer direkte Public-Expositionen laeuft ueber:
  - `python scripts/public_ipv6_exposure_audit.py`

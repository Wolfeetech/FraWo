# Home Assistant Operations

## Zweck

Home Assistant ist die Hausautomationsplattform auf `VM 210`.

## Zugriff

- `http://ha.hs27.internal`
- intern auch `192.168.2.24:8123`

## Normalbetrieb

- stabil halten
- USB-Passthrough erst nach sauberem Hardware-Audit erweitern
- keine unkontrollierten Add-on-Experimente vor der Kernstabilitaet

## T?gliche Checks

- UI erreichbar
- Core healthy
- keine `io-error`-Folgen auf VM-Seite

## Nie tun

- keine Admin-Freigabe nach au?en
- keinen USB-Storage mit echten Zigbee/Z-Wave-Dongles verwechseln

## Eskalation

- bei UI-Problemen zuerst Proxmox-VM-Zustand und Storagepfad pr?fen

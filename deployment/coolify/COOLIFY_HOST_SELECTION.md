# Coolify Host Selection

## Ziel

Einen internen `Coolify`-Management-Host festlegen, ohne die Public-DMZ oder bestehende Business-Laufzeiten zu vermischen.

## Faktische Ausgangslage

- `toolbox` ist online, Tailscale-erreichbar und aktuell kein Kapazitaets-Hotspot
- `surface-go-frontend` ist derzeit nicht betriebsbereit
- `stock-pve` ist aktuell der Druckpunkt und kein guter v1-Controller-Kandidat
- `proxmox-anker` selbst ist Management-Hypervisor und kein sauberer Ort fuer den App-Controller

## Empfehlung v1

Der professionelle Zielpfad ist:

- **kein** `Coolify` direkt auf `proxmox-anker`
- **kein** `Coolify` direkt in der DMZ
- **kein** `Coolify` auf `stock-pve`
- **kein** `Coolify` auf `surface-go-frontend` solange dieser Knoten nicht sauber rebuilt ist

Empfohlene Reihenfolge:

1. spaeter einen **dedizierten internen Management-CT/VM auf Anker** bereitstellen
2. bis dahin `toolbox` nur als **temporären technischen Fallback** betrachten, nicht als Zielarchitektur

## Warum nicht sofort toolbox als Zielarchitektur

`toolbox` ist aktuell schon:

- Tailscale-Subnet-Router
- Frontdoor-Knoten
- DNS-/Proxy-Kontrollpunkt
- UCG-Uebergangshost

Ein zusaetzlicher `Coolify`-Controller darauf waere als Notbehelf machbar, aber nicht die sauberste Endform.

## Gated Stop

Die echte Host-Festlegung bleibt `gated_infra`, weil sie spaeter Laufzeit, SSH-Trust, Persistenz und Backup beruehrt.

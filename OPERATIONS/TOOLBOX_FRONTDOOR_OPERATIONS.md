# Toolbox Frontdoor Operations

## Zweck

`CT 100 toolbox` ist der interne Frontdoor fuer Caddy, AdGuard, Portal und mobile Tailscale-Proxy-Pfade.

## Zugriff

- Portal: `http://portal.hs27.internal`
- Caddy/Frontdoor intern: `192.168.2.20`
- AdGuard Admin: nur lokal auf `127.0.0.1:3000`

## Normalbetrieb

- interne Domains und Proxies stabil halten
- AdGuard nicht unkoordiniert als globalen DNS scharf schalten
- mobile Tailscale-Ports nur kontrolliert erweitern

## T?gliche Checks

- `portal.hs27.internal` antwortet
- `cloud.hs27.internal`, `paperless.hs27.internal`, `odoo.hs27.internal`, `ha.hs27.internal` routen sauber
- AdGuard Admin bleibt lokal-only
- Tailscale-Frontdoor antwortet nur auf den freigegebenen Ports

## Nie tun

- keine Adminpfade ?ffentlich exponieren
- keine wilden DNS-Umschaltungen mitten im Arbeitstag

## Eskalation

- bei Erreichbarkeitsproblemen zuerst Caddy, DNS und Tailscale pr?fen, nicht direkt die App selbst verd?chtigen

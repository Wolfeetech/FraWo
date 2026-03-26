# Vaultwarden Internal HTTPS Rollout

Stand: `2026-03-26`

## Ziel

`Vaultwarden` soll intern sauber unter:

- `https://vault.hs27.internal`

laufen, ohne die Plattform oeffentlich freizugeben.

## Was bereits vorbereitet ist

- Repo-Konfiguration fuer `vault.hs27.internal` ist angepasst
- Ziel-Proxy:
  - `192.168.2.20` -> `192.168.2.26:8080`
- Zieltechnik:
  - `Caddy` mit `tls internal`
  - `AdGuard` Rewrite fuer `vault.hs27.internal`

## Aktueller Blocker

- Live-Deploy auf `CT100 toolbox` kann von diesem PC aus gerade nicht automatisch ausgefuehrt werden
- deshalb braucht es einen kurzen manuellen Root-Run auf `toolbox`

## Direkter manueller Rollout auf CT100

Auf `CT100 toolbox` als `root` ausfuehren:

```bash
python3 - <<'PY'
from pathlib import Path

caddy = Path('/opt/homeserver2027/stacks/toolbox-network/Caddyfile')
cfg = caddy.read_text()
block = """
https://vault.hs27.internal {
  tls internal
  reverse_proxy 192.168.2.26:8080
}
"""
if 'https://vault.hs27.internal' not in cfg:
    if not cfg.endswith('\n'):
        cfg += '\n'
    cfg += '\n' + block.strip() + '\n'
    caddy.write_text(cfg)

adguard = Path('/opt/homeserver2027/stacks/toolbox-network/adguard/conf/AdGuardHome.yaml')
text = adguard.read_text()
needle = "  - domain: vault.hs27.internal\n    answer: 192.168.2.20\n"
if 'domain: vault.hs27.internal' not in text:
    marker = "  - domain: radio.hs27.internal\n    answer: 192.168.2.20\n"
    if marker in text:
        text = text.replace(marker, marker + needle)
        adguard.write_text(text)
PY

systemctl restart homeserver-compose-toolbox-network.service
sleep 5
curl -kI https://vault.hs27.internal
curl -fsS http://192.168.2.26:8080/alive
```

## Erwartetes Ergebnis

- `curl -kI https://vault.hs27.internal` liefert `200`
- `curl -fsS http://192.168.2.26:8080/alive` liefert `OK`

## Danach

### Browser-Test

- `https://vault.hs27.internal`

### Wichtig

- Beim ersten Aufruf ist das Zertifikat intern ausgestellt
- je nach Geraet muss die interne CA bewusst vertraut werden

## Definition Of Done

- `vault.hs27.internal` loest intern auf `192.168.2.20`
- `Caddy` proxyt intern per `HTTPS`
- `Vaultwarden` ist ueber `https://vault.hs27.internal` erreichbar
- danach kann der erste produktive Benutzer angelegt werden

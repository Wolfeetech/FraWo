# Vaultwarden Internal HTTPS Rollout

Stand: `2026-03-26`

## Ziel

`Vaultwarden` soll intern sauber unter `https://vault.hs27.internal` laufen, ohne die Plattform oeffentlich freizugeben.

## Status

- Rollout ist intern aktiv.
- Verifiziert am `2026-03-26`:
  - `curl -kI https://vault.hs27.internal` -> `HTTP 200`
  - `curl -fsS http://192.168.2.26:8080/alive` -> erfolgreiche Antwort

## Ergebnis

- `vault.hs27.internal` loest intern sauber auf die Toolbox-Frontdoor
- `Caddy` liefert internes `HTTPS`
- `Vaultwarden` ist produktiv ueber `HTTPS` erreichbar
- der erste produktive Benutzer kann darueber arbeiten

## Betriebsnotizen

- Das Zertifikat ist intern ausgestellt (`tls internal`).
- Auf PCs/Laptops muss die interne Caddy Root-CA dem Trust-Store hinzugefügt werden, oder der Browser warnt.
- **Mobile App Blocker**: Die iOS/Android Vaultwarden-App erlaubt *keine* unsicheren Verbindungen und *keine* self-signed Zertifikate (Fehler: "Zertifikat des Servers nicht verifizierbar"). 
- **Lösungspfad**: Um Mobile Apps nutzbar zu machen, muss Vaultwarden final von `vault.hs27.internal` auf das offizielle, öffentliche `safe.frawo-tech.de` umziehen und Caddy muss mittels Strato/IONOS API Keys ein offizielles "Let's Encrypt" Zertifikat ausstellen.
- Der nackte HTTP-Pfad `http://192.168.2.26:8080` (bzw. nun `10.1.0.26`) bleibt nur Bootstrap-/Health-Endpunkt.

## Wenn neu ausgerollt werden muss

Auf `CT100 toolbox` als `root`:

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

## Definition Of Done

- `vault.hs27.internal` liefert intern `HTTPS`
- `Vaultwarden` ist ueber `HTTPS` erreichbar
- produktive Vaultwarden-Nutzung laeuft nicht mehr ueber den nackten HTTP-Pfad

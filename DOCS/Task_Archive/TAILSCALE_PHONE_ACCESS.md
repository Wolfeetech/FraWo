# Tailscale Phone Access Runbook

## Ziel

Dieses Runbook beschreibt den echten Zugriffsweg vom Smartphone auf die Homeserver-Services. Es trennt bewusst zwischen:

- funktionierendem Tailscale-Transport
- noch nicht abgeschlossener Tailnet-Freigabe
- optionalem Komfort-DNS ueber `hs27.internal`

## Aktueller Ist-Stand

- `CT 100 toolbox` ist im Tailnet online.
- Tailscale-Backend-State ist `Running`.
- Toolbox-Tailscale-IP: `100.99.206.128`
- MagicDNS-Name der Toolbox: `toolbox.tail150400.ts.net`
- Die Toolbox annonciert lokal die Subnet-Route `192.168.2.0/24`.
- Diese Route ist in der Tailnet-Netzsicht derzeit noch nicht als aktive Subnet-Route sichtbar.

Das bedeutet:
- Tailscale selbst laeuft.
- Der Subnet-Router ist lokal vorbereitet.
- Der Restblocker fuer Handy-Zugriff per LAN-IP ist die Tailnet-seitige Freigabe der Route.

## Warum Handy-Zugriff bisher hakt

Es gibt zwei getrennte Ebenen:

1. Transport:
   - Das Handy braucht eine aktive Tailscale-Verbindung im selben Tailnet.
   - Die Route `192.168.2.0/24` muss im Tailscale-Admin fuer `toolbox` freigegeben sein.

2. DNS:
   - `ha.hs27.internal`, `odoo.hs27.internal` und die anderen internen Namen werden aktuell von AdGuard auf `CT 100` aufgeloest.
   - Diese Namen funktionieren nicht automatisch auf dem Handy, nur weil Tailscale verbunden ist.
   - Dafuer braucht es spaeter eine Tailnet-DNS- oder Split-DNS-Konfiguration.

## Was heute schon der richtige Zielpfad ist

### Minimaler und robuster Handy-Zugriff

Es gibt jetzt zwei moegliche mobile Zugriffspfade.

#### Pfad A - direkt ueber Tailscale-Frontdoor der Toolbox

Dieser Pfad braucht keine aktive Subnet-Route. Das Handy spricht nur mit der Toolbox als Tailscale-Node, und die Toolbox proxyt intern weiter.

- Home Assistant: `http://100.99.206.128:8443`
- Odoo: `http://100.99.206.128:8444/web/login`
- Nextcloud: `http://100.99.206.128:8445`
- Paperless: `http://100.99.206.128:8446/accounts/login/`
- Portal: `http://100.99.206.128:8447`
- Radio: `http://100.99.206.128:8448`

Wenn MagicDNS auf dem Handy sauber greift, gehen alternativ dieselben Ports auch ueber:

- `http://toolbox.tail150400.ts.net:8443`
- `http://toolbox.tail150400.ts.net:8444/web/login`
- `http://toolbox.tail150400.ts.net:8445`
- `http://toolbox.tail150400.ts.net:8446/accounts/login/`
- `http://toolbox.tail150400.ts.net:8447`
- `http://toolbox.tail150400.ts.net:8448`

#### Pfad B - direkter Zugriff auf die LAN-Zieladressen

Sobald die Subnet-Route freigegeben ist, funktioniert der Zugriff ohne DNS-Sonderlogik auch ueber die LAN-Zieladressen:

- Home Assistant: `http://192.168.2.24:8123`
- Odoo: `http://192.168.2.22:8069/web/login`
- Nextcloud: `http://192.168.2.21`
- Paperless: `http://192.168.2.23:8000`

Das ist der erste saubere Erfolgszustand fuer mobile Nutzung.

### Komfort-Zugriff mit internen Namen

Der schoene Pfad ist spaeter:

- `http://ha.hs27.internal`
- `http://odoo.hs27.internal`
- `http://cloud.hs27.internal`
- `http://paperless.hs27.internal`

Dafuer brauchen wir zusaetzlich:

- Tailnet-Split-DNS fuer `hs27.internal`
- AdGuard auf `CT 100` als Nameserver fuer diese Zone
- Tailnet-Clients duerfen DNS-Anfragen an AdGuard stellen

## Serverseitig bereits vorbereitet

- AdGuard ist jetzt fuer LAN plus Tailscale-Clientbereiche vorbereitet.
- Caddy beantwortet die internen Hostnamen bereits korrekt.
- Die Toolbox stellt jetzt zusaetzlich einen direkten mobilen Tailscale-Frontdoor ueber die Ports `8443` bis `8448` bereit.
- Diese Ports sind per Toolbox-Firewall vom LAN abgeschirmt und nur noch fuer Tailscale-Traffic gedacht.
- Die interne Proxy-Seite ist damit schon fuer den mobilen Interimszugriff bereit, auch wenn Route und Tailnet-DNS noch nicht fertig sind.

## Operative Reihenfolge

1. Handy mit Tailscale-App ins gleiche Tailnet bringen.
2. Soforttest ueber die Toolbox-Tailscale-Frontdoor auf `100.99.206.128:8443-8448`.
3. Im Tailscale-Admin die Route `192.168.2.0/24` fuer `toolbox` freigeben.
4. Danach direkten LAN-Zugriff testen.
5. Erst danach Tailnet-DNS fuer `hs27.internal` sauber nachziehen.

## Definition Of Done

Minimal fertig:
- Das Handy erreicht mindestens einen Dienst ueber die Toolbox-Tailscale-Frontdoor.

Komfort fertig:
- Das Handy erreicht `http://ha.hs27.internal` ueber Tailscale und Tailnet-DNS.

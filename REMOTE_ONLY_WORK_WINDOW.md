# Remote-Only Work Window

## Ziel

Dieses Runbook beschreibt, was waehrend einer reinen Remote-Session vom `ZenBook` ueber `AnyDesk` und `Tailscale` sinnvoll erledigt werden kann, ohne physisch am Homeserver-Standort zu sein.

Der Fokus ist bewusst auf:

- Arbeiten ohne Hardware-Anfassen
- Arbeiten ohne SD-/USB-Flash-Schritte
- Arbeiten ohne Clean-Rebuild am Surface
- saubere Remote-Reihenfolge statt zufaelligem Springen zwischen Baustellen

## Aktueller Remote-Only-Befund

Stand der verifizierten Remote-Basis:

- der `ZenBook` ist im richtigen Tailnet
- `AnyDesk` ist aktiv und taugt als GUI-Fallback
- der mobile Tailscale-Frontdoor der Toolbox funktioniert
- die `Surface`-ISO ist inzwischen komplett und SHA-verifiziert vorbereitet
- der AdGuard-Pilotpfad ist vorbereitet und kann spaeter clientweise aktiviert werden
- die Kerninfrastruktur ist intern gesund
- `PBS` bleibt blockiert, solange kein separates Backup-Storage physisch bereitsteht
- `Surface Go` bleibt blockiert, solange kein physischer Clean Rebuild gestartet wird
- der `Raspberry Pi` ist inzwischen remote uebernehmbar und als Radio-Node in den internen Stack eingebunden

## Was bis 15:00 remote machbar ist

### Sofort und ohne Service-Risiko

1. Gesundheits- und Sicherheitschecks laufen lassen:
   - `make start-day`
   - `make zenbook-remote-check`
   - `make remote-only-check`
2. Tailscale-Admin im Browser pflegen:
   - Subnet-Route fuer `toolbox` approven
   - Tailnet-/DNS-Zustand pruefen
3. Handy-Tailscale von ausserhalb testen:
   - nur Mobilfunk
   - Tailscale `Connected`
   - Tests auf `100.99.206.128:8447`, `:8448`, `:8443`, `:8444/web/login`
4. Tailscale-Split-DNS fuer `hs27.internal` vorbereiten oder setzen:
   - zuerst die `toolbox`-Route `192.168.2.0/24` approven
   - danach den Nameserver `192.168.2.20` in Tailscale nur fuer `hs27.internal` hinterlegen
5. Easy-Box-Leases manuell mit dem Inventar abgleichen:
   - davor read-only pruefen mit `make easybox-browser-probe`
   - Login auf `https://192.168.2.1`
   - offene Router-Namen gegen `NETWORK_INVENTORY.md` aufloesen
6. Planungs- und Dokumentationsarbeit:
   - DNS-Pilotpfad fuer AdGuard
   - Public-Edge-Vorplanung
   - Gateway-Cutover-Voraussetzungen weiter schaerfen
7. Radio-Node im normalen Betriebsfenster weiterpflegen:
   - `make rpi-radio-integration-check`
   - `make rpi-resource-check`

### Remote moeglich, aber nur im Wartungsfenster

1. `VM 200` und `VM 220` right-sizen
   - technisch remote machbar
   - verursacht Neustarts und braucht Nachtests
2. groessere Toolbox-/Caddy-/AdGuard-Aenderungen
   - nur mit sofortigen Checks danach

### Nicht remote loesbar

1. PBS produktiv bauen
   - physisches separates Storage fehlt
2. Surface Go produktiv machen
   - Clean Rebuild und lokaler Erststart sind physisch
3. HAOS-USB-Passthrough finalisieren
   - USB-Hardware ist nicht angesteckt

## Empfohlene Remote-Reihenfolge

Wenn du vom Arbeitsplatz aus auf dem ZenBook per AnyDesk sitzt, ist dies die saubere Reihenfolge:

1. Baseline pruefen
   - `make start-day`
   - `make zenbook-remote-check`
   - `make remote-only-check`
2. Tailscale fertigziehen
   - `toolbox`-Route `192.168.2.0/24` im Tailnet approven
   - danach Split-DNS fuer `hs27.internal` setzen
   - danach Handy- und Direktpfad pruefen
3. Easy-Box-Leases abgleichen
   - offene Clients identifizieren
   - `NETWORK_INVENTORY.md` danach aktualisieren
4. Installationsmedien nur noch verifizieren, nicht mehr laden
   - `make remote-only-check`
5. Radio-Node weiter in den Regelbetrieb ziehen
   - `make rpi-radio-integration-check`
   - danach Medienpfade und Stations-Feinschliff
6. Optionales Wartungsfenster nur wenn bewusst gewollt
   - `make rightsize-plan`
   - danach erst `make rightsize-apply`

## Genaue Umsetzungsanweisungen

### 1. Remote-Basis verifizieren

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make start-day
make zenbook-remote-check
make remote-only-check
```

Erwartung:

- `tailscale_joined=yes`
- `anydesk_service=active`
- Business-Stacks gesund
- `toolbox_mobile_frontdoor_ready=yes`

### 2. Tailscale-Subnet-Route approven

1. Im Browser `https://login.tailscale.com/admin/machines` oeffnen.
2. Im Tailnet `w.prinz1101@gmail.com` bleiben.
3. Node `toolbox` oeffnen.
4. Unter `Subnets` oder `Routing Settings` die Route `192.168.2.0/24` approven.
5. Danach lokal pruefen:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make toolbox-tailscale-check
```

Erwartung:

- `tailnet_route_visible=yes`

### 3. Split-DNS fuer `hs27.internal` in Tailscale vorbereiten

Voraussetzung:

- `make toolbox-tailscale-check` zeigt `tailnet_route_visible=yes`

Dann in Tailscale Admin:

1. `DNS` oder `Nameservers` im Tailnet oeffnen.
2. Einen eingeschraenkten Nameserver fuer `hs27.internal` anlegen.
3. Als Nameserver `192.168.2.20` verwenden.
4. Nur den Domain-Scope `hs27.internal` setzen, nicht global.
5. Danach pruefen:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make tailscale-split-dns-check
```

Erwartung:

- `split_dns_prereqs_ready=yes`

### 4. Handy-Off-LAN-Test

1. Am Handy WLAN ausschalten.
2. Tailscale-App offen lassen und `Connected` pruefen.
3. Dann im Browser testen:
   - `http://100.99.206.128:8447`
   - `http://100.99.206.128:8443`
   - `http://100.99.206.128:8444/web/login`
4. Wenn die Subnet-Route approved ist, danach auch testen:
   - `http://192.168.2.24:8123`

### 5. Easy-Box-Leases manuell abgleichen

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make easybox-browser-probe
make inventory-resolution-check
```

Erwartung:

- `browser_probe_ready=yes`
- `login_page_title=Vodafone EasyBox 805`
- `inventory_resolution_ready=no`, solange noch Restlabels offen sind

1. Auf dem ZenBook im Browser `https://192.168.2.1` oeffnen.
2. Mit dem bekannten Easy-Box-Zugang einloggen.
3. Lease-/DHCP-Ansicht oeffnen.
4. Gegen `NETWORK_INVENTORY.md` abgleichen:
   - `fireTV`
   - `Franz_iphone`
   - `udhcpc1.21.1`
   - `udhcp 1.24.1`
   - offene `.141-.144`
5. Danach die bestaetigten Zuordnungen in `NETWORK_INVENTORY.md` uebernehmen.

### 6. Surface-ISO nur noch verifizieren

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make surface-iso-fetch
```

Erwartung:

- das Skript meldet, dass die Datei bereits vollstaendig ist
- am Ende `sha256 ok`

### 7. Right-Sizing nur im bewussten Wartungsfenster

Vorher:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make rightsize-stage-gate
make rightsize-plan
```

Live-Umsetzung nur bewusst:

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make rightsize-apply
make business-drift-check
make toolbox-network-check
```

## Definition of Done fuer ein erfolgreiches Remote-Fenster

Minimal erfolgreich:

- `make remote-only-check` ist im erwarteten Zustand
- Tailscale- und AnyDesk-Zugang sind verifiziert
- mindestens ein offener Browser-/Phone-/Lease-Block ist geschlossen

Stark erfolgreich:

- `toolbox`-Subnet-Route ist approved
- `make tailscale-split-dns-check` ist gruen
- Handy-Off-LAN-Test ist bestaetigt
- Lease-Abgleich ist weiter reduziert
- Surface-ISO ist verifiziert

## Harte Stoppbedingungen

Nicht weitermachen mit veraendernden Arbeiten, wenn:

- `make start-day` rot ist
- `make security-baseline-check` rot ist
- `make business-drift-check` rot ist
- `make remote-only-check` zeigt, dass die Remote-Basis selbst bruechig ist
- ein Schritt physischen Zugriff erfordert

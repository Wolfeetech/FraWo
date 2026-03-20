# AdGuard Pilot Rollout Plan

## Ziel

Dieses Dokument beschreibt den professionelle Einfuehrungspfad fuer `AdGuard Home` auf `CT 100`, solange die Easy Box noch der aktive DHCP- und Router-Endpunkt ist.

Der Schwerpunkt ist bewusst:

- zuerst direkter DNS-Test
- dann begrenzter Pilot auf einzelnen Clients
- erst spaeter DHCP-/LAN-Promotion
- jederzeit klarer Rollback

## Aktueller Ist-Stand

- `AdGuard Home` laeuft auf `192.168.2.20:53`
- die Admin-Oberflaeche ist nur lokal auf `127.0.0.1:3000` verfuegbar
- `hs27.internal`-Rewrites liefern auf `192.168.2.20`
- erlaubte Clientbereiche enthalten bereits:
  - `192.168.2.0/24`
  - `100.64.0.0/10`
  - `fd7a:115c:a1e0::/48`
- `toolbox` ist damit DNS-seitig bereit fuer LAN-Piloten und spaeter fuer Tailnet-Split-DNS

## Pilot-Reihenfolge

### Stage A - Read-only Direktqueries

Noch keine System-DNS-Aenderung auf dem Client.

Ziel:

- pruefen, ob AdGuard korrekt antwortet
- Rewrites testen
- Rollback-Risiko null halten

### Stage B - Einzelclient-Pilot

Erster Pilotclient:

- `wolf-ZenBook-UX325EA-UX325EA`

Warum:

- administrativer Hauptclient
- Tailscale und AnyDesk bereits stabil
- Fehlerbild schnell sichtbar
- Rollback sofort moeglich

Zweiter Pilotclient spaeter:

- `Wolf_Pixel`

Nur nach bestaetigtem Tailscale-/Handy-Test.

### Stage C - Verifizierter Trusted-Client-Pilot

Erst wenn Stage B stabil ist:

- zweites Bewohnergeraet
- evtl. Surface nach Clean Rebuild

### Stage D - DHCP-Promotion

Ausdruecklich spaeter:

- erst nach finalem Lease-Abgleich
- erst nach dokumentiertem Rollback
- erst nach stabiler Pilotphase

## Remote-Safe Testpfad

### 1. Readiness pruefen

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make adguard-pilot-check
```

Erwartung:

- `adguard_port53_ready=yes`
- `adguard_admin_lan_surface=no`
- `adguard_rewrite_ha=yes`
- `adguard_rewrite_portal=yes`
- `adguard_pilot_ready=yes`

### 2. Direkte DNS-Queries ohne Client-Umstellung

```bash
dig +short @192.168.2.20 portal.hs27.internal
dig +short @192.168.2.20 ha.hs27.internal
dig +short @192.168.2.20 cloud.hs27.internal
```

Erwartung:

- jeweils `192.168.2.20`

### 3. HTTP-Pfad weiter pruefen

```bash
curl -I http://portal.hs27.internal
curl -I http://ha.hs27.internal
```

## Einzelclient-Pilot auf dem ZenBook

Nur wenn Stage A gruen ist.

### Vorher aktive Verbindung ermitteln

```bash
nmcli connection show --active
```

Beispielhaft nennen wir sie hier `${ACTIVE_CONN}`.

### Pilot-DNS setzen

```bash
ACTIVE_CONN="HIER-DEN-AKTIVEN-NAMEN-EINTRAGEN"
nmcli connection modify "${ACTIVE_CONN}" ipv4.ignore-auto-dns yes ipv4.dns "192.168.2.20 1.1.1.1" ipv4.dns-search "hs27.internal"
nmcli connection up "${ACTIVE_CONN}"
```

### Pilot pruefen

```bash
resolvectl status | sed -n '1,120p'
getent ahostsv4 ha.hs27.internal
getent ahostsv4 portal.hs27.internal
curl -I http://ha.hs27.internal
curl -I http://portal.hs27.internal
```

## Rollback fuer den ZenBook

Wenn der Pilotclient merkwuerdig reagiert oder DNS unklar wird:

```bash
ACTIVE_CONN="HIER-DEN-AKTIVEN-NAMEN-EINTRAGEN"
nmcli connection modify "${ACTIVE_CONN}" ipv4.ignore-auto-dns no ipv4.dns "" ipv4.dns-search ""
nmcli connection up "${ACTIVE_CONN}"
```

Danach pruefen:

```bash
resolvectl status | sed -n '1,120p'
```

## Nicht jetzt tun

- AdGuard als DHCP-seitigen LAN-Default-DNS fuer alle Clients ausrollen
- IoT-Geraete blind umhaengen
- Public DNS / Domain / TLS mit diesem Pilot vermischen
- Admin-Oberflaeche im LAN freischalten

## Definition of Done

Minimal fertig:

- `make adguard-pilot-check` ist gruen
- Read-only Direktqueries funktionieren
- Rollback fuer den ZenBook ist dokumentiert

Pilot fertig:

- ZenBook laeuft mit AdGuard als DNS
- `hs27.internal` funktioniert dort reproduzierbar
- Rollback wurde verstanden und ist sofort moeglich

LAN-Promotion fertig:

- Lease-Abgleich abgeschlossen
- Pilotphase stabil
- DHCP-/Rollback-Pfad dokumentiert

# Tailscale Split DNS Plan

## Ziel

Dieses Dokument beschreibt den sauberen Zielpfad, damit `hs27.internal` nicht nur im LAN, sondern auch auf Tailscale-Clients komfortabel aufgeloest wird.

## Naming-Entscheidung

- Aktive Betriebszone bleibt vorerst `hs27.internal`.
- Spaeterer professioneller Zielpfad fuer interne Namen ist `frawo.home.arpa`.
- `frawo.internal` und `frawo.lan` werden nicht als neue Standardzone eingefuehrt.
- Solange keine geplante Migration vorbereitet und getestet ist, bleibt Split-DNS ausschliesslich auf `hs27.internal`.

Zielbild:

- `MagicDNS` bleibt fuer Tailnet-Nodes aktiv
- `hs27.internal` wird als `restricted nameserver` bzw. `split DNS` ueber Tailscale eingefuehrt
- `AdGuard Home` auf `toolbox` wird fuer Tailscale-Clients ueber `100.82.26.53` als Nameserver nur fuer `hs27.internal` angesprochen
- die eigentlichen Service-Antworten fuer `hs27.internal` bleiben auf der Toolbox-LAN-IP `10.1.0.20`
- andere DNS-Anfragen bleiben ausserhalb dieses Splits unberuehrt

## Aktueller Ist-Stand

- `MagicDNS` ist im Tailnet aktiv
- der ZenBook akzeptiert Tailscale-DNS (`CorpDNS=true`)
- `toolbox.tail150400.ts.net` ist ueber `100.100.100.100` aufloesbar
- CT 100 (toolbox) ist nach Netz-Migration jetzt auf `10.4.0.20` (frueherer Stand: `10.1.0.20`)
- der restricted nameserver fuer `hs27.internal` zeigt noch auf die alte IP `10.1.0.20` und muss auf `10.4.0.20` (oder Tailscale-IP `100.82.26.53`) aktualisiert werden
- Route `10.4.0.0/24` muss im Tailscale-Admin approved sein, damit Remote-Clients `10.4.0.20` (AdGuard) erreichen koennen
- Windows Hosts-Datei Workaround (`scripts/tools/Update-HS27-DNS-Aliases.ps1`) ist solange aktiv

## Wichtige Regel

Der restricted Nameserver fuer `hs27.internal` sollte fuer entfernte Tailscale-Clients nicht auf die private LAN-IP `10.1.0.20` zeigen, sondern auf die Toolbox-Tailscale-IP `100.82.26.53`.

Praktisch hiess das fuer die Umsetzung:

- erst Route `10.1.0.0/24` approven
- dann Split-DNS in der Tailscale-Adminseite auf `100.82.26.53` setzen

Die Frontdoor-Antworten bleiben dabei weiter auf `10.1.0.20`, deshalb braucht der eigentliche Zugriff auf `portal`, `odoo`, `cloud` und die anderen internen Ziele nach wie vor die funktionierende Route `10.1.0.0/24`.

## Readiness Check

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make tailscale-split-dns-check
```

Erwartung fuer echte Umstellung:

- `magicdns_enabled=yes`
- `zenbook_accepts_tailscale_dns=yes`
- `adguard_pilot_ready=yes`
- `tailnet_route_visible=yes`
- `split_dns_prereqs_ready=yes`
- `magicdns_split_ha_resolves=yes`

## Exakte Admin-Schritte

Status: restricted nameserver zeigt noch auf alte IP `10.1.0.20`; muss auf `10.4.0.20` (CT 100 neue LAN-IP) aktualisiert werden.

### 1. Route zuerst

1. `https://login.tailscale.com/admin/machines`
2. Tailnet `w.prinz1101@gmail.com`
3. Node `toolbox` (oder PVE-Host)
4. Route `10.4.0.0/24` approven (frueheres Netz `10.1.0.0/24` obsolet)

### 2. DNS-Seite oeffnen

1. `https://login.tailscale.com/admin/dns`
2. `MagicDNS` eingeschaltet lassen

### 3. Restricted Nameserver fuer `hs27.internal` aktualisieren

1. Bestehenden Eintrag fuer `hs27.internal` entfernen (zeigt noch auf `10.1.0.20`)
2. `Add nameserver`
3. Custom nameserver `10.4.0.20` (CT 100 LAN-IP, AdGuard)
4. Restrict to domain `hs27.internal`
5. Speichern

Alternativ, wenn CT 100 eine Tailscale-IP hat (`100.82.26.53`): diese bevorzugen, da kein Subnet-Route-Dependency.

### 4. Kein globaler DNS-Cutover an dieser Stelle

Noch nicht tun:

- keinen globalen Nameserver fuer alles auf `10.4.0.20` setzen
- `Override DNS servers` nicht als blanket change einschalten, wenn nur `hs27.internal` gebraucht wird

Der saubere erste Schritt ist wirklich nur:

- `restricted nameserver`
- Domain `hs27.internal`
- Server `10.4.0.20` (oder Tailscale-IP falls verfuegbar)

## Validierung nach dem Admin-Schritt

### ZenBook

```bash
cd /home/wolf/.gemini/antigravity/brain/2c5853e0-5815-4be5-9475-dd2b9bd1e0f2
make tailscale-split-dns-check
resolvectl query ha.hs27.internal
resolvectl query portal.hs27.internal
curl -I http://ha.hs27.internal
curl -I http://portal.hs27.internal
```

### Handy

Nur nach bestaetigter Route:

- Tailscale `Connected`
- Browser:
  - `http://ha.hs27.internal`
  - `http://portal.hs27.internal`
  - `http://odoo.hs27.internal/web/login`

## Rollback

Wenn `hs27.internal` danach auf Clients merkwuerdig wird:

1. `https://login.tailscale.com/admin/dns`
2. den restricted nameserver fuer `hs27.internal` entfernen
3. speichern
4. danach erneut testen:

```bash
resolvectl query ha.hs27.internal
```

## Definition of Done

Minimal fertig:

- Route `10.4.0.0/24` approved
- restricted nameserver auf `10.4.0.20` (oder Tailscale-IP) gesetzt
- ZenBook loest `ha.hs27.internal` erfolgreich ueber Tailscale-DNS auf

Komfort fertig:

- Handy loest `ha.hs27.internal` ueber Tailscale erfolgreich auf
- `portal`, `ha`, `odoo`, `cloud`, `paperless` funktionieren ueber `hs27.internal`
- Windows Hosts-Datei Workaround (`Update-HS27-DNS-Aliases.ps1`) deaktiviert oder entfernt

## Quellen

- Tailscale DNS in Tailscale:
  - https://tailscale.com/kb/1054/dns/
- Tailscale MagicDNS:
  - https://tailscale.com/kb/1081/magicdns/
- Tailscale client DNS preferences:
  - https://tailscale.com/docs/features/client/manage-preferences

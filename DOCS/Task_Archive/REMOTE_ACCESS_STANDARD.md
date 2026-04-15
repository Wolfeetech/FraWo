# Remote Access Standard

## Ziel

Der Remote-Zugriff fuer Homeserver 2027 folgt einem klaren professionellen Standard:

- `Tailscale` ist der primaere administrative Fernzugang
- `AnyDesk` ist der GUI-Fallback auf dem `ZenBook`
- alte manuelle VPN-Profile wie `WireGuard` bleiben getrennt und werden nicht parallel aktiv betrieben
- wichtig: das lokale alte `StudioPC`-`WireGuard` ist nicht dasselbe wie ein spaeteres professionelles `Site-to-Site WireGuard` zwischen `UCG` und `Stockenweiler`

## Was "voll remote steuerbar" konkret heisst

Ein Geraet gilt erst dann als wirklich remote steuerbar, wenn der passende Fernzugriff fuer seine Rolle vorhanden ist:

1. Headless Infrastruktur:
   - `Tailscale`
   - `SSH`
   - idealerweise `Ansible`
2. Desktop-/Frontend-Geraete:
   - `Tailscale`
   - `SSH` fuer Admin-Aufgaben
   - genau ein GUI-Fallback wie `AnyDesk`
3. Appliance-/Router-Weboberflaechen:
   - Zugriff ueber `Tailscale` plus Browser
   - keine "vollstaendige Shell-Kontrolle" erwarten, nur dokumentierte Admin-Funktionen
4. Handys:
   - primaer Servicezugriff und Browser-Tests
   - nicht als Haupt-Admin-Knoten einplanen

Das ist der entscheidende Unterschied:

- `voll administrierbar` fuer Server bedeutet Shell + Automation
- `voll bedienbar` fuer Desktop-Geraete bedeutet Shell + GUI
- `erreichbar` allein reicht nicht

## Aktueller Stand

- `wolf-ZenBook-UX325EA-UX325EA`
  - ist im richtigen Tailnet `w.prinz1101@gmail.com`
  - Tailscale-IP: `100.76.249.126`
  - kann die Toolbox ueber den Tailscale-Frontdoor erreichen
  - `AnyDesk 8.0.0` ist installiert und aktiv
- Android-Handy:
  - Tailscale-Login ist erfolgreich bestaetigt
  - der eigentliche Off-LAN-Funktionstest bleibt noch als Operator-Test offen

## Aktuelle kanonische Adminpfade 2026-03-31

- `Anker`
  - primaer ueber direkte SSH-Aliase mit `~/.ssh/hs27_ops_ed25519`
- `Stockenweiler`
  - aktuell primaer ueber `ssh stock-pve`
  - realer Pfad: `StudioPC -> toolbox -> userspace WireGuard -> 192.168.178.25`
  - professioneller Tagesbetrieb bleibt aktuell `Tailscale first`
  - das lokale stale Windows-`WireGuard` auf `StudioPC` ist nur Altlast/Recovery, nicht Zielarchitektur
  - ein spaeteres professionelles `Site-to-Site WireGuard` zwischen `UCG` und `Stockenweiler` ist davon getrennt und bleibt ein eigener Infrastrukturpfad
- `StudioPC`
  - `Pyrefly`-Workspace-Language-Services sind fuer diesen Workspace deaktiviert, damit Editor-Spam nicht als Infrastrukturproblem verwechselt wird

## Standards

1. Server- und Admin-Zugriffe laufen primaer ueber Tailscale.
2. AnyDesk dient fuer Desktop-Arbeit auf dem ZenBook, nicht als Ersatz fuer saubere Server-Administration.
3. AnyDesk-ID und Passwort werden nicht im Workspace dokumentiert.
4. Auf Android darf immer nur ein VPN aktiv sein; ein altes WireGuard-Profil muss fuer Tailscale deaktiviert sein.
5. Die `100.x`-Tailscale-Endpunkte sind der erste Remote-Test, bevor direkte `192.168.2.x`-Ziele bewertet werden.
6. Jeder Linux-Knoten, den Codex/Gemini spaeter autonom betreiben soll, braucht einen stabilen `SSH`-Pfad.
7. Jeder GUI-Knoten, den Codex/Gemini spaeter auch optisch uebernehmen koennen soll, braucht zusaetzlich genau einen sauberen Remote-Desktop-Weg.
8. `ZenBook` ist der primaere menschliche Control-Plane-Client fuer Arbeit von ausserhalb.
9. `Surface Go` wird spaeter ein verwalteter Frontend-Knoten, aber nicht der Haupt-Admin-Knoten.
10. Router, HAOS und andere Appliances bleiben browser- oder serviceorientiert; dort ist nicht immer echte "vollstaendige Fernsteuerung" moeglich.

## Zielbild Pro Geraeteklasse

### ZenBook

- Rolle: Admin-Control-Plane
- Soll-Zugriff:
  - `Tailscale`
  - lokales Terminal
  - `Ansible`
  - `AnyDesk` als GUI-Fallback
- Zweck:
  - von hier aus sollen spaeter moeglichst alle anderen Linux-Knoten verwaltet werden

### Toolbox / Proxmox / Linux-Server / Raspberry Pi

- Rolle: Headless Infrastruktur
- Soll-Zugriff:
  - `Tailscale`
  - `SSH`
  - `Ansible`
- GUI-Fallback:
  - nicht noetig
- Ziel:
  - Codex/Gemini kann diese Knoten direkt ueber Shell und IaC warten

### Surface Go Frontend

- Rolle: Shared GUI-Frontend
- Soll-Zugriff:
  - `Tailscale`
  - `SSH`
  - `AnyDesk` nach dem Rebuild
- Ziel:
  - Remote-Admin per Shell
  - Remote-GUI fuer Kiosk-/Desktoppflege

### Handy

- Rolle: Endgeraet und Akzeptanztest
- Soll-Zugriff:
  - `Tailscale`
  - Browser
- Ziel:
  - Servicezugriff, Portal, Home Assistant, Odoo
  - kein Hauptweg fuer tiefere Admin-Arbeit

### Easy Box / spaeter UCG-Ultra

- Rolle: Netzwerk-Appliance
- Soll-Zugriff:
  - Browser ueber LAN oder Tailscale-Subnet-Pfad
- Ziel:
  - Konfigurationsaenderungen dokumentiert und kontrolliert
  - keine Bastel-Loesungen mit inoffizieller Dauerautomation als Primarweg

## Was Codex/Gemini dafuer braucht

Damit wir "von einem Geraet aus das andere komplett steuern" koennen, brauche ich fuer den jeweiligen Zielknoten:

- Netzwerkpfad:
  - `Tailscale` oder sauberer LAN-Zugriff
- Admin-Pfad:
  - `SSH` fuer Linux
  - Browser fuer Appliances
  - `AnyDesk` nur fuer echte GUI-Geraete
- Identitaet:
  - stabiler Hostname
  - feste IP oder zuverlaessige Namensaufloesung
- Betriebsstandard:
  - dokumentierte Rollen
  - kein Passwort-Chaos
  - keine unbekannten Parallelwege

Ohne `SSH` kann ich Linux-Knoten nicht sauber autonom pflegen.
Ohne GUI-Fallback kann ich Desktop-Gerate nicht vollstaendig optisch uebernehmen.
Ohne Tailscale oder gleichwertigen Pfad bleibt alles vom lokalen LAN abhaengig.

## Testmatrix

### ZenBook

- `tailscale status`
- `curl http://100.99.206.128:8447`
- `curl http://100.99.206.128:8443`
- `systemctl is-active anydesk`

### Handy

- WLAN aus
- Mobilfunk an
- Tailscale `Connected`
- Browser-Test:
  - `http://100.99.206.128:8447`
  - `http://100.99.206.128:8443`
  - `http://100.99.206.128:8444/web/login`

## Rollout-Reihenfolge Fuer Vollstaendige Fernsteuerung

1. `ZenBook` als Control Plane stabil halten
   - `Tailscale` aktiv
   - `AnyDesk` aktiv
   - Workspace und `Ansible` funktionsfaehig
2. Alle Linux-Infrastrukturknoten ueber `Tailscale` und `SSH` standardisieren
   - Toolbox
   - Proxmox
   - spaeter Raspberry Pi
   - spaeter Surface Go nach Rebuild
3. Split-DNS und interne Namen stabilisieren
   - `hs27.internal`
   - Portal / HA / Odoo / Nextcloud
4. Erst danach GUI-Fallbacks fuer echte Frontend-Geraete ausbauen
   - `Surface Go`
5. Appliances getrennt behandeln
   - Easy Box heute
   - spaeter `UCG-Ultra`

## Operator-Hinweise

- Wenn Tailscale und AnyDesk gleichzeitig verfuegbar sind, bleibt Tailscale der bevorzugte Weg.
- Wenn nur GUI-Zugriff gebraucht wird, ist AnyDesk okay.
- Wenn Serverwartung oder Diagnose anstehen, immer Tailscale zuerst.
- Wenn ein Geraet spaeter durch Codex/Gemini autonom betreut werden soll, ist `SSH` Pflicht und `GUI` optional.

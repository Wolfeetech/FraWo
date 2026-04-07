# User Onboarding Operations

Stand: `2026-03-30`

## Zweck

Diese Datei ist der kanonische Onboarding- und Benutzerbetriebsartikel fuer:

- `Wolf`
- `Franz`
- gemeinsame Geraete
- Franzs `Surface Laptop` und `iPhone`
- Wolfs `Arbeitssurface`

## Aktueller Betriebsstand

- `portal.hs27.internal/status.json` meldete zuletzt `7/7` gesunde Kerndienste
- `Vaultwarden` ist intern ueber `HTTPS` erreichbar
- `Franz` hat die `FraWo`-Einladung in `Vaultwarden` angenommen
- `portal.hs27.internal/franz/` ist live
- das Root-Portal und der Franz-Pfad sind jetzt bewusst auf den Betriebs-MVP reduziert
- Root-Portal und Franz-Seite sind sichtbar gegen den neuen MVP-Stand abgenommen (`2026-03-30`)
- `Nextcloud`, `Paperless`, `Odoo`, `Jellyfin`, `Radio` und `Home Assistant` antworten intern
- der TV-Pfad zu `Jellyfin` funktioniert wieder
- der letzte TV-Test lief ueber `Wolf`, nicht ueber `TV Wohnzimmer`

## Aktueller Lane-A-Restpunkt

Der offene Benutzerblock fuer den aktuellen Arbeits-MVP ist jetzt nur noch:

- `device_rollout_verified`

Pass-Bedingung dafuer:

- `Franz Surface Laptop` nutzt sichtbar `http://portal.hs27.internal/franz/` als alltagstauglichen Startpfad
- `Franz iPhone` nutzt sichtbar `http://100.99.206.128:8447/franz/` als mobilen Startpfad
- auf beiden Pfaden sind `Nextcloud`, `Paperless`, `Odoo` und `Vaultwarden` sichtbar als direkte Kernziele erreichbar
- es bleibt kein sichtbarer Blocker fuer den echten Alltagspfad uebrig

Danach:

- `python scripts/device_rollout_preflight.py`
- `powershell -ExecutionPolicy Bypass -File .\scripts\prove_device_rollout.ps1`
- anschliessend zieht Codex `release_mvp_gate.py` und `generate_ai_server_handoff.py` automatisch nach

## Standard-Einstieg

- Portal intern: `http://portal.hs27.internal`
- Franz intern: `http://portal.hs27.internal/franz/`
- Vaultwarden: `https://vault.hs27.internal`
- Vaultwarden-Referenzregister: `..\ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`

## Direkte Dienstpfade

- Nextcloud: `http://cloud.hs27.internal`
- Paperless: `http://paperless.hs27.internal`
- Odoo: `http://odoo.hs27.internal/web/login`
- Home Assistant: `http://ha.hs27.internal`
- Jellyfin LAN mit DNS: `http://media.hs27.internal`
- Jellyfin LAN ohne DNS: `http://192.168.2.20:8096`
- Jellyfin mobil: `http://100.99.206.128:8449`
- Radio: `http://radio.hs27.internal`

## Benutzerrollen

### Wolf

- Alltag:
  - `Nextcloud`
  - `Paperless`
  - `Odoo`
- Admin:
  - `Vaultwarden`
  - weitere Admin-UIs erst nach stabilem MVP

### Wolfs Arbeitssurface

- ist **nicht** dasselbe Geraet wie `Franz Surface Laptop`
- Router-/WLAN-Signal derzeit: `Surface_Laptop` auf `192.168.2.118`
- Rolle:
  - primaeres Arbeitsgeraet fuer Wolf
  - muss fuer `VT`- und Hauptarbeitskontext auch ohne dauerhaften VPN-Zwang brauchbar bleiben
- Zugriffsmodell:
  - Standardmodus:
    - normales WLAN-/Arbeitsgeraet
    - kein permanenter Volltunnel
    - keine blinde `RouteAll`-/Exit-Node-Pflicht
  - interner App-Modus:
    - `Tailscale` bei Bedarf aktiv
    - Zugriff auf `portal.hs27.internal`, `Nextcloud`, `Paperless`, `Odoo`, `Vaultwarden`, `Home Assistant`, `Radio`
  - Admin-/Vollzugriffsmodus:
    - nur bewusst bei Bedarf
    - fuer interne Adminpfade und spaetere Support-/Bridge-Arbeit
    - nicht als Dauerzustand fuer die Hauptarbeit
- Betriebsregel:
  - `Tailscale-first`, aber nur on-demand
  - das Geraet bleibt ein `trusted-client`, kein Kiosk und kein Sonder-Fernwartungsgeraet
  - keine Verwechslung mit dem Franz-Deploypfad oder dem `surface-go-frontend`

### Franz

- Alltag:
  - `Nextcloud`
  - `Paperless`
  - `Odoo`
  - `Vaultwarden` nur bei Login-Bedarf
- kein `Surface Go`-Kioskpfad
- persoenlicher Start ueber `portal.hs27.internal/franz/`
- `Franz` bleibt Anwender, nicht Mit-Admin
- der Standard ist portal-first und shortcut-first, nicht URL-Merkerei

### Spaetere Erweiterung Nach MVP

- `Jellyfin`
- `Radio`
- Shared `surface-go-frontend`
- spaetere Komfortpfade fuer TV und Wohnzimmer

## Reihenfolge Fuer Den Internen Benutzer-Deploy

1. `Vaultwarden`-Bestand fuer `Franz` sichtbar pruefen
2. Wolf-Logins komplett pruefen
3. Franz-Logins komplett pruefen
4. Franz-Geraete ohne Sonderkonfig abnehmen
5. erst danach Stresstest fuer den Arbeitskern
6. spaetere Shared-Geraete erst nach stabilem MVP wieder aufmachen
7. Wolfs `Arbeitssurface` nur als separates Split-Access-Geraet behandeln, nicht in den Franz- oder Kioskpfad hineinziehen

## Sichtpruefung In Vaultwarden

- `Nextcloud Admin`
- `Paperless Admin`
- `Odoo Admin`
- `AdGuard Admin`
- `AzuraCast Admin`
- `Jellyfin - TV Wohnzimmer`

Zusatz:

- `AdGuard Admin` auf `http://127.0.0.1:3000`

## Sichtbare Abnahme Fuer Diesen Block

### Wolf

- `Vaultwarden`
- `Portal`
- `Nextcloud`
- `Paperless`
- `Odoo`

### Franz

- `FraWo`
- `Vaultwarden`
- `Nextcloud`
- `Paperless`
- `Odoo`
- `portal.hs27.internal/franz/`

### Spaeterer Ausbau

- `surface-go-frontend`
- `TV Wohnzimmer`
- `Jellyfin`
- `Radio`
- `Home Assistant`

## Franz Geraete-Deploy

### Surface Laptop

- Hauptpfad: `http://portal.hs27.internal/franz/`
- Shortcuts ausrollen mit:
  - `scripts/bootstrap_franz_surface_shortcuts.ps1`
- vorbereiteter Shortcut-Ordner lokal:
  - `C:\Users\StudioPC\Documents\FraWo Franz Deploy\Surface Shortcuts`
- sichtbare Abnahme erst gruen, wenn:
  - `Franz Start` als primaerer Einstieg funktioniert
  - die Direktziele `Nextcloud`, `Paperless`, `Odoo` und `Vaultwarden` sichtbar vorhanden sind
  - der Alltagspfad ohne Admin-Umweg funktioniert

### iPhone

- bevorzugt im LAN:
  - `http://portal.hs27.internal/franz/`
- mobil ueber `Tailscale`:
  - `http://100.99.206.128:8447/franz/`
- Jellyfin mobil:
  - `http://100.99.206.128:8449`
- sichtbare Abnahme erst gruen, wenn:
  - `Franz Mobil Start` sichtbar laedt
  - die Kernziele `Nextcloud`, `Paperless`, `Odoo` und `Vaultwarden` von dort sichtbar erreichbar sind
  - kein mobiler Start-Blocker mehr uebrig bleibt

### Homescreen-Standard

1. `Tailscale` verbinden
2. `http://100.99.206.128:8447/franz/` in Safari oeffnen
3. `Zum Home-Bildschirm` anlegen
4. `Vaultwarden` bewusst separat nutzen

## Franz Endnutzer-Standard

- `Franz` startet ueber `Franz Start`, nicht ueber einzelne Admin- oder Service-URLs
- das Surface-Laptop bekommt den nummerierten Shortcut-Ordner
- das iPhone bekommt genau einen Homescreen-Einstieg auf `Franz Mobil Start`
- `Vaultwarden` bleibt nur der Passwortnachschlag, nicht die Arbeitsoberflaeche
- wenn ein Link sauber funktioniert, wird kein zusaetzlicher Client-Setup-Zwang eingefuehrt
- Media-, Radio- und Wohnzimmerpfade bleiben bis nach dem MVP ausserhalb des Hauptstarts

## Wolf Arbeitssurface Standard

- Standardpfad:
  - lokales Arbeiten zuerst
  - `Tailscale` nur einschalten, wenn interner Zugriff wirklich gebraucht wird
- interne Kernziele bei Bedarf:
  - `http://portal.hs27.internal`
  - `http://cloud.hs27.internal`
  - `http://paperless.hs27.internal`
  - `http://odoo.hs27.internal/web/login`
  - `https://vault.hs27.internal`
- keine Dauerregel:
  - kein permanenter Volltunnel
  - keine pauschale Exit-Node-Pflicht
  - kein erzwungenes Umpolen des gesamten Arbeitsgeraets in einen reinen Admin-Client
- falls spaeter echter Vollzugriff fuer Support-/Bridge-Arbeit gebraucht wird:
  - bewusst aktivieren
  - danach wieder in den normalen Arbeitsmodus zurueck

## Shared Jellyfin Regeln

- TV-Clients im Zweifel direkt mit `http://192.168.2.20:8096` verbinden
- fuer TV-Clients nicht `https://media.hs27.internal` verwenden
- `TV Wohnzimmer` bleibt das gewollte Shared-Profil
- solange das Passwort fuer `TV Wohnzimmer` nicht sichtbar vorliegt, den Zustand nicht als fertig markieren

## Offene Benutzerblocker

- Offline-Recovery-Zettel fuer `Vaultwarden` wirklich ausfuellen
- zweite getrennte Offline-Kopie fuer das Master-Passwort anlegen
- `Franz` in `FraWo` sichtbar mit Collections und Kernlogins pruefen
- Mailboxen und App-SMTP ueber den Mail-Kanon fuer `Nextcloud`, `Paperless` und `Odoo` sichtbar fertigziehen
- den Workspace klartextfrei halten und nur noch mit `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md` arbeiten
- spaetere Erweiterungen:
  - `TV Wohnzimmer`
  - `Jellyfin`
  - `Radio`
  - `surface-go-frontend`

## Wenn Etwas Kaputt Wirkt

Zuerst:

1. `..\PLATFORM_STATUS.md`
2. `..\OPS_HOME.md`
3. `..\STRESS_TEST_READINESS.md`

Dann dienstspezifisch:

- `NEXTCLOUD_OPERATIONS.md`
- `PAPERLESS_OPERATIONS.md`
- `ODOO_OPERATIONS.md`
- `JELLYFIN_OPERATIONS.md`
- `AZURACAST_OPERATIONS.md`
- `MAIL_OPERATIONS.md`

## Nicht Tun

- keine neuen produktiven Passwoerter in Markdown pflegen
- keine Admin-UIs oeffentlich freigeben
- Franz nicht in den `Surface Go`-Kioskpfad pressen
- Wolfs `Arbeitssurface` nicht mit `Franz Surface Laptop` oder `surface-go-frontend` verwechseln
- Wolfs `Arbeitssurface` nicht dauerhaft in einen Volltunnel zwingen
- `Odoo` nicht als persoenlichen Mailclient verwenden
- den Arbeits-MVP nicht wieder mit spaeteren Komfortpfaden ueberladen

## Zugeordnete Uebergangsdokumente

- `..\START_HERE_WOLF_FRANZ.md`
- `..\WOLF_FRANZ_HANDOUT.md`
- `..\CHECKLIST_NEXT_STEPS_WOLF_FRANZ.md`
- `..\FRANZ_DEVICE_DEPLOY.md`

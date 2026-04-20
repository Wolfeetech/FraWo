# Public Edge Architecture Plan

## Ziel

Dieses Dokument beschreibt den professionellen Zielpfad fuer die spaetere Oeffnung einzelner Dienste zur Oeffentlichkeit.

Es geht ausdruecklich nicht um sofortige Freigabe, sondern um:

- klare Trennung zwischen internem Betrieb und externer Exposition
- saubere Vorbedingungen
- definierte oeffentliche Dienste
- Rollback und Monitoring

## Release-Default

Stand `2026-03-26` ist der freigegebene Release-Scope fuer `2026-04-01` bewusst klein:

- `frawo-tech.de` leitet spaeter auf `www.frawo-tech.de` um
- `www.frawo-tech.de` ist die erste oeffentliche FRAWO-Website ueber die Odoo-Website
- interne Apps bleiben intern oder Tailscale-only
- die Website selbst traegt im ersten Release bereits die sichtbare Radio-Praesenz
- `radio.frawo-tech.de` bleibt fuer spaeter vorbereitet, ist aber nicht die Pflicht-Frontdoor des ersten Releases

Aktueller Zwischenstand fuer Lane B Stand `2026-04-20`:

- das operative Nahziel ist noch kleiner als der volle erste Website-Release
- zuerst soll nur die HTTPS-/Public-Edge-Baseline fuer `frawo-tech.de` und `www.frawo-tech.de` gruen werden
- Design, Content-Reife und Feintuning der Website duerfen bis spaeter provisorisch bleiben

## Live Facts 2026-04-20

- `frawo-tech.de` loest oeffentlich jetzt auf `92.211.33.54` und `2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc` auf.
- `www.frawo-tech.de` folgt aktuell sauber auf `frawo-tech.de`.
- HTTP auf Apex liefert jetzt den geplanten Redirect auf `https://www.frawo-tech.de/`.
- HTTP auf `www` liefert jetzt die echte FraWo-Odoo-Website.
- HTTPS auf Apex und `www` ist aktuell nicht gruen und scheitert im Live-Check mit `TLSV1_ALERT_INTERNAL_ERROR`.
- Mail-DNS ist noch nicht gruen genug fuer Release:
  - `MX` sichtbar
  - `DMARC` sichtbar
  - `SPF` im Live-Check nicht sichtbar
- letzter Website-Gate-Entscheid: `artifacts/website_release_gate/20260330_161648/website_release_gate.md` = `BLOCKED`
- letzter Website-Audit: `artifacts/website_release_audit/20260330_161613`
- letzter Zielpfad-Preview: `artifacts/public_edge_preview/20260330_134359/report.md` = `passed`
- der Website-Track ist jetzt nativ ohne WSL pruefbar
- sichtbare Browser-Abnahme bestaetigt den Technikbefund:
  - `www`-HTTP zeigt die echte FraWo-Seite
  - Apex-HTTP redirectet korrekt
  - HTTPS endet aktuell mit `ERR_SSL_PROTOCOL_ERROR`
- `VM220` ist jetzt der klare Public-Origin-Kandidat:
  - Host `www.frawo-tech.de` auf `10.1.0.22` liefert `Home | FraWo`
  - Host `frawo-tech.de` auf `10.1.0.22` liefert `308` auf `https://www.frawo-tech.de/`
  - `/radio/public/frawo-funk` liefert den AzuraCast-Player
- `VM220` besitzt eine globale IPv6 `2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc`, die fuer Host `www.frawo-tech.de` auf HTTP bereits `200 OK` liefert.
- `CT100 toolbox` bleibt ein interner Preview- und Infrastrukturpfad; fuer den oeffentlichen First-Class-Cutover ist `VM220` fachlich sauberer.
- `curl -6` gegen Apex und `www` auf Port `80` ist jetzt gruen; die Website ist damit oeffentlich ueber IPv6 sichtbar.
- `curl -4` gegen Apex und `www` auf Port `80` ist weiter rot; ein aktiver Router-Forward fuer IPv4 auf `VM220` ist aktuell nicht belegt.
- Caddy-ACME auf `VM220` versucht Zertifikate jetzt am richtigen Ziel zu ziehen, scheitert aber aktuell mit `92.211.33.54: Connection refused`; der Restblocker ist damit konkret der fehlende IPv4-Pfad fuer `80/443`.

## Decision Stand 2026-04-20

Der bevorzugte HTTPS-/Website-Pfad ist jetzt klar:

- primaerer Edge-Pfad: `Cloudflare` als oeffentlicher Edge vor `VM220`
- primaerer Origin: `VM220 odoo` auf `10.1.0.22`
- primaerer Scope: nur `frawo-tech.de` und `www.frawo-tech.de`
- primaerer Nutzen: HTTPS wird nicht mehr vom DS-Lite-/IPv4-Forward der EasyBox blockiert

Der alternative Pfad bleibt sichtbar, ist aber nicht mehr die bevorzugte Arbeitsannahme:

- Alternativpfad: echter Dual-Stack-/IPv4-Pfad fuer `80/443` direkt auf `VM220`
- dieser Pfad ist nur dann sinnvoll, wenn ein belastbarer oeffentlicher IPv4-Forward wirklich verfuegbar gemacht wird

Nicht mehr als aktive Standardannahme behandeln:

- zufaellig mitlaufende direkte Public-Exposition von `VM220`
- `CT100 toolbox` als primaeres oeffentliches Website-Ziel
- Alpha-/Ad-hoc-Tunnel als produktiver Dauerzustand

## Grundsatz

Oeffentliche Freigaben starten erst, wenn:

- das interne Business-MVP sichtbar stabil ist
- Zielsystem, DNS, TLS, Logging und Rollback definiert sind
- der Website-Scope strikt klein gehalten wird
- Domain, DNS, TLS, Auth, Logging und Rollback definiert sind
- der Passwortmanager produktiv eingefuehrt ist

## Verbindlicher Domain-Pfad

Stand heute ist der bevorzugte oeffentliche Markenpfad:

- primaere Domain: `frawo-tech.de`
- Website: `www.frawo-tech.de`
- Radio-/Player-Pfad spaeter: `radio.frawo-tech.de`

Betriebsregel dazu:

- `www.frawo-tech.de` wird der kanonische Web-Hostname.
- `frawo-tech.de` leitet auf `www.frawo-tech.de` um.
- `www.frawo-tech.de` ist als Odoo-Website-Frontend mit Radio-Praesenz geplant.
- `radio.frawo-tech.de` bleibt technisch getrennt von der Hauptwebsite und ist spaeter optional.
- interne Namen bleiben bis zur bewussten internen DNS-Migration unveraendert:
  - `portal.hs27.internal`
  - `radio.hs27.internal`
  - `media.hs27.internal`
- spaeterer professioneller Zielpfad fuer interne Namen ist `frawo.home.arpa`.

Veraltet und nicht mehr Zielbild:

- `frawo.studio`
- `www.frawo.studio`
- `radio.frawo.studio`

## Nie oeffentlich exponieren

- Proxmox
- PBS-Admin
- AdGuard-Admin
- Home-Assistant-Admin
- interne Toolbox-Adminpfade
- rohe Datenbankports
- interne Nextcloud-, Paperless- oder Odoo-Admins

## Geplante oeffentliche Dienste

### Phase 1

- Odoo-verwaltete GbR-Website auf `www.frawo-tech.de`
- sichtbare Radio-Praesenz oder Player-Pfad auf der Website
- optional Kontaktformular-/Lead-Pfad

### Phase 2

- oeffentliche Radio-/Player-Seite auf `radio.frawo-tech.de`
- spaeter Stream-Endpunkte

### Phase 3

- nur bewusst entschiedene Kunden-/Portalpfade
- keine direkte Vermischung mit internen Admin-Oberflaechen

## Architekturprinzip

### Website

- getrennt von Odoo-Admin und internen Business-UIs
- als Odoo-Website-Frontend, aber ohne oeffentliche Odoo-Admin-Oberflaeche
- mit sichtbarer Radio-Praesenz im ersten Release
- Odoo-Admin und ERP bleiben intern

### Edge

- Reverse Proxy mit TLS
- explizite Hostname-Freigaben
- Logging
- Monitoring
- Rollback

Aktueller Zielpfad dafuer:

- First-Class-Origin fuer die Website: `VM220 odoo`
- Oeffentliche Hostnames: `frawo-tech.de`, `www.frawo-tech.de`
- `frawo-tech.de` -> `308` auf `https://www.frawo-tech.de{uri}`
- `www.frawo-tech.de` -> Odoo-Website
- `/radio` -> sichtbarer Radio-/Player-Pfad
- `CT100 toolbox` nur als interner Gegenprobe- und Preview-Pfad, nicht als primaeres oeffentliches Zielsystem

### DNS

- Apex- und `www`-Strategie fuer `frawo-tech.de`
- spaeter eigene Subdomains wie:
  - `radio.frawo-tech.de`
  - optional `portal.frawo-tech.de` nur bei echtem Produktgrund

Bevorzugter Zielpfad dafuer:

- `frawo-tech.de` -> Redirect auf `www.frawo-tech.de`
- `www.frawo-tech.de` -> Odoo-verwaltete GbR-Website mit Radio-Praesenz
- `radio.frawo-tech.de` -> spaetere dedizierte Radio-/Player-Seite
- kein oeffentliches `portal.frawo-tech.de`, solange kein klarer Produktgrund besteht

Cutover-Realitaet Stand jetzt:

- `www` kann fachlich direkt auf den `VM220`-Origin zeigen, aber der direkte IPv4-/ACME-Pfad ist durch DS-Lite weiter blockiert.
- fuer IPv6 ist das Ziel bereits sichtbar vorbereitet.
- fuer IPv4 fehlt aktuell noch der nachweisbare Router-Forward auf `VM220`.
- der bevorzugte Entschaerfungspfad ist deshalb jetzt `Cloudflare` vor `VM220`, nicht weiteres Hoffen auf einen impliziten Router-Fix.
- Zertifikate koennen auf dem direkten Pfad erst erfolgreich geholt werden, wenn die oeffentlichen A/AAAA-Eintraege nicht mehr auf die `STRATO`-Parking-Ziele zeigen und der IPv4-Pfad real offen ist.

### Zertifikate

- nur automatisiert
- keine manuellen Dauer-Zertifikatsprozesse

## Vorbedingungen

Vor dem ersten Public Rollout muessen gruen sein:

- `RELEASE_READINESS_2026-04-01.md`
- `make website-release-audit`
- `make website-release-gate`
- `make release-mvp-gate`
- Zielsystem fuer `www.frawo-tech.de` ist bestimmt
- das Zielsystem ist als Odoo-Website-Frontend und nicht als Odoo-Adminpfad festgelegt
- DNS-/Redirect-Modell ist dokumentiert
- TLS-Automation ist festgelegt
- die Website-Radio-Einbindung ist definiert
- SPF, DKIM und DMARC sind sauber gesetzt
- dokumentierter DNS-/TLS-/Rollback-Pfad
- produktiver Passwortmanager mit den relevanten Logins

## Rollout-Reihenfolge

1. `frawo-tech.de` final dokumentieren
2. Public-Edge-Modell final festziehen: bevorzugt `Cloudflare -> VM220`
3. Mailboxen und DNS-Mail-Records sauber setzen
4. Edge-Hostnamen und Redirect-Regeln festlegen
5. TLS-Automation ueber den gewaehlten Edge-Pfad einrichten
6. Logging und Uptime-Monitoring festlegen
7. zuerst nur die HTTPS-/Public-Edge-Baseline gruen ziehen, auch wenn die Website inhaltlich noch vorlaeufig ist
8. danach Odoo-Website mit sichtbarer Radio-Praesenz sauber release-faehig ziehen
9. erst spaeter eine separate dedizierte Radio-Seite
10. Business-/Portalpfade nur bewusst und spaet

## Definition of Done

Minimal fertig:

- Domain vorhanden
- Website getrennt geplant
- keine Admin-UIs oeffentlich

Professionell fertig:

- Gateway unter Kontrolle
- PBS/Restore belastbar
- oeffentliche Hostnames klar getrennt
- TLS, Logging, Monitoring und Rollback aktiv
- Secrets nicht mehr dauerhaft in Markdown-Dateien abgelegt

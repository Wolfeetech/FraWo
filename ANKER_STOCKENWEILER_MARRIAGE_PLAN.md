# Anker + Stockenweiler Marriage Plan

## Zweck

Dieses Dokument ist die gemeinsame SSOT fuer den geplanten professionellen Bruecken- und spaeteren Marriage-Pfad zwischen:

- `Anker / Homeserver 2027 / 192.168.2.0/24`
- `Stockenweiler / Legacy Support Site / 192.168.178.0/24`

Es ersetzt keine Fachdokumente, aber es ordnet sie in eine klare Reihenfolge.
Der Zweck ist:

- den aktuellen Ist-Stand ehrlich zu benennen
- den besten Architekturpfad festzulegen
- klar zu trennen zwischen `jetzt moeglich`, `spaeter moeglich` und `jetzt ausdruecklich verboten`
- festzuhalten, welche Entscheidungen der Operator treffen muss

## Kurzantworten

### Haben wir aktuell Zugriff auf alle Tools in Stockenweiler?

Nein.

Aktuell verifiziert:

- `stock-pve` ist per `SSH` von diesem `StudioPC` aus erreichbar
- der Pfad ist `StudioPC -> toolbox -> userspace WireGuard -> 192.168.178.25`
- read-only PVE-Wahrheit ist damit schon moeglich

Aktuell nicht verifiziert oder nicht sauber integriert:

- kompletter `192.168.178.0/24` Zugriff ueber `Tailscale`
- aktueller Haupt-PC in Stockenweiler
- aktuelles Handy in Stockenweiler
- gemappte `AnyDesk`-IDs auf heutige Geraete
- funktionierende Legacy-Dienste fuer `Paperless`, `Nextcloud`, `pve` public

### Ist dieser PC bereits voll in beide Netzwerke integriert?

Nein.

`StudioPC` ist voll im Anker-LAN integriert, aber fuer Stockenweiler nur teilweise:

- Anker: `ja`
- Stockenweiler Recovery-Zugriff: `ja`
- professioneller Management-Bridge-Zugriff: `noch nicht`
- voll sichtbare duale Arbeitsumgebung fuer beide Netze: `noch nicht`

### Koennen wir jetzt schon "anstaendig arbeiten"?

Teilweise.

Wir koennen jetzt:

- auf `stock-pve` arbeiten
- Proxmox-/Storage-Wahrheit read-only sichern
- den Bridge-Pfad professionell fertigbauen
- den Integrationspfad sauber vorbereiten

Wir koennen noch nicht sauber:

- das gesamte Stockenweiler-LAN wie ein zweites Management-Netz nutzen
- alle Legacy-Dienste reproduzierbar erreichen
- beide Standorte als gemeinsame professionelle Plattform betreiben

### Koennen die zwei PVE-Nodes jetzt schon wie ein gemeinsamer Proxmox-Verbund arbeiten?

Nein.

Wichtig:

- `ein gemeinsamer WAN-Proxmox-Cluster` ist **nicht** der empfohlene Zielpfad
- `eine gemeinsame Management-Sicht` ist sinnvoll
- `komplementaere Rollen` sind sinnvoll
- `Cross-site Backup/Storage/Failover-Konzepte` sind sinnvoll
- `Corosync/Cluster ueber WAN` ist fuer euren Stand falsch getaktet und riskant

## Externe Design-Leitplanken

Diese Punkte sind der aktuelle technische Leitfaden fuer den Plan:

- `Proxmox VE cluster` ist fuer stabile, latenzarme Cluster-Netze gedacht; WAN-/Internet-Strecken sind dafuer nicht der Standardweg
- `Tailscale subnet router` ist der saubere Pfad, um ein entferntes Subnetz kontrolliert sichtbar zu machen
- `Proxmox Datacenter Manager (PDM)` ist der passendere Zielpfad fuer eine gemeinsame Uebersicht ueber getrennte Sites als ein erzwungener WAN-Cluster

Siehe:

- Proxmox Cluster Manager: https://pve.proxmox.com/pve-docs/chapter-pvecm.html
- Proxmox Datacenter Manager Remotes: https://pve.proxmox.com/pdm-docs/remotes.html
- Tailscale Subnet Routers: https://tailscale.com/kb/1019/subnets

## Verbindliche Architekturentscheidung

### Was wir bauen

Wir bauen **kein** "alles mit allem sofort verheiraten".

Wir bauen in dieser Reihenfolge:

1. `professionelle Management-Bridge`
2. `gemeinsame Sicht und saubere Fernarbeit`
3. `komplementaere Rollen der beiden Sites`
4. `spaetere selektive Service-Integration`
5. `spaetere professionelle Public-Edge-Freigaben`

### Was wir ausdruecklich nicht bauen

- keinen `Proxmox-Cluster ueber WAN`
- kein `L2-Stretch`
- keine Broadcast-/VLAN-Magie zwischen den Standorten
- keine unkontrollierte Vermischung von `Familie Prinz` und `FraWo GbR`
- kein "eine DB fuer alles" fuer `Paperless` oder `Nextcloud`
- keine direkten oeffentlichen Adminflaechen

## Aktueller Audit-Stand 2026-03-31

### Gruen

- `Anker` Kernplattform ist intern arbeitsfaehig
- `stock-pve` ist von `StudioPC` aus per `SSH` erreichbar
- `Stockenweiler PVE` ist identifiziert:
  - Host `pve`
  - `pve-manager/9.1.4`
- `Tailscale` laeuft auf `StudioPC`
- `WireGuard`-Recovery-Pfad ueber `toolbox` funktioniert
- neue Klarstellung: der lokale `StudioPC`-`WireGuard` ist nicht die spaetere Zielarchitektur; wenn die Standortbruecke professionell gebaut wird, dann als eigenes `Site-to-Site WireGuard` zwischen `UCG` und `Stockenweiler`
- die alte Stockenweiler-DNS-/Host-Wahrheit ist weitgehend geborgen und dokumentiert

### Gelb

- `stockenweiler-pve` ist als `Tailscale subnet-router` vorbereitet, aber noch nicht freigeschaltet
- `StudioPC` hat noch stale lokales `WireGuard`; das ist Altlast/Recovery, nicht das spaetere Standort-VPN
- `AnyDesk` ist lokal da, aber die IDs sind nicht den heutigen Geraeten zugeordnet
- `Surface_Laptop` fuer Wolf ist separat modelliert, aber live noch zu bestaetigen
- `PBS`-Rolle in Stockenweiler ist nur ein spaeterer Kandidat

### Rot

- `192.168.178.0/24` ist noch nicht sauber als sichtbare Tailscale-Route verfuegbar (und per direktem WireGuard-Tunnel auf StudioPC aktuell nur per SSH, nicht per Browser erreichbar)
- `pve.prinz-stockenweiler.de` hat keinen DNS-Eintrag
- `cloud.prinz-stockenweiler.de` hat TLS/SNI-Fehler
- `papierkram.prinz-stockenweiler.de` timed out
- `Home Assistant` public zeigt nur Frontend ohne funktionierendes Backend
- **Sichtbarer Browser-Befund (intern) am 2026-03-31**:
  - `http://192.168.178.1` -> **Timeout** (`ERR_CONNECTION_TIMED_OUT`)
  - `https://192.168.178.25:8006` -> **Timeout**
  - `http://192.168.178.67` -> **Timeout**
- die grossen HDD-Pfade auf `stock-pve` sind derzeit voll:
  - `/mnt/data_family` = `100%`
  - `/mnt/music_hdd` = `100%`
  - `hdd-backup` = `100%`

## Zielbild

## Zielbild A - Management

- `StudioPC` bleibt primarer Admin- und Brueckenknoten
- `toolbox` bleibt Anker-Kontrollknoten
- `stock-pve` wird fuer den aktuellen Adminbetrieb professionell ueber `Tailscale` erreichbar
- die spaetere Standortbruecke wird getrennt davon als `Site-to-Site WireGuard` bewertet, sobald das bestehende `WireGuard`-Setup in `Stockenweiler` read-only inventarisiert ist
- spaeter gemeinsame Uebersicht ueber getrennte Sites
- bevorzugt nicht als WAN-Proxmox-Cluster, sondern als getrennte Management-Domaenen mit gemeinsamer Sicht

## Zielbild B - Daten- und Mandantengrenzen

### FraWo GbR

- `Nextcloud`
- `Paperless`
- `Odoo`
- `Vaultwarden`
- `Website`

laufen produktiv in `Anker`.

### Familie Prinz / Stockenweiler

- lokale Scan-Ordner bleiben lokal
- spaetere Dokumentenautomatisierung nur als eigener Stockenweiler-Pfad
- spaetere `Paperless`-Automatisierung nur mit eigener DB
- Wolf darf beides administrieren
- die Systeme duerfen fachlich nie unklar vermischt werden

Regel:

- `gleicher Operator` ist erlaubt
- `gleiche Datenhaltung ohne Trennung` ist nicht erlaubt

## Zielbild C - Dienste

### Home Assistant

Ziel:

- zwei Haushalte
- ein Operator
- getrennte Site-Identitaet

Kurzfristig:

- Stockenweiler-HA lokal halten
- Management und Support zuerst

Spaeter:

- entweder zwei getrennte HA-Instanzen mit Wolf als Admin
- oder spaetere bewusste Site-uebergreifende Integrationslogik

Aber nicht jetzt:

- kein spontanes Verschmelzen der beiden Haushalte in eine einzige HA-Laufzeit

### Nextcloud / Paperless

Ziel:

- FraWo und Familie Prinz muessen logisch getrennt bleiben

Deshalb:

- FraWo-Produktivinstanz bleibt in Anker
- Stockenweiler-Dokumente bleiben lokal zuerst lokal
- spaeter moeglich:
  - eigener Stockenweiler-Dokumentenpfad
  - eigene Stockenweiler-Paperless-DB
  - optional spaeter eigener Storage-/Sync-Pfad

Nicht empfohlen als erster Schritt:

- eine einzige produktive `Paperless`-DB fuer beide Welten
- eine unklare gemeinsame `Nextcloud`-Arbeitswelt ohne klare Mandantentrennung

### Radio

- Radio wird dort gehostet, wo Hardware und Stabilitaet es zulassen
- keine Standortideologie
- keine Zwangsmigration jetzt

### PBS / Storage

- Stockenweiler soll spaeter Kapazitaet beitragen
- aber nur nach:
  - sauberer Management-Erreichbarkeit
  - dokumentierter Disk-Wahrheit
  - Kapazitaetsbereinigung
  - Rollback

## Phasenplan

### Phase 0 - Operator Control Plane bereinigen

- Ziel: ein sauberer Arbeitsweg statt drei halbaktive Wege
- done_when:
  - `stock-pve` per `SSH` stabil
  - `Tailscale` auf `StudioPC` sauber
  - lokaler stale `WireGuard` bereinigt oder bewusst als Recovery gekennzeichnet
  - Pyrefly-/IDE-Laerm stoert den Betriebsweg nicht mehr
- blocked_by:
  - lokaler Admin-Token fuer Windows-Cleanup
  - Tailscale-Freigabe fuer `stockenweiler-pve`
- next_operator_action:
  - Tailscale-Login fuer `stockenweiler-pve` autorisieren
  - lokales Windows-WireGuard einmal erhoeht sauber bereinigen/reapplien
- next_codex_action:
  - nur einen kanonischen Zugriffspfad sichtbar halten und stale Hilfsprozesse vermeiden

### Phase 1 - Management Bridge fertigstellen

- Ziel: `192.168.178.0/24` kontrolliert von `StudioPC` aus erreichen
- done_when:
  - `stockenweiler-pve` ist im Tailnet autorisiert
  - `192.168.178.0/24` ist als kontrollierte Route sichtbar
  - Proxmox, HA, Scanner-/SMB-Ziele sind reproduzierbar erreichbar
- blocked_by:
  - `stockenweiler-pve` Tailscale `NeedsLogin`
  - ungeklaerte Stockenweiler-Endpunkte
- next_operator_action:
  - Tailscale-Freigabe abschliessen
- next_codex_action:
  - Bridge-Checks erneut fahren und Dokumente aktualisieren

### Phase 2 - Gemeinsame Sicht ohne WAN-Cluster

- Ziel: beide Sites in einer professionellen Betriebsansicht fuehren
- done_when:
  - beide PVE-Hosts sind stabil fernadministrierbar
  - zentrale Uebersicht ueber beide Sites ist entschieden
  - klar ist, ob dafuer `PDM` oder ein anderes Managementmodell genutzt wird
- blocked_by:
  - Phase 1 nicht vollstaendig
- next_operator_action:
  - entscheiden, ob die gewuenschte "eine PVE-Ansicht" als getrennte Management-Sicht ausreicht
- next_codex_action:
  - Managementmodell konkretisieren, aber keinen WAN-Corosync-Cluster bauen

### Phase 3 - Rollen und Daten sauber trennen

- Ziel: `FraWo` und `Familie Prinz` fachlich sauber trennen
- done_when:
  - Dokumentenstrategie entschieden
  - Home-Assistant-Strategie entschieden
  - Identity-/Vault-/Secret-Bereiche sauber getrennt
- blocked_by:
  - fehlende Operator-Entscheidungen zu Daten- und Rollenmodell
- next_operator_action:
  - festlegen, ob Stockenweiler spaeter eine eigene Paperless-DB bekommen soll
  - festlegen, ob Home Assistant getrennt bleibt
- next_codex_action:
  - Trennungsmodell in die Architektur- und Betriebsdokumente ziehen

### Phase 4 - Ressourcen ergaenzen statt vermischen

- Ziel: beide Sites sollen sich technisch ergaenzen
- done_when:
  - PVE-Storage in Stockenweiler ist fuer spaeteren PBS-Einsatz realistisch
  - Radio-Hostingentscheidung folgt Hardware-/Stabilitaetskriterien
  - Backup-/Offsite-/Redundanzpfade sind dokumentiert
- blocked_by:
  - Stockenweiler-HDDs aktuell voll
- next_operator_action:
  - entscheiden, ob PVE-HDDs in Stockenweiler fuer PBS wirklich priorisiert werden sollen
- next_codex_action:
  - Kapazitaets- und PBS-Reuse-Plan aufsetzen, aber noch nicht live cutovern

### Phase 5 - Public Edge professionell vorbereiten

- Ziel: beide Standorte nutzen, ohne oeffentliche Admin-Leaks
- done_when:
  - FraWo-Website sauber online
  - Stockenweiler-Supportpfad sauber getrennt
  - Failover-/Offsite-Gedanke ist dokumentiert
- blocked_by:
  - FraWo Public Edge heute noch `BLOCKED`
  - Stockenweiler noch kein aktiver Rollout
- next_operator_action:
  - Domain-/Markenentscheidung fuer Stockenweiler klar halten
- next_codex_action:
  - Public Edge weiter getrennt behandeln; keine direkte Standortvermischung

## Wichtigste offenen Fehler vor echter Arbeit

1. `stockenweiler-pve` ist zwar vorbereitet, aber noch nicht im Tailnet freigeschaltet.
2. `StudioPC` ist noch nicht professionell in beide Netze integriert, sondern nur teilweise ueber Recovery-Pfade.
3. Lokales `WireGuardTunnel$VPN` ist stale und braucht Admin-Cleanup.
4. Stockenweiler-Endgeraete sind noch nicht vollstaendig identifiziert.
5. Legacy-Hostnamen und Public-DNS in Stockenweiler sind inkonsistent oder kaputt.
6. `stock-pve`-HDDs sind aktuell voll; damit ist PBS dort heute noch nicht produktionsreif.
7. Daten- und Mandantengrenzen fuer `FraWo` vs `Familie Prinz` sind noch nicht als Endentscheid festgezurrt.
8. Die oeffentliche FraWo-Website ist selbst noch nicht release-gruen.

## Entscheidungen, die der Operator jetzt treffen muss

### Entscheidung 1

Willst du fuer "eine gemeinsame PVE-Ansicht" wirklich:

- `eine gemeinsame Management-Sicht`

oder

- `einen echten WAN-Proxmox-Cluster`

Empfehlung: `gemeinsame Management-Sicht`, **nicht** WAN-Cluster.

### Entscheidung 2

Soll Stockenweiler spaeter fuer Dokumente nur:

- lokale Scan-Ordner behalten

oder

- eine eigene Stockenweiler-Paperless-DB bekommen

Empfehlung: zuerst lokal, spaeter separate DB statt Vermischung mit FraWo.

### Entscheidung 3

Soll Home Assistant spaeter:

- getrennt je Haushalt bleiben

oder

- bewusst uebergreifend teilintegriert werden

Empfehlung: erst getrennt bleiben.

### Entscheidung 4

Soll Stockenweiler-PVE spaeter wirklich:

- `PBS/Backup-Kapazitaet` beitragen

oder

- nur Support-/Legacy-Host bleiben

Empfehlung: spaeter `PBS/Backup-Kapazitaet`, aber erst nach Disk-Cleanup.

### Entscheidung 5

Soll `online-prinz.de` spaeter:

- reiner Support-/Familienkontext bleiben

oder

- auch als aktive Website-/Service-Domain dienen

Empfehlung: vorerst Support-/Familienkontext.

## Was wir als Naechstes konkret tun

1. `stockenweiler-pve` sauber in `Tailscale` autorisieren
2. den Bridge-Check neu ziehen
3. den professionellen Arbeitsweg auf `Tailscale-first, WireGuard-fallback` festschreiben
4. die Stockenweiler-Endpunkte sichtbar identifizieren
5. die gemeinsame Management-Sicht definieren
6. erst danach PBS-/Storage-/Service-Fragen weiterziehen

## Nicht von Kleinigkeiten ablenken lassen

Die grossen Linien sind jetzt klar:

- Erst `Control Plane`
- dann `Bridge`
- dann `gemeinsame Sicht`
- dann `Trennung der Datenwelten`
- dann `komplementaere Ressourcennutzung`
- erst ganz spaet `Public`

Der Hauptgrund fuer die gefuehlte Langsamkeit war bisher:

- zu viele parallele Teilpfade
- kein einziges gut sichtbares Marriage-SSOT
- mehrere halbfertige Zugriffsmodelle gleichzeitig
- lokale Tooling-Stoerungen, die wie Infrastrukturprobleme wirkten

Dieses Dokument ist genau dafuer da, das ab jetzt zu beenden.

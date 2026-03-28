# Production Readiness Operations

## Zweck

Dieses Dokument definiert das professionelle Produktions-Gate fuer den Homeserver-Betrieb.

Es gibt absichtlich nur zwei echte Entscheidungen:

- `CERTIFIED`
- `BLOCKED`

Ein freundliches Bauchgefuehl zaehlt hier nicht.

## Grundsatz

Es gibt kein ehrliches `100% risikofrei`.

Es gibt aber ein belastbares, professionelles Freigabemodell:

1. harte technische Kernchecks muessen gruen sein
2. sichtbare manuelle Evidenz fuer Benutzer-, Tresor-, Mail- und Frontendpfade muss vorliegen
3. die Freigabe wird nur durch das Produktions-Gate ausgesprochen

## Zertifizierter Scope Fuer V1

Der erste professionelle interne Freigabestand umfasst bewusst den vollen internen Scope:

- Kernserver
- `PBS`
- App-SMTP fuer `Nextcloud`, `Paperless`, `Odoo`, `AzuraCast`
- `Franz Surface Laptop`
- `iPhone`
- gemeinsames `surface-go-frontend`

Akzeptierte externe Abhaengigkeiten fuer diesen V1-Stand:

- bestehendes `STRATO`-Domain-/Mailmodell
- `Tailscale` als temporaerer Remote-Zugriffspfad

Nicht akzeptabel:

- neue kostenpflichtige SaaS-Abhaengigkeiten fuer Secrets, Orchestrierung oder Kernbetrieb
- eine Produktionsbehauptung ohne `CERTIFIED`

## Technischer Gate-Pfad

1. `make stress-test`
2. manuelle Evidenz in `manifests/production_gate/manual_checks.json` pflegen
3. `make production-gate`

## Zwei Freigabesignale

Es gibt jetzt bewusst zwei getrennte Entscheidungen:

- `make release-mvp-gate`
  - bewertet nur den aktuellen Business-MVP
  - Scope: `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`, STRATO-Mail-Backbone, lokale Proxmox-Business-Backups
  - ignoriert `PBS`, `surface-go-frontend`, `Radio/AzuraCast`-Integration und Shared-Frontend-Zertifizierung bewusst
- `make production-gate`
  - bleibt der harte Vollscope fuer die spaetere interne Gesamtzertifizierung

Wichtig:

- `MVP_READY` ist nicht `CERTIFIED`
- `CERTIFIED` bleibt nur der volle interne Produktionsstand

## Bedeutung der Entscheidung

### `CERTIFIED`

- alle kritischen Codex-Checks sind gruen
- alle kritischen manuellen Evidenzen sind als `passed` dokumentiert
- der Stand ist fuer produktiven internen Betrieb freigegeben

### `BLOCKED`

- mindestens ein kritischer Check oder eine kritische manuelle Evidenz ist nicht gruen
- produktive Freigabe darf nicht behauptet werden
- zuerst die konkreten Blocker schliessen, dann Gate erneut laufen lassen

### `MVP_READY`

- nur im `release-mvp-gate`
- der interne Business-Kern ist sichtbar und technisch freigabefaehig
- das ist ausdruecklich kein Vollsiegel fuer `PBS`, Shared Frontend, Radio oder spaetere Komfortpfade

## Manuelle Evidenz

Die manuelle Evidenz wird in `manifests/production_gate/manual_checks.json` gepflegt.

Kritisch sind derzeit:

- `FraWo`-Zugriff fuer Franz
- sichtbare `Vaultwarden`-Stichprobe
- Wolf-Login-Durchlauf
- Franz-Login-Durchlauf
- sichtbare Shared-Frontend-Abnahme
- verifiziertes `STRATO`-Mailmodell
- sichtbarer App-SMTP-Funktionstest
- fertiger Geraeterollout fuer `Surface Laptop` und `iPhone`
- offline verifiziertes `Vaultwarden`-Recovery-Material

## Artefakte

- letzter Stresslauf: `artifacts/stress_tests/...`
- letzter Produktionsentscheid: `artifacts/production_gate/...`

## Betriebsregel

Wenn das Produktions-Gate `BLOCKED` meldet, dann ist die Plattform nicht professionell freigegeben.

Wenn das Produktions-Gate `CERTIFIED` meldet, dann ist die Plattform professionell freigegeben fuer den definierten Scope.

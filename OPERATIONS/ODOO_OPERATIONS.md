# Odoo Operations

## Zweck

Odoo ist ERP-, CRM-, Angebots-, Rechnungs- und Prozessplattform fuer `FraWo`.

Der professionelle Zielzustand ist nicht nur `HTTP 200`, sondern ein bewusst definierter Business-Stack.

## Zugriff

- `http://odoo.hs27.internal/web/login`
- `http://100.99.206.128:8444/web/login`

## Normalbetrieb

- nur personengebundene Logins verwenden
- Odoo Studio bleibt optional und nicht Teil des kritischen Plattformpfads
- produktive Aenderungen an Prozessen bewusst und nachvollziehbar ausrollen
- Odoo ist die bevorzugte Business-Schale fuer `CRM`, `Sales`, `Invoicing`, `Project`, spaeter optional `Helpdesk` und `Customer Portal`
- Odoo ist nicht der Ort fuer unkontrollierte Infrastruktur- oder Medienlogik; Radio bleibt davon fachlich getrennt

## Taegliche Checks

- Login funktioniert
- Datenbank `FraWo_GbR` erreichbar
- Basis-Workflows laufen ohne UI-Fehler
- Systemmail laeuft ueber `noreply@frawo-tech.de`
- Tailscale-Frontdoor `http://100.99.206.128:8444/web/login` liefert `200`
- direkter Infrastrukturnachweis ueber `http://192.168.2.22:8069/web/login` liefert `200` vom Proxmox-Host aus

## Production-Ready bedeutet hier

- ein bewusstes Modulprofil statt "alles einschalten"
- klares Kundenportal-Zielbild und Benutzerrollen
- dokumentierter Mail- und Benachrichtigungspfad
- sichtbarer Restore-/Backup-Pfad bleibt im SSOT gruen
- keine Vermischung mit `Familie Prinz` oder Stockenweiler-Datenwelten

## Naechste sinnvolle Schritte

- Scope fuer `CRM`, `Angebote/Rechnungen`, `Projekt/Aufgaben` und optional `Customer Portal` festziehen
- reale Nutzerreisen dokumentieren: Lead -> Angebot -> Auftrag -> Rechnung -> Kundenportal
- externe Kunden erst nach bewusstem Rollen-/Portalmodell freigeben

## Nie tun

- keine Testinstanzen mit Produktions-IP
- keine ungeplanten Studio-/Custom-Aenderungen im Kernbetrieb
- keine Stockenweiler-/Familie-Prinz-Daten in denselben Odoo-Betrieb ziehen

## Eskalation

- bei Langsamkeit erst Host-/Storage-Lage pruefen, dann Odoo selbst
- wenn `production-ready` gefordert ist, zuerst Prozess-/Modulprofil klaeren und nicht reflexhaft weitere Apps oder Custom-Code in Odoo ziehen

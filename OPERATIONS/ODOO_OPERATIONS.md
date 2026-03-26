# Odoo Operations

## Zweck

Odoo ist ERP/CRM/Rechnungs- und Prozessplattform.

## Zugriff

- `http://odoo.hs27.internal/web/login`

## Normalbetrieb

- nur personengebundene Logins verwenden
- Odoo Studio bleibt optional und nicht Teil des kritischen Plattformpfads
- produktive ?nderungen an Prozessen bewusst und nachvollziehbar ausrollen

## T?gliche Checks

- Login funktioniert
- Datenbank `FraWo_GbR` erreichbar
- Basis-Workflows laufen ohne UI-Fehler
- Systemmail spaeter ueber `noreply@frawo-tech.de`

## Nie tun

- keine Testinstanzen mit Produktions-IP
- keine ungeplanten Studio-/Custom-?nderungen im Kernbetrieb

## Eskalation

- bei Langsamkeit erst Host-/Storage-Lage pr?fen, dann Odoo selbst

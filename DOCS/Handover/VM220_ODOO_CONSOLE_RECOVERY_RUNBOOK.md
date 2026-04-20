# VM220 Odoo Console Recovery Runbook

Stand: `2026-04-20`

## Zweck

Dieses Runbook ist fuer den Fall, dass `odoo.hs27.internal` auf `HTTP 502` faellt, weil `VM 220 odoo` selbst keine Dienste mehr anbietet.

Der aktuelle Befund fuer diesen Incident:

- `toolbox -> 10.1.0.22` antwortet auf `Ping`
- `10.1.0.22:22` = `connection refused`
- `10.1.0.22:8069` = `connection refused`
- `100.82.26.53:8444` = `502`
- ein kontrollierter Reboot von `VM 220` hat den Zustand nicht behoben

Damit ist die Arbeitsdiagnose:

- nicht primaer DNS
- nicht primaer `toolbox`-Caddy
- primaer Gast-OS oder Odoo-Runtime in `VM 220`

## Einstieg

In Proxmox die Konsole von `VM 220 odoo` oeffnen.

## Sofortchecks

Diese Kommandos in genau dieser Reihenfolge ausfuehren:

```bash
hostname
date
ip a
ip route
systemctl status ssh --no-pager
systemctl status homeserver-compose-odoo.service --no-pager
ss -lntp | grep -E ':22|:80|:443|:8069|:8072' || true
cd /opt/homeserver2027/stacks/odoo && docker compose ps
cd /opt/homeserver2027/stacks/odoo && docker compose logs --tail=120
journalctl -u homeserver-compose-odoo.service -n 120 --no-pager
curl -I http://127.0.0.1:8069/web/login
```

## Erwartungsbild

Gruen waere:

- `ssh` = `active (running)`
- `homeserver-compose-odoo.service` = `active`
- `docker compose ps` zeigt laufende Container fuer Web und DB
- `curl -I http://127.0.0.1:8069/web/login` liefert `200` oder `303`

Rot ist jeder dieser Befunde:

- `ssh` ist `inactive`, `failed` oder gar nicht installiert
- `homeserver-compose-odoo.service` ist `failed`
- `docker compose ps` zeigt `exited`, `dead`, `restarting`
- `127.0.0.1:8069` ist lokal ebenfalls tot

## Entscheidungspfad

### Fall A: Nur SSH ist down, Odoo lokal lebt

Merkmale:

- `curl 127.0.0.1:8069` ist gruen
- `docker compose ps` ist gruen
- nur `ssh` ist rot

Dann:

```bash
systemctl restart ssh
systemctl enable ssh
ss -lntp | grep ':22' || true
```

Danach extern gegenpruefen:

- `10.1.0.22:22`
- `10.1.0.22:8069`
- `http://100.82.26.53:8444/web/login`

### Fall B: Odoo-Service oder Compose-Stack ist down

Merkmale:

- `homeserver-compose-odoo.service` rot oder
- `docker compose ps` rot oder
- `127.0.0.1:8069` rot

Dann:

```bash
cd /opt/homeserver2027/stacks/odoo
docker compose ps
docker compose up -d
sleep 10
docker compose ps
docker compose logs --tail=120
curl -I http://127.0.0.1:8069/web/login
systemctl restart homeserver-compose-odoo.service
systemctl status homeserver-compose-odoo.service --no-pager
```

Wenn danach gruen:

- extern `10.1.0.22:8069`
- dann `odoo.hs27.internal`
- dann `100.82.26.53:8444`

### Fall C: Datenbank oder Odoo-Container crasht sofort

Merkmale:

- `docker compose logs` zeigt Crashloop
- Hinweise auf DB-Auth, fehlende Volumes, kaputte Config oder Port-Bind-Fehler

Dann zuerst diese Fokusstellen pruefen:

```bash
cd /opt/homeserver2027/stacks/odoo
ls -la
cat odoo.conf
docker compose config
docker compose logs db --tail=120
docker compose logs web --tail=120
```

Typische Fehlerbilder:

- Datenbankpasswort / `env_file` kaputt
- `odoo.conf` fehlt oder ist defekt
- Containername oder Service-Name nach Drift veraendert
- lokaler Portbind auf `8069` kollidiert

In diesem Fall keine hektischen Repo-Edits zuerst. Erst den echten Laufzeitfehler aus dem Log sichern.

## Externe Nachpruefung nach Recovery

Von `toolbox` oder `WolfSurface`:

```bash
curl -I http://10.1.0.22:8069/web/login
curl -I http://odoo.hs27.internal/web/login
curl -I http://100.82.26.53:8444/web/login
```

Erwartung:

- direkt `10.1.0.22:8069` = `200` oder `303`
- `odoo.hs27.internal` = kein `502`
- `:8444` = kein `502`

## Zusatzbefund aus diesem Incident

Auf Proxmox liegt aktuell eine kaputte VM-Firewall-Datei:

- `/etc/pve/firewall/220.fw`

Befund:

- `pve-firewall` meldet dort einen Parsefehler
- das wirkt im aktuellen Incident nicht wie die Hauptursache, weil die Ports aktiv `connection refused` liefern

Trotzdem spaeter separat bereinigen:

```bash
cat /etc/pve/firewall/220.fw
```

## Done When

Der Incident gilt erst dann als sauber geschlossen, wenn alle Punkte stimmen:

- `10.1.0.22:8069` antwortet wieder
- `odoo.hs27.internal` antwortet ohne `502`
- `100.82.26.53:8444` antwortet ohne `502`
- der eigentliche Fehlergrund wurde kurz dokumentiert
